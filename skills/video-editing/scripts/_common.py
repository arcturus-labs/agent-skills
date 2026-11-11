"""Small local helpers. No provider SDK, model choice, or project layout required."""
from __future__ import annotations
import json
import math
import os
from pathlib import Path
import subprocess
import tempfile


def seconds(value):
    parts = str(value).split(":")
    if not 1 <= len(parts) <= 3:
        raise ValueError("Use seconds, M:SS, or H:MM:SS")
    numbers = [float(p) for p in parts]
    if any(not math.isfinite(n) or n < 0 for n in numbers):
        raise ValueError("Times must be finite and nonnegative")
    if len(numbers) > 1 and any(n >= 60 for n in numbers[1:]):
        raise ValueError("Minutes/seconds after ':' must be below 60")
    result = 0.0
    for n in numbers:
        result = result * 60 + n
    return result


def stamp(t):
    h, remainder = divmod(float(t), 3600)
    m, s = divmod(remainder, 60)
    return f"{int(h)}:{int(m):02}:{s:06.3f}" if h else f"{int(m)}:{s:06.3f}"


def load(path):
    return json.loads(Path(path).read_text())


def save(path, value):
    """Atomically write JSON, keeping private state owner-readable only."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=target.parent, prefix=".json-")
    try:
        with os.fdopen(fd, "w") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.replace(temporary, target)
    finally:
        Path(temporary).unlink(missing_ok=True)


def fingerprint(path):
    p = Path(path).resolve(strict=True)
    st = p.stat()
    return {"path": str(p), "size": st.st_size, "mtime_ns": st.st_mtime_ns}


def output_safe(output, sources=(), replace=False):
    dest = Path(output).resolve()
    for source in sources:
        p = Path(source).resolve()
        if dest == p or (dest.exists() and p.exists() and os.path.samefile(dest, p)):
            raise ValueError("Refusing to overwrite an input/source")
    if dest.exists() and not replace:
        raise ValueError("Output exists; use a new draft or explicit --replace for scratch")
    dest.parent.mkdir(parents=True, exist_ok=True)
    return dest


def run(args, timeout=120):
    result = subprocess.run(args, capture_output=True, timeout=timeout)
    if result.returncode:
        # Do not echo provider payloads, commands, private paths, or tokens.
        raise RuntimeError(f"{Path(args[0]).name} failed (exit {result.returncode}); inspect the input/format")
    return result.stdout


def probe(path):
    return json.loads(run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)]))


def cli(main):
    try:
        main()
    except (ValueError, RuntimeError, OSError, KeyError, subprocess.TimeoutExpired) as exc:
        # Most messages are intentionally bounded; do not print provider objects.
        raise SystemExit(str(exc)) from None
