import argparse
import json
from pathlib import Path

from . import config, importer


def main():
    ap = argparse.ArgumentParser(prog="wa_archive")
    sub = ap.add_subparsers(dest="cmd", required=True)
    imp = sub.add_parser("import", help="import one or more export ZIPs")
    imp.add_argument("zips", nargs="+", type=Path)
    imp.add_argument("--name", help="chat name (default: from file name)")
    sub.add_parser("serve", help="start the local web app")
    args = ap.parse_args()
    if args.cmd == "import":
        for z in args.zips:
            r = importer.import_zip(z, chat_name=args.name)
            r.pop("missing_media", None)
            print(z.name, json.dumps(r, indent=2))
    else:
        from .app import create_app
        print(f"Open http://{config.HOST}:{config.PORT}")
        create_app().run(host=config.HOST, port=config.PORT)


if __name__ == "__main__":
    main()
