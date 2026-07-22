# Creating a New D&D 5e Character Build

This directory contains character build definitions for the D&D 5e character sheet builder. This guide walks you through creating a new build from scratch.

## Directory layout

| Path | Purpose |
|---|---|
| `Characters/` | The real character builds (one file per build) |
| `Tests/` | Test builds (spell slots, multiclassing) |
| `Examples/` | `_TEMPLATE.py` and a worked example |
| `GeneratedBuilds/` | Output of the Character Creator UI |
| `CharacterCreator/` | The Character Creator UI implementation |
| `CharacterBuilder.py` | Base class every build subclasses |
| `CharacterCreatorUI.py` | Entry point for the Character Creator UI |

## Easiest way: the Character Creator UI

Run from the repo root:

```bash
python Builds/CharacterCreatorUI.py
```

Pick a class, subclass, level, species, ability scores, skills, feats, spells
and equipment in the form. **Preview code** shows the build file it will
write; **Generate** writes it to `Builds/GeneratedBuilds/<Name>.py` and
verifies it by running `.build()`.

To start from an existing build and tweak it, either click **Load build…**
or pass it on the command line:

```bash
python Builds/CharacterCreatorUI.py --load-build Builds/Characters/OptimizedBarbarianBerserker.py
```

Notes:
- Every dropdown is discovered from the codebase, so new subclasses, feats,
  spells and species show up automatically.
- Values the UI cannot represent structurally can always be entered as raw
  Python via the `«code»` choice or the Advanced tab.
- Multiclass builds are not supported by the UI yet; loading one keeps only
  the starter class.

To register a generated build in `RunCharacterCreator.py`, import it from
`Builds.GeneratedBuilds.<Name>` and add it to `BuildSelector.builds()` like
any other build.

## Quick Start

1. **Copy the template**: `Examples/_TEMPLATE.py` → `Characters/MyNewBuild.py`
2. **Edit your build**: Follow the inline TODO comments in the template
3. **Add to RunCharacterCreator.py**: Register your build in `RunCharacterCreator.py`'s `BuildSelector.builds()` dict
4. **Run it**: `python RunCharacterCreator.py` (or test locally first)

## Step-by-Step Guide

### Step 1: Copy the Template

```bash
cp Examples/_TEMPLATE.py Characters/MyNewBuild.py
```

Open `Characters/MyNewBuild.py` in your editor and follow the TODOs.

### Step 2: Choose Your Class and Subclass

**Find valid classes:**
```
CharacterConfigs/BaseClasses/
├── ArtificerBase.py
├── BarbarianBase.py
├── BardBase.py
├── ClericBase.py
├── DruidBase.py
├── FighterBase.py
├── MonkBase.py
├── PaladinBase.py
├── RangerBase.py
├── RogueBase.py
├── SorcererBase.py
├── WarlockBase.py
└── WizardBase.py
```

**Find valid subclasses** (after choosing your class):
```
CharacterConfigs/SubClasses/
├── FighterChampion.py        # Fighter subclass
├── FighterBattleMaster.py     # Fighter subclass
├── ClericKnowledge.py         # Cleric subclass
├── ClericLight.py             # Cleric subclass
├── WizardBladesinger.py       # Wizard subclass
└── ...
```

**In your build file**, update the imports:

```python
# Import your class levels
from CharacterConfigs.BaseClasses.FighterBase import (
    FighterLevel1, FighterLevel2, FighterLevel3, FighterLevel4,
)

# Import your subclass levels and starter class args
from CharacterConfigs.SubClasses2024.FighterChampion import (
    FighterChampionLevel3,
    FighterChampionCustomStarterClassArgs,
)
```

### Step 3: Configure Ability Scores

D&D 5e uses the **Standard Array**: 15, 14, 13, 12, 10, 8

Distribute these among your six abilities:

```python
abilities=StandardArrayAbilitiesStatBlock(
    strength=15,       # High for melee fighters
    dexterity=14,
    constitution=13,   # Keep decent for survivability
    intelligence=8,    # Low for non-casters
    wisdom=12,
    charisma=10,
)
```

