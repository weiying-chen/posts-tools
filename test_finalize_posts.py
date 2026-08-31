from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from docx import Document

from finalize_posts import main, normalize_smart_quotes


class FinalizePostsTests(unittest.TestCase):
    def test_normalizes_smart_quotes_before_phrase_check(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "post.docx"
            document = Document()
            paragraph = document.add_paragraph()
            run = paragraph.add_run(
                "The Master said “Let’s protect people’s health.” Let’s take a listen."
            )
            run.bold = True
            document.add_paragraph("一起來聽聽。")
            document.add_paragraph("參考資料：")
            document.save(path)

            self.assertEqual(main([str(path)]), 0)

            result = Document(path)
            self.assertEqual(
                result.paragraphs[0].text,
                'The Master said "Let\'s protect people\'s health." Let\'s take a listen.',
            )
            self.assertTrue(result.paragraphs[0].runs[0].bold)

    def test_normalizer_reports_replaced_characters(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "post.docx"
            document = Document()
            document.add_paragraph("‘one’ “two”")
            document.save(path)

            self.assertEqual(normalize_smart_quotes(path), 4)
            self.assertEqual(Document(path).paragraphs[0].text, "'one' \"two\"")


if __name__ == "__main__":
    unittest.main()
