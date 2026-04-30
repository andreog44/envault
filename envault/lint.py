"""Lint/validate .env files for common issues."""

from pathlib import Path
from typing import NamedTuple


class LintIssue(NamedTuple):
    line: int
    code: str
    message: str


LINT_CODES = {
    "E001": "Blank key name",
    "E002": "Key contains spaces",
    "E003": "Key does not follow UPPER_SNAKE_CASE convention",
    "E004": "Value contains unquoted special characters",
    "E005": "Duplicate key",
    "W001": "Line missing '=' separator",
    "W002": "Trailing whitespace in value",
    "W003": "Empty value (may be intentional)",
}

SPECIAL_CHARS = set("#$&*(){}|;<>?")


def lint_env_file(path: Path, strict: bool = False) -> list[LintIssue]:
    """Lint a .env file and return a list of issues found."""
    issues: list[LintIssue] = []
    seen_keys: dict[str, int] = {}

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    lines = path.read_text().splitlines()

    for lineno, raw in enumerate(lines, start=1):
        line = raw.strip()

        # Skip blank lines and comments
        if not line or line.startswith("#"):
            continue

        if "=" not in line:
            issues.append(LintIssue(lineno, "W001", f"Line {lineno}: missing '=' separator"))
            continue

        key, _, value = line.partition("=")

        if not key:
            issues.append(LintIssue(lineno, "E001", f"Line {lineno}: blank key name"))
            continue

        if " " in key:
            issues.append(LintIssue(lineno, "E002", f"Line {lineno}: key '{key}' contains spaces"))

        if strict and not key.replace("_", "").isupper():
            issues.append(LintIssue(lineno, "E003", f"Line {lineno}: key '{key}' is not UPPER_SNAKE_CASE"))

        if key in seen_keys:
            issues.append(LintIssue(lineno, "E005", f"Line {lineno}: duplicate key '{key}' (first seen at line {seen_keys[key]})"))
        else:
            seen_keys[key] = lineno

        unquoted = value not in ('', ) and not (value.startswith('"') or value.startswith("'"))
        if unquoted and any(c in SPECIAL_CHARS for c in value):
            issues.append(LintIssue(lineno, "E004", f"Line {lineno}: value for '{key}' contains unquoted special characters"))

        if value != value.rstrip():
            issues.append(LintIssue(lineno, "W002", f"Line {lineno}: value for '{key}' has trailing whitespace"))

        if value == "":
            issues.append(LintIssue(lineno, "W003", f"Line {lineno}: value for '{key}' is empty"))

    return issues


def format_lint_report(issues: list[LintIssue]) -> str:
    """Format lint issues into a human-readable report."""
    if not issues:
        return "No issues found."
    lines = []
    for issue in issues:
        lines.append(f"  [{issue.code}] {issue.message}")
    return "\n".join(lines)
