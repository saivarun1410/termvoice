# Architecture

TermVoice keeps the device-facing pieces behind small adapters and coordinates
them in a testable workflow.

```text
SoundDeviceRecorder
        |
        v
FasterWhisperTranscriber
        |
        v
PromptReviewer ---- cancel
        |
        v
dispatch_prompt ---- Codex | clipboard | stdout
```

`workflow.run_dictation` owns temporary-file lifecycle and orchestration. It
depends on protocols rather than concrete implementations, allowing tests and
future backends to replace any stage independently.

## Boundaries

- `audio.py`: microphone capture and WAV encoding only.
- `transcribe.py`: local speech-to-text only.
- `review.py`: terminal confirmation and editor integration.
- `dispatch.py`: explicit outbound integrations without shell evaluation.
- `workflow.py`: cleanup and state transitions.
- `cli.py`: arguments, environment defaults, and user-facing error handling.

## Adding an agent adapter

Add a target to `dispatch_prompt` and pass the reviewed prompt using an argument
vector or standard input. Do not concatenate a transcript into a command string.
The target should return its process exit status and leave permission decisions
to the agent.

## Adding a transcription backend

Implement `transcribe(audio_path: Path) -> str`, import optional dependencies
inside the method, and document whether model files or audio ever cross the
network. Backends must reject empty transcripts.
