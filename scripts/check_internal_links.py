#!/usr/bin/env python3
"""Validate local href/src references and same-page/cross-page anchors."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, asdict
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports"
HTML_FILES = [
    p for p in ROOT.rglob("*.html")
    if not any(part in {"node_modules", "playwright-report", "test-results", "_site"} for part in p.parts)
]
PREFIX = "/portfolio-dtp/"
SKIP_SCHEMES = {"http", "https", "mailto", "tel", "data", "javascript"}


@dataclass
class Finding:
    page: str
    attribute: str
    value: str
    message: str


class RefParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()
        self.refs: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = dict(attrs)
        if data.get("id"):
            self.ids.add(data["id"] or "")
        for attr in ("href", "src", "poster"):
            value = data.get(attr)
            if value:
                self.refs.append((attr, value))
        srcset = data.get("srcset")
        if srcset:
            for item in srcset.split(","):
                candidate = item.strip().split()[0]
                if candidate:
                    self.refs.append(("srcset", candidate))


def parse_html(path: Path) -> RefParser:
    parser = RefParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser


def map_local_path(page: Path, raw_path: str) -> Path:
    decoded = unquote(raw_path)
    if decoded.startswith(PREFIX):
        return ROOT / decoded[len(PREFIX):]
    if decoded.startswith("/"):
        return ROOT / decoded.lstrip("/")
    return page.parent / decoded


def resolve_document(path: Path) -> Path:
    if path.is_dir() or str(path).endswith("/"):
        return path / "index.html"
    if path.suffix == "":
        index_candidate = path / "index.html"
        if index_candidate.exists():
            return index_candidate
    return path


def main() -> int:
    parsed = {path.resolve(): parse_html(path) for path in HTML_FILES}
    findings: list[Finding] = []

    for page in HTML_FILES:
        parser = parsed[page.resolve()]
        for attr, raw in parser.refs:
            split = urlsplit(raw)
            if split.scheme in SKIP_SCHEMES or raw.startswith("//"):
                continue
            if split.path == "" and split.fragment:
                if split.fragment not in parser.ids:
                    findings.append(Finding(str(page.relative_to(ROOT)), attr, raw, "Fragment target does not exist on this page"))
                continue
            target = resolve_document(map_local_path(page, split.path).resolve())
            try:
                target.relative_to(ROOT.resolve())
            except ValueError:
                findings.append(Finding(str(page.relative_to(ROOT)), attr, raw, "Reference escapes the repository root"))
                continue
            if not target.exists():
                findings.append(Finding(str(page.relative_to(ROOT)), attr, raw, f"Target does not exist: {target.relative_to(ROOT)}"))
                continue
            if split.fragment and target.suffix.lower() in {".html", ".htm"}:
                target_parser = parsed.get(target.resolve())
                if target_parser is None:
                    target_parser = parse_html(target)
                    parsed[target.resolve()] = target_parser
                if split.fragment not in target_parser.ids:
                    findings.append(Finding(str(page.relative_to(ROOT)), attr, raw, f"Fragment #{split.fragment} does not exist in {target.relative_to(ROOT)}"))

    REPORT_DIR.mkdir(exist_ok=True)
    (REPORT_DIR / "internal-links.json").write_text(
        json.dumps([asdict(item) for item in findings], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    lines = ["# Internal link audit", "", f"Checked {len(HTML_FILES)} HTML files.", ""]
    if findings:
        lines.append(f"Found {len(findings)} error(s):")
        lines.extend(f"- `{f.page}` `{f.attribute}={f.value}` — {f.message}" for f in findings)
    else:
        lines.append("No broken local links, assets or fragment targets were found.")
    (REPORT_DIR / "internal-links.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    if findings:
        print("\n".join(lines), file=sys.stderr)
        return 1
    print(f"Internal link audit passed ({len(HTML_FILES)} HTML files).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
