from __future__ import annotations

import os
import shlex
import subprocess
import sys
import tempfile
from collections.abc import Sequence
from pathlib import Path
from typing import Callable

from .errors import TermVoiceError


class PromptReviewer:
    """Require an explicit review before a transcript leaves TermVoice."""

    def __init__(
        self,
        editor: str | None = None,
        input_fn: Callable[[str], str] = input,
    ) -> None:
        self.editor = editor
        self.input_fn = input_fn

    def review(self, transcript: str) -> str | None:
        current = transcript
        while True:
            print("\n--- Transcript ---", file=sys.stderr)
            print(current, file=sys.stderr)
            print("------------------", file=sys.stderr)
            choice = self.input_fn("[Enter] continue  [e] edit  [q] cancel: ").strip().lower()
            if choice in {"", "s", "send", "continue"}:
                return current.strip()
            if choice in {"q", "quit", "cancel"}:
                return None
            if choice in {"e", "edit"}:
                current = self._edit(current)
                continue
            print("Choose Enter, e, or q.", file=sys.stderr)

    def _edit(self, text: str) -> str:
        editor = self.editor or os.environ.get("VISUAL") or os.environ.get("EDITOR")
        if not editor:
            raise TermVoiceError("Set $EDITOR or pass --editor to edit the transcript.")

        command: Sequence[str] = shlex.split(editor)
        if not command:
            raise TermVoiceError("The configured editor command is empty.")

        path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".txt", prefix="termvoice-edit-", delete=False, encoding="utf-8"
            ) as handle:
                handle.write(text)
                handle.write("\n")
                path = Path(handle.name)

            result = subprocess.run([*command, str(path)], check=False)
            if result.returncode != 0:
                raise TermVoiceError(f"Editor exited with status {result.returncode}.")
            return path.read_text(encoding="utf-8").strip()
        finally:
            if path is not None:
                path.unlink(missing_ok=True)