**Typical strategies:**
- **Strength-based fighter**: STR=15, CON=13+, DEX/WIS secondary
- **Dexterity-based rogue**: DEX=15, WIS=14, CON=12+
- **Spellcaster (Wizard/Cleric)**: Primary ability=15, CON=13+, WIS or INT=14
- **Monk**: DEX=15, WIS=14, CON=13+

### Step 4: Choose Your Skills

Each class has a limited set of skill proficiencies. Check `StatBlocks/SkillsStatBlock.py` for your class.

Example for Fighter:

```python
from StatBlocks.SkillsStatBlock import FighterSkillsStatBlock

skills=FighterSkillsStatBlock(
    proficiencies={
        Skill.ACROBATICS: True,      # Choose 2 skills
        Skill.ANIMAL_HANDLING: True,
        Skill.ATHLETICS: False,      # Rest are False
        # ... fill in all options
    }
)
```

**Bonus skills from background** (+2 additional):

```python
background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
    [
        Skill.INTIMIDATION,
        Skill.SURVIVAL,
    ]
)
```

### Step 5: Equipment

**Armor:**

Find valid armor in `Features/Equipment/Armor.py`:

```python
armor=[
    Armor.LeatherArmor(),
    Armor.Shield(),
]
```

**Weapons:**

Find valid weapons in `Features/Equipment/Weapons.py`:

```python
weapons=[
    Weapons.Longsword(player_is_proficient=True),
    Weapons.Shortbow(player_is_proficient=True),
]
```

Set `player_is_proficient=True` only if your class has proficiency with that weapon.

### Step 6: Per-Level Features (The Core)

For each level up to `base_class_level`, define features and spells.

**Check what each level requires** by looking at your class file:

```
CharacterConfigs/BaseClasses/YourClassBase.py
```

Example (Fighter):

```python
base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
    base_class_features_by_level={
        1: FighterLevel1(
            weapon_mastery_1=Weapons.Shortsword(),
            weapon_mastery_2=Weapons.Scimitar(),
            weapon_mastery_3=Weapons.Longbow(),
            fighting_style=FightingStyles.Archery(),
        ),
        2: FighterLevel2(),
        3: FighterLevel3(),
        4: FighterLevel4(
            general_feat=GeneralFeats.MountedCombatant(
                character_level=4,
                ability=Ability.STRENGTH,
            ),
        ),
    },
    subclass_features_by_level={
        3: FighterChampionLevel3(),
    },
)
```

**For spellcasters** (Wizard, Cleric, Bard, etc.):

```python
from Spells.SpellLists import WizardLevel0Spells, WizardLevel1Spells

base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
    base_class_features_by_level={
        1: WizardLevel1(
            cantrip_1=WizardLevel0Spells.MAGE_HAND,
            cantrip_2=WizardLevel0Spells.FIRE_BOLT,
            spell_1=WizardLevel1Spells.MAGIC_MISSILE,
            spell_2=WizardLevel1Spells.SHIELD,
        ),
        2: WizardLevel2(...),
    },
    subclass_features_by_level={...},
)
```

Check `Spells/Definitions.py` for spell names and availability by class/level.

### Step 7: Choose Your Species

Find available species in `SpeciesConfigs/`:

```
SpeciesConfigs/
├── Dwarf.py
├── Elf.py
├── Halfling.py
├── Tiefling.py
└── ...
```

Example:

```python
from SpeciesConfigs import Dwarf, Elf

# Simple species
species_builder=Dwarf.DwarfSpeciesBuilder()

# Species with parameters
species_builder=Elf.ElfSpeciesBuilder(
    elven_lineage=Elf.ElvenLineage.WOOD_ELF,
    skill_proficiency=Definitions.Skill.PERCEPTION,
)
```

Check the specific species file to see what parameters are required.

### Step 8: Set Your Character Name

```python
class MyCustomBarbarianCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Thorg the Mighty",  # Your character's name
            starter_class_builder=get_starter_class_builder(),
            species_builder=Elf.ElfSpeciesBuilder(...),
        )
```

## Advanced: Multiclassing

