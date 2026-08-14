"""Example build: Bard College of Whispers (2014 rules). Demonstrates the subclass up through level 14."""

import Core.Definitions as Definitions
from Builds.CharacterBuilder import CharacterBuilder
from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterContent.Classes.BaseClasses.BardBase import (
    BardLevel1,
    BardLevel2,
    BardLevel3,
    BardLevel4,
    BardLevel5,
    BardLevel6,
    BardLevel7,
    BardLevel8,
    BardLevel9,
    BardLevel10,
    BardLevel11,
    BardLevel12,
    BardLevel13,
    BardLevel14,
)
from CharacterContent.Classes.SubClasses2014.BardWhispers import (
    BardWhispersCustomStarterClassArgs,
    BardWhispersLevel3,
    BardWhispersLevel6,
    BardWhispersLevel14,
)
from Core.Definitions import Ability, Skill
from CharacterContent.Features.CharacterFeats import Backgrounds, GeneralFeats, OriginFeats
from CharacterContent.Features.CharacterFeats import OriginFeats as SpeciesOriginFeats
from CharacterContent.Species import Human
from CharacterContent.Spells.SpellLists import (
    BardLevel0Spells,
    BardLevel1Spells,
    BardLevel2Spells,
    BardLevel3Spells,
    BardLevel4Spells,
)
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from CharacterContent.ToolProficiencies.Proficiencies import Dulcimer, Lyre, Viol
from StatBlocks.SkillsStatBlock import BardSkillsStatBlock


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=BardWhispersCustomStarterClassArgs(
            skills=BardSkillsStatBlock(
                proficiencies={
                    Skill.PERFORMANCE: True,
                    Skill.PERSUASION: True,
                    Skill.DECEPTION: True,
                }
            ),
        ),
        base_class_level=14,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilitiesStatBlock(
            strength=8,
            dexterity=14,
            constitution=13,
            intelligence=10,
            wisdom=12,
            charisma=15,
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.CHARISMA, 2),
                (Ability.DEXTERITY, 1),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.DECEPTION,
                Skill.INSIGHT,
            ]
        ),
        add_default_equipment=True,
        origin_feat=OriginFeats.Musician(),
        armor=[],
        weapons=[],
        tool_proficiencies=[
            Lyre(),
            Viol(),
            Dulcimer(),
        ],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: BardLevel1(
                    cantrip_1=BardLevel0Spells.VICIOUS_MOCKERY,
                    cantrip_2=BardLevel0Spells.MINOR_ILLUSION,
                    spell_1=BardLevel1Spells.CHARM_PERSON,
                    spell_2=BardLevel1Spells.DISGUISE_SELF,
                    spell_3=BardLevel1Spells.FAERIE_FIRE,
                    spell_4=BardLevel1Spells.HEALING_WORD,
                ),
                2: BardLevel2(
                    spell=BardLevel1Spells.DISSONANT_WHISPERS,
                    skill_expertise_1=Skill.DECEPTION,
                    skill_expertise_2=Skill.PERSUASION,
                ),
                3: BardLevel3(
                    spell=BardLevel2Spells.SUGGESTION,
                ),
                4: BardLevel4(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[(Ability.CHARISMA, 2)]),
                    cantrip=BardLevel0Spells.MAGE_HAND,
                    spell=BardLevel2Spells.INVISIBILITY,
                ),
                5: BardLevel5(
                    spell_1=BardLevel3Spells.BESTOW_CURSE,
                    spell_2=BardLevel3Spells.FEAR,
                ),
                6: BardLevel6(
                    spell=BardLevel3Spells.HYPNOTIC_PATTERN,
                ),
                7: BardLevel7(
                    spell=BardLevel2Spells.CALM_EMOTIONS,
                ),
                8: BardLevel8(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[(Ability.CONSTITUTION, 2)]),
                    spell=BardLevel4Spells.CHARM_MONSTER,
                ),
                9: BardLevel9(
                    spell_1=BardLevel4Spells.CONFUSION,
                    spell_2=BardLevel4Spells.COMPULSION,
                    skill_expertise_1=Skill.INSIGHT,
                    skill_expertise_2=Skill.PERFORMANCE,
                ),
                10: BardLevel10(
                    cantrip=BardLevel0Spells.PRESTIDIGITATION,
                    spell=BardLevel4Spells.GREATER_INVISIBILITY,
                ),
                11: BardLevel11(
                    spell=BardLevel4Spells.POLYMORPH,
                ),
                12: BardLevel12(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[(Ability.CHARISMA, 1), (Ability.WISDOM, 1)]),
                ),
                13: BardLevel13(
                    spell=BardLevel4Spells.DIMENSION_DOOR,
                ),
                14: BardLevel14(),
            },
            subclass_features_by_level={
                3: BardWhispersLevel3(),
                6: BardWhispersLevel6(),
                14: BardWhispersLevel14(),
            },
        ),
    )


class Y2014BardWhispersNyraHollowechoCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Nyra Hollowecho",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Human.HumanSpeciesBuilder(
                origin_feat=SpeciesOriginFeats.Tough(),
                skill_proficiency=Skill.INSIGHT,
            ),
        )
