"""Safe ZIP import: store original, extract media, parse, dedupe, commit atomically."""
import hashlib
import json
import mimetypes
import re
import shutil
import zipfile
from collections import Counter
from pathlib import Path, PurePosixPath

from . import config, db
from .parser import PARSERS

# Add-on seam: functions called as hook(con, import_id, chat_id, new_message_ids)
# after a successful import (transcription, embeddings, reconciliation review...).
after_import_hooks = []

CHAT_FILE_RE = re.compile(r"(^|/)(_chat\.txt|WhatsApp Chat.*\.txt)$", re.I)


class ImportErrorReport(Exception):
    pass


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def _safe_member(info):
    """Return a clean relative name, or None if the entry is unsafe."""
    name = info.filename.replace("\\", "/")
    if info.is_dir() or name.startswith("/") or re.match(r"^[A-Za-z]:", name):
        return None
    parts = PurePosixPath(name).parts
    if ".." in parts or any(p in ("", ".") for p in parts):
        return None
    if (info.external_attr >> 16) & 0o170000 == 0o120000:   # symlink
        return None
    return "/".join(parts)


def validate_zip(zf):
    infos = zf.infolist()
    if len(infos) > config.MAX_FILES:
        raise ImportErrorReport(f"ZIP has too many entries ({len(infos)}).")
    total = sum(i.file_size for i in infos)
    if total > config.MAX_TOTAL_BYTES:
        raise ImportErrorReport("ZIP expands beyond the configured size limit.")
    return infos


def _guess_mime(name):
    return mimetypes.guess_type(name)[0] or "application/octet-stream"


def _chat_name_from_filename(filename):
    base = re.sub(r"\.zip$", "", filename, flags=re.I)
    base = re.sub(r"^WhatsApp[ _]Chat[ _]*-?[ _]*", "", base, flags=re.I)
    return base.replace("_", " ").strip() or "Imported chat"


