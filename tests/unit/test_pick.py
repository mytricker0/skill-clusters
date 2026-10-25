"""Unit tests for build_options."""

from skill_clusters.classify import classify
from skill_clusters.model import Membership, Skill
from skill_clusters.pick import build_options


def _skills():
    return [
        Skill("diagram-a", "Create architecture diagrams and flowcharts", "project"),
        Skill("diagram-b", "Draw diagrams and mind maps", "project"),
        Skill("diagram-c", "Make flowcharts and diagrams", "project"),
    ]


def _memberships():
    return [
        Membership("diagram-a", "project", "diagrams", 5.0),
        Membership("diagram-b", "project", "diagrams", 3.0),
        Membership("diagram-c", "project", "diagrams", 2.0),
    ]


def test_orders_by_score():
    result = build_options("draw a diagram", _skills(), _memberships(), None, {})
    assert result["cluster"] == "diagrams"
    assert [o["name"] for o in result["options"]] == ["diagram-a", "diagram-b", "diagram-c"]


def test_favor_reorders():
    result = build_options("draw a diagram", _skills(), _memberships(), None, {"global": {"favor": ["diagram-b"]}})
    assert result["options"][0]["name"] == "diagram-b"


def test_single_true_for_one_member():
    members = [Membership("diagram-a", "project", "diagrams", 5.0)]
    result = build_options("draw a diagram", _skills(), members, None, {})
    assert result["single"] is True


def test_no_match_returns_null_cluster():
    result = build_options("xyzzy qwerty", _skills(), _memberships(), None, {})
    assert result["cluster"] is None


def test_exclude_removes_option():
    result = build_options("draw a diagram", _skills(), _memberships(), None, {"global": {"exclude": ["diagram-b"]}})
    assert [o["name"] for o in result["options"]] == ["diagram-a", "diagram-c"]
