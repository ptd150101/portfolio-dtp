#!/usr/bin/env python3
"""Audit image markup, binary headers, dimensions, lazy loading and SVG validity."""

from __future__ import annotations

import json
import struct
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, asdict
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports"
PREFIX = "/portfolio-dtp/"
EAGER_IMAGES = {
    "assets/context-real-translation-vietnamese.png",
    "assets/og-remotekey.svg",
}
MAX_WARNING_BYTES = 3 * 1024 * 1024


@dataclass
class Finding:
    severity: str
    page: str
    asset: str
    message: str


class ImageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.images: list[dict[str, str | None]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "img":
            self.images.append(dict(attrs))


def map_src(page: Path, src: str) -> Path:
    path = unquote(urlsplit(src).path)
    if path.startswith(PREFIX):
        return ROOT / path[len(PREFIX):]
    if path.startswith("/"):
        return ROOT / path.lstrip("/")
    return page.parent / path


def png_size(data: bytes) -> tuple[int, int]:
    if data[:8] != b"\x89PNG\r\n\x1a\n" or len(data) < 24:
        raise ValueError("invalid PNG signature")
    return struct.unpack(">II", data[16:24])


def main() -> int:
    findings: list[Finding] = []
    html_files = [p for p in ROOT.rglob("*.html") if not any(x in p.parts for x in ("node_modules", "_site", "playwright-report"))]

    for page in html_files:
        parser = ImageParser()
        parser.feed(page.read_text(encoding="utf-8"))
        for attrs in parser.images:
            src = attrs.get("src") or ""
            rel_page = str(page.relative_to(ROOT))
            if not src:
                findings.append(Finding("error", rel_page, "", "Image is missing src"))
                continue
            asset = map_src(page, src).resolve()
            try:
                rel_asset = asset.relative_to(ROOT.resolve())
            except ValueError:
                findings.append(Finding("error", rel_page, src, "Image source escapes repository root"))
                continue
            if not asset.exists():
                findings.append(Finding("error", rel_page, str(rel_asset), "Image file does not exist"))
                continue
            if "alt" not in attrs:
                findings.append(Finding("error", rel_page, str(rel_asset), "Image is missing alt attribute"))
            if not attrs.get("width") or not attrs.get("height"):
                findings.append(Finding("error", rel_page, str(rel_asset), "Image must declare intrinsic width and height"))
            eager = str(rel_asset).replace("\\", "/") in EAGER_IMAGES or attrs.get("fetchpriority") == "high"
            if eager and attrs.get("loading") == "lazy":
                findings.append(Finding("error", rel_page, str(rel_asset), "Above-the-fold image must not be lazy-loaded"))
            if not eager and attrs.get("loading") != "lazy":
                findings.append(Finding("error", rel_page, str(rel_asset), "Below-the-fold image must use loading=lazy"))
            if attrs.get("decoding") != "async":
                findings.append(Finding("warning", rel_page, str(rel_asset), "Consider decoding=async"))

    assets = ROOT / "assets"
    for path in assets.rglob("*"):
        if not path.is_file():
            continue
        rel = str(path.relative_to(ROOT))
        try:
            if path.suffix.lower() == ".png":
                data = path.read_bytes()
                width, height = png_size(data)
                if width <= 0 or height <= 0:
                    raise ValueError("non-positive dimensions")
                if len(data) > MAX_WARNING_BYTES:
                    findings.append(Finding("warning", "", rel, f"Large PNG: {len(data) / 1024 / 1024:.2f} MiB"))
            elif path.suffix.lower() == ".svg":
                ET.parse(path)
        except (ValueError, ET.ParseError) as exc:
            findings.append(Finding("error", "", rel, f"Invalid asset: {exc}"))

    report = [asdict(item) for item in findings]
    REPORT_DIR.mkdir(exist_ok=True)
    (REPORT_DIR / "assets.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = ["# Asset audit", ""]
    errors = [f for f in findings if f.severity == "error"]
    warnings = [f for f in findings if f.severity == "warning"]
    lines.append(f"Errors: {len(errors)} · Warnings: {len(warnings)}")
    lines.append("")
    for f in findings:
        location = f" in `{f.page}`" if f.page else ""
        lines.append(f"- **{f.severity.upper()}** `{f.asset}`{location} — {f.message}")
    if not findings:
        lines.append("No asset issues were found.")
    (REPORT_DIR / "assets.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    for warning in warnings:
        print(f"WARNING: {warning.asset}: {warning.message}")
    if errors:
        print("\n".join(lines), file=sys.stderr)
        return 1
    print(f"Asset audit passed with {len(warnings)} warning(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
