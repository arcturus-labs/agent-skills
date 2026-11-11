import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import quicktime


class PlayerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.source = Path(self.tmp.name).resolve() / "a source's name.mp4"
        self.source.write_bytes(b"not opened: mocked player")

    def invoke(self, readback):
        output = io.StringIO()
        with patch.object(sys, "platform", "darwin"), \
             patch.object(sys, "argv", ["quicktime.py", str(self.source), "--time", "12:30"]), \
             patch.object(quicktime.subprocess, "run", return_value=SimpleNamespace(returncode=0, stdout=readback)) as run, \
             contextlib.redirect_stdout(output):
            quicktime.main()
            self.assertEqual(run.call_args.args[0][2], str(self.source))
        return json.loads(output.getvalue())

    def test_explicit_path_time_and_default_pause(self):
        result = self.invoke(f"{self.source}\n750\n1000\nfalse\n")
        self.assertEqual(result["current_seconds"], 750)
        self.assertFalse(result["playing"])

    def test_readback_mismatch_fails(self):
        other = self.source.with_name("another.mp4")
        for path, t in [(str(self.source), "740"), (str(other), "750")]:
            with self.subTest(path=path, time=t), self.assertRaises(RuntimeError):
                self.invoke(f"{path}\n{t}\n1000\nfalse\n")


if __name__ == "__main__":
    unittest.main()
