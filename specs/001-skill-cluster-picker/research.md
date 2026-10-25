# Research: Skill Cluster Picker

All Technical Context items were resolved; no NEEDS CLARIFICATION remain.

## Language and dependencies
- **Decision**: Python 3.11+, stdlib only.
- **Rationale**: `tomllib`, `json`, `pathlib`, `re` cover everything; no install step for a skill tool.
- **Alternatives**: Node/TypeScript (extra toolchain); Bash (poor frontmatter parsing, hard to test).

## Skill discovery
- **Decision**: Scan `<project>/.claude/skills/*/SKILL.md` and `~/.claude/skills/*/SKILL.md`; parse YAML-subset frontmatter (`name`, `description`) with a small hand-written parser. Origin = `project` or `user`. Same name in both is kept as two entries (spec edge case).
- **Rationale**: Matches the layout in this repo. Frontmatter is flat key/value, so a full YAML parser is unnecessary.
- **Alternatives**: PyYAML (dependency); asking the agent for its skill list (not scriptable or testable).

## Classification
- **Decision**: Deterministic keyword scoring. Each default cluster has a keyword set; score = weighted matches in name (x2) and description. A skill joins every cluster scoring above a threshold; none above it means unclustered. Empty description means unclustered. Default clusters: diagrams, video, research, charts, documents, code-review.
- **Rationale**: Reproducible, offline, testable against a reference set for SC-003, and never executes skills. The arranger's user corrections cover misses.
- **Alternatives**: LLM classification (non-deterministic, cost, hard to test; could be a pluggable classifier later via the module boundary); embeddings (heavy dependency).

## Preferences
- **Decision**: One TOML file. User-level `~/.config/skill-clusters/preferences.toml`, project-level `.skill-clusters/preferences.toml` overriding it. Sections: `[favor]`, `[disfavor]`, `[exclude]` as lists of skill names, optionally per cluster (`[clusters.diagrams]`).
- **Rationale**: Stdlib reads TOML; human-editable; supports project override per spec assumption. Parse errors report file, line, and message, then fall back to defaults (FR-007).
- **Alternatives**: YAML (needs a dependency); JSON (no comments).

## State and human-readable view
- **Decision**: `state.json` holds memberships with `source: auto|user`. After each arrange, render `CLUSTERS.md` (cluster -> members, origin, source). User corrections are stored with `source: user` and never overwritten by auto runs (FR-010).
- **Rationale**: Satisfies FR-012 and SC-006 with a file the user can open; separates machine state from user-edited preferences.
- **Alternatives**: Single file for both (users would edit machine state by hand).

## Picker integration and deferral
- **Decision**: A `skill-cluster-picker` SKILL.md tells the agent to run `skill-clusters options --request "<text>"`, show the returned list, wait for the choice, then invoke only that skill. Deferral of member skills is a documented convention plus an `arrange --annotate` follow-up that is explicitly NOT done in v1, because FR-013 forbids modifying installed skills.
- **Rationale**: Stays within FR-013. Risk: members can still self-trigger; the picker description should be written to win routing for cluster requests. Flag for tasks phase.
- **Alternatives**: Editing member frontmatter to `disable-model-invocation` (violates FR-013).

## Request-to-cluster matching
- **Decision**: Score the request text against the same cluster keyword sets. One clear winner returns it; a tie within a margin returns the ambiguity so the agent asks which task type (spec edge case).
- **Rationale**: Reuses the classifier; no extra model.

## List capping
- **Decision**: Show top 7 by default; `--all` returns the rest.
