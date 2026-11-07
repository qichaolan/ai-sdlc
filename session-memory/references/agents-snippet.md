# AGENTS.md snippet

Add this section to the project's `AGENTS.md`, replacing the
placeholders. Skills load only when the agent matches them to the
task, so this pointer makes sure the agent uses the skill at the start
and end of every session.

```markdown
## Context and session management

Use the `session-memory` skill at the start and end of every session
and before the context is compacted or cleared. Project settings:

- Handoff file: `docs/PROGRESS.md` (<committed | git-ignored>)
- Plan tracker: <OpenSpec (`openspec/changes/`) | `docs/plans/` | none>
- Doc map: conventions → this file; user-visible changes →
  `CHANGELOG.md`; deployment → <deploy doc>
- Run once per task, at the end: <slow or live checks, e.g. the smoke
  test>
- Never store in memory files: <private data specific to this project>
```
