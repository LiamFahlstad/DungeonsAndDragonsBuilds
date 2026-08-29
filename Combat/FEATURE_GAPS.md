# Combat Simulator — Feature Gap Analysis

Fresh audit (2026-08-22) of `Combat/CombatUIQt/` and `Combat/Definitions.py`, verified directly against
the current code — not carried over from any earlier version of this file. Framed around what actually
costs a GM efficiency (extra manual bookkeeping, extra clicks) or reliability (wrong data logged, silent
no-ops, state that quietly drifts from the table) during a live session, ranked most to least critical.

Several claims from an earlier version of this doc turned out to be wrong or stale once checked against
the code — see **Already Handled** at the bottom before treating anything here as new work.

## Critical

1. **Legendary/Lair/Mythic actions, Legendary Resistance, and Recharge abilities are fully scraped but
   have zero interactive tracking.** Every generated monster file under `Combat/Monsters/CR_*/` carries
   `legendary_actions`, `lair_actions`, `mythic_actions`, `legendary_resistances`, and recharge-tagged
   actions (`ExtendedCombatantData` in `Definitions.py`) — real, correctly-scraped rules text. In the UI,
   `dialogs_mixin.py` only prints them as static paragraphs inside "More Info" (lines ~625-627). There's
   no per-round legendary-action budget, no lair-action trigger on initiative count 20, no recharge d6
   roll at the top of a monster's turn, and no auto-negate-a-failed-save-and-decrement for Legendary
   Resistance. This data is richest on exactly the CR 10+ boss encounters where forgetting one of these
   mid-fight is most costly — and the tool currently gives the GM no help running them despite already
   having the content loaded.

2. **Silent no-op on a bad amount.** `_apply_damage`, `_apply_heal`, and `_apply_temp_hp`
   (`damage_mixin.py`) each wrap `int(self.damage_input.text())` (etc.) in a bare `try/except ValueError:
   return` — a mistyped or non-numeric amount produces *zero* visible feedback. Compare: forgetting to
   pick a damage type on the same form correctly pops a `QMessageBox` warning. At a noisy table, a GM who
   fat-fingers an amount and hits Enter has no way to tell "nothing happened" from "it worked" without
   double-checking the HP bar — a small thing that directly undermines trust in the log being accurate.

## Significant

3. **No dice roller for damage.** `rolls_mixin.py` covers d20s with advantage/disadvantage (initiative,
   saves, checks) but there's no equivalent for damage dice — every hit's `2d6+3`-style total has to be
   computed by hand before it's typed into the Damage field. Everything else numeric in this tool (spell
   slots, HP math, turn order) is automated; damage totals are the one place that still requires outside
   arithmetic on every single attack.

4. **Undo is one global LIFO stack, not per-character.** `_undo_last` (`logging_mixin.py`) only reverses
   the single most recent action across the *entire* encounter. If Goblin B, Goblin C, and the party
   Wizard each acted after the mistake you want to fix, undoing it means undoing all three actions in
   between too (or leaving the mistake in). There's also no visible, clickable history — only the
   read-only Encounter Log text and blind sequential Ctrl+Z — so recovering from an error buried a few
   actions back is disproportionately disruptive mid-round.

5. **No general saving-throw dialog.** The Concentration Check dialog (`damage_mixin.py`) is the only
   place with the "enter a roll, compare to a DC, log the result" pattern — every other saving throw
   (a Fireball's DEX save, a poison's CON save, a monster's WIS save vs. a spell) has no equivalent, even
   though ability scores and saving-throw modifiers are already loaded per character. The GM resolves
   these entirely outside the tool and then manually applies whatever conditions/damage result.

## Worth Noting, Lower Priority

6. **Condition rules text is complete but purely informational.** `ConditionRule` in `Definitions.py`
   carries accurate, complete 2024 rules for every condition (Poisoned → disadvantage on attacks/checks,
   Prone → attack advantage/disadvantage depending on range, Paralyzed → auto-fail STR/DEX + crits within
   5 ft, etc.), shown on click as a popup. Nothing reads these rules mechanically — but that's arguably by
   design, since there's no attack-roll or ability-check system in this tool at all (the GM rolls physical
   dice and types in results/damage). Worth a deliberate call on scope before treating this as a gap:
   either this stays a GM-facing rules reference on purpose, or the tool grows an attack-roll system that
   would make enforcement meaningful.

7. **Exhaustion is a single badge, not six levels.** `Condition.EXHAUSTION` is one flat condition even
   though its own `ConditionRule` text describes six cumulative levels with an escalating penalty. A
   character at Exhaustion 4 looks identical on their card to one at Exhaustion 1.

## Already Handled

Confirmed working in the current code — don't re-flag these:

- **Damage resistance/vulnerability/immunity** — fully implemented and applied via the "Apply (Check
  Resist)" button (`damage_mixin.py:_damage_type_modifier`): immune → 0, resisted → half, vulnerable →
  double.
- **Concentration breaks on incapacitation, knockout, and death** — auto-enforced
  (`conditions_mixin.py`'s `INCAPACITATING_CONDITIONS` check, and explicit removal on knockout/death in
  `damage_mixin.py`), and as of this session, removing Concentrating by *any* path (including the Ctrl+C
  shortcut and a failed save) now also ends the underlying `active_spells` entry instead of leaving it
  ticking — see `spells_mixin.py:_end_concentration_spells`.
- **Casting a new concentration spell correctly ends the old one** — handled in
  `spells_mixin.py:_apply_cast_spell`.
- **Multi-target damage/heal/temp HP** — already supported; `target_characters` is a list (Shift+right-click
  to multi-select) and every apply loop iterates it.
- **"Apply as Condition" can now target the caster or the target(s)** — the Cast Spell dialog has separate
  "Apply to Source" / "Apply to Target(s)" buttons (`spells_mixin.py:_apply_spell_as_condition`, now takes
  `apply_to_target`); a debuff like Hold Person correctly badges the affected creature(s) instead of the
  caster, while the caster is still always recorded as the condition's source for log/stat attribution.
  The main "Cast" button (`_apply_cast_spell`) is unchanged and stays caster-only by design — Concentration
  and its duration timer are inherently a property of the caster, not the target, per RAW.
