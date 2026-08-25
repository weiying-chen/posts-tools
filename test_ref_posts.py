from pathlib import Path
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


if __name__ == "__main__":
    unittest.main()
