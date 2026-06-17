# posts-tools

Post-generation tooling.

## Scripts

- `gen_posts.sh`: generate `_al.docx` post files from a schedule `.docx`.
- `highlight_posts`: turn paired `*text*` markers in generated post DOCX files into bright-green highlights.
- `check_posts`: verify each post contains `Let's take a listen!` and `一起來聽聽！`.
- `finalize_posts`: run highlighting first, then run the phrase checker.

## Usage

Generate posts from a schedule file:

```bash
/home/weiying/python/posts-tools/gen_posts.sh /path/to/schedule.docx
```

If exactly one `.docx` exists in current directory, argument is optional:

```bash
/home/weiying/python/posts-tools/gen_posts.sh
```

Highlight generated posts in place:

```bash
/home/weiying/python/posts-tools/highlight_posts
```

If shell aliases are loaded, use the short alias:

```bash
hs
```

By default this processes all `.docx` files in the current directory, skipping Word temp files like `~$...docx`.
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
