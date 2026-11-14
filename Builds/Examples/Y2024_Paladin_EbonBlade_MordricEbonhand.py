"""Example build: Paladin Oath of the Ebon Blade (World of Warcraft). A Strength-based Unholy-rune death knight with a Greatsword."""

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
from CharacterContent.Classes.SubClasses2024.PaladinEbonBlade import (
    PaladinEbonBladeCustomStarterClassArgs,
    PaladinEbonBladeLevel3,
    PaladinEbonBladeLevel5,
    PaladinEbonBladeLevel7,
    PaladinEbonBladeLevel9,
    PaladinEbonBladeLevel11,
    PaladinEbonBladeLevel13,
    PaladinEbonBladeLevel14,
    PaladinEbonBladeLevel15,
    PaladinEbonBladeLevel17,
    PaladinEbonBladeLevel20,
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
        non_generic_arguments=PaladinEbonBladeCustomStarterClassArgs(
            skills=[
                Skill.ATHLETICS,
                Skill.INTIMIDATION,
            ],
        ),
        base_class_level=20,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilityScores(
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
                Skill.RELIGION,
                Skill.STEALTH,
            ]
        ),
        add_default_equipment=True,
        origin_feat=OriginFeats.Tough(),
        armor=[],
        weapons=[],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: PaladinLevel1(
                    weapon_mastery_1=Weapons.Greatsword(),
                    weapon_mastery_2=Weapons.Javelin(),
                    spell_1=PaladinLevel1Spells.COMMAND,
                    spell_2=PaladinLevel1Spells.DIVINE_FAVOR,
                ),
                2: PaladinLevel2(
                    fighting_style=FightingStyles.GreatWeaponFighting(),
                    spell=PaladinLevel1Spells.WRATHFUL_SMITE,
                ),
                3: PaladinLevel3(
                    spell=PaladinLevel1Spells.SHIELD_OF_FAITH,
                ),
                4: PaladinLevel4(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.STRENGTH, 2),
                        ]
                    ),
                    spell=PaladinLevel1Spells.SEARING_SMITE,
                ),
                5: PaladinLevel5(
                    spell=PaladinLevel2Spells.MAGIC_WEAPON,
                ),
                6: PaladinLevel6(),
                7: PaladinLevel7(
                    spell=PaladinLevel2Spells.BRANDING_SMITE,
                ),
                8: PaladinLevel8(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.CHARISMA, 2),
                        ]
                    ),
                ),
                9: PaladinLevel9(
                    spell_1=PaladinLevel3Spells.SPIRIT_SHROUD,
                    spell_2=PaladinLevel3Spells.REMOVE_CURSE,
                ),
                10: PaladinLevel10(),
                11: PaladinLevel11(
                    spell=PaladinLevel3Spells.BLINDING_SMITE,
                ),
                12: PaladinLevel12(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.CHARISMA, 2),
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
                            (Ability.CONSTITUTION, 2),
                        ]
                    ),
                ),
                17: PaladinLevel17(
                    spell_1=PaladinLevel5Spells.BANISHING_SMITE,
                    spell_2=PaladinLevel5Spells.DESTRUCTIVE_WAVE,
                ),
                18: PaladinLevel18(),
                19: PaladinLevel19(
                    epic_boon=EpicBoon.DummyEpicBoon(),
                    spell=PaladinLevel5Spells.HOLY_WEAPON,
                ),
                20: PaladinLevel20(),
            },
            subclass_features_by_level={
                3: PaladinEbonBladeLevel3(),
                5: PaladinEbonBladeLevel5(),
                7: PaladinEbonBladeLevel7(),
                9: PaladinEbonBladeLevel9(),
                11: PaladinEbonBladeLevel11(),
                13: PaladinEbonBladeLevel13(),
                14: PaladinEbonBladeLevel14(),
                15: PaladinEbonBladeLevel15(),
                17: PaladinEbonBladeLevel17(),
                20: PaladinEbonBladeLevel20(),
            },
        ),
    )


class Y2024PaladinEbonBladeMordricEbonhandCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Mordric Ebonhand",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Human.HumanSpeciesBuilder(
                skill_proficiency=Skill.SURVIVAL,
                origin_feat=OriginFeats.Skilled(
                    skills=[
                        Skill.PERCEPTION,
                        Skill.INSIGHT,
                        Skill.HISTORY,
                    ]
                ),
            ),
        )
