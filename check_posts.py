#!/usr/bin/env python3

from __future__ import annotations

import argparse
from dataclasses import dataclass
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


@dataclass(frozen=True)
class RequiredPhraseGroup:
    display: str
    variants: tuple[str, ...]


def phrase_variants(base: str, punctuation: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(f"{base}{mark}" for mark in punctuation)


REQUIRED_PHRASE_GROUPS = (
    RequiredPhraseGroup(
        display="Let's take a listen! or Let's take a listen.",
        variants=phrase_variants("Let's take a listen", ("!", ".")),
    ),
    RequiredPhraseGroup(
        display="一起來聽聽！或一起來聽聽。",
        variants=phrase_variants("一起來聽聽", ("！", "。")),
    ),
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
    if any(variant in text for group in REQUIRED_PHRASE_GROUPS for variant in group.variants):
        return []

    return [
        "Let's take a listen! or Let's take a listen. / 一起來聽聽！或一起來聽聽。"
    ]


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    targets = resolve_targets(args.paths)

    if not targets:
        print("[warn] no DOCX files found in the current directory", file=sys.stderr)
        return 1

    exit_code = 0
    for source in targets:
        if not source.exists():
            print(f"[not-found] {source}", file=sys.stderr)
            exit_code = 1
            continue
        if source.suffix.lower() != ".docx":
            print(f"[skipped] not a .docx file: {source}", file=sys.stderr)
            continue

        missing = find_missing_phrases(source)
        if missing:
            exit_code = 1
            joined = ", ".join(repr(item) for item in missing)
            print(f"[check-failed] {source}: {joined}")
            continue

        print(f"[check-passed] {source}")

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
