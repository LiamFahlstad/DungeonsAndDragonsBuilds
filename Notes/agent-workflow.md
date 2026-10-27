# Working with Claude Code agents in this repo

How the agent setup is organised, why each piece exists, and how to use and extend it. The patterns follow Anthropic's Claude Code documentation ([subagents](https://code.claude.com/docs/en/sub-agents), [skills](https://code.claude.com/docs/en/skills), [hooks](https://code.claude.com/docs/en/hooks)) and the lessons this repo learned the hard way.

## The short version

| Piece | File | Job |
|---|---|---|
| Shared context | `CLAUDE.md` | Project rules, commands, and how agents behave and report. **Every session and every subagent loads it.** |
| Roles | `.claude/agents/<domain>/<agent>.md` | One focused expert per kind of task: its own prompt, tool list, default model and the skills it preloads. Grouped by domain: `builds/`, `features/`, `spells/`, `combat/`, `tooling/`. |
| Know-how | `.claude/skills/<skill>/` | Procedures, reference files and scripts, shared by every agent that preloads them and usable by the main session: `balance-monster`, `monster-stat-blocks`, `usage-tags`, `verify-agent-work`. |
| Self-improvement | `.claude/agent-memory/<agent>/MEMORY.md` | Each agent's own lessons, loaded into its prompt every run. Agents write them; the main session reviews them and promotes good ones into prompts and skills (section 7). |
| Config test | `tests/test_claude_config.py` | Fails the normal test run if an agent's or skill's frontmatter is broken, or if a `skills:` entry, link or script path points at something missing. |
| Guardrail | `.claude/hooks/check_subagent_edits.py` (wired in `.claude/settings.json`) | A subagent can't finish while a `.py` file it edited fails to compile, or if it edited another agent's worktree. |
| Verification | `.claude/skills/verify-agent-work/` | Checks the working tree against what an agent *claimed*: compile, undefined names, imports, sibling worktrees, tests. |
| Permissions | `.claude/settings.json` | Safe, general allow rules shared by all sessions and agents; destructive git commands always ask. |
| Personal | `.claude/settings.local.json`, auto-memory | Your own overrides and Claude's private notes. Not shared. |

Everything above except the personal row is now tracked by git (see `.gitignore`).

## 1. The layers, and what goes where

Claude Code reads instructions from several places. Putting a rule in the wrong one is the most common reason it gets ignored.

| Layer | Who sees it | Put here |
|---|---|---|
| `CLAUDE.md` (repo root) | Main session **and every subagent** (except the built-in Explore/Plan) | Rules that apply to all work: project conventions, safety rules, the report format, orchestration guidance |
| Agent prompt (`.claude/agents/<domain>/<name>.md`) | Only that subagent; loaded in full at start | The role: who it is, its scope, workflow, token discipline and report |
| Skill (`.claude/skills/<name>/SKILL.md` + files) | Agents that list it in `skills:` (SKILL.md injected at start), or any session that invokes it. Its other files are read only when needed | Know-how more than one agent (or the main session) needs: procedures, rubrics, reference material, scripts |
| Agent memory (`.claude/agent-memory/<name>/MEMORY.md`) | That agent, every run (first 200 lines) | Lessons the agent learned from its own runs, until they are promoted into its prompt or a skill |
| Hook (`.claude/settings.json` → `hooks`) | Runs automatically; Claude can't skip it | Checks that must *always* happen. Deterministic code, not a request |
| Auto-memory (`~/.claude/projects/.../memory/`) | Main session; **not reliably** subagents (see below) | Personal working preferences and incident history |

**Key fact behind this setup:** don't rely on auto-memory reaching subagents. The docs say subagents don't load it ("the main conversation's auto memory isn't loaded"). Yet a test subagent in this repo did receive the memory *index*: a stale copy from when the session started, with no memory file contents. Either way it is the wrong channel. Rules like "`origin=` is a category, not a sourcebook", "2014 subclasses start at level 3" and "homebrew monsters score 0.4-0.6" lived only in memory, so agents got them partially and out of date, at best. They now live in `CLAUDE.md`, the documented channel every agent loads.

**Agent and skill changes take effect after a restart.** A running session keeps serving the agent definitions (and the memory snapshot) it loaded at startup. After editing anything under `.claude/agents/` or `.claude/skills/`, restart Claude Code, then run the smoke test in section 8.

## 2. The agents

