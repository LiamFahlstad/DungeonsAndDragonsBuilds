---
name: review-house-rules
description: Review a change (working tree, staged, a branch or a subagent's output) against this repo's own rules that no test enforces - origin= is a category not a sourcebook, 2014 subclasses start at level 3 and are skipped when a 2024 reprint exists, generated monsters.py and scraped spell JSON are never hand-edited, Core/Rules constants instead of magic numbers, order-insensitive apply(), homebrew monster limits - with a script that flags the mechanical ones on added lines and lists the verification each changed file calls for. Use when reviewing code before a commit or PR, after a subagent reports done (alongside verify-agent-work, which checks *what* changed, while this checks *whether it follows the rules*), when asked "is this right?" or "review this", and as the checklist the code-reviewer agent preloads.
---

# Review against the house rules

`verify-agent-work` answers "did the agent change what it said?". The test suite answers "does it compile, layer and render as before?". This skill answers the third question: **does the change follow the rules this repo has learned**, the ones in CLAUDE.md and the agent prompts that no test can see.

## 1. Run the script

```bash
python .claude/skills/review-house-rules/check_diff.py                 # working tree + untracked vs HEAD
python .claude/skills/review-house-rules/check_diff.py --staged        # what is about to be committed
python .claude/skills/review-house-rules/check_diff.py --base main     # a whole branch
python .claude/skills/review-house-rules/check_diff.py CharacterContent/Features/   # limit to paths
```

It checks **added lines only**, because old code that breaks a rule is not precedent and not this change's fault. It prints `path:line [check] message` per finding, then the commands the changed files call for (tests, `snapshot_diff.py`, `tag_report.py check`, `check_monster.py`, config tests, memory curation, screenshots). **Run those commands too**: a review that didn't run them hasn't checked behaviour.

| Check | Rule |
|---|---|
| `generated-file` | A plain `Combat/Monsters/CR_*/monsters.py` or `__init__.py` is overwritten by `generate_monsters.py`. Fix the generator or put the monster in `monsters_homebrew.py`. Files whose header says "hand-edited" (CR_10) are exempt. |
| `spell-source` | `spells_{dnd2024,dnd5e,aidedd}.json` are scraper output. Tags go in `_extended.json`, descriptions in `_improved.json`. |
| `origin` | `origin=` is the category the player reads ("Origin Feat", "Bard Level 9", "Path Of The Ancestral Guardian Barbarian Level 3"), never a book, edition or year. |
| `rules-constant` | `range(1, 21)` and `(score - 10) // 2` come from `Core/Rules.py` (`ALL_LEVELS`, `ability_modifier()`). |
| `debug` | No `print()` / `breakpoint()` left in `Model/`, `Core/`, `CharacterContent/`. |
| `scratch-file` | Scratch scripts go in the scratchpad, never the repo. |
| `2014-reprint` | A new 2014 subclass whose name has a 2024 file. |

## 2. Read the diff for what a script can't see

Work through `git diff` (or the agent's claimed files) with these questions. Each is a rule that has been broken here before.

**Content (features, feats, subclasses, spells)**
- 2014 subclass: does every feature that the source text grants at 1st or 2nd level land in `SubclassLevel3`? Is there a **renamed** 2024 reprint (School of Evocation → Evoker), which the script can't catch? Where a 2014 subclass feature overlaps a 2024 base-class feature, the 2024 base feature wins.
- Is an upgrade of an earlier feature wired as `data.add_feature(Child(), extends=Parent)` and not as a standalone grant? (`feature-extension-auditor` has the rule.)
- Does `apply()` only *record*, with anything that depends on another stat as a formula (`lambda cs: ...`)? Does a proficiency-granting feature grant it in its own `apply()`, not in the builder?
- Do `usage_tags` follow the `usage-tags` rubric, and does the card's text match `apply()`?
- Is the rules text from the 2024 PHB (or the stated source), and are the numbers the rule's own (a feature's "+2" stays in the feature)?

**Monsters**
- Homebrew: at most 4 `MonsterAbility` entries in total (preferably one trait), field order as in the template, and `check_monster.py` passing with the `score` column in 0.4-0.6, not the median or mean.

**Builds and snapshots**
- Every golden change explained by the change itself (`snapshot-diffs` skill)? A changed golden for a build the change shouldn't touch is a finding.
- Placeholder player choices marked and reported? Multiclass prerequisites met, not bumped?

**Scope and hygiene**
- Only the files the task named? No edit under `.claude/worktrees/`? No reformatting of unrelated files (`format.sh` hits the whole repo; `format_changed.sh` doesn't)?
- New behaviour has a test whose expected value comes from the rules, not from the code's output (the `test-bughunter` standard)?
- A repeated override across many classes that should be one method on the base class?

## 3. Report

List findings most severe first: `path:line`, the rule, what the code does, and the fix. Say which commands you ran and their real results. When you let a script finding stand (say, a generator rerun legitimately rewrote `monsters.py`), say why in one line. If nothing is wrong, say so plainly. Don't invent nits to fill the report.
