---
name: character-engine-dev
description: Use for any D&D character build task — creating new builds, adding subclasses, implementing features/feats/spells, or understanding how the character sheet pipeline works.
tools: Read, Grep, Glob, Edit, Write, Bash
model: opus
memory: project
skills:
  - subagent-protocol
  - multiclass-builds
  - snapshot-diffs
---

You are an expert on this D&D 5e character sheet builder codebase. Implement tasks correctly and efficiently.

## Token discipline — follow these strictly

- **Never spawn subagents.** You have no Agent tool; do all work with Read/Grep/Glob/Edit/Write/Bash directly.
- **Grep/Glob before Read.** Find the class/function first, then read only those lines (`offset` + `limit`). Never read a whole file to find one pattern.
- **One verification pass.** After all edits in a task are done, run `python RunCharacterCreator.py` once. Not between each edit.
- **No exploratory reads.** If you already know the pattern from context, implement without re-reading reference files.

## Bulk mechanical edits — write a script, don't Edit-loop

If a change is the same substitution applied in more than ~5 files (renaming a symbol, moving a module and fixing every import), don't call Edit file by file:

1. `Grep` the exact pattern first to confirm scope (use `\b` word boundaries; watch for longer names that contain it, e.g. `starter_class` vs `starter_class_builder`).
2. Write a small script to the scratchpad directory (never into the repo) that applies precise `re.sub` substitutions, and run it once.
3. Re-grep for the old pattern (expect zero hits) and `python -m py_compile` the changed files.

```python
import re, pathlib
SKIP = (".git", ".claude")   # .claude/worktrees holds other agents' checkouts - never edit them
for f in pathlib.Path(".").rglob("*.py"):
    if any(part in SKIP for part in f.parts):
        continue
    text = f.read_text(encoding="utf-8")
    new = re.sub(r"\bold_name\b", "new_name", text)
    if new != text:
        f.write_text(new, encoding="utf-8")
```

For file moves, `git mv` each file first (keeps history), then fix imports with a script like the one above.

## Pipeline

**Build → Character → HTML**

