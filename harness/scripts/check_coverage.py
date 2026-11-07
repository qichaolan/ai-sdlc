"""Fail when branch or function coverage is below the threshold.

Reads the JSON report from ``pytest --cov --cov-branch
--cov-report=json`` and checks each file and the total. A function
counts as covered when at least one of its lines ran. Files with no
branches or no functions pass that check. Tested with coverage.py
7.13; a report without function data is rejected.

Usage: python scripts/check_coverage.py [coverage.json] [--min 90]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def branch_counts(summary: dict[str, Any]) -> tuple[int, int]:
    """Return (covered, total) branches from a coverage summary."""
    return summary.get("covered_branches", 0), summary.get("num_branches", 0)


def function_counts(file_data: dict[str, Any]) -> tuple[int, int]:
    """Return (covered, total) functions for one file.

    Coverage.py lists module-level code under the "" key; skip it.
    """
    functions = {
        name: data
        for name, data in file_data.get("functions", {}).items()
        if name
    }
    covered = sum(
        1
        for data in functions.values()
        if data["summary"]["covered_lines"] > 0
    )
    return covered, len(functions)


def percent(covered: int, total: int) -> float:
    """Return a percentage; an empty total counts as fully covered."""
    return 100.0 if total == 0 else 100.0 * covered / total


def check(report: dict[str, Any], minimum: float) -> list[str]:
    """Return one failure message per metric below the minimum."""
    failures: list[str] = []
    totals = {"branch": [0, 0], "function": [0, 0]}
    for path, file_data in sorted(report["files"].items()):
        counts = {
            "branch": branch_counts(file_data["summary"]),
            "function": function_counts(file_data),
        }
        for metric, (covered, total) in counts.items():
            totals[metric][0] += covered
            totals[metric][1] += total
            pct = percent(covered, total)
            if pct < minimum:
                failures.append(
                    f"{path}: {metric} {pct:.1f}% "
                    f"({covered}/{total}) < {minimum:g}%"
                )
    for metric, (covered, total) in totals.items():
        pct = percent(covered, total)
        print(f"Total {metric} coverage: {pct:.1f}% ({covered}/{total})")
        if pct < minimum:
            failures.append(f"Total: {metric} {pct:.1f}% < {minimum:g}%")
    return failures


def main(argv: list[str] | None = None) -> int:
    """Run the gate and return the process exit code."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("report", nargs="?", default="coverage.json")
    parser.add_argument("--min", type=float, default=90.0)
    args = parser.parse_args(argv)
    path = Path(args.report)
    if not path.is_file():
        print(f"Coverage report not found: {path}", file=sys.stderr)
        return 2
    report = json.loads(path.read_text(encoding="utf-8"))
    if not report.get("files"):
        print("Coverage report has no files", file=sys.stderr)
        return 2
    if not any("functions" in data for data in report["files"].values()):
        print(
            "Coverage report has no function data; upgrade coverage.py",
            file=sys.stderr,
        )
        return 2
    failures = check(report, args.min)
    for failure in failures:
        print(f"FAIL {failure}", file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
