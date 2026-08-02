# CharacterContent Naming Quality Review

## Scope and Rating Scale

Full sweep of every class and function/method name under `CharacterContent/` (~318 `.py` files, excluding `__pycache__`): `Classes/`, `Features/` (ClassFeatures, SubClassFeatures, SubClassFeatures2014, CharacterFeats, CombatFeatures, Core, FeatureGeneration, SpeciesFeatures), `Items/`, `Spells/`, `Invocations/`, `Species/`, `ToolProficiencies/`. This evaluates Python identifier quality, not in-game D&D lore names.

- **critical**: Breaks convention badly, actively misleading, a likely bug, or a PEP 8 violation that could cause a case-sensitive lookup failure.
- **major**: Inconsistent with sibling classes/files or violates an established codebase pattern.
- **minor**: Small style nits that don't significantly affect clarity.
- **fine**: No issues detected.

Findings below are grouped by area and ranked critical → major → minor. Areas with no non-fine findings are summarized rather than enumerated (the codebase is overwhelmingly consistent — see the Fine tally per section).

---

## Critical Issues (5)

| File | Name | Kind | Note |
|------|------|------|------|
| `Classes/BaseClasses/RangerBase.py` | `RangerMulticlassBuilder` | Class (inheritance) | Inherits from `ClassBuilder.ClassBuilder` instead of `ClassBuilder.MulticlassBuilder` — every other multiclass builder (Artificer, Barbarian, Bard, Cleric, Druid, Fighter, Monk, Paladin, Rogue, Sorcerer, Warlock, Wizard) inherits from `MulticlassBuilder`. This isn't just a naming nit — the class is now structurally different from its name and siblings, which likely produces wrong behavior when Ranger is multiclassed. |
| `Features/SubClassFeatures/Cleric/ClericLifeFeatures.py` | `DiscipleofLife` | Class | Should be `DiscipleOfLife` — lowercase "o" breaks PascalCase word-boundary convention. |
| `Features/SubClassFeatures/Fighter/FighterPsiWarriorFeatures.py` | `BulwarkofForce` | Class | Should be `BulwarkOfForce` — same lowercase "o" defect. |
| `Features/SubClassFeatures/Monk/MonkMercyFeatures.py` | `HandofHarm` | Class | Should be `HandOfHarm` — inconsistent with its own sibling `HandOfHealing` in the same file. |
| `Species/Tiefling.py` | `FiendishLineage.Chthonic` | Enum member | Mixed-case `Chthonic` instead of `CHTHONIC`; siblings `ABYSSAL` and `INFERNAL` are both SCREAMING_SNAKE_CASE. Risky if any code does case-sensitive name comparisons or lookups against this enum. |

---

## Major Issues

### Classes — reversed name order between sibling classes in the same file (11 files)
*(Carried forward from the existing `ClassNamingReview.md` class-name pass — included here for a complete picture.)*

`CustomStarterClassArgs` and `MulticlassBuilder` use opposite word order for the same subclass within one file, e.g. `WarlockArchfeyCustomStarterClassArgs` vs. `ArchfeyWarlockMulticlassBuilder`.

- Paladin: `PaladinAncients.py`, `PaladinDevotion.py`, `PaladinGenies.py`
- Ranger: `RangerHunter.py`
- Warlock: `WarlockArchfey.py`, `WarlockCelestial.py`, `WarlockFiend.py`, `WarlockHexblade.py`, `WarlockUndead.py`
- Wizard: `WizardEvocation.py`, `WizardNecromancy.py`

### SubClassFeatures2014 — Artificer subclass-prefix inconsistency (26 classes across 4 files)

Every Artificer subclass file mixes prefixed and unprefixed feature class names within the same file:

| File | Prefixed (has subclass name) | Unprefixed (missing it) |
|------|-------------------------------|--------------------------|
| `ArtificerAlchemistFeatures.py` | `AlchemistToolsOfTheTrade`, `AlchemistSpells` | `ExperimentalElixir`, `AlchemicalSavant`, `RestorativeReagents`, `ChemicalMastery` |
| `ArtificerArmorerFeatures.py` | `ArmorerToolsOfTheTrade`, `ArmorerSpells`, `ArmorerExtraAttack` | `ArcaneArmor`, `ArmorModel`, `ArmorModifications`, `PerfectedArmor` |
| `ArtificerArtilleristFeatures.py` | `ArtilleristToolsOfTheTrade`, `ArtilleristSpells` | `EldritchCannon`, `ArcaneFirearm`, `ExplosiveCannon`, `FortifiedPosition` |
| `ArtificerBattleSmithFeatures.py` | `BattleSmithToolsOfTheTrade`, `BattleSmithSpells`, `BattleSmithExtraAttack` | `BattleReady`, `SteelDefender`, `ArcaneJolt`, `ImprovedDefender` |

