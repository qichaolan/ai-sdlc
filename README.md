# ai-sdlc

Agent skills and a project harness for running the software development lifecycle with coding agents such as Claude Code and Codex. The skills cover Python development, spec-driven changes, design review, documentation, and session memory. The harness makes agents follow the same workflow, checks, and approval gates in every repo.

**What it isn't:** a framework or a program you run. Everything here is Markdown instructions and configuration files that you copy into a project. The Python skills target uv, Ruff, mypy, pytest, GitHub Actions, and Google Cloud; the design, docs, OpenSpec, and session skills work with any stack.

## How the pieces fit

| Piece | What it is | Use it for |
| --- | --- | --- |
| **Skills** (`*/SKILL.md`) | Instructions an agent loads when a task matches, such as how to review a diff or write tests | Better results on each task |
| **Harness** ([harness/](harness/README.md)) | `AGENTS.md` and `CLAUDE.md` templates, CI, permission rules, a session-start hook, a sandbox, and CODEOWNERS | Making the workflow repeatable and enforced in every project |

Skills are advice: an agent may skip one or not load it. The harness covers what must happen anyway. CI blocks merges that fail tests or coverage, permission rules stop force-pushes and unapproved deploys, and `AGENTS.md` tells the agent which skill to use for which task. Use skills on their own to try them out; add the harness when you want the same guarantees in every repo.

## Before you begin

