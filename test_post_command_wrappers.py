from pathlib import Path


ROOT = Path(__file__).resolve().parent


def test_clean_posts_wrapper_targets_cleaner() -> None:
    wrapper = (ROOT / "clean_posts").read_text(encoding="utf-8")

    assert "CLEAN_POSTS_PYTHON" in wrapper
    assert '"$SCRIPT_DIR/clean_posts.py" "$@"' in wrapper


def test_prepare_posts_wrapper_targets_preparation_script() -> None:
    wrapper = (ROOT / "prepare_posts.sh").read_text(encoding="utf-8")

    assert "prepare-posts [schedule_docx] [output_dir]" in wrapper
    assert "$HOME/python/word/prepare_posts.py" in wrapper
    assert "--schedule" in wrapper


def test_gen_posts_wrapper_targets_finished_post_generator() -> None:
    wrapper = (ROOT / "gen_posts.sh").read_text(encoding="utf-8")

    assert "gen-posts [post_txt] [output_docx]" in wrapper
    assert "$HOME/python/word/generate_posts.py" in wrapper
    assert '  --input "$post_txt"' in wrapper
    assert '  --output "$output_docx"' in wrapper
    assert "--schedule" not in wrapper
