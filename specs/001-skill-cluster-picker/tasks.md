# Tasks: Skill Cluster Picker

**Input**: Design documents from `/specs/001-skill-cluster-picker/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/cli.md, contracts/preferences.schema.md, quickstart.md

**Tests**: Included. plan.md specifies pytest unit, contract (CLI JSON shape) and integration tests, and quickstart.md step 6 expects them to pass. Write each story's tests first and confirm they fail before implementing.

**Organization**: Grouped by user story. US1 and US2 are both P1, but US1's `options` command needs the classifier from US2, so US2 is built first (Phase 3) and US1 follows (Phase 4).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: US1-US4, mapping to spec.md
- Paths are relative to the repository root `/home/zeta/dev/skill-clusters`

## Path Conventions

Single project: `src/skill_clusters/`, `tests/{unit,contract,integration,fixtures}/`. Modules exchange plain dataclasses and import each other only through `model.py` and `store.py` (FR-011).

---

## Phase 1: Setup

**Purpose**: Project scaffolding

- [ ] T001 Create `pyproject.toml` at the repo root: package `skill-clusters`, `requires-python = ">=3.11"`, no runtime dependencies, optional extra `test = ["pytest"]`, console script `skill-clusters = "skill_clusters.cli:main"`, `src` layout, pytest `testpaths = ["tests"]`
- [ ] T002 Create the empty package and test directories: `src/skill_clusters/__init__.py`, `tests/unit/`, `tests/contract/`, `tests/integration/`, `tests/fixtures/` (add `__init__.py` or `conftest.py` only where pytest needs it)
- [ ] T003 [P] Create the fixture skills tree under `tests/fixtures/.claude/skills/` (so `--project-dir tests/fixtures` works as quickstart.md uses it, since discovery scans `<project>/.claude/skills/*/SKILL.md`). Each skill is `<name>/SKILL.md` with `name:` and `description:` frontmatter. Add: three diagram skills (`diagram-a`, `diagram-b`, `diagram-c`, descriptions mentioning diagrams/flowcharts/architecture), one video skill (`video-maker`), one skill with an empty `description:` (`no-desc`), and a `new-skill` directory kept OUTSIDE the tree at `tests/fixtures/extra/new-skill/SKILL.md` (a research-type skill that tests copy in to simulate a new install)
- [ ] T004 [P] Create preference fixtures: `tests/fixtures/preferences/favor-b.toml` (`[global] favor = ["diagram-b"]`), `tests/fixtures/preferences/exclude-b.toml` (`[global] exclude = ["diagram-b"]`), `tests/fixtures/preferences/invalid.toml` (deliberately broken TOML)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared types, storage, and CLI skeleton that every story uses

**CRITICAL**: No story work starts until this phase is complete

- [ ] T005 Implement dataclasses in `src/skill_clusters/model.py` per data-model.md:
  - `Skill(name, description, origin, kind, path)` with `origin: "project"|"user"`, `kind: "skill"|"mcp"` (only `skill` used in v1), identity `(origin, name)`; `description` may be empty
  - `Cluster(name, keywords: dict[str,float], proposed: bool)` where `name` is a "unique, lowercase slug"
  - `Membership(skill, cluster, source: "auto"|"user", score: float, removed: bool=False)`; "`user` always wins over `auto`"; a user-removed membership is stored as `source: user, removed: true`
  - `Preference(skill, action: "favor"|"disfavor"|"exclude", cluster: optional, level: "user"|"project")`
  - `Pick(request, cluster, options: list of {name, description, origin}, selection: name|"none")`; not persisted in v1
- [ ] T006 Implement state storage in `src/skill_clusters/store.py`: `load_state(path)` / `save_state(path, memberships, proposed_clusters)` reading and writing `state.json` (memberships with `source`, `removed`, `score`); a missing file returns empty state; default path configurable via the CLI `--state` flag. Never write inside any skill directory (FR-013)
- [ ] T007 Implement the CLI skeleton in `src/skill_clusters/cli.py`: `main(argv)` with argparse subcommands `discover|classify|options|arrange|correct|show` (handlers stubbed), common flags `--project-dir` (default cwd), `--user-dir` (default `~/.claude/skills`), `--state`, and `--format json|human` (default json). JSON on stdout, problems on stderr. Exit codes per contracts/cli.md: 0 ok, 1 usage error, 2 recoverable problem reported in output
- [ ] T008 [P] Add `tests/conftest.py` with fixtures: path to `tests/fixtures`, a helper that runs `cli.main` and captures stdout/stderr/exit code, and a `tmp_path`-based copy of the fixtures tree for tests that mutate skills

**Checkpoint**: Foundation ready

---

## Phase 3: User Story 2 - Automatic discovery and classification (Priority: P1)

**Goal**: Find installed skills (project and user level) and assign each to task-type clusters or mark it unclustered.

**Independent Test**: `skill-clusters classify --project-dir tests/fixtures --user-dir /nonexistent` puts the three diagram skills under `diagrams`, the video skill under `video`, and lists `no-desc` as unclustered with reason `no-description`.

### Tests for User Story 2

- [ ] T009 [P] [US2] Unit tests in `tests/unit/test_discover.py`: finds `*/SKILL.md` under project and user dirs; parses flat `name`/`description` frontmatter; same name in both origins yields two Skills labeled by origin; a missing user dir is not an error; a skill with no frontmatter or no `name` is skipped without crashing
- [ ] T010 [P] [US2] Unit tests in `tests/unit/test_classify.py`: name matches count x2 versus description matches; a skill above the threshold joins every cluster it scores for (multi-cluster allowed); empty description gives unclustered with reason `no-description`; no cluster above threshold gives reason `no-match`; output is deterministic
- [ ] T011 [P] [US2] Contract tests in `tests/contract/test_cli_discover_classify.py` asserting the JSON shapes: `discover` returns `{"skills":[{"name","description","origin","kind","path"}]}`; `classify` returns `{"memberships":[{"skill","origin","cluster","score"}],"unclustered":[{"name","origin","reason"}]}` with `reason` one of `no-description`, `no-match`
- [ ] T012 [US2] Integration test in `tests/integration/test_classify_flow.py`: run `classify` over the fixture tree, assert the quickstart step 1 expectations, then delete one fixture skill from a tmp copy and assert it no longer appears in any cluster (US2 scenario 3)

### Implementation for User Story 2

- [ ] T013 [P] [US2] Implement `src/skill_clusters/discover.py`: `discover(project_dir, user_dir) -> list[Skill]` scanning `<project>/.claude/skills/*/SKILL.md` and `<user_dir>/*/SKILL.md` with a small hand-written parser for flat frontmatter (`name`, `description`, including quoted values and simple multi-line folded descriptions). Read-only on skills (FR-013). `kind="skill"`
- [ ] T014 [P] [US2] Implement `src/skill_clusters/classify.py` default clusters: a `DEFAULT_CLUSTERS` mapping with keyword -> weight sets for exactly diagrams, video, research, charts, documents, code-review (lowercase slugs)
- [ ] T015 [US2] Implement `classify(skills, clusters, threshold) -> (memberships, unclustered)` in `src/skill_clusters/classify.py`: score = weighted keyword matches in name (x2) plus description; a skill joins every cluster scoring above the threshold; empty description gives unclustered `no-description`; otherwise nothing above threshold gives `no-match`. Set the default threshold so T010/T012 pass (depends on T014)
- [ ] T016 [US2] Wire `discover` and `classify` subcommands in `src/skill_clusters/cli.py` to emit the contract JSON, plus a `--format human` table (depends on T013, T015)

**Checkpoint**: US2 works standalone. Run T009-T012.

---

## Phase 4: User Story 1 - Pick from a cluster of matching skills (Priority: P1) MVP

**Goal**: For a request, show the matching cluster's skills best-first and make the agent wait for the user's choice before any runs.

**Independent Test**: `skill-clusters options --request "draw a diagram of this flow" --project-dir tests/fixtures` returns `cluster: diagrams`, three options each with name, one-line description and origin, and `single: false`. A request that matches a one-member cluster returns `single: true`.

### Tests for User Story 1

- [ ] T017 [P] [US1] Unit tests in `tests/unit/test_pick.py`: request-to-cluster matching returns one winner for a clear request; a tie within the margin returns `ambiguous` with cluster null; no match returns cluster null and empty options; one-member cluster sets `single=true`; options list is capped at 7 and reports `hidden_count`; `--all` returns the rest; each description is truncated to one line
- [ ] T018 [P] [US1] Contract test in `tests/contract/test_cli_options.py` asserting the `options` JSON shape from contracts/cli.md: keys `cluster`, `ambiguous`, `single`, `options` (each `{name, description, origin}`), `hidden_count`, `warnings`; and that the CLI never executes a skill
- [ ] T019 [US1] Integration test in `tests/integration/test_options_flow.py`: quickstart step 2 against the fixture tree; also a same-name skill in project and user dirs appears twice, labeled by origin; no skills installed gives null cluster and empty options with exit code 0

### Implementation for User Story 1

- [ ] T020 [US1] Add `match_request(text, clusters, margin)` to `src/skill_clusters/classify.py`: score the request against the same cluster keyword sets; one clear winner returns it; a tie within `margin` returns the ambiguity list (research.md "Request-to-cluster matching")
- [ ] T021 [US1] Implement `src/skill_clusters/pick.py`: `build_options(request, skills, memberships, clusters, show_all=False) -> dict` producing the cluster, ambiguous, single, options, hidden_count, warnings structure. Default order is "score descending, then name"; cap "top 7 by default", with `show_all` returning the rest; one-line descriptions (first line or sentence, trimmed) (depends on T020)
- [ ] T022 [US1] Wire `options --request TEXT [--all]` in `src/skill_clusters/cli.py` to run discover, classify, then `build_options`, and print contract JSON (or a readable one-line-per-option table with `--format human`) (depends on T016, T021)
- [ ] T023 [US1] Create the agent wrapper `.claude/skills/skill-cluster-picker/SKILL.md`: frontmatter with a `description` written to win routing for cluster-type requests (draw/diagram/video/research/chart etc.), and instructions to (1) run `skill-clusters options --request "<user request>"`, (2) show the list and wait for an explicit choice, (3) invoke ONLY the chosen skill, (4) on "none" run nothing and proceed normally, (5) if `single` is true run it and name it, (6) if `ambiguous` is non-empty ask which task type, (7) surface `warnings`. Document the self-triggering risk from research.md and that member skills are not modified (FR-013)

**Checkpoint**: US1 and US2 together form the MVP. Run T017-T019 and quickstart steps 1-2.

---

## Phase 5: User Story 3 - Preference-based ranking (Priority: P2)

**Goal**: Order options by the user's preference file; hide excluded skills; degrade gracefully.

**Independent Test**: Copy `tests/fixtures/preferences/favor-b.toml` to `.skill-clusters/preferences.toml`; `options` lists `diagram-b` first. Add it to `exclude`: it is absent. Remove the file: default order, no error. Invalid TOML: a `warnings` entry naming file, line and message, default order, exit code 2.

### Tests for User Story 3

- [ ] T024 [P] [US3] Unit tests in `tests/unit/test_rank.py`: favor order is the order listed; disfavor goes last; exclude removes; "a skill both favored and excluded at the same level is excluded, with a warning"; "cluster-level over global, project over user" precedence; names not installed are ignored and reported once; unknown keys give a warning, not a failure
- [ ] T025 [P] [US3] Unit tests in `tests/unit/test_preferences_load.py` for `load_preferences`: missing file gives empty prefs and no warnings; invalid TOML gives a warning with file, line and message; wrong value types give a warning and fall back to defaults
- [ ] T026 [US3] Integration test in `tests/integration/test_preferences_flow.py` covering the quickstart step 3 scenarios, including exit code 2 on invalid TOML and that adding a favorite changes the order on the very next `options` run (SC-005)

### Implementation for User Story 3

- [ ] T027 [US3] Implement `load_preferences(project_dir, user_dir_config)` in `src/skill_clusters/store.py` reading `~/.config/skill-clusters/preferences.toml` and `<project>/.skill-clusters/preferences.toml` with `tomllib`. Schema per contracts/preferences.schema.md: `[global]` and `[clusters.<name>]` tables with optional `favor`, `disfavor`, `exclude` lists of strings; project overrides user key by key. Return `(preferences, warnings)`; never raise on bad input
- [ ] T028 [US3] Implement `src/skill_clusters/rank.py`: `apply_preferences(options, preferences, cluster, installed) -> (ordered, warnings)` with ordering favor (in listed order) then default order then disfavor, drops excluded, applies the precedence and conflict rules in T024
- [ ] T029 [US3] Integrate ranking into `build_options` in `src/skill_clusters/pick.py` and the `options` handler in `src/skill_clusters/cli.py`: apply ranking before capping, merge preference warnings into `warnings`, return exit code 2 when preference loading produced an error (depends on T027, T028)

**Checkpoint**: US1-US3 work. Run T024-T026.

---

## Phase 6: User Story 4 - Arranger files newly installed skills (Priority: P2)

**Goal**: Detect new or removed skills, file them, tell the user, and keep user corrections permanently.

**Independent Test**: Copy `tests/fixtures/extra/new-skill` into the fixture tree and run `arrange`: it is reported as filed with its cluster. After `correct new-skill --cluster research`, later `arrange` runs keep it there. `git status` shows no changes under any skill directory.

### Tests for User Story 4

- [ ] T030 [P] [US4] Unit tests in `tests/unit/test_arrange.py`: new skill matching a cluster is filed; new skill matching none is reported unclustered or yields a `proposed_clusters` entry (`proposed=true`); skill removed from disk is dropped from all memberships and listed under `removed`; a `source: user` membership is never overwritten by auto; a `source: user, removed: true` membership is not re-added; `--dry-run` writes nothing
- [ ] T031 [P] [US4] Contract tests in `tests/contract/test_cli_arrange_correct_show.py`: `arrange` output shape `{"filed":[{"skill","cluster"}],"unclustered":[...],"proposed_clusters":[{"name","skills"}],"removed":[...]}`; `correct` output returns the updated membership; `show --cluster` and `show --skill` print membership including source
- [ ] T032 [US4] Integration test in `tests/integration/test_arranger_flow.py` running quickstart steps 4-5 against a tmp copy of the fixtures, plus a check that file contents and mtimes under every skill directory are unchanged after `arrange` and `correct` (FR-013)

### Implementation for User Story 4

- [ ] T033 [US4] Implement `render_clusters_md(memberships, skills, path)` in `src/skill_clusters/store.py`: writes `CLUSTERS.md` next to `state.json` listing each cluster with member name, origin and `auto`/`user` source, plus an Unclustered section (FR-012, SC-006)
- [ ] T034 [US4] Implement `src/skill_clusters/arrange.py`: `arrange(skills, state, clusters, dry_run) -> result` that diffs discovery against saved state; files new skills via `classify`; reports unclustered; proposes a new cluster (`proposed=true`) when a skill matches none but several unclustered skills share keywords, else leaves it unclustered; drops memberships of skills no longer on disk; preserves `source: user` memberships and `removed: true` markers; never touches any skill path
- [ ] T035 [US4] Implement `correct(skill, cluster, remove, confirm_cluster)` in `src/skill_clusters/arrange.py`: records a `source: user` membership, or `removed: true` with `--remove`; `--confirm-cluster` sets a proposed cluster's `proposed=false`; persists via `store.save_state`
- [ ] T036 [US4] Wire `arrange [--dry-run]`, `correct SKILL --cluster NAME [--remove] [--confirm-cluster]`, and `show [--cluster NAME | --skill NAME]` in `src/skill_clusters/cli.py`. `arrange` writes `state.json` and `CLUSTERS.md` unless `--dry-run` and prints what it filed so the user is told (FR-009); `show` defaults to human-readable output (depends on T033-T035)
- [ ] T037 [US4] Make `options` consume saved state when present in `src/skill_clusters/cli.py` and `src/skill_clusters/pick.py`: user-source memberships override auto classification and removed markers exclude a skill from a cluster, so corrections affect picks (FR-010)
- [ ] T038 [US4] Extend `.claude/skills/skill-cluster-picker/SKILL.md` so the agent runs `skill-clusters arrange` at the start of a session and relays the "filed" report to the user, then offers `correct` if they disagree (spec assumption: arrange runs on invocation or at session start)

**Checkpoint**: All four stories work. Run the full suite.

---

## Phase 7: Polish & Cross-Cutting Concerns

- [ ] T039 [P] Performance test in `tests/integration/test_performance.py`: generate 500 synthetic skills in a tmp dir; discover plus classify completes in under 1 s (plan.md performance goal)
- [ ] T040 [P] Reference-set accuracy test in `tests/integration/test_reference_set.py`: a labeled set of real-looking skill descriptions with expected clusters; assert at least 90% agreement (SC-003); tune `DEFAULT_CLUSTERS` keywords in `src/skill_clusters/classify.py` if it fails
- [ ] T041 [P] Update `README.md`: install (`pip install -e .[test]`), CLI usage, the preferences file location and format, and the self-triggering limitation
- [ ] T042 Decide the fate of the hand-written `.claude/skills/diagram-cluster/SKILL.md`: once `options` can generate the diagrams list, mark it superseded in its description or remove it, without altering the third-party diagram skills it lists (FR-013)
- [ ] T043 Run every step of `specs/001-skill-cluster-picker/quickstart.md` and fix any discrepancy between the document and actual behavior; then run `pytest` and confirm green

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (1)**: none
- **Foundational (2)**: after Setup; blocks all stories
- **US2 (3)**: after Foundational
- **US1 (4)**: after US2 (needs `discover`/`classify` and the CLI wiring from T016)
- **US3 (5)**: after US1 (modifies `build_options` and the `options` handler)
- **US4 (6)**: after US2 for the arranger core (T033-T036); T037 and T038 need US1. Can run in parallel with US3 if edits to `cli.py` and `pick.py` are coordinated
- **Polish (7)**: after the stories it covers

### Within Each Story

- Tests first, confirm they fail, then implement
- Model/types, then logic modules, then CLI wiring, then the SKILL.md wrapper

### Same-File Cautions

`cli.py` is edited by T007, T016, T022, T029, T036, T037. `classify.py` by T014, T015, T020. `store.py` by T006, T027, T033. `pick.py` by T021, T029, T037. These are sequential, not [P].

## Parallel Opportunities

- Setup: T003 and T004 together
- Foundational: T008 alongside T005-T007
- US2 tests T009, T010, T011 together; impl T013 and T014 together
- US1 tests T017, T018 together
- US3 tests T024, T025 together
- US4 tests T030, T031 together
- Polish: T039, T040, T041 together

### Parallel Example: User Story 2

```text
Task: "Unit tests in tests/unit/test_discover.py"
Task: "Unit tests in tests/unit/test_classify.py"
Task: "Contract tests in tests/contract/test_cli_discover_classify.py"
Task: "Implement src/skill_clusters/discover.py"
Task: "Implement DEFAULT_CLUSTERS in src/skill_clusters/classify.py"
```

## Implementation Strategy

### MVP First (US2 + US1)

1. Phase 1 Setup, Phase 2 Foundational
2. Phase 3 US2, then Phase 4 US1
3. **Stop and validate**: quickstart steps 1-2 and `pytest`; install the picker SKILL.md and try a real "draw a diagram" request

### Incremental Delivery

1. MVP (US2 + US1)
2. US3 preferences, validate quickstart step 3
3. US4 arranger, validate quickstart steps 4-5
4. Polish and the full quickstart run

## Notes

- `.specify/memory/constitution.md` is still the unfilled template, so there are no governance gates. plan.md recommends running `/speckit-constitution` first.
- Known risk carried from research.md: member skills can still self-trigger because FR-013 forbids editing them. T023 mitigates this only through the picker's description.
- Plan lists fixtures at `tests/fixtures/skills/`, but quickstart uses `--project-dir tests/fixtures`. This file follows quickstart (`tests/fixtures/.claude/skills/`) so both discovery and the documented commands work.
