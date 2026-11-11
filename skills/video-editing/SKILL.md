---
name: video-editing
description: >-
  Use when researching recordings, auditioning quotes, collaboratively assembling
  speech, editing highlights or longer videos, choosing synchronized camera layouts,
  or creating branded cards, overlays, and transitions. Supports transcript-led
  selection, isolated video previews, numbered drafts, and source-preserving delivery.
---

# Video editing

Work with the user to turn recorded speech into a coherent viewing experience.
Prefer existing voices and fast, concrete previews over speculative narration or
an elaborate pipeline. This skill is standalone; resolve paths relative to here.

## Start or resume

1. Read the project's `PROJECT.md` and current edit description, if present.
2. Establish the intended audience, arc, output, and current request. Do not ask
   again when the conversation already supplies the answer.
3. Identify the **exact recording/date/instance**. “Previous meeting” is not
   necessarily the recording already open. Preserve original media.
4. Choose the mode below; read only its relevant references. Modes can overlap
   and repeat. No mandatory march through every phase.

| Mode | Read | Result |
|---|---|---|
| Discover / research | [Sources](references/sources.md), [transcription](references/transcription.md) | Complete transcript reading, topic map, candidates |
| Audition / select | [Collaboration](references/collaboration.md), [player](references/player.md) | Numbered candidates, source playback, selections |
| Transcript workshop | [Collaboration](references/collaboration.md), [speech](references/speech.md) | Proposed spoken sequence and annotations |
| Isolated stitch | [Speech](references/speech.md), [rendering](references/rendering.md) | Short **video** preview of an uncertain passage |
| Assemble / revise | [Rendering](references/rendering.md), [cameras](references/cameras.md) | Versioned reel, topical cut, or long-form video |
| Graphics / transitions | [Graphics](references/graphics.md) | Approved cards, overlays, audio/picture transitions |
| Cleanup / polish | [Speech](references/speech.md) | Selective filler, repetition, pause, and seam edits |
| Verify / deliver | [Verification](references/verification.md) | Checked output, honest QA report, approved final |

## Collaboration defaults

- **Understand → propose → audition → agree → preview → revise.** Honor explicit
  “don't build yet” boundaries. A request for a timestamp is not a request to render.
- For exploration, show numbered quotes with source times and why they help.
  Let the user choose. For a proposed new substantive quote, show it before inclusion.
- Distinguish actual recorded words, proposed omissions, and paraphrased copy.
  Preserve meaning, attribution, qualifications, and context across stitches.
- Keep editorial and mechanical cleanup separate. Usually establish a coherent
  rough cut before removing ums, uhs, and ordinary pauses; user preference wins.
- Prefer a short isolated **video** stitch before rebuilding a whole edit when a
  seam is uncertain. Use audio-only only when requested.
- Track selections, rejections, exact copy, pending changes, and approvals. Never
  interpret “good until X” ambiguously: record whether X itself is kept or excluded.
- Keep replies short during auditioning. Stop maintaining abandoned variants.
  Don't ask for ritual approval on every minor authorized adjustment.

## Project layout

```text
project/
├── PROJECT.md                # brief, decisions, latest draft, pending edits, QA
├── edit.json                 # current manifest, when useful; custom scripts OK
├── final.mp4                 # only after user designates an approved final
├── assets/
│   ├── sources.json          # original paths, source IDs, dates, clock offsets
│   ├── transcripts/<source-id>/
│   │   ├── transcript.json   # durable word timings; reuse before any paid request
│   │   ├── readable.md
│   │   └── provenance.json
│   └── branding/             # supplied logos, fonts where licensed, references
├── scratch/                  # flexible workbench: snippets, frames, caches, etc.
├── drafts/
│   ├── 001/                  # video.mp4, transcript.md, edit.json/build snapshot
│   └── 002/                  # alternatives can be video-A.mp4, video-B.mp4
└── scripts/                  # custom project helpers, builds, unusual effects
```

Original media may stay in its existing location. `assets/` is durable input;
`scratch/` is reproducible working material, **not automatically deleted**. Its
contents and subdirectories are intentionally unconstrained. Each draft number
is a reviewed/delivered snapshot, not every test render. Do not silently overwrite
reviewed drafts. Preserve the plan/build configuration used for each. The newest
draft is not automatically `final.mp4`.

## Timing and integrity rules

- Use real word start/**end** estimates, not interpolated caption cues. Check
  actual audio around delicate boundaries: ASR is not phoneme-perfect.
- One transcript per shared source clock; verify alignment before reusing across
  camera layouts. Different meetings have different clocks and IDs.
- Keep source and output times explicit. A cut-file timestamp must be mapped back
  to its source before editing. Recompute output mappings after each revision.
- Never manufacture an endorsement, response, or factual claim through splicing.
- Do not claim a listen-through from a transcript, decode, waveform, or contact sheet.
- No source overwrites, unsolicited cleanup/deletion, publishing, new narration,
  or account/security changes. External transcription needs appropriate permission;
  keep credentials and private media/transcripts out of version control.

## Optional tools, not a framework

Python 3.10+ and FFmpeg/ffprobe suffice for the included helpers; see
[scripts and rendering](references/rendering.md). Custom project scripts and
simpler native commands are welcome. There is deliberately no universal renderer.

If a helper is inadequate or a format/API has changed: **explain the situation,
ask the user, and recommend a durable rewrite when warranted. Get approval before
changing the shared skill/helper contract.** Do not repeatedly patch around the
same limitation, silently migrate saved files, or rewrite helpers just to fit one
project. A scoped project workaround can be proposed separately.

No helper grants editorial approval. No dependency on other skills, fixed model
IDs, particular provider SDKs, personal filesystem locations, or a local
capability-discovery service is required.
