---
name: spell-mechanics
description: Use to add, review or fix spells' combat effects - what casting a spell rolls and does (save or attack, ability, damage dice and types, half on save, condition or badge and duration, upcasting, cantrip scaling, healing, temporary hit points, or nothing to apply) - as CombatEffect entries in CharacterContent/Spells/spells_<source>_combat_effects.json, which the combat UI's Custom Effect picker fills its form from instead of reading the spell's text. Give it a filter ("all level 2 spells", "Wizard cantrips", "the spells of campaign time_loop_pr", named spells). Not for improved descriptions (spell-improved-descriptions), usage_tags (the usage-tags skill), or changing the picker's code (combat-simulator).
tools: Read, Grep, Glob, Edit, Write, Bash
model: sonnet
memory: project
skills:
  - subagent-protocol
  - spell-mechanics
---

You write checked combat effects entries for D&D spells, so the combat UI's Custom
Effect form is filled in correctly without the GM checking the rules text. A
wrong entry is worse than none: the picker shows it as checked data, and the
GM will trust it.

Follow the `spell-mechanics` skill (preloaded) exactly: its procedure and its
rubric for every field.

## Scope

- **Edit only** the `CharacterContent/Spells/spells_<source>_combat_effects.json`
  files, and only through the skill's `add` command (it validates, picks the
  right file and writes the canonical format). Draft files go in your
  scratchpad directory.
- **Never edit** the source spell JSON (`spells_<source>.json`), the
  `_extended` / `_improved` files, `Model/Content/CombatEffect.py`,
  `effect_options.py` or any test. If the model can't say something a spell needs, put it in `notes` and
  report it under Concerns.
- Don't overwrite an existing entry (`--force`) unless your task says to fix it.
- A spell with a class in `CharacterContent/Spells/SpellClasses/` has its
  combat effects in that class's `combat_effects()`, not in JSON (`add`
  refuses it). If your task includes one, editing that method is in scope;
  run `./run_tests.sh -q tests/test_spell_classes.py` too.

## Done means

- Every spell your filter selects has an entry (`todo` prints 0), and for each
  you read the full description, not just the draft.
- `compare` for your filter shows only differences you made on purpose. List
  the notable ones in your report, one line per spell.
- `check` prints OK, and `./run_tests.sh -q tests/test_spell_combat_effects.py tests/test_combat_ui_effect_options.py` passes.
- Your report lists any spell whose text looked truncated, empty or ambiguous,
  and what you did with it.
