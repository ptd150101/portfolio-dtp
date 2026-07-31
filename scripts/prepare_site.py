#!/usr/bin/env python3
"""Build the deployable static directory and apply environment-specific URL/analytics settings."""

from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_URL = "https://ptd150101.github.io/portfolio-dtp"
EXCLUDED_TOP_LEVEL = {
    ".git", ".github", ".portfolio-upgrade", "node_modules", "tests", "scripts", "docs", "reports",
    "playwright-report", "test-results", ".lighthouseci", "_site",
}
EXCLUDED_FILES = {
    "package.json", "package-lock.json", ".htmlvalidate.json", "playwright.config.js",
    "lighthouserc.cjs", "site.webmanifest",
}


def copy_site(output: Path) -> None:
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    for source in ROOT.iterdir():
        if source.name in EXCLUDED_TOP_LEVEL or source.name in EXCLUDED_FILES:
            continue
        target = output / source.name
        if source.is_dir():
            shutil.copytree(source, target)
        else:
            shutil.copy2(source, target)


def rewrite_text_files(output: Path, site_url: str, token: str) -> None:
    site_url = site_url.rstrip("/")
    parsed = urlparse(site_url)
    custom_root = parsed.hostname != "ptd150101.github.io" or parsed.path.rstrip("/") != "/portfolio-dtp"
    text_extensions = {".html", ".xml", ".txt", ".js", ".css", ".json"}
    for path in output.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in text_extensions:
            continue
        text = path.read_text(encoding="utf-8")
        text = text.replace(DEFAULT_URL, site_url)
        text = text.replace("__CF_ANALYTICS_TOKEN__", token.strip())
        if custom_root:
            text = text.replace('"/portfolio-dtp/', '"/')
            text = text.replace("'/portfolio-dtp/", "'/")
            text = text.replace("(/portfolio-dtp/", "(/")
        path.write_text(text, encoding="utf-8")

    robots = output / "robots.txt"
    robots.write_text(f"User-agent: *\nAllow: /\nSitemap: {site_url}/sitemap.xml\n", encoding="utf-8")
    (output / ".nojekyll").write_text("", encoding="utf-8")

    if custom_root and parsed.hostname:
        (output / "CNAME").write_text(parsed.hostname + "\n", encoding="utf-8")
    else:
        cname = output / "CNAME"
        if cname.exists():
            cname.unlink()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="_site")
    args = parser.parse_args()
    output = ROOT / args.output
    site_url = os.environ.get("SITE_URL", DEFAULT_URL)
    token = os.environ.get("CF_ANALYTICS_TOKEN", "")
    copy_site(output)
    rewrite_text_files(output, site_url, token)
    print(f"Prepared {output} for {site_url}")
    if token:
        print("Cloudflare Web Analytics token injected.")
    else:
        print("Cloudflare Web Analytics remains disabled because CF_ANALYTICS_TOKEN is empty.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
