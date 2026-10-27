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
  {"facts": [["Flavor", "A bright streak flashes from you to a point you choose within range and then blossoms with a low roar into a fiery explosion."],
             ["Area", "20-foot-radius Sphere centered on that point"],
             ["Save", "Dexterity, made by each creature in the area"]]},
  {"table": {"columns": ["Failed save", "Successful save"],
             "rows": [["8d6 Fire damage", "Half as much damage"]]}},
  {"option": {"name": "Using a Higher-Level Spell Slot", "blocks": [
    {"facts": [["Damage", "+1d6 for each spell slot level above 3"]]}]}}
]
```

Options don't nest, and there is no stat-block form (a summon's stat block
is an Option of Facts rows). A spell without flavor opens with a
`{"paragraph": ...}` lead instead, or straight with its rows.

The `spell-improved-descriptions` agent (`.claude/agents/`) writes
these in bulk and carries the full workflow and checks.

## Guidelines

Not a summary: keep every rule of the source text.

- **Flavor.** When the source describes how the magic looks, sounds or
  feels, or where it comes from ("A frigid beam of blue-white light
  streaks toward…", "Invoking Hadar…"), quote it word for word in a
  `Flavor` row, the card's first row. Quote whole sentences, or a clause
  when the rest of the sentence is rules; only capitalize the first letter
  and end with a period. Never write flavor yourself, and never rephrase
  it. A rule that appears in the flavor sentence (Magic Missile's "three"
  darts) also gets its own row, since readers skim past flavor.
- With a Flavor row the card needs no lead sentence. Without one, lead with
  a plain sentence saying what the spell does, with no imagery the source
  doesn't have ("Divine power fills your weapon attacks" is invented), or
  leave the lead out when the rows say it all.
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
  abilities) gets its own Option. Many small one-line choices
  (Prestidigitation, Command, Elementalism) go in one Table instead, a row
  each, with a "Lasts" column when their durations differ.
- A paragraph opening with a short phrase and "." or ":" gets that phrase
  bolded as a lead-in; write the lead as a plain sentence.

## Wording is rules

D&D rules hinge on single words. Restructure the text, but carry its
qualifiers over exactly:

- **Optional stays optional.** "You can take a Magic action to move it"
  must keep its "can"; a bare "Move: Magic action: move it" reads as
  mandatory. The same goes for "can repeat the save", "you can issue a
  general command", "it can deal 2d8 damage".
- **Keep the limiting words**: only, until, unless, instead, immediately,
  automatically, willingly, up to, at least, no larger than, of your choice,
  that you can see, other than, the first time, once per turn.
- **Keep defined terms as defined.** "Can't be possessed or Charmed" is not
  "Immune to" (Immunity is its own rule); "the target" is not "the last
  one"; damage "from the attack" is not damage "to the attack".
- **Don't reword rules text for presentation**, not even to keep a word
  like "fire" or "force" from being colored as a damage type. Only your own
  lead sentence is yours to phrase.
- **Don't import another edition's text** (a 2014 flavor line on a 2024
  spell), and don't add rules the source lacks. A table or stat block the
  source refers to but doesn't include can be added, but say so to the user.
- **Save-or-nothing is explicit**: give "Successful save: No damage" (or
  "No effect") its own row, so it can't be mistaken for half damage.
- Upcasting goes last, in an Option named exactly as the source's paragraph:
  `Using a Higher-Level Spell Slot` (2024) or `At Higher Levels` (2014). A
  scroll casts at its own level and drops that Option by name.
- Cantrip scaling goes in a `Cantrip Upgrade` Option, as a Table of
  character levels.
- Name conditions and damage types as the rules do (Paralyzed, Fire): damage
  types are colored on the card.
