"""Discover installed skills: find SKILL.md files (project + user dirs), parse frontmatter.

Read-only on skills (FR-013). A hand-written parser handles flat frontmatter
(``name`` and ``description``, including quoted values and simple multi-line
folded descriptions).
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from .model import Skill


def _parse_frontmatter(text: str) -> dict[str, str]:
    """Parse a flat YAML-like frontmatter block.

    Only the keys we need (``name`` and ``description``) are extracted. Handles
    quoted values and simple multi-line folded descriptions (``>`` and ``|``).
    """
    fm: dict[str, str] = {}
    lines = text.splitlines()
    # Skip the opening ``---`` if present.
    if lines and lines[0].strip() == "---":
        lines = lines[1:]
    end = len(lines)
    for i, line in enumerate(lines):
        if line.strip() == "---" and i > 0:
            end = i
            break
    for line in lines[:end]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        if value.startswith(">") or value.startswith("|"):
            # Folded/literal block: join subsequent indented lines.
            folded: list[str] = []
            i = lines.index(line) + 1
            indent = len(line) - len(line.lstrip()) + 4
            while i < len(lines):
                nxt = lines[i]
                if not nxt.strip():
                    folded.append("")
                    i += 1
                    continue
                if len(nxt) - len(nxt.lstrip()) < indent and not nxt.lstrip().startswith((" ", "\t")):
                    break
                folded.append(nxt.lstrip())
                i += 1
            value = " ".join(folded).strip()
        elif value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        elif value.startswith("'") and value.endswith("'"):
            value = value[1:-1]
        fm[key] = value
    return fm


def _discover_in_root(root: str, origin: str) -> list[Skill]:
    """Discover skills directly under ``root/*/SKILL.md``."""
    skills: list[Skill] = []
    if not os.path.isdir(root):
        return skills
    for entry in sorted(os.listdir(root)):
        skill_dir = os.path.join(root, entry)
        if not os.path.isdir(skill_dir):
            continue
        skill_file = os.path.join(skill_dir, "SKILL.md")
        if not os.path.isfile(skill_file):
            continue
        try:
            with open(skill_file, "r", encoding="utf-8") as fh:
                text = fh.read()
        except (OSError, UnicodeDecodeError):
            continue
        fm = _parse_frontmatter(text)
        name = fm.get("name")
        if not name:
            continue
        skills.append(
            Skill(
                name=name,
                description=fm.get("description", ""),
                origin=origin,
                kind="skill",
                path=os.path.relpath(skill_file, start=root),
            )
        )
    return skills


def discover(project_dir: str, user_dir: str) -> list[Skill]:
    """Discover installed skills from project and user locations.

    Project skills live under ``<project_dir>/.claude/skills/*/SKILL.md`` and
    user skills under ``<user_dir>/*/SKILL.md``. A missing directory is not an
    error. A skill with no ``name`` frontmatter is skipped.
    """
    skills: list[Skill] = []
    project_root = os.path.join(project_dir, ".claude", "skills")
    skills.extend(_discover_in_root(project_root, "project"))
    skills.extend(_discover_in_root(user_dir, "user"))
    return skills
