"""Integration test: discovery + classification performance."""

import os
import time

from skill_clusters.classify import classify
from skill_clusters.discover import discover


def _make_skills(tmp_path, count):
    root = tmp_path / "skills"
    for i in range(count):
        d = root / f"skill-{i}"
        d.mkdir(parents=True)
        (d / "SKILL.md").write_text(
            f"name: skill-{i}\n"
            f"description: Create architecture diagrams and flowcharts for {i}\n"
        )
    return root


def test_discover_classify_under_1s(tmp_path):
    root = _make_skills(tmp_path, 500)
    skills = discover(str(root), str(root))
    assert len(skills) == 500
    start = time.perf_counter()
    result = classify(skills, None)
    elapsed = time.perf_counter() - start
    assert elapsed < 1.0, f"classify took {elapsed:.3f}s"
    assert len(result.memberships) == 500
