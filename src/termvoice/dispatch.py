from __future__ import annotations

import platform
import shutil
import subprocess
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Callable

from .errors import TermVoiceError

Runner = Callable[..., subprocess.CompletedProcess]


@dataclass(frozen=True)
class DispatchResult:
    target: str
    returncode: int = 0


def clipboard_command(
    system: str | None = None,
    which: Callable[[str], str | None] = shutil.which,
) -> list[str]:
    current = system or platform.system()
    candidates: Sequence[Sequence[str]]
    if current == "Darwin":
        candidates = (("pbcopy",),)
    elif current == "Windows":
        candidates = (("clip",),)
    else:
        candidates = (
            ("wl-copy",),
            ("xclip", "-selection", "clipboard"),
            ("xsel", "--clipboard", "--input"),
        )

    for candidate in candidates:
        resolved = which(candidate[0])
        if resolved:
            return [resolved, *candidate[1:]]
    raise TermVoiceError("No clipboard utility found for this platform.")


def dispatch_prompt(
    prompt: str,
    target: str,
    *,
    runner: Runner = subprocess.run,
    which: Callable[[str], str | None] = shutil.which,
) -> DispatchResult:
    if target == "stdout":
        print(prompt)
        return DispatchResult(target=target)

    if target == "clipboard":
        command = clipboard_command(which=which)
        result = runner(command, input=prompt, text=True, check=False)
        if result.returncode != 0:
            raise TermVoiceError(f"Clipboard command exited with status {result.returncode}.")
        print("Transcript copied to the clipboard.", file=sys.stderr)
        return DispatchResult(target=target)

    if target == "codex":
        executable = which("codex")
        if not executable:
            raise TermVoiceError("Codex CLI was not found. Install it or use --target clipboard.")
        # An argument vector is intentional: the reviewed prompt is never evaluated by a shell.
        result = runner([executable, prompt], check=False)
        return DispatchResult(target=target, returncode=result.returncode)

    raise TermVoiceError(f"Unsupported target: {target}")
