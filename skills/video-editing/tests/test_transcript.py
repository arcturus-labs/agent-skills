import json
import math
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from _common import output_safe, seconds
from transcript import find, in_range, read_words, readable


class TranscriptTests(unittest.TestCase):
    def setUp(self):
        self.words = [
            {"word": "Hello,", "start": .1, "end": .5, "speaker": "A"},
            {"word": "WORLD!", "start": .6, "end": 1.2, "speaker": "A"},
            {"word": "these", "start": 1.4, "end": 1.9, "speaker": "B"}]

    def test_phrase_returns_last_word_end(self):
        self.assertEqual(find(self.words, "hello world"), [{"start": .1, "end": 1.2, "text": "Hello, WORLD!"}])
        self.assertEqual(find(self.words, "hello world", start=1.3), [])
        self.assertEqual(find(self.words, "these")[0]["end"], 1.9)

    def test_overlapping_window_and_negative_gaps(self):
        result = in_range(self.words, .4, 1.5)
        self.assertEqual(len(result), 3)
        self.assertAlmostEqual(result[1]["gap_before"], .1)
        self.assertEqual(in_range(self.words, 1.2, 1.4), [])

    def test_readable_speaker_turn(self):
        text = readable(self.words)
        self.assertEqual(len(text.splitlines()), 2)
        self.assertIn("speaker=B] these", text)

    def test_time_formats(self):
        self.assertEqual(seconds("1:48:36"), 6516)
        self.assertEqual(seconds("49:44.56"), 2984.56)
        for bad in ("-1", "nan", "inf", "1:62", "1:2:3:4"):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                seconds(bad)

    def test_source_and_output_safety(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source.json"
            source.write_text(json.dumps({"words": self.words}))
            self.assertEqual(read_words(source), self.words)
            alias = Path(tmp) / "alias.json"; alias.symlink_to(source)
            with self.assertRaises(ValueError):
                output_safe(alias, [source], replace=True)
            with self.assertRaises(ValueError):
                output_safe(source)
            source.write_text(json.dumps({"words": [{"word": "bad", "start": 2, "end": 1}]}))
            with self.assertRaises(ValueError):
                read_words(source)


if __name__ == "__main__":
    unittest.main()
