# skill-clusters

Group similar agent skills and MCP servers into clusters by task type. When you
start a project or ask for something, the picker discovers the skills installed
on your machine, classifies them into task-type clusters, ranks them by your
preference, and asks you to pick before any member runs.

## Idea

- A **cluster** = a task type (diagrams, video, research, charts, documents,
  code-review, ...).
- Discovery scans `<project>/.claude/skills/` and `~/.claude/skills/`.
- Classification is deterministic keyword scoring over each skill's name and
  description — no LLM, no skill execution.
- A user **preference file** orders members by preference; you set it once.
- The **arranger** auto-files newly installed skills into their cluster and
  records your corrections.
- The **picker** (`options`) asks you to pick before any member runs.

## Install

```bash
pip install -e .[test]
```

Requires Python 3.11+ (stdlib only; `tomllib` for preferences).

## Usage

```bash
# Discover installed skills
skill-clusters discover --project-dir . --user-dir ~/.claude/skills

# Classify into clusters
skill-clusters classify --project-dir . --user-dir ~/.claude/skills

# Pick from a cluster (ask the user before running anything)
skill-clusters options --request "draw a diagram of this flow" --project-dir . --user-dir ~/.claude/skills

# Arrange newly installed skills into clusters
skill-clusters arrange --project-dir . --user-dir ~/.claude/skills

# Correct a filing (permanent user override)
skill-clusters correct new-skill --cluster research

# Inspect a cluster
skill-clusters show --cluster diagrams
```

Common flags: `--project-dir` (default cwd), `--user-dir` (default
`~/.claude/skills`), `--state` (state file path), `--prefs` (preferences file
path), `--format json|human`. Exit codes: `0` ok, `1` usage error, `2`
recoverable problem reported in output (e.g. bad preferences).

## Preferences

A TOML file with `[global]` and `[clusters.<name>]` tables:

```toml
[global]
favor = ["diagram-b"]
disfavor = ["video-maker"]
exclude = ["old-skill"]

[clusters.diagrams]
favor = ["architecture-diagram"]
```

- `favor` orders first, `disfavor` orders last, `exclude` removes.
- Cluster-level preferences override global; project-level override user-level.
- Project file: `<project>/.skill-clusters/preferences.toml`
- User file: `~/.config/skill-clusters/preferences.toml`
- Invalid TOML or unknown keys produce a `warnings` entry and fall back to
  defaults (exit code `2`).

## State

- `state.json` — memberships (source, removed, score), machine-written.
- `CLUSTERS.md` — generated human-readable view of each cluster's members.
- `arrange` writes both; `--dry-run` shows without writing.

## How classification works

Each skill's name is weighted twice as heavily as its description. A skill joins
every cluster scoring above a threshold (default 3.0); it may join several. An
empty description yields `no-description`; nothing above threshold yields
`no-match`.

## Self-triggering limitation

The picker's `description` is written to win routing for cluster-type requests,
but it does not modify the member skills it lists (FR-013). If a member skill
also fires independently, you still pick first here.

## Tests

```bash
pytest
```

Unit (per module), contract (CLI JSON shape), and integration (end-to-end over a
fixture tree) tests.
