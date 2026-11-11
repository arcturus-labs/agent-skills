# Optional helpers and reproducible rendering

## Small toolkit

Core helpers use Python 3.10+ standard library plus FFmpeg/ffprobe. `quicktime.py`
is macOS-only; frame sheets optionally use Pillow. No SDK or particular service
model is required. Run `python <skill>/scripts/<name>.py --help` for options.
For optional sheets in an isolated environment:

```sh
uv run --project <skill> --extra visuals python <skill>/scripts/media.py sheet ...
```

Without `uv`, use a project virtualenv and install Pillow there. No global installs.

| Helper | Purpose |
|---|---|
| `transcribe.py` | Cached/resumable AssemblyAI job, caller-supplied current model config |
| `transcript.py` | Readable transcript, phrase search, word-range inspection |
| `media.py` | Probe, one-range video excerpt, labeled frame sheet, basic verification |
| `quicktime.py` | Explicit-file open/seek/readback; paused by default |

Helpers are conveniences, not required steps. For a custom stitch, branding, or
animated transition, write a project script. There is intentionally no universal
renderer or required editing schema.

If a helper expects an obsolete format or repeatedly fails a needed operation,
explain the incompatibility and ask the user whether to improve it. Recommend a
scoped durable rewrite and tests; **get approval before modifying shared helpers
or migrating their data contracts**. Don't silently change formats for old runs.

## Edit description

Use [the example manifest](../templates/edit-manifest.example.json) as a starting
point, not a renderer API. Keep source ID, layout, exact source range, camera/effect
decisions, card text, and pauses explicit. A custom script can be the executable
plan, but save its version/configuration for each delivered draft.

Half-open `[start,end)` keeps use source seconds. Output ranges account for frame
rounding, deliberate silence, speed changes, and transition overlaps. Generate a
source/output map and draft transcript from the **actual assembly**, not rounded
mental arithmetic. Identify source/layout in multi-meeting edits.

## Efficient implementation

- Seek near each range on input, then trim precisely. Avoid repeatedly decoding
  hours of discarded footage for tiny selections.
- Normalize dimensions, pixel format, sample aspect ratio, frame rate/time base,
  audio sample rate/channels for concat. Keep rational frame rates where relevant.
- Use matching video `trim` and audio `atrim`, resetting PTS consistently. Check
  original A/V offsets before independently resetting tracks: preserve relative
  alignment, fixing only known offsets.
- Prefer PCM audio intermediates and **one final AAC encode**, avoiding repeated
  AAC priming/padding. H.264 `yuv420p`, AAC, and `+faststart` are broadly playable.
  Ordinary lossy CRF settings are not “lossless.”
- Cache by source fingerprint + ranges + effects + assets + settings. Validate
  cached outputs and invalidate them when inputs change. Render active variants only.
- Bound subprocess timeouts and check exit codes **and** artifact integrity.
  FFmpeg can leave partial output after input errors; existence isn't success.
- Bound looped images/synthetic audio. Combinations of `tpad`, input `-t`, `apad`,
  and framesync can stall: prove a small case first.
- Render to temporary output, verify, then atomically promote. Never deliver a
  partial file or overwrite a reviewed draft or original (including via symlinks).

Measure representative render time rather than promising a universal estimate.
Wait for producing tool calls before reading their outputs.

## Quick commands

```sh
python <skill>/scripts/media.py excerpt assets/originals/source.mp4 \
  --start 12:30 --end 12:45 --output scratch/excerpt.mp4
python <skill>/scripts/media.py sheet scratch/excerpt.mp4 \
  --times 0 5 10 --output scratch/excerpt-sheet.png
python <skill>/scripts/media.py verify drafts/003/video.mp4 --expected-duration 92.4
```

Example paths/times are placeholders. `excerpt` re-encodes one range, without
adding padding, changing speech, or choosing a camera. It is not a stitch renderer
and does not grant editorial permission. Use `--replace` only for scratch outputs.

## Testing

```sh
python -m unittest discover -s <skill>/tests -v
```

Offline tests cover lookup, time parsing, safety, request validation, and resume
behavior. Synthetic FFmpeg fixtures exercise preview/sheet creation. Real provider
behavior and desktop automation require separate user-authorized validation.
No private recordings, credentials, transcripts, or generated artifacts are bundled.
