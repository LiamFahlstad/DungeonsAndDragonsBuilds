"""Example build: Cleric Forge Domain (2014 rules). Demonstrates the subclass up through level 17."""

from Builds.CharacterBuilder import CharacterBuilder
from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterConfigs.BaseClasses.ClericBase import (
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
from CharacterConfigs.SubClasses2014.ClericForge import (
    ClericForgeCustomStarterClassArgs,
    ClericForgeLevel3,
    ClericForgeLevel6,
    ClericForgeLevel8,
    ClericForgeLevel17,
)
from Core.Definitions import Ability, Skill
from Features.CharacterFeats import Backgrounds, GeneralFeats, OriginFeats
from SpeciesConfigs import Dwarf
from Spells.SpellLists import (
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
        non_generic_arguments=ClericForgeCustomStarterClassArgs(
            skills=ClericSkillsStatBlock(
                proficiencies={
                    Skill.INSIGHT: True,
                    Skill.MEDICINE: True,
                    Skill.PERSUASION: False,
                    Skill.RELIGION: False,
                    Skill.HISTORY: False,
                }
            ),
        ),
        base_class_level=17,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilitiesStatBlock(
            strength=15,
            dexterity=10,
            constitution=14,
            intelligence=8,
            wisdom=13,
            charisma=12,
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.STRENGTH, 2),
                (Ability.CONSTITUTION, 1),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.HISTORY,
                Skill.MEDICINE,
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
                    cantrip_3=ClericLevel0Spells.MENDING,
                    spell_1=ClericLevel1Spells.HEALING_WORD,
                    spell_2=ClericLevel1Spells.BLESS,
                    spell_3=ClericLevel1Spells.SHIELD_OF_FAITH,
                    spell_4=ClericLevel1Spells.DETECT_MAGIC,
                ),
                2: ClericLevel2(
                    spell=ClericLevel1Spells.COMMAND,
                ),
                3: ClericLevel3(
                    spell=ClericLevel2Spells.AID,
                ),
                4: ClericLevel4(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.STRENGTH, 1),
                            (Ability.CONSTITUTION, 1),
                        ]
                    ),
                    cantrip=ClericLevel0Spells.TOLL_THE_DEAD,
                    spell=ClericLevel2Spells.ENHANCE_ABILITY,
                ),
                5: ClericLevel5(
                    spell_1=ClericLevel3Spells.AURA_OF_VITALITY,
                    spell_2=ClericLevel3Spells.BEACON_OF_HOPE,
                ),
                6: ClericLevel6(
                    spell=ClericLevel3Spells.DISPEL_MAGIC,
                ),
                7: ClericLevel7(
                    spell=ClericLevel2Spells.LESSER_RESTORATION,
                ),
                8: ClericLevel8(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.WISDOM, 2),
                        ]
                    ),
                    spell=ClericLevel4Spells.FREEDOM_OF_MOVEMENT,
                ),
                9: ClericLevel9(
                    spell_1=ClericLevel5Spells.FLAME_STRIKE,
                    spell_2=ClericLevel5Spells.GREATER_RESTORATION,
                ),
                10: ClericLevel10(
                    cantrip=ClericLevel0Spells.RESISTANCE,
                    spell=ClericLevel5Spells.MASS_CURE_WOUNDS,
                ),
                11: ClericLevel11(
                    spell=ClericLevel6Spells.HEAL,
                ),
                12: ClericLevel12(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.CONSTITUTION, 1),
                            (Ability.WISDOM, 1),
                        ]
                    ),
                ),
                13: ClericLevel13(
                    spell=ClericLevel7Spells.CONJURE_CELESTIAL,
                ),
                14: ClericLevel14(),
                15: ClericLevel15(
                    spell=ClericLevel8Spells.EARTHQUAKE,
                ),
                16: ClericLevel16(
                    general_feat=GeneralFeats.WarCaster(
                        character_level=16,
                        ability=Ability.WISDOM,
                    ),
                ),
                17: ClericLevel17(
                    spell=ClericLevel9Spells.GATE,
                ),
            },
            subclass_features_by_level={
                3: ClericForgeLevel3(),
                6: ClericForgeLevel6(),
                8: ClericForgeLevel8(),
                17: ClericForgeLevel17(),
            },
        ),
        replace_spells={},
    )


class ExampleClericForge2014CharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Example Forge Cleric",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Dwarf.DwarfSpeciesBuilder(),
        )
