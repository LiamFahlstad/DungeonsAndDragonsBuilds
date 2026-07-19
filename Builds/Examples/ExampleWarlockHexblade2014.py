"""Example build: Warlock Hexblade Patron (2014 rules). Demonstrates the subclass up through level 14."""

from Builds.CharacterBuilder import CharacterBuilder
from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterConfigs.BaseClasses.WarlockBase import (
    WarlockLevel1,
    WarlockLevel2,
    WarlockLevel3,
    WarlockLevel4,
    WarlockLevel5,
    WarlockLevel6,
    WarlockLevel7,
    WarlockLevel8,
    WarlockLevel9,
    WarlockLevel10,
    WarlockLevel11,
    WarlockLevel12,
    WarlockLevel13,
    WarlockLevel14,
)
from CharacterConfigs.SubClasses2014.WarlockHexblade import (
    HexbladeWarlockLevel3,
    HexbladeWarlockLevel6,
    HexbladeWarlockLevel10,
    HexbladeWarlockLevel14,
    WarlockHexbladeCustomStarterClassArgs,
)
from Definitions import Ability, Skill
from Features.CharacterFeats import Backgrounds, GeneralFeats, OriginFeats
from Invocations.Definitions import (
    InvocationsLevel0,
    InvocationsLevel2,
    InvocationsLevel5,
    InvocationsLevel7,
    InvocationsLevel9,
    InvocationsLevel12,
)
from SpeciesConfigs import Human
from Spells.SpellLists import (
    WarlockLevel0Spells,
    WarlockLevel1Spells,
    WarlockLevel2Spells,
    WarlockLevel3Spells,
    WarlockLevel4Spells,
    WarlockLevel5Spells,
    WarlockLevel6Spells,
    WarlockLevel7Spells,
)
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import WarlockSkillsStatBlock


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=WarlockHexbladeCustomStarterClassArgs(
            skills=WarlockSkillsStatBlock(
                proficiencies={
                    Skill.ARCANA: False,
                    Skill.DECEPTION: False,
                    Skill.HISTORY: False,
                    Skill.INTIMIDATION: True,
                    Skill.INVESTIGATION: False,
                    Skill.NATURE: False,
                    Skill.RELIGION: True,
                }
            ),
        ),
        base_class_level=14,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilitiesStatBlock(
            strength=10,
            dexterity=12,
            constitution=14,
            intelligence=8,
            wisdom=13,
            charisma=15,
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.CONSTITUTION, 1),
                (Ability.CHARISMA, 2),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.ATHLETICS,
                Skill.PERSUASION,
            ]
        ),
        add_default_equipment=True,
        origin_feat=OriginFeats.Tough(),
        armor=[],
        weapons=[],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: WarlockLevel1(
                    cantrip_1=WarlockLevel0Spells.ELDRITCH_BLAST,
                    cantrip_2=WarlockLevel0Spells.CHILL_TOUCH,
                    spell_1=WarlockLevel1Spells.HEX,
                    spell_2=WarlockLevel1Spells.ARMOR_OF_AGATHYS,
                    eldritch_invocation=InvocationsLevel0.ARMOR_OF_SHADOWS,
                ),
                2: WarlockLevel2(
                    spell=WarlockLevel1Spells.HELLISH_REBUKE,
                    eldritch_invocation_1=InvocationsLevel2.AGONIZING_BLAST,
                    eldritch_invocation_2=InvocationsLevel2.DEVILS_SIGHT,
                ),
                3: WarlockLevel3(
                    spell=WarlockLevel2Spells.MISTY_STEP,
                ),
                4: WarlockLevel4(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[
                            (Ability.CHARISMA, 1),
                            (Ability.CONSTITUTION, 1),
                        ]
                    ),
                    cantrip=WarlockLevel0Spells.MINOR_ILLUSION,
                    spell=WarlockLevel2Spells.INVISIBILITY,
                ),
                5: WarlockLevel5(
                    spell=WarlockLevel3Spells.FEAR,
                    eldritch_invocation_1=InvocationsLevel5.ASCENDANT_STEP,
                    eldritch_invocation_2=InvocationsLevel5.GAZE_OF_TWO_MINDS,
                ),
                6: WarlockLevel6(
                    spell=WarlockLevel3Spells.COUNTERSPELL,
                ),
                7: WarlockLevel7(
                    spell=WarlockLevel4Spells.BANISHMENT,
                    eldritch_invocation=InvocationsLevel7.WHISPERS_OF_THE_GRAVE,
                ),
                8: WarlockLevel8(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[
                            (Ability.CHARISMA, 1),
                            (Ability.STRENGTH, 1),
                        ]
                    ),
                    spell=WarlockLevel4Spells.DIMENSION_DOOR,
                ),
                9: WarlockLevel9(
                    spell=WarlockLevel5Spells.HOLD_MONSTER,
                    eldritch_invocation=InvocationsLevel9.LIFEDRINKER,
                ),
                10: WarlockLevel10(
                    cantrip=WarlockLevel0Spells.TRUE_STRIKE,
                ),
                11: WarlockLevel11(
                    spell=WarlockLevel6Spells.EYEBITE,
                ),
                12: WarlockLevel12(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[
                            (Ability.CHARISMA, 1),
                            (Ability.CONSTITUTION, 1),
                        ]
                    ),
                    eldritch_invocation=InvocationsLevel12.DEVOURING_BLADE,
                ),
                13: WarlockLevel13(
                    spell=WarlockLevel7Spells.FINGER_OF_DEATH,
                ),
                14: WarlockLevel14(),
            },
            subclass_features_by_level={
                3: HexbladeWarlockLevel3(),
                6: HexbladeWarlockLevel6(),
                10: HexbladeWarlockLevel10(),
                14: HexbladeWarlockLevel14(),
            },
        ),
        replace_spells={},
    )


class ExampleWarlockHexblade2014CharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Example Warlock Hexblade",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Human.HumanSpeciesBuilder(
                skill_proficiency=Skill.INTIMIDATION,
                origin_feat=OriginFeats.Alert(),
            ),
        )
