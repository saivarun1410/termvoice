from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Protocol

from .dispatch import DispatchResult


class Recorder(Protocol):
    def record(self, destination: Path) -> Path: ...


class Transcriber(Protocol):
    def transcribe(self, audio_path: Path) -> str: ...


class Reviewer(Protocol):
    def review(self, transcript: str) -> str | None: ...


Dispatcher = Callable[[str, str], DispatchResult]


@dataclass(frozen=True)
class DictationOptions:
    target: str
    audio_path: Path | None = None
    keep_audio: bool = False
    skip_review: bool = False


@dataclass(frozen=True)
class WorkflowResult:
    status: str
    transcript: str = ""
    audio_path: Path | None = None
    dispatch: DispatchResult | None = None


def run_dictation(
    options: DictationOptions,
    recorder: Recorder,
    transcriber: Transcriber,
    reviewer: Reviewer,
    dispatcher: Dispatcher,
) -> WorkflowResult:
    created_audio = options.audio_path is None
    audio_path = options.audio_path

    if created_audio:
        file_descriptor, temporary_name = tempfile.mkstemp(prefix="termvoice-", suffix=".wav")
        os.close(file_descriptor)
        audio_path = Path(temporary_name)

    assert audio_path is not None
    try:
        if created_audio:
            recorder.record(audio_path)

        transcript = transcriber.transcribe(audio_path)
        reviewed = transcript if options.skip_review else reviewer.review(transcript)
        if reviewed is None:
            return WorkflowResult(status="cancelled", transcript=transcript)
        if not reviewed.strip():
            return WorkflowResult(status="cancelled", transcript=transcript)

        dispatch_result = dispatcher(reviewed.strip(), options.target)
        return WorkflowResult(
            status="dispatched",
            transcript=reviewed.strip(),
            audio_path=audio_path if options.keep_audio else None,
            dispatch=dispatch_result,
        )
    finally:
        if created_audio and not options.keep_audio:
            audio_path.unlink(missing_ok=True)
