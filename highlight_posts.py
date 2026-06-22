#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from posts_common import output_path_for, resolve_targets
from posts_highlight import highlight_docx


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="highlight-posts",
        description=(
            "Turn paired *text* markers in generated post DOCX files into "
            "bright-green Word highlights."
        )
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
        help="Write processed files to this folder instead of editing in place.",
    )
    parser.add_argument(
        "--suffix",
        default=None,
        help=(
            "Suffix for side-by-side output. "
            "Default is '_highlighted' unless --in-place is used."
        ),
    )
    parser.add_argument(
        "--in-place",
        action="store_true",
        help="Edit files in place instead of writing side-by-side output.",
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
    suffix = "" if args.in_place else (args.suffix or "_highlighted")

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

        destination = output_path_for(source, args.output_dir, suffix)
        if args.dry_run:
            print(f"[target] {source} -> {destination}")
            continue

        changed, skipped = highlight_docx(source, destination)
        if changed:
            print(f"[highlighted] {destination} ({changed} paragraph(s))")
        else:
            print(f"[no-highlights] {destination}")
        if skipped:
            print(
                f"[skipped-hyperlinks] {source} ({skipped} paragraph(s))",
                file=sys.stderr,
            )

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
