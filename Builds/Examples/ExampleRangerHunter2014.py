"""Example build: Ranger Hunter (2014 rules). Demonstrates the subclass up through level 15."""

from Builds.CharacterBuilder import CharacterBuilder
from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterConfigs.BaseClasses.RangerBase import (
    RangerLevel1,
    RangerLevel2,
    RangerLevel3,
    RangerLevel4,
    RangerLevel5,
    RangerLevel6,
    RangerLevel7,
    RangerLevel8,
    RangerLevel9,
    RangerLevel10,
    RangerLevel11,
    RangerLevel12,
    RangerLevel13,
    RangerLevel14,
    RangerLevel15,
)
from CharacterConfigs.SubClasses2014.RangerHunter import (
    RangerHunterLevel3,
    RangerHunterLevel7,
    RangerHunterLevel11,
    RangerHunterLevel15,
    RangerHunterCustomStarterClassArgs,
)
from Definitions import Ability, Skill
from Features.CharacterFeats import Backgrounds, GeneralFeats, OriginFeats
from Features.Combat import FightingStyles
from Features.Equipment import Weapons
from SpeciesConfigs import Human
from Spells.SpellLists import RangerLevel1Spells, RangerLevel2Spells, RangerLevel3Spells, RangerLevel4Spells
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import RangerSkillsStatBlock


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=RangerHunterCustomStarterClassArgs(
            skills=RangerSkillsStatBlock(
                proficiencies={
                    Skill.ANIMAL_HANDLING: False,
                    Skill.ATHLETICS: True,
                    Skill.INSIGHT: False,
                    Skill.INVESTIGATION: False,
                    Skill.NATURE: False,
                    Skill.PERCEPTION: True,
                    Skill.STEALTH: False,
                    Skill.SURVIVAL: True,
                }
            ),
        ),
        base_class_level=15,
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
        weapons=[
            Weapons.Longbow(player_is_proficient=True, ability=Ability.DEXTERITY),
        ],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: RangerLevel1(
                    weapon_mastery_1=Weapons.Longbow(),
                    weapon_mastery_2=Weapons.Shortsword(),
                    spell_1=RangerLevel1Spells.ENSNARING_STRIKE,
                    spell_2=RangerLevel1Spells.GOODBERRY,
                ),
                2: RangerLevel2(
                    skill=Skill.PERCEPTION,
                    fighting_style=FightingStyles.Archery(),
                    spell=RangerLevel1Spells.ANIMAL_FRIENDSHIP,
                ),
                3: RangerLevel3(
                    spell=RangerLevel1Spells.ZEPHYR_STRIKE,
                ),
                4: RangerLevel4(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[
                            (Ability.DEXTERITY, 2),
                        ]
                    ),
                    spell=RangerLevel1Spells.LONGSTRIDER,
                ),
                5: RangerLevel5(
                    spell=RangerLevel2Spells.PASS_WITHOUT_TRACE,
                ),
                6: RangerLevel6(),
                7: RangerLevel7(
                    spell=RangerLevel2Spells.SPIKE_GROWTH,
                ),
                8: RangerLevel8(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[
                            (Ability.WISDOM, 1),
                            (Ability.CONSTITUTION, 1),
                        ]
                    ),
                ),
                9: RangerLevel9(
                    skill_1=Skill.SURVIVAL,
                    skill_2=Skill.ATHLETICS,
                    spell_1=RangerLevel3Spells.CONJURE_ANIMALS,
                    spell_2=RangerLevel2Spells.ENHANCE_ABILITY,
                ),
                10: RangerLevel10(),
                11: RangerLevel11(
                    spell=RangerLevel3Spells.LIGHTNING_ARROW,
                ),
                12: RangerLevel12(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[
                            (Ability.DEXTERITY, 2),
                        ]
                    ),
                ),
                13: RangerLevel13(
                    spell=RangerLevel4Spells.LOCATE_CREATURE,
                ),
                14: RangerLevel14(),
                15: RangerLevel15(
                    spell=RangerLevel4Spells.GUARDIAN_OF_NATURE,
                ),
            },
            subclass_features_by_level={
                3: RangerHunterLevel3(),
                7: RangerHunterLevel7(),
                11: RangerHunterLevel11(),
                15: RangerHunterLevel15(),
            },
        ),
        replace_spells={},
    )


class ExampleRangerHunter2014CharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Example Ranger Hunter",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Human.HumanSpeciesBuilder(
                skill_proficiency=Skill.SURVIVAL,
                origin_feat=OriginFeats.Alert(),
            ),
        )
