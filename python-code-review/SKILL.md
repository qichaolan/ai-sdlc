---
name: python-code-review
description: "Use when reviewing Python source, diffs, pull requests, or tests for correctness, security, failure handling, performance, maintainability, and project-style compliance."
---

# Python Code Review

Review the requested Python files, diff, or pull request. Prefer concrete, evidence-based findings over broad style commentary. Review changed code first, then inspect directly related code only when needed to establish impact.

## Workflow

1. Identify the review surface and the repository's stated conventions. Check `pyproject.toml`, `setup.cfg`, `tox.ini`, formatter/linter configuration, type-checker settings, and nearby tests when they exist.
2. Understand the control flow and data flow before judging an implementation. Trace inputs, side effects, resource ownership, exception paths, and public API contracts.
3. Run the narrowest relevant tests, linter, formatter check, or type checker when practical. Report only commands that were actually run and distinguish tool failures from code findings.
4. Prioritize findings by user impact: security and correctness, data loss or reliability, failure handling, performance and scalability, maintainability, then style.
5. For each finding, explain the impact and propose the smallest practical fix. Do not request speculative refactors or rewrites.

## Review Checklist

### Correctness and failure handling

- Check edge cases, invalid or missing inputs, empty collections, retries, timeouts, concurrency, and transaction boundaries.
- Check that expected errors are handled at the right boundary, with useful context and without silently swallowing exceptions.
- Check cleanup of files, sockets, locks, temporary resources, and database transactions. Prefer context managers where appropriate.
- Check that return values, state changes, and exceptions match the surrounding API and its tests.

### Security

- Look for hardcoded credentials, tokens, private data in logs, unsafe interpolation, injection risks, path traversal, unsafe deserialization, weak randomness, and insecure defaults.
- Treat user-controlled input and external responses as untrusted until validated.
- Do not report a security issue without describing the reachable attack or exposure path.

### Performance and scalability

- Look for accidental quadratic work, repeated I/O or database queries in loops, unnecessary materialization, unbounded retries, and excessive memory retention.
- Consider realistic workload size and the largest input the surrounding contract permits. Recommend generators, batching, caching, or a different algorithm only when the evidence supports it.

### Python design and idioms

- Prefer clear standard-library features, context managers, comprehensions when readable, and existing project utilities over custom reinvention.
- Check mutable default arguments, surprising mutation or aliasing, broad exception handling, import cycles, hidden global state, and unclear ownership.
- Check type annotations and docstrings when the project uses them, but follow the project's configured conventions rather than imposing a universal style.

### Tests and maintainability

- Check whether important behavior, failure paths, permissions, boundaries, and regressions are covered by focused tests.
- Flag missing tests only when the untested behavior creates meaningful regression risk.
- Look for mixed responsibilities, excessive nesting, duplicated logic, and interfaces that are difficult to test.
- Treat function and module size as heuristics, not defects by themselves. A long cohesive function may be acceptable; a short function with several responsibilities is not.

## Finding Rules

- Review the diff first and avoid unrelated cleanup.
- State assumptions when repository context is incomplete.
- Do not report formatting or naming issues when project configuration explicitly permits them.
- Do not claim that a test, linter, formatter, or type checker passed unless it was run.
- Distinguish definite defects from risks, suggestions, and test gaps.
- Prefer one finding per root cause and avoid duplicate findings for the same behavior.

## Output Format

List findings first, ordered by severity:

```text
[High] `path/to/file.py:line` - Short issue title
Area: Security | Correctness | Reliability | Performance | Maintainability | Style | Tests
Impact: Explain the concrete failure, affected users or data, and relevant conditions.
Fix: Describe the smallest practical change.
```

Use `Medium` for issues that can cause meaningful failures under common or important conditions, and `Low` for limited-impact defects or maintainability concerns. Use `High` only for severe security, data-loss, outage, or broadly breaking issues.

After findings, include:

- **Open questions or assumptions:** only when they affect the review result.
- **Checks run:** exact commands and their outcomes, or state that no checks were run.
- **Summary:** one sentence describing the overall risk and any notable test gap.

If no issues are found, say so explicitly and still mention meaningful untested areas or checks that were not run.
