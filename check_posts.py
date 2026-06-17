#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from docx import Document
except ImportError as exc:  # pragma: no cover - depends on local environment
    raise SystemExit(
        "python-docx is required. Try running: "
        "/home/weiying/python/word/.venv/bin/python check_posts.py"
    ) from exc

from posts_common import resolve_targets

REQUIRED_PHRASES = (
    "Let's take a listen!",
    "一起來聽聽！",
)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="check-posts",
        description="Check DOCX posts for required listening prompt phrases.",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="DOCX files or folders. Default: all DOCX files in the current directory.",
    )
    return parser.parse_args(argv)


def read_docx_text(path: Path) -> str:
    doc = Document(str(path))
    return "\n".join(paragraph.text for paragraph in doc.paragraphs)


def find_missing_phrases(path: Path) -> list[str]:
    text = read_docx_text(path)
    return [phrase for phrase in REQUIRED_PHRASES if phrase not in text]


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    targets = resolve_targets(args.paths)

    if not targets:
        print("[warn] no DOCX files found in the current directory", file=sys.stderr)
        return 1

    exit_code = 0
    for source in targets:
        if not source.exists():
            print(f"[error] not found: {source}", file=sys.stderr)
            exit_code = 1
            continue
        if source.suffix.lower() != ".docx":
            print(f"[skip] not a .docx file: {source}", file=sys.stderr)
            continue

        missing = find_missing_phrases(source)
        if missing:
            exit_code = 1
            joined = ", ".join(repr(item) for item in missing)
            print(f"[missing] {source}: {joined}")
            continue

        print(f"[ok] {source}")

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
