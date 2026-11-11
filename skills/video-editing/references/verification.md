# Verification and delivery

Run only the checks appropriate to the draft, and report exactly which ran.
A decode pass is not a listen-through or editorial approval.

## Technical

```sh
python <skill>/scripts/media.py verify drafts/003/video.mp4 --expected-duration 95.2
```

This performs a full A/V decode, probes stream starts/duration, and reports
initial black/silence detection. It does not certify semantics, lip-sync, or
whether intentional silent/black content is appropriate. Inspect the JSON report.
The default duration tolerance is for small previews, not hundreds of sloppy seams.

For longer/multi-segment edits, also compare mapped source/output audio at the
beginning, middle, and end (cross-correlation or equivalent), and inspect actual
lip-sync. A common zero-point shift differs from relative A/V delay; don't erase
an intentional offset by blindly resetting each track independently.

## Picture and sound

- Inspect the first and last frames, not only frames a second into the clip.
- Check for accidental black, silence, frozen frames, gallery flashes, and
  one-frame gaps. Black/silence may be intentional; evaluate against the plan.
- Inspect a frame strip around transitions, camera landings, and jump cuts.
- Listen to every changed seam and phrase endpoint, especially quiet final
  consonants. Tiny padding may still clip “these”; metadata isn't acoustic proof.
- Check screen readability, framing, overlay placement, and privacy.
- Review the complete draft if audio/video audition is available. If not, give
  the user targeted review points rather than claiming it sounds smooth.

A fresh ASR pass is a localization aid, not proof that a human listened or that a
speaker's identity is verified. Contact sheets do not establish continuous motion.

## Delivery and final

Deliver the exact versioned MP4 link, runtime, key changes, and remaining issues.
Open the requested file/player when asked; verify the correct document and seek
position if possible. Avoid lengthy technical narrations during rapid review.
Record the latest artifact, decisions, and outstanding issues in `PROJECT.md`.

Only place/copy the designated approved output at the project root as `final.mp4`
after the user calls it final. Retain its draft/build provenance. Publishing is a
separate authorized task. Chapters/captions must use the final **output clock**,
not source times; revisions invalidate old chapter mappings.

Before pausing, leave a short handoff with source IDs, assets, draft, accepted and
rejected selections, pending changes, exact card text, QA evidence, and next step.
Do not automatically delete scratch or modify shared helpers during a debrief.
