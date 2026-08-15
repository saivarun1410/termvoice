import subprocess
import unittest

from termvoice.dispatch import clipboard_command, dispatch_prompt
from termvoice.errors import TermVoiceError


class DispatchTests(unittest.TestCase):
    def test_codex_uses_argument_vector_without_shell(self):
        calls = []

        def runner(command, **kwargs):
            calls.append((command, kwargs))
            return subprocess.CompletedProcess(command, 0)

        prompt = "review this; rm -rf definitely-not-a-command"
        result = dispatch_prompt(
            prompt,
            "codex",
            runner=runner,
            which=lambda name: "/usr/local/bin/codex" if name == "codex" else None,
        )

        self.assertEqual(result.returncode, 0)
        self.assertEqual(calls[0][0], ["/usr/local/bin/codex", prompt])
        self.assertNotIn("shell", calls[0][1])

    def test_macos_clipboard_command(self):
        command = clipboard_command(
            system="Darwin",
            which=lambda name: "/usr/bin/pbcopy" if name == "pbcopy" else None,
        )
        self.assertEqual(command, ["/usr/bin/pbcopy"])

    def test_missing_codex_is_actionable(self):
        with self.assertRaisesRegex(TermVoiceError, "Codex CLI was not found"):
            dispatch_prompt("hello", "codex", which=lambda _name: None)


if __name__ == "__main__":
    unittest.main()
