"""Example build: Cleric Death Domain (2014 rules). Demonstrates the subclass up through level 17."""

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
from CharacterConfigs.SubClasses2014.ClericDeath import (
    ClericDeathCustomStarterClassArgs,
    ClericDeathLevel3,
    ClericDeathLevel6,
    ClericDeathLevel8,
    ClericDeathLevel17,
)
from Definitions import Ability, Skill
from Features.CharacterFeats import Backgrounds, GeneralFeats, OriginFeats
from SpeciesConfigs import Human
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
        non_generic_arguments=ClericDeathCustomStarterClassArgs(
            skills=ClericSkillsStatBlock(
                proficiencies={
                    Skill.INSIGHT: True,
                    Skill.MEDICINE: False,
                    Skill.PERSUASION: False,
                    Skill.RELIGION: True,
                    Skill.HISTORY: False,
                }
            ),
        ),
        base_class_level=17,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilitiesStatBlock(
            strength=13,
            dexterity=10,
            constitution=14,
            intelligence=8,
            wisdom=15,
            charisma=12,
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.WISDOM, 2),
                (Ability.CONSTITUTION, 1),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.HISTORY,
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
                    cantrip_3=ClericLevel0Spells.TOLL_THE_DEAD,
                    spell_1=ClericLevel1Spells.CURE_WOUNDS,
                    spell_2=ClericLevel1Spells.BLESS,
                    spell_3=ClericLevel1Spells.INFLICT_WOUNDS,
                    spell_4=ClericLevel1Spells.SHIELD_OF_FAITH,
                ),
                2: ClericLevel2(
                    spell=ClericLevel1Spells.DETECT_MAGIC,
                ),
                3: ClericLevel3(
                    spell=ClericLevel2Spells.BLINDNESS_DEAFNESS,
                ),
                4: ClericLevel4(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.WISDOM, 2),
                        ]
                    ),
                    cantrip=ClericLevel0Spells.SPARE_THE_DYING,
                    spell=ClericLevel2Spells.SILENCE,
                ),
                5: ClericLevel5(
                    spell_1=ClericLevel3Spells.ANIMATE_DEAD,
                    spell_2=ClericLevel3Spells.BESTOW_CURSE,
                ),
                6: ClericLevel6(
                    spell=ClericLevel3Spells.SPIRIT_GUARDIANS,
                ),
                7: ClericLevel7(
                    spell=ClericLevel4Spells.BANISHMENT,
                ),
                8: ClericLevel8(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.WISDOM, 2),
                        ]
                    ),
                    spell=ClericLevel4Spells.DEATH_WARD,
                ),
                9: ClericLevel9(
                    spell_1=ClericLevel5Spells.CONTAGION,
                    spell_2=ClericLevel5Spells.MASS_CURE_WOUNDS,
                ),
                10: ClericLevel10(
                    cantrip=ClericLevel0Spells.RESISTANCE,
                    spell=ClericLevel5Spells.RAISE_DEAD,
                ),
                11: ClericLevel11(
                    spell=ClericLevel6Spells.HARM,
                ),
                12: ClericLevel12(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.CONSTITUTION, 2),
                        ]
                    ),
                ),
                13: ClericLevel13(
                    spell=ClericLevel7Spells.RESURRECTION,
                ),
                14: ClericLevel14(),
                15: ClericLevel15(
                    spell=ClericLevel8Spells.HOLY_AURA,
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
                3: ClericDeathLevel3(),
                6: ClericDeathLevel6(),
                8: ClericDeathLevel8(),
                17: ClericDeathLevel17(),
            },
        ),
        replace_spells={},
    )


class ExampleClericDeath2014CharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Example Death Cleric",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Human.HumanSpeciesBuilder(
                skill_proficiency=Skill.PERCEPTION,
                origin_feat=OriginFeats.Tough(),
            ),
        )
