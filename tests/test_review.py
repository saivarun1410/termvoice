import unittest
from unittest.mock import patch

from termvoice.review import PromptReviewer


class ReviewTests(unittest.TestCase):
    @patch("termvoice.review.print")
    def test_enter_approves_transcript(self, _print):
        reviewer = PromptReviewer(input_fn=lambda _prompt: "")
        self.assertEqual(reviewer.review("  fix the tests  "), "fix the tests")

    @patch("termvoice.review.print")
    def test_q_cancels(self, _print):
        reviewer = PromptReviewer(input_fn=lambda _prompt: "q")
        self.assertIsNone(reviewer.review("do something"))


if __name__ == "__main__":
    unittest.main()
