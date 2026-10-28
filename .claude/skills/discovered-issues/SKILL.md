---
name: discovered-issues
description: The shared log of bugs, rules mismatches and gaps found but not fixed (Notes/discovered-issues.md) and the script every agent uses to add, update, close and search entries in it - safe for several agents writing at once, and from worktrees. Use whenever you notice a problem outside your task's scope, before starting work on a known bug (check it isn't already logged or being fixed), after fixing something that may be logged (mark it fixed), when a review or rules check produces findings nobody is fixing now, and whenever someone asks "what's broken?", "what's left?", "is X a known issue?" or "what's still open?".
---

# Discovered issues

[Notes/discovered-issues.md](../../../Notes/discovered-issues.md) is the one list of known problems that every agent and the main session shares. Entries are grouped into Open (`open`, `in-progress`), Fixed and Won't fix, and each has a stable id (`DI-007`) and a history line for every change.

## Always write through the script

```bash
python .claude/skills/discovered-issues/issues.py list --status open                   # what's known
python .claude/skills/discovered-issues/issues.py list --grep "temp hp"                 # is it already logged?
python .claude/skills/discovered-issues/issues.py show DI-004
python .claude/skills/discovered-issues/issues.py add --title "Temp HP stack instead of keep-one" \
    --area combat-simulator --where "Combat/CombatUIQt/damage_mixin.py:456" --by rules-checker \
    --details "What's wrong, a failing scenario with numbers, the suggested fix."
python .claude/skills/discovered-issues/issues.py update DI-004 --status in-progress --by combat-simulator
python .claude/skills/discovered-issues/issues.py update DI-004 --status fixed --commit 03bcecb0 --by combat-simulator
python .claude/skills/discovered-issues/issues.py update DI-004 --note "Also affects rest.py" --by code-reviewer
```

- Never change the document with Edit or Write. The script holds a lock while it re-reads, changes one entry and swaps the file in, so writes from several agents at once never overwrite each other. A direct edit can.
- The script always writes to the document in the **main checkout**, even when you run in a `.claude/worktrees/` worktree, so there is one list and no merge conflicts. Don't commit the copy in your worktree.
- Writing to it is always in scope. It is the one shared file besides your own agent memory that every agent may change, and only through the script.

## When to add an entry

- You find a bug, rules mismatch or gap **that your task doesn't cover**. Log it and name the id under **Concerns** in your report, instead of fixing it out of scope.
- A review or rules check reports findings that nobody is fixing now (the main session logs what the user deferred).
- `list --grep` first. If it's already there, add a `--note` with what you saw instead of a duplicate.

A good entry: a one-line title saying what's wrong; `--area` is the agent that would fix it (`combat-simulator`, `character-engine-dev`, `spell-improved-descriptions`, ...); `--where` is `path:line` (repeat it for several places); `--details` is a concrete failing scenario with numbers and a suggested fix, plus the rule quoted if it's a rules mismatch.

## When to change one

- **Starting a fix:** `--status in-progress`, so a parallel agent doesn't fix it too. If it is already `in-progress`, leave it to whoever has it and say so in your report.
- **Fixed:** `--status fixed` with `--commit <hash>` when there is one. Without a commit the entry says "uncommitted"; whoever commits the fix (the `git-commit` agent or the main session) updates it with the hash.
- **Won't fix:** only when the user decided so; put their reason in `--note`.
- Never mark fixed an entry your change didn't fix, and never reopen, delete or reword another agent's entry. Add a `--note` instead.

## Committing it

Commit `Notes/discovered-issues.md` whole, together with the fix it records, or on its own as "Update discovered issues". Entries from other agents may ride along; that's fine for this file, and the only exception to staging only your own hunks.