Each agent is a Markdown file with YAML frontmatter:

```markdown
---
name: dnd-monster-balancer
description: Use to check and rebalance homebrew monsters ...   # what the router reads to pick an agent
tools: Read, Grep, Glob, Edit, Write, Bash                      # allowlist; leave out what it doesn't need
model: sonnet                                                   # default model; can be overridden per call
skills:                                                         # shared know-how injected at start
  - balance-monster
  - monster-stat-blocks
---
<system prompt: role, scope, workflow, report format>
```

Good practices this setup follows:

- **One job per agent, with a precise `description`.** The description is the routing signal. Say what it's for *and* what it's not for ("Not for creating monsters, use dnd-monster-creator"). Most of the existing agents already do this well.
- **Least privilege.** Read-only or narrow agents get only the tools they need. For example, `dnd-feature-summaries` has no Bash or Write.
- **One prompt per agent, model chosen per call.** There used to be `dnd-builds-haiku` and `combat-sim-haiku` copies of the Sonnet agents. They had drifted:
  - `dnd-builds-haiku` still said "expertise requires proficiency first" (no longer true).
  - It listed output pages that no longer exist (`weapons.html`, `spells.html`).
  - It shipped a repo-wide `rglob` script that *didn't* exclude `.claude/worktrees`, the exact hazard behind an earlier incident.

  Two copies of a prompt always drift. Now there is one agent, and the caller passes `model: "haiku"` when a cheap run is fine (per-call model override, documented in the subagent docs). The old files are backed up, not deleted (see *What changed*).
- **Subagents can nest** (up to 3 levels), but here they don't: the agents have no `Agent` tool. Delegation stays with the main session, which also does the verifying. Each extra layer is one more self-report nobody checks.

### Which model when

| Use | Model |
|---|---|
| Writing tests or hunting bugs, subjective tagging or classification across many items, migrations over shared code, new subclasses or builds | Agent default (Sonnet) |
| One feature, one combatant, one encounter, a lookup, a near-mechanical edit that's easy to check | `model: "haiku"` is fine |
| Small edits you can see in full | Don't spawn an agent; the main session does it |

