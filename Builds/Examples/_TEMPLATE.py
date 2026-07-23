"""
D&D 5e Character Build Template

This template demonstrates how to create a new character build. To create your own:
1. Copy this file to a new build file (e.g., "MyCustomBard.py")
2. Replace the placeholder sections (marked with TODO) with your choices
3. Update the class name at the bottom
4. Add your build to RunCharacterCreator.py's BuildSelector.builds() dict
5. Run: python RunCharacterCreator.py  (or test just your build with the command in the README)

Key sections:
- Imports: Find valid options in the paths noted below
- get_starter_class_builder(): Configure your main class, abilities, skills, spells/features, equipment
- CharacterBuilder subclass: Name your character and set the species
"""

# ============================================================================
# STEP 1: IMPORTS - Find valid options in the paths below, then import them
# ============================================================================

from Builds.CharacterBuilder import CharacterBuilder
from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.ClassBuilder import StarterClassBuilder

# TODO: Replace 'Fighter' with your class name. Available classes:
#   - CharacterConfigs/BaseClasses/FighterBase.py → FighterLevel1, FighterLevel2, ...
#   - CharacterConfigs/BaseClasses/ClericBase.py → ClericLevel1, ClericLevel2, ...
#   - CharacterConfigs/BaseClasses/WizardBase.py → WizardLevel1, WizardLevel2, ...
#   - CharacterConfigs/BaseClasses/ has files for all 13 classes: Artificer, Barbarian,
#     Bard, Cleric, Druid, Fighter, Monk, Paladin, Ranger, Rogue, Sorcerer, Warlock, Wizard
# Import the level classes for YOUR starter class:
from CharacterConfigs.BaseClasses.FighterBase import (
    FighterLevel1,
    FighterLevel2,
    FighterLevel3,
    FighterLevel4,
)

# TODO: Replace 'FighterChampion' with your subclass. Available subclasses per class:
#   Fighter: CharacterConfigs/SubClasses/FighterChampion.py, FighterBattleMaster.py
#   Cleric: CharacterConfigs/SubClasses/ClericKnowledge.py, ClericLight.py, etc.
#   Wizard: CharacterConfigs/SubClasses/WizardBladesinger.py, WizardDiviner.py, etc.
#   See CharacterConfigs/SubClasses/ for all available subclasses
# Import your subclass:
from CharacterConfigs.SubClasses2024.FighterChampion import (
    FighterChampionCustomStarterClassArgs,
    FighterChampionLevel3,
)
from Core.Definitions import Ability, Skill
from Features.CharacterFeats import Backgrounds, GeneralFeats, OriginFeats
from Features.Combat import FightingStyles
from Features.Equipment import Armor, Weapons

# TODO: Replace 'Dwarf' with your desired species. Available species:
#   CharacterConfigs/SpeciesConfigs/ has: Human, Elf, Dwarf, Halfling, Tiefling, Dragonborn,
#   Gnome, Orc, Aasimar, Changeling, Dhampir, Goliath, Hexblood, Kalashtar, Khoravar,
#   Lupin, Reborn, Shifter, Warforged
from SpeciesConfigs import Dwarf
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock

# TODO: Import your class's skill block. Available skill blocks:
#   StatBlocks/SkillsStatBlock.py has: FighterSkillsStatBlock, ClericSkillsStatBlock,
#   WizardSkillsStatBlock, etc. for each class
from StatBlocks.SkillsStatBlock import FighterSkillsStatBlock

# TODO: If your class uses spells (Cleric, Wizard, Bard, Druid, etc.), import spell definitions:
#   from Spells.SpellLists import (
#       WizardLevel0Spells, WizardLevel1Spells, WizardLevel2Spells, ...
#   )
# For Fighter, Monk, Barbarian, Rogue (non-spellcasters), you don't need this


# ============================================================================
# STEP 2: FUNCTION get_starter_class_builder()
# This function builds your main (starter) class configuration.
# ============================================================================


