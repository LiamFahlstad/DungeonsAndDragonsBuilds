"""Example build: Warlock The Great Old One Patron (2014 rules). Demonstrates the subclass up through level 14."""

from Builds.CharacterBuilder import CharacterBuilder
from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterContent.Classes.BaseClasses.WarlockBase import (
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
from CharacterContent.Classes.SubClasses2014.WarlockGreatOldOne import (
    WarlockGreatOldOneLevel3,
    WarlockGreatOldOneLevel6,
    WarlockGreatOldOneLevel10,
    WarlockGreatOldOneLevel14,
    WarlockGreatOldOneCustomStarterClassArgs,
)
from Core.Definitions import Ability, Skill
from CharacterContent.Features.CharacterFeats import Backgrounds, GeneralFeats, OriginFeats
from CharacterContent.Invocations.Definitions import (
    InvocationsLevel0,
    InvocationsLevel2,
    InvocationsLevel5,
    InvocationsLevel7,
    InvocationsLevel9,
    InvocationsLevel12,
)
from CharacterContent.Species import Human
from CharacterContent.Spells.SpellLists import (
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
        non_generic_arguments=WarlockGreatOldOneCustomStarterClassArgs(
            skills=WarlockSkillsStatBlock(
                proficiencies={
                    Skill.ARCANA: True,
                    Skill.DECEPTION: False,
                    Skill.HISTORY: True,
                    Skill.INTIMIDATION: False,
                    Skill.INVESTIGATION: False,
                    Skill.NATURE: False,
                    Skill.RELIGION: False,
                }
            ),
        ),
        base_class_level=14,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilitiesStatBlock(
            strength=8,
            dexterity=13,
            constitution=14,
            intelligence=12,
            wisdom=10,
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
                Skill.INSIGHT,
                Skill.PERCEPTION,
            ]
        ),
        add_default_equipment=True,
        origin_feat=OriginFeats.Lucky(),
        armor=[],
        weapons=[],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: WarlockLevel1(
                    cantrip_1=WarlockLevel0Spells.ELDRITCH_BLAST,
                    cantrip_2=WarlockLevel0Spells.MIND_SLIVER,
                    spell_1=WarlockLevel1Spells.CHARM_PERSON,
                    spell_2=WarlockLevel1Spells.WITCH_BOLT,
                    eldritch_invocation=InvocationsLevel0.ELDRITCH_MIND,
                ),
                2: WarlockLevel2(
                    spell=WarlockLevel1Spells.UNSEEN_SERVANT,
                    eldritch_invocation_1=InvocationsLevel2.AGONIZING_BLAST,
                    eldritch_invocation_2=InvocationsLevel2.DEVILS_SIGHT,
                ),
                3: WarlockLevel3(
                    spell=WarlockLevel2Spells.MIND_SPIKE,
                ),
                4: WarlockLevel4(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[
                            (Ability.CHARISMA, 2),
                        ]),
                    cantrip=WarlockLevel0Spells.MINOR_ILLUSION,
                    spell=WarlockLevel2Spells.CROWN_OF_MADNESS,
                ),
                5: WarlockLevel5(
                    spell=WarlockLevel3Spells.HUNGER_OF_HADAR,
                    eldritch_invocation_1=InvocationsLevel5.ASCENDANT_STEP,
                    eldritch_invocation_2=InvocationsLevel5.GAZE_OF_TWO_MINDS,
                ),
                6: WarlockLevel6(
                    spell=WarlockLevel3Spells.HYPNOTIC_PATTERN,
                ),
                7: WarlockLevel7(
                    spell=WarlockLevel4Spells.SICKENING_RADIANCE,
                    eldritch_invocation=InvocationsLevel7.WHISPERS_OF_THE_GRAVE,
                ),
                8: WarlockLevel8(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[
                            (Ability.CHARISMA, 2),
                        ]),
                    spell=WarlockLevel4Spells.RAULOTHIMS_PSYCHIC_LANCE,
                ),
                9: WarlockLevel9(
                    spell=WarlockLevel5Spells.SYNAPTIC_STATIC,
                    eldritch_invocation=InvocationsLevel9.LIFEDRINKER,
                ),
                10: WarlockLevel10(
                    cantrip=WarlockLevel0Spells.TRUE_STRIKE,
                ),
                11: WarlockLevel11(
                    spell=WarlockLevel6Spells.MENTAL_PRISON,
                ),
                12: WarlockLevel12(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[
                            (Ability.CHARISMA, 2),
                        ]),
                    eldritch_invocation=InvocationsLevel12.DEVOURING_BLADE,
                ),
                13: WarlockLevel13(
                    spell=WarlockLevel7Spells.CROWN_OF_STARS,
                ),
                14: WarlockLevel14(),
            },
            subclass_features_by_level={
                3: WarlockGreatOldOneLevel3(),
                6: WarlockGreatOldOneLevel6(),
                10: WarlockGreatOldOneLevel10(),
                14: WarlockGreatOldOneLevel14(),
            },
        ),
        replace_spells={},
    )


class ExampleWarlockGreatOldOne2014CharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Example Warlock The Great Old One",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Human.HumanSpeciesBuilder(
                skill_proficiency=Skill.RELIGION,
                origin_feat=OriginFeats.Alert(),
            ),
        )
