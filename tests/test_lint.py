"""Tests for envault.lint module."""

import pytest
from pathlib import Path
from envault.lint import lint_env_file, format_lint_report, LintIssue


@pytest.fixture
def env_file(tmp_path):
    """Return a factory that writes content to a temp .env file."""
    def _write(content: str) -> Path:
        p = tmp_path / ".env"
        p.write_text(content)
        return p
    return _write


def test_lint_clean_file_returns_no_issues(env_file):
    path = env_file("FOO=bar\nBAZ=qux\n")
    issues = lint_env_file(path)
    assert issues == []


def test_lint_missing_separator(env_file):
    path = env_file("NOEQUALSSIGN\n")
    issues = lint_env_file(path)
    codes = [i.code for i in issues]
    assert "W001" in codes


def test_lint_blank_key(env_file):
    path = env_file("=somevalue\n")
    issues = lint_env_file(path)
    codes = [i.code for i in issues]
    assert "E001" in codes


def test_lint_key_with_spaces(env_file):
    path = env_file("MY KEY=value\n")
    issues = lint_env_file(path)
    codes = [i.code for i in issues]
    assert "E002" in codes


def test_lint_duplicate_key(env_file):
    path = env_file("FOO=bar\nFOO=baz\n")
    issues = lint_env_file(path)
    codes = [i.code for i in issues]
    assert "E005" in codes


def test_lint_empty_value_warns(env_file):
    path = env_file("FOO=\n")
    issues = lint_env_file(path)
    codes = [i.code for i in issues]
    assert "W003" in codes


def test_lint_unquoted_special_chars(env_file):
    path = env_file("FOO=hello#world\n")
    issues = lint_env_file(path)
    codes = [i.code for i in issues]
    assert "E004" in codes


def test_lint_quoted_special_chars_no_issue(env_file):
    path = env_file('FOO="hello#world"\n')
    issues = lint_env_file(path)
    codes = [i.code for i in issues]
    assert "E004" not in codes


def test_lint_strict_mode_flags_lowercase_key(env_file):
    path = env_file("myKey=value\n")
    issues = lint_env_file(path, strict=True)
    codes = [i.code for i in issues]
    assert "E003" in codes


def test_lint_strict_mode_accepts_upper_snake(env_file):
    path = env_file("MY_KEY=value\n")
    issues = lint_env_file(path, strict=True)
    codes = [i.code for i in issues]
    assert "E003" not in codes


def test_lint_skips_comments_and_blank_lines(env_file):
    path = env_file("# This is a comment\n\nFOO=bar\n")
    issues = lint_env_file(path)
    assert issues == []


def test_lint_file_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        lint_env_file(tmp_path / "nonexistent.env")


def test_format_lint_report_no_issues():
    assert format_lint_report([]) == "No issues found."


def test_format_lint_report_shows_codes():
    issues = [LintIssue(1, "E001", "Line 1: blank key name")]
    report = format_lint_report(issues)
    assert "E001" in report
    assert "blank key name" in report