def get_starter_class_builder():
    """
    Configure your character's main class.

    StarterClassBuilder parameters:
    - non_generic_arguments: Class-specific setup (subclass choice, mandatory parameters)
    - base_class_level: Your character level (1-20)
    - abilities: Ability scores using standard array (15,14,13,12,10,8)
    - background_ability_bonuses: Ability score increases from background (+2 to one, +1 to another)
    - background_skill_proficiencies: Two bonus skill proficiencies from background
    - add_default_equipment: True = get default class gear, False = customize with armor/weapons
    - origin_feat: One feat at level 1 from OriginFeats.* (found in Features/CharacterFeats/OriginFeats.py)
    - armor: List of armor pieces (Features/Equipment/Armor.py)
    - weapons: List of weapons (Features/Equipment/Weapons.py)
    - base_class_level_features: Per-level features and spells (see below)
    """

    return StarterClassBuilder(
        # =====================================================================
        # non_generic_arguments: Subclass-specific configuration
        # =====================================================================
        # This varies by subclass. Check CharacterConfigs/SubClasses/YourSubclass.py
        # for a "CustomStarterClassArgs" class to see what's required.
        # Example: FighterChampion requires skills, Fighter BattleMaster would need maneuvers, etc.
        non_generic_arguments=FighterChampionCustomStarterClassArgs(
            skills=FighterSkillsStatBlock(
                proficiencies={
                    # TODO: Set True for 2 skill proficiencies from your class's list
                    # Example: Fighter can choose from Acrobatics, Animal Handling, Athletics,
                    # History, Insight, Intimidation, Perception, Survival
                    Skill.ACROBATICS: True,
                    Skill.ANIMAL_HANDLING: True,
                    Skill.ATHLETICS: False,
                    Skill.HISTORY: False,
                    Skill.INSIGHT: False,
                    Skill.INTIMIDATION: False,
                    Skill.PERCEPTION: False,
                    Skill.SURVIVAL: False,
                }
            ),
        ),
        # =====================================================================
        # base_class_level: Character level (1-20)
        # =====================================================================
        # This determines how many level features you need to define below
        # TODO: Set your desired level (1-20)
        base_class_level=4,
        # =====================================================================
        # abilities: Standard array (15, 14, 13, 12, 10, 8) distributed
        # =====================================================================
        # TODO: Distribute these 6 values among your 6 abilities based on your build
        # Example strategy for Fighter: STR=15 (primary), CON=13+ (survivability),
        # DEX/WIS for AC/initiative, CHA/INT lower priority
        abilities=StandardArrayAbilitiesStatBlock(
            strength=15,  # TODO: Change to fit your character
            dexterity=14,
            constitution=13,
            intelligence=8,
            wisdom=12,
            charisma=10,
        ),
        # =====================================================================
        # background_ability_bonuses: +2 to one ability, +1 to another
        # =====================================================================
        # TODO: Choose which abilities to boost (see Backgrounds.FreeBackgroundAbilityBonus)
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.DEXTERITY, 1),
                (Ability.STRENGTH, 2),
            ]
        ),
        # =====================================================================
        # background_skill_proficiencies: Two additional skill proficiencies
        # =====================================================================
        # TODO: Choose 2 skills not already proficient from Skill enum
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.INTIMIDATION,
                Skill.ATHLETICS,
            ]
        ),
        # =====================================================================
        # add_default_equipment: True = auto-equip class defaults, False = manually set below
        # =====================================================================
        # Set to True for quick builds, False to customize armor/weapons
        add_default_equipment=False,
        # =====================================================================
        # origin_feat: One feat from background/origin
        # =====================================================================
        # TODO: Choose from Features/CharacterFeats/OriginFeats.py
        # Examples: Tough(), Alert(), GiftedLeaner(), etc.
        origin_feat=OriginFeats.SavageAttacker(),
        # =====================================================================
        # armor: Your equipped armor pieces
        # =====================================================================
        # TODO: Choose armor from Features/Equipment/Armor.py
        # Examples: LeatherArmor(), ChainMailArmor(), PlateArmor(), etc.
        armor=[
            Armor.LeatherArmor(),
        ],
        # =====================================================================
        # weapons: Weapons you carry
        # =====================================================================
        # TODO: Choose weapons from Features/Equipment/Weapons.py
        # Set player_is_proficient=True if your class has proficiency
        # Set player_has_mastery=True if you have weapon mastery (Fighter-specific)
        weapons=[
            Weapons.Shortsword(),
            Weapons.Scimitar(),
            Weapons.Longbow(),
        ],
        # =====================================================================
        # base_class_level_features: Per-level class and subclass features
        # =====================================================================
        # This is the core of your character: spells, maneuvers, abilities per level
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            # ----- base_class_features_by_level: Main class features -----
            # Define features for levels 1 through base_class_level
            # TODO: Add a level entry for each level from 1 to base_class_level
            # For each level, construct YourClassLevel#(parameters as required by that level)
            # Check CharacterConfigs/BaseClasses/YourClassBase.py to see what parameters
            # each level class requires.
            base_class_features_by_level={
                1: FighterLevel1(
                    # Level 1 Fighter requires: weapon_mastery_1, _2, _3, fighting_style
                    # See CharacterConfigs/BaseClasses/FighterBase.py for details
                    weapon_mastery_1=Weapons.Shortsword(),
                    weapon_mastery_2=Weapons.Scimitar(),
                    weapon_mastery_3=Weapons.Longbow(),
                    fighting_style=FightingStyles.Archery(),
                ),
                2: FighterLevel2(),
                # Level 3 is usually where you pick a subclass (see subclass_features_by_level below)
                3: FighterLevel3(),
                4: FighterLevel4(
                    # Level 4 often has feat selection. If your class/level has GeneralFeats,
                    # import from Features/CharacterFeats/GeneralFeats.py
                    weapon_mastery=Weapons.Handaxe(),
                    general_feat=GeneralFeats.MountedCombatant(
                        character_level=4,
                        ability=Ability.STRENGTH,
                    ),
                ),
                # TODO: Add levels 5-20 following the same pattern
                # If base_class_level=4, you only need levels 1-4 above
            },
            # ----- subclass_features_by_level: Subclass-specific features -----
            # These typically start at level 3 and continue at intervals (7, 10, 14, 17, 20)
            # TODO: For your subclass, check CharacterConfigs/SubClasses/YourSubclass.py
            # to see which levels have subclass features and what parameters they take
            subclass_features_by_level={
                3: FighterChampionLevel3(),
                # If you were at level 7+, you might add:
                # 7: FighterChampionLevel7(maneuver_1=..., maneuver_2=...),
            },
        ),
    )


