#!/usr/bin/env python3
"""Optional media mechanics: probe, one-range excerpt, labeled sheet, basic verify.
No automatic padding, speech cuts, camera selection, or universal editing schema.
"""
from __future__ import annotations
import argparse
import io
import json
import math
import os
from pathlib import Path
import re
import subprocess
import tempfile
from _common import cli, output_safe, probe, run, seconds, stamp


def streams(info, kind):
    return [s for s in info["streams"] if s["codec_type"] == kind]


def decode(path, timeout=1200):
    run(["ffmpeg", "-v", "error", "-xerror", "-i", str(path), "-map", "0:v:0", "-map", "0:a:0?", "-f", "null", "-"], timeout)


def excerpt(source, start, end, output, replace=False, timeout=120):
    source = Path(source).resolve(strict=True)
    dest = output_safe(output, [source], replace)
    info = probe(source)
    duration = float(info["format"]["duration"])
    if not streams(info, "video") or not 0 <= start < end <= duration:
        raise ValueError("Need a video and a range inside its duration")
    if dest.suffix.lower() != ".mp4":
        raise ValueError("Excerpt output must be an MP4")
    with tempfile.TemporaryDirectory(dir=dest.parent, prefix=".preview-") as work:
        part = Path(work) / "preview.mp4"
        run(["ffmpeg", "-v", "error", "-y", "-ss", str(start), "-i", str(source),
             "-t", str(end - start), "-map", "0:v:0", "-map", "0:a:0?",
             "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2,setsar=1,format=yuv420p",
             "-c:v", "libx264", "-preset", "fast", "-crf", "20",
             "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-movflags", "+faststart", str(part)], timeout)
        result = probe(part)
        if not streams(result, "video") or (streams(info, "audio") and not streams(result, "audio")):
            raise RuntimeError("Excerpt is missing expected streams")
        actual = float(result["format"]["duration"])
        if abs(actual - (end - start)) > .2:
            raise RuntimeError("Excerpt duration differs from requested range")
        decode(part, timeout)
        os.replace(part, dest)
    return {"output": str(dest), "duration": actual, "source_start": start, "source_end": end,
            "decode": "passed", "listened": False}


def sheet(source, times, output, columns=4, width=320, replace=False):
    try:
        from PIL import Image, ImageDraw, ImageOps
    except ImportError:
        raise ValueError("Contact sheets need optional Pillow; install visuals extra or use your own frame tool") from None
    dest = output_safe(output, [source], replace)
    duration = float(probe(source)["format"]["duration"])
    if not times or any(t < 0 or t >= duration for t in times) or columns < 1 or width < 32:
        raise ValueError("Need in-range frame times and positive sheet geometry")
    if dest.suffix.lower() != ".png":
        raise ValueError("Sheet output must be PNG")
    height = round(width * 9 / 16)
    cols = min(columns, len(times))
    canvas = Image.new("RGB", (cols * width, math.ceil(len(times) / cols) * (height + 26)), "#202020")
    draw = ImageDraw.Draw(canvas)
    for i, t in enumerate(times):
        png = run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", str(source), "-frames:v", "1",
                   "-vf", f"scale={width}:-1", "-f", "image2pipe", "-c:v", "png", "pipe:1"])
        frame = ImageOps.contain(Image.open(io.BytesIO(png)).convert("RGB"), (width, height))
        x, y = (i % cols) * width, (i // cols) * (height + 26)
        canvas.paste(frame, (x + (width - frame.width) // 2, y + (height - frame.height) // 2))
        draw.text((x + 5, y + height + 5), stamp(t), fill="white")
    with tempfile.TemporaryDirectory(dir=dest.parent, prefix=".sheet-") as work:
        tmp = Path(work) / "sheet.png"; canvas.save(tmp); os.replace(tmp, dest)
    return {"output": str(dest), "frames": len(times), "motion_review": False}


def verify(source, expected=None, tolerance=.15, timeout=1200):
    info = probe(source)
    vs, aus = streams(info, "video"), streams(info, "audio")
    if not vs:
        raise ValueError("Expected video stream")
    decode(source, timeout)
    actual = float(info["format"]["duration"])
    starts = {"video": float(vs[0].get("start_time", 0)),
              "audio": float(aus[0].get("start_time", 0)) if aus else None}
    filters = ["-vf", "blackdetect=d=0.01:pix_th=0.10"]
    if aus:
        filters += ["-af", "silencedetect=n=-50dB:d=0.02"]
    process = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", str(source), "-t", "2", *filters, "-f", "null", "-"],
        capture_output=True, text=True, timeout=timeout, check=True)
    evidence = [line.strip() for line in process.stderr.splitlines()
                if re.search(r"black_start:|silence_start:|silence_end:", line)]
    passed = expected is None or abs(actual - expected) <= tolerance
    return {"video": str(Path(source).resolve()), "decode": "passed", "duration": actual,
            "expected_duration": expected, "duration_within_tolerance": passed,
            "stream_starts": starts, "initial_two_second_detection": evidence,
            "note": "Inspect detections/start offsets against intent; no lip-sync, seam listening, or human review performed."}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="command", required=True)
    p = sub.add_parser("probe"); p.add_argument("source")
    p = sub.add_parser("excerpt"); p.add_argument("source")
    p.add_argument("--start", required=True, type=seconds); p.add_argument("--end", required=True, type=seconds)
    p.add_argument("--output", required=True); p.add_argument("--replace", action="store_true")
    p.add_argument("--timeout", type=float, default=120)
    p = sub.add_parser("sheet"); p.add_argument("source"); p.add_argument("--times", nargs="+", type=seconds, required=True)
    p.add_argument("--output", required=True); p.add_argument("--columns", type=int, default=4)
    p.add_argument("--width", type=int, default=320); p.add_argument("--replace", action="store_true")
    p = sub.add_parser("verify"); p.add_argument("source"); p.add_argument("--expected-duration", type=seconds)
    p.add_argument("--tolerance", type=float, default=.15); p.add_argument("--timeout", type=float, default=1200)
    a = ap.parse_args()
    if hasattr(a, "timeout") and (not math.isfinite(a.timeout) or a.timeout <= 0):
        raise ValueError("Timeout must be finite and positive")
    if a.command == "probe":
        result = probe(a.source)
    elif a.command == "excerpt":
        result = excerpt(a.source, a.start, a.end, a.output, a.replace, a.timeout)
    elif a.command == "sheet":
        result = sheet(a.source, a.times, a.output, a.columns, a.width, a.replace)
    else:
        if not math.isfinite(a.tolerance) or a.tolerance < 0:
            raise ValueError("Tolerance must be finite and nonnegative")
        result = verify(a.source, a.expected_duration, a.tolerance, a.timeout)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result.get("duration_within_tolerance") is False:
        raise SystemExit(1)


if __name__ == "__main__":
    cli(main)
