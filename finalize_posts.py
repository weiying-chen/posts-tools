#!/usr/bin/env python3

from __future__ import annotations

import argparse
import shutil
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

        changed, _skipped = highlight_docx(source, destination)
        if not changed and destination != source:
            destination.parent.mkdir(parents=True, exist_ok=True)
            if args.copy or args.output_dir is not None:
                shutil.copy2(source, destination)
            else:
                source.replace(destination)
        if changed:
            print(f"[highlighted] {destination} ({changed} paragraph(s))")
        else:
            print(f"[no-highlights] {destination}")

        check_path = destination if destination.exists() else source
        missing = find_missing_phrases(check_path)
        if missing:
            exit_code = 1
            joined = ", ".join(repr(item) for item in missing)
            print(f"[check-failed] {check_path}: {joined}")
        else:
            print(f"[check-passed] {check_path}")

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
