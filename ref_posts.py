#!/usr/bin/env python3
"""Build Markdown reference bundles for the posts project.

DOCX files are read directly with the Python standard library. Tracked-change
insertions are retained, while deleted and move-from text is excluded, giving
the same text as Word's accepted-changes view.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile


DEFAULT_ROOT = Path.home() / "text" / "posts"
DEFAULT_LATEST_BATCH_COUNT = 8
ROOT = DEFAULT_ROOT
REFS = ROOT / "refs"
W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W = f"{{{W_NS}}}"
WORLD_DAY_RE = re.compile(r"\bWorld[^\n]{0,80}?Day\b", re.IGNORECASE)
ZH_WORLD_DAY_RE = re.compile(r"世界[^\n]{0,30}?日")
INTERNATIONAL_DAY_RE = re.compile(
    r"\bInternational Day of Awareness of Food Loss and Waste\b",
    re.IGNORECASE,
)
ZH_INTERNATIONAL_DAY_RE = re.compile(r"國際[^\n]{0,40}?日")


@dataclass(frozen=True)
class Pair:
    key: str
    pre: Path
    post: Path
    revision: Path | None = None


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def docx_lines(path: Path) -> list[str]:
    """Extract accepted-change text, representing bright-green text as *text*."""
    with ZipFile(path) as archive:
        root = ET.fromstring(archive.read("word/document.xml"))

    parents = {child: parent for parent in root.iter() for child in parent}

    def excluded(node: ET.Element) -> bool:
        parent = parents.get(node)
        while parent is not None:
            if parent.tag in {W + "del", W + "moveFrom"}:
                return True
            parent = parents.get(parent)
        return False

    def green_highlighted(node: ET.Element) -> bool:
        parent = parents.get(node)
        while parent is not None and parent.tag != W + "p":
            if parent.tag == W + "r":
                highlight = parent.find(f"{W}rPr/{W}highlight")
                return (
                    highlight is not None
                    and highlight.get(W + "val") in {"green", "brightGreen"}
                )
            parent = parents.get(parent)
        return False

    lines: list[str] = []
    for paragraph in root.iter(W + "p"):
        parts: list[str] = []
        green = False
        for node in paragraph.iter():
            if excluded(node):
                continue
            if node.tag == W + "t":
                value = node.text or ""
            elif node.tag == W + "tab":
                value = "\t"
            elif node.tag in {W + "br", W + "cr"}:
                value = "\n"
            else:
                continue
            is_green = green_highlighted(node)
            if value and is_green != green:
                parts.append("*")
                green = is_green
            parts.append(value)
        if green:
            parts.append("*")
        lines.extend("".join(parts).split("\n"))
    return lines


def normalize_blank_lines(lines: list[str]) -> list[str]:
    """Keep one blank between blocks and discard edge padding."""
    normalized: list[str] = []
    for line in lines:
        if line.strip():
            normalized.append(line)
        elif normalized and normalized[-1].strip():
            normalized.append("")
    while normalized and not normalized[-1].strip():
        normalized.pop()
    return normalized


def append_document(lines: list[str], heading: str, path: Path) -> None:
    lines.extend(["", heading, f"Filename: `{relative(path)}`", ""])
    lines.extend(normalize_blank_lines(docx_lines(path)))


def human_posts_pairs(
    limit: int = DEFAULT_LATEST_BATCH_COUNT,
) -> list[tuple[Path, list[Pair]]]:
    eligible: list[tuple[int, Path, list[Pair]]] = []
    for folder in ROOT.iterdir():
        match = re.fullmatch(r"posts-(\d+)", folder.name)
        if not match or not folder.is_dir():
            continue
        pairs: list[Pair] = []
        refs = folder / "refs"
        for revision in sorted(refs.glob("al_115????_revision.docx")):
            date_match = re.search(r"115(\d{4})_revision$", revision.stem)
            if not date_match:
                continue
            mmdd = date_match.group(1)
            pre_candidates = sorted((folder / "output").glob(f"26{mmdd}_人間菩提小編文_al.docx"))
            post_candidates = sorted(
                (folder / "edited").glob(f"26{mmdd}_人間菩提小編文_al*_ev.docx")
            )
            if len(pre_candidates) == 1 and len(post_candidates) == 1:
                pairs.append(Pair(f"115{mmdd}", pre_candidates[0], post_candidates[0], revision))
        # A standard batch contains exactly two 人間菩提 posts. Requiring two
        # prevents a partially edited new batch from displacing a complete one.
        if len(pairs) >= 2:
            eligible.append((int(match.group(1)), folder, pairs))
    if limit < 1:
        raise ValueError("limit must be at least 1")
    return [(folder, pairs) for _, folder, pairs in sorted(eligible)[-limit:]]


def generate_latest_posts(limit: int = DEFAULT_LATEST_BATCH_COUNT) -> str:
    batches = human_posts_pairs(limit)
    if not batches:
        raise RuntimeError("No complete two-pair posts batches were found")
    names = [folder.name for folder, _ in batches]
    lines = [
        f"# Latest {len(batches)} Posts",
        "",
        f"Reference batches from {', '.join(f'`{name}`' for name in names)}. "
        "Each batch contains two 人間菩提小編文 sets: the complete revision "
        "script, pre-edit `_al`, and post-edit `_al_ev`.",
    ]
    for folder, pairs in batches:
        lines.extend(["", "---", "", f"# {folder.name}"])
        for pair in pairs:
            lines.extend(["", f"## {pair.key}"])
            append_document(lines, "### Revision", pair.revision)  # type: ignore[arg-type]
            append_document(lines, "### Pre-edit", pair.pre)
            append_document(lines, "### Post-edit", pair.post)
    return "\n".join(normalize_blank_lines(lines)) + "\n"


def accepted_text(path: Path) -> str:
    return "\n".join(docx_lines(path))


def is_world_day(path: Path) -> bool:
    text = accepted_text(path)
    return bool(
        WORLD_DAY_RE.search(text)
        or ZH_WORLD_DAY_RE.search(text)
        or INTERNATIONAL_DAY_RE.search(text)
        or ZH_INTERNATIONAL_DAY_RE.search(text)
    )


def world_day_pairs() -> list[Pair]:
    found: dict[tuple[Path, Path], Pair] = {}

    # Current convention: output/foo_al.docx -> edited/foo_al_ev.docx.
    for post in ROOT.glob("**/edited/*_al*_ev.docx"):
        pre_name = re.sub(r"_al(?: \d+)?_ev\.docx$", "_al.docx", post.name)
        pre = post.parent.parent / "output" / pre_name
        if pre.is_file() and (is_world_day(pre) or is_world_day(post)):
            found[(pre, post)] = Pair(pre.stem.removesuffix("_al"), pre, post)

    # Earlier convention: backup/foo_al.docx -> output/foo_al.docx.
    for pre in ROOT.glob("**/backup/*_al.docx"):
        post = pre.parent.parent / "output" / pre.name
        if post.is_file() and pre.read_bytes() != post.read_bytes() and (is_world_day(pre) or is_world_day(post)):
            found[(pre, post)] = Pair(pre.stem.removesuffix("_al"), pre, post)

    return sorted(found.values(), key=lambda pair: relative(pair.pre))


def observance(path: Path) -> str:
    text = accepted_text(path)
    en = WORLD_DAY_RE.search(text) or INTERNATIONAL_DAY_RE.search(text)
    zh = ZH_WORLD_DAY_RE.search(text) or ZH_INTERNATIONAL_DAY_RE.search(text)
    labels = []
    if en:
        labels.append(en.group(0).strip())
    if zh:
        labels.append(zh.group(0).strip())
    return " / ".join(dict.fromkeys(labels)) or path.stem


def generate_world_days() -> str:
    pairs = world_day_pairs()
    lines = [
        "# Observance Post References",
        "",
        "Complete matched pre-edit and post-edit reference posts connected to "
        "a World or International Day observance. No revision/original-script "
        "files are included.",
    ]
    for pair in pairs:
        lines.extend(["", "---", "", f"# {observance(pair.pre)}"])
        append_document(lines, "## Pre-edit", pair.pre)
        append_document(lines, "## Post-edit", pair.post)
    return "\n".join(normalize_blank_lines(lines)) + "\n"


def update(path: Path, content: str, check: bool) -> bool:
    current = path.read_text(encoding="utf-8") if path.exists() else None
    changed = current != content
    if changed and not check:
        path.write_text(content, encoding="utf-8")
    return changed


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=DEFAULT_ROOT,
        help=f"posts project root (default: {DEFAULT_ROOT})",
    )
    parser.add_argument(
        "--latest",
        type=int,
        default=DEFAULT_LATEST_BATCH_COUNT,
        help=f"maximum number of latest batches to include (default: {DEFAULT_LATEST_BATCH_COUNT})",
    )
    parser.add_argument("--check", action="store_true", help="report stale outputs without rewriting them")
    parser.add_argument("--dry-run", action="store_true", help="show files that would change without rewriting them")
    args = parser.parse_args(argv)
    if args.latest < 1:
        parser.error("--latest must be at least 1")
    return args


def main() -> int:
    global ROOT, REFS
    args = parse_args()

    ROOT = args.root.expanduser().resolve()
    REFS = ROOT / "refs"
    if not ROOT.is_dir():
        raise SystemExit(f"Missing posts project root: {ROOT}")
    REFS.mkdir(parents=True, exist_ok=True)

    selected_count = len(human_posts_pairs(args.latest))
    outputs = {
        REFS / f"latest-{selected_count}-posts.md": generate_latest_posts(args.latest),
        REFS / "world-day-posts.md": generate_world_days(),
    }
    readonly = args.check or args.dry_run
    changed = [path for path, content in outputs.items() if update(path, content, readonly)]
    if args.check and changed:
        for path in changed:
            print(f"stale: {relative(path)}", file=sys.stderr)
        return 1
    if args.dry_run:
        for path in changed:
            print(f"would update: {relative(path)}")
        if not changed:
            print("reference files are up to date")
        return 0
    for path in changed:
        print(f"updated: {relative(path)}")
    if not changed:
        print("reference files are up to date")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
