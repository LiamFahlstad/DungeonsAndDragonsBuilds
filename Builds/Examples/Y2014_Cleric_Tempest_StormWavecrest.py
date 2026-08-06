"""Example build: Cleric Tempest Domain (2014 rules). Demonstrates the subclass up through level 17."""

from Builds.CharacterBuilder import CharacterBuilder
from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterContent.Classes.BaseClasses.ClericBase import (
    ClericLevel1,
    ClericLevel2,
    ClericLevel3,
    ClericLevel4,
    ClericLevel5,
    ClericLevel6,
    ClericLevel7,
    ClericLevel8,
    ClericLevel9,
    ClericLevel10,
    ClericLevel11,
    ClericLevel12,
    ClericLevel13,
    ClericLevel14,
    ClericLevel15,
    ClericLevel16,
    ClericLevel17,
)
from CharacterContent.Classes.SubClasses2014.ClericTempest import (
    ClericTempestCustomStarterClassArgs,
    ClericTempestLevel3,
    ClericTempestLevel6,
    ClericTempestLevel8,
    ClericTempestLevel17,
)
from Core.Definitions import Ability, Skill
from CharacterContent.Features.CharacterFeats import Backgrounds, GeneralFeats, OriginFeats
from CharacterContent.Species import Human
from CharacterContent.Spells.SpellLists import (
    ClericLevel0Spells,
    ClericLevel1Spells,
    ClericLevel2Spells,
    ClericLevel3Spells,
    ClericLevel4Spells,
    ClericLevel5Spells,
    ClericLevel6Spells,
    ClericLevel7Spells,
    ClericLevel8Spells,
    ClericLevel9Spells,
)
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import ClericSkillsStatBlock


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=ClericTempestCustomStarterClassArgs(
            skills=ClericSkillsStatBlock(
                proficiencies={
                    Skill.INSIGHT: True,
                    Skill.MEDICINE: False,
                    Skill.PERSUASION: True,
                    Skill.RELIGION: False,
                    Skill.HISTORY: False,
                }
            ),
        ),
        base_class_level=17,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilitiesStatBlock(
            strength=14,
            dexterity=10,
            constitution=13,
            intelligence=8,
            wisdom=15,
            charisma=12,
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.WISDOM, 2),
                (Ability.STRENGTH, 1),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.ATHLETICS,
                Skill.INTIMIDATION,
            ]
        ),
        add_default_equipment=True,
        origin_feat=OriginFeats.Tough(),
        armor=[],
        weapons=[],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: ClericLevel1(
                    cantrip_1=ClericLevel0Spells.GUIDANCE,
                    cantrip_2=ClericLevel0Spells.SACRED_FLAME,
                    cantrip_3=ClericLevel0Spells.SPARE_THE_DYING,
                    spell_1=ClericLevel1Spells.CURE_WOUNDS,
                    spell_2=ClericLevel1Spells.BLESS,
                    spell_3=ClericLevel1Spells.HEALING_WORD,
                    spell_4=ClericLevel1Spells.CREATE_OR_DESTROY_WATER,
                ),
                2: ClericLevel2(
                    spell=ClericLevel1Spells.DETECT_MAGIC,
                ),
                3: ClericLevel3(
                    spell=ClericLevel2Spells.AID,
                ),
                4: ClericLevel4(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.WISDOM, 2),
                        ]),
                    cantrip=ClericLevel0Spells.RESISTANCE,
                    spell=ClericLevel2Spells.SILENCE,
                ),
                5: ClericLevel5(
                    spell_1=ClericLevel3Spells.SPIRIT_GUARDIANS,
                    spell_2=ClericLevel3Spells.DISPEL_MAGIC,
                ),
                6: ClericLevel6(
                    spell=ClericLevel3Spells.WATER_WALK,
                ),
                7: ClericLevel7(
                    spell=ClericLevel4Spells.CONTROL_WATER,
                ),
                8: ClericLevel8(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.WISDOM, 2),
                        ]),
                    spell=ClericLevel4Spells.FREEDOM_OF_MOVEMENT,
                ),
                9: ClericLevel9(
                    spell_1=ClericLevel5Spells.INSECT_PLAGUE,
                    spell_2=ClericLevel5Spells.GREATER_RESTORATION,
                ),
                10: ClericLevel10(
                    cantrip=ClericLevel0Spells.MENDING,
                    spell=ClericLevel5Spells.COMMUNE,
                ),
                11: ClericLevel11(
                    spell=ClericLevel6Spells.HEAL,
                ),
                12: ClericLevel12(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.CONSTITUTION, 2),
                        ]),
                ),
                13: ClericLevel13(
                    spell=ClericLevel7Spells.FIRE_STORM,
                ),
                14: ClericLevel14(),
                15: ClericLevel15(
                    spell=ClericLevel8Spells.CONTROL_WEATHER,
                ),
                16: ClericLevel16(
                    general_feat=GeneralFeats.WarCaster(
                        character_level=16,
                        ability=Ability.WISDOM,
                    ),
                ),
                17: ClericLevel17(
                    spell=ClericLevel9Spells.MASS_HEAL,
                ),
            },
            subclass_features_by_level={
                3: ClericTempestLevel3(),
                6: ClericTempestLevel6(),
                8: ClericTempestLevel8(),
                17: ClericTempestLevel17(),
            },
        ),
        replace_spells={},
    )


class Y2014ClericTempestStormWavecrestCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Storm Wavecrest",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Human.HumanSpeciesBuilder(
                skill_proficiency=Skill.PERCEPTION,
                origin_feat=OriginFeats.Tough(),
            ),
        )
