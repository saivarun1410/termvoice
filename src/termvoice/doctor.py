from __future__ import annotations

import importlib.util
import platform
import shutil
import sys
from dataclasses import dataclass

from .dispatch import clipboard_command
from .errors import TermVoiceError


@dataclass(frozen=True)
class Check:
    name: str
    ok: bool
    detail: str
    required: bool = True


def collect_checks() -> list[Check]:
    checks = [
        Check("Python", sys.version_info >= (3, 9), platform.python_version()),
    ]
    for module in ("numpy", "sounddevice", "faster_whisper"):
        available = importlib.util.find_spec(module) is not None
        checks.append(Check(module, available, "installed" if available else "missing"))

    if importlib.util.find_spec("sounddevice") is not None:
        try:
            import sounddevice as sd

            input_device = sd.query_devices(kind="input")
            checks.append(Check("Microphone", True, str(input_device.get("name", "default input"))))
        except Exception as exc:
            checks.append(Check("Microphone", False, f"no default input available ({exc})"))

    codex: str | None = shutil.which("codex")
    checks.append(Check("Codex CLI", codex is not None, codex or "not found", required=False))
    try:
        clipboard = " ".join(clipboard_command())
        checks.append(Check("Clipboard", True, clipboard, required=False))
    except TermVoiceError as exc:
        checks.append(Check("Clipboard", False, str(exc), required=False))
    return checks


def print_doctor() -> int:
    checks = collect_checks()
    for check in checks:
        marker = "OK" if check.ok else ("FAIL" if check.required else "WARN")
        print(f"[{marker:4}] {check.name}: {check.detail}")
    return 0 if all(check.ok or not check.required for check in checks) else 1
