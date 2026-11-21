# Optional helpers and reproducible rendering

## Small toolkit

Core helpers use Python 3.10+ standard library plus FFmpeg/ffprobe. Frame sheets
optionally use Pillow. No SDK, mandatory service model,
or graphics framework is required. Run `python <skill>/scripts/<name>.py --help`
for exact options. For optional sheets in an isolated environment:

```sh
uv run --project <skill> --extra visuals python <skill>/scripts/media.py sheet ...
```

Without `uv`, use a project virtualenv and install Pillow there. No global installs.

| Helper | Purpose |
|---|---|
| `transcribe.py` | Cached/resumable AssemblyAI job, caller-supplied current model config |
| `transcript.py` | Human-readable transcript, phrase search, word-range inspection |
| `media.py` | Probe, one-range video excerpt, labeled frame sheet, basic verification |

Helpers are conveniences, not required steps. For a custom stitch, branding, or
animated transition, write an appropriate project script. They intentionally don't
prescribe a universal edit format or implement every creative operation.

If a helper expects an obsolete format or repeatedly fails a needed operation,
explain the incompatibility and ask the user whether to improve it. Recommend a
scoped durable rewrite and tests; **get approval before modifying shared helpers
or migrating their data contracts**. Don't silently change formats for old runs.

## Edit description

To write the project's build script, follow [build-scripts.md](build-scripts.md):
one parameterized script reading a declarative plan, with derived `edit.json`
output. What follows is background on the timeline itself.

Use `templates/edit-manifest.example.json` as a starting point, not a required
renderer API. Keep source ID, layout, exact source range, camera/effect decisions,
card text, and pauses explicit. A custom script can be the executable plan, but
save the version/configuration for each delivered draft. Do not create v2/v3/v4
copies forever when one parameterized build plus snapshots will do.

Half-open `[start,end)` keeps use source seconds; output ranges account for frame
rounding, deliberate silence, speed changes, and transition overlaps. Generate a
source/output map and draft transcript from the **actual assembly**, not rounded
mental arithmetic. Mapping must identify source/layout for multi-meeting edits.

## Efficient implementation

- Seek near each range on input, then trim precisely. Avoid decoding hours of
  discarded footage separately for every 5-second selection.
- Normalize resolution, pixel format, sample aspect ratio, frame rate/time base,
  audio sample rate/channels for concat. Keep rational frame rates where relevant.
- Use matching video `trim` and audio `atrim`, reset PTS consistently. Check
  original audio/video offsets before independently resetting them: preserve real
  relative alignment, fixing only a known/common offset.
- Prefer PCM audio intermediates (e.g. MKV with H.264 + PCM) and **one final AAC
  encode** to avoid priming/padding at repeated AAC seams. H.264 `yuv420p`, AAC,
  and `+faststart` make broadly playable final MP4s. Set quality for the output;
  do not describe ordinary lossy CRF settings as “lossless.”
- Cache clips/cards by source fingerprint + ranges + effects + assets + settings.
  Validate cache outputs before reuse. A changed source, logo, font, or filter
  invalidates the relevant cache. Render only requested active variants.
- Use bounded subprocess timeouts and check exit codes **and** artifact integrity.
  FFmpeg can emit partial files after input errors; “file exists” isn't success.
- Bound looped images and synthetic audio explicitly. Some combinations of
  `tpad`, input `-t`, `apad`, and framesync can stall: prove a small case first.
- Render to a temporary/partial file, verify, then atomically promote it. Never
  open or deliver a partial render as if complete. Preserve the prior reviewed
  draft on failure. Do not overwrite originals (including through symlinks).

Do not assert universal render-time estimates. Measure a representative sample;
report actual time if useful. Serial tool calls cannot consume files from other
parallel calls before those producers finish.

## Quick commands

```sh
python <skill>/scripts/media.py excerpt /source.mp4 \
  --start 49:44.4 --end 50:00.5 --output scratch/ending.mp4
python <skill>/scripts/media.py sheet scratch/ending.mp4 \
  --times 0 5 10 15 --output scratch/ending-sheet.png
python <skill>/scripts/media.py verify drafts/003/video.mp4 --expected-duration 92.4
```

`excerpt` is a single-range convenience, not a stitch renderer. It does not add
padding, alter speech, choose a camera, or grant permission to render. Default
output dimensions/rate follow the selected video. It re-encodes for non-keyframe
boundaries. Use `--replace` only for disposable scratch outputs.

## Skill testing

```sh
python -m unittest discover -s <skill>/tests -v
```

Offline tests cover transcript lookup, time parsing, safety, request validation,
and resume behavior. FFmpeg fixture tests exercise actual preview and sheet
creation. Live provider behavior and model quality still need user-authorized
validation. No private media is bundled.
