#!/usr/bin/env python3
"""Generate sitemap.xml from public index pages and their most recent Git dates."""

from __future__ import annotations

import argparse
import subprocess
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SITE_URL = "https://ptd150101.github.io/portfolio-dtp"
ROUTES = {
    "index.html": "/",
    "projects/context-video-translator/index.html": "/projects/context-video-translator/",
    "projects/remotekey/index.html": "/projects/remotekey/",
    "resume/index.html": "/resume/",
    "privacy/index.html": "/privacy/",
}


def last_modified(path: Path) -> str:
    try:
        value = subprocess.check_output(
            ["git", "log", "-1", "--format=%cs", "--", str(path.relative_to(ROOT))],
            cwd=ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        if value:
            return value
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    return date.today().isoformat()


def render(site_url: str, root: Path = ROOT) -> str:
    base = site_url.rstrip("/")
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for file_name, route in ROUTES.items():
        file_path = root / file_name
        if not file_path.exists():
            continue
        loc = f"{base}{route}" if route != "/" else f"{base}/"
        lines.extend([
            "  <url>",
            f"    <loc>{escape(loc)}</loc>",
            f"    <lastmod>{last_modified(ROOT / file_name)}</lastmod>",
            "  </url>",
        ])
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site-url", default=DEFAULT_SITE_URL)
    parser.add_argument("--output", default=str(ROOT / "sitemap.xml"))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    output = Path(args.output)
    expected = render(args.site_url)
    if args.check:
        current = output.read_text(encoding="utf-8") if output.exists() else ""
        if current != expected:
            print("sitemap.xml is stale. Run: python3 scripts/generate_sitemap.py")
            return 1
        print("sitemap.xml is up to date.")
        return 0
    output.write_text(expected, encoding="utf-8")
    print(f"Wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
