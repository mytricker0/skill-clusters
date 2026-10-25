"""Unit tests for arrange."""

import os

from skill_clusters.arrange import arrange, correct
from skill_clusters.model import Membership, Skill
from skill_clusters.store import State, load_state, save_state


def test_new_skill_matching_cluster_is_filed():
    skills = [Skill("diagram-a", "Create architecture diagrams and flowcharts", "project")]
    state = State(memberships=[], proposed_clusters=[])
    result = arrange(skills, state)
    assert result["filed"] == [{"skill": "diagram-a", "cluster": "diagrams"}]


def test_new_skill_matching_none_is_unclustered():
    skills = [Skill("mystery", "something totally unrelated", "project")]
    state = State(memberships=[], proposed_clusters=[])
    result = arrange(skills, state)
    assert result["unclustered"] == [{"name": "mystery", "origin": "project", "reason": "unclustered"}]


def test_skill_removed_is_dropped_and_listed():
    skills = [Skill("diagram-b", "Draw diagrams and mind maps", "project")]
    state = State(memberships=[Membership("diagram-a", "project", "diagrams", 5.0, source="auto")])
    result = arrange(skills, state)
    assert {"name": "diagram-a", "origin": "project"} in result["removed"]


def test_user_membership_never_overwritten_by_auto():
    skills = [Skill("diagram-a", "Create architecture diagrams and flowcharts", "project")]
    state = State(memberships=[Membership("diagram-a", "project", "diagrams", 5.0, source="user")])
    result = arrange(skills, state)
    # Already filed by user, not re-filed.
    assert result["filed"] == []


def test_removed_true_marker_not_readded():
    skills = [Skill("diagram-a", "Create architecture diagrams and flowcharts", "project")]
    state = State(memberships=[Membership("diagram-a", "project", "diagrams", 5.0, source="user", removed=True)])
    result = arrange(skills, state)
    assert result["filed"] == []


def test_dry_run_writes_nothing():
    skills = [Skill("diagram-a", "Create architecture diagrams and flowcharts", "project")]
    state = State(memberships=[], proposed_clusters=[])
    result = arrange(skills, state, dry_run=True)
    assert result["filed"] == [{"skill": "diagram-a", "cluster": "diagrams"}]
    assert len(state.memberships) == 0


def test_correct_records_user_membership():
    state = State(memberships=[], proposed_clusters=[])
    result = correct("diagram-a", "diagrams", state=state, state_path="state.json")
    assert result["source"] == "user"
    assert any(m.skill == "diagram-a" and m.source == "user" for m in state.memberships)


def test_correct_remove_marks_removed():
    state = State(memberships=[Membership("diagram-a", "project", "diagrams", 5.0, source="user")])
    result = correct("diagram-a", "diagrams", remove=True, state=state, state_path="state.json")
    assert result["removed"] is True
    assert state.memberships[0].removed is True
