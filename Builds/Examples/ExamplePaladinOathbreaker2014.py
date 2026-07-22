"""Example build: Paladin Oathbreaker (2014 rules)."""

from Builds.CharacterBuilder import CharacterBuilder
from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterConfigs.BaseClasses.PaladinBase import (
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
from CharacterConfigs.SubClasses2014.PaladinOathbreaker import (
    OathbreakerPaladinLevel3,
    OathbreakerPaladinLevel5,
    OathbreakerPaladinLevel7,
    OathbreakerPaladinLevel9,
    OathbreakerPaladinLevel13,
    OathbreakerPaladinLevel15,
    OathbreakerPaladinLevel17,
    OathbreakerPaladinLevel18,
    OathbreakerPaladinLevel20,
    PaladinOathbreakerCustomStarterClassArgs,
)
from Core.Definitions import Ability, Skill
from Features.CharacterFeats import Backgrounds, EpicBoon, GeneralFeats, OriginFeats
from Features.Combat import FightingStyles
from Features.Equipment import Weapons
from SpeciesConfigs import Human
from Spells.SpellLists import (
    PaladinLevel1Spells,
    PaladinLevel2Spells,
    PaladinLevel3Spells,
    PaladinLevel4Spells,
    PaladinLevel5Spells,
)
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import PaladinSkillsStatBlock


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=PaladinOathbreakerCustomStarterClassArgs(
            skills=PaladinSkillsStatBlock(
                proficiencies={
                    Skill.ATHLETICS: True,
                    Skill.INSIGHT: False,
                    Skill.INTIMIDATION: True,
                    Skill.MEDICINE: False,
                    Skill.PERSUASION: False,
                    Skill.RELIGION: False,
                }
            ),
        ),
        base_class_level=20,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilitiesStatBlock(
            strength=15,
            dexterity=10,
            constitution=14,
            intelligence=8,
            wisdom=12,
            charisma=13,
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.STRENGTH, 2),
                (Ability.CHARISMA, 1),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.INTIMIDATION,
                Skill.DECEPTION,
            ]
        ),
        add_default_equipment=True,
        origin_feat=OriginFeats.Tough(),
        armor=[],
        weapons=[
            Weapons.Longsword(player_is_proficient=True, ability=Ability.STRENGTH),
        ],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: PaladinLevel1(
                    weapon_mastery_1=Weapons.Longsword(),
                    weapon_mastery_2=Weapons.Javelin(),
                    spell_1=PaladinLevel1Spells.WRATHFUL_SMITE,
                    spell_2=PaladinLevel1Spells.COMMAND,
                ),
                2: PaladinLevel2(
                    fighting_style=FightingStyles.GreatWeaponFighting(),
                    spell=PaladinLevel1Spells.DIVINE_FAVOR,
                ),
                3: PaladinLevel3(
                    spell=PaladinLevel1Spells.SEARING_SMITE,
                ),
                4: PaladinLevel4(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.STRENGTH, 2),
                        ]
                    ),
                    spell=PaladinLevel1Spells.CURE_WOUNDS,
                ),
                5: PaladinLevel5(
                    spell=PaladinLevel2Spells.SHINING_SMITE,
                ),
                6: PaladinLevel6(),
                7: PaladinLevel7(
                    spell=PaladinLevel2Spells.MAGIC_WEAPON,
                ),
                8: PaladinLevel8(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.CHARISMA, 2),
                        ]
                    ),
                ),
                9: PaladinLevel9(
                    spell_1=PaladinLevel3Spells.BLINDING_SMITE,
                    spell_2=PaladinLevel3Spells.CRUSADERS_MANTLE,
                ),
                10: PaladinLevel10(),
                11: PaladinLevel11(
                    spell=PaladinLevel3Spells.ELEMENTAL_WEAPON,
                ),
                12: PaladinLevel12(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.STRENGTH, 2),
                        ]
                    ),
                ),
                13: PaladinLevel13(
                    spell=PaladinLevel4Spells.STAGGERING_SMITE,
                ),
                14: PaladinLevel14(),
                15: PaladinLevel15(
                    spell=PaladinLevel4Spells.BANISHMENT,
                ),
                16: PaladinLevel16(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.CHARISMA, 2),
                        ]
                    ),
                ),
                17: PaladinLevel17(
                    spell_1=PaladinLevel5Spells.DESTRUCTIVE_WAVE,
                    spell_2=PaladinLevel5Spells.GEAS,
                ),
                18: PaladinLevel18(),
                19: PaladinLevel19(
                    epic_boon=EpicBoon.DummyEpicBoon(),
                    spell=PaladinLevel5Spells.BANISHING_SMITE,
                ),
                20: PaladinLevel20(),
            },
            subclass_features_by_level={
                3: OathbreakerPaladinLevel3(),
                5: OathbreakerPaladinLevel5(),
                7: OathbreakerPaladinLevel7(),
                9: OathbreakerPaladinLevel9(),
                13: OathbreakerPaladinLevel13(),
                15: OathbreakerPaladinLevel15(),
                17: OathbreakerPaladinLevel17(),
                18: OathbreakerPaladinLevel18(),
                20: OathbreakerPaladinLevel20(),
            },
        ),
        replace_spells={},
    )


class ExamplePaladinOathbreaker2014CharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Example Paladin Oathbreaker",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Human.HumanSpeciesBuilder(
                skill_proficiency=Skill.DECEPTION,
                origin_feat=OriginFeats.Alert(),
            ),
        )
