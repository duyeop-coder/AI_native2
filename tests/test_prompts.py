import os
import tempfile
import unittest
from unittest import mock

import main


def sample():
    return [
        {"title": "Hello Title", "content": "본문", "category": "글쓰기", "favorite": False, "views": 0},
        {"title": "제목2", "content": "contains HELLO inside", "category": "코딩", "favorite": True, "views": 3},
        {"title": "제목3", "content": "x", "category": "코딩", "favorite": False, "views": 5},
    ]


def run_with_input(func, prompts, *answers):
    with mock.patch("builtins.input", side_effect=list(answers)), mock.patch("builtins.print"):
        func(prompts)


class PromptTests(unittest.TestCase):
    def test_add_prompt_reflected_in_list(self):
        prompts = sample()
        run_with_input(main.add_prompt, prompts, "새 제목", "새 내용", "1")
        self.assertEqual(len(prompts), 4)
        self.assertEqual(prompts[-1]["category"], main.CATEGORIES[0])

    def test_add_prompt_retries_on_empty_title(self):
        prompts = sample()
        run_with_input(main.add_prompt, prompts, "  ", "제목", "내용", "1")
        self.assertEqual(prompts[-1]["title"], "제목")

    def test_duplicate_title_overwrite_and_cancel(self):
        prompts = sample()
        run_with_input(main.add_prompt, prompts, "hello title", "덮어씀", "2", "1")
        self.assertEqual((len(prompts), prompts[0]["content"]), (3, "덮어씀"))
        run_with_input(main.add_prompt, prompts, "hello title", "취소됨", "2", "3")
        self.assertEqual((len(prompts), prompts[0]["content"]), (3, "덮어씀"))

    def test_category_filter(self):
        matches = main.find_prompts(sample(), lambda p: p["category"] == "코딩")
        self.assertEqual([n for n, _ in matches], [2, 3])

    def test_search_title_or_content_case_insensitive(self):
        keyword = "hello"
        matches = main.find_prompts(
            sample(), lambda p: keyword in p["title"].lower() or keyword in p["content"].lower())
        self.assertEqual([n for n, _ in matches], [1, 2])

    def test_toggle_favorite(self):
        prompts = sample()
        run_with_input(main.toggle_favorite, prompts, "1")
        self.assertTrue(prompts[0]["favorite"])
        run_with_input(main.toggle_favorite, prompts, "1")
        self.assertFalse(prompts[0]["favorite"])

    def test_invalid_number_does_not_crash(self):
        prompts = sample()
        run_with_input(main.toggle_favorite, prompts, "99")
        run_with_input(main.toggle_favorite, prompts, "abc")
        self.assertFalse(any(p["favorite"] for p in prompts[:1]))

    def test_detail_increments_views(self):
        prompts = sample()
        run_with_input(main.show_detail, prompts, "1")
        self.assertEqual(prompts[0]["views"], 1)

    def test_edit_and_delete(self):
        prompts = sample()
        run_with_input(main.edit_prompt, prompts, "1", "바뀐 제목", "", "n")
        self.assertEqual(prompts[0]["title"], "바뀐 제목")
        self.assertEqual(prompts[0]["content"], "본문")
        run_with_input(main.delete_prompt, prompts, "1", "y")
        self.assertEqual(len(prompts), 2)

    def test_json_round_trip_and_broken_file(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "p.json")
            main.save_prompts(sample(), path)
            self.assertEqual(main.load_prompts(path), sample())
            self.assertIsNone(main.load_prompts(os.path.join(d, "none.json")))
            with open(path, "w") as f:
                f.write("{broken")
            with mock.patch("builtins.print"):
                self.assertIsNone(main.load_prompts(path))
            self.assertTrue(os.path.exists(path + ".bak"))

    def test_markdown_export_per_category(self):
        with tempfile.TemporaryDirectory() as d, mock.patch.object(main, "EXPORT_DIR", d):
            run_with_input(main.export_markdown, sample())
            self.assertEqual(sorted(os.listdir(d)), ["글쓰기.md", "코딩.md"])
            with open(os.path.join(d, "코딩.md"), encoding="utf-8") as f:
                text = f.read()
            self.assertIn("제목2", text)
            self.assertNotIn("Hello Title", text)


if __name__ == "__main__":
    unittest.main()
