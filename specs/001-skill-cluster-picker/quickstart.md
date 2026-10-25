# Quickstart: validating the Skill Cluster Picker

Prerequisites: Python 3.11+, `pip install -e .[test]`. Use the fixture tree in `tests/fixtures/skills/` (three diagram skills, one video skill, one with an empty description). Contracts: [cli.md](contracts/cli.md), [preferences.schema.md](contracts/preferences.schema.md). Entities: [data-model.md](data-model.md).

## 1. Discovery and classification (US2)
```bash
skill-clusters classify --project-dir tests/fixtures --user-dir /nonexistent
```
Expect: diagram skills under `diagrams`, the video skill under `video`, the empty-description skill listed as `unclustered` with reason `no-description`.

## 2. Pick from a cluster (US1)
```bash
skill-clusters options --request "draw a diagram of this flow" --project-dir tests/fixtures
```
Expect: `cluster: diagrams`, three options with name, one-line description, origin; `single: false`. A request matching a one-member cluster returns `single: true`.

## 3. Preferences (US3)
Copy `tests/fixtures/preferences/favor-b.toml` to `.skill-clusters/preferences.toml`, rerun step 2: B listed first. Add B to `exclude`: B absent. Remove the file: default order, no error. Put invalid TOML in it: output has a `warnings` entry naming the problem, exit code 2, default order.

## 4. Arranger (US4)
```bash
skill-clusters arrange --dry-run     # shows what would be filed
skill-clusters arrange               # writes state.json and CLUSTERS.md
skill-clusters correct new-skill --cluster research
skill-clusters arrange               # correction persists
```
Expect: newly added fixture skill reported as filed with its cluster; after `correct`, later arranges keep it in `research`; `git status` shows no changes under any skill directory (FR-013).

## 5. Inspect (SC-006)
```bash
skill-clusters show --skill new-skill
```
Expect: its cluster(s) and whether set automatically or by user.

## 6. Test suite
```bash
pytest
```
Expect: unit, contract (CLI JSON shape), and integration tests all pass.
