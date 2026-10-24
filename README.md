# WhatsApp Archive (lean)

A local viewer and backup for exported WhatsApp chats. Runs on your PC, bound to `127.0.0.1`.

## Run
```
pip install -r requirements.txt
python -m wa_archive serve          # open http://127.0.0.1:8765
python -m wa_archive import chat.zip [--name "Chat name"]   # or import from the command line
python -m unittest tests.test_archive
```
On Windows, `run.bat` does the same. Data lives in `./data` (override with `WA_DATA_DIR`).

## What it does
- **Import** iOS and Android exports (ZIP). Original ZIP is kept untouched in `data/imports/`; media is extracted to `data/media/` by content hash.
- **Safe extraction:** rejects `..`, absolute paths, symlinks; size/entry-count limits; whole import is one transaction (a failure leaves nothing behind).
- **Dates:** original timestamp text is stored beside the normalized value. Day/month order is detected from impossible values (e.g. 24/10), then attachment-name dates, then chronology; only if all are inconclusive it uses `WA_DATE_ORDER` (default `MDY`) and says so in the import report.
- **Overlapping exports:** a message is a duplicate if timestamp + sender + text (+ attachment) match. Identical messages in the same second are numbered, so genuine repeats stay separate. Re-importing the same ZIP does nothing. `message_sources` records which import and line each message came from.
- **View:** chat bubbles, images/video/audio inline, date jump, older/newer messages load as you scroll, "my side" selectable per chat.
- **Search:** SQLite FTS5 with prefix matching, `"exact phrase"`, sender and date filters; results jump to the message in context.

## Add-on seams
| Want to add | Where |
|---|---|
| Another format | add a function to `parser.PARSERS` |
| Transcripts, embeddings, AI notes, reconciliation review | append to `importer.after_import_hooks`; store results in **new tables** keyed by `message_id` |
| LAN access | set `WA_HOST`; **add a login first** (none exists yet, so keep the default `127.0.0.1`) |

## Known limits
- No authentication (localhost only by design).
- Messages missing from a newer export are kept, never treated as deleted.
- Same text at the same second from the same sender in two exports with different repeat counts could be miscounted; rare, and the originals are preserved.
