"""Contract tests: options, arrange, correct, show JSON shapes."""

import json

from conftest import FIXTURES


def test_options_json_shape(run_cli):
    code, out, err = run_cli(
        "options", "--request", "draw a diagram",
        "--project-dir", FIXTURES, "--user-dir", FIXTURES,
    )
    assert code == 0
    data = json.loads(out)
    assert {"cluster", "ambiguous", "single", "options", "hidden_count", "warnings"}.issubset(data.keys())
    for o in data["options"]:
        assert {"name", "description", "origin"}.issubset(o.keys())


def test_options_single_true(run_cli):
    code, out, err = run_cli(
        "options", "--request", "draw a diagram",
        "--project-dir", FIXTURES, "--user-dir", FIXTURES,
    )
    data = json.loads(out)
    assert data["cluster"] == "diagrams"
    assert data["options"], "expected at least one diagram option"


def test_options_human(run_cli):
    code, out, err = run_cli(
        "options", "--request", "draw a diagram",
        "--project-dir", FIXTURES, "--user-dir", FIXTURES,
        "--format", "human",
    )
    assert code == 0
    assert "diagrams" in out


def test_arrange_json_shape(run_cli, tmp_path):
    state = str(tmp_path / "state.json")
    code, out, err = run_cli(
        "arrange", "--dry-run",
        "--project-dir", FIXTURES, "--user-dir", FIXTURES,
        "--state", state,
    )
    assert code == 0
    data = json.loads(out)
    assert {"filed", "unclustered", "proposed_clusters", "removed"}.issubset(data.keys())


def test_correct_json_shape(run_cli, tmp_path):
    state = str(tmp_path / "state.json")
    code, out, err = run_cli(
        "correct", "diagram-a", "diagrams",
        "--project-dir", FIXTURES, "--user-dir", FIXTURES,
        "--state", state,
    )
    assert code == 0
    data = json.loads(out)
    assert data["source"] == "user"
    assert data["skill"] == "diagram-a"


def test_show_json(run_cli, tmp_path):
    state = str(tmp_path / "state.json")
    run_cli("correct", "diagram-a", "diagrams",
            "--project-dir", FIXTURES, "--user-dir", FIXTURES, "--state", state)
    code, out, err = run_cli(
        "show", "--cluster", "diagrams",
        "--project-dir", FIXTURES, "--user-dir", FIXTURES,
        "--state", state,
    )
    assert code == 0
    assert "diagram-a" in out
