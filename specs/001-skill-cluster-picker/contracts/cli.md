# Contract: `skill-clusters` CLI

Text protocol: arguments in, JSON on stdout (`--format human` for a readable table), problems on stderr. Exit codes: 0 ok, 1 usage error, 2 recoverable problem reported in output (e.g. bad preferences, defaults used).

Common flags: `--project-dir PATH` (default cwd), `--user-dir PATH` (default `~/.claude/skills`), `--state PATH`.

## `discover`
Output: `{"skills":[{"name","description","origin","kind","path"}]}`

## `classify`
Output: `{"memberships":[{"skill","origin","cluster","score"}],"unclustered":[{"name","origin","reason"}]}`
`reason` is `no-description` or `no-match`.

## `options --request TEXT [--all]`
Output:
```json
{"cluster": "diagrams",
 "ambiguous": [],
 "single": false,
 "options": [{"name":"...","description":"one line","origin":"user"}],
 "hidden_count": 0,
 "warnings": []}
```
- `ambiguous` non-empty (cluster null): agent asks which task type.
- `single` true: agent may run the one option and name it (FR-003 exception).
- No match: `cluster` null, `options` empty; agent proceeds normally.
- `warnings` carries preference-file errors and ignored-preference notices.
- The CLI never runs a skill; the agent runs only the user's selection. "none" runs nothing.

## `arrange [--dry-run]`
Compares discovery to `state.json`. Output: `{"filed":[{"skill","cluster"}],"unclustered":[...],"proposed_clusters":[{"name","skills"}],"removed":[...]}`. Writes `state.json` and `CLUSTERS.md` unless `--dry-run`. Never writes inside any skill directory.

## `correct SKILL --cluster NAME [--remove] [--confirm-cluster]`
Records a `source: user` membership (or removal). Output: the updated membership. Persisted across later `arrange` runs.

## `show [--cluster NAME | --skill NAME]`
Prints cluster membership (human-readable by default) so a user can locate any skill quickly (SC-006).
