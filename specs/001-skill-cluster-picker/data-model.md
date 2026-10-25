# Data Model: Skill Cluster Picker

## Skill
| Field | Type | Notes |
|-------|------|-------|
| name | string | from frontmatter; required |
| description | string | may be empty (then unclustered) |
| origin | `project` \| `user` | where it was found |
| kind | `skill` \| `mcp` | only `skill` in v1 |
| path | string | location of SKILL.md; read-only (FR-013) |

Identity: `(origin, name)`. Same name in two origins is two Skills.

## Cluster
| Field | Type | Notes |
|-------|------|-------|
| name | string | unique, lowercase slug (e.g. `diagrams`) |
| keywords | map word -> weight | used by the classifier and request matching |
| proposed | bool | true until the user confirms a new cluster |

## Membership
| Field | Type | Notes |
|-------|------|-------|
| skill | Skill id | |
| cluster | Cluster name | a skill may have several |
| source | `auto` \| `user` | `user` always wins over `auto` |
| score | float | classifier score, auto only |

Rules: a user-removed membership is stored as `source: user, removed: true` so auto runs do not re-add it.

## Preference
| Field | Type | Notes |
|-------|------|-------|
| skill | name | |
| action | `favor` \| `disfavor` \| `exclude` | |
| cluster | optional name | global when absent |
| level | `user` \| `project` | project overrides user |

Rules: a preference naming an uninstalled skill is ignored and reported once.

## Pick
| Field | Type | Notes |
|-------|------|-------|
| request | string | |
| cluster | name or ambiguity list | |
| options | list of {name, description, origin} | ordered, capped |
| selection | name \| `none` | |

Picks are returned to the agent and not persisted in v1.

## Transitions
- Skill: new -> filed (auto) -> corrected (user) ; removed from disk -> dropped from all memberships on next discovery.
- Cluster: proposed -> confirmed (user) or discarded.
