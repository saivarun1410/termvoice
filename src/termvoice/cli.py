from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Sequence
from pathlib import Path

from . import __version__
from .audio import SoundDeviceRecorder
from .dispatch import dispatch_prompt
from .doctor import print_doctor
from .errors import TermVoiceError
from .review import PromptReviewer
from .transcribe import FasterWhisperTranscriber
from .workflow import DictationOptions, run_dictation


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="termvoice",
        description="Turn speech into reviewed prompts for terminal AI agents.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command")

    dictate = subparsers.add_parser("dictate", help="record or transcribe a prompt")
    dictate.add_argument("--audio", type=Path, help="transcribe an existing audio file")
    dictate.add_argument(
        "--target",
        choices=("codex", "clipboard", "stdout"),
        default=os.environ.get("TERMVOICE_TARGET", "codex"),
        help="where to send the reviewed prompt (default: codex)",
    )
    dictate.add_argument(
        "--model",
        default=os.environ.get("TERMVOICE_MODEL", "base"),
        help="faster-whisper model name or local model path (default: base)",
    )
    dictate.add_argument(
        "--language",
        default=os.environ.get("TERMVOICE_LANGUAGE", "auto"),
        help="language code or auto detection (default: auto)",
    )
    dictate.add_argument(
        "--device",
        choices=("auto", "cpu", "cuda"),
        default=os.environ.get("TERMVOICE_DEVICE", "auto"),
        help="inference device (default: auto)",
    )
    dictate.add_argument(
        "--compute-type",
        default=os.environ.get("TERMVOICE_COMPUTE_TYPE", "auto"),
        help="faster-whisper compute type (default: auto)",
    )
    dictate.add_argument("--editor", help="editor command used by the review screen")
    dictate.add_argument(
        "--input-device",
        default=os.environ.get("TERMVOICE_INPUT_DEVICE"),
        help="sounddevice input index or name (default: system input)",
    )
    dictate.add_argument(
        "--keep-audio",
        action="store_true",
        help="retain a newly recorded WAV file",
    )
    dictate.add_argument(
        "--yes",
        action="store_true",
        help="skip transcript confirmation (unsafe for unattended agent dispatch)",
    )
    subparsers.add_parser("doctor", help="check local dependencies and integrations")
    return parser


def normalize_argv(argv: Sequence[str]) -> list[str]:
    values = list(argv)
    if not values:
        return ["dictate"]
    if values[0] not in {"dictate", "doctor", "-h", "--help", "--version"}:
        return ["dictate", *values]
    return values


def parse_input_device(value: str | None) -> int | str | None:
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return value


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(normalize_argv(sys.argv[1:] if argv is None else argv))

    if args.command == "doctor":
        return print_doctor()
    if args.command != "dictate":
        parser.print_help()
        return 0

    transcriber = FasterWhisperTranscriber(
        model_name=args.model,
        language=args.language,
        device=args.device,
        compute_type=args.compute_type,
    )
    try:
        result = run_dictation(
            DictationOptions(
                target=args.target,
                audio_path=args.audio,
                keep_audio=args.keep_audio,
                skip_review=args.yes,
            ),
            recorder=SoundDeviceRecorder(device=parse_input_device(args.input_device)),
            transcriber=transcriber,
            reviewer=PromptReviewer(editor=args.editor),
            dispatcher=dispatch_prompt,
        )
    except TermVoiceError as exc:
        print(f"termvoice: {exc}", file=sys.stderr)
        return 1

    if result.status == "cancelled":
        print("Cancelled; nothing was sent.", file=sys.stderr)
        return 2
    if result.audio_path is not None:
        print(f"Audio kept at {result.audio_path}", file=sys.stderr)
    if result.dispatch is not None:
        return result.dispatch.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
