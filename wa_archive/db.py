import sqlite3
from . import config

SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS chats (
    id          INTEGER PRIMARY KEY,
    name        TEXT NOT NULL UNIQUE,
    me          TEXT,                      -- sender shown on the right side
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS imports (
    id          INTEGER PRIMARY KEY,
    chat_id     INTEGER NOT NULL REFERENCES chats(id),
    filename    TEXT NOT NULL,
    sha256      TEXT NOT NULL UNIQUE,      -- identical ZIP = already imported
    stored_path TEXT NOT NULL,             -- untouched original ZIP
    size        INTEGER NOT NULL,
    imported_at TEXT NOT NULL DEFAULT (datetime('now')),
    date_order  TEXT,                      -- MDY / DMY as detected
    report      TEXT                       -- JSON import report
);

CREATE TABLE IF NOT EXISTS media (
    id            INTEGER PRIMARY KEY,
    chat_id       INTEGER NOT NULL REFERENCES chats(id),
    import_id     INTEGER NOT NULL REFERENCES imports(id),
    original_name TEXT NOT NULL,
    sha256        TEXT NOT NULL,
    stored_name   TEXT NOT NULL,           -- file name under MEDIA_DIR
    mime          TEXT,
    size          INTEGER NOT NULL,
    UNIQUE (chat_id, original_name, sha256)
);

CREATE TABLE IF NOT EXISTS messages (
    id            INTEGER PRIMARY KEY,
    chat_id       INTEGER NOT NULL REFERENCES chats(id),
    ts            TEXT NOT NULL,           -- normalized local time, ISO 8601, no timezone
    ts_original   TEXT NOT NULL,           -- exactly as exported
    sender        TEXT,                    -- NULL for system lines
    body          TEXT NOT NULL,
    kind          TEXT NOT NULL,           -- text / media / system
    edited        INTEGER NOT NULL DEFAULT 0,
    media_id      INTEGER REFERENCES media(id),
    media_name    TEXT,                    -- referenced name, even if file missing
    dedupe_key    TEXT NOT NULL,
    UNIQUE (chat_id, dedupe_key)
);
CREATE INDEX IF NOT EXISTS idx_messages_order ON messages (chat_id, ts, id);

-- Provenance: which import(s) contributed each message, and from which line.
CREATE TABLE IF NOT EXISTS message_sources (
    message_id  INTEGER NOT NULL REFERENCES messages(id),
    import_id   INTEGER NOT NULL REFERENCES imports(id),
    line_no     INTEGER NOT NULL,
    raw         TEXT NOT NULL,
    PRIMARY KEY (message_id, import_id)
);

CREATE VIRTUAL TABLE IF NOT EXISTS messages_fts USING fts5(
    body, sender, content='messages', content_rowid='id', tokenize='unicode61 remove_diacritics 2'
);
CREATE TRIGGER IF NOT EXISTS messages_ai AFTER INSERT ON messages BEGIN
    INSERT INTO messages_fts(rowid, body, sender) VALUES (new.id, new.body, new.sender);
END;
CREATE TRIGGER IF NOT EXISTS messages_ad AFTER DELETE ON messages BEGIN
    INSERT INTO messages_fts(messages_fts, rowid, body, sender) VALUES ('delete', old.id, old.body, old.sender);
END;

-- Add-on tables (transcripts, embeddings, AI output) go in their own tables,
-- keyed by message_id, and never modify the rows above.
"""


def connect(path=None):
    config.ensure_dirs()
    con = sqlite3.connect(path or config.DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    con.execute("PRAGMA journal_mode = WAL")
    con.executescript(SCHEMA)
    return con
