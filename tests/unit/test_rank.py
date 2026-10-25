"""Unit tests for apply_preferences."""

from skill_clusters.rank import apply_preferences


def test_favor_orders_first():
    opts = [
        {"name": "diagram-a", "description": "a", "origin": "project"},
        {"name": "diagram-b", "description": "b", "origin": "project"},
    ]
    ordered, _ = apply_preferences(opts, {"global": {"favor": ["diagram-b"]}}, "diagrams", {"diagram-a", "diagram-b"})
    assert ordered[0]["name"] == "diagram-b"


def test_exclude_removes():
    opts = [
        {"name": "diagram-a", "description": "a", "origin": "project"},
        {"name": "diagram-b", "description": "b", "origin": "project"},
    ]
    ordered, _ = apply_preferences(opts, {"global": {"exclude": ["diagram-b"]}}, "diagrams", {"diagram-a", "diagram-b"})
    assert [o["name"] for o in ordered] == ["diagram-a"]


def test_disfavor_orders_last():
    opts = [
        {"name": "diagram-a", "description": "a", "origin": "project"},
        {"name": "diagram-b", "description": "b", "origin": "project"},
    ]
    ordered, _ = apply_preferences(opts, {"global": {"disfavor": ["diagram-b"]}}, "diagrams", {"diagram-a", "diagram-b"})
    assert ordered[-1]["name"] == "diagram-b"


def test_unknown_names_ignored_with_warning():
    opts = [{"name": "diagram-a", "description": "a", "origin": "project"}]
    _, warnings = apply_preferences(opts, {"global": {"favor": ["unknown"]}}, "diagrams", {"diagram-a"})
    assert any("unknown" in w for w in warnings)


def test_cluster_over_global():
    opts = [
        {"name": "diagram-a", "description": "a", "origin": "project"},
        {"name": "diagram-b", "description": "b", "origin": "project"},
    ]
    prefs = {
        "global": {"favor": ["diagram-b"]},
        "clusters": {"diagrams": {"favor": ["diagram-a"]}},
    }
    ordered, _ = apply_preferences(opts, prefs, "diagrams", {"diagram-a", "diagram-b"})
    assert ordered[0]["name"] == "diagram-a"
