import importlib, io, os, tempfile, unittest, zipfile
from pathlib import Path

SAMPLES = Path(os.environ.get("WA_SAMPLES", "/mnt/user-data/uploads"))


def make_zip(path, chat_text, files=None):
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("_chat.txt", chat_text)
        for n, data in (files or {}).items():
            z.writestr(n, data)
    return path


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["WA_DATA_DIR"] = self.tmp
        from wa_archive import config, db, importer, parser
        for m in (config, db, importer):
            importlib.reload(m)
        self.config, self.db, self.importer, self.parser = config, db, importer, parser
        self.con = db.connect()

    def imp(self, name, text, files=None, chat="T"):
        p = make_zip(Path(self.tmp) / name, text, files)
        return self.importer.import_zip(p, chat_name=chat, con=self.con)

    def count(self, sql="SELECT COUNT(*) FROM messages"):
        return self.con.execute(sql).fetchone()[0]


class ParserTests(Base):
    def test_ios_multiline_and_ampm(self):
        t = "[11/4/24, 12:05:00\u202fAM] A: line1\nline2\n[11/4/24, 12:06:00\u202fPM] B: hi\n"
        p = self.parser.parse_whatsapp(t)
        self.assertEqual(p.messages[0].body, "line1\nline2")
        self.assertEqual(p.messages[0].ts, "2024-11-04T00:05:00")
        self.assertEqual(p.messages[1].ts, "2024-11-04T12:06:00")

    def test_android_dmy_detected_by_value_over_12(self):
        t = "24/10/2026, 15:07 - A: hi\n25/10/2026, 09:01 - B: yo\n01/11/2026, 09:01 - A: there\n"
        p = self.parser.parse_whatsapp(t)
        self.assertEqual(p.date_order, "DMY")
        self.assertEqual(p.messages[0].ts, "2026-10-24T15:07:00")

    def test_android_system_line_has_no_sender(self):
        p = self.parser.parse_whatsapp("1/2/25, 10:00 - Messages are end-to-end encrypted.\n")
        self.assertEqual((p.messages[0].sender, p.messages[0].kind), (None, "system"))

    def test_attachment_and_edited_flag(self):
        t = "[1/2/25, 3:00:00 PM] A: \u200e<attached: IMG-1.jpg>\n[1/2/25, 3:01:00 PM] A: hello \u200e<This message was edited>\n"
        m = self.parser.parse_whatsapp(t).messages
        self.assertEqual((m[0].kind, m[0].media_name), ("media", "IMG-1.jpg"))
        self.assertTrue(m[1].edited)
        self.assertEqual(m[1].body, "hello")


class ImportTests(Base):
    TXT = "[1/2/25, 3:00:00 PM] A: hi\n[1/2/25, 3:00:00 PM] A: hi\n[1/2/25, 3:05:00 PM] B: bye\n"

    def test_reimport_same_zip_is_noop(self):
        self.imp("a.zip", self.TXT)
        r = self.imp("a.zip", self.TXT)
        self.assertEqual(r["status"], "already_imported")
        self.assertEqual(self.count(), 3)

    def test_identical_messages_stay_two(self):
        self.imp("a.zip", self.TXT)
        self.assertEqual(self.count("SELECT COUNT(*) FROM messages WHERE body='hi'"), 2)

    def test_overlapping_exports_dedupe(self):
        self.imp("a.zip", self.TXT)
        r = self.imp("b.zip", self.TXT + "[1/2/25, 4:00:00 PM] A: new\n")
        self.assertEqual((r["new_messages"], r["duplicates_skipped"]), (1, 3))
        self.assertEqual(self.count(), 4)
        self.assertEqual(self.count("SELECT COUNT(*) FROM message_sources"), 7)   # provenance kept

    def test_zip_slip_rejected_and_nothing_written_outside(self):
        r = self.imp("evil.zip", self.TXT, {"../../evil.txt": b"x", "/abs.txt": b"x"})
        self.assertEqual(len(r["media"]["rejected"]), 2)
        self.assertFalse((Path(self.tmp).parent / "evil.txt").exists())

    def test_media_linked_and_missing_reported(self):
        t = "[1/2/25, 3:00:00 PM] A: <attached: a.jpg>\n[1/2/25, 3:01:00 PM] A: <attached: gone.jpg>\n"
        r = self.imp("m.zip", t, {"a.jpg": b"\xff\xd8data"})
        self.assertEqual(r["missing_media"], ["gone.jpg"])
        self.assertEqual(self.count("SELECT COUNT(*) FROM messages WHERE media_id IS NOT NULL"), 1)

    def test_failed_import_rolls_back(self):
        r = self.imp("bad.zip", "no messages here\n")
        self.assertEqual(r["status"], "failed")
        self.assertEqual(self.count("SELECT COUNT(*) FROM imports"), 0)
        self.assertEqual(list(self.config.IMPORTS_DIR.iterdir()), [])

    def test_hook_runs(self):
        seen = []
        self.importer.after_import_hooks.append(lambda con, i, c, ids: seen.append(len(ids)))
        self.imp("a.zip", self.TXT)
        self.assertEqual(seen, [3])


class WebTests(Base):
    TXT = ImportTests.TXT

    def test_search_paging_and_media_headers(self):
        self.imp("a.zip", self.TXT + "[1/3/25, 9:00:00 AM] B: needle \"quoted\" (x)\n", {"a.svg": b"<svg onload=alert(1)>"})
        from wa_archive import app as appmod
        importlib.reload(appmod)
        c = appmod.create_app().test_client()
        cid = c.get("/api/chats").json[0]["id"]
        hits = c.get(f"/api/chats/{cid}/search?q=needle").json
        self.assertEqual(len(hits), 1)
        self.assertEqual(c.get(f"/api/chats/{cid}/search?q=%22%22%20AND%20OR(").status_code, 200)  # hostile input is safe
        ctx = c.get(f"/api/chats/{cid}/messages?around={hits[0]['id']}").json
        self.assertIn(hits[0]["id"], [m["id"] for m in ctx])
        mid = self.con.execute("SELECT id FROM media").fetchone()[0]
        r = c.get(f"/media/{mid}")
        self.assertIn("attachment", r.headers["Content-Disposition"])   # SVG is never rendered inline


@unittest.skipUnless(SAMPLES.exists(), "sample exports not available")
class SampleTests(Base):
    def test_real_samples(self):
        for z, n_msgs, n_media in (("WhatsApp_Chat_-_LG_Canada.zip", 11, 2), ("WhatsApp_Chat_-_Tres_Amigos.zip", 19, 1)):
            r = self.importer.import_zip(SAMPLES / z, con=self.con)
            self.assertEqual((r["new_messages"], r["media"]["extracted"], r["date_order"]), (n_msgs, n_media, "MDY"))
            self.assertEqual(r["missing_media"], [])


if __name__ == "__main__":
    unittest.main()
