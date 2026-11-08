---
name: spell-mechanics
description: Spells' combat effects - what casting a spell rolls and does (saving throw or attack roll, which ability, damage dice and types, half on a save, a condition or badge and how long it lasts, upcasting, cantrip scaling, healing, Temporary Hit Points, or nothing to apply at all), stored as lists of CombatEffect dicts in CharacterContent/Spells/spells_<source>_combat_effects.json and used by the combat UI's Custom Effect picker instead of reading the spell's text. The same CombatEffect model features and monster abilities use. Holds the format, the rubric for each field, and a script that checks the files, lists spells without an entry (by level, class or campaign), drafts entries from the text for review, merges reviewed entries into the right file and compares them with the text reading. Use when adding, reviewing or fixing a spell's combat effects, when a spell fills the Custom Effect form wrongly, when a campaign's spells should be checked, or when someone asks why a spell's picker row says "Read from its rules text".
---

# Spells' combat effects

The combat UI's Custom Effect dialog fills its form from a spell
(`spell_option()` in `Combat/CombatUIQt/effect_options.py`). A spell with an
entry in its source's combat effects file is filled from that entry; any other
spell is read from its rules text with regexes, which the GM then has to check.
These entries replace that guess with checked data, so every one must be right.

Spells, features and monster abilities all describe themselves with the same
model, `CombatEffect` (`Model/Content/CombatEffect.py`; its docstring has every
field). A feature writes it in Python; a spell writes it in JSON, exactly as
`CombatEffect.to_dict()` writes it. The plan behind this is
`Notes/combat-effects-plan.md`.

## Where entries live

`CharacterContent/Spells/spells_<source>_combat_effects.json`, keyed by spell
name, beside the source the SpellFactory loads. Sources merge whole-record,
dnd2024 first, then aidedd, then dnd5e: an entry must go in the file of the
source that **wins** for that spell, or it is never read. `add` picks the file
for you. Never edit the source spell JSON itself.

An entry is a **list**:

