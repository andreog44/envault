"""Tests for envault/tags.py"""

import pytest
from pathlib import Path

from envault.config import init_config
from envault.tags import (
    list_tags,
    add_tag,
    remove_tag,
    has_tag,
    clear_tags,
)


@pytest.fixture
def project_dir(tmp_path: Path) -> Path:
    init_config(tmp_path)
    return tmp_path


def test_list_tags_empty_initially(project_dir):
    assert list_tags(project_dir) == []


def test_add_tag_returns_list_with_tag(project_dir):
    result = add_tag(project_dir, "production")
    assert "production" in result


def test_add_tag_persists(project_dir):
    add_tag(project_dir, "staging")
    assert "staging" in list_tags(project_dir)


def test_add_multiple_tags(project_dir):
    add_tag(project_dir, "alpha")
    add_tag(project_dir, "beta")
    tags = list_tags(project_dir)
    assert "alpha" in tags
    assert "beta" in tags
    assert len(tags) == 2


def test_add_duplicate_tag_is_idempotent(project_dir):
    add_tag(project_dir, "dup")
    add_tag(project_dir, "dup")
    assert list_tags(project_dir).count("dup") == 1


def test_add_empty_tag_raises(project_dir):
    with pytest.raises(ValueError, match="empty"):
        add_tag(project_dir, "   ")


def test_remove_tag(project_dir):
    add_tag(project_dir, "to-remove")
    remove_tag(project_dir, "to-remove")
    assert "to-remove" not in list_tags(project_dir)


def test_remove_nonexistent_tag_raises(project_dir):
    with pytest.raises(KeyError, match="ghost"):
        remove_tag(project_dir, "ghost")


def test_has_tag_true(project_dir):
    add_tag(project_dir, "present")
    assert has_tag(project_dir, "present") is True


def test_has_tag_false(project_dir):
    assert has_tag(project_dir, "absent") is False


def test_clear_tags_removes_all(project_dir):
    add_tag(project_dir, "x")
    add_tag(project_dir, "y")
    clear_tags(project_dir)
    assert list_tags(project_dir) == []
