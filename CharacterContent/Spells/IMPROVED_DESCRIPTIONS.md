# Improved spell descriptions

A spell's rules laid out for reading at a glance, shown on its card in place
of the source text. The spell-side counterpart of
`Feature.get_improved_description()`; it uses the same blocks
(`Model/Content/FeatureText.py`) and the same renderer, so spell and feature
cards read alike.

## Where they live

`spells_<source>_improved.json`, beside each source file
(`spells_dnd2024.json` → `spells_dnd2024_improved.json`), keyed by spell
name. An entry rides on that source's record only: the factory merges
sources whole-record, so a description written for the 2024 wording never
lands on the 2014 one. A spell with no entry keeps its source text.

`RunCharacterCreator.py --source-text` prints the source text instead, for
checking an improved description against it.

## Format

A list of blocks, each an object with one key naming its type:

```json
"Fireball": [
  {"paragraph": "A bright streak ... blossoms into a fiery explosion."},
  {"facts": [["Area", "20-foot-radius Sphere centered on that point"],
             ["Save", "Dexterity, made by each creature in the area"]]},
  {"table": {"columns": ["Failed save", "Successful save"],
             "rows": [["8d6 Fire damage", "Half as much damage"]]}},
  {"option": {"name": "Using a Higher-Level Spell Slot", "blocks": [
    {"facts": [["Damage", "+1d6 for each spell slot level above 3"]]}]}}
]
```

Options don't nest, and there is no stat-block form.

## Guidelines

Not a summary: keep every rule of the source text (that's what
`spells_<source>_concise.json` is for).

- Lead with one sentence saying what the spell does.
- Don't repeat what the card already shows: level, school, casting time,
  range, duration, components, Concentration and Ritual. Do spell out what
  the card's line can't say — a reaction's trigger, an area's shape.
- Facts for the numbers looked up mid-combat: Target(s), Area, Attack,
  Save, On a hit, Healing, Effect, Repeat save. Write the save as its
  ability ("Wisdom"); the DC and attack bonus are in the sheet's
  Spellcasting headline.
- A Table for parallel outcomes (failed/successful save; a choice of
  effects).
- Each choice the spell offers (Alter Self's forms, Enhance Ability's
  abilities) gets its own Option.
- Upcasting goes last, in an Option named exactly as the source's paragraph:
  `Using a Higher-Level Spell Slot` (2024) or `At Higher Levels` (2014). A
  scroll casts at its own level and drops that Option by name.
- Cantrip scaling goes in a `Cantrip Upgrade` Option, as a Table of
  character levels.
- Name conditions and damage types as the rules do (Paralyzed, Fire): damage
  types are colored on the card.