- one effect per way to cast it: usually one; several for options with
  different mechanics (Command's five, each `"name": "Command: Grovel"`) or
  steps of one casting (Ice Knife's shard, then its explosion), or
- `[]` when the spell has nothing to apply to a creature in a fight.

A spell without an entry is "not described yet" and is read from its text.

**A spell written as a class** (`CharacterContent/Spells/SpellClasses/`,
see `SpellFactory/ClassSpell.py`) has its combat effects in the class's
`combat_effects()` method instead, as the same `CombatEffect` objects written
in Python, and no JSON entry (`check` reports one, `add` refuses it). To
describe such a spell, edit its class. To make a JSON spell a class, run
`python -m CharacterContent.Spells.SpellClassConverter --name <spell>`: it
writes the class from the record and every companion entry, checks the class
gives the same as the JSON did, and takes the spell out of the companion files.

```json
"Fireball": [
  {
    "roll": "save",
    "save_ability": "Dexterity",
    "half_on_success": true,
    "damage": [
      {"dice": "8d6", "damage_type": "Fire", "upcast": "1d6"}
    ]
  }
],
"Alarm": []
```

Leave out every number that belongs to the caster (`dc`, `attack_bonus`): the
picker works those out. Leave out every field at its default: `check` refuses a
default written out, and `format` / `add` write each effect as `to_dict()` does.

## Tools

```bash
S=.claude/skills/spell-mechanics/spell_mechanics.py
python $S todo --campaign time_loop_pr          # what's missing (also --level N, --class Wizard, --name X)
python $S draft --level 2 --out <scratchpad>/draft.json   # drafts + a review sheet with each spell's full text
python $S add <scratchpad>/draft.json           # validate and merge into the right file(s), canonical format
python $S compare --level 2                     # where the entries and the text reading disagree
python $S check                                 # run before you report: exit 1 on any problem
```

Write drafts in the scratchpad, never the repo. `add` refuses to overwrite an
existing entry that differs unless you pass `--force`. Use that only when you
are fixing that entry on purpose.

## Procedure

1. `todo` for your filter, then `draft --out`.
2. For **every** spell, read its full description on the review sheet and fix
   the draft field by field against the rubric below. The draft comes from the
   regex reading these entries exist to replace. "Improved description agrees"
   only means the two automatic readings agree, not that they are right.
3. `add`, then `compare` for your filter. Every difference it lists must be one
   you made on purpose (the reason is usually in the entry's notes).
4. `check`, and `./run_tests.sh -q tests/test_spell_combat_effects.py tests/test_combat_ui_effect_options.py`.

## Rubric

- **`roll`.** Use `"attack"` when the caster makes a spell attack, or a weapon
  attack the spell grants (True Strike). Use `"save"` when the *target* rolls a
  save that decides the effect. Leave it out (`"none"`) when it just happens:
  healing, buffs, auto-hit damage (Magic Missile), or a condition with no save
  (Invisibility). If a spell has both an attack and a save, give each its
  own effect (Ice Knife: "Ice Knife: shard", then "Ice Knife: explosion").
- **`save_ability`** (with `roll: "save"`): the full ability name,
  `"Dexterity"`. **`half_on_success`** only when the text says half as much
  damage on a success. **`repeat_save`** only for "at the end of each of its
  turns, the target repeats the save, ending the effect on a success" (Hold
  Person, Tasha's). Other later saves, such as Sleep's second save, an
  Athletics check to escape, or a save when it enters the area, go in `notes`.
- **`damage`.** This is only the damage the hit or failed save deals *now*.
  Damage on later turns, on moving through an area, or on a later hit goes in
  `notes` (Witch Bolt's 1d12, Spike Growth, Hunter's Mark, Ensnaring Strike).
  Use one part per damage type, each `{"dice", "damage_type"}`. `upcast` goes
  only on the part the higher-level paragraph names. `cantrip`
  (`{"5": "2d8", "11": "3d8", "17": "4d8"}`) only when the dice themselves grow
  (Eldritch Blast's extra beams are `instances`). Use `add_modifier: true` when
  the text adds "your spellcasting ability modifier". When the caster picks the
  type, use `"damage_type": null` with `choices`. Damage only some targets take
  is a part with `when`, what follows "if": Divine Smite's
  `{"dice": "1d8", "damage_type": "Radiant", "when": "the target is a Fiend or
  an Undead"}`. When the dice *replace* the others for some targets, make a
  second effect instead ("Toll the Dead (hurt target)" with d12s).
- **`instances`.** `{"count", "upcast", "cantrip", "noun"}` when one casting
  rolls and deals its damage several times, at one target or several:
  Scorching Ray `{"count": 3, "upcast": 1, "noun": "ray"}`, Magic Missile's
  darts, Eldritch Blast `{"count": 1, "cantrip": {"5": 2, "11": 3, "17": 4},
  "noun": "beam"}`. The damage is one instance's. The dialog fills its Times
  box with the count. Extra *targets* per slot level are not instances: they
  go in `notes`.
- **`healing`.** `{"dice", "upcast", "add_modifier"}` for Hit Points each
  target regains now (Cure Wounds, Healing Word); the picker fills the form's
  amount box with it, set to Healing. `upcast` can be a number (Heal's "+10").
  Hit Points regained later, or "equal to half the damage dealt" (Vampiric
  Touch), go in `notes`.
- **`temp_hp`.** The same for Temporary Hit Points (False Life, Armor of
  Agathys), with the Temp HP box. An effect has at most one of `damage`,
  `healing` and `temp_hp` (the form has one amount box): a spell that deals
  damage puts its Hit Points in `notes`. When the caster gets them ("You gain
  ..."), say so in `notes`: the dialog gives them to its targets.
- **`conditions`.** A list of `{"name", "until"}`, each a rules condition
  (`Core.Definitions.Condition`) the effect gives, **or the spell's own name as
  a badge** on its targets (Bless, Faerie Fire, Shield, Hunter's Mark). Use a
  badge when the spell lasts and marks its targets with something the form
  can't show (a bonus, a rider), and not for an area (Spike Growth), for
  healing or damage that's over when cast, or for a spell that's
  instantaneous. Nothing is put on a target unless the entry says so. Use
  `until` only when it lasts until the start or end of a turn
  (`["end", "target"]` = the end of the target's next turn; `"source"` = the
  caster's); otherwise it lasts the spell's duration. List every condition
  it gives (Tasha's: Incapacitated and Prone): the dialog applies them all,
  for the same time, and one repeat save ends them all. A spell whose option
  only lasts the target's next turn (Command: Halt) marks it with its own name
  until `["end", "target"]`.
- **`[]`.** Use it only when the spell has nothing the form could put on a
  creature in a fight (Alarm, Message, Minor Illusion, Thaumaturgy, Disguise
  Self, Speak with Animals, Fog Cloud). The spell is hidden from "All spells"
  but stays in its caster's own list, so casting it still spends the slot.
- **`notes`.** Write short, complete sentences, taken from the text, about what
  the form can't hold: riders, who is affected, extra targets per slot level,
  how the spell ends early. Don't restate what the form already shows (the
  damage, the ability, the condition). When you write the same kind of note
  for a third spell, report it: it is a field the model is missing
  (`Notes/combat-effects-plan.md`, principle 7).
- **`spends_use: false`** only on a later step of one casting (Ice Knife's
  explosion): that row spends no slot, no action and counts no cast.
- **Not for spells:** `dc`, `attack_bonus` (the caster's), `action_type` and
  `concentration` (the spell's casting time and duration say them), and
  `spell` (for a feature's use that casts one).
