# Contributing to TermVoice

Thank you for helping make voice input for terminal tools more accessible.

## Development setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
PYTHONPATH=src python -m unittest discover -s tests -v
```

Keep hardware and model imports lazy so unit tests can run without microphone
access or downloaded weights. New recorder, transcriber, reviewer, and dispatcher
implementations should remain separable from the workflow coordinator.

## Pull requests

- Add tests for changed behavior.
- Preserve review-before-dispatch as the default.
- Never execute transcript content through a shell.
- Document any network access, retained audio, telemetry, or cloud processing.
- Keep platform-specific behavior behind a small adapter.

By contributing, you agree that your contribution is licensed under the MIT
License included in this repository.
