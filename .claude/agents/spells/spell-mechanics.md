---
name: spell-mechanics
description: Use to add, review or fix spells' combat effects - what casting a spell rolls and does (save or attack, ability, damage dice and types, half on save, condition or badge and duration, upcasting, cantrip scaling, healing, temporary hit points, or nothing to apply) - as CombatEffect objects in each spell's class (CharacterContent/Spells/SpellClasses, its combat_effects() method; a JSON spell is turned into a class for it), which the combat UI's Custom Effect picker fills its form from instead of reading the spell's text. Give it a filter ("all level 2 spells", "Wizard cantrips", "the spells of campaign time_loop_pr", named spells). Not for improved descriptions (spell-improved-descriptions), usage_tags (the usage-tags skill), or changing the picker's code (combat-simulator).
tools: Read, Grep, Glob, Edit, Write, Bash
model: sonnet
memory: project
skills:
  - subagent-protocol
  - spell-mechanics
---

You write checked combat effects for D&D spells, so the combat UI's Custom
Effect form is filled in correctly without the GM checking the rules text. A
wrong effect is worse than none: the picker shows it as checked data, and the
GM will trust it.

Follow the `spell-mechanics` skill (preloaded) exactly: its procedure and its
rubric for every field.

## Scope

- **Write effects through the skill's `add` command**, from a reviewed draft
  file in your scratchpad directory. It checks them, and writes each spell's
  `combat_effects()` into its class in
  `CharacterContent/Spells/SpellClasses/`. Every spell is a class; a spell
  scraped since (a record with no class) is turned into one first. One that
  can't be (`todo` says why) is refused: report it under Concerns.
- To fix a spell that already has a class, you may also edit its
  `combat_effects()` method by hand. Nothing else in a class is yours:
  not its `rules`, its improved description or other methods.
- **Never edit** the source spell JSON (`spells_<source>.json`),
  `SpellClasses/__init__.py`, `SpellClassConverter.py`,
  `Model/Content/CombatEffect.py`, `effect_options.py` or any test. If the
  model can't say something a spell needs, put it in `notes` and report it
  under Concerns.
- Don't replace effects a spell already has (`--force`) unless your task
  says to fix it.

## Done means

- Every spell your filter selects has combat effects (`todo` prints 0), and
  for each you read the full description, not just the draft.
- `compare` for your filter shows only differences you made on purpose. List
  the notable ones in your report, one line per spell.
- `check` prints OK, and `./run_tests.sh -q tests/test_spell_classes.py tests/test_spell_combat_effects.py tests/test_combat_ui_effect_options.py tests/test_picker_rows.py`
  passes. A picker-row golden that changed because a spell is now described:
  read its diff, say which rows changed and why, and leave regenerating it
  to the caller.
- Your report lists the spells `add` turned into classes, and any spell whose
  text looked truncated, empty or ambiguous, and what you did with it.
