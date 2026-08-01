#!/usr/bin/env python3
"""Build the production artifact and apply deterministic performance/accessibility fixes."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from prepare_site import DEFAULT_URL, ROOT, build


def optimize_artifact(output: Path) -> None:
    """Apply fixes that must be identical in browser tests and production deploys."""
    styles = output / "assets" / "styles.css"
    css = styles.read_text(encoding="utf-8")
    css = css.replace(
        ".resume-entry span { color: #6c788e; font-size: 12px; }",
        ".resume-entry span { color: #5f6b80; font-size: 12px; }",
    )
    css += """

/* Résumé is intentionally a fixed light document; do not inherit the dark
   translucent button surface from the main portfolio theme. */
.resume-page .resume-actions .button:not(.primary) {
  color: #172033;
  background: #ffffff;
  border-color: #8a96aa;
}
.resume-page .resume-actions .button:not(.primary):hover {
  background: #f8fafc;
  border-color: #5f6b80;
}
"""
    styles.write_text(css, encoding="utf-8")

    context_page = output / "projects" / "context-video-translator" / "index.html"
    html = context_page.read_text(encoding="utf-8")
    old_hero = (
        '<img src="../../assets/context-real-translation-vietnamese.png" '
        'width="1357" height="771" fetchpriority="high" '
        'alt="Real Context Video Translator screenshot showing Japanese source captions and Vietnamese contextual translation on a video player.">'
    )
    new_hero = (
        '<img src="../../assets/context-translator-card.svg" '
        'width="1200" height="700" loading="eager" fetchpriority="high" decoding="async" '
        'alt="Context Video Translator overview showing synchronized source and translated subtitles on a video player.">'
    )
    if old_hero not in html:
        raise RuntimeError("Context Translator hero markup changed; update build_site.py explicitly.")
    html = html.replace(old_hero, new_hero, 1)
    context_page.write_text(html, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="_site")
    args = parser.parse_args()

    output = ROOT / args.output
    site_url = os.environ.get("SITE_URL", DEFAULT_URL).rstrip("/")
    token = os.environ.get("CF_ANALYTICS_TOKEN", "")
    build(output, site_url, token)
    optimize_artifact(output)

    print(f"Built optimized production artifact at {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
