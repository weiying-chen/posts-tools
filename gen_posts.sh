#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOH'
Usage:
  gen-posts [post_txt] [output_docx]

Generate a finished post DOCX from completed post text.

Defaults:
  post_txt:    the only .txt in the current directory
  output_docx: ./output/<post_txt_stem>_al.docx

Environment overrides:
  GENERATE_POSTS_SCRIPT   default: $HOME/python/word/generate_posts.py
  GENERATE_POSTS_PYTHON   default: $HOME/python/word/.venv/bin/python
  GENERATE_POSTS_TEMPLATE default: $HOME/python/word/templates/post_template.docx
EOH
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

SCRIPT_PATH="${GENERATE_POSTS_SCRIPT:-$HOME/python/word/generate_posts.py}"
PYTHON_BIN="${GENERATE_POSTS_PYTHON:-$HOME/python/word/.venv/bin/python}"
TEMPLATE_PATH="${GENERATE_POSTS_TEMPLATE:-$HOME/python/word/templates/post_template.docx}"

post_txt="${1:-}"
if [[ -z "$post_txt" ]]; then
  mapfile -t txt_files < <(find . -maxdepth 1 -type f -name '*.txt' | sort)
  if [[ "${#txt_files[@]}" -ne 1 ]]; then
    echo "[error] expected exactly one .txt in current folder, found ${#txt_files[@]}" >&2
    echo "[info] pass post txt explicitly: gen-posts /path/to/post.txt" >&2
    exit 1
  fi
  post_txt="${txt_files[0]}"
fi

post_name="$(basename "$post_txt")"
post_stem="${post_name%.txt}"
if [[ "$post_stem" != *_al ]]; then
  post_stem="${post_stem}_al"
fi
output_docx="${2:-./output/${post_stem}.docx}"

if [[ ! -f "$post_txt" ]]; then
  echo "[error] post txt not found: $post_txt" >&2
  exit 1
fi
if [[ ! -f "$SCRIPT_PATH" ]]; then
  echo "[error] generate_posts script not found: $SCRIPT_PATH" >&2
  exit 1
fi
if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "[error] python binary not executable: $PYTHON_BIN" >&2
  exit 1
fi
if [[ ! -f "$TEMPLATE_PATH" ]]; then
  echo "[error] template not found: $TEMPLATE_PATH" >&2
  exit 1
fi

mkdir -p "$(dirname "$output_docx")"

"$PYTHON_BIN" "$SCRIPT_PATH" \
  --input "$post_txt" \
  --template "$TEMPLATE_PATH" \
  --output "$output_docx"

echo "[created] $(basename "$output_docx")"
