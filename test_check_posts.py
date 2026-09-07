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

    def test_take_a_look_phrases_pass(self) -> None:
        with TemporaryDirectory() as directory:
            path = self.make_docx(
                [
                    "Let's take a look.",
                    "一起來看看。",
                    "參考資料：",
                    "source material",
                ],
                directory,
            )

            self.assertEqual(find_missing_phrases(path), [])

    def test_descriptive_look_call_to_action_phrases_pass(self) -> None:
        with TemporaryDirectory() as directory:
            path = self.make_docx(
                [
                    (
                        "As September 29 marks the International Day of Awareness "
                        "of Food Loss and Waste, let's see how simple choices can "
                        "keep good food from going to waste."
                    ),
                    "一起來看看，我們如何從生活中的小小選擇做起，讓珍貴的食物不被浪費。",
                    "參考資料：",
                    "source material",
                ],
                directory,
            )

            self.assertEqual(find_missing_phrases(path), [])

    def test_unfinished_descriptive_look_phrases_still_fail(self) -> None:
        with TemporaryDirectory() as directory:
            path = self.make_docx(
                ["Now let's see how", "一起來看看，", "參考資料："],
                directory,
            )

            self.assertEqual(len(find_missing_phrases(path)), 2)


if __name__ == "__main__":
    unittest.main()