def import_zip(zip_path, chat_name=None, original_filename=None, con=None):
    """Import one export. Returns a report dict. Re-importing the same ZIP is a no-op."""
    config.ensure_dirs()
    own = con is None
    con = con or db.connect()
    zip_path = Path(zip_path)
    filename = original_filename or zip_path.name
    digest = sha256_file(zip_path)

    row = con.execute("SELECT id, chat_id FROM imports WHERE sha256=?", (digest,)).fetchone()
    if row:
        return {"status": "already_imported", "import_id": row["id"], "chat_id": row["chat_id"],
                "new_messages": 0, "warnings": ["This exact ZIP was imported before; nothing changed."]}

    report = {"status": "ok", "filename": filename, "warnings": [], "media": {"extracted": 0, "reused": 0, "rejected": []}}
    stored_zip = config.IMPORTS_DIR / f"{digest}.zip"
    new_media_files = []
    try:
        with zipfile.ZipFile(zip_path) as zf:
            infos = validate_zip(zf)
            chat_infos = [i for i in infos if _safe_member(i) and CHAT_FILE_RE.search(_safe_member(i))]
            if not chat_infos:
                raise ImportErrorReport("No chat text file (_chat.txt) found in the ZIP.")
            chat_info = max(chat_infos, key=lambda i: i.file_size)
            text = zf.read(chat_info).decode("utf-8-sig", errors="replace")

            parsed = PARSERS["whatsapp-text"](text, config.DEFAULT_DATE_ORDER)
            if not parsed.messages:
                raise ImportErrorReport("No messages could be parsed from the chat file.")
            report["warnings"] += parsed.warnings

            name = (chat_name or _chat_name_from_filename(filename)).strip()
            con.execute("BEGIN")
            con.execute("INSERT OR IGNORE INTO chats(name) VALUES (?)", (name,))
            chat_id = con.execute("SELECT id FROM chats WHERE name=?", (name,)).fetchone()["id"]

            shutil.copyfile(zip_path, stored_zip)             # untouched original = the backup
            cur = con.execute(
                "INSERT INTO imports(chat_id, filename, sha256, stored_path, size, date_order) VALUES (?,?,?,?,?,?)",
                (chat_id, filename, digest, str(stored_zip), zip_path.stat().st_size, parsed.date_order))
            import_id = cur.lastrowid

            # ---- media: extract everything that is not the chat file
            media_by_name = {}
            for info in infos:
                safe = _safe_member(info)
                if info.is_dir():
                    continue
                if safe is None:
                    report["media"]["rejected"].append({"name": info.filename, "reason": "unsafe path"})
                    continue
                if info is chat_info:
                    continue
                if info.file_size > config.MAX_FILE_BYTES or (
                        info.compress_size and info.file_size / info.compress_size > config.MAX_RATIO and info.file_size > 10_000_000):
                    report["media"]["rejected"].append({"name": safe, "reason": "exceeds size/compression limits"})
                    continue
                try:
                    tmp = config.MEDIA_DIR / f".tmp-{digest[:12]}"
                    h = hashlib.sha256()
                    written = 0
                    with zf.open(info) as src, open(tmp, "wb") as dst:
                        for block in iter(lambda: src.read(1 << 20), b""):
                            written += len(block)
                            if written > config.MAX_FILE_BYTES:
                                raise ImportErrorReport("file exceeded limit while extracting")
                            h.update(block)
                            dst.write(block)
                    fdigest = h.hexdigest()
                    ext = PurePosixPath(safe).suffix.lower()[:10]
                    stored_name = f"{fdigest}{ext}"
                    final = config.MEDIA_DIR / stored_name
                    if final.exists():
                        tmp.unlink()
                        report["media"]["reused"] += 1
                    else:
                        tmp.replace(final)
                        new_media_files.append(final)
                        report["media"]["extracted"] += 1
                    base = PurePosixPath(safe).name
                    con.execute(
                        "INSERT OR IGNORE INTO media(chat_id, import_id, original_name, sha256, stored_name, mime, size) VALUES (?,?,?,?,?,?,?)",
                        (chat_id, import_id, base, fdigest, stored_name, _guess_mime(base), written))
                    mid = con.execute("SELECT id FROM media WHERE chat_id=? AND original_name=? AND sha256=?",
                                      (chat_id, base, fdigest)).fetchone()["id"]
                    media_by_name[base] = mid
                except Exception as e:                      # keep going; report the failure
                    report["media"]["rejected"].append({"name": safe, "reason": str(e)})

            # ---- messages: dedupe by (timestamp, sender, text, nth occurrence)
            seen = Counter()
            new_ids, dup = [], 0
            missing_media = []
            for m in parsed.messages:
                base_key = f"{m.ts}\x1f{m.sender or ''}\x1f{m.body}\x1f{m.media_name or ''}"
                seen[base_key] += 1            # identical messages in one second stay separate
                key = hashlib.sha1(f"{base_key}\x1f{seen[base_key]}".encode("utf-8")).hexdigest()
                media_id = media_by_name.get(m.media_name) if m.media_name else None
                if m.media_name and media_id is None:
                    missing_media.append(m.media_name)
                cur = con.execute(
                    """INSERT OR IGNORE INTO messages
                       (chat_id, ts, ts_original, sender, body, kind, edited, media_id, media_name, dedupe_key)
                       VALUES (?,?,?,?,?,?,?,?,?,?)""",
                    (chat_id, m.ts, m.ts_original, m.sender, m.body, m.kind, int(m.edited),
                     media_id, m.media_name, key))
                if cur.rowcount:
                    mid = cur.lastrowid
                    new_ids.append(mid)
                else:
                    mid = con.execute("SELECT id FROM messages WHERE chat_id=? AND dedupe_key=?",
                                      (chat_id, key)).fetchone()["id"]
                    dup += 1
                    if media_id:   # a later export may carry the file an earlier one lacked
                        con.execute("UPDATE messages SET media_id=? WHERE id=? AND media_id IS NULL", (media_id, mid))
                con.execute("INSERT OR IGNORE INTO message_sources VALUES (?,?,?,?)", (mid, import_id, m.line_no, m.raw))

            if missing_media:
                report["warnings"].append(f"{len(missing_media)} attachment(s) referenced in the chat were not in the ZIP.")
            report.update(import_id=import_id, chat_id=chat_id, chat_name=name, date_order=parsed.date_order,
                          parsed=len(parsed.messages), new_messages=len(new_ids), duplicates_skipped=dup,
                          missing_media=missing_media)
            con.execute("UPDATE imports SET report=? WHERE id=?", (json.dumps(report), import_id))
            for hook in after_import_hooks:
                hook(con, import_id, chat_id, new_ids)
            con.execute("COMMIT")
    except Exception as e:
        if con.in_transaction:
            con.execute("ROLLBACK")
        for f in new_media_files:
            f.unlink(missing_ok=True)
        stored_zip.unlink(missing_ok=True)
        if isinstance(e, (ImportErrorReport, zipfile.BadZipFile)):
            return {"status": "failed", "error": str(e) or "Not a valid ZIP file.", "warnings": []}
        raise
    finally:
        if own:
            con.close()
    return report
