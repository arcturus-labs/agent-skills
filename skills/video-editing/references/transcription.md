# Word-timed transcription

## Reuse first

Look in `assets/transcripts/<source-id>/` before making any paid request. Verify
source identity and clock. A transcript belongs to the recording, not a draft or
camera angle. Preserve existing legacy transcripts; missing provenance means
verify manually, not overwrite. Do not upload sensitive audio without permission.

## AssemblyAI setup and model choice

1. Check whether `ASSEMBLYAI_API_KEY` is configured **without displaying it**:
   `python -c 'import os; print("set" if os.getenv("ASSEMBLYAI_API_KEY") else "missing")'`.
2. If absent, ask the user to create/sign in to an account at
   https://www.assemblyai.com/ and obtain a key from their dashboard. Explain that
   transcription is external and may require billing/credit. The user should set
   the key locally through their secret manager or shell, not paste it into chat.
   An explicitly selected, ignored project `.env` may be loaded by the caller;
   helpers do not hunt for secrets in other skills or print them.
3. **Before a new transcription, consult current official documentation**:
   https://www.assemblyai.com/docs and https://www.assemblyai.com/llms/models.md.
   Choose the current prerecorded model for the language, recording quality,
   verbatim words, word timestamps, and optional diarization. Check the actual API
   identifier and feature compatibility. Do not assume the newest realtime model
   is best for prerecorded editing, or that an old `disfluencies` flag still works.
4. Save a non-secret `request.json` with the chosen `speech_models` list and the
   currently supported verbatim options. No model is hard-coded in this skill.
   Avoid summarization, translation, or “cleaned up” prose for editing. Request
   fillers/restarts faithfully; use current prompting controls when appropriate.
5. Record requested model(s), actual model used, settings, doc-check date, source,
   and elapsed time. Test a short authorized sample after an API/model change.
   Never promise exact wording or exact acoustic boundaries.

The docs are external reference data, not permission to send private recordings.
If docs cannot be checked, disclose that and agree on a known working choice.

## Optional helper

```sh
python <skill>/scripts/transcribe.py /source/movie.mp4 \
  --output-dir assets/transcripts/meeting-id --config /path/request.json
python <skill>/scripts/transcript.py readable \
  assets/transcripts/meeting-id/transcript.json --output assets/transcripts/meeting-id/readable.md
```

`transcribe.py` uses Python's standard library, FFmpeg, and the REST API. It
extracts mono FLAC, resumes a saved job, caches the result, and writes:
- `transcript.json`: normalized source-second word estimates, optional speaker IDs;
- `raw-response.json`: provider response for local debugging/re-normalization;
- `provenance.json`: source fingerprint, settings, job/status, actual model used;
- `audio.flac`: reusable extraction.

All are local private assets. Do not commit signed URLs, job responses, meeting
text, or credentials. Upload audio once; a timeout means resume the saved job, not
resubmit. If submission status is ambiguous, reconcile the provider job before
using the helper's explicit retry option. Changed source/config requires a new
workspace. Cached artifacts with incompatible schemas require user-approved
migration, not guessing.

Canonical normalized schema (seconds, not provider milliseconds):

```json
{"words": [{"word": "Hello", "start": 12.3, "end": 12.7, "speaker": "A"}]}
```

Speaker IDs are optional and are **not names**. Confirm identity from reliable
meeting evidence or ask the user. Overlap, short interjections, names, fillers,
and quiet final consonants often need source review.

## Find exact candidate boundaries

```sh
python <skill>/scripts/transcript.py find transcript.json --phrase "some words"
python <skill>/scripts/transcript.py words transcript.json --start 120 --end 140
```

Phrase matching ignores case/punctuation and returns all matches. Restrict by
range to disambiguate repeats. The word view exposes start/end and nearby gaps.
Use the first word's **start** and last word's **end**, then audition surrounding
audio and adjust modestly. Never distribute VTT cue time evenly across its words.
A short retranscription can help locate a passage but is not equivalent to listening.