Every other base class (Barbarian, Bard, Cleric, Druid, Fighter, Monk, Paladin, Ranger, Rogue, Sorcerer, Warlock, Wizard) uses **no** subclass-name prefix on feature classes — Artificer should be normalized to match, in both the 2014 and 2024 tree (same pattern recurs in `Features/SubClassFeatures/Artificer/*` for 2024, e.g. `AlchemistToolsOfTheTrade` vs. `ExperimentalElixir`, and `ReanimatorsSkillSet` additionally uses an inconsistent plural possessive — should be `ReanimatorSkillSet`).

### SubClassFeatures2014 — Cleric domain singular/plural inconsistency (3 files)

- `ClericDeathFeatures.py` → `BonusProficiency` (singular)
- `ClericForgeFeatures.py` → `BonusProficiencies` (plural)
- `ClericLifeFeatures.py` → `BonusProficiency` (singular)

### SubClassFeatures2014 — Fighter one-off prefix

- `FighterEldritchKnightFeatures.py`: `EldritchKnightSpellcasting` is the only class in the file with a subclass-name prefix; siblings (`WeaponBond`, `WarMagic`, `EldritchStrike`, `ArcaneCharge`, `ImprovedWarMagic`) have none.

### SubClassFeatures2024 — Sorcerer origin-string naming (2 files)

`SorcererAberrantFeatures.py` and `SorcererClockworkFeatures.py` use "Aberrant Sorcery" / "Clockwork Sorcery" as the feature origin string, breaking the "`[Name] Sorcerer`" pattern used by every other Sorcerer subclass (Wild Magic Sorcerer, Draconic Sorcerer, Shadow Sorcerer, Spellfire Sorcerer, Clockwork Sorcerer[sic, inconsistent with itself]).

### SubClassFeatures2024 — Rogue compound-name inconsistency

`RogueSoulKnifeFeatures.py` uses "Soulknife" as one word for its feature origin strings ("Soulknife Rogue Level X"), while every other multi-word Rogue/Ranger subclass name is space-separated ("Arcane Trickster", "Beast Master", "Fey Wanderer", "Gloom Stalker", "Hollow Warden", "Winter Walker").

### ClassFeatures (base class features)

| File | Name | Note |
|------|------|------|
| `ClassFeatures/Ranger/RangerFeatures.py` | `SpellCasting` | Every sibling class (Bard, Cleric, Druid, Artificer, Sorcerer) uses `Spellcasting` (lowercase "c"). |
| `ClassFeatures/Barbarian/BarbarianFeatures.py` | `UnarmoredDefenseText`, `DangerSenseText` | Non-descriptive "Text" suffix obscures whether the class holds a description or a mechanical effect. |
| `ClassFeatures/Monk/MonkFeatures.py` | `UnarmoredDefenseText` | Same "Text" suffix issue, same feature name, independently. |
| `ClassFeatures/Bard/BardFeatures.py` | `Expertise1`, `Expertise2` | Generic numeric suffixes don't convey that these are the level-1 and level-9 versions. |

### Items

| File | Name | Note |
|------|------|------|
| `Items/Packs.py` | `Entertainers` | Every sibling pack class follows `<Name>Pack` (`DungeoneersPack`, `BurglarsPack`, `DiplomatsPack`, …); this one is missing the `Pack` suffix. |
| `Items/Gear.py` | `StringItem` | Every sibling item in the file is named directly (`Rope`, `Chain`, `Bell`, `Net`) without an "Item" suffix — likely added to dodge a builtin shadow, but breaks the pattern. |
| `Items/Wondrous.py` | `RingOfIntelligence` | Class name doesn't match the item's own internal display name, "Ring of Intellect". |

### Species / Invocations

