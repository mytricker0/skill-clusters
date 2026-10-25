"""Apply preferences to an ordered options list.

Ordering: favor (in listed order) then default order then disfavor; drops
excluded; applies cluster-level-over-global and project-over-user precedence.
"""

from __future__ import annotations

from typing import Optional

from .model import Preference


def _pref(prefs: dict, cluster: Optional[str], key: str) -> tuple[dict, list[str]]:
    """Return the merged favor/disfavor/exclude list for ``key`` at one level."""
    global_section = prefs.get("global", {})
    global_list = global_section.get(key, [])
    cluster_section = {}
    if cluster:
        cluster_section = prefs.get("clusters", {}).get(cluster, {})
    cluster_list = cluster_section.get(key, [])
    return cluster_list, global_list


def apply_preferences(options: list[dict], prefs: dict, cluster: Optional[str], installed: set) -> tuple[list[dict], list[str]]:
    """Reorder ``options`` by preference, drop excluded ones.

    ``installed`` is the set of real skill names (to ignore unknown names).
    Returns ``(ordered, warnings)``.
    """
    warnings: list[str] = []
    if not options:
        return options, warnings

    favor_cluster, favor_global = _pref(prefs, cluster, "favor")
    disfavor_cluster, disfavor_global = _pref(prefs, cluster, "disfavor")
    exclude_cluster, exclude_global = _pref(prefs, cluster, "exclude")

    all_favor = favor_cluster + favor_global
    disfavor_all = disfavor_cluster + disfavor_global
    exclude_all = exclude_cluster + exclude_global

    preferred = [s for s in all_favor if s in installed]
    disfavored = [s for s in disfavor_all if s in installed]
    excluded = set(s for s in exclude_all if s in installed)

    for name in all_favor + disfavor_all + exclude_all:
        if name not in installed and name not in warnings:
            warnings.append(f"preference for unknown skill '{name}' ignored")

    def sort_key(opt: dict):
        name = opt["name"]
        if name in preferred:
            return (0, preferred.index(name), name)
        if name in disfavored:
            return (2, disfavored.index(name), name)
        return (1, 0, name)

    ordered = sorted(options, key=sort_key)
    ordered = [o for o in ordered if o["name"] not in excluded]
    return ordered, warnings
