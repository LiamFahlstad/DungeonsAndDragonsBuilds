# DungeonsAndDragonsBuilds

A D&D 5e (2024 rules) character engine that renders HTML character sheets, plus a PyQt6 combat simulator and a character-creator-gui GUI. Python 3.11, `attrs`. All commands run from the repo root; [HOWTO.md](HOWTO.md) lists every script and flag.

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

- **Stay in scope.** Only edit the files your task names, plus your own `.claude/agent-memory/<your-name>/`. If a shared/core file needs a change, stop and say so in your report; do not edit it.
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
5. **Lessons:** the lines you added to or removed from your memory (or "none"), and any **proposed change** to your own prompt, a skill or CLAUDE.md, as the exact text to change and why.

### Learning from your runs (subagents)

Every agent has persistent memory (`memory: project`): `.claude/agent-memory/<your-name>/MEMORY.md` is loaded into your prompt on every run. That is how you improve yourself.

- **Before starting**, read your memory and apply it. It overrides your prompt where they conflict, because it is newer.
- **Record a lesson when you hit a problem a future run would hit again**: an instruction in your prompt or skill that was wrong or stale, a path or command that didn't work and what did, a check that caught your own mistake, or a correction from the orchestrator.
- **A lesson is one line**: the date, what to do, and a short why. For example: `2026-10-26: monster_score.py needs the exact combatant_type= text, not the class name. A class name returns "not found".` Record the fix, not the story. Only record what you actually observed this run; never record guesses, and never record "task went fine".
- **Keep it short and current.** Update or delete a lesson that turns out wrong or is superseded instead of adding a contradicting one. Keep `MEMORY.md` under 100 lines; move detail into a topic file beside it and link to it.
- **Re-read `MEMORY.md` right before you edit it.** Another run of the same agent may have changed it.
- **Don't edit your own agent file, a skill or CLAUDE.md.** Those are shared, tested and reviewed. Put the exact change you want under **Lessons** in your report; the orchestrator applies it.

## Orchestrating agents (main session)

Agents live in `.claude/agents/<domain>/` (roles: prompt, tools, model). Shared know-how lives in `.claude/skills/<skill>/` (procedures, reference files, scripts), which agents preload with `skills:` and the main session can use directly. The description in each file says when to use it. [Notes/agent-workflow.md](Notes/agent-workflow.md) explains the whole setup.

- **Commit through `git-commit`** when the user asks for a commit. Tell it what to commit and who made the changes: the user, or the Claude model from this session's attribution instructions. That decides its Co-Authored-By trailer. Relay its report, including the full message it wrote.
- **Find the right one in the index.** `.claude/skills/agent-index/SKILL.md` (the `agent-index` skill) lists every agent and skill, generated from their frontmatter. A hook rebuilds it after edits, and a test fails if it's stale.
- **Pick the specialist first** (`subclass-implementer`, `monster-designer`, `test-bughunter`, ...), and fall back to `character-engine-dev` / `combat-simulator` for general work. Do small or single-file edits yourself instead of spawning an agent.
- **Model choice.** Each agent's frontmatter model follows one rule:
  - **opus** (Opus 5.5) for design, engineering and judgment: engine and GUI work, new subclasses and monsters, test writing and bug hunting, scrapers, commits;
  - **sonnet** for rubric-driven batch work that a tool or exact check verifies (balancing monsters, converting abilities, improved spell descriptions);
  - **haiku** for near-mechanical bulk tagging and summaries.

  Keep the default. Pass `model: "sonnet"` to run an opus agent on a small, easy-to-verify task (one feature, one combatant, a lookup). Never downgrade tests or bug hunting, subjective classification at scale, or migrations over shared code: haiku runs here have failed at exactly those.
- **Brief like a stranger.** A subagent sees CLAUDE.md, its own prompt and its preloaded skills, not this conversation. Don't count on it seeing auto-memory. Agent and skill edits apply only after Claude Code restarts. Say exactly which files are in scope, which are off-limits, what "done" means, and how to verify it.
- **Parallel work.** Split by disjoint file sets. Name the off-limits shared files explicitly. Prefer `isolation: "worktree"` when scopes might overlap. For a change that repeats one pattern across many classes, consider one generic method on the base class instead of N hand-written overrides.
- **Verify before reporting done.** After agents finish, run the `verify-agent-work` skill (`python .claude/skills/verify-agent-work/verify.py --claimed <files> --off-limits <shared files>`), and add `--tests` after the last agent in a batch. A detailed self-report is no more trustworthy than a vague one.
- **Curate what agents learn.** After verifying a run, review its memory changes (`git diff -- .claude/agent-memory/`). Delete lessons that are wrong. That matters most for haiku runs, whose reports have been confidently false here. When a lesson has proven itself, or an agent proposed a prompt or skill change, make the change in the prompt or skill and delete the lesson from memory, so memory stays a short list of recent, unpromoted lessons. When *you* catch an agent's mistake during verification, write the lesson into that agent's `MEMORY.md` yourself; agents rarely notice their own fabricated successes.
- A `SubagentStop` hook (`.claude/hooks/check_subagent_edits.py`) already refuses to let a subagent finish while a file it edited fails to compile, or when it edited another agent's worktree.
