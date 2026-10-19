# Pi harness adapter

This adapter targets <https://github.com/nicobailon/pi-subagents> (npm `pi-subagents`, unscoped). Confirm the installed extension and load its bundled skill for dispatch, workflows, monitoring, steering, and control details rather than duplicating them here. Validate launch into the orchestrator-provisioned worktree without a second allocator; an unsupported factory workspace blocks dispatch.

Note that an unrelated project, `@tintinweb/pi-subagents`, shares the name. If the session's tools are `Agent` / `get_subagent_result` / `steer_subagent` rather than `subagent` / `subagent_supervisor` / `subagents_enable`, this adapter does not apply.

## Direct session contact — letting the user talk to a worker

When the user wants to discuss something with a worker rather than read a report — during QA walkthroughs, when they want to interrogate a worker's reasoning or push back on its choices, or when the worker is blocked on direction only the user can give — offer direct contact only after verifying that the installed harness supports safe handoff and managed resumption: the orchestrator hands them a command to enter the worker's real session. A direct conversation appends to the worker's session file, so it works only as a strict sequential handoff: the user owns the session while they are in it, the orchestrator stays silent, and the orchestrator resumes through the managed path only after the user has fully exited.

Historical validation (Pi 1.1.0, pi-subagents 0.76.1; revalidate for the installed versions before offering direct contact): a finished async child, a direct `pi --session` conversation adding a genuine turn, a clean exit, then a managed `resume` — the resumed child recalled the direct-session turn from the same file. Sequential, never concurrent.

- **Finished or paused only.** Verify the run is complete or paused and its runner process has exited before offering the command. Never offer direct contact on a live running child — a second writer on the same session file can silently branch or corrupt it.
- **Resolve the full session path.** The orchestrator reads `steps[N].sessionFile` from the run's `status.json` (it appears about a second after launch). The full path is mandatory: Pi's session listing and ID-prefix lookup do not descend into child run directories, so a session ID or prefix will not resolve for a subagent session. Do not invent a shorter form.
- **Hand over an exact command**, run from the child's cwd with its model stated explicitly (resuming does not restore the child's model):

  ```bash
  cd <child-cwd> && pi --session '<full-session-path>' --model <provider/model>
  ```

- **After offering, hands off.** Do not steer, resume, probe, or summarize the child while the user may be talking to it. Any orchestrator-side turn in that window races the user's session. The only cautious period is after this offer has been made — before that, normal supervision applies. Do not offer direct contact unless the user or worker needs it.
- **Instruct the user to fully quit** (`/quit`, process ended — not merely idle) when done and say so; only then resume through the managed path, targeting the most recent run id (`resume` returns a new run id each time).
- Decisions reached in a directly driven session are invisible to the orchestrator until the resume; fold them into the planning documents.

## Relay mode — fallback when direct contact will not serve

When direct contact is unavailable, unverified, or impractical — the run is still live, or the user would rather not open a second terminal — offer relay mode instead: the orchestrator passes the user's messages to the worker verbatim, and passes the worker's replies back verbatim. The user is effectively talking to the worker, and the worker stays a managed run the whole time.

### Running it

- Enter and leave the mode explicitly, so both sides know which messages are being relayed.
- Relay faithfully in both directions. Do not summarize, soften, or answer on the worker's behalf.
- Live run: deliver with `steer`. Paused or completed run: deliver with `resume`.
- **`resume` returns a new run id each time.** Always target the most recent one; the original id goes stale after the first revival.
- Carry the worker's working constraints in the relayed message when they change — for example lifting a no-write restriction for one specific file.
- The orchestrator still owns the conversation around the relay. If the worker reports a genuine ambiguity, resolving it from the project's own documents is better than bouncing the question back to the user.
- Decisions reached during a relay still need folding into the planning documents; the transcript is not the record.
