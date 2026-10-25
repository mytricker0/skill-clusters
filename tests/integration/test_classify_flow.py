"""Integration test: end-to-end discover -> classify over a fixtures tree."""

import os
import shutil
import tempfile

from skill_clusters.classify import classify
from skill_clusters.discover import discover


def test_classify_over_fixtures(fixtures_dir):
    skills = discover(fixtures_dir, os.path.join(fixtures_dir, "nonexistent"))
    result = classify(skills, None)
    by_name = {m.skill: m.cluster for m in result.memberships}
    assert by_name.get("diagram-a") == "diagrams"
    assert by_name.get("diagram-b") == "diagrams"
    assert by_name.get("video-maker") == "video"
    unclustered = {u["name"]: u["reason"] for u in result.unclustered}
    assert unclustered.get("no-desc") == "no-description"


def test_new_skill_filed(tmp_path):
    project = tmp_path / "project"
    skill_dir = project / ".claude" / "skills" / "research-hub"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("name: research-hub\ndescription: Do literature reviews and cite sources\n")
    skills = discover(str(project), str(tmp_path))
    result = classify(skills, None)
    clusters = [m.cluster for m in result.memberships if m.skill == "research-hub"]
    assert "research" in clusters


def test_fully_empty(tmp_path):
    skills = discover(str(tmp_path), str(tmp_path))
    result = classify(skills, None)
    assert result.memberships == []
    assert result.unclustered == []
