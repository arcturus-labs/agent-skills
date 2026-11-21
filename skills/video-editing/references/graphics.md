# Cards, overlays, and transitions

Discuss exact copy before rendering a new substantive message. Cards should
bridge ideas, not explain every cut. Prefer concise language grounded in the
footage. Keep approved punctuation and wording verbatim; global removals apply
to every occurrence. Revisit copy when the spoken sequence changes.

## Practical design

Pillow is sufficient for clean static PNGs; FFmpeg can composite and animate them.
Install Pillow in an isolated project environment only if needed. A custom project
script is usually simpler than a mandatory graphics schema/helper.

- Use supplied logo/reference assets and the user's brand preferences.
- Use explicit available font paths, with a documented fallback; do not assume
  macOS Georgia exists everywhere. Respect font licensing.
- Keep safe margins, readable type, and adequate contrast. Measure rendered text,
  not character count. Preserve paragraph breaks and distinguish paragraph spacing
  from line spacing. Long text should wrap or shrink deliberately.
- Logo cards: retain transparency correctly, center with room for the motto.
- Transparent overlays: small, legible, and away from the demonstrated work.
  A translucent backing may help. They must not obscure what the words refer to.
- Full cards: group related lines with visible separation between thoughts.

## Audio and picture are separate decisions

| Treatment | Audio | Picture |
|---|---|---|
| Opening bookend | Speech starts immediately if requested | Logo holds briefly, fades away to reveal speaker |
| Section bridge | Deliberate brief silence, then speech begins | Card holds for reading, fades away over speech |
| Small overlay | Speech continues naturally | Transparent text fades on/off over footage |
| Closing | Finish all intended words | Fade to message, hold, transition to logo/motto |

A dead-air beat is intentional, unlike accidental encoder delay or a black lead-in.
Choose card reading time based on copy, not a universal duration. Don't force the
viewer to read dense text while hearing unrelated important speech.

With FFmpeg, alpha-fade a looped RGBA PNG over normalized footage for a reveal;
`xfade` is useful for full-picture transitions. Explicitly bound image inputs,
output duration, and audio. Align frame rate/time base and reset PTS. Crossfades
overlap time: account for that in the output map. Don't fade the audio just because
the picture fades. Verify effects with short previews before a full render.

Static PNGs, exact copy, font choices, timings, and custom graphics scripts belong
in the project/build snapshot. No project-specific logo, motto, or personal font
path is baked into the shared skill.
