---
name: spell-mechanics
description: Spells' combat effects - what casting a spell rolls and does (saving throw or attack roll, which ability, damage dice and types, half on a save, a condition or badge and how long it lasts, upcasting, cantrip scaling, healing, Temporary Hit Points, or nothing to apply at all), written as CombatEffect objects in the spell's class (CharacterContent/Spells/SpellClasses, its combat_effects() method) and used by the combat UI's Custom Effect picker instead of reading the spell's text. The same CombatEffect model features and monster abilities use. Holds the format, the rubric for each field, and a script that checks every spell's effects, lists spells without them (by level, class or campaign), drafts them from the text as Python for review, writes reviewed drafts into each spell's class (turning a JSON spell into a class first) and compares them with the text reading. Use when adding, reviewing or fixing a spell's combat effects, when a spell fills the Custom Effect form wrongly, when a campaign's spells should be checked, or when someone asks why a spell's picker row says "Read from its rules text".
---

# Spells' combat effects

The combat UI's Custom Effect dialog fills its form from a spell
(`spell_option()` in `Combat/CombatUIQt/effect_options.py`). A spell whose
`combat_effects()` returns a list is filled from it; any other spell is read
from its rules text with regexes, which the GM then has to check. Combat
effects replace that guess with checked data, so every one must be right.

Spells, features and monster abilities all describe themselves with the same
model, `CombatEffect` (`Model/Content/CombatEffect.py`; its docstring has every
field). The plan behind this is `Notes/combat-effects-plan.md`.

## Where they live

In the spell's **class**, `CharacterContent/Spells/SpellClasses/<Level>.py`
(`Cantrips.py`, `Level1.py`, ...; see `SpellFactory/ClassSpell.py`):

```python
class Fireball(ClassSpell):
    rules = SpellRules(...)

    def combat_effects(
        self, character: CharacterView | None = None
    ) -> list[CombatEffect]:
        return [
            CombatEffect(
                roll=EffectRoll.SAVE,
                save_ability=Ability.DEXTERITY,
                half_on_success=True,
                damage=(CombatDamage("8d6", DamageType.FIRE, upcast="1d6"),),
            )
        ]
```

The list holds:

