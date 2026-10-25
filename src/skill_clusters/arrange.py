"""Diff discovery against saved state, file new skills, persist corrections.

``arrange`` reports what it filed, reports unclustered skills, proposes a new
cluster when a skill matches none but several unclustered skills share
keywords, drops memberships of skills no longer on disk, preserves
``source: user`` memberships and ``removed: true`` markers, and never touches
any skill path.
"""

from __future__ import annotations

import os
from collections import Counter
from typing import Optional

from .classify import _default_clusters as _default_clusters_fn, _tokenize, classify
from .model import DEFAULT_THRESHOLD, Cluster, Membership, Skill
from .store import State, render_clusters_md, save_state


def _candidate_clusters(unclustered_skills: list[Skill], clusters: list[Cluster]) -> list[Cluster]:
    """Propose a new cluster when several unclustered skills share keywords."""
    if len(unclustered_skills) < 2:
        return []
    counter: Counter = Counter()
    for skill in unclustered_skills:
        counter.update(_tokenize(skill.name + " " + skill.description))
    common = {w for w, c in counter.most_common() if c >= 2 and len(w) >= 4}
    if not common:
        return []
    return [Cluster(name=sorted(common)[0], keywords={w: 1.0 for w in common}, proposed=True)]


def arrange(
    skills: list[Skill],
    state: State,
    clusters: Optional[list[Cluster]] = None,
    dry_run: bool = False,
    state_path: str = "state.json",
    threshold: float = DEFAULT_THRESHOLD,
) -> dict:
    """Diff discovery against saved state and file new skills."""
    clusters = clusters or _default_clusters_fn()
    new_memberships = classify(skills, clusters, threshold).memberships
    new_names = {m.skill for m in new_memberships}

    filed: list[dict] = []
    for m in new_memberships:
        existing = next((x for x in state.memberships if x.skill == m.skill and x.cluster == m.cluster), None)
        if existing is None:
            filed.append({"skill": m.skill, "cluster": m.cluster})

    unclustered = [
        {"name": s.name, "origin": s.origin, "reason": "unclustered"}
        for s in skills
        if s.name not in {m.skill for m in new_memberships}
    ]

    removed = [
        {"name": m.skill, "origin": m.origin}
        for m in state.memberships
        if not m.removed and m.skill not in new_names
    ]

    proposed_clusters = _candidate_clusters(
        [s for s in skills if s.name not in new_names], clusters
    )

    if not dry_run:
        for f in filed:
            state.memberships.append(
                Membership(
                    skill=f["skill"],
                    origin="auto",
                    cluster=f["cluster"],
                    score=0.0,
                    source="auto",
                )
            )
        for r in removed:
            membership = next((x for x in state.memberships if x.skill == r["name"]), None)
            if membership:
                membership.removed = True
        state.proposed_clusters = proposed_clusters
        render_clusters_md(state.memberships, [c.name for c in clusters], "CLUSTERS.md")
        save_state(state_path, state.memberships, state.proposed_clusters, state.threshold)

    return {
        "filed": filed,
        "unclustered": unclustered,
        "proposed_clusters": [{"name": c.name, "skills": []} for c in proposed_clusters],
        "removed": removed,
    }


def correct(
    skill: str,
    cluster: str,
    remove: bool = False,
    confirm_cluster: bool = False,
    state: Optional[State] = None,
    clusters: Optional[list[Cluster]] = None,
    state_path: str = "state.json",
) -> dict:
    """Record a ``source: user`` membership (or removal).

    ``--remove`` marks a membership removed; ``--confirm-cluster`` confirms a
    proposed cluster. Persists via store.save_state.
    """
    clusters = clusters or _default_clusters_fn()
    if state is None:
        state = State(memberships=[], proposed_clusters=[])
    if confirm_cluster:
        for c in state.proposed_clusters:
            if c.name == cluster:
                c.proposed = False
        state.proposed_clusters = [c for c in state.proposed_clusters if not c.proposed]
        save_state(state_path, state.memberships, state.proposed_clusters, state.threshold)
        render_clusters_md(state.memberships, [c.name for c in clusters], "CLUSTERS.md")
        return {"corrected": {"cluster": cluster, "confirmed": True}}
    membership = next((x for x in state.memberships if x.skill == skill and x.cluster == cluster), None)
    if membership:
        membership.source = "user"
        membership.removed = remove
    else:
        membership = Membership(
            skill=skill, origin="user", cluster=cluster, score=0.0, source="user", removed=remove
        )
        state.memberships.append(membership)
    save_state(state_path, state.memberships, state.proposed_clusters, state.threshold)
    render_clusters_md(state.memberships, [c.name for c in clusters], "CLUSTERS.md")
    return {
        "skill": skill,
        "cluster": cluster,
        "source": "user",
        "removed": remove,
    }
