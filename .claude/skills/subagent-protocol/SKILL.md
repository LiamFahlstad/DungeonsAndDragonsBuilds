---
name: subagent-protocol
description: How every project subagent reports back and learns from its runs - the fixed final report sections, and when and how to record lessons in its own agent memory. Preloaded by every agent in .claude/agents; read it when you are running as a subagent of this repo, or when reviewing what an agent should have reported or recorded.
---

# Subagent protocol

You are a subagent. The main session (the orchestrator) checks your work against the files on disk, not your words, and it curates what you learn. These two habits make that work.

## Final report

End with these sections, plain and factual, in addition to anything your own prompt asks you to report. Your final message *is* the report: write it out in full. The orchestrator compares it with `git status`.

1. **Files changed:** exact paths, one per line. Nothing else.
2. **Commands run:** each verification command and its actual result (pass/fail counts, not "looks good").
3. **Not done:** anything skipped, partly done or deferred, with the reason. Write "none" if none.
4. **Concerns:** anything the orchestrator should check, including any shared file you think needs a change, and the `DI-###` ids of any discovered issues you added or updated.
5. **Lessons:** the lines you added to or removed from your memory (or "none"), and any **proposed change** to your own prompt, a skill or CLAUDE.md, as the exact text to change and why.

## Learning from your runs

You have persistent memory (`memory: project`): `.claude/agent-memory/<your-name>/MEMORY.md` is loaded into your prompt on every run. That is how you improve yourself, and it is the one place outside your task's scope that you may always write to.

- **Before starting**, apply what your memory says. Where it conflicts with your prompt, the memory is newer, so follow it and mention the conflict under **Lessons**.
- **Record a lesson when you hit a problem a future run would hit again**: an instruction in your prompt or skill that was wrong or stale, a path or command that didn't work and what did, a check that caught your own mistake, or a correction from the orchestrator. A deliberate test, or a one-off caused by the task itself, is not a lesson.
- **A lesson is one line in `MEMORY.md` itself**: the date, what to do, and a short why. For example: `2026-10-26: monster_score.py needs the exact combatant_type= text, not the class name. A class name returns "not found".` Record the fix, not the story, and only what you observed this run: never guesses, never "task went fine".
- **This overrides the memory system's default format** (one file per memory, plus an index line). Only `MEMORY.md` is loaded into every run, so a lesson kept in a separate file would be missed exactly when it matters. Use a topic file only for detail, linked from a one-line lesson.
- **Keep it short and current.** Update or delete a lesson that turns out wrong or is superseded instead of adding a contradicting one. Keep `MEMORY.md` under 100 lines; a test enforces it.
- **Re-read `MEMORY.md` right before you edit it.** Another run of the same agent may have changed it.
- **Don't edit your own agent file, a skill or CLAUDE.md.** Those are shared, tested and reviewed. Put the exact change you want under **Lessons**, and the orchestrator applies it.

## Bugs outside your task

`Notes/discovered-issues.md` is the list of known problems that every agent shares. When you find a bug, rules mismatch or gap that your task doesn't cover, don't fix it out of scope. Log it with the `discovered-issues` skill's script (`python .claude/skills/discovered-issues/issues.py add ...`) after checking `issues.py list --grep <words>` for an existing entry. If your task fixes a logged entry, mark it `in-progress` when you start and `fixed` when done. Only ever write to that file through the script: it locks the file so several agents can write at once, and it writes to the main checkout even from a worktree. The skill's SKILL.md has the full rules.

## If a hook stops you

When you try to hand back, a hook compiles every `.py` file you edited and checks that you didn't edit another agent's worktree. If it blocks you, fix what it lists, then hand back again, and mention it in your report. If you can't fix it, hand back anyway: it blocks only once per problem, and your report must explain what's still broken.
