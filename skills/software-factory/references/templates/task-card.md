---
id: "<stable-id>"
title: "<short task name>"
status: triage # adapt to chosen board; promotion alone does not mean ready
created: "<date>"
touched: "<date>"
board_order: <optional-number>
tags: []
# Optional relationships/capabilities; use only if the task system supports them.
# priority: <optional>
# parent: <optional-task-id>
# subtasks: []
# blocked_by: []
---

# <Task title>

## Desired outcome

<What should change and why?>

## Acceptance criteria

- [ ] <Observable result>

## Planning artifacts

Planning directory: <exact TASKS/PLANNING/<task>/ path, set by the orchestrator when planning begins; updated to the dated TASKS/WIP/YYYY-MM-DD-<task>/ path at dispatch>

## Planning and implementation checklist

- [ ] Review relevant PRODUCT/ and ARCHITECTURE/ guidance.
- [ ] Orchestrator: create brainstorm.md and todos.md from templates, gather user details, and iterate inline Q&A until both parties agree the requirements and QA plan.
- [ ] Orchestrator: after brainstorming is explicitly complete, populate the execution checklist; verify both planning files and move them to dated WIP at dispatch.
- [ ] Worker: review all WIP documents, then implement the agreed task and maintain todos.md.
- [ ] Run agreed tests and independent product QA.
- [ ] Record outcome and evidence; move WIP artifacts into `TASKS/COMPLETE/YYYY-MM-DD-<task>/` and archive this card there from `TASKS/KANBAN/`; update paths and links.

## Notes / activity

<Visible comments, decisions, blockers, or links. Keep blocker rationale here or in the task system's activity log.>
