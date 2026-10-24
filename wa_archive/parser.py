"""WhatsApp export parser (iOS and Android text formats).

Adapter interface: a parser is a function  parse(text, date_order) -> ParsedChat.
Register new ones in PARSERS to add formats later.
"""
import re
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime

LRM_CHARS = "\u200e\u200f\u202a\u202b\u202c\u202d\u202e"
_TIME = r"(\d{1,2}):(\d{2})(?::(\d{2}))?[\s\u202f\u00a0]*([AaPp]\.?\s?[Mm]\.?)?"
_DATE = r"(\d{1,4})[/.\-](\d{1,2})[/.\-](\d{1,4}),?"
# iOS:     [11/4/24, 3:07:43 PM] Sender: text
IOS_RE = re.compile(rf"^[{LRM_CHARS}]*\[{_DATE}\s+{_TIME}\]\s(.*)$")
# Android: 24/10/2026, 15:07 - Sender: text
ANDROID_RE = re.compile(rf"^[{LRM_CHARS}]*{_DATE}\s+{_TIME}\s-\s(.*)$")

ATTACHED_RE = re.compile(r"<attached:\s*([^>]+?)\s*>")
ANDROID_ATTACHED_RE = re.compile(r"^\s*(.+?)\s+\(file attached\)\s*$")
FILENAME_DATE_RE = re.compile(r"(?:-|_)(20\d{2})-?(\d{2})-?(\d{2})(?:-|_|\.|\D)")
EDITED_MARKERS = ("<This message was edited>", "<Message edited>")


@dataclass
class RawMessage:
    line_no: int
    date_parts: tuple          # (a, b, c) as written
    time_parts: tuple          # (h, m, s|None, ampm|None)
    ts_original: str
    sender: str | None
    body: str
    raw: str


@dataclass
class ParsedChat:
    messages: list = field(default_factory=list)
    date_order: str = "MDY"
    warnings: list = field(default_factory=list)
    unparsed_leading_lines: int = 0


def _split_sender(rest):
    if ": " in rest:
        sender, body = rest.split(": ", 1)
        return sender.strip(LRM_CHARS + " "), body
    return None, rest


def split_messages(text):
    """Group physical lines into messages (multiline aware)."""
    msgs, cur, leading = [], None, 0
    for i, line in enumerate(text.replace("\r\n", "\n").replace("\r", "\n").split("\n"), 1):
        m = IOS_RE.match(line) or ANDROID_RE.match(line)
        if m:
            if cur:
                msgs.append(cur)
            a, b, c, h, mi, s, ap, rest = m.groups()
            sender, body = _split_sender(rest)
            ts_original = line[: line.index(rest)].strip(LRM_CHARS + " -[]").rstrip(" -]")
            cur = RawMessage(i, (a, b, c), (h, mi, s, ap), ts_original, sender, body, line)
        elif cur is not None:
            cur.body += "\n" + line
            cur.raw += "\n" + line
        elif line.strip():
            leading += 1
    if cur:
        msgs.append(cur)
    return msgs, leading


def detect_date_order(msgs, default="MDY"):
    """Return (order, note). Uses impossible values first, then chronology."""
    pairs = [(int(m.date_parts[0]), int(m.date_parts[1])) for m in msgs if len(m.date_parts[0]) <= 2]
    if not pairs:
        return default, None
    if any(a > 12 for a, b in pairs):
        return "DMY", None
    if any(b > 12 for a, b in pairs):
        return "MDY", None
    # Both readings are valid. Best evidence: attachment names embed the real
    # date (e.g. IMG-20241104-WA0001.jpg, PHOTO-2024-11-04-15-07-43.jpg).
    votes = Counter()
    for m in msgs:
        fm = FILENAME_DATE_RE.search(m.body)
        if not fm:
            continue
        real = (int(fm.group(1)), int(fm.group(2)), int(fm.group(3)))
        for order in ("MDY", "DMY"):
            try:
                d = _build_date(m, order)
            except ValueError:
                continue
            if (d.year, d.month, d.day) == real:
                votes[order] += 1
    if votes["MDY"] != votes["DMY"]:
        return votes.most_common(1)[0][0], None
    # Next: count backwards jumps in file order.
    def jumps(order):
        prev, n = None, 0
        for m in msgs:
            try:
                d = _build_date(m, order)
            except ValueError:
                continue
            if prev and d < prev:
                n += 1
            prev = d
        return n
    mdy, dmy = jumps("MDY"), jumps("DMY")
    if mdy < dmy:
        return "MDY", None
    if dmy < mdy:
        return "DMY", None
    return default, f"Date order is ambiguous; assumed {default}."


def _build_date(m, order):
    a, b, c = m.date_parts
    if len(a) == 4:                      # YYYY-MM-DD
        y, mo, d = int(a), int(b), int(c)
    else:
        y = int(c)
        y += 2000 if y < 100 else 0
        mo, d = (int(a), int(b)) if order == "MDY" else (int(b), int(a))
    h, mi, s, ap = m.time_parts
    h = int(h)
    if ap:
        pm = ap.lower().startswith("p")
        h = (h % 12) + (12 if pm else 0)
    return datetime(y, mo, d, h, int(mi), int(s or 0))


def _classify(m):
    body = m.body.strip(LRM_CHARS + " \n")
    edited = False
    for mark in EDITED_MARKERS:
        if mark in body:
            body = body.replace(mark, "").strip(LRM_CHARS + " \n")
            edited = True
    media_name = None
    mt = ATTACHED_RE.search(body) or ANDROID_ATTACHED_RE.match(body)
    if mt:
        media_name = mt.group(1).strip()
        body = (ATTACHED_RE.sub("", body) if ATTACHED_RE.search(body) else "").strip(LRM_CHARS + " \n")
    if m.sender is None:
        kind = "system"
    elif media_name:
        kind = "media"
    elif m.body.startswith("\u200e") and not media_name:
        kind = "system"          # iOS marks system notices with a leading LRM
    else:
        kind = "text"
    return body, kind, edited, media_name


def parse_whatsapp(text, default_order="MDY"):
    text = text.lstrip("\ufeff")
    msgs, leading = split_messages(text)
    out = ParsedChat(unparsed_leading_lines=leading)
    if leading:
        out.warnings.append(f"{leading} non-empty line(s) before the first message were ignored.")
    order, note = detect_date_order(msgs, default_order)
    out.date_order = order
    if note:
        out.warnings.append(note)
    for m in msgs:
        try:
            ts = _build_date(m, order)
        except ValueError:
            out.warnings.append(f"Line {m.line_no}: unreadable date '{m.ts_original}'; skipped.")
            continue
        body, kind, edited, media_name = _classify(m)
        m.ts, m.body, m.kind, m.edited, m.media_name = ts.isoformat(), body, kind, edited, media_name
        out.messages.append(m)
    return out


PARSERS = {"whatsapp-text": parse_whatsapp}
