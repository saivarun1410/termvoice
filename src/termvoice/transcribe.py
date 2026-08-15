from __future__ import annotations

from pathlib import Path

from .errors import TermVoiceError


class FasterWhisperTranscriber:
    """Transcribe audio locally with faster-whisper."""

    def __init__(
        self,
        model_name: str = "base",
        language: str = "auto",
        device: str = "auto",
        compute_type: str = "auto",
    ) -> None:
        self.model_name = model_name
        self.language = language
        self.device = device
        self.compute_type = compute_type

    def transcribe(self, audio_path: Path) -> str:
        try:
            from faster_whisper import WhisperModel
        except ImportError as exc:
            raise TermVoiceError(
                "faster-whisper is missing. Install TermVoice and run `termvoice doctor`."
            ) from exc

        if not audio_path.is_file():
            raise TermVoiceError(f"Audio file does not exist: {audio_path}")

        print(f"Transcribing locally with model '{self.model_name}'...", flush=True)
        try:
            model = WhisperModel(
                self.model_name,
                device=self.device,
                compute_type=self.compute_type,
            )
            segments, _info = model.transcribe(
                str(audio_path),
                language=None if self.language == "auto" else self.language,
                vad_filter=True,
            )
            transcript = " ".join(segment.text.strip() for segment in segments).strip()
        except Exception as exc:
            raise TermVoiceError(f"Local transcription failed: {exc}") from exc

        if not transcript:
            raise TermVoiceError("No speech was detected.")
        return transcript
