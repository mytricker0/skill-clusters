# skill-clusters

Group similar agent skills and MCP servers into clusters by task type (diagrams, video, research, ...). When you ask for something in a cluster, the agent first proposes the matching options and you pick, instead of one skill silently firing.

## Idea

- A cluster = one small "picker" skill that lists members (skills and MCP servers), when to use each, and how to run it.
- Member skills defer to the picker so they do not trigger on their own.
- First cluster: diagrams (`.claude/skills/diagram-cluster/`).

## Related work

- [Sheshiyer/skill-clusters](https://github.com/Sheshiyer/skill-clusters): hub-and-spoke skill clusters per tech stack.
- [pcx-wave/skill-router](https://github.com/pcx-wave/skill-router), [David-CKS/claude-skill-router](https://github.com/David-CKS/claude-skill-router): route a request to one installed skill automatically.

This project differs by spanning skills and MCP servers, grouping by task type, and always asking the user to pick first.

## Status

Scaffolded with [Spec Kit](https://github.com/github/spec-kit). `claude` integration configured.

- ✅ `diagram-cluster` picker skill added (members + delegation rules).
- ⬜ Constitution / spec / plan still to be filled in via `.specify/`.
- ⬜ More clusters (video, research, charts) — copy `diagram-cluster`.
- ⬜ Confirm each referenced member skill/MCP is installed before promising it.
