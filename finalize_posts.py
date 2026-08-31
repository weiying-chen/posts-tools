#!/usr/bin/env python3

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from check_posts import find_missing_phrases
from clean_posts import clean_docx
from posts_common import output_path_for, resolve_targets
from posts_highlight import highlight_docx


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="finalize-posts",
        description=(
            "Run post finalization steps: apply highlights, then check for required phrases."
        ),
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
        help="Write highlighted files to this folder instead of editing in place.",
    )
    parser.add_argument(
        "--suffix",
        default=None,
        help=(
            "Suffix for side-by-side copy output. "
            "Default is '_finalized' when --copy is used."
        ),
    )
    parser.add_argument(
        "--copy",
        action="store_true",
        help="Keep the source file and write a side-by-side finalized copy instead.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report target files without writing changes or running checks.",
    )
    return parser.parse_args(argv)


def destination_for(source: Path, args: argparse.Namespace) -> Path:
    if args.output_dir is not None:
        return args.output_dir / source.name
    if args.copy:
        return output_path_for(source, None, args.suffix or "_finalized")
    return source


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

        destination = destination_for(source, args)
        if args.dry_run:
            print(f"[target] {source} -> {destination}")
            continue

        if destination != source:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)

        cleanup_changes = clean_docx(destination)
        if cleanup_changes:
            print(f"[cleaned] {destination} ({cleanup_changes} changes)")

        result = highlight_docx(destination, destination)
        if result.changed:
            print(
                f"[highlighted] {destination} "
                f"(green: {result.green_paragraphs}, "
                f"cyan: {result.cyan_paragraphs}, "
                f"total: {result.total_paragraphs})"
            )
        else:
            print(f"[no-highlights] {destination}")

        missing = find_missing_phrases(destination)
        if missing:
            exit_code = 1
            joined = ", ".join(repr(item) for item in missing)
            print(f"[check-failed] {destination}: {joined}")
        else:
            print(f"[check-passed] {destination}")

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
