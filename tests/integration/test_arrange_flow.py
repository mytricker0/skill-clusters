"""Integration test: arrange files a new skill and corrects it."""

import os

from skill_clusters.arrange import arrange, correct
from skill_clusters.discover import discover
from skill_clusters.model import Membership, Skill
from skill_clusters.store import State


def test_arrange_files_new_skill(tmp_path):
    project = tmp_path / "project"
    skill_dir = project / ".claude" / "skills" / "research-hub"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("name: research-hub\ndescription: literature reviews and citations\n")
    skills = discover(str(project), str(tmp_path))
    state = State(memberships=[], proposed_clusters=[])
    result = arrange(skills, state, dry_run=False)
    assert any(
        f["skill"] == "research-hub" and f["cluster"] == "research"
        for f in result["filed"]
    )
    assert any(m.skill == "research-hub" and m.source == "auto" for m in state.memberships)


def test_correct_persists_user_membership(tmp_path):
    project = tmp_path / "project"
    skill_dir = project / ".claude" / "skills" / "research-hub"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("name: research-hub\ndescription: literature reviews and citations\n")
    skills = discover(str(project), str(tmp_path))
    state = State(memberships=[], proposed_clusters=[])
    arrange(skills, state)
    result = correct("research-hub", "diagrams", state=state, state_path="state.json")
    assert result["source"] == "user"
    diagrams = [m for m in state.memberships if m.cluster == "diagrams"]
    assert diagrams and diagrams[0].source == "user"
    assert diagrams[0].skill == "research-hub"


def test_correct_survives_arrange(tmp_path):
    project = tmp_path / "project"
    skill_dir = project / ".claude" / "skills" / "research-hub"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("name: research-hub\ndescription: literature reviews and citations\n")
    skills = discover(str(project), str(tmp_path))
    state = State(memberships=[], proposed_clusters=[])
    correct("research-hub", "diagrams", state=state, state_path="state.json")
    # Re-arrange: user correction should not be overwritten by auto.
    result = arrange(skills, state)
    diagrams = [m for m in state.memberships if m.cluster == "diagrams"]
    assert diagrams and diagrams[0].source == "user"
    assert diagrams[0].skill == "research-hub"


def test_removed_skill_dropped(tmp_path):
    skills = [Skill("gone", "something", "project")]
    state = State(memberships=[Membership("gone", "project", "diagrams", 5.0, source="auto")])
    result = arrange(skills, state)
    assert {"name": "gone", "origin": "project"} in result["removed"]
