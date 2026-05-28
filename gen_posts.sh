#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOH'
Usage:
  gen-posts [schedule_docx] [output_dir]

Generate post docs from a schedule DOCX.

Defaults:
  schedule_docx: the only .docx in current directory
  output_dir:    ./output

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

schedule_docx="${1:-}"
if [[ -z "$schedule_docx" ]]; then
  mapfile -t docx_files < <(find . -maxdepth 1 -type f -name '*.docx' | sort)
  if [[ "${#docx_files[@]}" -ne 1 ]]; then
    echo "[error] expected exactly one .docx in current folder, found ${#docx_files[@]}" >&2
    echo "[info] pass schedule docx explicitly: gen-posts /path/to/schedule.docx" >&2
    exit 1
  fi
  schedule_docx="${docx_files[0]}"
fi

OUTPUT_DIR="${2:-./output}"

if [[ ! -f "$schedule_docx" ]]; then
  echo "[error] schedule docx not found: $schedule_docx" >&2
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

mkdir -p "$OUTPUT_DIR"

"$PYTHON_BIN" "$SCRIPT_PATH" \
  --schedule "$schedule_docx" \
  --template "$TEMPLATE_PATH" \
  --output-dir "$OUTPUT_DIR"

created=0
while IFS= read -r f; do
  echo "[created] $(basename "$f")"
  created=$((created + 1))
done < <(find "$OUTPUT_DIR" -maxdepth 1 -type f -name '*_al.docx' | sort)

if (( created == 0 )); then
  echo "[warn] no *_al.docx files found in: $OUTPUT_DIR"
fi
