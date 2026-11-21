# Speech, cleanup, and seams

## Select by thought, finish by sound

Use word timestamps to locate—not certify—cuts. Print context before/after the
range, especially when the user says something sounds clipped or stilted.
An orphaned “that people…” may need “so I hope that people…” restored. A montage
of individually useful sentences can still feel unnatural; replace the passage
rather than endlessly polishing an incoherent chain.

Use `[start,end)` intervals. Resolve the first word's start and the last word's
**end**. Add breathing room where available, bounded by neighboring speech and
source duration. Do not blindly apply the same padding to both sides of every cut:
it can duplicate speech, include an unwanted “yeah,” or create silent lead-ins.
Round keeps outward to frame boundaries when safe, keeping adjacent retained
ranges nonoverlapping. Never feed inclusive-frame ends into an exclusive renderer.

Inspect/listen to the *rendered* last word. “Conversation” and “these” were clipped
in the reference project despite plausible timestamps. Preserve final consonants;
place fades after speech, not across its last syllable. Tiny edge ramps may prevent
clicks, but larger fades can erase quiet speech. Normal breaths aren't defects.

## Internal removals

For removing “our current niche” or a redundant “literally”:
1. Find exact word starts/ends, inspect adjacent words and pauses.
2. Draft the resulting sentence verbatim; check meaning and grammar.
3. Render a local stitch, inspect rhythm and lip-sync, and compare source context.
4. Adjust the seam instead of assuming a fixed silence makes it natural.

Prefer natural room tone and breathing pauses. Added silence/frozen frames are
explicit editorial devices, not universal seam fixes. A short audio crossfade can
soften room-tone changes, but do not overlap distinct spoken syllables. Gallery,
screen footage, or another honest synchronized angle can cover a visible jump.
Do not use unrelated reaction shots to manufacture agreement or response.

## Cleanup

Removing ums/uhs, long silences, stutters/stumbles, and irrelevant content has its
own guidance in [cleanup.md](cleanup.md). This page covers the seams those cuts
produce: word boundaries, finishing the last word, internal removals, and
attribution.

## Attribution and testimony

Check who speaks and what their comment refers to. A participant describing a
*separate* group isn't necessarily endorsing this one. Removing that setup can
misrepresent them. Confirm names rather than inferring identity from an anonymous
ASR speaker label or appearance alone. Preserve quoted attribution, qualifications,
and later corrections even when they weaken a promotional hook.
