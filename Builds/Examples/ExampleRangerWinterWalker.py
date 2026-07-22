"""Example build: Ranger Winter Walker."""

from Builds.CharacterBuilder import CharacterBuilder
from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterConfigs.BaseClasses.RangerBase import (
    RangerLevel1,
    RangerLevel2,
    RangerLevel3,
)
from CharacterConfigs.SubClasses2024.RangerWinterWalker import (
    RangerWinterWalkerCustomStarterClassArgs,
    WinterWalkerRangerLevel3,
)
from Core.Definitions import Ability, Skill
from Features.CharacterFeats import Backgrounds, OriginFeats
from Features.Combat import FightingStyles
from Features.Equipment import Weapons
from SpeciesConfigs import Dwarf
from Spells.SpellLists import RangerLevel1Spells
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import RangerSkillsStatBlock


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=RangerWinterWalkerCustomStarterClassArgs(
            skills=RangerSkillsStatBlock(
                proficiencies={
                    Skill.ANIMAL_HANDLING: False,
                    Skill.ATHLETICS: False,
                    Skill.INSIGHT: False,
                    Skill.INVESTIGATION: False,
                    Skill.NATURE: True,
                    Skill.PERCEPTION: True,
                    Skill.STEALTH: True,
                    Skill.SURVIVAL: False,
                }
            ),
        ),
        base_class_level=3,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilitiesStatBlock(
            strength=13,
            dexterity=15,
            constitution=14,
            intelligence=8,
            wisdom=12,
            charisma=10,
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.DEXTERITY, 2),
                (Ability.CONSTITUTION, 1),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.SURVIVAL,
                Skill.ATHLETICS,
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
                    spell_1=RangerLevel1Spells.FOG_CLOUD,
                    spell_2=RangerLevel1Spells.ENSNARING_STRIKE,
                ),
                2: RangerLevel2(
                    skill=Skill.SURVIVAL,
                    fighting_style=FightingStyles.Archery(),
                    spell=RangerLevel1Spells.ENTANGLE,
                ),
                3: RangerLevel3(
                    spell=RangerLevel1Spells.GOODBERRY,
                ),
            },
            subclass_features_by_level={
                3: WinterWalkerRangerLevel3(),
            },
        ),
        replace_spells={},
    )


class ExampleRangerWinterWalkerCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Example Ranger Winter Walker",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Dwarf.DwarfSpeciesBuilder(),
        )
