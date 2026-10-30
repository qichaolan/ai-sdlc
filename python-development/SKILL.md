---
name: python-development
description: "Use when implementing, fixing, or refactoring Python code: AST-aware context gathering, PEP 8 edits, sandboxed testing, bounded self-correction, structured patch/JSON output, and safe Git isolation and rollback."
---

# Python Development

Make the **smallest correct, readable change**. Prefer existing project patterns over new abstractions. Never claim a check passed unless it actually ran.

## Workflow

1. **Inspect context:** Read the request, `pyproject.toml` (or `setup.cfg`, `tox.ini`, linter/type-checker config), related modules, callers, and tests. Use Python's `ast` module to parse relevant `.py` files **without importing or executing them**; identify classes, functions, imports, and call sites, and record `lineno`/`end_lineno` and signatures of symbols you may change. If AST parsing fails, fall back to text inspection and report the syntax error.
2. **Isolate with Git:** Run `git status` first and record the starting commit.
   - For a multi-file or risky task, create a uniquely named branch (e.g. `agent/fix-bug-123`), preferably in a **separate agent-owned worktree** (`git worktree add`). Never overwrite an existing branch, discard user changes, or reuse a dirty worktree for risky operations.
   - If the directory is **not a Git repository**, do not run `git init`. Edit in place with minimal changes, report `branch: null`, and treat automated rollback as `not_safe`.
3. **Implement:** Make minimal, targeted edits; preserve public interfaces unless a change is requested; keep unrelated refactoring out of scope. Track each edit by **file, affected symbol signature, and before/after line range**. Re-parse changed files with `ast`, then review `git diff --check` and the full diff for unintended edits.
4. **Check safely:** **Treat AI-generated and untrusted code as unsafe to execute.**
   - **Static checks** that do not import or run project code (`ast` parsing, Ruff, formatter `--check`, type checkers without executing plugins) may run on the host.
   - **Dynamic checks** (tests, project imports, build steps, any project command) run **only in a disposable isolated container/sandbox**: no production credentials, no network by default, unprivileged user, restricted mounts, CPU/memory/time limits, disposable storage. A virtual environment or subprocess alone is **not** a sandbox.
   - If no suitable sandbox is available, run static checks only and report dynamic checks as `not_run`.
5. **Self-correct:** Examine lint/type results, test failures, and the diff. Fix root causes, not symptoms, and rerun the relevant checks. Allow **at most 3 fix-and-recheck iterations**; stop if still failing. Never invent results or weaken, skip, or delete tests to make them pass.
6. **Finish or roll back:**
   - **Success:** keep the branch/worktree for review. Do not merge, push, or deploy.
   - **Failure after the iteration limit:** restore the **agent-owned isolated worktree** to its recorded starting commit and remove only files the agent created. `git reset --hard <starting-commit>` (plus removing agent-created untracked files) is permitted **only** inside that verified worktree with no pre-existing user edits; **never** in the user's original or a shared worktree.
   - If isolation or ownership is uncertain, stop and ask instead of running destructive cleanup; report `rollback: "not_safe"`.
7. **Return output** per the contract below.

## Coding Rules

- **PEP 8:** 4-space indents; `snake_case` functions/variables; `CapWords` classes; `UPPER_CASE` constants; imports grouped stdlib / third-party / local. Default to **79** characters per code line and **72** for comments/docstrings; **project settings override** (e.g. Ruff/Black `line-length`).
- **Functions:** one responsibility. **5–20 lines ideal**, review at 21–50, normally split **over 50**. Do not split a cohesive function just to hit a number.
- **Modules:** one cohesive concept. **Under 300 lines ideal**, review at 300–500, normally split **over 500**; avoid **over 1,000**.
- Prefer built-ins, the standard library, context managers, and simple control flow. Add type hints to public or nontrivial functions. Avoid new dependencies unless necessary.
- Validate inputs at boundaries; catch specific exceptions; close resources; never silently swallow failures.
- Never introduce hardcoded secrets, `shell=True` with untrusted input, unsafe deserialization (`pickle`, `yaml.load`), SQL string interpolation, or mutable default arguments.
- Consider **100,000-row** inputs where relevant: avoid quadratic loops, repeated I/O in loops, and loading everything into memory unnecessarily.
- Add focused tests for normal cases, edge cases, and failure paths.

## Final Self-Review

Before returning, answer each question against the final diff:

| Area | Question |
| --- | --- |
| **1. Style** | Does this look like standard, readable Python that matches the project? |
| **2. Idiom** | Does it use built-ins and the standard library rather than reinventing them? |
| **3. Safety** | What happens when it fails? Are errors handled specifically and resources released? |
| **4. Speed** | Will it freeze or run out of memory with 100,000 rows? |
| **5. Security** | Any leaked keys, unvalidated inputs, injection paths, or risky defaults? |

## Output Contract

Choose one mode. Machine-consumed output has **no preamble, Markdown fences, or extra prose**.

- **Apply mode (default):** edit the repository files, then return **strict valid JSON**:
  `{"status":"passed|failed|unverified","branch":"agent/task-or-null","worktree":"/path/or-null","changes":[{"path":"src/x.py","symbol":"function_name(args)","before_lines":[10,20],"after_lines":[10,24]}],"checks":[{"name":"pytest","result":"passed|failed|not_run"}],"rollback":"none|completed|not_safe","notes":[]}`
  - Use one concrete value where alternatives are shown with `|`.
  - `status` is `passed` only if every required check ran and passed; `unverified` if any required check was `not_run`; otherwise `failed`.
  - Use `null` for line ranges that do not apply (e.g. `before_lines` of a new file). Use `changes: []` if no files changed.
  - Put failures, skipped checks, and unverified behavior in `notes`.
- **Patch-only mode (when a patch is requested):** do **not** modify files; return **only a valid unified diff** with `--- a/path` / `+++ b/path` headers and `@@ -start,count +start,count @@` hunks with context lines, so it applies cleanly with `git apply`. If a patch cannot be made safely, return apply-mode JSON with `changes: []` and the reason in `notes` instead of inventing a diff.
- Never output speculative line numbers; verify them against the final files or diff.

For a separate audit or pull-request review, use the `python-code-review` skill.
