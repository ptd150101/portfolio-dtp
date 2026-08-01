#!/usr/bin/env python3
"""Serve a portfolio directory under /portfolio-dtp/ for browser and Lighthouse tests."""

from __future__ import annotations

import argparse
import http.server
import socketserver
from pathlib import Path
from urllib.parse import unquote, urlparse

PREFIX = "/portfolio-dtp"
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


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
        self.send_header("Cache-Control", "public, max-age=3600")
        self.send_header("X-Content-Type-Options", "nosniff")
        super().end_headers()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=4173)
    parser.add_argument("--root", default=".", help="Directory to serve, relative to the repository root")
    args = parser.parse_args()

    root = (REPOSITORY_ROOT / args.root).resolve()
    if not root.is_dir():
        raise SystemExit(f"Serve root does not exist: {root}")

    handler = lambda *a, **kw: PortfolioHandler(*a, directory=str(root), **kw)
    with socketserver.TCPServer(("127.0.0.1", args.port), handler) as httpd:
        print(f"Serving portfolio at http://127.0.0.1:{args.port}{PREFIX}/ from {root}", flush=True)
        httpd.serve_forever()
