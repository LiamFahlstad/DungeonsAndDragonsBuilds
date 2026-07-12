"""Example build: Ranger Hollow Warden."""

from Builds.CharacterBuilder import CharacterBuilder
from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterConfigs.BaseClasses.RangerBase import (
    RangerLevel1,
    RangerLevel2,
    RangerLevel3,
)
from CharacterConfigs.SubClasses.RangerHollowWarden import (
    RangerHollowWardenLevel3,
    RangerHollowWardenCustomStarterClassArgs,
)
from Definitions import Ability, Skill
from Features.CharacterFeats import Backgrounds, OriginFeats
from Features.Combat import FightingStyles
from Features.Equipment import Weapons
from SpeciesConfigs import Orc
from Spells.SpellLists import RangerLevel1Spells
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import RangerSkillsStatBlock


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=RangerHollowWardenCustomStarterClassArgs(
            skills=RangerSkillsStatBlock(
                proficiencies={
                    Skill.ANIMAL_HANDLING: False,
                    Skill.ATHLETICS: True,
                    Skill.INSIGHT: False,
                    Skill.INVESTIGATION: False,
                    Skill.NATURE: True,
                    Skill.PERCEPTION: True,
                    Skill.STEALTH: False,
                    Skill.SURVIVAL: False,
                }
            ),
        ),
        base_class_level=3,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilitiesStatBlock(
            strength=15,
            dexterity=12,
            constitution=14,
            intelligence=8,
            wisdom=13,
            charisma=10,
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.STRENGTH, 2),
                (Ability.WISDOM, 1),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.ATHLETICS,
                Skill.SURVIVAL,
            ]
        ),
        add_default_equipment=True,
        origin_feat=OriginFeats.Tough(),
        armor=[],
        weapons=[],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: RangerLevel1(
                    weapon_mastery_1=Weapons.Greataxe(),
                    weapon_mastery_2=Weapons.Shortsword(),
                    spell_1=RangerLevel1Spells.FOG_CLOUD,
                    spell_2=RangerLevel1Spells.GOODBERRY,
                ),
                2: RangerLevel2(
                    skill=Skill.SURVIVAL,
                    fighting_style=FightingStyles.Dueling(),
                    spell=RangerLevel1Spells.ENTANGLE,
                ),
                3: RangerLevel3(
                    spell=RangerLevel1Spells.ANIMAL_FRIENDSHIP,
                ),
            },
            subclass_features_by_level={
                3: RangerHollowWardenLevel3(),
            },
        ),
        replace_spells={},
    )


class ExampleRangerHollowWardenCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Example Ranger Hollow Warden",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Orc.OrcSpeciesBuilder(),
        )
