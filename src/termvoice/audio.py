from __future__ import annotations

import sys
import wave
from pathlib import Path
from typing import Any

from .errors import TermVoiceError


class SoundDeviceRecorder:
    """Record mono PCM audio until the user presses Enter."""

    def __init__(
        self,
        sample_rate: int = 16_000,
        channels: int = 1,
        device: int | str | None = None,
    ) -> None:
        self.sample_rate = sample_rate
        self.channels = channels
        self.device = device

    def record(self, destination: Path) -> Path:
        if not sys.stdin.isatty():
            raise TermVoiceError("Recording needs an interactive terminal. Use --audio for a file.")

        try:
            import numpy as np
            import sounddevice as sd
        except ImportError as exc:
            raise TermVoiceError(
                "Microphone dependencies are missing. Install TermVoice and run `termvoice doctor`."
            ) from exc

        chunks: list[Any] = []
        status_messages: list[str] = []

        def callback(indata: Any, frames: int, time: Any, status: Any) -> None:
            del frames, time
            if status:
                status_messages.append(str(status))
            chunks.append(indata.copy())

        print("Recording... press Enter to stop.", file=sys.stderr)
        try:
            with sd.InputStream(
                device=self.device,
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype="int16",
                callback=callback,
            ):
                input()
        except KeyboardInterrupt as exc:
            raise TermVoiceError("Recording cancelled.") from exc
        except Exception as exc:
            raise TermVoiceError(f"Could not record from the microphone: {exc}") from exc

        if not chunks:
            raise TermVoiceError(
                "No audio was captured. Check microphone permissions and input device."
            )

        audio = np.concatenate(chunks, axis=0)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with wave.open(str(destination), "wb") as output:
            output.setnchannels(self.channels)
            output.setsampwidth(2)
            output.setframerate(self.sample_rate)
            output.writeframes(audio.tobytes())

        if status_messages:
            print(f"Audio warning: {status_messages[-1]}", file=sys.stderr)
        return destination