- A coding agent that supports skills in the `SKILL.md` format. The commands below use Claude Code.
- `git`, plus [uv](https://docs.astral.sh/uv/) for the Python skills.
- For the OpenSpec skills: Node and the [openspec](https://github.com/Fission-AI/OpenSpec) CLI.
- For the harness sandbox: Docker. The devcontainer also needs an editor or CLI that supports dev containers.

## Quick start: skills only

1. Clone the repo:

   ```bash
   git clone https://github.com/qichaolan/ai-sdlc.git
   cd ai-sdlc
   ```

2. Copy the skills into one project, or into your user folder to use them everywhere:

   ```bash
   # One project
   mkdir -p /path/to/project/.claude/skills
   cp -r python-* design-review-web-ux tech-doc-writer-reviewer openspec-* session-memory /path/to/project/.claude/skills/

   # Every project
   mkdir -p ~/.claude/skills
   cp -r python-* design-review-web-ux tech-doc-writer-reviewer openspec-* session-memory ~/.claude/skills/
   ```

   If a skill folder already exists, `cp -r` overwrites its files, including any local edits, but keeps files that no longer exist in this repo. To update cleanly, see [Updating](#updating).

3. Start a new Claude Code session in the project and ask it to list its skills. The skill names in the catalog below should appear.

4. Give it a task, for example "review the diff on this branch". The agent picks the matching skill. To pick one yourself, name it in the prompt ("use python-code-review on this diff") or type `/<skill-name>`.

## Quick start: full harness

Follow [harness/README.md](harness/README.md). In short:

1. Copy the harness files and the skills into the project root.
2. Fill in the `<placeholders>` in `AGENTS.md`, the CI workflow, `CODEOWNERS`, and, if you use OpenSpec, `openspec/config.yaml`.
3. Add the Ruff, mypy, and coverage settings to `pyproject.toml`.
4. Work inside the devcontainer, or run tests on the host with `scripts/test-offline.sh`.
5. Ask the agent to "set up session memory".
6. On GitHub, protect `main` with required pull requests, required CI checks, and code-owner review.

## Daily workflow

| Task | Skills, in order | Your part |
| --- | --- | --- |
| New feature or behavior change | `openspec-explore` → `openspec-propose` → `openspec-apply-change` (uses `python-development` and `python-testing`) → `python-code-review` → `openspec-archive-change` | Approve the proposal before implementation starts; review the PR |
| Bug fix or refactor | `python-development` → `python-testing` → `python-code-review` | Review the PR |
| Release | `python-release` | Approve each deploy |
| Docs or UX change | `tech-doc-writer-reviewer`, `design-review-web-ux` | Review the findings |
| Any session | `session-memory` at the start and end | Read the handoff in `docs/PROGRESS.md` when you return |

Tips:

- **Review in a fresh context.** Run `python-code-review` in a new session or a subagent, not in the session that wrote the code.
- **Put project rules in `AGENTS.md`, not in the skills.** Rules in `AGENTS.md` override a skill when they conflict, so you can keep the skills identical across projects and update them by copying again.
- **Name the skill when it matters.** Matching is automatic but not guaranteed.

## Skill catalog

The skills fall into four groups. Within a group they are meant to be used in order, but each one also works on its own.

### Python development

Set up, build, test, review, and ship a Python project.

| Skill | Use it when |
| --- | --- |
| [python-project-setup](python-project-setup/SKILL.md) | Scaffolding or modernizing a project (uv, Ruff, mypy, pytest, GitHub Actions, GCP Cloud Run) |
| [python-development](python-development/SKILL.md) | Implementing, fixing, or refactoring code |
| [python-testing](python-testing/SKILL.md) | Writing, running, or debugging pytest tests with coverage |
| [python-code-review](python-code-review/SKILL.md) | Reviewing code, diffs, or pull requests |
| [python-release](python-release/SKILL.md) | Releasing a reviewed project to GKE or Cloud Run functions with gated, human-approved deploys |

### Spec-driven changes (OpenSpec)

Plan a change as written specs, implement it, then archive it. These skills require the [openspec](https://github.com/Fission-AI/OpenSpec) CLI.

| Skill | Use it when |
| --- | --- |
| [openspec-explore](openspec-explore/SKILL.md) | Thinking through ideas or requirements before proposing a change |
| [openspec-propose](openspec-propose/SKILL.md) | Generating a full change proposal: design, specs, and tasks |
| [openspec-apply-change](openspec-apply-change/SKILL.md) | Implementing the tasks of an OpenSpec change |
| [openspec-archive-change](openspec-archive-change/SKILL.md) | Archiving a completed change |

### Design and documentation

Standalone skills for UX and docs work. They can be used at any point in the lifecycle.

| Skill | Use it when |
| --- | --- |
| [design-review-web-ux](design-review-web-ux/SKILL.md) | Auditing or designing web UX: accessibility, responsive behavior, flows, forms, dashboards |
| [tech-doc-writer-reviewer](tech-doc-writer-reviewer/SKILL.md) | Writing or reviewing READMEs, guides, API references, design docs, runbooks, release notes |

### Session management

Keeps work resumable across sessions and agents through a handoff file and the project's own docs. Skills load only when an agent matches them to the task, so add the [AGENTS.md snippet](session-memory/references/agents-snippet.md) (already in the harness template) to make agents use this one at the start and end of every session.

| Skill | Use it when |
| --- | --- |
| [session-memory](session-memory/SKILL.md) | Starting, resuming, or handing off work; keeping context small; recording decisions in the right doc |

## Repo map

```text
ai-sdlc/
├── python-*/                  # Python lifecycle skills
├── openspec-*/                # spec-driven change skills
├── design-review-web-ux/      # UX review skill, with reference files
├── tech-doc-writer-reviewer/  # documentation skill
├── session-memory/            # session handoff skill, with templates
└── harness/                   # project starter kit (see harness/README.md)
```

## Updating

1. If you changed a skill inside a project, move that change into the project's `AGENTS.md` first. The next step deletes it.
2. Pull the repo, delete the old skill folders, and copy them again:

   ```bash
   cd ai-sdlc && git pull
   rm -rf /path/to/project/.claude/skills/{python-*,design-review-web-ux,tech-doc-writer-reviewer,openspec-*,session-memory}
   cp -r python-* design-review-web-ux tech-doc-writer-reviewer openspec-* session-memory /path/to/project/.claude/skills/
   ```

   Deleting first removes files that no longer exist in this repo. Use `~/.claude/skills` instead of the project path if you installed for every project.
