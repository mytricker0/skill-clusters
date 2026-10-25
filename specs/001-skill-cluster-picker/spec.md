# Feature Specification: Skill Cluster Picker

**Feature Branch**: `001-skill-cluster-picker`

**Created**: 2026-10-25

**Status**: Draft

**Input**: User description: "a modular skill-cluster picker that discovers installed skills, auto-classifies them into task-type clusters, ranks by a user-preference file, and asks the user to pick; with an arranger that auto-files newly installed skills into their cluster"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Pick from a cluster of matching skills (Priority: P1)

A user asks their agent for something that several installed skills could handle (for example, "draw a diagram of this flow"). Instead of one skill silently firing, the agent shows the matching cluster's options, ordered best-first, with a one-line description of each, and asks the user to choose. The chosen skill then runs.

**Why this priority**: This is the core value of the project: replacing silent, arbitrary skill selection with an informed user choice.

**Independent Test**: With two or more installed skills in the same task type, make a request in that task type and confirm the user is shown all of them and the chosen one is the one that runs.

**Acceptance Scenarios**:

1. **Given** three installed skills belong to the "diagrams" cluster, **When** the user requests a diagram, **Then** the agent lists all three with short descriptions and waits for the user to choose before running any.
2. **Given** the options are shown, **When** the user picks one, **Then** only that skill runs.
3. **Given** a cluster has exactly one member, **When** the user makes a matching request, **Then** the agent may run it without prompting, noting which skill it used.
4. **Given** the user declines all options, **When** they answer "none", **Then** no cluster skill runs and the agent proceeds without one.

---

### User Story 2 - Automatic discovery and classification (Priority: P1)

The system finds the skills installed for the user (project-level and user-level) and groups them into task-type clusters (diagrams, video, research, charts, and so on) based on what each skill says it does, with no manual list maintenance.

**Why this priority**: Without discovery and grouping there is nothing to pick from; manual lists would not scale as skills are added.

**Independent Test**: Install a set of skills of varied purpose, run discovery, and confirm each lands in a sensible cluster and uncategorizable ones are reported as unclustered.

**Acceptance Scenarios**:

1. **Given** installed skills with descriptions, **When** discovery runs, **Then** each skill is assigned to a task-type cluster or marked unclustered.
2. **Given** a skill that fits more than one task type, **When** it is classified, **Then** it may appear in each relevant cluster.
3. **Given** a skill is removed, **When** discovery runs again, **Then** it no longer appears in any cluster.

---

### User Story 3 - Preference-based ranking (Priority: P2)

The user keeps a preference file stating which skills they favor, disfavor, or want excluded per cluster. The picker uses it to order options so favorites appear first and excluded skills do not appear.

**Why this priority**: Makes the choice faster and personal, but the picker is useful without it.

**Independent Test**: Add a preference file favoring one skill, make a request, and confirm that skill is listed first; mark another excluded and confirm it is absent.

**Acceptance Scenarios**:

1. **Given** a preference favoring skill B over A, **When** options are shown, **Then** B is listed before A.
2. **Given** a skill is marked excluded, **When** options are shown, **Then** it is not listed.
3. **Given** no preference file exists, **When** options are shown, **Then** a sensible default order is used and nothing fails.
4. **Given** the preference file is malformed, **When** the picker runs, **Then** the user is told what is wrong and the default order is used.

---

### User Story 4 - Arranger files newly installed skills (Priority: P2)

When a new skill is installed, the arranger detects it, classifies it, and files it into the right cluster (or proposes a new cluster when none fits), then tells the user what it did so they can accept or correct it.

**Why this priority**: Keeps clusters current without effort, but depends on classification (Story 2).

**Independent Test**: Install a new skill and confirm it appears in the expected cluster on the next request, with the user told where it was filed.

**Acceptance Scenarios**:

1. **Given** a new skill matching an existing cluster, **When** the arranger runs, **Then** it is added to that cluster and the user is informed.
2. **Given** a new skill matching no cluster, **When** the arranger runs, **Then** it is reported as unclustered or a new cluster is proposed for the user to confirm.
3. **Given** the user corrects a filing, **When** the correction is saved, **Then** later arranger runs do not undo it.

---

### Edge Cases

- No skills are installed, or none match the request: the agent says so and proceeds normally.
- Two skills share the same name across project and user locations: both are shown, labeled by origin.
- A skill has a missing or empty description: it is marked unclustered rather than guessed at.
- A preference refers to a skill that is no longer installed: it is ignored and reported once.
- A request matches more than one cluster: the user is asked which task type they mean, or shown a combined list.
- A very large number of members in a cluster: the list is capped to a readable top set with a way to see the rest.
- Member skills that would trigger on their own: they must defer to the picker so the user is not asked twice or bypassed.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST discover all skills installed at project and user level without a manually maintained list.
- **FR-002**: System MUST classify each discovered skill into one or more task-type clusters from its name and description, or mark it unclustered.
- **FR-003**: System MUST present the matching cluster's members to the user and wait for an explicit choice before running any of them, except for single-member clusters.
- **FR-004**: Each option shown MUST include the skill's name, a one-line description, and its origin.
- **FR-005**: Users MUST be able to decline all options.
- **FR-006**: System MUST read a user-editable preference file to order members and exclude skills, and MUST work with default ordering when it is absent.
- **FR-007**: System MUST report an unreadable or invalid preference file to the user with the problem identified, and continue with defaults.
- **FR-008**: The arranger MUST detect newly installed skills and file each into a matching cluster, or flag it as unclustered or propose a new cluster.
- **FR-009**: The arranger MUST tell the user where each new skill was filed.
- **FR-010**: User corrections to classification MUST persist and take precedence over automatic classification on later runs.
- **FR-011**: Discovery, classification, ranking, picking, and arranging MUST be separable modules that can be used or replaced independently.
- **FR-012**: Cluster membership MUST be inspectable by the user in a human-readable form.
- **FR-013**: System MUST NOT modify or delete the installed skills themselves while arranging.

### Key Entities

- **Skill**: An installed capability with a name, description, and origin (project or user level).
- **Cluster**: A named task type (for example, diagrams) with a set of member skills.
- **Membership**: The link between a skill and a cluster, recording whether it was set automatically or by user correction.
- **Preference**: A user rule that favors, disfavors, or excludes a skill, optionally per cluster.
- **Pick**: One choice event: the request, options shown, and the user's selection.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For requests that match a multi-member cluster, 100% of the time the user is asked to choose before any member runs.
- **SC-002**: Each option fits on one line, so a user can read the list and choose in under 10 seconds.
- **SC-003**: At least 90% of installed skills with a clear description are placed in a cluster the user agrees with on a reference set of skills.
- **SC-004**: A newly installed skill is filed and reported to the user within one session of installation, with no manual list editing.
- **SC-005**: Adding a favorite in the preference file changes the option order on the very next request in 100% of tests.
- **SC-006**: A user can find which cluster any given skill belongs to in under 30 seconds.

## Assumptions

- The agent environment exposes installed skills with a name and description that can be read.
- Classification uses descriptions only; skills are not executed to learn what they do.
- MCP servers are out of scope for this first version and may be added later; the design should not preclude them.
- The preference file is a single user-editable file, with project-level settings overriding user-level.
- Task-type cluster names start from a small default set and grow as the arranger proposes new ones.
- Arranging runs when the user invokes it or at the start of a session, not continuously in the background.
- Single-user, local use is assumed; no sharing of clusters between users.
