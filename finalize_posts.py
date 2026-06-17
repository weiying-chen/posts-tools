#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from check_posts import find_missing_phrases
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
        default="",
        help=(
            "Suffix for side-by-side output, for example '_highlighted'. "
            "Default is empty, so files are edited in place unless --output-dir is used."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report target files without writing changes or running checks.",
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
            print(f"[error] not found: {source}", file=sys.stderr)
            exit_code = 1
            continue
        if source.suffix.lower() != ".docx":
            print(f"[skip] not a .docx file: {source}", file=sys.stderr)
            continue

        destination = output_path_for(source, args.output_dir, args.suffix)
        if args.dry_run:
            print(f"[target] {source} -> {destination}")
            continue

        changed, skipped = highlight_docx(source, destination)
        if changed:
            print(f"[updated] {destination} ({changed} paragraph(s))")
        else:
            print(f"[unchanged] {destination}")
        if skipped:
            print(
                f"[warn] skipped {skipped} hyperlink paragraph(s) in {source}",
                file=sys.stderr,
            )

        check_path = destination if destination.exists() else source
        missing = find_missing_phrases(check_path)
        if missing:
            exit_code = 1
            joined = ", ".join(repr(item) for item in missing)
            print(f"[missing] {check_path}: {joined}")
        else:
            print(f"[ok] {check_path}")

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
