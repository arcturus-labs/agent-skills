# Writing a project build script

The skill ships no universal renderer. Each project gets **one** small build script
that turns a *declarative plan* into a numbered draft. This page is the pattern that
worked, and the mistakes to avoid. Adapt it; don't copy it blindly. If the
shared helpers in [rendering.md](rendering.md) already do what you need, use them.

## The one rule: plan in, draft out

```text
drafts/004/plan.json  ──►  scripts/build.py --draft 004  ──►  drafts/004/
 (what to keep, cards,                                         video.mp4
  cut lists, intents)                                          edit.json (resolved timeline)
                                                               transcript-timed.json
                                                               review.json (chapters)
                                                               changes.md, cuts.json
```

- **One parameterized `build.py`.** Not `build_v2.py`, `build003.py`, … Those copy a
  plan into code and drift. A new draft is a new `plan.json`, same script.
- **The plan is the only hand-edited input.** `edit.json` is *derived output*: the
  resolved timeline with output times. Never read a derived file back as the plan:
  it breaks when it's hand-edited or truncated (a stray character once made a
  draft's `edit.json` unparseable and the next build couldn't read it). If you
  must derive draft N+1 from N, derive from N's `plan.json`.
- **Snapshots are immutable.** A new reviewed draft gets the next number; don't
  overwrite. Keep `plan.json` with the draft so you can reproduce or diff it.
- **Source of truth for words** is the normalized `transcript.json`. Never the raw
  provider response.

## Plan shape

Keep it boring and explicit. Source seconds, half-open `[start, end)`:

```json
{
  "output": {"width": 1280, "height": 720, "fps": 25},
  "sources": {"meeting": {"transcript": "assets/transcripts/meeting/transcript.json",
                           "layouts": {"speaker": "/path/speaker.mp4", "screen": "/path/screen.mp4"}}},
  "sequence": [
    {"card": "opening", "seconds": 4},
    {"source": "meeting", "layout": "speaker", "start": 527.8, "end": 1039.6, "intent": "Framing"},
    {"source": "meeting", "layout": "screen",  "start": 1086.4, "end": 1574.0, "intent": "Demo"},
    {"card": "closing", "seconds": 4}
  ],
  "cleanup": {"fillers": true, "silence": {"min_gap": 1.3, "keep_each_side": 0.22},
              "repeats": {"protect": ["very", "no", "right", "yeah"]}},
  "extra_cuts": [{"start": 1522.9, "end": 1523.2, "reason": "approved restart"}],
  "cards": {"opening": {"title": "…", "subtitle": "…"}},
  "chapters": [{"start": true, "title": "…"}, {"phrase": "words where it begins", "within": [690, 710], "title": "…"}]
}
```

The cut *lists* the build computes (fillers, pauses, repeats) are written out to
`drafts/NNN/cuts.json` with a reason each, for review and reproduction. User-approved
manual cuts go in `extra_cuts`.

## What the script does, in order

1. **Load** the plan and word transcript. Validate types, ordered ranges, and that
   every source file exists. Fail early with a clear message.
2. **Snap range bounds to words.** If a bound lands inside a word (ASR times are
   estimates), expand to that word's edge plus a small margin so you don't clip it.
   Round to the frame grid: start down, end up.
3. **Compute cuts** per [cleanup.md](cleanup.md) over the kept ranges, in one pass.
   Merge overlaps, snap to frames, and drop slivers (<~1 frame).
4. **Resolve the timeline.** Turn each range minus its cuts into pieces with
   `output_start/output_end`. Cap any one piece at ~60 s so render jobs are bounded.
5. **Render pieces** (below), then concatenate.
6. **Verify** (below), then promote the output atomically.
7. **Write derived outputs** (below).
8. **Print a summary:** duration, seconds saved vs. the base draft, cut counts.

Support `--dry-run` (steps 1–4, prints the timeline and runtime, renders nothing) and
`--draft NNN` (default: reject if the folder already contains a reviewed `video.mp4`
unless `--replace-scratch` style flags say otherwise).

## Rendering pieces

- **Batch by layout:** consecutive pieces from the same source go in one FFmpeg
  call (≈16 pieces or <~90 s span). Seek near the batch start with `-ss` *before*
  `-i`, then trim exactly with `trim`/`atrim` in a `filter_complex_script`.
- **Per piece:** `trim=start:end,setpts=PTS-STARTPTS,<normalize>` for video;
  `atrim=…,asetpts=PTS-STARTPTS,aresample=48000,afade in/out 4 ms` for audio.
  Normalize every piece to the output size, SAR 1, constant fps, `yuv420p`, 48 kHz
  stereo, so concat is safe. Never reset video and audio timestamps independently
  of each other without checking the original offset.
- **Intermediates:** H.264 video + **PCM** audio in `.mkv`. **One AAC encode** at
  the final mux. Repeated AAC encodes accumulate priming/padding at every seam.
- **Cards:** make the PNG with Pillow (explicit font path with a fallback), loop it
  for N seconds with `anullsrc` silent audio, same normalization as clips.
- **Cache** each rendered piece under `scratch/`, named by a hash of: source path
  and mtime, ranges, filter/encode settings, and any asset bytes. Re-renders
  then only do changed pieces. A changed logo, font, or filter must change the hash.
- **Bound everything:** pass a timeout to every FFmpeg call, bound looped image
  inputs and synthetic audio explicitly (`-t`), render to `*.partial.mkv`, check
  its duration (±~0.12 s vs expected), then rename. `tpad`/`apad` combinations can
  stall; test small first.
