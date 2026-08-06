"""Example build: Sorcerer Aberrant Mind. Demonstrates the Aberrant Sorcery subclass up through level 18."""

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
from CharacterContent.Classes.SubClasses2024.SorcererAberrant import (
    SorcererAberrantCustomStarterClassArgs,
    SorcererAberrantLevel3,
    SorcererAberrantLevel5,
    SorcererAberrantLevel6,
    SorcererAberrantLevel7,
    SorcererAberrantLevel9,
    SorcererAberrantLevel14,
    SorcererAberrantLevel18,
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
        non_generic_arguments=SorcererAberrantCustomStarterClassArgs(
            skills=SorcererSkillsStatBlock(
                proficiencies={
                    Skill.ARCANA: True,
                    Skill.DECEPTION: False,
                    Skill.INSIGHT: True,
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
            dexterity=14,
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
                Skill.ARCANA,
                Skill.RELIGION,
            ]
        ),
        add_default_equipment=False,
        origin_feat=OriginFeats.Lucky(),
        weapons=[
            Weapons.Dagger(),
            Weapons.Quarterstaff(),
        ],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: SorcererLevel1(
                    cantrip_1=SpellDefinitions.SorcererLevel0Spells.FIRE_BOLT,
                    cantrip_2=SpellDefinitions.SorcererLevel0Spells.PRESTIDIGITATION,
                    cantrip_3=SpellDefinitions.SorcererLevel0Spells.MAGE_HAND,
                    cantrip_4=SpellDefinitions.SorcererLevel0Spells.MESSAGE,
                    spell_1=SpellDefinitions.SorcererLevel1Spells.SHIELD,
                    spell_2=SpellDefinitions.SorcererLevel1Spells.CHROMATIC_ORB,
                ),
                2: SorcererLevel2(
                    spell_1=SpellDefinitions.SorcererLevel1Spells.DETECT_MAGIC,
                    spell_2=SpellDefinitions.SorcererLevel1Spells.MAGIC_MISSILE,
                ),
                3: SorcererLevel3(
                    spell_1=SpellDefinitions.SorcererLevel2Spells.MIRROR_IMAGE,
                    spell_2=SpellDefinitions.SorcererLevel2Spells.SCORCHING_RAY,
                ),
                4: SorcererLevel4(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [(Ability.CHARISMA, 2)]),
                    cantrip=SpellDefinitions.SorcererLevel0Spells.MINOR_ILLUSION,
                    spell=SpellDefinitions.SorcererLevel2Spells.MISTY_STEP,
                ),
                5: SorcererLevel5(
                    spell_1=SpellDefinitions.SorcererLevel3Spells.COUNTERSPELL,
                    spell_2=SpellDefinitions.SorcererLevel3Spells.HYPNOTIC_PATTERN,
                ),
                6: SorcererLevel6(
                    spell=SpellDefinitions.SorcererLevel3Spells.FEAR,
                ),
                7: SorcererLevel7(
                    spell=SpellDefinitions.SorcererLevel4Spells.DIMENSION_DOOR,
                ),
                8: SorcererLevel8(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [(Ability.CHARISMA, 2)]),
                    spell=SpellDefinitions.SorcererLevel4Spells.GREATER_INVISIBILITY,
                ),
                9: SorcererLevel9(
                    spell_1=SpellDefinitions.SorcererLevel5Spells.DOMINATE_PERSON,
                    spell_2=SpellDefinitions.SorcererLevel5Spells.SYNAPTIC_STATIC,
                ),
                10: SorcererLevel10(
                    cantrip=SpellDefinitions.SorcererLevel0Spells.TRUE_STRIKE,
                    spell=SpellDefinitions.SorcererLevel5Spells.HOLD_MONSTER,
                ),
                11: SorcererLevel11(
                    spell=SpellDefinitions.SorcererLevel6Spells.DISINTEGRATE,
                ),
                12: SorcererLevel12(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [(Ability.CHARISMA, 2)]),
                ),
                13: SorcererLevel13(
                    spell=SpellDefinitions.SorcererLevel7Spells.PLANE_SHIFT,
                ),
                14: SorcererLevel14(),
                15: SorcererLevel15(
                    spell=SpellDefinitions.SorcererLevel8Spells.DOMINATE_MONSTER,
                ),
                16: SorcererLevel16(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [(Ability.CHARISMA, 2)]),
                ),
                17: SorcererLevel17(
                    spell=SpellDefinitions.SorcererLevel9Spells.PSYCHIC_SCREAM,
                ),
                18: SorcererLevel18(
                    spell=SpellDefinitions.SorcererLevel9Spells.TIME_STOP,
                ),
            },
            subclass_features_by_level={
                3: SorcererAberrantLevel3(),
                5: SorcererAberrantLevel5(),
                6: SorcererAberrantLevel6(),
                7: SorcererAberrantLevel7(),
                9: SorcererAberrantLevel9(),
                14: SorcererAberrantLevel14(),
                18: SorcererAberrantLevel18(),
            },
        ),
    )


class Y2024SorcererAberrantMindNyssaVoidwhisperCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Nyssa Voidwhisper",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Human.HumanSpeciesBuilder(
                skill_proficiency=Skill.PERCEPTION,
                origin_feat=OriginFeats.Skilled(
                    skills=[
                        Skill.HISTORY,
                        Skill.INVESTIGATION,
                        Skill.NATURE,
                    ]
                ),
            ),
        )
