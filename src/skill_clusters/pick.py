"""Build the options list for a request and apply preferences.

``build_options`` produces the cluster, ambiguous, single, options, hidden_count
and warnings structure. Default order is score descending then name; capped at
7 by default, with ``show_all`` returning the rest.
"""

from __future__ import annotations

from typing import Optional

from .classify import match_request
from .model import Cluster, Membership
from .rank import apply_preferences


def _one_line(description: str) -> str:
    text = (description or "").strip()
    if not text:
        return "(no description)"
    first = text.splitlines()[0]
    if len(first) > 120:
        first = first[:117] + "..."
    return first


def build_options(
    request: str,
    skills: list,
    memberships: list[Membership],
    clusters: Optional[list[Cluster]],
    prefs: dict,
    show_all: bool = False,
) -> dict:
    """Build the ranked options list for ``request``.

    ``memberships`` may be auto-classified or user-corrected; ``skills`` is the
    full discovered set (used to look up descriptions/origins).
    """
    match = match_request(request, clusters)
    cluster_name = match.get("cluster")
    ambiguous = match.get("ambiguous", [])

    if cluster_name:
        cluster_members = [m for m in memberships if m.cluster == cluster_name and not m.removed]
    else:
        cluster_members = []

    skill_by_name = {s.name: s for s in skills}
    options = [
        {
            "name": m.skill,
            "description": _one_line(skill_by_name.get(m.skill, "").description),
            "origin": m.origin,
        }
        for m in sorted(cluster_members, key=lambda x: (-x.score, x.skill, x.origin))
    ]

    hidden_count = 0
    if options and not show_all:
        hidden_count = max(0, len(options) - 7)
        options = options[:7]

    ordered, pref_warnings = apply_preferences(options, prefs, cluster_name, {s.name for s in skills})

    return {
        "cluster": cluster_name,
        "ambiguous": ambiguous,
        "single": len(ordered) == 1 and not ambiguous,
        "options": ordered,
        "hidden_count": hidden_count,
        "warnings": pref_warnings,
    }