- `Character` (`Model/Character.py`) — the one character object, immutable and built from `CharacterSources` (`Model/CharacterSources.py`, what builders fill in; `Character(sources)`), with two kinds of public member: **sources** (read-only: `base_abilities`, `base_speed`, `size`, `feature_grants`, `spell_grants`, `armors`, `weapons`, `items`, ...; `character.sources` returns a copy to change and rebuild from) and **queries** (`get_skill_modifier()`, `calculate_armor_class()`, `spells`, `features`, and listings such as `senses()`, `damage_resistances()`, `armor_training()`: one-liners that hand the character to a part of its private ledger, `Character._ledger`, which holds what every effect's `apply()` recorded and is never read from outside). `validate()` checks it (and returns it, so `builder.build().validate()` chains). `HtmlCharacterSheetWriter().write_character_sheet(character)` (`Presentation/CharacterSheetWriters.py`) writes the sheet.
- The sheet is a folder, not one file: `Output/<class>_<subclass>_<name>/` (`Presentation/CharacterSheetWriters.get_output_folder`; `example_` prefix for example builds) with `character.html`, `full_character_sheet.html`, `features/level_NN.html` per level that grants a feature or spell, and `fighting_styles.html` / `items.html` only when the build has them. All pages share one nav bar built from the same page list, so which pages exist depends on the build.
- Level and species builders get a `Grants` scope (`Model/Grants.py`) as `data`: `add_feature`, `add_spell`, `add_cantrip`, `add_fighting_style`, `add_weapon_mastery`, `add_invocation` (and a species' `base_speed`/`size`). It stamps every grant with its level and source, so nothing depends on call order. There is nothing to read from `data` while granting - and nothing to look up: an upgrade is `data.add_feature(Child(), extends=Parent)`.

## Key APIs

```python
# Ability scores
# apply(self, ledger_writer: LedgerWriter) gets a WRITE-ONLY record: it can add, never read -
# not a score, not a proficiency, not even a level. Anything that depends on another
# stat is a formula (lambda character: ...), evaluated when the value is read.
# Prefer the improvements in Model/Content/Improvements.py:
AbilityScoreBonus([(ability, bonus)], total=bonus).apply(ledger_writer)

# Skills / saving throws
SkillProficiency([skill]).apply(ledger_writer)
SkillExpertise([skill]).apply(ledger_writer)   # proficiency may come before or after; validated at the end
SavingThrowProficiency([ability]).apply(ledger_writer)
InitiativeProficiency().apply(ledger_writer)
HitPointsBonus(lambda character: character.get_class_level(CharacterClass.SORCERER)).apply(ledger_writer)

# Weapon / armor / tool proficiencies (never data.add_*_proficiency in a builder)
GrantWeaponProficiency([WeaponProficiency.MARTIAL]).apply(ledger_writer)
GrantArmorTraining([ArmorType.HEAVY]).apply(ledger_writer)
GrantToolProficiency([SmithsTools()]).apply(ledger_writer)

# Limited-use tracking (boxes reset on Long Rest)
StringUtils.add_boxes(description, uses)   # uses = int or proficiency_bonus

# Proficiency bonus
character.get_proficiency_bonus()

# Spells - in a level or species builder, `data` is a Grants scope (Model/Grants.py)
# that stamps each spell with its grant level and who grants it ("Wizard").
data.add_spell(spell)        # optional source="Chosen spell" label for the sheet
# The same spell from two grants (class + species) is listed for each; twice from
# one grant fails validate(). replace_spells={old: new} is declared, resolved on read.

# A spell that comes WITH a feature (a feat's or boon's spells, a subclass feature's
# ritual, a chosen cantrip a feature hands out) is declared by the feature itself -
# never added next to it in the builder, and no feat/boon-specific grant_to override:
def granted_spells(self) -> list[FeatureSpell]:   # from Model.Spells import FeatureSpell
    return [FeatureSpell(DruidLevel2Spells.BEAST_SENSE, Ability.WISDOM, "Ritual only"),
            FeatureSpell(self.cantrip, source=SpellSource.CHOSEN)]
# The character grants them whenever the feature is granted (plainly or as a kept
# extension), stamped like the feature. ability=None means the spellcasting ability
# the character had when the feature was granted. data.add_spell stays for spells no
# feature owns: class spell picks and subclass spell tables (domain/oath/patron spells).
```

## Feature types

- `Feature` (`Model/Content/Feature.py`) — override `apply(ledger_writer: LedgerWriter)` for mechanical effects (usually by composing `CharacterImprovement`s from `Model/Content/Improvements.py`), effects conditioned on worn armor or other stats as read-time formulas (`SpeedBonus(lambda cs: ...)`, `ArmorClassBonus(lambda cs: ...)`, see `Notes/feature-application-model.md`), and `get_description(self, character: CharacterView)` for the card text. Content reads the character only through `CharacterView` (`from Model.View import CharacterView`), never `Model.Character` (`tests/test_layering.py` enforces it); to ask whether a feature is granted, use `character.has_feature(SomeFeature)`. A display-only trait just overrides `get_description`.
- Nothing depends on the order features are granted in (`data.add_feature(...)`), including extensions (`data.add_feature(Child(), extends=Parent)` - declared, resolved on read, so parent and child may be granted in either order). Every grant is stamped by the builder's `Grants` scope with its level, kind and source, and the sheet buckets and sorts by that stamp, not by the `origin` text or call order. Effects must be order-insensitive too:
  - a bonus "equal to your <ability> modifier" is a formula, e.g. `SkillBonus(skill, lambda cs: max(1, cs.get_wisdom_modifier()))` — never compute it inside `apply()` (a test fails if you do);
  - expertise may be granted before its proficiency; the pairing is validated after all features apply.

## Directory layout

| Directory | Purpose |
|---|---|
| `CharacterContent/Classes/BaseClasses/` | Per-class base level features and Builder ABCs |
| `CharacterContent/Classes/SubClasses/` | Per-subclass level features and `NonGenericStarterClassArgs` |
| `Builds/Characters/` | One file per build; `CharacterBuilder` subclass registered in `RunCharacterCreator.py` |
| `Builds/Tests/`, `Builds/Examples/` | Test builds (spell slots, multiclass) and `_TEMPLATE.py` + example |
| `CharacterContent/Species/` | One file per species; a `SpeciesBuilder` subclass whose `_grant(data)` writes speed, size, features and spells into the character's sources. `data` is a `SpeciesGrants` scope, which also carries `character_level` and `spell_casting_ability` (the build's best mental ability, for species spells the build doesn't choose an ability for) - a species never takes the level as a constructor argument |
| `CharacterContent/Features/CharacterFeats/` | `GeneralFeats.py`, `OriginFeats.py`, `Backgrounds.py` |
| `CharacterContent/Features/CombatFeatures/` | `Maneuvers.py`, `FightingStyles.py` |
| `CharacterContent/Items/` | `Items/` (item classes, by category), `Armor/`, `Weapons/` (each a package split by category, re-exported through `__init__.py`) |
| `Model/` | `CharacterSources` (what builders fill in), `Character` (immutable: sources and queries, answered from its private ledger), `Grants` (the builder's scope), `Ledger/` (`Ledger.py`: one part per concern - `AbilityIncreases`, `EquipmentTraining`, `Languages`, `Defenses`, `Senses`, `AbilityRequirements`, `Initiative`, `WornArmor`, `ArmorClass`, `HitPoints`, `Speed`, `CarryingCapacity`, `Spellcasting`, `Skills`, `SavingThrows`, `WeaponBonuses`, plus `Bonuses`, the shared flat+formula bonus shape; and `LedgerWriter.py`, the write-only record `apply()` gets), `View.py` (`CharacterView`, `Formula`, `Value` - the one Protocol), `Content/` (the base classes content subclasses: `Effect`, `Feature`, `Improvements`, `FightingStyle`, `Item`, `AbstractWeapon`, `AbstractArmor`, `ExtraDamage`), `Records/` (`GrantStamp`, `SourcedValue`, `ToolProficiency`), `FeatureGrants.py` (`FeatureGrant`, `ExtensionTree`, `IfParentMissing`), `Creatures/` (stat blocks), `Spells.py` (`SpellGrant`, `SpellReplacement`), `AbilityScores` (immutable base scores), `Inventory` (gear and gold) |
| `CharacterContent/Spells/` | `SpellFactory` and spell definitions |
| `CharacterContent/Invocations/` | `InvocationFactory` and warlock invocations |
| `Utils/` | `StringUtils.py`, `CharaterSheetWriters.py`, `TableUtils.py` |

## Style rules

- `attrs` dataclasses, standard Python only — no external dependencies beyond `attrs`.
- Before implementing a new mechanic, read **one** existing analogous file — no more.
- All feats with ability score increases take an explicit `ability: Ability` parameter with validation.
- Shared rules numbers come from `Core/Rules.py` (`MAX_LEVEL`, `ALL_LEVELS`, `MAX_ABILITY_SCORE`, `MAX_PROFICIENCY_BONUS`, `MAX_ABILITY_MODIFIER`, `ability_modifier()`, ...) - never write `20`, `range(1, 21)` or `(score - 10) // 2`. A number that is one feature's own rule ("+2 to Strength", "maximum of 25") stays in the feature.
- A feature that grants a proficiency (skill, save, weapon, armor, tool) does it in its own `apply()`, so text and mechanics stay together; builders only `add_feature()` it.

## Running

```bash
python RunCharacterCreator.py                          # all builds
python -c "
import Core.Definitions as Definitions
from Builds.Characters.Y2024_Fighter_Champion_OsricIronheart import Y2024FighterChampionOsricIronheartCharacterBuilder
from Presentation.CharacterSheetWriters import HtmlCharacterSheetWriter
HtmlCharacterSheetWriter().write_character_sheet(Y2024FighterChampionOsricIronheartCharacterBuilder().build(), skill_config=Definitions.SkillConfig.DEFAULT)
"
```

`Definitions.SkillConfig.DEFAULT` — standard 5e. `Definitions.SkillConfig.HOMEBREW` — condensed skills.
