"""Tests for envault profile management."""

import pytest
from pathlib import Path

from envault.config import init_config
from envault.profiles import (
    add_profile,
    list_profiles,
    get_profile,
    remove_profile,
    set_active_profile,
    get_active_profile,
    DEFAULT_PROFILE,
)


@pytest.fixture
def project_dir(tmp_path):
    init_config(tmp_path)
    return tmp_path


def test_list_profiles_empty_initially(project_dir):
    assert list_profiles(project_dir) == []


def test_add_profile_returns_profile_dict(project_dir):
    profile = add_profile(project_dir, "staging", ".env.staging")
    assert profile["env_file"] == ".env.staging"


def test_add_profile_appears_in_list(project_dir):
    add_profile(project_dir, "staging", ".env.staging")
    assert "staging" in list_profiles(project_dir)


def test_add_multiple_profiles(project_dir):
    add_profile(project_dir, "dev", ".env.dev")
    add_profile(project_dir, "prod", ".env.prod")
    profiles = list_profiles(project_dir)
    assert "dev" in profiles
    assert "prod" in profiles


def test_get_profile_returns_correct_data(project_dir):
    add_profile(project_dir, "dev", ".env.dev")
    p = get_profile(project_dir, "dev")
    assert p is not None
    assert p["env_file"] == ".env.dev"


def test_get_profile_returns_none_for_missing(project_dir):
    assert get_profile(project_dir, "nonexistent") is None


def test_remove_profile_removes_it(project_dir):
    add_profile(project_dir, "staging", ".env.staging")
    result = remove_profile(project_dir, "staging")
    assert result is True
    assert "staging" not in list_profiles(project_dir)


def test_remove_profile_returns_false_when_not_found(project_dir):
    assert remove_profile(project_dir, "ghost") is False


def test_remove_default_profile_raises(project_dir):
    with pytest.raises(ValueError, match="default"):
        remove_profile(project_dir, DEFAULT_PROFILE)


def test_get_active_profile_defaults_to_default(project_dir):
    assert get_active_profile(project_dir) == DEFAULT_PROFILE


def test_set_active_profile_changes_active(project_dir):
    add_profile(project_dir, "prod", ".env.prod")
    set_active_profile(project_dir, "prod")
    assert get_active_profile(project_dir) == "prod"


def test_set_active_profile_raises_for_unknown(project_dir):
    with pytest.raises(KeyError):
        set_active_profile(project_dir, "unknown")
