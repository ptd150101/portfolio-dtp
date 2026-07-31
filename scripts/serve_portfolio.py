#!/usr/bin/env python3
"""Serve the repository under /portfolio-dtp/ for local browser and Lighthouse tests."""

from __future__ import annotations

import argparse
import http.server
import socketserver
from pathlib import Path
from urllib.parse import unquote, urlparse

PREFIX = "/portfolio-dtp"
ROOT = Path(__file__).resolve().parents[1]


class PortfolioHandler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path: str) -> str:
        parsed = unquote(urlparse(path).path)
        if parsed == PREFIX:
            parsed = "/"
        elif parsed.startswith(PREFIX + "/"):
            parsed = parsed[len(PREFIX) :]
        original = self.path
        try:
            self.path = parsed
            return super().translate_path(parsed)
        finally:
            self.path = original

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        super().end_headers()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=4173)
    args = parser.parse_args()
    handler = lambda *a, **kw: PortfolioHandler(*a, directory=str(ROOT), **kw)
    with socketserver.TCPServer(("127.0.0.1", args.port), handler) as httpd:
        print(f"Serving portfolio at http://127.0.0.1:{args.port}{PREFIX}/", flush=True)
        httpd.serve_forever()
