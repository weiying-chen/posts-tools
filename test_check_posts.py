from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from docx import Document

from check_posts import find_missing_phrases


class CheckPostsTests(unittest.TestCase):
    def make_docx(self, paragraphs: list[str], directory: str) -> Path:
        path = Path(directory) / "post.docx"
        document = Document()
        for text in paragraphs:
            document.add_paragraph(text)
        document.save(path)
        return path

    def test_reference_material_cannot_satisfy_required_phrases(self) -> None:
        with TemporaryDirectory() as directory:
            path = self.make_docx(
                [
                    "標題",
                    "{{POST_EN}}",
                    "{{POST_ZH}}",
                    "參考資料：",
                    "Let's hear what a physician has to say.",
                    "一起來聽聽中醫師怎麼說。",
                ],
                directory,
            )

            self.assertEqual(len(find_missing_phrases(path)), 2)

    def test_phrases_in_post_copy_still_pass(self) -> None:
        with TemporaryDirectory() as directory:
            path = self.make_docx(
                [
                    "Let's hear what a physician has to say.",
                    "一起來聽聽中醫師怎麼說。",
                    "參考資料:",
                    "source material",
                ],
                directory,
            )

            self.assertEqual(find_missing_phrases(path), [])


if __name__ == "__main__":
    unittest.main()