To add a second class, create a multiclass builder:

```python
def get_multiclass_builder():
    return WizardMulticlassBuilder(
        wizard_level=3,
        wizard_level_features=ClassBuilder.BaseClassLevelFeatures(...),
    )

class MyMulticlassCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Blade Singer",
            starter_class_builder=get_starter_class_builder(),  # Fighter 1
            multiclass_builders=[get_multiclass_builder()],      # + Wizard 3
            species_builder=Elf.ElfSpeciesBuilder(...),
        )
```

See `Builds/Tests/MulticlassTest.py` for a complete multiclass example.

## Step 9: Register Your Build

Edit `RunCharacterCreator.py`:

```python
from Builds.Characters.MyNewBuild import MyCustomBarbarianCharacterBuilder

class BuildSelector:
    @staticmethod
    def builds() -> dict[str, CharacterBuilder]:
        return {
            # ... existing builds ...
            "MyCustomBarbarian": MyCustomBarbarianCharacterBuilder(),
        }
```

## Testing Your Build

### Option 1: Run All Builds

```bash
python RunCharacterCreator.py
```

This generates HTML character sheets in the `Output/` directory for all registered builds.

### Option 2: Test Just Your Build

```bash
python -c "
import Definitions
from Builds.Characters.MyNewBuild import MyCustomBarbarianCharacterBuilder
MyCustomBarbarianCharacterBuilder().build().create_character_sheet(
    skill_config=Definitions.SkillConfig.DEFAULT
)
"
```

If there's an error, it will show missing imports or configuration mistakes.

### Option 3: Debug Mode (Python REPL)

```python
from Builds.Characters.MyNewBuild import MyCustomBarbarianCharacterBuilder
builder = MyCustomBarbarianCharacterBuilder()
character_data = builder.build()
# Inspect character_data to debug
print(character_data.character_name)
print(character_data.character_level)
```

## Common Patterns

### Adding Feats at Level-Up

```python
from Features.CharacterFeats import GeneralFeats

8: PaladinLevel8(
    general_feat=GeneralFeats.AbilityScoreImprovement(
        [
            (Ability.WISDOM, 2),
        ]
    ),
),
```

### Adding Spells (Spellcasters)

```python
from Spells.SpellLists import ClericLevel1Spells, ClericLevel2Spells

2: ClericLevel2(
    spell=ClericLevel1Spells.SANCTUARY,
),
3: ClericLevel3(
    spell=ClericLevel2Spells.SPIRITUAL_WEAPON,
),
```

### Weapon Mastery (Fighter)

```python
1: FighterLevel1(
    weapon_mastery_1=Weapons.Longsword(),
    weapon_mastery_2=Weapons.Scimitar(),
    weapon_mastery_3=Weapons.Greatsword(),
    fighting_style=FightingStyles.GreatWeaponFighting(),
),
```

## Troubleshooting

**"ImportError: cannot import..."**
- Check the file paths in your imports match the directory structure exactly
- Verify the class name matches (e.g., `FighterLevel3`, not `Fighter3`)

**"TypeError: __init__() missing required keyword argument..."**
- Check the level class definition in `CharacterConfigs/BaseClasses/YourClassBase.py`
- Verify you're passing all required parameters

**"No such file or directory: Output/..."**
- Create the `Output/` directory manually or run `python RunCharacterCreator.py` once to auto-create it

## More Resources

- **Definitions**: `Definitions.py` — Enums for CharacterClass, Ability, Skill, etc.
- **Existing builds**: `Builds/Characters/Optimized*.py` — Examine real examples for your class
- **Class features**: `CharacterConfigs/BaseClasses/` — See what each level offers
- **Equipment options**: `Features/Equipment/Armor.py`, `Weapons.py`
- **Spells**: `Spells/Definitions.py` — Available spells by class and level
- **Feats**: `Features/CharacterFeats/GeneralFeats.py`, `OriginFeats.py`

## Questions?

Refer back to `Examples/_TEMPLATE.py` or copy an existing build from `Builds/Characters/` and modify it step-by-step. The template is thoroughly commented to guide you through each section.
