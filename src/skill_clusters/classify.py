"""Classify skills into task-type clusters and match requests to clusters.

Classification is deterministic keyword scoring over each skill's name and
description (no LLM, no skill execution). A request is matched to a cluster the
same way. See research.md "Request-to-cluster matching".
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

from .model import Cluster, Membership, Skill

WORD_RE = re.compile(r"[A-Za-z0-9]+")


def _tokenize(text: str) -> list[str]:
    return [t.lower() for t in WORD_RE.findall(text or "")]


def _score(text: str, keywords: dict[str, float], name_weight: float = 2.0) -> float:
    """Score ``text`` against keyword -> weight pairs.

    Matches in the name count ``name_weight`` times as often as matches in the
    description.
    """
    if not keywords:
        return 0.0
    combined = (text or "")
    tokens = _tokenize(combined)
    total = 0.0
    for kw, weight in keywords.items():
        kw_tokens = _tokenize(kw)
        for kt in kw_tokens:
            for token in tokens:
                if kt == token or kt.startswith(token) or token.startswith(kt):
                    total += weight
                    break
    return total


@dataclass
class ClassifyResult:
    memberships: list[Membership]
    unclustered: list[dict] = field(default_factory=list)  # {"name", "origin", "reason"}


def _default_clusters() -> list[Cluster]:
    """Keyword -> weight sets for the default clusters (lowercase slugs)."""
    return [
        Cluster(
            name="diagrams",
            keywords={
                "diagram": 2.0,
                "flowchart": 2.5,
                "architecture": 2.0,
                "sequence diagram": 2.5,
                "wireframe": 2.0,
                "mockup": 1.5,
                "uml": 2.0,
                "schematic": 2.0,
                "node": 0.5,
                "box": 0.5,
            },
        ),
        Cluster(
            name="video",
            keywords={
                "video": 2.5,
                "clip": 2.0,
                "animation": 2.0,
                "mp4": 2.0,
                "gif": 1.5,
                "render": 1.5,
                "timeline": 1.5,
                "footage": 2.0,
            },
        ),
        Cluster(
            name="research",
            keywords={
                "research": 2.5,
                "survey": 2.0,
                "literature review": 2.5,
                "citation": 2.0,
                "paper": 1.5,
                "evidence": 1.5,
                "source": 1.0,
                "analyze": 1.0,
            },
        ),
        Cluster(
            name="charts",
            keywords={
                "chart": 2.5,
                "graph": 2.5,
                "plot": 2.0,
                "dashboard": 2.0,
                "metric": 1.5,
                "statistic": 1.5,
                "bar": 1.0,
                "pie": 1.0,
            },
        ),
        Cluster(
            name="documents",
            keywords={
                "document": 2.5,
                "doc": 2.0,
                "report": 2.0,
                "markdown": 1.5,
                "writeup": 2.0,
                "outline": 1.5,
                "summary": 1.5,
                "notes": 1.0,
            },
        ),
        Cluster(
            name="code-review",
            keywords={
                "code review": 2.5,
                "review": 1.5,
                "audit": 2.0,
                "lint": 1.5,
                "refactor": 1.5,
                "pr": 1.5,
                "quality": 1.0,
                "bug": 1.0,
            },
        ),
    ]


def classify(
    skills: list[Skill],
    clusters: Optional[list[Cluster]] = None,
    threshold: float = 3.0,
) -> ClassifyResult:
    """Assign each skill to every cluster scoring above ``threshold``.

    An empty description yields ``no-description``; no cluster above threshold
    yields ``no-match``. Output is deterministic (sorted by name, then origin).
    """
    clusters = clusters or _default_clusters()
    memberships: list[Membership] = []
    unclustered: list[dict] = []
    for skill in sorted(skills, key=lambda s: (s.name, s.origin)):
        scored = sorted(
            ((c, _score(skill.name + " " + skill.description, c.keywords)) for c in clusters),
            key=lambda pair: (-pair[1], pair[0].name),
        )
        joined = False
        for cluster, score in scored:
            if score > threshold:
                memberships.append(
                    Membership(
                        skill=skill.name,
                        origin=skill.origin,
                        cluster=cluster.name,
                        score=round(score, 3),
                    )
                )
                joined = True
        if not joined:
            reason = "no-description" if not (skill.description or "").strip() else "no-match"
            unclustered.append({"name": skill.name, "origin": skill.origin, "reason": reason})
    return ClassifyResult(memberships=memberships, unclustered=unclustered)


def match_request(text: str, clusters: Optional[list[Cluster]] = None, margin: float = 0.5) -> dict:
    """Score the request against each cluster keyword set.

    Returns one clear winner, or an ``ambiguous`` list (cluster null) when two
    clusters score within ``margin`` of each other, or ``None`` when nothing
    clears the threshold.
    """
    clusters = clusters or _default_clusters()
    scored = [
        (c, _score(text, c.keywords)) for c in clusters
    ]
    scored = [(c, s) for c, s in scored if s > 0]
    if not scored:
        return {"cluster": None, "ambiguous": []}
    scored.sort(key=lambda pair: (-pair[1], pair[0].name))
    top = scored[0]
    if len(scored) == 1 or top[1] - scored[1][1] >= margin:
        return {"cluster": top[0].name, "ambiguous": []}
    tied = [c.name for c, s in scored if abs(s - top[1]) <= margin]
    return {"cluster": None, "ambiguous": tied}
