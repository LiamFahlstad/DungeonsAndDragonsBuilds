---
name: multiclass-builds
description: How to multiclass a character build in this repo (2024 rules) - the StarterClassBuilder + <Class>MulticlassBuilder pattern, level order, resuming a class after a dip, what a multiclass level does and doesn't grant (proficiencies, saves, spell slots, HP, subclass), the gaps the engine doesn't model, which tests and snapshots change, and a script that reports what a multiclass build came out as. Use whenever a character takes a level in a second class ("dip", "multiclass", "take a level in Fighter", "Paladin 2 / Warlock 1"), when converting a level-up into another class, when reviewing a multiclass build, or when someone asks why a multiclass sheet shows the wrong slots, saves, proficiencies or subclass.
---

# Multiclass builds

A build has exactly one **starting class** (`StarterClassBuilder`, its 1st level is character level 1) and any number of **multiclass builders** (`<Class>MulticlassBuilder` or `<Class><Subclass>MulticlassBuilder`), passed to `CharacterBuilder(multiclass_builders=[...])`. All of them grant into one shared set of sources.

Reference builds, read the one closest to your case:

| Case | Build |
|---|---|
| Caster with a Fighter 1 dip at the latest level | `Builds/Characters/Y2024_Artificer_Cartographer_ObmarStalskagg.py` (Artificer 3 / Fighter 1) |
| Fighter 1 *starting* class, rest in a subclassed caster | `Builds/Characters/Y2024_Fighter_BardValor_Clover.py`, `Builds/Tests/MulticlassTest.py` |
| Dip in the middle, then resume the first class | `Builds/Characters/Y2024_Paladin_Devotion_ElricPactsworn.py` (Paladin 1, Warlock 2, Paladin 3-20) |
| Two spell slot pools | `Builds/Tests/SpellSlotTestWizard3Warlock3.py`, `Builds/Tests/SpellSlotTestPaladin4Wizard3.py` |

## Check the build (run it; don't guess)

```bash
python .claude/skills/multiclass-builds/multiclass_report.py Builds/Characters/<File>.py [more files...]
```

It builds the character, runs `validate()` (which enforces the 13+ prerequisites), and prints the class of each character level, the features each class level granted, saves, armor and weapon proficiencies (per carried weapon), HP/AC, masteries, fighting styles and spell slots, and notes the grants the engine doesn't model. Compare each line against the rules below.

## Level order

Character levels are recorded in builder order: starting class first, then each multiclass builder in list order. So the order of `multiclass_builders` *is* the order the player took the levels.

- **Dip at the latest level** (the usual level-up case): lower the starting class's `base_class_level` by one, delete that level's entry from `base_class_features_by_level` (and its subclass entry, if any), and add a multiclass builder at level 1 for the new class. The choices made in the deleted level (ASI/feat, spells) are gone. Say so in your report.
- **Dip, then resume the first class**: add a *second* builder for the first class after the dip (Elric). A builder resuming a class declares the class's **final total level**, not the number of new levels, and lists only the levels it adds. A class level already granted by an earlier builder is skipped, never applied twice.
- A feat taken at a later class level takes `character_level=` = the **character** level it's taken at, not the class level (e.g. `GeneralFeats.DualWielder(character_level=4, ...)` on Wizard 4 at character level 4).

## What a multiclass level grants (2024 PHB)

Engine-handled, so don't add them by hand:

- **Prerequisites**: 13+ in the primary ability of the starting class *and* every new class (Fighter: STR or DEX; Monk: DEX and WIS; Paladin: STR and CHA; see `CharacterClass.multiclass_prerequisites`). `validate()` raises if not met. Check the scores *before* writing the build; if they fail, stop and tell the user rather than bumping scores.
- **Proficiencies**: only the reduced multiclass set (`_MULTICLASS_PROFICIENCIES` in `CharacterContent/Features/ClassFeatures/ClassProficiencies.py`): Fighter/Paladin/Ranger give Light+Medium+Shield and Martial weapons, Barbarian Shield+Martial, and so on. **No saving throws** from a non-starting class. **No Heavy armor** from a multiclass Fighter or Paladin: only a starting Fighter/Paladin gets it (that's why Clover starts as Fighter).
- **HP**: a multiclass level uses that class's fixed average (d10 → 6, d8 → 5, ...) + CON. Only character level 1 gets the max hit die.
- **Spell slots**: worked out across classes by `Core/SpellcastingRules.py`: full casters count full, Paladin/Ranger/Artificer half rounded up, third-casters a third, against the multiclass table. A lone caster plus a non-caster keeps its own table. Warlock Pact Magic is a separate pool. Each class prepares spells from its own list at its own class level.
- **Subclass**: shown once a class reaches its first subclass-features level. A Fighter 1 dip has none; pass `subclass=""` to the plain `FighterMulticlassBuilder` (Obmar). If no class has reached a subclass yet, the first subclass named is shown.
- **Class features**: each class level's `add_features` runs as written. Level 1 features that only a starting class gets (e.g. starting equipment) are already left to `StarterClassBuilder`.

Not modelled (the report prints a note):

- The **one skill proficiency** from multiclassing into Artificer, Bard, Ranger or Rogue (Bard also gives one musical instrument). If the player took one, ask which, and flag that the engine doesn't model it. Don't change shared engine code from a build task.
- **Rules overlap the engine doesn't police**: Extra Attack doesn't stack across classes, and a second Unarmored Defense or a second Fighting Style feature of the same style gains nothing. Read the sheet for duplicates.

## Choices the player makes

A new class's level 1 has picks (Fighter: 3 weapon masteries + a fighting style; Warlock: cantrips, spells, an invocation; ...). Use the player's picks when given. Otherwise choose sensibly from the weapons and style the character actually uses, mark them `# Placeholder picks - confirm with the player.` in the build, and list them in your report so the user can confirm.

## Tests and snapshots that change

Multiclassing an existing build legitimately changes its golden snapshots. Run `./run_tests.sh -q`, **read every diff** (`python .claude/skills/snapshot-diffs/snapshot_diff.py <BuildName>` shows the changed stats and page text) and check each changed line is a consequence of the multiclass (class levels, lost ASI, HP from the new hit die, new proficiencies on weapons, slots, features). Then `UPDATE_SNAPSHOTS=1 ./run_tests.sh -q -k <BuildName>` and rerun the full suite. The order-invariance tests may fail *during* the update run because the golden is being rewritten under them; they must pass on the plain rerun.

The Character Creator GUI can't load multiclass builds. If the build is newly multiclassed, `tests/test_creator_roundtrip.py`'s `NOT_REPRODUCED` entry for it must name `_MULTICLASS` (it's a strict xfail, so a missing entry fails).
