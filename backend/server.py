"""HTTP server exposing the SPD-Notifier JSON API and fallback dashboard."""

from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

from . import feed
from . import storage


def _load_html() -> str:
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "web", "index.html")
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return "<h1>SPD-Notifier</h1><p>web/index.html not found.</p>"


def _done_page() -> str:
    """Small page shown after a session is captured."""
    return (
        "<!doctype html><html><head><meta charset='utf-8'>"
        "<title>SPD-Notifier</title></head><body style='font-family:sans-serif;"
        "background:#0f1220;color:#e7e9f3;text-align:center;padding:60px'>"
        "<h2>&#10003; Authenticated!</h2>"
        "<p>Your SPD-Hub session was captured. You can close this tab and "
        "return to the dashboard &mdash; it will refresh automatically.</p>"
        "<script>setTimeout(function(){window.close();},2500);</script>"
        "</body></html>"
    )


class Handler(BaseHTTPRequestHandler):
    cookies: str | None = None  # set on the server instance

    def _send(self, code: int, body: bytes, content_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path

        if path in ("/", "/index.html"):
            self._send(200, _load_html().encode("utf-8"), "text/html; charset=utf-8")
            return

        if path == "/api/jobs":
            cookies = self.cookies or storage.load_cookies()
            payload = feed.collect(cookies=cookies)
            self._send(200, json.dumps(payload, indent=2).encode("utf-8"),
                       "application/json; charset=utf-8")
            return

        if path == "/api/status":
            has = bool(self.cookies or storage.load_cookies())
            self._send(200, json.dumps({"authenticated": has, "has_cookies": has}).encode("utf-8"),
                       "application/json; charset=utf-8")
            return

        if path == "/api/settings":
            cookies = self.cookies or storage.load_cookies()
            self._send(200, json.dumps(storage.load_settings(cookies)).encode("utf-8"),
                       "application/json; charset=utf-8")
            return

        if path == "/set-cookies":
            qs = parse_qs(parsed.query)
            cookies = qs.get("cookies", [None])[0]
            if cookies:
                storage.save_cookies(cookies)
                self.cookies = cookies
            self._send(200, _done_page().encode("utf-8"), "text/html; charset=utf-8")
            return

        self._send(404, b"Not found", "text/plain; charset=utf-8")

    def do_POST(self):  # noqa: N802
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0) or 0)
        raw = self.rfile.read(length).decode("utf-8", "replace") if length else "{}"
        try:
            data = json.loads(raw)
        except ValueError:
            data = {}

        if parsed.path == "/api/cookies":
            cookies = data.get("cookies")
            if cookies:
                storage.save_cookies(cookies)
                self.cookies = cookies
                self._send(200, json.dumps({"ok": True}).encode("utf-8"),
                           "application/json; charset=utf-8")
            else:
                self._send(400, json.dumps({"ok": False, "error": "missing cookies"}).encode("utf-8"),
                           "application/json; charset=utf-8")
            return

        if parsed.path == "/api/settings":
            cookies = self.cookies or storage.load_cookies()
            settings = storage.save_settings(data, cookies)
            self._send(200, json.dumps(settings).encode("utf-8"),
                       "application/json; charset=utf-8")
            return

        if parsed.path == "/api/logout":
            storage.save_cookies(None)
            self.cookies = None
            self._send(200, json.dumps({"ok": True}).encode("utf-8"),
                       "application/json; charset=utf-8")
            return

        self._send(404, b"Not found", "text/plain; charset=utf-8")

    def log_message(self, *args):  # silence default logging
        return


def run_server(host: str = "localhost", port: int = 8000, cookies: str | None = None) -> None:
    server = ThreadingHTTPServer((host, port), Handler)
    Handler.cookies = cookies or storage.load_cookies()
    print(f"SPD-Notifier running at http://{host}:{port}  (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.shutdown()
