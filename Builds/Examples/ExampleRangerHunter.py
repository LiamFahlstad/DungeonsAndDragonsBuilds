"""Example build: Ranger Hunter."""

from Builds.CharacterBuilder import CharacterBuilder
from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterConfigs.BaseClasses.RangerBase import (
    RangerLevel1,
    RangerLevel2,
    RangerLevel3,
)
from CharacterConfigs.SubClasses2024.RangerHunter import (
    HunterRangerLevel3,
    RangerHunterCustomStarterClassArgs,
)
from Definitions import Ability, Skill
from Features.CharacterFeats import Backgrounds
from Features.CharacterFeats import OriginFeats
from Features.CharacterFeats import OriginFeats as SpeciesOriginFeats
from Features.Combat import FightingStyles
from Features.Equipment import Weapons
from SpeciesConfigs import Human
from Spells.SpellLists import RangerLevel1Spells
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import RangerSkillsStatBlock


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=RangerHunterCustomStarterClassArgs(
            skills=RangerSkillsStatBlock(
                proficiencies={
                    Skill.ANIMAL_HANDLING: True,
                    Skill.ATHLETICS: False,
                    Skill.INSIGHT: False,
                    Skill.INVESTIGATION: False,
                    Skill.NATURE: False,
                    Skill.PERCEPTION: True,
                    Skill.STEALTH: False,
                    Skill.SURVIVAL: True,
                }
            ),
        ),
        base_class_level=3,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilitiesStatBlock(
            strength=14,
            dexterity=15,
            constitution=13,
            intelligence=8,
            wisdom=12,
            charisma=10,
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.DEXTERITY, 1),
                (Ability.WISDOM, 2),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.SURVIVAL,
                Skill.NATURE,
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
                    weapon_mastery_2=Weapons.Shortsword(),
                    spell_1=RangerLevel1Spells.ENSNARING_STRIKE,
                    spell_2=RangerLevel1Spells.FOG_CLOUD,
                ),
                2: RangerLevel2(
                    skill=Skill.SURVIVAL,
                    fighting_style=FightingStyles.Archery(),
                    spell=RangerLevel1Spells.ENTANGLE,
                ),
                3: RangerLevel3(
                    spell=RangerLevel1Spells.ANIMAL_FRIENDSHIP,
                ),
            },
            subclass_features_by_level={
                3: HunterRangerLevel3(),
            },
        ),
        replace_spells={},
    )


class ExampleRangerHunterCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Example Ranger Hunter",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Human.HumanSpeciesBuilder(
                origin_feat=SpeciesOriginFeats.Tough(),
                skill_proficiency=Skill.SURVIVAL,
            ),
        )
