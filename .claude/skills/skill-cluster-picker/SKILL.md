---
name: "skill-cluster-picker"
description: "Propose the best installed skills for a request, ranked by user preference; user picks one before it is built. Auto-files newly installed skills into clusters."
compatibility: "Works with any integration that runs the skill-clusters CLI. First member of every skill cluster."
metadata:
  author: "mytricker0"
  source: "skill-clusters"
user-invocable: true
disable-model-invocation: false
---

## Purpose

A picker that discovers installed skills, classifies them into task-type
clusters, ranks them by a user preference file, and asks the user to pick before
any member runs. Do NOT build silently.

## When to run

At the start of a new project or whenever the user asks to do something
plausibly covered by an installed skill. Run it before picking a tool.

## How to run

1. Run the picker with the user's request:

   ```bash
   skill-clusters options --request "<user request>" --project-dir <project> --user-dir ~/.claude/skills
   ```

2. Read the JSON output. It contains:
   - `cluster`: the matched task type, or `null` if none matched.
   - `ambiguous`: non-empty when the request could mean more than one cluster — ask the user which task type.
   - `single`: true when exactly one option exists — you may run it and name it.
   - `options`: ranked list of `{name, description, origin}`.
   - `warnings`: preference-file issues to surface.

3. Present the options in ranked order and ask the user to pick.

4. Invoke ONLY the chosen skill. If the user says "none", run nothing and proceed normally.

5. If `single` is true, run the one option and name it.

6. If `ambiguous` is non-empty, ask which task type the user meant, then run the selected option.

7. Surface any `warnings`.

## Arranging new skills

At the start of a session, run:

```bash
skill-clusters arrange --project-dir <project> --user-dir ~/.claude/skills
```

It reports which newly installed skills it filed into clusters. If the user
disagrees with a filing, correct it:

```bash
skill-clusters correct <SKILL> --cluster <cluster-name>
```

Later `arrange` runs keep the correction. `--dry-run` shows what would be filed
without writing. `--remove` drops a membership; `--confirm-cluster` confirms a
proposed cluster.

## Self-triggering note

The picker's `description` is written to win routing for cluster-type requests,
but it does NOT modify the member skills it lists (FR-013). If a member skill
also fires independently, the user still picks first here.
