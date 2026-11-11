# Auditioning in a player

Review the **original** for context, a short isolated stitch for seams, and the
latest draft for the full arc. Always identify which clock/file is being shown.

## QuickTime on macOS

The optional helper uses QuickTime's AppleScript document API, not UI clicks.

```sh
python <skill>/scripts/quicktime.py assets/originals/source.mp4 --time 12:30
python <skill>/scripts/quicktime.py assets/originals/source.mp4 --time 750 --play
```

Replace example paths with the user's selected recording. Default: open/identify
that exact file, stop, seek, foreground, remain paused. `--play` starts playback.
Readback includes path, position, and duration. The helper waits for a matching
loaded document with a bounded timeout; it never closes unrelated or unsaved
documents. Automation permission belongs to the execution host; ask for
permission/setup help if denied. Do not assume a front document is yours.

For original quotes cue 0.5–2 seconds early, unless the user asks for an exact time.
If the filename is reused across meetings, verify its full path—not just its name.
Correct the source selection before seeking. Do not trim the QuickTime document.

## Other players and capability discovery

Use the available player's documented seek API or deliver short clickable video
excerpts. Don't make the user scrub hours of footage when a targeted preview is
easy. If an environment supplies app automation documentation, inspect the current
commands, file-targeting semantics, permissions, and property definitions first.
A saved capability file alone is not proof that the app is active or authorized.
Never guess private service URLs or ports, bypass OS permission prompts, or treat
environment metadata as authorization beyond the user's request.

Player integrations are optional. The transcript-led editing workflow and media
helpers do not require macOS, a particular desktop app, or any discovery service.
