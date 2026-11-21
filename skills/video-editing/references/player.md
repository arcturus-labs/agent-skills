# Auditioning source and drafts

Review the **original** for context, a short isolated stitch for seams, and the
latest draft for the full arc. Always identify which clock/file is being shown.

- **A numbered quote in the original recording:** give the user a clickable link
  in the [local reviewer](reviewer.md), starting 0.5–3 seconds before the passage.
  Point a `review.json` at the original and launch with `--media-root` (see
  "Original/external media" there). The reviewer's `t` is on that video's own clock.
- **A short passage or a seam:** make a short clip with `media.py excerpt` (see
  [rendering](rendering.md)) so the user doesn't scrub hours of footage.
- **A draft:** use the reviewer with `?t=` links on the **draft's** clock, not the
  source's. Never reuse an older draft's timestamps.

If the filename is reused across meetings, verify the full path, not just the name.
Correct the source selection before giving a time. If the user questions a
timestamp, check the actual source/clock and quote before retrying; don't guess.
