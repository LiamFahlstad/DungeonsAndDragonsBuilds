"""Example build: Paladin Oath of the Holy (World of Warcraft). A Charisma-forward support paladin with a Longsword and Shield."""

from Builds.CharacterBuilder import CharacterBuilder
from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterContent.Classes.BaseClasses.PaladinBase import (
    PaladinLevel1,
    PaladinLevel2,
    PaladinLevel3,
    PaladinLevel4,
    PaladinLevel5,
    PaladinLevel6,
    PaladinLevel7,
    PaladinLevel8,
    PaladinLevel9,
    PaladinLevel10,
    PaladinLevel11,
    PaladinLevel12,
    PaladinLevel13,
    PaladinLevel14,
    PaladinLevel15,
    PaladinLevel16,
    PaladinLevel17,
    PaladinLevel18,
    PaladinLevel19,
    PaladinLevel20,
)
from CharacterContent.Classes.SubClasses2024.PaladinHoly import (
    PaladinHolyCustomStarterClassArgs,
    PaladinHolyLevel3,
    PaladinHolyLevel5,
    PaladinHolyLevel7,
    PaladinHolyLevel9,
    PaladinHolyLevel13,
    PaladinHolyLevel15,
    PaladinHolyLevel17,
    PaladinHolyLevel20,
)
from Core.Definitions import Ability, Skill
from CharacterContent.Features.CharacterFeats import (
    Backgrounds,
    EpicBoon,
    GeneralFeats,
    OriginFeats,
)
from CharacterContent.Features.CombatFeatures import FightingStyles
from CharacterContent.Items import Weapons
from CharacterContent.Species import Human
from CharacterContent.Spells.SpellLists import (
    PaladinLevel1Spells,
    PaladinLevel2Spells,
    PaladinLevel3Spells,
    PaladinLevel4Spells,
    PaladinLevel5Spells,
)
from Model.AbilityScores import StandardArrayAbilityScores


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=PaladinHolyCustomStarterClassArgs(
            skills=[
                Skill.MEDICINE,
                Skill.PERSUASION,
            ],
        ),
        base_class_level=20,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilityScores(
            strength=14,
            dexterity=8,
            constitution=13,
            intelligence=10,
            wisdom=12,
            charisma=15,
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.CHARISMA, 2),
                (Ability.CONSTITUTION, 1),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.RELIGION,
                Skill.INSIGHT,
            ]
        ),
        add_default_equipment=True,
        origin_feat=OriginFeats.Healer(),
        armor=[],
        weapons=[],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: PaladinLevel1(
                    weapon_mastery_1=Weapons.Longsword(),
                    weapon_mastery_2=Weapons.Javelin(),
                    spell_1=PaladinLevel1Spells.BLESS,
                    spell_2=PaladinLevel1Spells.SHIELD_OF_FAITH,
                ),
                2: PaladinLevel2(
                    fighting_style=FightingStyles.Protection(),
                    spell=PaladinLevel1Spells.DIVINE_FAVOR,
                ),
                3: PaladinLevel3(
                    spell=PaladinLevel1Spells.PROTECTION_FROM_EVIL_AND_GOOD,
                ),
                4: PaladinLevel4(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.CHARISMA, 2),
                        ]
                    ),
                    spell=PaladinLevel1Spells.HEROISM,
                ),
                5: PaladinLevel5(
                    spell=PaladinLevel2Spells.AID,
                ),
                6: PaladinLevel6(),
                7: PaladinLevel7(
                    spell=PaladinLevel2Spells.WARDING_BOND,
                ),
                8: PaladinLevel8(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.CONSTITUTION, 2),
                        ]
                    ),
                ),
                9: PaladinLevel9(
                    spell_1=PaladinLevel3Spells.REVIVIFY,
                    spell_2=PaladinLevel3Spells.AURA_OF_VITALITY,
                ),
                10: PaladinLevel10(),
                11: PaladinLevel11(
                    spell=PaladinLevel3Spells.DAYLIGHT,
                ),
                12: PaladinLevel12(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.STRENGTH, 2),
                        ]
                    ),
                ),
                13: PaladinLevel13(
                    spell=PaladinLevel4Spells.AURA_OF_PURITY,
                ),
                14: PaladinLevel14(),
                15: PaladinLevel15(
                    spell=PaladinLevel4Spells.BANISHMENT,
                ),
                16: PaladinLevel16(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.WISDOM, 2),
                        ]
                    ),
                ),
                17: PaladinLevel17(
                    spell_1=PaladinLevel5Spells.RAISE_DEAD,
                    spell_2=PaladinLevel5Spells.CIRCLE_OF_POWER,
                ),
                18: PaladinLevel18(),
                19: PaladinLevel19(
                    epic_boon=EpicBoon.DummyEpicBoon(),
                    spell=PaladinLevel5Spells.HOLY_WEAPON,
                ),
                20: PaladinLevel20(),
            },
            subclass_features_by_level={
                3: PaladinHolyLevel3(),
                5: PaladinHolyLevel5(),
                7: PaladinHolyLevel7(),
                9: PaladinHolyLevel9(),
                13: PaladinHolyLevel13(),
                15: PaladinHolyLevel15(),
                17: PaladinHolyLevel17(),
                20: PaladinHolyLevel20(),
            },
        ),
    )


class Y2024PaladinHolyLioraDawnmendCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Liora Dawnmend",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Human.HumanSpeciesBuilder(
                skill_proficiency=Skill.PERCEPTION,
                origin_feat=OriginFeats.Skilled(
                    skills=[
                        Skill.ATHLETICS,
                        Skill.HISTORY,
                        Skill.ARCANA,
                    ]
                ),
            ),
        )
