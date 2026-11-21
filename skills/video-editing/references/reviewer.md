# Local content reviewer

A read-only browser workbench for **rendered videos**: project/draft navigation,
clickable chapters and transcript paragraphs, seek controls, and timestamp links
that work directly from chat. No framework, upload, account, access token, or
transcription service is needed. Originals and edits are not modified.

## Launch

Requires Python 3.10+. Run the bundled program from any working directory:

```sh
python <skill>/scripts/reviewer/serve.py --project /path/to/project
# Multiple projects or a collection; no need to register a draft individually:
python <skill>/scripts/reviewer/serve.py --root /path/to/projects --port 8765
```

Replace paths with real user-selected directories. `--project` and `--root` are
repeatable and may be combined. A project registration allows that exact project;
a collection root allows projects below it. The index lists immediate recognizable
projects (PROJECT.md, drafts/, review.json, video.mp4, or final.mp4). Deeply nested
projects can be registered explicitly or visited by a permitted absolute path.
Prefer narrow roots, not the user's whole home directory.

Open the printed `http://127.0.0.1:8765/` URL. The program stays in the foreground;
Ctrl-C stops it. If running it in the background, save its PID/log in the project's
`scratch/` and only stop that owned process. A busy port is an error: select another
port or reconcile the known existing reviewer, not kill an unrelated process.

## Stable links and endpoints

| URL | Purpose |
|---|---|
| `/` | Registered-project browser |
| `/review?path=<absolute-project-directory>` | Project overview / draft choices |
| `/review?path=<directory>&draft=001&t=3370.12` | Draft, positioned at 56:10.12 |
| `/api/projects` | Project list JSON |
| `/api/project?path=<directory>` | Available reviews JSON |
| `/api/review?path=<directory>&draft=001` | Playback metadata / normalized paragraphs |
| `/media?path=<directory>&draft=001` | Selected video bytes; GET/HEAD and HTTP ranges |

Static UI resources are under `/static/`. No arbitrary `file=` route or filesystem
browser exists. URL-encode directory parameters (spaces, `&`, `#`, Unicode). Use
**Copy link here** in the viewer instead of constructing links by hand. `t` is
nonnegative seconds, decimals allowed, on the **selected video's clock**. Links
remain stable across restarts at the same port and unchanged paths. Moving a
project or removing/replacing a draft changes what a link can show.

Click a chapter/paragraph to seek and play. Direct chat links seek too, but browser
autoplay policy may require an initial Play click. Player controls include ±10s,
seconds/M:SS/H:MM:SS jump, transcript search, and copy-current-time. Navigation stays
inside the site; the browser Back button returns to prior project/draft selections.
Browser codec support still applies; H.264/AAC MP4 is the safest starting point.

## Project/draft conventions and review.json

The layout in SKILL.md remains unchanged. Optional playback metadata lives beside
the video, not in the server code:

```text
project/
├── review.json              # optional root review, e.g. an original recording
├── video.mp4                # optional root video
├── final.mp4                # optional final
├── final.review.json        # optional metadata for final.mp4
└── drafts/001/
    ├── video.mp4
    ├── review.json          # optional title, video, chapters, transcript
    ├── transcript-timed.json
    └── edit.json
```

`draft=001` selects a draft folder. Reserved selections `draft=project` and
`draft=final` select the root review and final. Do not use those reserved names
for numbered draft folders. No final file is created merely by reviewing.

Example (see [template](../templates/review.example.json)):

```json
{
  "version": 1,
  "title": "Draft 001",
  "video": "video.mp4",
  "transcript": "transcript-timed.json",
  "chapters": [{"time": 0, "title": "Opening"}, {"time": 15.5, "title": "Demo"}]
}
```

Paths resolve **relative to review.json's directory**. Every field is optional.
`duration` can optionally supply seconds for the overview; the browser obtains the
actual duration during playback. `chapters` can be a list or a path to JSON
containing a list (or `{ "chapters": [...] }`). Chapter times may be seconds or
H:MM:SS. `transcript: null` and `chapters: []` explicitly disable those features.

Without a sidecar, the reviewer uses:
- `video.mp4` (or `final.mp4` for the final selection).
- `transcript-timed.json`, then `transcript.json`, **in the selected draft folder**.
- `chapters.json`; otherwise chapter headings from edit.json's `sequence` entries
  **only when they already have output_start times**.

Transcript input: `{ "words": [{ "word": "Hi", "start": 1, "end": 1.4,
"speaker": "A" }] }`, or `paragraphs`/`segments` entries with `text`, `start`,
`end`, optional `speaker`. Existing timed transcripts' `cards` entries with
`output_start`, `output_end`, and `card` are supported. Word entries are grouped
into readable paragraphs; names are not inferred from anonymous speaker labels.

All chapter/transcript times must already match the selected video. Never attach
an original source-clock transcript to an edited render without remapping it.
The reviewer does not load raw-response.json, transcribe, or regenerate edits.
Missing optional metadata leaves a usable video player. Malformed optional
metadata produces a warning; invalid explicit media paths produce a clear error.
An edit plan without a rendered video is listed as unavailable—not silently played
as though it were a finished cut.

## Original/external media and safety

To review an original stored elsewhere, explicitly point a root or draft
review.json's `video` at it and launch with `--media-root /path/to/recordings`.
Relative external paths work too, but only within explicitly allowed media roots.
Metadata remains confined to the selected project. There is no automatic import
of every private source-registry file or transcript.

The server binds only to 127.0.0.1. No random token is used, as requested. Selected
roots, resolved-path checks, fixed routes, media extensions, Host/Origin checks,
Fetch Metadata, no CORS, and a restrictive content-security policy reduce accidental
exposure. This is **not authentication or a hardened multi-user service**: other
programs/users on the same machine may access selected content. Don't expose it
through a proxy/tunnel or use broad roots. Treat project text as untrusted;
transcripts render as text, not HTML. Don't commit runtime configs with private
paths or generated transcripts to a public skill distribution.

## Maintenance / limits

UI and server code are bundled together under `scripts/reviewer/`. Run all helper
tests with `python -m unittest discover -s <skill>/tests -v`. Test actual browser
seeking/navigation after changes; HTTP tests alone don't prove the UI works.
The optional browser harness uses Playwright only for testing, without adding web
search tools or requiring it to run the reviewer:

```sh
uv run --no-project --with playwright python <skill>/tests/browser_reviewer.py \
  --output-dir /path/to/scratch/reviewer-qa
```

Install Playwright Chromium in the test environment first, or pass
`--browser-executable /path/to/chrome` to use an existing browser binary in an
isolated temporary profile. Add `--project /path/to/project` for actual-draft QA.
Do not commit resulting screenshots/reports with private content.
Custom project builds can emit review.json without adopting a universal edit
schema. Ask before changing shared contracts to accommodate new formats.

Source-assembly previews, transitions/effects without rendering, and saved review
annotations are future work in [BACKLOG.md](../BACKLOG.md), not current features.
