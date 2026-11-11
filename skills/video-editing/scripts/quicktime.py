#!/usr/bin/env python3
"""Open/identify an exact QuickTime file, cue seconds or H:MM:SS, pause by default.
Does not close other documents, edit media, or assume the front document is yours.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys
from _common import cli, seconds

SCRIPT = r'''
on run argv
    set desiredPath to item 1 of argv
    set desiredFile to (POSIX file desiredPath) as alias
    set seekTime to (item 2 of argv) as real
    set shouldPlay to (item 3 of argv) is "play"
    tell application "QuickTime Player"
        open desiredFile
        set foundDocument to false
        repeat 120 times
            repeat with candidate in documents
                try
                    if ((file of candidate) as alias) is desiredFile then
                        if (duration of candidate) > 0 then
                            set targetDocument to candidate
                            set foundDocument to true
                            exit repeat
                        end if
                    end if
                end try
            end repeat
            if foundDocument then exit repeat
            delay 0.25
        end repeat
        if not foundDocument then error "The requested QuickTime document did not load."
        if seekTime > (duration of targetDocument) then error "Seek time exceeds document duration."
        stop targetDocument
        set current time of targetDocument to seekTime
        activate
        set observedTime to current time of targetDocument
        set observedPath to POSIX path of (file of targetDocument)
        set observedDuration to duration of targetDocument
        if shouldPlay then play targetDocument
        return observedPath & linefeed & (observedTime as text) & linefeed & (observedDuration as text) & linefeed & ((playing of targetDocument) as text)
    end tell
end run
'''


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source"); ap.add_argument("--time", type=seconds, default=0)
    ap.add_argument("--play", action="store_true")
    args = ap.parse_args()
    if sys.platform != "darwin":
        raise ValueError("QuickTime helper is macOS-only; use your player's seek API or a short excerpt")
    source = Path(args.source).resolve(strict=True)
    result = subprocess.run(["osascript", "-", str(source), str(args.time), "play" if args.play else "pause"],
                            input=SCRIPT, text=True, capture_output=True, timeout=50)
    if result.returncode:
        raise RuntimeError("QuickTime did not verify the requested document/seek; inspect loading or macOS Automation permission")
    lines = result.stdout.strip().splitlines()
    if len(lines) != 4 or Path(lines[0]).resolve() != source:
        raise RuntimeError("Unexpected QuickTime readback; inspect before repeating the action")
    observed_time = float(lines[1].replace(",", "."))
    duration = float(lines[2].replace(",", "."))
    if abs(observed_time - args.time) > .2 or (lines[3] == "true") != args.play:
        raise RuntimeError("QuickTime readback differs from requested seek/play state; inspect before retrying")
    print(json.dumps({"path": lines[0], "current_seconds": observed_time, "duration_seconds": duration,
                      "playing": lines[3] == "true", "visual_window_confirmation": "not performed"}, indent=2))


if __name__ == "__main__":
    cli(main)
