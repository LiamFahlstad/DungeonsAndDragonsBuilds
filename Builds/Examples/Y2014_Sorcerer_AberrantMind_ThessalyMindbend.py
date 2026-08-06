"""Example build: Sorcerer Aberrant Mind (2014 rules). Demonstrates a psionic sorcerer with telepathy and aberrant transformations."""

from Builds.CharacterBuilder import CharacterBuilder
from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterContent.Classes.BaseClasses.SorcererBase import (
    SorcererLevel1,
    SorcererLevel2,
    SorcererLevel3,
    SorcererLevel4,
    SorcererLevel5,
    SorcererLevel6,
    SorcererLevel7,
    SorcererLevel8,
    SorcererLevel9,
    SorcererLevel10,
    SorcererLevel11,
    SorcererLevel12,
    SorcererLevel13,
    SorcererLevel14,
    SorcererLevel15,
    SorcererLevel16,
    SorcererLevel17,
    SorcererLevel18,
)
from CharacterContent.Classes.SubClasses2014.SorcererAberrantMind import (
    SorcererAberrantMindCustomStarterClassArgs,
    SorcererAberrantMindLevel3,
    SorcererAberrantMindLevel5,
    SorcererAberrantMindLevel6,
    SorcererAberrantMindLevel7,
    SorcererAberrantMindLevel9,
    SorcererAberrantMindLevel14,
    SorcererAberrantMindLevel18,
)
from Core.Definitions import Ability, Skill
from CharacterContent.Features.CharacterFeats import Backgrounds, GeneralFeats, OriginFeats
from CharacterContent.Items import Weapons
from CharacterContent.Species import Human
from CharacterContent.Spells import SpellLists as SpellDefinitions
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import SorcererSkillsStatBlock


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=SorcererAberrantMindCustomStarterClassArgs(
            skills=SorcererSkillsStatBlock(
                proficiencies={
                    Skill.ARCANA: True,
                    Skill.INSIGHT: True,
                    Skill.DECEPTION: False,
                    Skill.INTIMIDATION: False,
                    Skill.PERSUASION: False,
                    Skill.RELIGION: False,
                }
            ),
        ),
        base_class_level=18,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilitiesStatBlock(
            strength=8,
            dexterity=13,
            constitution=14,
            intelligence=10,
            wisdom=12,
            charisma=15,
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.CHARISMA, 2),
                (Ability.INTELLIGENCE, 1),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.INSIGHT,
                Skill.PERSUASION,
            ]
        ),
        add_default_equipment=False,
        origin_feat=OriginFeats.Lucky(),
        weapons=[
            Weapons.Dagger(),
        ],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: SorcererLevel1(
                    cantrip_1=SpellDefinitions.SorcererLevel0Spells.FIRE_BOLT,
                    cantrip_2=SpellDefinitions.SorcererLevel0Spells.LIGHT,
                    cantrip_3=SpellDefinitions.SorcererLevel0Spells.PRESTIDIGITATION,
                    cantrip_4=SpellDefinitions.SorcererLevel0Spells.MAGE_HAND,
                    spell_1=SpellDefinitions.SorcererLevel1Spells.SHIELD,
                    spell_2=SpellDefinitions.SorcererLevel1Spells.CHARM_PERSON,
                ),
                2: SorcererLevel2(
                    spell_1=SpellDefinitions.SorcererLevel1Spells.FOG_CLOUD,
                    spell_2=SpellDefinitions.SorcererLevel1Spells.EXPEDITIOUS_RETREAT,
                ),
                3: SorcererLevel3(
                    spell_1=SpellDefinitions.SorcererLevel2Spells.BLUR,
                    spell_2=SpellDefinitions.SorcererLevel2Spells.SUGGESTION,
                ),
                4: SorcererLevel4(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [(Ability.CHARISMA, 2)]),
                    cantrip=SpellDefinitions.SorcererLevel0Spells.SHOCKING_GRASP,
                    spell=SpellDefinitions.SorcererLevel2Spells.MIRROR_IMAGE,
                ),
                5: SorcererLevel5(
                    spell_1=SpellDefinitions.SorcererLevel3Spells.COUNTERSPELL,
                    spell_2=SpellDefinitions.SorcererLevel3Spells.HYPNOTIC_PATTERN,
                ),
                6: SorcererLevel6(
                    spell=SpellDefinitions.SorcererLevel3Spells.FEAR,
                ),
                7: SorcererLevel7(
                    spell=SpellDefinitions.SorcererLevel4Spells.DOMINATE_BEAST,
                ),
                8: SorcererLevel8(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [(Ability.CHARISMA, 2)]),
                    spell=SpellDefinitions.SorcererLevel4Spells.DIMENSION_DOOR,
                ),
                9: SorcererLevel9(
                    spell_1=SpellDefinitions.SorcererLevel5Spells.DOMINATE_PERSON,
                    spell_2=SpellDefinitions.SorcererLevel5Spells.CONTROL_WINDS,
                ),
                10: SorcererLevel10(
                    cantrip=SpellDefinitions.SorcererLevel0Spells.THUNDERCLAP,
                    spell=SpellDefinitions.SorcererLevel5Spells.CLOUDKILL,
                ),
                11: SorcererLevel11(
                    spell=SpellDefinitions.SorcererLevel5Spells.HOLD_MONSTER,
                ),
                12: SorcererLevel12(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [(Ability.WISDOM, 2)]),
                ),
                13: SorcererLevel13(
                    spell=SpellDefinitions.SorcererLevel5Spells.ANIMATE_OBJECTS,
                ),
                14: SorcererLevel14(),
                15: SorcererLevel15(
                    spell=SpellDefinitions.SorcererLevel5Spells.SYNAPTIC_STATIC,
                ),
                16: SorcererLevel16(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [(Ability.CONSTITUTION, 2)]),
                ),
                17: SorcererLevel17(
                    spell=SpellDefinitions.SorcererLevel5Spells.SUMMON_DRACONIC_SPIRIT,
                ),
                18: SorcererLevel18(
                    spell=SpellDefinitions.SorcererLevel5Spells.TELEPORTATION_CIRCLE,
                ),
            },
            subclass_features_by_level={
                3: SorcererAberrantMindLevel3(),
                5: SorcererAberrantMindLevel5(),
                6: SorcererAberrantMindLevel6(),
                7: SorcererAberrantMindLevel7(),
                9: SorcererAberrantMindLevel9(),
                14: SorcererAberrantMindLevel14(),
                18: SorcererAberrantMindLevel18(),
            },
        ),
    )


class Y2014SorcererAberrantMindThessalyMindbendCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Thessaly Mindbend",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Human.HumanSpeciesBuilder(
                skill_proficiency=Skill.ARCANA,
                origin_feat=OriginFeats.Lucky(),
            ),
        )
