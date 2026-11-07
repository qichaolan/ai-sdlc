---
name: session-memory
description: Keep coding work resumable across sessions and agents with repo-level memory. Resume from a handoff file, keep the context window small, track progress against the active plan, write a handoff before stopping or before the context is compacted or cleared, and promote lasting notes into the project's docs. Use at the start of a coding session, when resuming or picking up work, before ending, handing off, or compacting, when asked to save progress, record a decision, or remember something for the project, and to set up session memory in a repo. Not for the user's personal preferences.
---

# Session memory

Any agent, in any later session, should be able to pick up the work from the repo alone. Memory lives in version-controlled files, not in the conversation.

## Memory layers

| Layer | Holds | Lives for | Default location |
| --- | --- | --- | --- |
| Handoff file | Stopping point, unrecorded discoveries, blockers, verification, next action | One session to the next | `docs/PROGRESS.md` |
| Plan | Why a change is made, its decisions, its task checklist | One change | The project's plan tracker |
| Project docs | Requirements, conventions, architecture, user-visible changes | The project | Specs, `AGENTS.md`, `README.md`, `CHANGELOG.md`, ops docs |

## Project settings

Read `AGENTS.md` (and `CLAUDE.md`) first. A project may set: the handoff file path, the plan tracker, the doc map, and expensive checks to run only once. **Project rules override this skill.** Where a setting is missing, use the default or detect it:

- **Plan tracker:** `openspec/` exists → OpenSpec (`openspec list`; the change's `proposal.md`, `design.md`, `tasks.md`). Else `docs/plans/<name>.md` if that folder exists. Else none: the handoff file records only the stopping point and next action.
- **Doc map:** note which of `README.md`, `CHANGELOG.md`, `docs/`, ADRs, and deploy or runbook docs exist. Don't create new docs without asking.

## Mode

- **SETUP:** asked to set up session memory. Don't create memory files unasked.
- **START:** beginning or resuming work.
- **WORK:** during a task.
- **HANDOFF:** before stopping, handing off, or a context compaction or clear.
- **REMEMBER:** asked to save progress or record a fact or decision.

## Setup

1. Detect the settings above.
2. Create the handoff file from [references/progress-template.md](references/progress-template.md).
3. Propose the section in [references/agents-snippet.md](references/agents-snippet.md) for `AGENTS.md`, filled in with the detected paths and the project's expensive checks. Ask before editing `AGENTS.md` or `CLAUDE.md`.
4. Ask whether the handoff file is committed (shared across machines and agents) or git-ignored (local only); if git-ignored, add it to `.gitignore`.

## Start

1. Read the handoff file, then the active plan and the specs or docs it touches. If there is no handoff file, say so once and offer SETUP; then continue without it. Then read only the files the task needs; locate code with grep or glob before opening files.
2. Verify the notes against the code and Git state (branch, `git status`, `git log --oneline -10`) before relying on them. Fix stale notes, or flag them if you can't tell. Never repeat an unverified claim such as "tests pass".
3. Restate the goal and plan in a few lines before editing.

## Keep context small

- Read large files (lockfiles, fixtures, generated data) in targeted line ranges, not whole.
- Filter command output: quiet test flags, coverage only for changed files, `| tail -n 50` for long logs.
- Run slow, costly, or live checks (smoke tests against real services, full builds, deploy dry runs) once per task, at the end. Debug with fast offline reproductions instead of re-running them.
- Don't paste generated output (reports, coverage JSON, build artifacts) into the conversation; quote only the lines that matter.
- If subagents are available, send broad searches to one and bring back only its conclusions.

## Work

- Tick a plan task as soon as it is done and verified. Never tick unfinished work.
- Record a decision when it is made, in its lasting home (see the promotion map), not only in the handoff file.
- When the conversation is getting long, refresh the handoff file before continuing, so a compaction loses nothing.

## Handoff

1. Tick finished tasks in the plan.
2. Rewrite the handoff file; don't append to it. Keep it under ~60 lines and follow the template's sections. Link to the plan's checklist instead of copying it; work without an active plan records only its stopping point and next action. Remove stale and finished notes. Update the date.
3. Promote lasting notes (below), then delete them from the handoff file.
4. End with a summary that covers uncommitted changes, failing or unrun checks, whether the handoff file was updated, and the next step.

## Remember

Write the note straight to its lasting home from the promotion map. Use the handoff file only for notes that matter until the next session. Confirm where the note went.

## Promotion map (long-term memory)

| Note | Goes to |
| --- | --- |
| Required behavior | Specs, through the plan tracker's change process (for OpenSpec, a change's delta specs) |
| Why a change is made | The plan's proposal |
| Technical decision and rejected options | The plan's design doc, or an ADR |
| Convention, gotcha, architecture choice | `AGENTS.md` or `README.md`; propose the edit and ask before changing `AGENTS.md` or `CLAUDE.md` |
| User-visible change | `CHANGELOG.md` |
| Deployment or operations | The project's deploy or runbook doc |
| The user's personal preference | Not the repo; the agent's own user memory, if it has one |

If the target doc doesn't exist, keep the note in the handoff file and ask whether to create the doc.

## Rules

1. **No secrets or private data** in any memory file: no credentials, tokens, keys, personal data, or values from private datasets. Describe them; don't copy them.
2. **Facts with evidence.** Write dates, commit SHAs, and commands with their results, not intentions. Use absolute dates, never "yesterday".
3. **The repo wins.** On conflict, code and Git state beat notes; fix the note.
4. **A snapshot, not a log.** History belongs in Git, the plan, and `CHANGELOG.md`.
5. **Honest verification.** Record a check as `passed` only if it ran and passed; otherwise write `failed`, `not run`, or `not passed` with the reason.
