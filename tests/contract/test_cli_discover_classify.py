"""Contract tests: CLI JSON shapes for discover and classify."""

import json

from conftest import FIXTURES


def test_discover_json_shape(run_cli):
    code, out, err = run_cli("discover", "--project-dir", FIXTURES, "--user-dir", FIXTURES)
    assert code == 0
    data = json.loads(out)
    assert "skills" in data
    keys = {"name", "description", "origin", "kind", "path"}
    for s in data["skills"]:
        assert keys.issubset(s.keys())
        assert s["origin"] in {"project", "user"}


def test_classify_json_shape(run_cli):
    code, out, err = run_cli("classify", "--project-dir", FIXTURES, "--user-dir", FIXTURES, "--threshold", "3")
    assert code == 0
    data = json.loads(out)
    assert "memberships" in data
    assert "unclustered" in data
    for m in data["memberships"]:
        assert {"skill", "origin", "cluster", "score"}.issubset(m.keys())
    for u in data["unclustered"]:
        assert {"name", "origin", "reason"}.issubset(u.keys())
        assert u["reason"] in {"no-description", "no-match"}
