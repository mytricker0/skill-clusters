"""CLI entry point: discover | classify | options | arrange | correct | show.

Text protocol: JSON on stdout (``--format human`` for a readable table),
problems on stderr. Exit codes: 0 ok, 1 usage error, 2 recoverable problem
reported in output (e.g. bad preferences).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Optional

from .classify import classify
from .model import DEFAULT_THRESHOLD, Membership, Skill
from .pick import build_options
from .rank import apply_preferences
from .store import load_preferences, load_state, render_clusters_md


def _default_state_path(project_dir: str) -> str:
    return os.path.join(project_dir, ".skill-clusters", "state.json")


def _default_prefs_path(project_dir: str) -> str:
    return os.path.join(project_dir, ".skill-clusters", "preferences.toml")


def _human_options(result: dict) -> str:
    lines = []
    if result["cluster"]:
        lines.append(f"cluster: {result['cluster']}")
    if result["ambiguous"]:
        lines.append(f"ambiguous: {' or '.join(result['ambiguous'])}")
    for opt in result["options"]:
        lines.append(f"- {opt['name']} ({opt['origin']}): {opt['description']}")
    if result["hidden_count"]:
        lines.append(f"({result['hidden_count']} more; use --all)")
    for w in result["warnings"]:
        lines.append(f"warning: {w}")
    return "\n".join(lines)


def cmd_discover(args) -> int:
    from .discover import discover
    skills = discover(args.project_dir, args.user_dir)
    out = [{"name": s.name, "description": s.description, "origin": s.origin, "kind": s.kind, "path": s.path} for s in skills]
    print(json.dumps({"skills": out}, indent=2))
    return 0


def cmd_classify(args) -> int:
    from .discover import discover
    from .store import State
    skills = discover(args.project_dir, args.user_dir)
    state = load_state(args.state)
    threshold = args.threshold if args.threshold is not None else state.threshold
    result = classify(skills, None, threshold)
    out = {
        "memberships": [{"skill": m.skill, "origin": m.origin, "cluster": m.cluster, "score": m.score} for m in result.memberships],
        "unclustered": result.unclustered,
    }
    print(json.dumps(out, indent=2))
    return 0


def cmd_options(args) -> int:
    from .classify import classify
    from .discover import discover
    from .store import State
    skills = discover(args.project_dir, args.user_dir)
    state = load_state(args.state)
    if not state.memberships:
        state = State(memberships=classify(skills, None, state.threshold).memberships)
    prefs, warnings = load_preferences(args.prefs)
    result = build_options(args.request, skills, state.memberships, None, prefs, args.all)
    out = {
        "cluster": result["cluster"],
        "ambiguous": result["ambiguous"],
        "single": result["single"],
        "options": [{"name": o["name"], "description": o["description"], "origin": o["origin"]} for o in result["options"]],
        "hidden_count": result["hidden_count"],
        "warnings": warnings + result["warnings"],
    }
    if args.format == "human":
        print(_human_options(out))
    else:
        print(json.dumps(out, indent=2))
    return 2 if warnings else 0


def cmd_arrange(args) -> int:
    from .arrange import arrange
    from .discover import discover
    from .store import State
    skills = discover(args.project_dir, args.user_dir)
    state = load_state(args.state)
    result = arrange(skills, state, None, args.dry_run, args.state, state.threshold)
    print(json.dumps(result, indent=2))
    return 0


def cmd_correct(args) -> int:
    from .arrange import correct
    from .store import State
    state = load_state(args.state)
    result = correct(args.skill, args.cluster, args.remove, args.confirm_cluster, state, None, args.state)
    print(json.dumps(result, indent=2))
    return 0


def cmd_set_threshold(args) -> int:
    from .store import State, save_state
    state = load_state(args.state)
    state.threshold = args.value
    save_state(args.state, state.memberships, state.proposed_clusters, state.threshold)
    print(json.dumps({"threshold": state.threshold}))
    return 0


def cmd_show(args) -> int:
    from .store import load_state, render_clusters_md
    state = load_state(args.state)
    if args.cluster:
        rows = [m for m in state.memberships if m.cluster == args.cluster]
        if not rows:
            print(f"cluster {args.cluster}: (none)")
            return 0
        for m in sorted(rows, key=lambda x: (x.skill, x.origin)):
            print(f"- {m.skill} ({m.origin}) — {m.source}")
        return 0
    if args.skill:
        rows = [m for m in state.memberships if m.skill == args.skill]
        if not rows:
            print(f"skill {args.skill}: (unclustered)")
            return 0
        for m in sorted(rows, key=lambda x: (x.skill, x.origin)):
            print(f"- {m.cluster} — {m.source}")
        return 0
    clusters = sorted({m.cluster for m in state.memberships})
    render_clusters_md(state.memberships, clusters, os.path.join(os.path.dirname(args.state) or ".", "CLUSTERS.md"))
    for c in clusters:
        print(f"## {c}")
        rows = [m for m in state.memberships if m.cluster == c]
        for m in sorted(rows, key=lambda x: (x.skill, x.origin)):
            print(f"- {m.skill} ({m.origin}) — {m.source}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="skill-clusters", description="Discover, classify, rank, pick and arrange installed skills.")
    parser.add_argument("--project-dir", default=os.getcwd())
    parser.add_argument("--user-dir", default=os.path.expanduser("~/.claude/skills"))
    parser.add_argument("--state", default=None)
    parser.add_argument("--prefs", default=None)
    parser.add_argument("--format", choices=["json", "human"], default="json")
    sub = parser.add_subparsers(dest="command", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--project-dir", default=os.getcwd())
    common.add_argument("--user-dir", default=os.path.expanduser("~/.claude/skills"))
    common.add_argument("--state")
    common.add_argument("--prefs")
    common.add_argument("--format", choices=["json", "human"], default="json")

    p = sub.add_parser("discover", parents=[common])
    p.set_defaults(func=cmd_discover)

    p = sub.add_parser("classify", parents=[common])
    p.add_argument("--threshold", type=float, default=None)
    p.set_defaults(func=cmd_classify)

    p = sub.add_parser("options", parents=[common])
    p.add_argument("--request", required=True)
    p.add_argument("--all", action="store_true")
    p.set_defaults(func=cmd_options)

    p = sub.add_parser("arrange", parents=[common])
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(func=cmd_arrange)

    p = sub.add_parser("correct", parents=[common])
    p.add_argument("skill")
    p.add_argument("cluster")
    p.add_argument("--remove", action="store_true")
    p.add_argument("--confirm-cluster", action="store_true")
    p.set_defaults(func=cmd_correct)

    p = sub.add_parser("show", parents=[common])
    p.add_argument("--cluster")
    p.add_argument("--skill")
    p.set_defaults(func=cmd_show)

    p = sub.add_parser("set-threshold", parents=[common])
    p.add_argument("value", type=float)
    p.set_defaults(func=cmd_set_threshold)

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.state is None:
        args.state = _default_state_path(args.project_dir)
    if args.prefs is None:
        args.prefs = _default_prefs_path(args.project_dir)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
