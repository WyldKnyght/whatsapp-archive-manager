"""Local web app (Flask). Bound to localhost by default."""
import re
import tempfile
from pathlib import Path

from flask import Flask, abort, jsonify, request, send_from_directory

from . import config, db, importer

SAFE_INLINE = re.compile(r"^(image/(png|jpeg|gif|webp|bmp)|video/(mp4|quicktime|webm)|audio/.+|application/pdf)$")


def create_app():
    config.ensure_dirs()
    app = Flask(__name__, static_folder="static", static_url_path="/static")
    app.config["MAX_CONTENT_LENGTH"] = config.MAX_TOTAL_BYTES

    def q(sql, *args):
        con = db.connect()
        try:
            return [dict(r) for r in con.execute(sql, args).fetchall()]
        finally:
            con.close()

    @app.after_request
    def headers(resp):
        resp.headers["X-Content-Type-Options"] = "nosniff"
        resp.headers["Referrer-Policy"] = "no-referrer"
        return resp

    @app.get("/")
    def index():
        return send_from_directory(app.static_folder, "index.html")

    @app.get("/api/chats")
    def chats():
        return jsonify(q("""SELECT c.id, c.name, c.me,
               (SELECT COUNT(*) FROM messages m WHERE m.chat_id=c.id) AS messages,
               (SELECT MIN(ts) FROM messages m WHERE m.chat_id=c.id) AS first_ts,
               (SELECT MAX(ts) FROM messages m WHERE m.chat_id=c.id) AS last_ts
               FROM chats c ORDER BY last_ts DESC"""))

    @app.get("/api/chats/<int:cid>/senders")
    def senders(cid):
        return jsonify([r["sender"] for r in q(
            "SELECT DISTINCT sender FROM messages WHERE chat_id=? AND kind!='system' AND sender IS NOT NULL ORDER BY sender", cid)])

    @app.post("/api/chats/<int:cid>/me")
    def set_me(cid):
        me = (request.get_json(silent=True) or {}).get("me")
        con = db.connect()
        with con:
            con.execute("UPDATE chats SET me=? WHERE id=?", (me or None, cid))
        con.close()
        return jsonify(ok=True)

    SELECT = """SELECT m.id, m.ts, m.ts_original, m.sender, m.body, m.kind, m.edited, m.media_name,
                md.id AS media_id, md.mime AS media_mime
                FROM messages m LEFT JOIN media md ON md.id=m.media_id"""

    @app.get("/api/chats/<int:cid>/messages")
    def messages(cid):
        """Cursor paging on (ts,id). Params: before=ts|id, after=ts|id, date=YYYY-MM-DD, around=id, limit."""
        limit = min(int(request.args.get("limit", 100)), 500)
        a = request.args
        if "around" in a:
            row = q("SELECT ts,id FROM messages WHERE id=? AND chat_id=?", int(a["around"]), cid)
            if not row:
                abort(404)
            ts, mid = row[0]["ts"], row[0]["id"]
            before = q(f"{SELECT} WHERE m.chat_id=? AND (m.ts,m.id)<(?,?) ORDER BY m.ts DESC,m.id DESC LIMIT ?", cid, ts, mid, limit // 2)
            rest = q(f"{SELECT} WHERE m.chat_id=? AND (m.ts,m.id)>=(?,?) ORDER BY m.ts,m.id LIMIT ?", cid, ts, mid, limit // 2 + 1)
            return jsonify(before[::-1] + rest)
        if "date" in a:
            return jsonify(q(f"{SELECT} WHERE m.chat_id=? AND m.ts>=? ORDER BY m.ts,m.id LIMIT ?", cid, a["date"], limit))
        if "before" in a:
            ts, mid = a["before"].split("|")
            rows = q(f"{SELECT} WHERE m.chat_id=? AND (m.ts,m.id)<(?,?) ORDER BY m.ts DESC,m.id DESC LIMIT ?", cid, ts, int(mid), limit)
            return jsonify(rows[::-1])
        if "after" in a:
            ts, mid = a["after"].split("|")
            return jsonify(q(f"{SELECT} WHERE m.chat_id=? AND (m.ts,m.id)>(?,?) ORDER BY m.ts,m.id LIMIT ?", cid, ts, int(mid), limit))
        rows = q(f"{SELECT} WHERE m.chat_id=? ORDER BY m.ts DESC,m.id DESC LIMIT ?", cid, limit)  # latest
        return jsonify(rows[::-1])

    @app.get("/api/chats/<int:cid>/search")
    def search(cid):
        text = (request.args.get("q") or "").strip()
        if not text:
            return jsonify([])
        # Quote each term so user input can't break FTS syntax; "quoted phrase" stays a phrase.
        terms = re.findall(r'"([^"]+)"|(\S+)', text)
        fts = " ".join('"%s"' % (p or t).replace('"', '') + ("*" if t else "") for p, t in terms)
        sender = request.args.get("sender")
        sql = """SELECT m.id, m.ts, m.sender, snippet(messages_fts, 0, '[[', ']]', '…', 14) AS snippet
                 FROM messages_fts JOIN messages m ON m.id=messages_fts.rowid
                 WHERE messages_fts MATCH ? AND m.chat_id=?"""
        args = [fts, cid]
        if sender:
            sql += " AND m.sender=?"; args.append(sender)
        for k, op in (("from", ">="), ("to", "<=")):
            if request.args.get(k):
                sql += f" AND m.ts {op} ?"; args.append(request.args[k] + ("T23:59:59" if k == "to" else ""))
        sql += " ORDER BY m.ts DESC LIMIT 200"
        return jsonify(q(sql, *args))

    @app.get("/media/<int:mid>")
    def media(mid):
        rows = q("SELECT stored_name, mime, original_name FROM media WHERE id=?", mid)
        if not rows:
            abort(404)
        r = rows[0]
        inline = bool(SAFE_INLINE.match(r["mime"] or ""))
        return send_from_directory(config.MEDIA_DIR, r["stored_name"],
                                   mimetype=r["mime"] if inline else "application/octet-stream",
                                   as_attachment=not inline, download_name=r["original_name"])

    @app.get("/api/imports")
    def imports():
        return jsonify(q("""SELECT i.id, i.filename, i.imported_at, i.date_order, c.name AS chat, i.report
                            FROM imports i JOIN chats c ON c.id=i.chat_id ORDER BY i.id DESC"""))

    @app.post("/api/import")
    def do_import():
        f = request.files.get("file")
        if not f or not f.filename.lower().endswith(".zip"):
            return jsonify(status="failed", error="Please choose a WhatsApp export .zip file."), 400
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td) / "upload.zip"
            f.save(tmp)
            report = importer.import_zip(tmp, chat_name=request.form.get("chat_name") or None,
                                         original_filename=Path(f.filename).name)
        return jsonify(report), (200 if report["status"] != "failed" else 400)

    return app
