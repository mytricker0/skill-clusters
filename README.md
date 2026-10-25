# skill-clusters

Group similar agent skills and MCP servers into clusters by task type. When you
start a project or ask for something, the picker discovers the skills installed
on your machine, classifies them into task-type clusters, ranks them by your
preference, and asks you to pick before any member runs.

## Why

Agent skill ecosystems grow fast. You end up with dozens of skills and no idea
which one to reach for when a task comes up. `skill-clusters` gives you:

- **Discovery** — find every skill installed on your machine.
- **Classification** — group them into task-type clusters (diagrams, video,
  research, charts, documents, code-review, ...) with deterministic keyword
  scoring. No LLM, no skill execution, reproducible.
- **Preferences** — order members by what you prefer, set once in a TOML file.
- **Arrangement** — auto-file newly installed skills into their cluster and
  record your corrections.
- **Picking** — ask *you* which skill to use before any member runs.

## Install

```bash
pip install -e .
```

Requires Python 3.11+ (stdlib only; `tomllib` for preferences). No third-party
dependencies. For the test suite:

```bash
pip install -e .[test]
```

## Quickstart

```bash
# Discover installed skills
skill-clusters discover \
  --project-dir . \
  --user-dir ~/.claude/skills

# Classify into clusters
skill-clusters classify \
  --project-dir . \
  --user-dir ~/.claude/skills

# Pick from a cluster (ask the user before running anything)
skill-clusters options \
  --request "draw a diagram of this flow" \
  --project-dir . \
  --user-dir ~/.claude/skills

# Arrange newly installed skills into clusters
skill-clusters arrange \
  --project-dir . \
  --user-dir ~/.claude/skills

# Correct a filing (permanent user override)
skill-clusters correct new-skill --cluster research

# Inspect a cluster
skill-clusters show --cluster diagrams
```

### Common flags

| Flag | Default | Meaning |
|------|---------|---------|
| `--project-dir` | cwd | Where to scan for project skills. |
| `--user-dir` | `~/.claude/skills` | Where to scan for user skills. |
| `--state` | `.skill-clusters/state.json` | State file path. |
| `--prefs` | `.skill-clusters/preferences.toml` | Preferences file path. |
| `--format` | `json` | `json` or `human`. |

Exit codes: `0` ok, `1` usage error, `2` recoverable problem reported in output
(e.g. bad preferences).

### Threshold knob

Classification uses a threshold (default `3.0`). Raise it to make classification
stricter (fewer members), lower it to be more inclusive. The value persists in
`state.json`:

```bash
# Set a custom threshold
skill-clusters set-threshold 5.0

# Or pass one-off
skill-clusters classify --threshold 4.5
```

## Concepts

### Cluster

A task type. Each default cluster has a keyword set; a skill joins every cluster
scoring above the threshold. A single skill may join several clusters.

### Membership

A skill joined to a cluster. Memberships carry a `source`:

- `auto` — filed by classification or the arranger.
- `user` — a permanent correction made with `correct`.

### Preference

A TOML file that orders members by preference. `favor` sorts first, `disfavor`
sorts last, `exclude` removes.

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

- Cluster-level preferences override global.
- Project-level preferences override user-level.
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
every cluster scoring above the threshold; it may join several. An empty
description yields `no-description`; nothing above threshold yields `no-match`.

## Self-triggering limitation

The picker's `description` is written to win routing for cluster-type requests,
but it does not modify the member skills it lists (FR-013). If a member skill
also fires independently, you still pick first here.

## Development

```bash
pip install -e .[test]
pytest
```

Tests are organized into unit (per module), contract (CLI JSON shape), and
integration (end-to-end over a fixture tree) suites.

## License

MIT. See [LICENSE](LICENSE).
