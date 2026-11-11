# Word-timed transcription

## Reuse first

Look in `assets/transcripts/<source-id>/` before making a paid request. Verify
source identity and clock. A transcript belongs to the recording, not a draft or
camera angle. Missing legacy provenance means verify manually, not overwrite.
External transcription requires appropriate permission, particularly for sensitive
or third-party speech.

## AssemblyAI setup and model choice

1. Check `ASSEMBLYAI_API_KEY` **without displaying its value**:
   `python -c 'import os; print("set" if os.getenv("ASSEMBLYAI_API_KEY") else "missing")'`.
2. If absent, ask the user to create/sign in at https://www.assemblyai.com/ and
   obtain a dashboard API key. Explain external processing and potential billing.
   The user should configure it locally through their secret manager or shell,
   not paste it into chat. An explicitly selected, ignored project `.env` can be
   loaded by the caller; helpers do not hunt for credentials or print them.
3. **Before new transcription, consult current official documentation**:
   https://www.assemblyai.com/docs and https://www.assemblyai.com/llms/models.md.
   Select the current prerecorded model for the language, quality, verbatim words,
   word timing, and optional diarization. Check API IDs and feature compatibility:
   realtime recommendations and old disfluency flags may not apply.
4. Save a non-secret `request.json` with the chosen `speech_models` list and
   currently supported verbatim options. **No model is hard-coded here.** Avoid
   summarization, translation, or cleaned-up prose. Request fillers/restarts
   faithfully, using current prompting controls when appropriate.
5. Record requested and actual models, configuration, doc-check date, source, and
   elapsed time. Test a short authorized sample after an API/model change. Never
   promise exact wording or acoustic boundaries.

Documentation is reference data, not permission to upload recordings. If current
docs are unavailable, disclose that and agree on a known working choice.

## Optional helper

```sh
python <skill>/scripts/transcribe.py assets/originals/movie.mp4 \
  --output-dir assets/transcripts/meeting-id --config request.json
python <skill>/scripts/transcript.py readable \
  assets/transcripts/meeting-id/transcript.json --output assets/transcripts/meeting-id/readable.md
```

Replace example paths with actual inputs. The REST helper extracts mono FLAC,
resumes a saved job, caches results, and writes private runtime assets:
- `transcript.json`: normalized word estimates in seconds, optional speaker IDs;
- `raw-response.json`: provider response for local inspection/re-normalization;
- `provenance.json`: source fingerprint, settings, job/status, actual model;
- `audio.flac`: reusable extraction.

Keep all runtime assets out of public version control. They can contain speech,
absolute source paths, job IDs, or signed URLs. Never commit real credentials.

A timeout means resume the saved job—not resubmit. If a POST result is ambiguous,
reconcile provider jobs before using `--retry-ambiguous-submit`. Changed source or
configuration requires a new workspace; incompatible caches require user-approved
migration rather than guessing. Provenance uses file path, size, and mtime: moving
an unchanged recording requires deliberate identity verification before reuse.

Canonical schema (seconds, not provider milliseconds):

```json
{"words": [{"word": "Hello", "start": 12.3, "end": 12.7, "speaker": "A"}]}
```

Speaker IDs are not names. Confirm identity from reliable meeting evidence or ask.
Overlapping speech, names, short interjections, fillers, and final consonants can
need manual review.

## Find boundaries

```sh
python <skill>/scripts/transcript.py find transcript.json --phrase "some words"
python <skill>/scripts/transcript.py words transcript.json --start 120 --end 140
```

Phrase matching ignores case/punctuation and returns every match; restrict the
range to disambiguate repeats. The word view includes start/end and nearby gaps.
Use the first word's **start** and last word's **end**, then audition and adjust.
Never distribute VTT cue duration evenly across words. Short retranscription may
help locate a passage but does not substitute for listening.
