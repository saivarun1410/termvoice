# TermVoice

[![PyPI version](https://img.shields.io/pypi/v/termvoice.svg)](https://pypi.org/project/termvoice/)
[![Python versions](https://img.shields.io/pypi/pyversions/termvoice.svg)](https://pypi.org/project/termvoice/)
[![CI](https://github.com/saivarun1410/termvoice/actions/workflows/ci.yml/badge.svg)](https://github.com/saivarun1410/termvoice/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

TermVoice turns speech into reviewed prompts for terminal AI agents. Recording
and transcription happen locally; the prompt only leaves your computer when you
approve it and dispatch it to an agent.

> Alpha software. TermVoice never evaluates a transcript as a shell command,
> but an approved prompt can still cause an AI agent to take actions allowed by
> that agent's permissions. Read the transcript before sending it.

## Why TermVoice

- Push-to-talk input without leaving the terminal
- Local transcription with `faster-whisper`
- Review or edit every prompt before it is sent
- Direct Codex launch, clipboard, and stdout targets
- Automatic deletion of temporary microphone recordings
- Multilingual auto-detection and configurable Whisper models
- No TermVoice account, server, telemetry, or API key

## How it works

```text
microphone -> temporary WAV -> local Whisper -> review/edit -> Codex
                                                    |------> clipboard
                                                    |------> stdout
```

The first use of a named model downloads its weights. After the model is cached,
speech recognition runs locally. If you dispatch to Codex or another hosted
agent, the approved **text prompt** is still sent according to that product's
privacy and data policies. TermVoice does not send the audio recording.

## Install

TermVoice is [available on PyPI](https://pypi.org/project/termvoice/) and requires
Python 3.9 or newer. On macOS, PortAudio is recommended:

```bash
brew install portaudio
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install termvoice
termvoice doctor
```

To install the latest development version from a clone, replace the package
installation command with `python -m pip install -e .`.

Linux users may need their distribution's PortAudio package before installing.
Windows users can normally install the Python dependencies directly.

The initial install includes `faster-whisper`, which downloads a selected model
on first use. The default `base` model balances speed and accuracy. Use a larger
model for accuracy or a smaller model for lower latency.

## Use

From a normal shell prompt:

```bash
termvoice
```

Speak, press Enter, review the transcript, and press Enter again to start Codex
with that prompt.

To dictate into a Codex session that is already open, copy the reviewed text and
paste it into the session:

```bash
termvoice --target clipboard
```

To print only the approved prompt:

```bash
termvoice --target stdout
```

To transcribe an existing recording:

```bash
termvoice --audio ./prompt.m4a --target stdout
```

Useful options:

```text
--model small          choose a model name or local model directory
--language en          skip automatic language detection
--device cpu|cuda      choose the inference device
--compute-type int8    trade precision for speed and memory
--editor "code --wait" choose the transcript editor
--input-device 2       choose a microphone by sounddevice index or name
--keep-audio           retain a newly recorded WAV file
--yes                  bypass review (not recommended)
```

Defaults can also be set with `TERMVOICE_TARGET`, `TERMVOICE_MODEL`,
`TERMVOICE_LANGUAGE`, `TERMVOICE_DEVICE`, `TERMVOICE_COMPUTE_TYPE`, and
`TERMVOICE_INPUT_DEVICE`.

## Privacy and safety

- New microphone recordings use a temporary WAV file and are deleted after
  transcription unless `--keep-audio` is supplied.
- Audio is processed by the local `faster-whisper` runtime. Model weights may be
  downloaded on first use.
- TermVoice has no network or telemetry code of its own.
- The review screen is enabled by default.
- Prompts are passed to Codex as a process argument, never through `shell=True`.
- `--target clipboard` copies text but does not submit it anywhere.

Avoid `--yes` when dispatching directly to an agent. Speech recognition can
mishear filenames, destructive verbs, numbers, and negations.

## Development

The core workflow is dependency-injected, so tests do not need a microphone,
model download, or Codex installation.

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
python -m compileall -q src tests
```

See [CONTRIBUTING.md](CONTRIBUTING.md) and [docs/architecture.md](docs/architecture.md).

## Releasing

Releases use PyPI Trusted Publishing and do not store a long-lived PyPI token in
GitHub. Publishing a GitHub release builds the source and wheel distributions,
then uploads them from the `publish.yml` workflow through the protected `pypi`
environment. Published versions are available from the
[TermVoice PyPI project](https://pypi.org/project/termvoice/) and the
[GitHub releases page](https://github.com/saivarun1410/termvoice/releases).

## Roadmap

- Streaming partial transcripts
- Apple Silicon MLX backend
- `whisper.cpp` backend
- Configurable developer vocabulary and repository context
- Terminal-emulator hotkey recipes
- Additional agent adapters
- Signed packages and release automation

## License

MIT. See [LICENSE](LICENSE).
