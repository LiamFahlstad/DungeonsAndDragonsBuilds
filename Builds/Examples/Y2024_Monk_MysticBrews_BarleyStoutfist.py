"""Example build: Monk Warrior of Mystic Brews. Demonstrates this staggering, brew-drinking subclass up to its level 17 features."""

from Builds.CharacterBuilder import CharacterBuilder
from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterContent.Classes.BaseClasses.MonkBase import (
    MonkLevel1,
    MonkLevel2,
    MonkLevel3,
    MonkLevel4,
    MonkLevel5,
    MonkLevel6,
    MonkLevel7,
    MonkLevel8,
    MonkLevel9,
    MonkLevel10,
    MonkLevel11,
    MonkLevel12,
    MonkLevel13,
    MonkLevel14,
    MonkLevel15,
    MonkLevel16,
    MonkLevel17,
)
from CharacterContent.Classes.SubClasses2024.MonkMysticBrews import (
    MonkMysticBrewsCustomStarterClassArgs,
    MonkMysticBrewsLevel3,
    MonkMysticBrewsLevel6,
    MonkMysticBrewsLevel11,
    MonkMysticBrewsLevel17,
)
from Core.Definitions import Ability, Skill
from CharacterContent.Features.CharacterFeats import (
    Backgrounds,
    GeneralFeats,
    OriginFeats,
)
from CharacterContent.Species import Human
from Model.AbilityScores import StandardArrayAbilityScores


def get_starter_class_builder():
    monk_level = 17
    return StarterClassBuilder(
        non_generic_arguments=MonkMysticBrewsCustomStarterClassArgs(
            skills=[
                Skill.ACROBATICS,
                Skill.STEALTH,
            ],
            monk_level=monk_level,
            unarmed_strike=Ability.DEXTERITY,
        ),
        base_class_level=monk_level,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilityScores(
            strength=10,
            dexterity=15,
            constitution=13,
            intelligence=8,
            wisdom=14,
            charisma=12,
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.WISDOM, 2),
                (Ability.DEXTERITY, 1),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.PERFORMANCE,
                Skill.PERCEPTION,
            ]
        ),
        add_default_equipment=True,
        origin_feat=OriginFeats.Alert(),
        armor=[],
        weapons=[],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: MonkLevel1(),
                2: MonkLevel2(),
                3: MonkLevel3(),
                4: MonkLevel4(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.DEXTERITY, 2),
                        ]
                    ),
                ),
                5: MonkLevel5(),
                6: MonkLevel6(),
                7: MonkLevel7(),
                8: MonkLevel8(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.WISDOM, 2),
                        ]
                    ),
                ),
                9: MonkLevel9(),
                10: MonkLevel10(),
                11: MonkLevel11(),
                12: MonkLevel12(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.DEXTERITY, 2),
                        ]
                    ),
                ),
                13: MonkLevel13(),
                14: MonkLevel14(),
                15: MonkLevel15(),
                16: MonkLevel16(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.WISDOM, 2),
                        ]
                    ),
                ),
                17: MonkLevel17(),
            },
            subclass_features_by_level={
                # Performance is already known from the background, so Bonus
                # Proficiencies grants a Monk skill instead.
                3: MonkMysticBrewsLevel3(bonus_skill=Skill.INSIGHT),
                6: MonkMysticBrewsLevel6(),
                11: MonkMysticBrewsLevel11(),
                17: MonkMysticBrewsLevel17(),
            },
        ),
    )


class Y2024MonkMysticBrewsBarleyStoutfistCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Barley Stoutfist",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Human.HumanSpeciesBuilder(
                origin_feat=OriginFeats.Skilled(
                    [Skill.HISTORY, Skill.MEDICINE, Skill.SLEIGHT_OF_HAND]
                ),
                skill_proficiency=Skill.ANIMAL_HANDLING,
            ),
        )
