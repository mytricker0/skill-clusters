"""State storage, preference loading, and CLUSTERS.md rendering.

State lives in ``state.json`` (memberships, machine-written). Preferences live
in a TOML file the user edits. ``CLUSTERS.md`` is a generated human-readable
view next to ``state.json``. Never write inside any skill directory (FR-013).
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Optional

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None

from .model import DEFAULT_THRESHOLD, Cluster, Membership


@dataclass
class State:
    memberships: list[Membership]
    proposed_clusters: list[Cluster] = None  # type: ignore[assignment]
    threshold: float = DEFAULT_THRESHOLD


def _default_state() -> State:
    return State(memberships=[], proposed_clusters=[], threshold=DEFAULT_THRESHOLD)


def load_state(path: str) -> State:
    """Read ``state.json``. A missing file returns empty state."""
    if not os.path.isfile(path):
        return _default_state()
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return _default_state()
    memberships = [
        Membership(
            skill=m.get("skill", ""),
            origin=m.get("origin", ""),
            cluster=m.get("cluster", ""),
            score=float(m.get("score", 0) or 0),
            source=m.get("source", "auto"),
            removed=bool(m.get("removed", False)),
        )
        for m in data.get("memberships", [])
    ]
    proposed = [
        Cluster(name=c.get("name", ""), proposed=bool(c.get("proposed", False)))
        for c in data.get("proposed_clusters", [])
    ]
    threshold = float(data.get("threshold", DEFAULT_THRESHOLD) or DEFAULT_THRESHOLD)
    return State(memberships=memberships, proposed_clusters=proposed, threshold=threshold)


def save_state(path: str, memberships: list[Membership], proposed_clusters: Optional[list[Cluster]] = None, threshold: float = DEFAULT_THRESHOLD) -> None:
    """Write ``state.json``. Never writes inside a skill directory."""
    data = {
        "threshold": threshold,
        "memberships": [
            {
                "skill": m.skill,
                "origin": m.origin,
                "cluster": m.cluster,
                "score": m.score,
                "source": m.source,
                "removed": m.removed,
            }
            for m in memberships
        ],
        "proposed_clusters": [
            {"name": c.name, "proposed": c.proposed} for c in proposed_clusters or []
        ],
    }
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def load_preferences(path: str) -> tuple[dict, list[str]]:
    """Read a TOML preferences file.

    Missing file gives empty prefs and no warnings. Invalid TOML or wrong value
    types give warnings but never raise. Returns ``(preferences, warnings)``.
    """
    warnings: list[str] = []
    if not os.path.isfile(path):
        return {}, warnings
    if tomllib is None:  # pragma: no cover
        return {}, ["tomllib unavailable; preferences ignored"]
    try:
        with open(path, "rb") as fh:
            data = tomllib.load(fh)
    except ValueError as exc:
        return {}, [f"{path}: {exc}"]
    prefs: dict = {}
    for table, key in (
        ("global", "favor"),
        ("global", "disfavor"),
        ("global", "exclude"),
    ):
        section = data.get(table)
        if not isinstance(section, dict):
            continue
        values = section.get(key)
        if values is None:
            continue
        if not isinstance(values, list):
            warnings.append(f"{path}: [{table}] {key} should be a list of strings")
            continue
        if not all(isinstance(v, str) for v in values):
            warnings.append(f"{path}: [{table}] {key} must contain only strings")
            continue
        prefs.setdefault(table, {})[key] = values
    for cluster_name, section in data.get("clusters", {}).items():
        if not isinstance(section, dict):
            warnings.append(f"{path}: [clusters.{cluster_name}] should be a table")
            continue
        for key in ("favor", "disfavor", "exclude"):
            values = section.get(key)
            if values is None:
                continue
            if not isinstance(values, list) or not all(isinstance(v, str) for v in values):
                warnings.append(f"{path}: [clusters.{cluster_name}] {key} should be a list of strings")
                continue
            prefs.setdefault("clusters", {}).setdefault(cluster_name, {})[key] = values
    return prefs, warnings


def render_clusters_md(memberships: list[Membership], clusters: list[str], path: str) -> None:
    """Write ``CLUSTERS.md`` next to ``state.json`` listing each cluster's members.

    FR-012. Shows member name, origin and ``auto``/``user`` source, plus an
    Unclustered section.
    """
    lines = ["# Skill Clusters", "", "_Generated by skill-clusters. Do not edit by hand._", ""]
    for cluster in clusters:
        lines.append(f"## {cluster}")
        rows = [m for m in memberships if m.cluster == cluster and not m.removed]
        if not rows:
            lines.append("- (none)")
        else:
            for m in sorted(rows, key=lambda x: (x.skill, x.origin)):
                lines.append(f"- {m.skill} (`{m.origin}`) — {m.source}")
        lines.append("")
    if not clusters:
        lines.append("## (no clusters)")
        lines.append("")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
