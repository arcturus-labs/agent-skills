#!/usr/bin/env python3
"""Cached, resumable prerecorded AssemblyAI transcription. No fixed model default.
Supply --config JSON chosen from current docs (speech_models plus compatible options).
The ASSEMBLYAI_API_KEY environment variable is never written or printed.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import http.client
import json
import math
import os
from pathlib import Path
import time
from urllib import request, error
from _common import cli, fingerprint, load, output_safe, run, save
from transcript import read_words

API = "https://api.assemblyai.com/v2"


def validate_config(config):
    if not isinstance(config, dict):
        raise ValueError("Config must be a JSON object")
    models = config.get("speech_models")
    if not isinstance(models, list) or not models or any(not isinstance(m, str) or not m.strip() for m in models):
        raise ValueError("Choose a current prerecorded model: config needs a nonempty speech_models list")
    blocked = {"audio_url", "api_key", "authorization", "token", "speech_model"}
    if any(k.lower() in blocked for k in config):
        raise ValueError("Do not supply audio URLs, secrets, or deprecated speech_model in config")
    if "redact_pii_audio" in config and config["redact_pii_audio"]:
        raise ValueError("Helper is for transcription, not altering source speech")
    return config


def api_call(endpoint, key, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = request.Request(API + endpoint, data=data,
                          headers={"Authorization": key, "Content-Type": "application/json"})
    try:
        with request.urlopen(req, timeout=90) as response:
            return json.load(response)
    except error.HTTPError as exc:
        raise RuntimeError(f"AssemblyAI HTTP {exc.code}; inspect account/service status, not private payloads") from None
    except (error.URLError, TimeoutError, OSError):
        raise RuntimeError("AssemblyAI transport failed; preserve job state and reconcile before retrying submission") from None


def upload(path, key):
    connection = http.client.HTTPSConnection("api.assemblyai.com", timeout=300)
    try:
        connection.putrequest("POST", "/v2/upload")
        connection.putheader("Authorization", key)
        connection.putheader("Content-Type", "application/octet-stream")
        connection.putheader("Content-Length", str(path.stat().st_size))
        connection.endheaders()
        with path.open("rb") as stream:
            while chunk := stream.read(1024 * 1024):
                connection.send(chunk)
        response = connection.getresponse()
        if response.status != 200:
            raise RuntimeError(f"AssemblyAI upload HTTP {response.status}")
        value = json.loads(response.read())
        url = value["upload_url"]
        if not isinstance(url, str) or not url.startswith("https://"):
            raise ValueError("Provider returned an unexpected upload schema")
        return url
    except (OSError, http.client.HTTPException):
        raise RuntimeError("Audio upload failed; no job was intentionally submitted") from None
    finally:
        connection.close()


def normalized(job):
    result = []
    for word in job.get("words") or []:
        s, e = word["start"] / 1000, word["end"] / 1000
        if not isinstance(word["text"], str) or not all(math.isfinite(t) for t in (s, e)) or not 0 <= s <= e:
            raise ValueError("Unexpected provider word schema; ask before adapting the shared helper")
        item = {"word": word["text"], "start": s, "end": e}
        if word.get("speaker") is not None:
            item["speaker"] = word["speaker"]
        result.append(item)
    if not result:
        raise ValueError("Provider returned no word timings; inspect current model/API support")
    return {"words": sorted(result, key=lambda w: w["start"])}


def transcribe(source, output, config, timeout=7200, retry_ambiguous=False, docs_checked_on=None):
    source = Path(source).resolve(strict=True)
    config = validate_config(config)
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    paths = {n: output / n for n in ("transcript.json", "raw-response.json", "provenance.json", "audio.flac")}
    for p in paths.values():
        output_safe(p, [source], replace=True)
    signature = fingerprint(source)
    state_path, target = paths["provenance.json"], paths["transcript.json"]
    state = load(state_path) if state_path.exists() else {}
    if state and (state.get("schema_version") != 1 or state.get("source") != signature or state.get("request") != config):
        raise ValueError("Workspace source/config/schema differs; use a new workspace or approve a migration")
    if target.exists():
        if state.get("status") != "completed":
            raise ValueError("Existing transcript has incomplete/unknown provenance; verify rather than overwrite")
        read_words(target)
        return {"transcript": str(target), "reused": True}
    if paths["raw-response.json"].exists() and not state:
        raise ValueError("Unregistered response exists; inspect rather than overwrite")
    key = os.environ.get("ASSEMBLYAI_API_KEY")
    if not key:
        raise ValueError("ASSEMBLYAI_API_KEY is missing; configure it securely (see references/transcription.md)")
    if state.get("submission_pending") and not state.get("job_id") and not retry_ambiguous:
        raise ValueError("Prior submit outcome unknown: reconcile provider jobs before --retry-ambiguous-submit")
    t0 = time.monotonic()
    if not state:
        state = {"schema_version": 1, "source": signature, "request": config,
                 "docs_checked_on": docs_checked_on, "created_at": datetime.now(timezone.utc).isoformat()}
        save(state_path, state)
    if not state.get("job_id"):
        audio = paths["audio.flac"]
        if not state.get("audio_ready") or not audio.exists():
            partial = output / "audio.partial.flac"
            output_safe(partial, [source], replace=True)
            run(["ffmpeg", "-v", "error", "-y", "-i", str(source), "-vn", "-ac", "1", "-ar", "16000",
                 "-c:a", "flac", str(partial)], timeout=900)
            os.replace(partial, audio)
            state["audio_ready"] = True
            save(state_path, state)
        url = upload(audio, key)
        # Save before POST: an interrupted response must not silently create a second paid job.
        state["submission_pending"] = True
        save(state_path, state)
        job = api_call("/transcript", key, {**config, "audio_url": url})
        if not isinstance(job.get("id"), str) or not job["id"]:
            raise ValueError("Unexpected submission response; reconcile job before retry")
        state.update(job_id=job["id"], submission_pending=False)
        save(state_path, state)
    deadline = time.monotonic() + timeout
    while True:
        job = api_call("/transcript/" + state["job_id"], key)
        status = job.get("status")
        if status == "completed":
            break
        if status == "error":
            raise RuntimeError("Transcription service reports a job error; inspect securely, do not resubmit blindly")
        if status not in {"queued", "processing"}:
            raise ValueError("Unexpected provider status; ask before changing helper schema")
        if time.monotonic() >= deadline:
            raise RuntimeError("Transcription pending; rerun the same command to resume saved job")
        time.sleep(min(3, max(0, deadline - time.monotonic())))
    save(paths["raw-response.json"], job)
    words = normalized(job)
    # State first permits recovery if transcript write is interrupted.
    state.update(status="completed", word_count=len(words["words"]),
                 actual_model=job.get("speech_model_used") or job.get("speech_models"),
                 elapsed_seconds=round(time.monotonic() - t0, 2))
    save(state_path, state)
    save(target, words)
    return {"transcript": str(target), "words": len(words["words"]), "reused": False,
            "actual_model": state["actual_model"], "elapsed_seconds": state["elapsed_seconds"]}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source"); ap.add_argument("--output-dir", required=True)
    ap.add_argument("--config", required=True, help="Non-secret JSON selected from current provider docs")
    ap.add_argument("--timeout", type=float, default=7200, help="Polling budget in seconds; saved jobs resume")
    ap.add_argument("--docs-checked-on", help="Optional YYYY-MM-DD provenance")
    ap.add_argument("--retry-ambiguous-submit", action="store_true", help="Only after reconciling an unknown prior POST")
    args = ap.parse_args()
    if not math.isfinite(args.timeout) or args.timeout <= 0:
        raise ValueError("Polling timeout must be finite and positive")
    for name in ("transcript.json", "raw-response.json", "provenance.json", "audio.flac", "audio.partial.flac"):
        output_safe(Path(args.output_dir) / name, [args.source, args.config], replace=True)
    result = transcribe(args.source, args.output_dir, load(args.config), args.timeout,
                        args.retry_ambiguous_submit, args.docs_checked_on)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    cli(main)
