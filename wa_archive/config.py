"""Central configuration. Override with environment variables."""
import os
from pathlib import Path

DATA_DIR = Path(os.environ.get("WA_DATA_DIR", Path.cwd() / "data")).resolve()
DB_PATH = DATA_DIR / "archive.db"
IMPORTS_DIR = DATA_DIR / "imports"   # original ZIPs, never modified
MEDIA_DIR = DATA_DIR / "media"       # extracted media, stored by content hash

HOST = os.environ.get("WA_HOST", "127.0.0.1")  # localhost only by default
PORT = int(os.environ.get("WA_PORT", "8765"))

# ZIP safety limits
MAX_FILES = 20000
MAX_FILE_BYTES = 2 * 1024**3        # 2 GB per file
MAX_TOTAL_BYTES = 20 * 1024**3      # 20 GB per ZIP
MAX_RATIO = 200                     # suspicious compression ratio

# Used only when a chat's dates are genuinely ambiguous (all values <= 12
# and no ordering evidence). "MDY" or "DMY".
DEFAULT_DATE_ORDER = os.environ.get("WA_DATE_ORDER", "MDY")


def ensure_dirs():
    for d in (DATA_DIR, IMPORTS_DIR, MEDIA_DIR):
        d.mkdir(parents=True, exist_ok=True)
