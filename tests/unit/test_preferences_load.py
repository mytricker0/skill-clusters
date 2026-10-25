"""Unit tests for load_preferences."""

import os

from skill_clusters.store import load_preferences


def test_missing_file_returns_empty(fixtures_dir):
    prefs, warnings = load_preferences(os.path.join(fixtures_dir, "missing.toml"))
    assert prefs == {}
    assert warnings == []


def test_invalid_toml_returns_warning(fixtures_dir):
    prefs, warnings = load_preferences(os.path.join(fixtures_dir, "preferences", "invalid.toml"))
    assert warnings
    assert any("invalid.toml" in w for w in warnings)


def test_favor_list_parsed(fixtures_dir):
    prefs, warnings = load_preferences(os.path.join(fixtures_dir, "preferences", "favor-b.toml"))
    assert prefs["global"]["favor"] == ["diagram-b"]


def test_wrong_type_gives_warning(tmp_path):
    path = tmp_path / "bad.toml"
    path.write_text("[global]\nfavor = \"diagram-a\"\n")
    prefs, warnings = load_preferences(str(path))
    assert warnings
