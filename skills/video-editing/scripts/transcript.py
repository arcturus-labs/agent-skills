#!/usr/bin/env python3
"""Inspect canonical {'words': [{'word', 'start', 'end', optional 'speaker'}]} JSON.
Times are source seconds. Find results use the LAST word's end, not its start.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import re
from _common import cli, load, output_safe, seconds, stamp


def read_words(path):
    data = load(path)
    words = data.get("words")
    if not isinstance(words, list) or not words:
        raise ValueError("Expected nonempty normalized words array; do not silently migrate schemas")
    previous = -1
    for w in words:
        s, e = w["start"], w["end"]
        if not isinstance(w["word"], str) or not all(isinstance(t, (int, float)) and math.isfinite(t) for t in (s, e)):
            raise ValueError("Invalid word text/time")
        if s < 0 or e < s or s < previous:
            raise ValueError("Expected ordered nonnegative word timing estimates")
        previous = s
    return words


def norm(text):
    return "".join(c for c in text.casefold() if c.isalnum())


def find(words, phrase, start=0, end=math.inf):
    tokens = [norm(t) for t in phrase.split() if norm(t)]
    if not tokens:
        raise ValueError("Phrase must contain words")
    values = [norm(w["word"]) for w in words]
    hits = []
    for i in range(len(words) - len(tokens) + 1):
        if values[i:i + len(tokens)] == tokens:
            chunk = words[i:i + len(tokens)]
            if chunk[-1]["end"] > start and chunk[0]["start"] < end:
                hits.append({"start": chunk[0]["start"], "end": chunk[-1]["end"],
                             "text": " ".join(w["word"] for w in chunk)})
    return hits


def in_range(words, start, end):
    selected = []
    previous = None
    for w in words:
        if w["end"] > start and w["start"] < end:
            selected.append({**w, "gap_before": None if previous is None else round(w["start"] - previous, 4)})
            previous = w["end"]
    return selected


def readable(words, interval=8):
    lines, bucket = [], []
    anchor, speaker = words[0]["start"], words[0].get("speaker")
    for w in words:
        if bucket and (w["start"] - anchor >= interval or w.get("speaker") != speaker):
            label = f" speaker={speaker}" if speaker is not None else ""
            lines.append(f"[{stamp(anchor)}{label}] " + " ".join(bucket))
            bucket = []
        if not bucket:
            anchor, speaker = w["start"], w.get("speaker")
        bucket.append(w["word"])
    label = f" speaker={speaker}" if speaker is not None else ""
    lines.append(f"[{stamp(anchor)}{label}] " + " ".join(bucket))
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="mode", required=True)
    p = sub.add_parser("find"); p.add_argument("transcript"); p.add_argument("--phrase", required=True)
    p.add_argument("--start", type=seconds, default=0); p.add_argument("--end", type=seconds, default=math.inf)
    p = sub.add_parser("words"); p.add_argument("transcript")
    p.add_argument("--start", type=seconds, required=True); p.add_argument("--end", type=seconds, required=True)
    p = sub.add_parser("readable"); p.add_argument("transcript"); p.add_argument("--output")
    p.add_argument("--interval", type=float, default=8); p.add_argument("--replace", action="store_true")
    a = ap.parse_args(); words = read_words(a.transcript)
    if a.mode == "readable":
        if not math.isfinite(a.interval) or a.interval <= 0:
            raise ValueError("Interval must be finite and positive")
        text = readable(words, a.interval)
        if a.output:
            output_safe(a.output, [a.transcript], a.replace).write_text(text)
        else:
            print(text, end="")
    else:
        if a.end <= a.start:
            raise ValueError("End must follow start")
        result = find(words, a.phrase, a.start, a.end) if a.mode == "find" else in_range(words, a.start, a.end)
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    cli(main)
