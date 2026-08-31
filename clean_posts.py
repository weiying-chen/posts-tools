#!/usr/bin/env python3

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from docx import Document

from posts_common import output_path_for, resolve_targets


SMART_QUOTE_CHARS = "‘’“”"
SMART_QUOTE_TRANSLATION = str.maketrans(
    {
        "‘": "'",
        "’": "'",
        "“": '"',
        "”": '"',
    }
)


def clean_docx(path: Path) -> int:
    """Normalize a post DOCX in place and return the replacement count."""
    doc = Document(str(path))
    replacements = 0
    for paragraph in doc.paragraphs:
        for run in paragraph.runs:
            normalized = run.text.translate(SMART_QUOTE_TRANSLATION)
            if normalized == run.text:
                continue
            replacements += sum(run.text.count(char) for char in SMART_QUOTE_CHARS)
            run.text = normalized
    if replacements:
        doc.save(str(path))
    return replacements


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="clean-posts",
        description="Normalize generated post DOCX files.",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="DOCX files or folders. Default: all DOCX files in the current directory.",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        help="Write cleaned files to this folder instead of editing in place.",
    )
    parser.add_argument(
        "--copy",
        action="store_true",
        help="Keep the source and write a side-by-side `_cleaned` copy.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report target files without writing changes.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    targets = resolve_targets(args.paths)
    if not targets:
        print("[warn] no DOCX files found in the current directory", file=sys.stderr)
        return 1

    exit_code = 0
    for source in targets:
        if not source.exists():
            print(f"[file-not-found] {source}", file=sys.stderr)
            exit_code = 1
            continue
        if source.suffix.lower() != ".docx":
            print(f"[not-docx] {source}", file=sys.stderr)
            continue

        if args.output_dir is not None:
            destination = args.output_dir / source.name
        elif args.copy:
            destination = output_path_for(source, None, "_cleaned")
        else:
            destination = source

        if args.dry_run:
            print(f"[target] {source} -> {destination}")
            continue

        if destination != source:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        replacements = clean_docx(destination)
        if replacements:
            print(f"[cleaned] {destination} ({replacements} replacements)")
        else:
            print(f"[already-clean] {destination}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
