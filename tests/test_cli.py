import os
import unittest
from unittest.mock import patch

from termvoice.cli import build_parser, normalize_argv, parse_input_device


class CliTests(unittest.TestCase):
    def test_empty_arguments_default_to_dictation(self):
        self.assertEqual(normalize_argv([]), ["dictate"])

    def test_options_without_subcommand_are_dictation_options(self):
        self.assertEqual(
            normalize_argv(["--target", "stdout"]),
            ["dictate", "--target", "stdout"],
        )

    def test_help_is_not_rewritten(self):
        self.assertEqual(normalize_argv(["--help"]), ["--help"])

    def test_environment_defaults_are_applied(self):
        with patch.dict(
            os.environ,
            {"TERMVOICE_TARGET": "clipboard", "TERMVOICE_MODEL": "small"},
            clear=False,
        ):
            args = build_parser().parse_args(["dictate"])
        self.assertEqual(args.target, "clipboard")
        self.assertEqual(args.model, "small")

    def test_input_device_accepts_index_or_name(self):
        self.assertEqual(parse_input_device("2"), 2)
        self.assertEqual(parse_input_device("MacBook Microphone"), "MacBook Microphone")
        self.assertIsNone(parse_input_device(None))


if __name__ == "__main__":
    unittest.main()