This table comes from three recorded incidents (in Claude's memory): haiku agents wrote tests that couldn't fail, mis-tagged roughly half of a spell spot-check, and returned detailed but false completion reports during parallel migrations.

## 3. Briefing a subagent

A subagent starts cold: it sees `CLAUDE.md` and its own prompt, not your conversation. A good brief states:

1. **Scope:** the exact files or directories it may edit.
2. **Off-limits:** the shared files it must not touch (e.g. `Model/Content/Feature.py`, `Model/Ledger/`).
3. **Done:** what finished looks like ("every subclass in X has Y", "score in 0.4-0.6").
4. **Verify:** which command proves it (`./run_tests.sh -k ...`, `monster_score.py`, ...).

Every subagent ends with the report format from `CLAUDE.md`: **Files changed / Commands run / Not done / Concerns**. The file list is deliberately bare, so it can be compared mechanically with `git status`.

### Parallel agents

- Split by **disjoint** file sets, and name the shared files explicitly as off-limits.
- When scopes might overlap, use `isolation: "worktree"`. The agent then works in its own checkout under `.claude/worktrees/` on its own branch.
- Any repo-wide script must skip `.claude/` and `.git/`. Otherwise it edits other agents' worktrees too. This is in `CLAUDE.md`, and the hook catches direct edits there.
- If a change repeats the same override across 100 classes, prefer one generic method on the base class. Fewer edit sites leave fewer places for a wrong report to hide.

## 4. Verification: trust the tree, not the report

Two layers.

**Automatic: the `SubagentStop` hook.** When any subagent tries to finish, `check_subagent_edits.py`:

- reads *that agent's own* transcript to find the files it edited with Edit/Write, so parallel agents never block each other;
- compiles each edited `.py` file;
- flags any edit inside another agent's worktree;
- if something is wrong, exits with code 2, and Claude Code hands the message back to the agent as its next instruction.

It blocks at most once per stop (`stop_hook_active`), so an agent that can't fix the problem still ends and has to report it. Its limit: edits made through Bash (sed, scripts) don't show up as file edits in the transcript, and the verify skill covers those.

**On demand: the `verify-agent-work` skill.** Run it after agents report done:

```bash
python .claude/skills/verify-agent-work/verify.py --claimed Model/Grants.py CharacterContent/Features/CharacterFeats/GeneralFeats.py
python .claude/skills/verify-agent-work/verify.py --tests      # after the last agent in a batch
```

| Check | Catches |
|---|---|
| Changed files vs `--claimed` | "Updated 15 files" when 2 actually changed; files changed but not mentioned |
| Compile | Syntax errors |
| pyflakes undefined names | A name used inside a method but never imported. Compile *and* import both miss this, because Python only resolves it when the method runs |
| Import every changed module | Import-time errors, circular imports |
| Other worktrees | A stray script that edited another agent's checkout |
| `--tests` | Behaviour |

`SKILL.md` lists the checks a script can't do: off-limits files after every resume of an agent, spot-checking "skipped" items, re-grepping migration coverage, and sanity-checking content.

## 5. Permissions

`.claude/settings.json` was 71 one-off entries, mostly for scripts and folders that no longer exist (`Main.py`, `CharacterConfigs/`, old scratchpad paths). Two were risky:

- `git checkout *` could silently discard uncommitted work, including another agent's.
- `cat > *` allowed arbitrary file writes.

It now holds about 30 general rules: tests, format, typecheck, compile, the run scripts, the monster tools, read-only git, and the wikis the scrapers use. `git checkout -- / restore / reset --hard / clean / stash drop / stash clear / push` are in `ask`, so they always prompt.

`settings.local.json` (personal) was left alone. Your **user-level** `~/.claude/settings.json` applies to all your projects, so it was left alone too. It has about 245 accumulated allow entries, including broad ones like `git checkout *`, `git stash *`, `git rm *` and `pip install *`. Permission rules are checked deny → ask → allow, whichever file they come from. So this project's `ask` rules still make the destructive forms prompt here; in other projects they don't. Pruning that file by hand is worth doing at some point.

## 6. Folders: agents are roles, skills are know-how

The idea was to give every agent and skill its own folder, holding scripts, metadata and whatever else belongs to it. That is exactly right for skills, and only half right for agents, for these reasons.

**What Claude Code actually does with each folder** (from the docs):

- An **agent** is one Markdown file. Claude Code scans `.claude/agents/` recursively, and a file's identity comes only from its `name:` field, so subfolders are free to use for organising. But the agent's prompt is loaded **in full** every time it starts, and nothing else in its folder is loaded at all. An `.md` file with no `name:` beside it is silently treated as "documentation"; add a stray `name:` and it quietly becomes an agent.
- A **skill** is a folder: `SKILL.md` plus any reference files, examples and scripts. `SKILL.md` is the entry point. The other files are read **only when the task needs them** ("progressive disclosure"), and scripts are run, not read. An agent preloads a skill with `skills: [name]`, which injects that skill's `SKILL.md` when the agent starts. Several agents can preload the same skill, and the main session can invoke it too.

So a folder per agent, holding scripts and references, would be a skill without a skill's benefits: no on-demand loading, no sharing between agents, no access from the main session. The established split is:

| | Agent (`.claude/agents/<domain>/<name>.md`) | Skill (`.claude/skills/<name>/`) |
|---|---|---|
| Is | a **role**: who does the work | **know-how**: how the work is done |
| Holds | persona, scope, tools, model, workflow steps, report format | procedure, rubric, reference files, scripts |
| Loaded | in full when the agent starts | `SKILL.md` when preloaded or invoked; other files on demand |
| Shared | no | by every agent that lists it, and the main session |

**Agents are grouped by domain** (`builds/`, `features/`, `spells/`, `combat/`, `tooling/`), matching the areas in HOWTO section 10. **Skills stay flat**, one folder each, because that is the layout Claude Code discovers (`.claude/skills/<name>/SKILL.md`).

### What the split fixed

- **The monster creator never balanced its monsters.** CLAUDE.md requires every homebrew monster to score 0.4-0.6, but that procedure lived only inside `dnd-monster-balancer`. Now it is the `balance-monster` skill. The creator preloads it, its workflow ends with a balancing step, and the main session can use it when it edits a monster itself.
- **The MonsterAbility reference had silently gone stale.** `dnd-monster-ability-refactor` carried a hand-copied list of the structured ability classes. Comparing it with `Model/Creatures/MonsterAbilities.py` showed it:
  - missed seven subclasses (`MeleeOrRangedAttack`, `NamedAttackAction`, `CastSpellLegendaryAction`, `WaterBreathing`, `Flyby`, `PrimalBond`, `TinySwarm`);
  - missed `Multiattack(use_article=...)`;
  - still said "two damage types on one hit can't be structured", although `MeleeAttack`/`RangedAttack` gained `secondary_*` damage fields. The agent had been leaving convertible attacks as plain text.

  The `monster-stat-blocks` skill now has a script, `abilities.py`, that prints the reference **live from the code**, so it can't go stale again. Only the judgment rules (when a match is clean, how to verify, when to add a subclass) are written by hand.
- **One rubric for one chip.** `usage_tags` render as the same chip on feature cards and on spell cards, but each tagging agent carried its own copy of the rules. They now live side by side in the `usage-tags` skill. Their wording was moved, not merged: the deliberate differences (for example, "utility" is broad for spells but strict for features) are kept and listed explicitly, so a future change to either side happens in one visible place.
- **The creator now prefers structured abilities** where one fits exactly. Monsters come out in the form the refactor agent would otherwise have to convert them to, and the balance tools can read their numbers.

### Scripts over instructions

The most valuable thing a skill can hold is a script for work every run would otherwise redo by hand, and redo slightly differently each time. (This is the skill-creator guide's main lever: if every run writes the same helper, bundle it.) Each skill now has one, and `tests/test_skill_scripts.py` keeps them working against the real code:

| Script | Replaces | What it found on its first run |
|---|---|---|
| `balance-monster/check_monster.py` | Running `monster_score.py`, `monster_cr_compare.py` and an import check, then counting abilities and comparing field order by eye | **25 of 38 homebrew monsters fail the house rules:** 20 have more than 4 abilities (up to 9) and 5 score above 0.6. Most predate the 4-ability rule. Also, every homebrew monster that has a `description=` puts it right after `combatant_type`, not where the template said; the template was corrected to match. |
| `monster-stat-blocks/abilities.py` | A hand-copied list of ability classes | Seven missing subclasses and stale rules (see above) |
| `usage-tags/tag_report.py` | Ad-hoc grep and `json.dump` scripts | Spell tags live in `spells_<source>_extended.json`, merged *over* the source record since 2026-08-31, but `dnd-spell-usage-tags` still wrote into the source files, where the extended copy overrides them. Its edits would never have rendered. The agent was rewritten to use `tag_report.py set-spell`, which writes the right file in the exact format (2-space JSON, no trailing newline), so a one-spell change is a one-spell diff. All 661 feature and 566 spell tags validate. |
| `verify-agent-work/verify.py` (extended) | Manually diffing off-limits files; no way to check a worktree agent | `--off-limits` fails on a fenced file, and `--root` checks an isolated agent's worktree before merging |

The pattern behind all four: **a skill that says "check X" gets checked inconsistently; a skill that says "run this" gets checked the same way every time**, by every model tier. That matters most for the haiku agents, whose failures here have all been skipped or improvised checks.

### Why some things stayed in agent prompts

Task-specific workflow (the refactor agent's convert-and-diff loop, the action-tag rules for `action_type`/`duration`/`range` that only features have) is only used by one agent. Moving it into a skill would add indirection without sharing anything. **Make something a skill when a second user of it exists**, not before.

Scripts that people also run by hand (`Combat/Tools/monster_score.py`, `monster_cr_compare.py`) stay in `Combat/Tools/`; skills point at them instead of copying them.

### Guarding the structure

`tests/test_claude_config.py` runs with the normal test suite and fails when:

- an agent or skill has broken frontmatter, a `name` that doesn't match its file or folder, or no `description`;
- an agent preloads a skill that doesn't exist;
- two agents share a name;
- a skill link, a `.claude/...` script path or a hook command points at a missing file.

On its first run it found a real bug: `dnd-spell-usage-tags` had `"usage_tags": [...]` in its description, which makes the frontmatter invalid YAML. Claude Code's own parser happened to tolerate it this session, but the docs say unparseable agents are skipped, with the reason only in the debug log.

## 7. Self-improvement: agents learn from their runs

Every agent has `memory: project` in its frontmatter (the config test enforces it). Claude Code then gives the agent a folder, `.claude/agent-memory/<name>/`, injects its `MEMORY.md` (first 200 lines) into the agent's prompt on every run, and gives it instructions and Read/Write/Edit access to maintain it. This is the documented mechanism for "cross-session learning".

### The loop

```
agent hits a problem ──► writes a one-line lesson to its MEMORY.md ──► next run starts with it
        │                                                                   ▲
        └──► proposes prompt/skill changes in its report                    │
                         │                                                  │
main session verifies ───┴──► deletes wrong lessons, promotes proven ones ──┘
                              into the prompt or skill, adds lessons for
                              mistakes the agent didn't notice
```

The rules live in CLAUDE.md ("Learning from your runs" for agents, "Curate what agents learn" for the main session), so every agent gets them without 16 copies:

- **When to record:** a problem a future run would hit again. That means a wrong or stale instruction, a path or command that didn't work and what did, a check that caught a mistake, or a correction from the orchestrator.
- **Format:** one line, dated, the fix plus a short why. Observed facts only; no guesses and no "it went fine".
- **Curation:** fix or delete a wrong lesson instead of adding a contradicting one. Keep the file under 100 lines (the config test fails above that).
- **Report:** a new 5th section, **Lessons**, lists what changed in memory and any proposed prompt or skill change as exact text.
- **Nudges:** when the compile-check hook blocks an agent, its message asks the agent to record a lesson. `verify.py` lists memory changes separately, and the verify skill has a "curate what the agent learned" step.

### Why agents write to memory, not to their own prompt

You asked for agents that modify themselves. Memory *is* self-modification: the agent's next run starts with what it wrote. But it goes into a file that has a review step, not into the shared prompt:

1. **A prompt edit doesn't help the same session.** Running sessions serve the definitions cached at startup (we observed this), so a direct edit takes effect no sooner than a memory lesson.
2. **Agents' self-assessments have been confidently wrong here.** There were fabricated itemized reports and "failures are expected". A wrong lesson in memory is one line the orchestrator can delete. The same mistake written into a prompt or a shared skill would mislead every agent that loads it.
3. **Prompts and skills are shared and tested.** Several agents preload the same skill, and two parallel runs of one agent would race on its prompt file. Memory belongs to one agent, and agents re-read it before editing.
4. **Memory stays small.** Lessons are promoted into the prompt or skill once proven and then deleted, so prompts absorb the lessons without growing a pile of patches.

Memory is tracked by git (`.gitignore` has `!.claude/agent-memory/`), so every lesson shows up in `git diff` and gets committed like any other change.

### What it can't do

- An agent that doesn't *notice* its mistake can't learn from it. That's why the main session writes lessons for problems found during verification.
- Memory needs auto-memory to be on (it is by default).
- `memory` also grants Read/Write/Edit to agents whose tool list leaves those out (e.g. `dnd-feature-summaries` gains Write). CLAUDE.md limits them to their own memory folder outside their task scope.

## 8. Adding or changing an agent or skill

1. **Agent:** create `.claude/agents/<domain>/<name>.md` with `name` (matching the file name), a routing-quality `description` (when to use it *and* when not), a minimal `tools` list, a `model`, `memory: project` (required; the config test checks it), and `skills:` for any shared know-how it needs. Avoid `: ` inside the description; it breaks YAML.
2. Put only the role in the agent body: scope, workflow, checks, report. Rules for all agents go in `CLAUDE.md`. Know-how that a second agent (or the main session) also needs goes in a skill.
3. **Skill:** create `.claude/skills/<name>/SKILL.md` with `name` (matching the folder) and a `description` that says when to use it. Keep `SKILL.md` short (preloading injects all of it) and move detail into files it links to. Prefer a script that reads the code over a copied reference.
4. Give each a concrete verification step (the command that proves the task worked).
5. Run `./run_tests.sh tests/test_claude_config.py`. **Restart Claude Code**, then smoke-test the agent read-only: ask Claude to run it with `model: "haiku"` and the prompt below. Then try it on a real task and run the verify skill on the result. If it makes a mistake, add one line about that mistake, not a page.

   > Read-only smoke test; don't edit anything. List the skills injected into your context at startup and quote each one's first `# ` heading. Then state, from your instructions only, the rule your task depends on most (e.g. the balance band).

   If it reports no skills, or quotes text from an older version of the prompt, the session is still serving cached definitions: restart again.
6. Add agents to the table in HOWTO section 10. Commit; everything under `.claude/agents`, `skills` and `hooks` is tracked.

Optional, not enabled yet: `memory: project` in an agent's frontmatter gives it its own persistent notes in `.claude/agent-memory/<name>/`, shared through git. Good candidates are agents with a growing body of case knowledge, such as `dnd-test-bughunter` ("where bugs have hidden") or `dnd-monster-balancer`. Before relying on it, review what an agent writes there.

## 9. What changed on 2026-10-26

Fourth pass (improving the skills, section 6 "Scripts over instructions"):

- **Added** `check_monster.py` (balance-monster) and `tag_report.py` (usage-tags); extended `verify.py` with `--off-limits` and `--root`; gave every skill script `--help`.
- **Rewrote** each `SKILL.md` around its script, with descriptions that name the situations they're for (skills tend to under-trigger) and reasons in place of bare rules.
- **Fixed** `dnd-spell-usage-tags` (wrong file; see above) and the stat-block template's `description` position; the creator now finishes on `check_monster.py`.
- **Added** `tests/test_skill_scripts.py`.
- **Not done:** the skill-creator's full eval loop (with/without-skill subagent runs per test case) and its description optimizer. Many of these skills edit repo files, so parallel runs would clash in one tree. Both are worth running after the restart, one skill at a time.

Third pass (self-improvement, section 7):

- **Enabled** `memory: project` on all 16 agents, and tracked `.claude/agent-memory/` in git.
- **Added** the learning rules and the **Lessons** report section to CLAUDE.md, plus the orchestrator's curation duty.
- **Nudges:** the hook's block message, `verify.py`'s separate memory listing, and a curation step in the verify skill.
- **Config test:** every agent must have `memory: project`; each `MEMORY.md` must stay under 100 lines and belong to an existing agent.

Second pass (agents vs skills, section 6):

- **Grouped** the agents into `builds/`, `features/`, `spells/`, `combat/` and `tooling/` with `git mv` (history kept).
- **Added** the `balance-monster`, `monster-stat-blocks` (with `abilities.py`, `stat-block-template.md`, `monster-abilities.md`, `cr-guidelines.md`) and `usage-tags` skills.
- **Slimmed** the three monster agents to their roles: they preload the monster skills, the creator now balances, and the refactor agent's subclass list (via the skill) is complete again. The two tagging agents preload `usage-tags`.
- **Added** `tests/test_claude_config.py`, and fixed the invalid frontmatter it found in `dnd-spell-usage-tags`.
- **Smoke-tested** `dnd-monster-balancer` in the same session. It ran its *startup-cached* old prompt with no skills, and saw a stale memory index. Hence the restart rule and the corrected memory note in section 1. **Pending:** repeat the smoke test after a restart to confirm skill preloading from the new folders.

First pass:

- **Added** `CLAUDE.md`, the hook, the verify skill, and this file.
- **Rewrote** `.claude/settings.json` (curated permissions plus the hook). The old version is backed up in the session scratchpad.
- **Merged** `dnd-builds-haiku` into `dnd-builds` (bulk-edit guidance with the worktree exclusion fixed, corrected output-page list) and `combat-sim-haiku` into `combat-sim` (removed self-delegation and the `Agent` tool). The old files are in the session scratchpad under `retired-agents/`.
- **Updated** three agent descriptions that pointed at `dnd-builds-haiku`, and HOWTO section 10.
- **Switched** `dnd-equipment` from haiku to sonnet, and added the worktree exclusion to its bulk-edit steps.
- **Moved** five project rules from Claude's private memory into `CLAUDE.md`, so subagents see them.
- **`.gitignore`** now tracks `.claude/agents/`, `.claude/skills/`, `.claude/hooks/` and `.claude/settings.json`.

### Still worth doing

- Prune the ~245 user-level permission entries (see section 5).
- Decide what to do about the 25 homebrew monsters that fail `check_monster.py --all-homebrew` (20 over the 4-ability rule, 5 too strong). Either rebalance them with `dnd-monster-balancer`, or grandfather the ones that predate the rule.
- Four agents default to haiku: `dnd-feature-action-tags`, `dnd-feature-summaries`, `dnd-spell-summaries` and `dnd-spell-usage-tags`. The summary and usage-tag work is near-mechanical. `dnd-feature-action-tags` makes judgment calls, so watch its first few runs with the verify skill and switch it to `sonnet` if quality slips. (`dnd-equipment` was switched to `sonnet` because it edits engine code in `Model/Inventory.py`. For small gear edits to one build, call it with `model: "haiku"`.)
- 15 agents repeat a "Token discipline" block. It's harmless, but a change has to be made in 15 places; a candidate for moving into `CLAUDE.md` later.
