from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import ref_posts


class RefPostsTests(unittest.TestCase):
    def test_normalize_blank_lines_collapses_runs_and_edges(self):
        self.assertEqual(
            ref_posts.normalize_blank_lines(["", "A", "", "", "B", "", ""]),
            ["A", "", "B"],
        )

    def test_default_root_is_posts_folder(self):
        self.assertEqual(ref_posts.DEFAULT_ROOT, Path.home() / "text" / "posts")

    def test_latest_posts_defaults_to_four_and_falls_back_to_existing(self):
        original_root = ref_posts.ROOT
        try:
            with TemporaryDirectory() as directory:
                root = Path(directory)
                ref_posts.ROOT = root
                for number in range(1, 6):
                    folder = root / f"posts-{number}"
                    (folder / "refs").mkdir(parents=True)
                    (folder / "output").mkdir()
                    (folder / "edited").mkdir()
                    for mmdd in (f"0{number}01", f"0{number}02"):
                        (folder / "refs" / f"al_115{mmdd}_revision.docx").touch()
                        (folder / "output" / f"26{mmdd}_人間菩提小編文_al.docx").touch()
                        (folder / "edited" / f"26{mmdd}_人間菩提小編文_al_ev.docx").touch()

                batches = ref_posts.human_posts_pairs()
                self.assertEqual([folder.name for folder, _ in batches], [
                    "posts-2", "posts-3", "posts-4", "posts-5"
                ])

                for number in range(2, 6):
                    folder = root / f"posts-{number}"
                    for path in sorted(folder.rglob("*"), reverse=True):
                        if path.is_file():
                            path.unlink()
                        elif path.is_dir():
                            path.rmdir()
                    folder.rmdir()
                batches = ref_posts.human_posts_pairs()
                self.assertEqual([folder.name for folder, _ in batches], ["posts-1"])
        finally:
            ref_posts.ROOT = original_root


if __name__ == "__main__":
    unittest.main()
