---
name: "diagram-cluster"
description: "Propose diagram options for a request; user picks one before it is built."
compatibility: "Works with any integration. First member of the diagrams skill cluster."
metadata:
  author: "mytricker0"
  source: "skill-clusters"
user-invocable: true
disable-model-invocation: false
---

## Purpose

A cluster = one small "picker" that lists diagram members (skills + MCP servers),
when to use each, and how to run it. When the user asks for a diagram, propose
the members and let them pick. Do NOT build one silently.

## Members

| Member | What it is | Use when |
|--------|-----------|----------|
| `diagram-design` | Hand-drawn / ASCII style diagrams | quick sketches, mockups, ASCII art |
| `architecture-diagram` | Dark-themed SVG architecture/cloud diagrams | infra, cloud, system architecture |
| Excalidraw MCP | Excalidraw whiteboard (MCP server) | interactive, collaborative, hand-drawn-ish diagrams |
| `baoyu-infographic` | 21 layouts x 21 styles (信息图, 可视化) | polished infographics, data visualization |
| `manim-video` | Manim CE math animations | animated math / algorithm explainer videos |

## How to run

1. Read the request. Map it to the table above.
2. Propose the matching member(s) in ONE short line each (what it does + when to use).
3. Ask the user to pick. Wait for the choice.
4. After picking, follow that member's own skill/commands to build.

## Delegation

Member skills defer to this picker: when the user asks for a diagram, surface the
cluster first, do not fire the member directly. If a request clearly fits one
member and the user already picks that member, proceed.

## Open items

- Only the diagrams cluster is implemented. Add more clusters (video, research,
  charts) by copying this SKILL.md and listing their members.
- `architecture-diagram`, `baoyu-infographic`, `manim-video` are referenced by
  name; confirm each is installed before promising it.
