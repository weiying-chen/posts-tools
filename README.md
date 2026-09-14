# posts-tools

Post-generation tooling.

## Scripts

- `prepare_posts.sh`: prepare `_al.docx` post skeletons from a schedule `.docx`.
- `gen_posts.sh`: generate a finished post DOCX from completed post text.
- `ref_posts.py`: rebuild the Markdown reference bundles under `~/text/posts/refs`.
- `clean_posts`: normalize smart quotes and remove obsolete source labels from
  generated posts while preserving Word formatting.
- `highlight_posts`: turn paired `*text*` markers in generated post DOCX files into bright-green highlights.
- `check_posts`: verify each post contains an accepted English call to action (`Let's take a listen!`, `Let's take a look.`, `Let's hear what <subject> has to say.`, or `Let's get moving!`) and an accepted Chinese call to action (`一起來聽聽！`, `一起來看看。`, `一起來聽聽<主題>怎麼說。`, or `現在就跟著教練一起動起來！`).
- `finalize_posts`: apply green highlighting to paired `*text*` markers, make
  reference material after `參考資料：` cyan while preserving green spans,
  normalize smart quotes to straight quotes, then check the post copy for the
  required phrases.

## Usage

Prepare post skeletons from a schedule file:

```bash
/home/weiying/python/posts-tools/prepare_posts.sh /path/to/schedule.docx
```

If exactly one `.docx` exists in current directory, argument is optional:

```bash
/home/weiying/python/posts-tools/prepare_posts.sh
```

Generate a finished post from completed text:

```bash
/home/weiying/python/posts-tools/gen_posts.sh /path/to/post.txt
```

Clean generated posts independently:

```bash
/home/weiying/python/posts-tools/clean_posts
```

By default this cleans DOCX files in place. Use `--copy` for side-by-side
`_cleaned.docx` files, or `--output-dir` to write copies elsewhere.

Highlight generated posts in place:

```bash
/home/weiying/python/posts-tools/highlight_posts --in-place
```

If shell aliases are loaded, use the short alias:

```bash
hs
```

By default this processes all `.docx` files in the current directory, skipping Word temp files like `~$...docx`.
Without `--in-place`, it writes side-by-side files with the suffix `_highlighted`.
Pass files or folders explicitly if needed:

```bash
/home/weiying/python/posts-tools/highlight_posts /path/to/output
```

Check generated posts for required phrases:

```bash
/home/weiying/python/posts-tools/check_posts
```

Run the full finalization flow:

```bash
/home/weiying/python/posts-tools/finalize_posts
```

Rebuild post references:

```bash
python3 /home/weiying/python/posts-tools/ref_posts.py
```

Pass `--latest N` to select up to N complete batches; the default is 6. If
fewer complete batches exist, all available batches are included and the
filename uses the actual count.

Use `--dry-run` to list stale outputs without writing, or `--check` to exit
nonzero when generated references are stale. Pass `--root` to use a posts
project somewhere other than `~/text/posts`.

By default this finalizes in place and keeps the existing filename, including `*_al.docx`.
Use `--copy` to keep the source file and write a separate finalized file instead.
Without a custom `--suffix`, copy mode writes `*_finalized.docx`.
