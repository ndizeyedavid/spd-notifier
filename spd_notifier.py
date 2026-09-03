#!/usr/bin/env python3
"""
SPD-Notifier — command-line entry point.

A tiny, dependency-free Python backend that scans the ALU SPD-Hub job RSS
feed and serves it as JSON for the browser extension (and an optional local
dashboard). See `backend/` for the implementation.

Usage
-----
  python spd_notifier.py --json                 # print feed JSON to stdout
  python spd_notifier.py --json --output j.json # save feed JSON to file
  python spd_notifier.py --serve                # run the local web server
  python spd_notifier.py --serve --port 8000
  python spd_notifier.py --set-cookies "..."    # save a session cookie
  python spd_notifier.py --clear-cookies        # forget the session cookie
"""

from __future__ import annotations

import argparse
import json
import sys

from backend import feed, storage

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ALU SPD-Hub RSS notifier/parser.")
    parser.add_argument("--json", action="store_true", help="Print the JSON result to stdout.")
    parser.add_argument("--output", help="Write JSON to this file instead of stdout.")
    parser.add_argument("--serve", action="store_true", help="Run the local web server.")
    parser.add_argument("--port", type=int, default=8000, help="Port for --serve (default 8000).")
    parser.add_argument("--cookies", help="Session cookie string for authenticated fetching.")
    parser.add_argument("--set-cookies", help="Save a session cookie string and exit.")
    parser.add_argument("--clear-cookies", action="store_true", help="Forget the saved session cookie and exit.")
    parser.add_argument("--url", help="Override the feed URL (for testing).")
    args = parser.parse_args(argv)

    if args.clear_cookies:
        storage.save_cookies(None)
        print("Saved session cookie cleared.")
        return 0
    if args.set_cookies:
        storage.save_cookies(args.set_cookies)
        print("Session cookie saved.")
        return 0

    if not args.serve and not args.json and not args.output:
        # Default: behave like --json for convenience.
        args.json = True

    result = feed.collect(cookies=args.cookies, url=args.url)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            json.dump(result, fh, indent=2, ensure_ascii=False)
        print(f"Wrote {result['count']} job(s) to {args.output}", file=sys.stderr)
    elif args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))

    if args.serve:
        from backend import server

        server.run_server(port=args.port, cookies=args.cookies)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
