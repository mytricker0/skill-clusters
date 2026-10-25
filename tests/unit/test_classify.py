"""Unit tests for classify."""

from skill_clusters.classify import classify, match_request
from skill_clusters.model import Cluster, Skill


def _diagram_skills():
    return [
        Skill("diagram-a", "Create architecture diagrams and flowcharts", "project"),
        Skill("video-maker", "Edit video clips and make short animations", "project"),
        Skill("no-desc", "", "project"),
    ]


def test_name_scores_higher_than_description():
    skills = [Skill("d", "diagram", "project")]
    result = classify(skills)
    assert any(m.cluster == "diagrams" for m in result.memberships)


def test_diagram_skills_go_to_diagrams():
    result = classify(_diagram_skills())
    clusters = {m.skill: m.cluster for m in result.memberships}
    assert clusters.get("diagram-a") == "diagrams"


def test_empty_description_is_unclustered_no_description():
    result = classify(_diagram_skills())
    unclustered = {u["name"]: u["reason"] for u in result.unclustered}
    assert unclustered.get("no-desc") == "no-description"


def test_no_match_reason():
    skills = [Skill("x", "something totally unrelated to any cluster", "project")]
    result = classify(skills)
    unclustered = {u["name"]: u["reason"] for u in result.unclustered}
    assert unclustered.get("x") == "no-match"


def test_multi_cluster_allowed():
    skills = [Skill("both", "diagram flowchart and video animation", "project")]
    result = classify(skills)
    clusters = {m.cluster for m in result.memberships}
    assert "diagrams" in clusters and "video" in clusters


def test_deterministic_order():
    skills = _diagram_skills()
    first = classify(skills).memberships
    second = classify(list(reversed(skills))).memberships
    assert [m.skill for m in first] == [m.skill for m in second]


def test_match_request_clear_winner():
    result = match_request("draw a diagram of the flow")
    assert result["cluster"] == "diagrams"
    assert result["ambiguous"] == []


def test_match_request_ambiguous():
    result = match_request("chart video")
    assert result["cluster"] is None
    assert len(result["ambiguous"]) >= 2


def test_match_request_no_match():
    result = match_request("write a document")
    # 'document' matches documents cluster
    assert result["cluster"] == "documents"
