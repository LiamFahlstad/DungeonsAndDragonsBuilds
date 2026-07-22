"""Example build: Ranger Fey Wanderer."""

from Builds.CharacterBuilder import CharacterBuilder
from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterConfigs.BaseClasses.RangerBase import (
    RangerLevel1,
    RangerLevel2,
    RangerLevel3,
)
from CharacterConfigs.SubClasses2024.RangerFeyWanderer import (
    FeyWandererRangerLevel3,
    RangerFeyWandererCustomStarterClassArgs,
)
from Core.Definitions import Ability, Skill
from Features.CharacterFeats import Backgrounds, OriginFeats
from Features.Combat import FightingStyles
from Features.Equipment import Weapons
from SpeciesConfigs import Elf
from SpeciesConfigs.Elf import ElvenLineage
from Spells.SpellLists import RangerLevel1Spells
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import RangerSkillsStatBlock


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=RangerFeyWandererCustomStarterClassArgs(
            skills=RangerSkillsStatBlock(
                proficiencies={
                    Skill.ANIMAL_HANDLING: False,
                    Skill.ATHLETICS: False,
                    Skill.INSIGHT: True,
                    Skill.INVESTIGATION: False,
                    Skill.NATURE: False,
                    Skill.PERCEPTION: True,
                    Skill.STEALTH: True,
                    Skill.SURVIVAL: False,
                }
            ),
        ),
        base_class_level=3,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilitiesStatBlock(
            strength=8,
            dexterity=15,
            constitution=12,
            intelligence=10,
            wisdom=14,
            charisma=13,
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.DEXTERITY, 1),
                (Ability.CHARISMA, 2),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.INSIGHT,
                Skill.DECEPTION,
            ]
        ),
        add_default_equipment=True,
        origin_feat=OriginFeats.Alert(),
        armor=[],
        weapons=[],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: RangerLevel1(
                    weapon_mastery_1=Weapons.Longbow(),
                    weapon_mastery_2=Weapons.Dagger(),
                    spell_1=RangerLevel1Spells.ENSNARING_STRIKE,
                    spell_2=RangerLevel1Spells.GOODBERRY,
                ),
                2: RangerLevel2(
                    skill=Skill.INSIGHT,
                    fighting_style=FightingStyles.Archery(),
                    spell=RangerLevel1Spells.ANIMAL_FRIENDSHIP,
                ),
                3: RangerLevel3(
                    spell=RangerLevel1Spells.DETECT_MAGIC,
                ),
            },
            subclass_features_by_level={
                3: FeyWandererRangerLevel3(),
            },
        ),
        replace_spells={},
    )


class ExampleRangerFeyWandererCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Example Ranger Fey Wanderer",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Elf.ElfSpeciesBuilder(
                elven_lineage=ElvenLineage.WOOD_ELF,
                skill_proficiency=Skill.PERCEPTION,
            ),
        )
