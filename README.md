# ai-sdlc

Agent skills for the software development lifecycle (Python development, design review, documentation, and spec-driven changes), for use with Claude Code, Codex, and similar coding agents.

## Skills

| Skill | Use it when |
| --- | --- |
| [python-project-setup](python-project-setup/SKILL.md) | Scaffolding or modernizing a project (uv, Ruff, mypy, pytest, GitHub Actions, GCP Cloud Run) |
| [python-development](python-development/SKILL.md) | Implementing, fixing, or refactoring code |
| [python-testing](python-testing/SKILL.md) | Writing, running, or debugging pytest tests with coverage |
| [python-code-review](python-code-review/SKILL.md) | Reviewing code, diffs, or pull requests |
| [python-release](python-release/SKILL.md) | Releasing a reviewed project to GKE or Cloud Run functions with gated, human-approved deploys |
| [design-review-web-ux](design-review-web-ux/SKILL.md) | Auditing or designing web UX: accessibility, responsive behavior, flows, forms, dashboards |
| [tech-doc-writer-reviewer](tech-doc-writer-reviewer/SKILL.md) | Writing or reviewing READMEs, guides, API references, design docs, runbooks, release notes |
| [openspec-explore](openspec-explore/SKILL.md) | Thinking through ideas or requirements before proposing a change (requires the openspec CLI) |
| [openspec-propose](openspec-propose/SKILL.md) | Generating a full change proposal: design, specs, and tasks |
| [openspec-apply-change](openspec-apply-change/SKILL.md) | Implementing the tasks of an OpenSpec change |
| [openspec-archive-change](openspec-archive-change/SKILL.md) | Archiving a completed change |

## Installation

Copy the skills into `.claude/skills/` in a project, or into `~/.claude/skills/` to use them everywhere:

```bash
cp -r python-* design-review-web-ux tech-doc-writer-reviewer openspec-* .claude/skills/
```
