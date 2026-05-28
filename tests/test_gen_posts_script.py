import unittest
from pathlib import Path


SCRIPT_PATH = Path('/home/weiying/python/posts-tools/gen_posts.sh')


class GenPostsScriptUnitTest(unittest.TestCase):
    def test_usage_mentions_gen_posts(self) -> None:
        script = SCRIPT_PATH.read_text(encoding='utf-8')
        self.assertIn('gen-posts [schedule_docx] [output_dir]', script)

    def test_script_calls_generate_posts(self) -> None:
        script = SCRIPT_PATH.read_text(encoding='utf-8')
        self.assertIn('generate_posts.py', script)
        self.assertIn('--schedule', script)
        self.assertIn('--output-dir', script)


if __name__ == '__main__':
    unittest.main()
