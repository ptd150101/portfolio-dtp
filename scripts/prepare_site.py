#!/usr/bin/env python3
"""Build the deployable static directory with SEO, analytics and domain-aware URLs."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
from datetime import date
from pathlib import Path
from urllib.parse import urlparse
from xml.sax.saxutils import escape

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
PAGE_META = {
    "index.html": {"route": "/", "type": "website", "image": "og-home.png", "alt": "Đạt Tiến engineering portfolio featuring practical AI and systems projects."},
    "projects/context-video-translator/index.html": {"route": "/projects/context-video-translator/", "type": "article", "image": "og-context-translator.png", "alt": "Context Video Translator showing synchronized bilingual subtitles."},
    "projects/remotekey/index.html": {"route": "/projects/remotekey/", "type": "article", "image": "og-remotekey.png", "alt": "RemoteKey Android-to-Windows shortcut bridge product overview."},
    "resume/index.html": {"route": "/resume/", "type": "profile", "image": "og-resume.png", "alt": "Phan Tiến Đạt software engineering résumé."},
    "privacy/index.html": {"route": "/privacy/", "type": "website", "image": "og-home.png", "alt": "Đạt Tiến engineering portfolio preview."},
    "404.html": {"route": "/404.html", "type": "website", "image": "og-home.png", "alt": "Đạt Tiến engineering portfolio preview."},
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


def remove_meta(text: str, key: str, *, prop: bool = True) -> str:
    attribute = "property" if prop else "name"
    pattern = rf'\s*<meta\s+{attribute}=["\']{re.escape(key)}["\'][^>]*>\s*'
    return re.sub(pattern, "\n", text, flags=re.I)


def ensure_og_type(text: str, value: str) -> str:
    pattern = r'<meta\s+property=["\']og:type["\'][^>]*>'
    replacement = f'<meta property="og:type" content="{value}">'
    if re.search(pattern, text, flags=re.I):
        return re.sub(pattern, replacement, text, count=1, flags=re.I)
    return text.replace("</head>", f"  {replacement}\n</head>")


def page_url(site_url: str, route: str) -> str:
    base = site_url.rstrip("/")
    return f"{base}/" if route == "/" else f"{base}{route}"


def relative_asset(rel: str, target: str) -> str:
    depth = len(Path(rel).parent.parts)
    return "../" * depth + target


def add_privacy_link(text: str, href: str) -> str:
    if re.search(r'>Privacy</a>', text, flags=re.I):
        return text
    pattern = r'(<div\s+class=["\']footer-links["\']>)(.*?)(</div>)'
    return re.sub(pattern, lambda m: m.group(1) + m.group(2) + f'<a href="{href}">Privacy</a>' + m.group(3), text, count=1, flags=re.I | re.S)


def ensure_accessible_structure(text: str) -> str:
    text = re.sub(r'<nav\s+class="nav-links"\s+data-nav-links(?![^>]*\bid=)', '<nav class="nav-links" id="primary-navigation" data-nav-links', text, count=1, flags=re.I)
    text = re.sub(
        r'(<button\s+class="icon-button mobile-toggle"[^>]*data-menu-toggle)([^>]*>)',
        lambda m: m.group(1) + ('' if 'aria-controls=' in m.group(2) else ' aria-controls="primary-navigation"') + ('' if 'aria-label=' in m.group(2) else ' aria-label="Open navigation"') + m.group(2),
        text, count=1, flags=re.I,
    )
    if re.search(r'<main[^>]*\bid=["\']main["\']', text, flags=re.I):
        text = re.sub(r'(<main[^>]*\bid=["\']main["\'])(?![^>]*\btabindex=)', r'\1 tabindex="-1"', text, count=1, flags=re.I)
    else:
        text = re.sub(r'<main(\s|>)', r'<main id="main" tabindex="-1"\1', text, count=1, flags=re.I)
    return text


def schema_for(rel: str, canonical: str, site_url: str) -> dict | None:
    if rel == "index.html":
        return {"@context": "https://schema.org", "@type": "WebSite", "name": "Đạt Tiến — Engineering Portfolio", "url": canonical, "inLanguage": "en"}
    if rel.startswith("projects/"):
        name = "Context Video Translator" if "context-video" in rel else "RemoteKey"
        return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": site_url.rstrip("/") + "/"},
            {"@type": "ListItem", "position": 2, "name": "Projects", "item": site_url.rstrip("/") + "/#work"},
            {"@type": "ListItem", "position": 3, "name": name, "item": canonical},
        ]}
    if rel == "resume/index.html":
        return {"@context": "https://schema.org", "@type": "ProfilePage", "url": canonical, "mainEntity": {
            "@type": "Person", "name": "Phan Tiến Đạt", "jobTitle": "Software Engineer", "url": site_url.rstrip("/") + "/",
            "sameAs": ["https://github.com/ptd150101", "https://www.linkedin.com/in/ptd150101/"],
        }}
    return None


def transform_html(path: Path, output: Path, site_url: str) -> None:
    rel = path.relative_to(output).as_posix()
    cfg = PAGE_META.get(rel)
    text = path.read_text(encoding="utf-8")
    text = text.replace(DEFAULT_URL, site_url.rstrip("/"))
    text = re.sub(r'\s*<link\s+rel=["\']manifest["\'][^>]*>\s*', "\n", text, flags=re.I)
    text = ensure_accessible_structure(text)
    analytics_src = relative_asset(rel, "assets/analytics.js")
    if "analytics.js" not in text:
        text = text.replace("</head>", f'  <script src="{analytics_src}" defer></script>\n</head>')
    text = add_privacy_link(text, relative_asset(rel, "privacy/"))

    if cfg:
        canonical = page_url(site_url, cfg["route"])
        image = site_url.rstrip("/") + "/assets/" + cfg["image"]
        for key in ("og:url", "og:image", "og:image:width", "og:image:height", "og:image:alt"):
            text = remove_meta(text, key, prop=True)
        for key in ("twitter:card", "twitter:image", "twitter:image:alt"):
            text = remove_meta(text, key, prop=False)
        text = ensure_og_type(text, cfg["type"])
        canonical_pattern = r'<link\s+rel=["\']canonical["\'][^>]*>'
        canonical_tag = f'<link rel="canonical" href="{canonical}">'
        if re.search(canonical_pattern, text, flags=re.I):
            text = re.sub(canonical_pattern, canonical_tag, text, count=1, flags=re.I)
        else:
            text = text.replace("</head>", f"  {canonical_tag}\n</head>")
        block = (
            f'  <meta property="og:url" content="{canonical}">\n'
            f'  <meta property="og:image" content="{image}">\n'
            '  <meta property="og:image:width" content="1200">\n'
            '  <meta property="og:image:height" content="630">\n'
            f'  <meta property="og:image:alt" content="{cfg["alt"]}">\n'
            '  <meta name="twitter:card" content="summary_large_image">\n'
            f'  <meta name="twitter:image" content="{image}">\n'
            f'  <meta name="twitter:image:alt" content="{cfg["alt"]}">\n'
        )
        text = text.replace(canonical_tag, block + f"  {canonical_tag}")
        schema = schema_for(rel, canonical, site_url)
        if schema and 'id="portfolio-generated-schema"' not in text:
            payload = json.dumps(schema, ensure_ascii=False, separators=(",", ":"))
            text = text.replace("</head>", f'  <script id="portfolio-generated-schema" type="application/ld+json">{payload}</script>\n</head>')
    path.write_text(text, encoding="utf-8")


def rewrite_root_paths(output: Path, site_url: str) -> None:
    parsed = urlparse(site_url)
    custom_root = parsed.hostname != "ptd150101.github.io" or parsed.path.rstrip("/") != "/portfolio-dtp"
    if not custom_root:
        return
    for path in output.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".html", ".xml", ".txt", ".js", ".css", ".json"}:
            continue
        text = path.read_text(encoding="utf-8")
        text = text.replace('"/portfolio-dtp/', '"/').replace("'/portfolio-dtp/", "'/").replace("(/portfolio-dtp/", "(/")
        path.write_text(text, encoding="utf-8")


def generate_discovery_files(output: Path, site_url: str) -> None:
    base = site_url.rstrip("/")
    routes = [cfg["route"] for key, cfg in PAGE_META.items() if key != "404.html"]
    today = date.today().isoformat()
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for route in routes:
        loc = f"{base}/" if route == "/" else f"{base}{route}"
        lines.extend(["  <url>", f"    <loc>{escape(loc)}</loc>", f"    <lastmod>{today}</lastmod>", "  </url>"])
    lines.append("</urlset>")
    (output / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (output / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n", encoding="utf-8")
    (output / ".nojekyll").write_text("", encoding="utf-8")


def build(output: Path, site_url: str, token: str) -> None:
    copy_site(output)
    for html in output.rglob("*.html"):
        transform_html(html, output, site_url)
    analytics = output / "assets" / "analytics.js"
    if analytics.exists():
        analytics.write_text(analytics.read_text(encoding="utf-8").replace("__CF_ANALYTICS_TOKEN__", token.strip()), encoding="utf-8")
    rewrite_root_paths(output, site_url)
    generate_discovery_files(output, site_url)
    parsed = urlparse(site_url)
    custom_root = parsed.hostname != "ptd150101.github.io" or parsed.path.rstrip("/") != "/portfolio-dtp"
    if custom_root and parsed.hostname:
        (output / "CNAME").write_text(parsed.hostname + "\n", encoding="utf-8")
    elif (output / "CNAME").exists():
        (output / "CNAME").unlink()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="_site")
    args = parser.parse_args()
    output = ROOT / args.output
    site_url = os.environ.get("SITE_URL", DEFAULT_URL).rstrip("/")
    token = os.environ.get("CF_ANALYTICS_TOKEN", "")
    build(output, site_url, token)
    print(f"Prepared {output} for {site_url}")
    print("Cloudflare Web Analytics token injected." if token else "Cloudflare Web Analytics remains disabled because CF_ANALYTICS_TOKEN is empty.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