# ============================================================================
# STEP 3: CHARACTER BUILDER SUBCLASS
# This creates your final character and sets name + species
# ============================================================================


class YourCharacterNameCharacterBuilder(CharacterBuilder):
    """
    Your character builder. Replace 'YourCharacterName' with a unique class name
    following the pattern: [BuildName]CharacterBuilder

    Example: OptimizedFighterChampionCharacterBuilder, MyCustomBardLoreCharacterBuilder, etc.
    """

    def __init__(self):
        super().__init__(
            # TODO: Set your character's name (appears in character sheet)
            name="My Custom Fighter",
            # Your main class builder (configured above)
            starter_class_builder=get_starter_class_builder(),
            # TODO: Replace Dwarf with your desired species
            # Import from SpeciesConfigs/[SpeciesName].py
            # Some species have parameters (e.g., Elf has elven_lineage and skill_proficiency)
            # Check the species file to see what's required
            species_builder=Dwarf.DwarfSpeciesBuilder(),
            # OPTIONAL: multiclass_builders for multiclassing
            # If you want to multiclass, create additional class builders with
            # the MulticlassBuilder subclass for your secondary class.
            # Example: multiclass_builders=[get_wizard_multiclass_builder()]
            # See Builds/Tests/MulticlassTest.py for a full multiclass example
        )


# ============================================================================
# HOW TO RUN YOUR BUILD
# ============================================================================
# Option 1: Add to RunCharacterCreator.py
#   1. Import your builder in RunCharacterCreator.py:
#      from Builds.Characters.MyBuild import YourCharacterNameCharacterBuilder
#   2. Add to BuildSelector.builds() dict:
#      "MyBuild": YourCharacterNameCharacterBuilder(),
#   3. Run: python RunCharacterCreator.py
#
# Option 2: Test just your build
#   Run: python -c "
#   import Core.Definitions as Definitions
#   from Builds.Examples._TEMPLATE import YourCharacterNameCharacterBuilder
#   YourCharacterNameCharacterBuilder().build().create_character_sheet(
#       skill_config=Definitions.SkillConfig.DEFAULT
#   )
#   "
#
# ============================================================================
# HELPFUL REFERENCES
# ============================================================================
# Definitions: Definitions.py - CharacterClass, Ability, Skill, and class enums
# Classes: CharacterConfigs/BaseClasses/
# Subclasses: CharacterConfigs/SubClasses/
# Species: SpeciesConfigs/
# Spells: Spells/Definitions.py (check spell availability per class/level)
# Feats: Features/CharacterFeats/OriginFeats.py, GeneralFeats.py
# Equipment: Features/Equipment/Armor.py, Weapons.py
# Skills: StatBlocks/SkillsStatBlock.py for class-specific skill blocks
# ============================================================================
