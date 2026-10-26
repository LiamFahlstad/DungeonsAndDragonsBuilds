# DungeonsAndDragonsBuilds

A D&D 5e (2024 rules) character engine that renders HTML character sheets, plus a PyQt6 combat simulator and a character-creator GUI. Python 3.11, `attrs`. All commands run from the repo root; [HOWTO.md](HOWTO.md) lists every script and flag.

## Commands

```bash
./run_tests.sh -q -x                       # tests (args go to pytest); UPDATE_SNAPSHOTS=1 regenerates golden snapshots
./format.sh                                # Black
./typecheck.sh [folder]                    # pyright
python RunCharacterCreator.py [--example]  # build every registered (or example) character sheet
python Combat/Tools/monster_score.py -v "<monster>"   # homebrew monster balance score
```

## Project rules

- **2024 engine, 2014 content on top.** Subclasses always start at level 3, even 2014 ones that said 1 or 2; this is intended. If a subclass has a 2024 reprint (including renamed ones, e.g. School of Evocation → Evoker), the 2014 version is not added. 2024 base-class features win over overlapping 2014 subclass features.
- **A feature's `origin=` is its category**, the label a player reads ("Origin Feat", "General Feat Level 4+", "Bard Level 9"), never the sourcebook or release. Old code with sourcebook text in `origin` is not precedent.
- **Homebrew monsters** (`Combat/Monsters/CR_*/monsters_homebrew.py`): at most 4 `MonsterAbility` entries in total, preferably at least one trait. Balance them before calling them done: the `score` column (not median/mean) of `monster_score.py` must land in 0.4-0.6. The `balance-monster` and `monster-stat-blocks` skills have the procedure and format.
- Never hand-edit a plain generated `Combat/Monsters/CR_*/monsters.py`; `generate_monsters.py` overwrites it.
- **`usage_tags`** on features and spells follow the `usage-tags` skill.

## Rules for every agent, including subagents

- **Stay in scope.** Only edit the files your task names. If a shared/core file needs a change, stop and say so in your report; do not edit it.
- **Never revert or "fix" changes you didn't make.** Other agents may be working in the same tree at the same time.
- **Scripted edits exclude `.claude/` and `.git/`.** `.claude/worktrees/` holds full checkouts of other agents' branches; a repo-wide `rglob` will silently edit them.
- **Scratch scripts go in the scratchpad directory**, never the repo.
- **Fix what you broke; don't widen the change.** When you find a bug in your own work, fix those lines only, not the whole scope back to the old pattern.
- **Don't wave away failures.** A failing test or snapshot is never "expected" unless you have looked at the diff and can say why.

### Final report format (subagents)

End with these sections, plain and factual, in addition to anything your own agent prompt asks you to report. The orchestrator checks them against `git status`.

1. **Files changed:** exact paths, one per line. Nothing else.
2. **Commands run:** each verification command and its actual result (pass/fail counts, not "looks good").
3. **Not done:** anything skipped, partly done or deferred, with the reason. Write "none" if none.
4. **Concerns:** anything the orchestrator should check, including any shared file you think needs a change.

## Orchestrating agents (main session)

Agents live in `.claude/agents/<domain>/` (roles: prompt, tools, model). Shared know-how lives in `.claude/skills/<skill>/` (procedures, reference files, scripts), which agents preload with `skills:` and the main session can use directly. The description in each file says when to use it. [Notes/agent-workflow.md](Notes/agent-workflow.md) explains the whole setup.

- **Pick the specialist first** (subclass-creator, monster-creator, test-bughunter, ...), and fall back to `dnd-builds` / `combat-sim` for general work. Do small or single-file edits yourself instead of spawning an agent.
- **Model choice.** Agents default to the model in their frontmatter. Pass `model: "haiku"` only for small, mechanical, easy-to-verify tasks (one feature, one combatant, a lookup). Never use haiku for tests or bug hunting, for subjective classification or tagging across hundreds of items, or for bulk migrations over shared code.
- **Brief like a stranger.** A subagent sees CLAUDE.md, its own prompt and its preloaded skills, not this conversation. Don't count on it seeing auto-memory. Agent and skill edits apply only after Claude Code restarts. Say exactly which files are in scope, which are off-limits, what "done" means, and how to verify it.
- **Parallel work.** Split by disjoint file sets. Name the off-limits shared files explicitly. Prefer `isolation: "worktree"` when scopes might overlap. For a change that repeats one pattern across many classes, consider one generic method on the base class instead of N hand-written overrides.
- **Verify before reporting done.** After agents finish, run the `verify-agent-work` skill (`python .claude/skills/verify-agent-work/verify.py --claimed <files>`), and add `--tests` after the last agent in a batch. A detailed self-report is no more trustworthy than a vague one.
- A `SubagentStop` hook (`.claude/hooks/check_subagent_edits.py`) already refuses to let a subagent finish while a file it edited fails to compile, or when it edited another agent's worktree.
