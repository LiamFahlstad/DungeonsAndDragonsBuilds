# Working with Claude Code agents in this repo

How the agent setup is organised, why each piece exists, and how to use and extend it. The patterns follow Anthropic's Claude Code documentation ([subagents](https://code.claude.com/docs/en/sub-agents), [hooks](https://code.claude.com/docs/en/hooks)) and the lessons this repo learned the hard way.

## The short version

| Piece | File | Job |
|---|---|---|
| Shared context | `CLAUDE.md` | Project rules, commands, and how agents behave and report. **Every session and every subagent loads it.** |
| Specialists | `.claude/agents/*.md` | One focused expert per kind of task: its own prompt, tool list and default model. |
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
| Agent prompt (`.claude/agents/<name>.md`) | Only that subagent | Domain knowledge for one kind of task: file layout, APIs, worked examples, task-specific checks |
| Skill (`.claude/skills/<name>/SKILL.md`) | Loaded on demand (by name, or when its description matches) | A repeatable procedure with steps and maybe a script, such as verification |
| Hook (`.claude/settings.json` → `hooks`) | Runs automatically; Claude can't skip it | Checks that must *always* happen. Deterministic code, not a request |
| Auto-memory (`~/.claude/projects/.../memory/`) | **Main session only. Subagents never see it.** | Personal working preferences and incident history |

**Key fact behind this setup:** subagents do *not* load auto-memory. Before this change, rules like "`origin=` is a category, not a sourcebook", "2014 subclasses start at level 3" and "homebrew monsters score 0.4-0.6" lived only in memory. Every agent you dispatched worked without them. They now live in `CLAUDE.md`.

## 2. The agents

Each agent is a Markdown file with YAML frontmatter:

```markdown
---
name: dnd-monster-balancer
description: Use to check and rebalance homebrew monsters ...   # what the router reads to pick an agent
tools: Read, Grep, Glob, Edit, Write, Bash                      # allowlist; leave out what it doesn't need
model: sonnet                                                   # default model; can be overridden per call
---
<system prompt: domain knowledge, workflow, report format>
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

## 6. Adding or changing an agent

1. Create `.claude/agents/<name>.md` with `name`, a routing-quality `description` (when to use it *and* when not), a minimal `tools` list, and a `model`.
2. Put only domain-specific knowledge in the body. Anything that applies to all agents goes in `CLAUDE.md` instead. Don't copy it.
3. Give it a concrete verification step (the command that proves the task worked) and any task-specific report items.
4. Try it on a real task, then run the verify skill on the result. If it makes a mistake, add one line to its prompt about that mistake, not a page.
5. Add it to the table in HOWTO section 10. Commit the file; it's tracked now.

Optional, not enabled yet: `memory: project` in an agent's frontmatter gives it its own persistent notes in `.claude/agent-memory/<name>/`, shared through git. Good candidates are agents with a growing body of case knowledge, such as `dnd-test-bughunter` ("where bugs have hidden") or `dnd-monster-balancer`. Before relying on it, review what an agent writes there.

## 7. What changed on 2026-10-26

- **Added** `CLAUDE.md`, the hook, the verify skill, and this file.
- **Rewrote** `.claude/settings.json` (curated permissions plus the hook). The old version is backed up in the session scratchpad.
- **Merged** `dnd-builds-haiku` into `dnd-builds` (bulk-edit guidance with the worktree exclusion fixed, corrected output-page list) and `combat-sim-haiku` into `combat-sim` (removed self-delegation and the `Agent` tool). The old files are in the session scratchpad under `retired-agents/`.
- **Updated** three agent descriptions that pointed at `dnd-builds-haiku`, and HOWTO section 10.
- **Switched** `dnd-equipment` from haiku to sonnet, and added the worktree exclusion to its bulk-edit steps.
- **Moved** five project rules from Claude's private memory into `CLAUDE.md`, so subagents see them.
- **`.gitignore`** now tracks `.claude/agents/`, `.claude/skills/`, `.claude/hooks/` and `.claude/settings.json`.

### Still worth doing

- Prune the ~245 user-level permission entries (see section 5).
- Four agents default to haiku: `dnd-feature-action-tags`, `dnd-feature-summaries`, `dnd-spell-summaries` and `dnd-spell-usage-tags`. The summary and usage-tag work is near-mechanical. `dnd-feature-action-tags` makes judgment calls, so watch its first few runs with the verify skill and switch it to `sonnet` if quality slips. (`dnd-equipment` was switched to `sonnet` because it edits engine code in `Model/Inventory.py`. For small gear edits to one build, call it with `model: "haiku"`.)
- 15 agents repeat a "Token discipline" block. It's harmless, but a change has to be made in 15 places; a candidate for moving into `CLAUDE.md` later.
