"""Example build: Paladin Oath of Redemption (2014 rules)."""

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
from CharacterContent.Classes.SubClasses2014.PaladinRedemption import (
    PaladinRedemptionLevel3,
    PaladinRedemptionLevel5,
    PaladinRedemptionLevel7,
    PaladinRedemptionLevel9,
    PaladinRedemptionLevel13,
    PaladinRedemptionLevel15,
    PaladinRedemptionLevel17,
    PaladinRedemptionLevel18,
    PaladinRedemptionLevel20,
    PaladinRedemptionCustomStarterClassArgs,
)
from Core.Definitions import Ability, Skill
from CharacterContent.Features.CharacterFeats import Backgrounds, EpicBoon, GeneralFeats, OriginFeats
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
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import PaladinSkillsStatBlock


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=PaladinRedemptionCustomStarterClassArgs(
            skills=PaladinSkillsStatBlock(
                proficiencies={
                    Skill.ATHLETICS: False,
                    Skill.INSIGHT: True,
                    Skill.INTIMIDATION: False,
                    Skill.MEDICINE: False,
                    Skill.PERSUASION: True,
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
                Skill.PERSUASION,
                Skill.INSIGHT,
            ]
        ),
        add_default_equipment=True,
        origin_feat=OriginFeats.Tough(),
        armor=[],
        weapons=[
            Weapons.Longsword(ability=Ability.STRENGTH),
        ],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: PaladinLevel1(
                    weapon_mastery_1=Weapons.Longsword(),
                    weapon_mastery_2=Weapons.Javelin(),
                    spell_1=PaladinLevel1Spells.BLESS,
                    spell_2=PaladinLevel1Spells.COMMAND,
                ),
                2: PaladinLevel2(
                    fighting_style=FightingStyles.Defense(),
                    spell=PaladinLevel1Spells.DIVINE_FAVOR,
                ),
                3: PaladinLevel3(
                    spell=PaladinLevel1Spells.SHIELD_OF_FAITH,
                ),
                4: PaladinLevel4(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.STRENGTH, 2),
                        ]),
                    spell=PaladinLevel1Spells.CURE_WOUNDS,
                ),
                5: PaladinLevel5(
                    spell=PaladinLevel2Spells.MAGIC_WEAPON,
                ),
                6: PaladinLevel6(),
                7: PaladinLevel7(
                    spell=PaladinLevel2Spells.AID,
                ),
                8: PaladinLevel8(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.CHARISMA, 2),
                        ]),
                ),
                9: PaladinLevel9(
                    spell_1=PaladinLevel3Spells.AURA_OF_VITALITY,
                    spell_2=PaladinLevel3Spells.CRUSADERS_MANTLE,
                ),
                10: PaladinLevel10(),
                11: PaladinLevel11(
                    spell=PaladinLevel3Spells.REMOVE_CURSE,
                ),
                12: PaladinLevel12(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.STRENGTH, 2),
                        ]),
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
                            (Ability.CHARISMA, 2),
                        ]),
                ),
                17: PaladinLevel17(
                    spell_1=PaladinLevel5Spells.CIRCLE_OF_POWER,
                    spell_2=PaladinLevel5Spells.GEAS,
                ),
                18: PaladinLevel18(),
                19: PaladinLevel19(
                    epic_boon=EpicBoon.DummyEpicBoon(),
                    spell=PaladinLevel5Spells.HOLY_WEAPON,
                ),
                20: PaladinLevel20(),
            },
            subclass_features_by_level={
                3: PaladinRedemptionLevel3(),
                5: PaladinRedemptionLevel5(),
                7: PaladinRedemptionLevel7(),
                9: PaladinRedemptionLevel9(),
                13: PaladinRedemptionLevel13(),
                15: PaladinRedemptionLevel15(),
                17: PaladinRedemptionLevel17(),
                18: PaladinRedemptionLevel18(),
                20: PaladinRedemptionLevel20(),
            },
        ),
        replace_spells={},
    )


class Y2014PaladinRedemptionPaxMercywardCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Pax Mercyward",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Human.HumanSpeciesBuilder(
                skill_proficiency=Skill.PERSUASION,
                origin_feat=OriginFeats.Alert(),
            ),
        )
