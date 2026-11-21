# Cleanup

Four kinds of cleanup, each its own section: **[fillers](#1-fillers-ums-and-uhs)**,
**[silences](#2-silences)**, **[stutters and stumbles](#3-stutters-and-stumbles)**,
and **[irrelevant content](#4-irrelevant-content)**. They differ in risk and in who
decides, so don't merge them into one pass.

All numbers below are starting points that worked on a ~3-hour, multi-speaker
meeting transcribed with word timings. Tune them per recording, and report the
values you used. Cuts are **proposals in source seconds** (see
[speech.md](speech.md) for seams), applied by the project build
([build-scripts.md](build-scripts.md)).

## Order of work

1. **Irrelevant content** first. It's the biggest win and the most subjective, and
   it changes what the other passes even see.
2. **Stutters and stumbles**, then **fillers**, then **silences**, computed **together
   in one pass** over the kept ranges. Removing a filler or a repeat can create a
   new long gap, so don't trim silences before the words around them are final.
3. **Listen to the seams.** Plausible timestamps still clip words. See
   [verification.md](verification.md).

Usually do the rough, structural cut with the user *before* mechanical cleanup, and
say plainly what each pass removed (counts, total seconds).

## 1. Fillers: ums and uhs

Remove **standalone** `um`, `uh`, `umm`, `uhh`, `erm` tokens. Keep `like`, `you
know`, `kind of`, `sort of`, "I mean" unless the user asks: they carry meaning or
voice.

- **Detect** from the word transcript (verbatim transcription is required; a
  cleaned-up transcript has already deleted them). Normalize punctuation/case first:
  `Uh,` and `uh` are the same token.
- **Plausible duration only:** about 65 ms to 750 ms. ASR reports some fillers as
  16–50 ms, often shorter than one video frame (40 ms at 25 fps). Cutting those
  guesses at the wrong audio and tends to clip the neighbouring word. **Don't
  auto-cut them**; list them as "retained, needs listening" and tell the user.
- **Pad slightly, never into neighbours:** cut from ~15 ms before the token to ~15 ms
  after, but stay at least ~40 ms away from the previous word's end and the next
  word's start. Skip the cut if less than ~50 ms would be removed.
- **Join cleanly:** a filler between two words usually leaves a natural-sounding
  join; one at the edge of a sentence may leave a mid-breath start. Check by ear.
- **Report:** how many were removed, how many were skipped as untrustworthy.

## 2. Silences

Shorten **long** gaps; leave ordinary conversational pauses alone. A speaker who
loses all their pauses sounds like an auto-tuned montage.

- **Threshold:** word gaps of about 1.3 s or more are candidates. Keep roughly
  **0.2 s on each side** (e.g. 0.22 s) so breaths and sentence endings survive.
- **Confirm with audio when it matters:** ASR gaps can hide real speech, and quiet
  speech isn't silence. Use an acoustic check (e.g. FFmpeg `silencedetect` around
  −42 dB, ≥1.5 s) and protect any word midpoint that falls inside a proposed cut.
- **Silence that is content:** don't shorten waiting that the viewer needs: a demo
  loading, someone reading the screen, a meaningful reaction, a deliberate beat
  before or after a title card. A dead-silent pause on a card is an editorial
  device, not waste; keep it exactly as designed.
- **Across speakers:** gaps between different speakers are turn-taking. Trim less.
- **Combine with filler/stumble cuts** (see Order of work) so a removed word
  doesn't leave a double gap.
- **Report:** number of trims and total seconds saved.

## 3. Stutters and stumbles

A **stutter repeat** is an accidental repeated word or phrase: *"the, the, the The
people"*, *"bring, bring their customers"*, *"I use, I use essentially"*. A
**stumble** or false start is an abandoned attempt that gets restarted:
*"The This is normal ChatGPT"*, *"What is— what is— what are some of the…"*.

- **Keep the last occurrence.** The final repetition is the one the speaker
  committed to, with the best intonation going into the next word. Remove the
  earlier ones.
- **Protect deliberate emphasis and affirmation:** "very, very, very responsive",
  "no, no, we're not doing that", "right, right", yeah/yes/really. Start with a short
  protected-word list and let the user extend it. Emphatic repetition across a
  list ("their own memory, their own tools") is parallel structure, not a stutter.
- **Auto-detect the literal cases:** adjacent identical word or short phrase
  (1–3 words), same speaker, gap between repeats short (≈1.25 s or less). Repeat the
  pass until nothing changes, so a chain like "my, my, my, my general" collapses.
- **Read the transcript yourself** as well. Scripts find literal duplicates;
  they miss restarts ("it can be— I'm one of the environments…"), changed wordings,
  and trailing fragments ("and I should, any, anything like that should be—"). Read
  the entire readable transcript, list candidates with draft timestamps, and have
  the user approve anything beyond literal duplicates. Restarts need a *phrasing*
  decision; they aren't blind deletions.
- **Make the cut at the kept word's start.** The earlier repeat ends where the
  kept word begins. Snap to the video frame grid, and don't split a word.
- **Keep the removal list.** For each: removed text, kept text, source times, and
  reason (`keep last repeated word`). Rebuilding must be able to reproduce it.
- **Update the transcript.** Retained words map to the new timeline by source word
  index; removed words are *excluded by index*, so a repeated word can't reappear
  in the edited transcript, chapters, or links. See
  [build-scripts.md](build-scripts.md#mapping-words-and-review-links).
- Retained fragments such as "the calorie," are probably fine; "I, I think"
  becoming "I think" needs a listen to confirm the sentence still sounds natural.

## 4. Irrelevant content

Cutting whole passages that add nothing is the most subjective cleanup and the
largest time saver. **The user decides.** Present a numbered list and wait for
approval before removing substantive content, unless they've said to just do it.

**Candidates** (each only if it doesn't add argument, color, or humor):
- Housekeeping and logistics: waiting for people, who's muted, "can you hear me",
  "let me move this window".
- Setup chatter and waiting: screen-sharing setup, agent/tool delays, switching
  tabs, "let me think about that".
- Prompts to the audience that go unanswered, and the speaker's side commentary
  to an audience that doesn't respond.
- Repeated framing: the same point made twice; the second version is usually
  the weaker one.
- Tangents that leave the topic and don't return, and long anecdotes whose point
  is already made.
- Trailing fragments and abandoned thoughts at the end of a speech.
- Content that belongs to a different story (e.g. a participant describing a
  *different* group is not a testimonial for this one).

**Protect:** the central argument, working demos, a strong example, a joke or
aside that gives the speaker character, and any passage another section calls
back to. **Do a dependency check:** if a cut passage introduced a term, a person,
or a premise that later text relies on, keep the setup or cut the callback. An
orphaned "Mike's giving me the head nod" after its setup was removed is the
classic failure.

**Cut on thought boundaries.** Start where a complete thought begins; end after the
last word is *finished*, with room for the sentence tail. Never end a kept range
mid-sentence, and give a closing line a little extra tail so it doesn't sound cut
off. Check where the kept range ends in the *transcript text*, not just timestamps.

**The approval list** (one per pass, numbered so the user can say "yes to 1–5, 8"):

| # | Draft time (link) | What it contains | Why cut | Context lost | Saves |
|---|---|---|---|---|---|

Include total seconds saved and the projected runtime. Offer the user a link per
row that starts a few seconds before the passage (see
[reviewer.md](reviewer.md)). Keep one-line descriptions; the clickable link is for
detail. If the user states a target ("much shorter", "especially section X"),
that outranks these defaults. Don't *add* material (tangents, restored setup)
when asked to tighten.

After approval, apply the cuts in the build, regenerate the transcript and
chapters, and report what changed, using the new draft's timestamps.
