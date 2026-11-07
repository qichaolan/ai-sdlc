# Agent instructions

<!--
Template from ai-sdlc/harness. Replace every <placeholder>, delete
sections that don't apply (for example OpenSpec), then delete this
comment. Keep the file short: agents read all of it every session.
-->

## Project

<One or two sentences: what the project does, how it runs, and where
its output goes.> Python <3.12>, uv, `src/` layout.

```text
src/<package>/
├── cli.py            # <entry point>
├── config.py         # <settings>
├── integrations/     # <network, file, and cloud access>
└── services/         # <business logic; keep it pure>
```

<Architecture rules agents must keep, e.g. "services/ never does
I/O; put network, file, and cloud access in integrations/".>

## Commands

```bash
uv sync --locked
uv run ruff check . && uv run ruff format --check .   # lint
uv run mypy                                           # typecheck
uv run pytest -q --cov --cov-branch \
  --cov-report=term-missing --cov-report=json         # tests + coverage
uv run python scripts/check_coverage.py               # branch/function gate
<build command, e.g. docker build -t <image>:local .> # build
<smoke command against real services, if any>         # smoke test
openspec validate --all --strict --no-interactive     # specs + changes
```

Add dependencies with `uv add`, never by editing `uv.lock`.

## Skills

Load the matching skill before starting; one task may need several.
The rules in this file override a skill when they conflict.

| Task | Skill |
| --- | --- |
| Scaffolding, tooling, CI, deployment setup | `python-project-setup` |
| Implementing, fixing, refactoring code | `python-development` |
| Writing, running, debugging tests and coverage | `python-testing` |
| Reviewing code, diffs, pull requests | `python-code-review` |
| UX, accessibility, responsive layout | `design-review-web-ux` |
| Writing, reviewing, updating docs | `tech-doc-writer-reviewer` |
| Releasing to GKE or Cloud Run functions | `python-release` |
| Exploring, proposing, implementing, archiving a spec change | `openspec-explore`, `openspec-propose`, `openspec-apply-change`, `openspec-archive-change` |
| Starting, resuming, or handing off a session | `session-memory` |

Review in a fresh context: run `python-code-review` in a new session
or a subagent, not in the session that wrote the code.

## Spec-driven changes (OpenSpec)

`openspec/specs/<capability>/spec.md` states what the system does now.
`openspec/changes/<name>/` holds one proposed change: `proposal.md`,
delta specs, `design.md`, and `tasks.md`. `openspec/config.yaml` adds
project rules to every step.

- Open a change for new behavior, work that spans sessions, or any
  edit to a requirement. Skip it for bug fixes that restore specified
  behavior, refactors, dependency bumps, and doc fixes.
- Get the owner's approval of `proposal.md` and the delta specs before
  implementing.
- Implement from `tasks.md` and tick each task when it is done and
  verified.
- Archive with `openspec archive <name> --yes` as the last commit of
  the PR, so spec updates are reviewed with the code. Never archive by
  moving the folder: that skips the merge into `openspec/specs/`.

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

## Definition of Done

A task is not done until every item below holds. Don't report "done"
or propose a deployment before then.

1. **Tests change with the code.** Every new or changed function and
   branch has a test. A bug fix includes a regression test that fails
   before the fix. Never delete, skip, or weaken a failing test to make
   the suite pass; if a test looks wrong, stop and ask.
2. **Coverage ≥ <90> %, branch and function, per file and overall.**
   Run the tests and `scripts/check_coverage.py`. Don't lower the
   threshold, add `pragma: no cover`, or exclude files to pass.
3. **Docs change with the code.** Docstrings for changed public
   behavior; `README.md` for changed commands, settings, or setup;
   `CHANGELOG.md` "Unreleased" for user-visible changes; the deploy doc
   for infrastructure changes; specs through an OpenSpec change for
   specified behavior. If no doc changes, say why.
4. **Local checks pass, in order:** lint and typecheck, tests and
   coverage gate, build, smoke test. If a check can't run or an
   external service is down, report it as **not passed**, never as
   passed.

The final summary lists: files changed (code, tests, docs), branch and
function coverage, the result of each check, whether the handoff file
was updated, and the OpenSpec change and `openspec validate` result,
if any.

## Standards

- PEP 8; Ruff line length 79, docstrings 72; mypy strict.
- Functions 5–20 lines where practical; modules under 300 lines.
- Tests are offline: fake HTTP, cloud, and clock (see
  `tests/conftest.py`).
- <Contracts that need owner approval to change, e.g. a calculation
  method or a public output format.>

## Safety

- Tests, builds, and project commands run code: run them only in the
  devcontainer, a disposable sandbox, or CI, never with production
  credentials.
- Never commit `.env`, keys, or service-account JSON. Never create
  service-account keys; deploy with Workload Identity Federation.
- Never push, merge, force-push, or reset without explicit approval.
- Deployments, IAM changes, public access, and production changes need
  explicit approval. See <deploy doc>.
- Don't work around provider rate limits or bot checks.
- <Private data rules, e.g. "files in data/private/ never leave the
  machine; use synthetic numbers in tests, docs, and specs".>