| File | Name | Note |
|------|------|------|
| `Species/Warforged.py` | `WarForgedSpeciesBuilder` | Interior capital "F" (`WarForged`) is inconsistent with all 18+ sibling species builders (`DwarfSpeciesBuilder`, `ElfSpeciesBuilder`, `HalflingSpeciesBuilder`, …) and with the official D&D spelling "Warforged". |
| `Invocations/InvocationFactory.py` | `replace_last`, `inject_newline` | Defined nested inside the `description` property method rather than at module or static scope — not a name-collision issue but a naming/placement smell worth flagging. |

---

## Minor Issues (10)

| File | Name | Note |
|------|------|------|
| `Classes/BaseClasses/WizardBase.py` | `skill_to_expertise_in` (param) | Notably more verbose than sibling parameter names (`skill_1`, `skill_2`, `spell`). |
| `ClassFeatures/Barbarian/BarbarianFeatures.py` | `ImprovedBrutalStrike1`, `ImprovedBrutalStrike2` | Numeric suffix without indicating the level distinction. |
| `Features/FeatureGeneration/Output.py` | `TidesofChaos` | Should be `TidesOfChaos` (capital "O" at the word boundary). |
| `Features/SubClassFeatures/Rogue/RogueScionOfTheThreeFeatures.py` | `AuraofMalevolence` | Should be `AuraOfMalevolence`, matching `AuraOfWarding`, `AuraOfDevotion`, `AuraOfElementalShielding`. |
| `Features/SubClassFeatures/Sorcerer/SorcererAberrantFeatures.py` | `RevelationinFlesh` | Should be `RevelationInFlesh`. |
| `Features/SubClassFeatures/Wizard/WizardBladesingerFeatures.py` | `BladesongText` | Should just be `Bladesong`, matching the feature name passed to the superclass and the pattern used by `AbjurationSavant`, `Portent`, `IllusionSavant`, etc. |
| `Items/Weapons/Enums.py` | `WeaponsDamageTypes` | Sibling enums (`WeaponProperty`, `WeaponMastery`, `WeaponType`, `WeaponProficiency`) are singular; this and the next one are plural. |
| `Items/Weapons/Enums.py` | `WeaponsDamageRolls` | Same plural-vs-singular inconsistency as above. |
| `Invocations/Definitions.py` | `InvocationsLevel0`…`InvocationsLevel15` | Diverges from the parallel Spells pattern (`SorcererLevel0Spells`, `WizardLevel1Spells`, …); arguably justified since invocations aren't class-scoped, but still a pattern break worth noting. |

---

## Summary

| Severity | Count (approx., grouping systemic repeats) |
|----------|----------------------------------------------|
| Critical | 5 |
| Major | ~15 distinct issue types (spanning ~55 individual classes, mostly from the two systemic Artificer prefix inconsistencies) |
| Minor | 10 |
| Fine | ~1,700+ classes/functions reviewed with no issues |

**Files reviewed:** all ~318 `.py` files under `CharacterContent/` (Classes, Features, Items, Spells, Invocations, Species, ToolProficiencies), covering roughly 900+ classes and 1,000+ functions/methods.

### Top takeaways, worst to least severe

1. **`RangerMulticlassBuilder` inherits from the wrong base class** (`Classes/BaseClasses/RangerBase.py`) — this is a correctness bug wearing a naming-review disguise; a Ranger multiclass build is likely broken. Fix first.
2. **Three `...ofX` → `...OfX` capitalization slips** (`DiscipleofLife`, `BulwarkofForce`, `HandofHarm`) and **one enum-casing slip** (`Tiefling.Chthonic`) are mechanical, low-risk, high-confidence fixes — a simple rename each.
3. **Artificer's feature classes inconsistently prefix with the subclass name**, in *both* the 2014 and 2024 rule trees, and this is by far the largest source of major findings (~55 classes across 8 files). This is the single highest-leverage cleanup: pick one convention (prefixed or not) and apply it uniformly, matching every other class in the codebase (which uses no prefix).
4. Everything else (Cleric singular/plural, Sorcerer origin strings, "Soulknife" spacing, "Text"-suffixed classes, numeric-suffixed features, Item/Species one-offs) are isolated, low-blast-radius inconsistencies — worth cleaning up but not urgent.
5. The overwhelming majority of the codebase (SubClasses2024 in full, SubClasses2014, and most of Features/Items/Spells/Species) is **highly consistent**: `add_features()` as the universal level-feature method name, snake_case throughout for functions, and clear PascalCase for classes.
