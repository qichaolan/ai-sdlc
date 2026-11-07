# ai-sdlc

Agent skills for the software development lifecycle (Python development, design review, documentation, spec-driven changes, and session memory), for use with Claude Code, Codex, and similar coding agents.

The skills fall into four groups. Within a group they are meant to be used in order, but each one also works on its own.

## Python development

Setup, build, test, review, and ship a Python project.

| Skill | Use it when |
| --- | --- |
| [python-project-setup](python-project-setup/SKILL.md) | Scaffolding or modernizing a project (uv, Ruff, mypy, pytest, GitHub Actions, GCP Cloud Run) |
| [python-development](python-development/SKILL.md) | Implementing, fixing, or refactoring code |
| [python-testing](python-testing/SKILL.md) | Writing, running, or debugging pytest tests with coverage |
| [python-code-review](python-code-review/SKILL.md) | Reviewing code, diffs, or pull requests |
| [python-release](python-release/SKILL.md) | Releasing a reviewed project to GKE or Cloud Run functions with gated, human-approved deploys |

## Spec-driven changes (OpenSpec)

Plan a change as written specs, implement it, then archive it. These skills require the [openspec](https://github.com/Fission-AI/OpenSpec) CLI.

| Skill | Use it when |
| --- | --- |
| [openspec-explore](openspec-explore/SKILL.md) | Thinking through ideas or requirements before proposing a change |
| [openspec-propose](openspec-propose/SKILL.md) | Generating a full change proposal: design, specs, and tasks |
| [openspec-apply-change](openspec-apply-change/SKILL.md) | Implementing the tasks of an OpenSpec change |
| [openspec-archive-change](openspec-archive-change/SKILL.md) | Archiving a completed change |

## Design and documentation

Standalone skills for UX and docs work. They can be used at any point in the lifecycle.

| Skill | Use it when |
| --- | --- |
| [design-review-web-ux](design-review-web-ux/SKILL.md) | Auditing or designing web UX: accessibility, responsive behavior, flows, forms, dashboards |
| [tech-doc-writer-reviewer](tech-doc-writer-reviewer/SKILL.md) | Writing or reviewing READMEs, guides, API references, design docs, runbooks, release notes |

## Session management

Keeps work resumable across sessions and agents through a handoff file and the project's own docs. To set it up, ask the agent to set up session memory, then add the [AGENTS.md snippet](session-memory/references/agents-snippet.md). Skills load only when an agent matches them to the task, so the snippet tells agents to use this one at the start and end of every session.

| Skill | Use it when |
| --- | --- |
| [session-memory](session-memory/SKILL.md) | Starting, resuming, or handing off work; keeping context small; recording decisions in the right doc |

## Installation

Copy the skills into `.claude/skills/` in a project, or into `~/.claude/skills/` to use them everywhere:

```bash
cp -r python-* design-review-web-ux tech-doc-writer-reviewer openspec-* session-memory .claude/skills/
```
