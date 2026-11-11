import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import transcribe as tc
from _common import fingerprint, load, save


class TranscriptionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.source = Path(self.tmp.name) / "source.wav"; self.source.write_bytes(b"test")
        self.out = Path(self.tmp.name) / "transcript"
        self.config = {"speech_models": ["user-selected-model"]}
        self.job = {"id": "job-test", "status": "completed", "speech_model_used": "user-selected-model",
                    "words": [{"text": "these", "start": 100, "end": 580, "speaker": "B"}]}

    def state(self, **kwargs):
        return {"schema_version": 1, "source": fingerprint(self.source), "request": self.config, **kwargs}

    def test_no_fixed_model_and_secret_rejection(self):
        for bad in ({}, {"speech_models": []}, {**self.config, "api_key": "not-a-key"},
                    {**self.config, "audio_url": "https://example.test"}):
            with self.assertRaises(ValueError):
                tc.validate_config(bad)
        self.assertEqual(tc.validate_config(self.config), self.config)

    def test_normalized_milliseconds_and_speaker(self):
        result = tc.normalized(self.job)
        self.assertEqual(result["words"][0], {"word": "these", "start": .1, "end": .58, "speaker": "B"})
        with self.assertRaises(ValueError):
            tc.normalized({"words": []})

    @patch.dict(os.environ, {"ASSEMBLYAI_API_KEY": "fake-for-offline-test"})
    def test_resume_never_uploads_or_submits_again(self):
        save(self.out / "provenance.json", self.state(job_id="job-test"))
        with patch.object(tc, "upload") as upload, patch.object(tc, "run") as run, patch.object(tc, "api_call", return_value=self.job) as api:
            result = tc.transcribe(self.source, self.out, self.config)
            upload.assert_not_called(); run.assert_not_called()
            self.assertEqual(api.call_args.args[0], "/transcript/job-test")
            self.assertFalse(result["reused"])
        with patch.object(tc, "api_call") as api:
            self.assertTrue(tc.transcribe(self.source, self.out, self.config)["reused"])
            api.assert_not_called()
        self.assertNotIn("fake-for-offline-test", (self.out / "provenance.json").read_text())

    @patch.dict(os.environ, {"ASSEMBLYAI_API_KEY": "fake-for-offline-test"})
    def test_unknown_submission_stops(self):
        save(self.out / "provenance.json", self.state(submission_pending=True))
        with patch.object(tc, "api_call") as api, self.assertRaisesRegex(ValueError, "reconcile"):
            tc.transcribe(self.source, self.out, self.config)
        api.assert_not_called()

    @patch.dict(os.environ, {"ASSEMBLYAI_API_KEY": "fake-for-offline-test"})
    def test_new_job_caches_and_sends_config(self):
        def fake_extract(*args, **kwargs):
            (self.out / "audio.partial.flac").write_bytes(b"fake-audio")
        with patch.object(tc, "run", side_effect=fake_extract), patch.object(tc, "upload", return_value="https://example.test/upload"), \
             patch.object(tc, "api_call", side_effect=[{"id": "job-test"}, self.job]) as api:
            tc.transcribe(self.source, self.out, self.config)
            payload = api.call_args_list[0].args[2]
            self.assertEqual(payload["speech_models"], self.config["speech_models"])
            self.assertTrue(load(self.out / "provenance.json")["audio_ready"])
            self.assertEqual(load(self.out / "transcript.json")["words"][0]["end"], .58)

    def test_changed_config_and_unregistered_cache_refused(self):
        save(self.out / "provenance.json", self.state(status="completed"))
        with self.assertRaisesRegex(ValueError, "differs"):
            tc.transcribe(self.source, self.out, {"speech_models": ["another-choice"]})
        (self.out / "provenance.json").unlink()
        save(self.out / "transcript.json", {"words": []})
        with self.assertRaisesRegex(ValueError, "provenance"):
            tc.transcribe(self.source, self.out, self.config)


if __name__ == "__main__":
    unittest.main()
