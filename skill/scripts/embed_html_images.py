#!/usr/bin/env python3
"""Package a paper reader as one self-contained HTML file."""

from __future__ import annotations

import argparse
import base64
import mimetypes
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit


IMG_SRC_RE = re.compile(
    r"(?P<prefix><img\b[^>]*?\bsrc\s*=\s*)(?P<quote>['\"])(?P<src>.*?)(?P=quote)",
    re.IGNORECASE | re.DOTALL,
)
ICON_LINK_RE = re.compile(
    r"<link\b[^>]*\brel\s*=\s*['\"](?:shortcut\s+)?icon['\"]",
    re.IGNORECASE,
)
DATA_FAVICON = '<link rel="icon" href="data:,">'


def image_to_data_uri(path: Path) -> str:
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    if not mime.startswith("image/"):
        raise ValueError(f"Not an image MIME type: {path} ({mime})")
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def resolve_local_image(html_path: Path, src: str) -> Path:
    parsed = urlsplit(src)
    if parsed.scheme or parsed.netloc:
        raise ValueError(f"External image URL cannot be embedded: {src}")
    image_path = (html_path.parent / unquote(parsed.path)).resolve()
    if not image_path.is_file():
        raise FileNotFoundError(f"Image referenced by HTML does not exist: {image_path}")
    return image_path


def inject_data_favicon(html: str) -> str:
    if ICON_LINK_RE.search(html):
        return html
    charset_meta = re.search(r"<meta\b[^>]*\bcharset\s*=", html, re.IGNORECASE)
    if charset_meta:
        end = html.find(">", charset_meta.start())
        if end != -1:
            return html[: end + 1] + "\n  " + DATA_FAVICON + html[end + 1 :]
    closing_head = re.search(r"</head\s*>", html, re.IGNORECASE)
    if closing_head:
        return html[: closing_head.start()] + "  " + DATA_FAVICON + "\n" + html[closing_head.start() :]
    return DATA_FAVICON + "\n" + html


def build_self_contained_html(source: Path, target: Path) -> tuple[int, int]:
    source = Path(source).resolve()
    target = Path(target).resolve()
    html = source.read_text(encoding="utf-8-sig")
    embedded_count = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal embedded_count
        src = match.group("src").strip()
        if src.startswith("data:"):
            return match.group(0)
        image_path = resolve_local_image(source, src)
        embedded_count += 1
        return f'{match.group("prefix")}"{image_to_data_uri(image_path)}"'

    output = inject_data_favicon(IMG_SRC_RE.sub(replace, html))
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(output, encoding="utf-8")
    return embedded_count, target.stat().st_size


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="HTML with local image references")
    parser.add_argument("target", type=Path, help="self-contained output HTML")
    args = parser.parse_args()

    count, size = build_self_contained_html(args.source, args.target)
    print(f"Embedded images: {count}")
    print(f"Output: {args.target.resolve()}")
    print(f"Size: {size / 1024 / 1024:.2f} MiB")


if __name__ == "__main__":
    main()
