import tempfile
import unittest
from pathlib import Path

from termvoice.dispatch import DispatchResult
from termvoice.workflow import DictationOptions, run_dictation


class FakeRecorder:
    def __init__(self):
        self.path = None

    def record(self, destination):
        self.path = destination
        destination.write_bytes(b"fake wav")
        return destination


class FakeTranscriber:
    def transcribe(self, audio_path):
        assert audio_path.exists()
        return "run the focused tests"


class FakeReviewer:
    def __init__(self, result):
        self.result = result

    def review(self, transcript):
        return self.result


class WorkflowTests(unittest.TestCase):
    def test_records_reviews_dispatches_and_cleans_up(self):
        recorder = FakeRecorder()
        dispatched = []

        def dispatcher(prompt, target):
            dispatched.append((prompt, target))
            return DispatchResult(target)

        result = run_dictation(
            DictationOptions(target="codex"),
            recorder,
            FakeTranscriber(),
            FakeReviewer("run only the unit tests"),
            dispatcher,
        )

        self.assertEqual(result.status, "dispatched")
        self.assertEqual(dispatched, [("run only the unit tests", "codex")])
        self.assertIsNotNone(recorder.path)
        self.assertFalse(recorder.path.exists())

    def test_cancel_does_not_dispatch(self):
        recorder = FakeRecorder()

        def should_not_dispatch(_prompt, _target):
            self.fail("cancelled transcript was dispatched")

        result = run_dictation(
            DictationOptions(target="codex"),
            recorder,
            FakeTranscriber(),
            FakeReviewer(None),
            should_not_dispatch,
        )
        self.assertEqual(result.status, "cancelled")
        self.assertFalse(recorder.path.exists())

    def test_user_supplied_audio_is_never_deleted(self):
        with tempfile.TemporaryDirectory() as directory:
            audio = Path(directory) / "input.wav"
            audio.write_bytes(b"user audio")
            result = run_dictation(
                DictationOptions(target="stdout", audio_path=audio, skip_review=True),
                FakeRecorder(),
                FakeTranscriber(),
                FakeReviewer(None),
                lambda _prompt, target: DispatchResult(target),
            )
            self.assertEqual(result.status, "dispatched")
            self.assertTrue(audio.exists())


if __name__ == "__main__":
    unittest.main()
