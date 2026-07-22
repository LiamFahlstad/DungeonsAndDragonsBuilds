"""Example build: Fighter Banneret. Adapted from an optimized reference build to demonstrate this subclass."""

from Builds.CharacterBuilder import CharacterBuilder
from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterConfigs.BaseClasses.FighterBase import (
    FighterLevel1,
    FighterLevel2,
    FighterLevel3,
    FighterLevel4,
    FighterLevel5,
    FighterLevel6,
    FighterLevel7,
    FighterLevel8,
    FighterLevel9,
    FighterLevel10,
    FighterLevel11,
    FighterLevel12,
    FighterLevel13,
    FighterLevel14,
    FighterLevel15,
    FighterLevel16,
    FighterLevel17,
    FighterLevel18,
)
from CharacterConfigs.SubClasses2024.FighterBanneret import (
    FighterBanneretCustomStarterClassArgs,
    FighterBanneretLevel3,
    FighterBanneretLevel7,
    FighterBanneretLevel10,
    FighterBanneretLevel15,
    FighterBanneretLevel18,
)
from Core.Definitions import Ability, Skill
from Features.CharacterFeats import Backgrounds, GeneralFeats, OriginFeats
from Features.Combat import FightingStyles
from Features.Equipment import Armor, Weapons
from SpeciesConfigs import Human
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import FighterSkillsStatBlock


def get_starter_class_builder():
    fighter_level = 18
    return StarterClassBuilder(
        non_generic_arguments=FighterBanneretCustomStarterClassArgs(
            skills=FighterSkillsStatBlock(
                proficiencies={
                    Skill.ACROBATICS: False,
                    Skill.ANIMAL_HANDLING: False,
                    Skill.ATHLETICS: True,
                    Skill.HISTORY: False,
                    Skill.INSIGHT: True,
                    Skill.INTIMIDATION: False,
                    Skill.PERCEPTION: False,
                    Skill.SURVIVAL: False,
                }
            ),
        ),
        base_class_level=fighter_level,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilitiesStatBlock(
            strength=15,
            dexterity=12,
            constitution=14,
            intelligence=8,
            wisdom=10,
            charisma=13,
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.STRENGTH, 1),
                (Ability.CHARISMA, 2),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.PERSUASION,
                Skill.PERCEPTION,
            ]
        ),
        add_default_equipment=False,
        origin_feat=OriginFeats.Tough(),
        armor=[
            Armor.ChainMailArmor(),
        ],
        weapons=[
            Weapons.Longsword(player_is_proficient=True),
            Weapons.Greatsword(player_is_proficient=True),
        ],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: FighterLevel1(
                    weapon_mastery_1=Weapons.Longsword(),
                    weapon_mastery_2=Weapons.Flail(),
                    weapon_mastery_3=Weapons.Greatsword(),
                    fighting_style=FightingStyles.Defense(),
                ),
                2: FighterLevel2(),
                3: FighterLevel3(),
                4: FighterLevel4(
                    weapon_mastery=Weapons.Handaxe(),
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[(Ability.CHARISMA, 2)],
                    ),
                ),
                5: FighterLevel5(),
                6: FighterLevel6(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[(Ability.STRENGTH, 2)],
                    ),
                ),
                7: FighterLevel7(),
                8: FighterLevel8(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[(Ability.CHARISMA, 2)],
                    ),
                ),
                9: FighterLevel9(),
                10: FighterLevel10(
                    weapon_mastery=Weapons.Rapier(),
                ),
                11: FighterLevel11(),
                12: FighterLevel12(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[(Ability.STRENGTH, 2)],
                    ),
                ),
                13: FighterLevel13(),
                14: FighterLevel14(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[(Ability.CONSTITUTION, 2)],
                    ),
                ),
                15: FighterLevel15(),
                16: FighterLevel16(
                    weapon_mastery=Weapons.Warhammer(),
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[(Ability.CHARISMA, 2)],
                    ),
                ),
                17: FighterLevel17(),
                18: FighterLevel18(),
            },
            subclass_features_by_level={
                3: FighterBanneretLevel3(),
                7: FighterBanneretLevel7(),
                10: FighterBanneretLevel10(),
                15: FighterBanneretLevel15(),
                18: FighterBanneretLevel18(),
            },
        ),
    )


class ExampleFighterBanneretCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Example Fighter Banneret",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Human.HumanSpeciesBuilder(
                skill_proficiency=Skill.SURVIVAL,
                origin_feat=OriginFeats.Skilled(
                    skills=[
                        Skill.PERSUASION,
                        Skill.INVESTIGATION,
                        Skill.HISTORY,
                    ]
                ),
            ),
        )
