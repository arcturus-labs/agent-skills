# Cameras and screen footage

Choose picture based on meaning, not a fixed rotation:
- Speaker close-up: purpose, emotion, testimony, explanation.
- Gallery: connection, group participation, reactions that actually occurred.
- Shared screen: what participants are building/testing/reacting to.
- Screen + speaker: keep the human present when the interface remains readable.

Probe every useful layout, verify its clock, and use one continuous audio source
where possible. Equal durations don't establish synchronization. Different sources
may have different dimensions or letterboxing. Keep aspect ratio; don't stretch
interfaces or crop away meaningful controls. Upscaling isn't added source detail.
Check output readability at the intended viewing size and inspect screen shares
for private data, keys, addresses, account details, or unlabeled synthetic profiles.

## Animated close-up → gallery

When requested, a synchronized close-up can shrink into that speaker's gallery
tile while revealing the gallery beneath:

1. Inspect a source frame and identify the real tile rectangle. Layouts can change;
   don't hard-code a person to “top row, third slot” across recordings.
2. Normalize both streams to a common time base/frame rate and reset both PTS to
   zero before compositing. The foreground must exist on the **first frame**.
3. Animate position and size from full-frame to the tile using smooth easing,
   e.g. `E(u) = (1 - cos(pi * clamp(u,0,1))) / 2`.
4. Match framing at the destination. If aspect ratios differ, crop/contain
   deliberately; optionally dissolve the foreground away at landing.
5. Inspect a frame strip from before, during, and after the animation. A gallery
   flash at frame zero means stream timing/availability is wrong, not a reason
   to concatenate duplicate padded segments.

Use a project-specific FFmpeg filter graph or another suitable compositor.
Do not build a general motion-graphics engine for one requested transition.
