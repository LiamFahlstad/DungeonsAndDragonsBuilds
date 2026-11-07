---
name: spell-mechanics
description: Checked spell mechanics - what casting a spell rolls and does (saving throw or attack roll, which ability, damage dice and types, half on a save, a condition and how long it lasts, upcasting, cantrip scaling, healing, whether it has anything to apply at all), stored in CharacterContent/Spells/spells_<source>_mechanics.json and used by the combat UI's Custom Effect picker instead of reading the spell's text. Holds the schema, the rubric for each field, and a script that checks the files, lists spells without an entry (by level, class or campaign), drafts entries from the text for review, merges reviewed entries into the right file and compares them with the text reading. Use when adding, reviewing or fixing spell mechanics entries, when a spell fills the Custom Effect form wrongly, when a campaign's spells should be checked, or when someone asks why a spell's picker row says "Read from its rules text".
---

# Spell mechanics

The combat UI's Custom Effect dialog fills its form from a spell
(`spell_option()` in `Combat/CombatUIQt/effect_options.py`). A spell with an
entry in its source's mechanics file is filled from that entry; any other spell
is read from its rules text with regexes, which the GM then has to check. These
entries replace that guess with checked data, so every one must be right.

## Where entries live

`CharacterContent/Spells/spells_<source>_mechanics.json`, keyed by spell name,
beside the source the SpellFactory loads. Sources merge whole-record, dnd2024
first, then aidedd, then dnd5e: an entry must go in the file of the source that
**wins** for that spell, or it is never read. `add` picks the file for you.
Never edit the source spell JSON itself.

The schema is the docstring of
`CharacterContent/Spells/SpellFactory/Mechanics.py`, which also validates it.
Leave out every number that belongs to the caster (DC, attack bonus,
spellcasting modifier): the picker works those out.

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
4. `check`, and `./run_tests.sh -q tests/test_spell_mechanics.py tests/test_combat_ui_effect_options.py`.

## Rubric

- **`roll`.** Use `"attack"` when the caster makes a spell attack, or a weapon
  attack the spell grants (True Strike). Use `"save"` when the *target* rolls a
  save that decides the effect. Use `"none"` when it just happens: healing,
  buffs, auto-hit damage (Magic Missile), or a condition with no save
  (Invisibility). If a spell has both an attack and a save, put the first
  thing that happens in the entry and the second in `notes` (Ice Knife).
- **`save`.** `half_on_success` only when the text says half as much damage on a
  success. `repeat` only for "at the end of each of its turns, the target
  repeats the save, ending the effect on a success" (Hold Person, Tasha's).
  Other later saves, such as Sleep's second save, an Athletics check to escape,
  or a save when it enters the area, go in `notes`.
- **`damage`.** This is only the damage the hit or failed save deals *now*.
  Damage on later turns, on moving through an area, or on a later hit goes in
  `notes` (Witch Bolt's 1d12, Spike Growth, Hunter's Mark, Ensnaring Strike).
  Use one entry per damage type. `upcast` goes only on the part the
  higher-level paragraph names. `cantrip` only when the dice themselves grow
  (Eldritch Blast's extra beams are a note). Use `add_modifier` when the text
  adds "your spellcasting ability modifier". When the caster picks the type,
  use `"type": null` with `choices`.
- **`heal`.** Use it for Hit Points each target regains now (Cure Wounds,
  Healing Word); the picker fills the form's amount box with it, set to
  Healing. Hit Points regained later, or "equal to half the damage dealt"
  (Vampiric Touch), go in `notes`.
- **`temp_hp`.** The same for Temporary Hit Points (False Life, Armor of
  Agathys), with the Temp HP box. Its `upcast` may be a flat number ("5" for
  "5 additional Temporary Hit Points for each spell slot level"). An entry
  has at most one of `heal` and `temp_hp`, and a spell that deals damage
  fills the box with the damage, so its Hit Points become a note anyway. When
  the caster gets them ("You gain ..."), say so in `notes`: the dialog gives
  them to its targets.
- **`condition`.** Use it only for a rules condition (`Core.Definitions.Condition`)
  that the effect gives. Use `until` only when it lasts until the start or end of
  a turn (`["end", "target"]` = the end of the target's next turn; `"source"` =
  the caster's). The dialog applies one condition. If a spell gives two, put the
  one that matters most here and the other in `notes` (Tasha's: Incapacitated
  here, Prone in the notes).
- **`badge`.** By default, a spell with no damage or healing and a duration
  puts its own name on the targets as a badge (Bless, Faerie Fire, Shield).
  Set `true` when a spell that mentions damage should still mark its target
  (Hunter's Mark). Set `false` when the badge would mean nothing (an area such
  as Spike Growth, or every `applicable: false` spell).
- **`applicable: false`.** Use it only when the spell has nothing the form could
  put on a creature in a fight (Alarm, Message, Minor Illusion, Thaumaturgy,
  Disguise Self, Speak with Animals, Fog Cloud). The spell is hidden from "All
  spells" but stays in its caster's own list, so casting it still spends the slot.
- **`notes`.** Write short, complete sentences, taken from the text, about what
  the form can't hold: riders, who is affected, extra targets per slot level,
  how the spell ends early. Don't restate what the form already shows (the
  damage, the ability, the condition).
