"""Example build: Fighter Sorrow Knight. A Strength/Wisdom great-weapon fighter built to demonstrate this subclass."""

from Builds.CharacterBuilder import CharacterBuilder
from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterContent.Classes.BaseClasses.FighterBase import (
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
from CharacterContent.Classes.SubClasses2024.FighterSorrowKnight import (
    FighterSorrowKnightCustomStarterClassArgs,
    FighterSorrowKnightLevel3,
    FighterSorrowKnightLevel7,
    FighterSorrowKnightLevel10,
    FighterSorrowKnightLevel15,
    FighterSorrowKnightLevel18,
)
from Core.Definitions import Ability, Skill
from CharacterContent.Features.CharacterFeats import (
    Backgrounds,
    GeneralFeats,
    OriginFeats,
)
from CharacterContent.Features.CombatFeatures import FightingStyles
from CharacterContent.Items import Armor, Weapons
from CharacterContent.Species import Orc
from Model.AbilityScores import StandardArrayAbilityScores


def get_starter_class_builder():
    fighter_level = 18
    return StarterClassBuilder(
        non_generic_arguments=FighterSorrowKnightCustomStarterClassArgs(
            skills=[
                Skill.ATHLETICS,
                Skill.INTIMIDATION,
            ],
        ),
        base_class_level=fighter_level,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilityScores(
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
                Skill.INSIGHT,
                Skill.PERCEPTION,
            ]
        ),
        add_default_equipment=False,
        origin_feat=OriginFeats.Alert(),
        armor=[
            Armor.PlateArmor(),
        ],
        weapons=[
            Weapons.Greatsword(),
            Weapons.Javelin(),
        ],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: FighterLevel1(
                    weapon_mastery_1=Weapons.Greatsword(),
                    weapon_mastery_2=Weapons.Maul(),
                    weapon_mastery_3=Weapons.Javelin(),
                    fighting_style=FightingStyles.GreatWeaponFighting(),
                ),
                2: FighterLevel2(),
                3: FighterLevel3(),
                4: FighterLevel4(
                    weapon_mastery=Weapons.Glaive(),
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[(Ability.STRENGTH, 1), (Ability.WISDOM, 1)]
                    ),
                ),
                5: FighterLevel5(),
                6: FighterLevel6(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[(Ability.STRENGTH, 2)]
                    ),
                ),
                7: FighterLevel7(),
                8: FighterLevel8(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[(Ability.WISDOM, 2)]
                    ),
                ),
                9: FighterLevel9(),
                10: FighterLevel10(
                    weapon_mastery=Weapons.Longsword(),
                ),
                11: FighterLevel11(),
                12: FighterLevel12(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[(Ability.CONSTITUTION, 2)]
                    ),
                ),
                13: FighterLevel13(),
                14: FighterLevel14(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[(Ability.WISDOM, 2)]
                    ),
                ),
                15: FighterLevel15(),
                16: FighterLevel16(
                    weapon_mastery=Weapons.Halberd(),
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[(Ability.CONSTITUTION, 2)]
                    ),
                ),
                17: FighterLevel17(),
                18: FighterLevel18(),
            },
            subclass_features_by_level={
                3: FighterSorrowKnightLevel3(),
                7: FighterSorrowKnightLevel7(),
                10: FighterSorrowKnightLevel10(),
                15: FighterSorrowKnightLevel15(),
                18: FighterSorrowKnightLevel18(),
            },
        ),
    )


class Y2024FighterSorrowKnightMoiraAshenveilCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Moira Ashenveil",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Orc.OrcSpeciesBuilder(),
        )
