"""Data types shared across the skill-cluster modules.

Modules exchange these dataclasses and import each other only through
``model.py`` and ``store.py`` (FR-011).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Skill:
    name: str
    description: str
    origin: str  # "project" | "user"
    kind: str = "skill"  # "skill" | "mcp" (only "skill" in v1)
    path: str = ""

    def identity(self) -> tuple[str, str]:
        return (self.origin, self.name)


@dataclass
class Cluster:
    name: str  # unique, lowercase slug
    keywords: dict[str, float] = field(default_factory=dict)
    proposed: bool = False


@dataclass
class Membership:
    skill: str
    origin: str
    cluster: str
    score: float = 0.0
    source: str = "auto"  # "auto" | "user"
    removed: bool = False


@dataclass
class Preference:
    skill: str
    action: str  # "favor" | "disfavor" | "exclude"
    cluster: Optional[str] = None
    level: str = "user"  # "user" | "project"


@dataclass
class Pick:
    request: str
    cluster: Optional[str]
    options: list = field(default_factory=list)
    selection: Optional[str] = "none"
