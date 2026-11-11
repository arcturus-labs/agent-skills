from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from _common import probe
from media import excerpt, sheet, streams, verify


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "FFmpeg fixtures require ffmpeg/ffprobe")
class MediaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.source = Path(cls.tmp.name) / "fixture.mp4"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc2=s=160x90:r=25:d=2",
                        "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000:duration=2",
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(cls.source)], check=True)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_excerpt_and_verify(self):
        dest = Path(self.tmp.name) / "preview.mp4"
        result = excerpt(self.source, .24, 1.44, dest)
        self.assertAlmostEqual(result["duration"], 1.2, delta=.1)
        self.assertTrue(streams(probe(dest), "audio"))
        checks = verify(dest, 1.2)
        self.assertEqual(checks["decode"], "passed")
        self.assertTrue(checks["duration_within_tolerance"])
        self.assertFalse(verify(dest, 100)["duration_within_tolerance"])
        self.assertLess(abs(checks["stream_starts"]["video"]), .1)
        with self.assertRaises(ValueError):
            excerpt(self.source, 0, 1, dest)

    def test_no_source_overwrite_or_invalid_range(self):
        before = self.source.read_bytes()
        with self.assertRaises(ValueError):
            excerpt(self.source, 0, 1, self.source, replace=True)
        with self.assertRaises(ValueError):
            excerpt(self.source, 1, 3, Path(self.tmp.name) / "bad.mp4")
        self.assertEqual(before, self.source.read_bytes())

    def test_labeled_sheet(self):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("Optional Pillow not installed")
        out = Path(self.tmp.name) / "sheet.png"
        sheet(self.source, [0, .5, 1], out, columns=2, width=160)
        with Image.open(out) as image:
            self.assertEqual(image.size, (320, 232))
        with self.assertRaises(ValueError):
            sheet(self.source, [3], Path(self.tmp.name) / "bad.png")


if __name__ == "__main__":
    unittest.main()
