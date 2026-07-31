#!/usr/bin/env python3
"""Generate sitemap.xml and verify that every public route is represented."""

from __future__ import annotations

import argparse
import re
import subprocess
import xml.etree.ElementTree as ET
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
NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}


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


def expected_locations(site_url: str) -> set[str]:
    base = site_url.rstrip("/")
    return {
        f"{base}/" if route == "/" else f"{base}{route}"
        for file_name, route in ROUTES.items()
        if (ROOT / file_name).exists()
    }


def render(site_url: str) -> str:
    base = site_url.rstrip("/")
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for file_name, route in ROUTES.items():
        file_path = ROOT / file_name
        if not file_path.exists():
            continue
        loc = f"{base}/" if route == "/" else f"{base}{route}"
        lines.extend([
            "  <url>",
            f"    <loc>{escape(loc)}</loc>",
            f"    <lastmod>{last_modified(file_path)}</lastmod>",
            "  </url>",
        ])
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def validate(output: Path, site_url: str) -> int:
    if not output.exists():
        print("sitemap.xml is missing.")
        return 1
    try:
        root = ET.parse(output).getroot()
    except ET.ParseError as exc:
        print(f"sitemap.xml is invalid XML: {exc}")
        return 1
    locations = {node.text.strip() for node in root.findall("sm:url/sm:loc", NS) if node.text}
    expected = expected_locations(site_url)
    if locations != expected:
        print(f"Sitemap URL mismatch. Expected {sorted(expected)}, found {sorted(locations)}")
        return 1
    for node in root.findall("sm:url/sm:lastmod", NS):
        if not node.text or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", node.text.strip()):
            print(f"Invalid lastmod value: {node.text!r}")
            return 1
    if len(root.findall("sm:url/sm:lastmod", NS)) != len(expected):
        print("Each sitemap URL must include lastmod.")
        return 1
    print(f"sitemap.xml is valid and contains {len(expected)} public routes.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site-url", default=DEFAULT_SITE_URL)
    parser.add_argument("--output", default=str(ROOT / "sitemap.xml"))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    output = Path(args.output)
    if args.check:
        return validate(output, args.site_url)
    output.write_text(render(args.site_url), encoding="utf-8")
    print(f"Wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
