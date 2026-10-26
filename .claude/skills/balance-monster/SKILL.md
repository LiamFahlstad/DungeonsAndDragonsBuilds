---
name: balance-monster
description: Balance a homebrew D&D monster (ExtendedCombatantData in Combat/Monsters/CR_*/monsters_homebrew.py) against Combat/Tools/monster_score.py until its "score" is in 0.4-0.6 for its CR. Use after creating or editing any homebrew monster, or when asked whether a monster is balanced.
---

# Balance a homebrew monster

`Combat/Tools/monster_score.py` is the ground truth for "is this balanced for its CR". You tune the stat block's numbers until it agrees, without changing what the monster is. Which files you may edit is covered by the `monster-stat-blocks` skill's scope guard: homebrew files, or `monsters.py` files marked hand-edited.

## What "balanced" means

`monster_score.py "<name>" -v` fits each CR tier's mean/stdev (from *official* `monsters.py` stat blocks only) across HP, AC, the six ability scores, attack bonus, per-ability saving throws, save DC, damage/condition immunities/resistances/vulnerabilities, action economy and speed. It then reports the monster's percentile through several aggregations.

- **`score` (the first column) is the target.** 0.5 is dead average for the CR; the goal band is **0.4-0.6**.
- `mean`, `median`, `min`, `max`, `geomean` and `vote_share` are other views of the same z-scores. Use them to diagnose problems, never as the target. A low `min` next to a fine `score` means one attribute is a severe outlier.
- `dmg`/`dpr` are shown but never scored. They come from a fragile regex over ability text, so don't chase them.
- `score` = Φ(avg_z·√23), so the attribute z-scores must roughly cancel (sum within about ±1.3). At low CR each extra bonus action is about +1.9 z: fold minor options into traits or actions instead of adding more bonus actions.
- House rule: at most **4 `MonsterAbility` entries in total** (traits + actions + bonus actions + reactions; Multiattack counts), preferably at least one trait. Cutting actions lowers `score`, so compensate with HP, AC or ability scores.

## Workflow

1. **Baseline.** Run `python Combat/Tools/monster_score.py -v "<exact monster name>"`. If the name is ambiguous or not found, grep for the exact `combatant_type=` string. If the monster is already in 0.4-0.6, say so and stop.
2. **Diagnose.** The `-v` output lists each attribute with its value, the tier's mean/median/stdev/min/max, and a signed `z` (positive always means stronger). Sort by `|z|`:
   - score > 0.6: reduce the largest positive `z`s;
   - score < 0.4: raise the largest negative `z`s;
   - fix 2-4 outliers rather than nudging everything. A `min` far below the tier floor usually means a dump stat or a missing defence, which is worth fixing even when `score` is fine.
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

   When you change an attack bonus or a save DC, check that its damage still reads as plausible for the CR. **Never change what the monster is** to fit the band: keep its signature traits, damage types, name and `cr=`.
4. **Re-check** with `python Combat/Tools/monster_score.py "<name>"`. Do at most 2-3 rounds of diagnose and edit in total.
5. **If it won't converge**, stop and report the remaining score. Then either say what larger change is needed (usually reworking a signature ability), or that the `cr=` tag looks wrong, and ask before re-tiering.
6. **Confirm implied CR** with `python Combat/Tools/monster_cr_compare.py "<name>"`. It should roughly match `cr=`.
7. **Import check** every class you touched:
   ```bash
   python -c "from Combat.Monsters.CR_<tier>.monsters_homebrew import A, B; A(); B(); print('ok')"
   ```

**Batch mode:** `monster_score.py` accepts several names. Get every baseline in one call, work through the out-of-band ones one at a time, and do one import check at the end.

**Report** the final `score` and implied CR for each monster.
