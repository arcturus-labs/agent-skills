# Speech, cleanup, and seams

## Select by thought, finish by sound

Use word timestamps to locate—not certify—cuts. Print context before/after the
range, especially when the user says something sounds clipped or stilted.
An orphaned sentence fragment may need its preceding setup restored. A montage
of individually useful sentences can still feel unnatural; replace the passage
rather than endlessly polishing an incoherent chain.

Use `[start,end)` intervals. Resolve the first word's start and the last word's
**end**. Add breathing room where available, bounded by neighboring speech and
source duration. Do not blindly apply the same padding to both sides of every cut:
it can duplicate speech, include an unwanted interjection, or create silent lead-ins.
Round keeps outward to frame boundaries when safe, keeping adjacent retained
ranges nonoverlapping. Never feed inclusive-frame ends into an exclusive renderer.

Inspect/listen to the *rendered* last word. Plausible ASR timestamps can still
truncate syllables or quiet final consonants. Place fades after speech, not
across its last syllable. Tiny edge ramps may prevent clicks, but larger fades
can erase quiet speech. Normal breaths aren't defects.

## Internal removals

For removing a parenthetical aside or a redundant word:
1. Find exact word starts/ends, inspect adjacent words and pauses.
2. Draft the resulting sentence verbatim; check meaning and grammar.
3. Render a local stitch, inspect rhythm and lip-sync, and compare source context.
4. Adjust the seam instead of assuming a fixed silence makes it natural.

Prefer natural room tone and breathing pauses. Added silence/frozen frames are
explicit editorial devices, not universal seam fixes. A short audio crossfade can
soften room-tone changes, but do not overlap distinct spoken syllables. Gallery,
screen footage, or another honest synchronized angle can cover a visible jump.
Do not use unrelated reaction shots to manufacture agreement or response.

## Optional mechanical cleanup

Apply when requested or after the editorial draft works. Conservatively remove
standalone ums/uhs, immediate accidental repeats, false starts, and excessive
silence. Keep uncertainty, meaningful affirmations, rhetorical repetition, and
normal speech rhythm. “Like,” “sort of,” and “kind of” are not automatically waste.

Word gaps can suggest silence; validate acoustically. Quiet speech, screen reading,
waiting for a demo, or a meaningful reaction can be useful. Thresholds are tunable,
not hard requirements. Protect overlapping speech and implausible ASR durations.
Retain a drop list and original source mapping; avoid destructively editing a
render without being able to map the decision back to source.

## Attribution and testimony

Check who speaks and what their comment refers to. A participant describing a
*separate* group isn't necessarily endorsing this one. Removing that setup can
misrepresent them. Confirm names rather than inferring identity from an anonymous
ASR speaker label or appearance alone. Preserve quoted attribution, qualifications,
and later corrections even when they weaken a promotional hook.
