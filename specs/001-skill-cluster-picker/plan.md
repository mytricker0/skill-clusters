# Implementation Plan: Skill Cluster Picker

**Branch**: `001-skill-cluster-picker` (working on `main`; no feature branch created) | **Date**: 2026-10-25 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-skill-cluster-picker/spec.md`

## Summary

A modular picker that discovers installed skills, classifies them into task-type clusters from their name and description, orders each cluster by a user preference file, and has the user choose before any member runs. An arranger files newly installed skills and records user corrections. Technical approach: a small stdlib-only Python package of five independent modules (discover, classify, rank, pick, arrange) behind a JSON-emitting CLI. A thin `SKILL.md` layer lets the agent call the CLI and handle the user prompt. Classification is deterministic keyword scoring over descriptions. See [research.md](research.md).

## Technical Context

**Language/Version**: Python 3.11+ (stdlib only; `tomllib` for preferences)

**Primary Dependencies**: None at runtime; `pytest` for tests

**Storage**: Files. `preferences.toml` (user-edited), `state.json` (memberships, machine-written), `CLUSTERS.md` (generated human-readable view)

**Testing**: pytest (unit per module, contract tests for CLI JSON, integration over a fixture skills tree)

**Target Platform**: Linux/macOS local agent environment (Claude Code skills layout)

**Project Type**: single project (library + CLI + skill wrapper)

**Performance Goals**: Discovery + classification of 500 skills in under 1 s; picker output readable in under 10 s (SC-002)

**Constraints**: Read-only on installed skills (FR-013); offline; no skill execution; MCP servers out of scope but the `Skill` entity carries a `kind` field so they can be added

**Scale/Scope**: Single user, tens to low hundreds of skills, under 20 clusters

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` is still the unfilled template (placeholders only), so it defines no enforceable gates. Result: **no violations possible, gate passes vacuously**. Recommendation: run `/speckit-constitution` before `/speckit-tasks`. The design is consistent with the principles that template usually suggests (library-first, CLI text I/O, test-first, simplicity). Post-design re-check: unchanged.

## Project Structure

### Documentation (this feature)

```text
specs/001-skill-cluster-picker/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── cli.md
│   └── preferences.schema.md
└── tasks.md             # NOT created by /speckit-plan
```

### Source Code (repository root)

```text
src/skill_clusters/
├── model.py        # Skill, Cluster, Membership, Preference, Pick dataclasses
├── discover.py     # find SKILL.md files (project + user), parse frontmatter
├── classify.py     # name/description -> clusters (keyword scoring), unclustered
├── rank.py         # apply preferences: order, exclude, cap
├── pick.py         # build the options list / record the selection
├── arrange.py      # diff discovery vs state, file new skills, persist corrections
├── store.py        # read/write state.json, preferences.toml, render CLUSTERS.md
└── cli.py          # entry point: discover | classify | options | arrange | correct | show

tests/
├── contract/
├── integration/
├── unit/
└── fixtures/skills/

.claude/skills/skill-cluster-picker/SKILL.md   # agent-facing wrapper that calls the CLI
```

**Structure Decision**: Single project. One module per spec'd concern (FR-011); modules exchange plain dataclasses and never import each other except through `model.py` and `store.py`, so any can be replaced. The existing `diagram-cluster` skill stays as the hand-written first cluster and is superseded once the picker can generate its list.

## Complexity Tracking

No constitution violations to justify.
