---
name: balance-monster
description: Balance a homebrew D&D monster (ExtendedCombatantData in Combat/Monsters/CR_*/monsters_homebrew.py) so its monster_score.py "score" lands in 0.4-0.6 for its CR, and check it is done (implied CR, the 4-ability house rule, field order) with one script. Use after creating or editing any homebrew monster, and whenever someone asks whether a monster is balanced, too strong, too weak, "too swingy", right for its CR, or wants it made scarier/easier, even if they don't say "balance".
---

# Balance a homebrew monster

The goal is a monster that plays like an average monster of its CR, without losing what makes it that monster. `Combat/Tools/monster_score.py` is the ground truth: it measures each attribute against the official monsters of the same CR. You tune **numbers** until it agrees. Which files you may edit is in the `monster-stat-blocks` skill's scope guard: homebrew files, or `monsters.py` files marked hand-edited.

## Start and finish with the checker

```bash
python .claude/skills/balance-monster/check_monster.py "<exact combatant_type>"   # one or more names
python .claude/skills/balance-monster/check_monster.py --all-homebrew             # audit everything
```

It prints, per monster:

- `score`, with a FAIL outside 0.40-0.60;
- implied CR, flagged CHECK when it's more than 1 CR from `cr=`;
- the three scored attributes furthest from the tier mean, which is what to tune first;
- the house-rule ability count;
- whether the `super().__init__` fields are in template order.

It exits 1 on any FAIL, so **a clean run is the definition of done**. Run it before you edit (the baseline) and after every round. It uses the same code as `monster_score.py` and `monster_cr_compare.py`, so it can't disagree with them.

## How the score works, and why it steers the way it does

- `score` (the first column of `monster_score.py`) is the target; 0.5 is dead average. `mean`, `median`, `min`, `max`, `geomean` and `vote_share` are other views of the same z-scores. They help diagnose, but they aren't the goal: steering by them is how a monster at score 1.0 once got rationalised as "fine".
- `score` = Φ(avg_z·√23). The √23 amplifies: a small average lean gets far from 0.5 quickly. So the attribute z-scores must roughly **cancel** (sum within about ±1.3), and fixing 2-4 big outliers beats nudging everything.
- `dmg`/`dpr` are shown but never scored (a fragile regex reads them from ability text). Don't chase them; the checker already leaves them out of its outliers.
- **Action economy is expensive.** At low CR each extra bonus action is about +1.9 z. Fold minor options into a trait or an existing action instead of adding entries.
- **House rule: at most 4 ability entries** (traits + actions + bonus actions + reactions; Multiattack counts), preferably at least one trait. Stat blocks that run quickly at the table matter more here than completeness. Cutting entries lowers `score`, so compensate with HP, AC or ability scores.

## Workflow

1. **Baseline:** `check_monster.py "<name>"`. If it already passes, say so and stop; don't edit a monster that isn't broken.
2. **Diagnose:** start from the checker's outliers. For the full table (value, tier mean/median/stdev/min/max, signed `z` where positive always means stronger) run `python Combat/Tools/monster_score.py -v "<name>"`. Too strong: reduce the largest positive `z`s. Too weak: raise the largest negative ones. A `min` far below the tier floor usually means a dump stat or a missing defence, worth fixing even when `score` is fine.
3. **Edit the fields:**

   | Breakdown label | Field(s) |
   |---|---|
   | HP | `hp=` (rescale `hp_formula=` dice to roughly match) |
   | AC | `ac=` |
   | STR...CHA | `ability_scores={Ability.<X>: N}` |
   | ATK | structured `MeleeAttack`/`RangedAttack` `attack_bonus=`, or the `+N` in freeform `"Melee/Ranged Attack Roll: +N, ..."` text |
   | STR-SV etc. | `saving_throws={Ability.<X>: N}` |
   | DC | structured `SavingThrowEffect.dc=`, or `DC N` in freeform text |
   | C-IMM / D-IMM / D-RES / D-VULN | length of `condition_immunities` / `damage_immunities` / `damage_resistances` / `damage_vulnerabilities` (only types that fit the concept) |
   | ACT / B-ACT | number of `actions=` / `bonus_actions=` entries (never gut a signature ability) |
   | SPD | `speed_ground_ft=` / `speed_fly_ft=` / `speed_climb_ft=` |

   When an attack bonus or DC moves, check that its damage still reads as plausible for the CR. **Keep what the monster is:** its signature traits, damage types, name and `cr=`. The user chose the concept; you're tuning numbers.
4. **Re-check** with `check_monster.py`. Do at most 2-3 rounds of diagnose and edit. Past that, single-digit tweaks have diminishing returns.
5. **If it won't converge**, stop and report the remaining score. Then either say what larger change is needed (usually reworking a signature ability), or that `cr=` looks wrong (the implied CR says so), and ask before re-tiering.

**Batch:** pass every name to `check_monster.py` at once (or use `--all-homebrew`), then work through the failures one at a time.

**Report** each monster's starting and final `score`, implied CR, and what you changed.