- **Long builds:** write the log to `scratch/`, run with a generous timeout, and
  poll it. A killed job leaves only `.partial` files, never a half-written final.

## Verify, then promote

- Concatenate with stream copy for video, AAC for audio, `-movflags +faststart`,
  into `video.partial.mp4`.
- Compare duration to the timeline total (±~0.2 s) and fully decode
  (`ffmpeg -xerror -i … -map 0:v -map 0:a -f null -`).
- Check the first frame isn't black and the first audio isn't silent unless a
  card is meant to open silently. Mismatched stream start offsets caused black/silent
  lead-ins before; reset to zero and re-check start times with `ffprobe`.
- Only then `rename` to `video.mp4`. On failure, leave the previous draft intact.
- Say honestly what ran: decode passed is not a listen-through. See
  [verification.md](verification.md).

## Mapping words and review links

The edited transcript is *derived* so links, chapters, and "what's in the video"
stay correct.

- Assign each source word to the piece containing its **midpoint**; clamp its
  start/end to the piece. Output time = `piece.output_start + (t − piece.start)`.
- **Keep the source word index** on every mapped word. Removed repeats and fillers
  are excluded by index; an excluded word must never be re-added by a later
  retranscription or overlapping range. Assert uniqueness and that nothing excluded
  appears.
- Write `transcript-timed.json` (`words`, `cards`, `duration`) and `review.json`
  (`version`, `title`, `video`, `transcript`, `chapters`) so the
  [local reviewer](reviewer.md) can browse it. **Chapters are written separately
  from editing notes**; see [Chapters](#chapters).
- **Re-map saved review spots by source word index**, never by an old output time.
  Every cut shifts later timestamps: "1:10 in draft 002" is meaningless in draft 003.
  To show the same passages again, keep a list of source word IDs, look up their new
  output times, and emit links that start ~3 s earlier.
- Also write `changes.md`: what was cut and why, runtime vs. the previous draft,
  counts for each cleanup type, what's unverified.

## Chapters

Chapters are the viewer's table of contents (and what YouTube shows on the timeline),
so they are **their own field**, never the editing `intent` notes. Notes such as
"retain full final sentence" or "stop before the cutoff" are for the editor, and card
names like `about` or `update` mean nothing out of context.

**Write them for someone who hasn't seen the video and doesn't know the subject:**
- Describe what the viewer will get, in plain words: "How the demo works: tools,
  schemas, and a browser plugin", not "Demo architecture". A name or term the
  audience can't know may appear only if the chapter explains it (e.g. "What is
  WebMCP?").
- Expressive is good; **cryptic is not.** A title must make sense read alone in a
  list of twenty. Never use a bare "About", "Update", "Intro", "Part 2", or an
  internal label.
- No editing cues, timestamps, source notes, speaker initials, or "(cut)" remarks.
- Sentence case, no trailing period, about 25–60 characters. Use a question when the
  chapter answers one ("What is this project?"). Keep parallel phrasing and
  avoid repeating the same lead words across chapters.
- Name the topic, not the speaker, unless the person is the point.
- A title card or silent bridge belongs to the chapter it introduces, not to a
  chapter of its own: start that chapter on the card.

**YouTube's rules:** the first chapter starts at `0:00`; at least three chapters;
timestamps ascend; each chapter lasts **at least 10 seconds** (merge shorter ones
into a neighbor). Use `M:SS`, or `H:MM:SS` once the video passes an hour.

**Anchor each chapter to the words, not a time.** Give a short exact phrase from the
transcript plus a source-seconds window that matches it once, or a card name. The
build maps that to the draft's output clock, starts about 0.4 s early but never
before the piece that contains the word, and re-derives it after every re-render.
Reject an anchor that matches zero or several times. Validate the rules above, then
write `chapters.txt` (ready to paste) and the `chapters` array in `review.json`.
After any recut, spot-check that each chapter's first words match its title.

## Sketch

```python
# scripts/build.py  — adapt; keep under ~300 lines
import argparse, json, hashlib, subprocess
from pathlib import Path
P = Path(__file__).resolve().parents[1]

def main():
    a = argparse.ArgumentParser(); a.add_argument("--draft", required=True)
    a.add_argument("--dry-run", action="store_true"); args = a.parse_args()
    D = P / "drafts" / args.draft
    plan = json.loads((D / "plan.json").read_text())
    words = load_words(plan)                      # normalized transcript.json
    ranges = snap_to_words(plan["sequence"], words)
    cuts = compute_cuts(ranges, words, plan["cleanup"]) + plan.get("extra_cuts", [])
    timeline = resolve(ranges, cuts)              # pieces with output_start/end
    report(timeline, cuts)
    if args.dry_run: return
    pieces = [render_piece(p) for p in batches(timeline)]   # cached, PCM
    video = concat_and_mux(pieces, D)             # one AAC encode, verified, atomic
    write_outputs(D, plan, timeline, cuts, words, video)    # edit/transcript/review/changes
main()
```

## Don't

- Don't copy the script per draft or bake the plan into code.
- Don't read a derived `edit.json` back in as the plan.
- Don't trust old output timestamps after any change.
- Don't re-encode audio more than once, or render without timeouts and partial files.
- Don't overwrite a reviewed draft, or open/deliver a partial file.
- Don't add behavior to the shared helpers for one project's quirk. Keep it in the
  project script, and ask the user before changing shared helpers (see
  [rendering.md](rendering.md)).