- one effect per way to cast it: usually one; several for options with
  different mechanics (Command's five, each `name="Command: Grovel"`) or
  steps of one casting (Ice Knife's shard, then its explosion), or
- nothing (`[]`) when the spell has nothing to apply to a creature in a fight.

A spell whose `combat_effects()` returns `None` (no method, or a JSON spell)
is "not described yet" and is read from its text.

**Most spells are still JSON** (no class yet). You don't convert them by
hand: `add` turns the spell into a class (with
`CharacterContent/Spells/SpellClassConverter.py`, which moves its improved
description and usage tags into the class too, checks the class says what
the JSON said, and takes the spell out of the companion files) and gives it
your effects. **About 20 spells can't be classes** (a Dunamancy school or
class, DI-063; no components, DI-062): `todo` says so, and for those `add`
writes the effects as JSON, as `to_dict()` writes them, into
`CharacterContent/Spells/spells_<source>_combat_effects.json`. Never edit
those files or the source spell JSON by hand.

Leave out every number that belongs to the caster (`dc`, `attack_bonus`): the
picker works those out. Leave out every field at its default.

## Tools

```bash
S=.claude/skills/spell-mechanics/spell_mechanics.py
python $S todo --campaign time_loop_pr          # what's missing, and where each goes (also --level N, --class Wizard, --name X)
python $S draft --level 2 --out <scratchpad>/draft.py   # drafts as Python + a review sheet with each spell's full text
python $S add <scratchpad>/draft.py             # check the reviewed EFFECTS, write each into its class
python $S compare --level 2                     # where the effects and the text reading disagree
python $S check                                 # run before you report: exit 1 on any problem
```

The draft file is a Python module: `EFFECTS = {"Spell name": [CombatEffect(...), ...]}`,
each spell's checks as comments above it, imports included. Write drafts in
the scratchpad, never the repo. A draft the model refuses (a damage type to
choose with no choices yet) is left as a dict with the reason; `add` refuses
it until you write it as `CombatEffect(...)`. `add` writes nothing if any
spell in the file has a problem, and refuses to replace effects a spell has
already unless you pass `--force`. Use that only when you are fixing that
spell on purpose; it replaces the whole `combat_effects()` method, hand
edits included.

To fix one spell that has a class, you can also edit its `combat_effects()`
directly; then run `check` and the tests below.

## Procedure

1. `todo` for your filter, then `draft --out`.
2. For **every** spell, read its full description on the review sheet and fix
   the draft field by field against the rubric below. The draft comes from the
   regex reading these effects exist to replace. "Improved description agrees"
   only means the two automatic readings agree, not that they are right.
3. `add`, then `compare` for your filter. Every difference it lists must be one
   you made on purpose (the reason is usually in the effect's notes).
4. `check`, and `./run_tests.sh -q tests/test_spell_classes.py tests/test_spell_combat_effects.py tests/test_combat_ui_effect_options.py tests/test_picker_rows.py`.
   A picker-row golden that changes is a spell now described: read the
   diff (the `snapshot-diffs` skill) before `UPDATE_SNAPSHOTS=1`.

## Rubric

Names are the Python ones; `Ability`, `Condition` and `DamageType` come from
`Core.Definitions`, the rest from `Model.Content.CombatEffect`.

- **`roll`.** `EffectRoll.ATTACK` when the caster makes a spell attack, or a
  weapon attack the spell grants (True Strike). `EffectRoll.SAVE` when the
  *target* rolls a save that decides the effect. Leave it out
  (`EffectRoll.NONE`) when it just happens: healing, buffs, auto-hit damage
  (Magic Missile), or a condition with no save (Invisibility). If a spell has
  both an attack and a save, give each its own effect (Ice Knife: "Ice Knife:
  shard", then "Ice Knife: explosion").
- **`save_ability`** (with a save): `Ability.DEXTERITY`. **`half_on_success`**
  only when the text says half as much damage on a success. **`repeat_save`**
  only for "at the end of each of its turns, the target repeats the save,
  ending the effect on a success" (Hold Person, Tasha's). Other later saves,
  such as Sleep's second save, an Athletics check to escape, or a save when
  it enters the area, go in `notes`.
- **`damage`.** A tuple of `CombatDamage(dice, damage_type)`, only the damage
  the hit or failed save deals *now*. Damage on later turns, on moving
  through an area, or on a later hit goes in `notes` (Witch Bolt's 1d12,
  Spike Growth, Hunter's Mark, Ensnaring Strike). One part per damage type.
  `upcast="1d6"` goes only on the part the higher-level paragraph names.
  `cantrip=((5, "2d8"), (11, "3d8"), (17, "4d8"))` only when the dice
  themselves grow (Eldritch Blast's extra beams are `instances`). `add_modifier=True`
  when the text adds "your spellcasting ability modifier". When the caster
  picks the type: `CombatDamage("2d6", None, (DamageType.ACID, DamageType.COLD,
  ...))`. Damage only some targets take is a part with `when`, what follows
  "if": Divine Smite's `CombatDamage("1d8", DamageType.RADIANT, when="the
  target is a Fiend or an Undead")`. When the dice *replace* the others for
  some targets, make a second effect instead ("Toll the Dead (hurt target)"
  with d12s).
- **`instances`.** `CombatInstances(count, upcast=0, cantrip=..., noun="")`
  when one casting rolls and deals its damage several times, at one target or
  several: Scorching Ray `CombatInstances(3, upcast=1, noun="ray")`, Magic
  Missile's darts, Eldritch Blast `CombatInstances(1, cantrip=((5, 2), (11,
  3), (17, 4)), noun="beam")`. The damage is one instance's. The dialog fills its
  Times box with the count. Extra *targets* per slot level are not
  instances: they go in `notes`.
- **`healing`.** `CombatHitPoints(dice, upcast=..., add_modifier=...)` for Hit
  Points each target regains now (Cure Wounds, Healing Word); the picker
  fills the form's amount box with it, set to Healing. `upcast` is dice
  or a number, as text (Heal's `upcast="10"`). Hit Points regained later, or "equal to half the
  damage dealt" (Vampiric Touch), go in `notes`.
- **`temp_hp`.** The same for Temporary Hit Points (False Life, Armor of
  Agathys), with the Temp HP box. An effect has at most one of `damage`,
  `healing` and `temp_hp` (the form has one amount box): a spell that deals
  damage puts its Hit Points in `notes`. When the caster gets them ("You gain
  ..."), say so in `notes`: the dialog gives them to its targets.
- **`conditions`.** A tuple of `CombatCondition(...)`, each a rules condition
  (`CombatCondition(Condition.PRONE)`) the effect gives, **or the spell's own
  name as a badge** on its targets (`CombatCondition("Bless")`; also Faerie
  Fire, Shield, Hunter's Mark). Use a badge when the spell lasts and marks its
  targets with something the form can't show (a bonus, a rider), and not for
  an area (Spike Growth), for healing or damage that's over when cast, or for
  a spell that's instantaneous. Nothing is put on a target unless the effect
  says so. Use `until` only when it lasts until the start or end of a turn
  (`until=(TurnEdge.END, TurnOf.TARGET)` = the end of the target's next turn;
  `TurnOf.SOURCE` = the caster's); otherwise it lasts the spell's duration.
  List every condition it gives (Tasha's: Incapacitated and Prone): the
  dialog applies them all, for the same time, and one repeat save ends them
  all. A spell whose option only lasts the target's next turn (Command: Halt)
  marks it with its own name until `(TurnEdge.END, TurnOf.TARGET)`.
- **`[]`.** Use it only when the spell has nothing the form could put on a
  creature in a fight (Alarm, Message, Minor Illusion, Thaumaturgy, Disguise
  Self, Speak with Animals, Fog Cloud). The spell is hidden from "All spells"
  but stays in its caster's own list, so casting it still spends the slot.
- **`notes`.** A tuple of short, complete sentences, taken from the text,
  about what the form can't hold: riders, who is affected, extra targets per
  slot level, how the spell ends early. Don't restate what the form already
  shows (the damage, the ability, the condition). When you write the same
  kind of note for a third spell, report it: it is a field the model is
  missing (`Notes/combat-effects-plan.md`, principle 7).
- **`spends_use=False`** only on a later step of one casting (Ice Knife's
  explosion): that row spends no slot, no action and counts no cast.
- **Not for spells:** `dc`, `attack_bonus` (the caster's), `action_type` and
  `concentration` (the spell's casting time and duration say them), and
  `spell` (for a feature's use that casts one).
