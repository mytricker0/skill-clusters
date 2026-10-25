"""Unit tests for discover."""

import os

from skill_clusters.discover import discover


def test_finds_skills_in_project(fixtures_dir):
    skills = discover(fixtures_dir, os.path.join(fixtures_dir, "nonexistent"))
    names = {(s.name, s.origin) for s in skills}
    assert ("diagram-a", "project") in names
    assert ("video-maker", "project") in names


def test_parses_frontmatter(fixtures_dir):
    skills = discover(fixtures_dir, os.path.join(fixtures_dir, "nonexistent"))
    by_name = {s.name: s for s in skills}
    assert by_name["diagram-a"].description.startswith("Create architecture diagrams")


def test_missing_user_dir_is_not_error(fixtures_dir):
    skills = discover(fixtures_dir, os.path.join(fixtures_dir, "nonexistent"))
    assert isinstance(skills, list)


def test_same_name_in_both_origins_yields_two(tmp_path):
    user = tmp_path / "user"
    sd = user / "dup"
    sd.mkdir(parents=True)
    (sd / "SKILL.md").write_text("name: dup\ndescription: user dup\n")
    project = tmp_path / "project"
    psd = project / ".claude" / "skills" / "dup"
    psd.mkdir(parents=True)
    (psd / "SKILL.md").write_text("name: dup\ndescription: project dup\n")
    skills = discover(str(project), str(user))
    by_origin = {(s.origin, s.name) for s in skills}
    assert ("project", "dup") in by_origin
    assert ("user", "dup") in by_origin
