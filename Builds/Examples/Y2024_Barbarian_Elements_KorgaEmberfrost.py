"""Example build: Barbarian Path of the Elements. Exercises every subclass feature up to Barbarian level 14."""

from Builds.CharacterBuilder import CharacterBuilder
from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.BarbarianBase import (
    BarbarianLevel1,
    BarbarianLevel2,
    BarbarianLevel3,
    BarbarianLevel4,
    BarbarianLevel5,
    BarbarianLevel6,
    BarbarianLevel7,
    BarbarianLevel8,
    BarbarianLevel9,
    BarbarianLevel10,
    BarbarianLevel11,
    BarbarianLevel12,
    BarbarianLevel13,
    BarbarianLevel14,
    BarbarianLevel15,
    BarbarianLevel16,
    BarbarianLevel17,
    BarbarianLevel18,
    BarbarianLevel19,
    BarbarianLevel20,
)
from CharacterContent.Classes.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterContent.Classes.SubClasses2024.BarbarianPathOfTheElements import (
    BarbarianElementsCustomStarterClassArgs,
    BarbarianElementsLevel3,
    BarbarianElementsLevel6,
    BarbarianElementsLevel10,
    BarbarianElementsLevel14,
)
from Core.Definitions import Ability, Skill
from CharacterContent.Features.CharacterFeats import (
    Backgrounds,
    EpicBoon,
    GeneralFeats,
    OriginFeats,
)
from CharacterContent.Items import Weapons
from CharacterContent.Species import Orc
from Model.AbilityScores import StandardArrayAbilityScores


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=BarbarianElementsCustomStarterClassArgs(
            skills=[
                Skill.ATHLETICS,
                Skill.NATURE,
            ],
        ),
        base_class_level=14,  # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilityScores(
            strength=15,
            dexterity=13,
            constitution=14,
            intelligence=8,
            wisdom=12,
            charisma=10,
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.CONSTITUTION, 1),
                (Ability.STRENGTH, 2),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.INTIMIDATION,
                Skill.SURVIVAL,
            ]
        ),
        add_default_equipment=False,
        origin_feat=OriginFeats.Tough(),
        armor=[],
        weapons=[
            Weapons.Greataxe(),
            Weapons.Javelin(),
        ],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: BarbarianLevel1(
                    weapon_mastery_1=Weapons.Greataxe(),
                    weapon_mastery_2=Weapons.Javelin(),
                ),
                2: BarbarianLevel2(),
                3: BarbarianLevel3(
                    skill_proficiency=Skill.PERCEPTION,
                ),
                4: BarbarianLevel4(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[(Ability.CONSTITUTION, 2)],
                    )
                ),
                5: BarbarianLevel5(),
                6: BarbarianLevel6(),
                7: BarbarianLevel7(),
                8: BarbarianLevel8(
                    general_feat=GeneralFeats.GreatWeaponMaster(
                        character_level=8,
                        ability=Ability.STRENGTH,
                    )
                ),
                9: BarbarianLevel9(),
                10: BarbarianLevel10(),
                11: BarbarianLevel11(),
                12: BarbarianLevel12(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[(Ability.STRENGTH, 1), (Ability.CONSTITUTION, 1)],
                    )
                ),
                13: BarbarianLevel13(),
                14: BarbarianLevel14(),
                15: BarbarianLevel15(),
                16: BarbarianLevel16(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[(Ability.STRENGTH, 2)],
                    )
                ),
                17: BarbarianLevel17(),
                18: BarbarianLevel18(),
                19: BarbarianLevel19(
                    epic_boon=EpicBoon.DummyEpicBoon(),
                ),
                20: BarbarianLevel20(),
            },
            subclass_features_by_level={
                3: BarbarianElementsLevel3(),
                6: BarbarianElementsLevel6(),
                10: BarbarianElementsLevel10(),
                14: BarbarianElementsLevel14(),
            },
        ),
    )


class Y2024BarbarianElementsKorgaEmberfrostCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Korga Emberfrost",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Orc.OrcSpeciesBuilder(),
        )
