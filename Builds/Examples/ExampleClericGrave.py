"""Example build: Cleric Grave Domain. Adapted from an optimized reference build to demonstrate this subclass."""

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
    ClericLevel18,
    ClericLevel19,
    ClericLevel20,
)
from CharacterConfigs.SubClasses2024.ClericGrave import (
    ClericGraveCustomStarterClassArgs,
    ClericGraveLevel3,
    ClericGraveLevel5,
    ClericGraveLevel6,
    ClericGraveLevel7,
    ClericGraveLevel9,
    ClericGraveLevel17,
)
from Core.Definitions import Ability, Skill
from Features.CharacterFeats import Backgrounds, EpicBoon, GeneralFeats, OriginFeats
from SpeciesConfigs import Elf
from Spells.SpellLists import (
    ClericLevel0Spells,
    ClericLevel1Spells,
    ClericLevel2Spells,
    ClericLevel3Spells,
    ClericLevel4Spells,
    ClericLevel5Spells,
    ClericLevel6Spells,
    ClericLevel7Spells,
    ClericLevel9Spells,
)
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import ClericSkillsStatBlock


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=ClericGraveCustomStarterClassArgs(
            skills=ClericSkillsStatBlock(
                proficiencies={
                    Skill.HISTORY: False,
                    Skill.INSIGHT: False,
                    Skill.MEDICINE: True,
                    Skill.PERSUASION: False,
                    Skill.RELIGION: True,
                }
            ),
        ),
        base_class_level=3,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilitiesStatBlock(
            strength=8,
            dexterity=13,
            constitution=14,
            intelligence=10,
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
                Skill.ARCANA,
                Skill.PERCEPTION,
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
                    cantrip_2=ClericLevel0Spells.TOLL_THE_DEAD,
                    cantrip_3=ClericLevel0Spells.SACRED_FLAME,
                    spell_1=ClericLevel1Spells.CURE_WOUNDS,
                    spell_2=ClericLevel1Spells.BANE,
                    spell_3=ClericLevel1Spells.INFLICT_WOUNDS,
                    spell_4=ClericLevel1Spells.GUIDING_BOLT,
                ),
                2: ClericLevel2(
                    spell=ClericLevel1Spells.HEALING_WORD,
                ),
                3: ClericLevel3(
                    spell=ClericLevel2Spells.SPIRITUAL_WEAPON,
                ),
                4: ClericLevel4(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.WISDOM, 1),
                            (Ability.CONSTITUTION, 1),
                        ]
                    ),
                    cantrip=ClericLevel0Spells.WORD_OF_RADIANCE,
                    spell=ClericLevel2Spells.AID,
                ),
                5: ClericLevel5(
                    spell_1=ClericLevel3Spells.SPIRIT_GUARDIANS,
                    spell_2=ClericLevel3Spells.ANIMATE_DEAD,
                ),
                6: ClericLevel6(
                    spell=ClericLevel3Spells.BESTOW_CURSE,
                ),
                7: ClericLevel7(
                    spell=ClericLevel2Spells.LESSER_RESTORATION,
                ),
                8: ClericLevel8(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.CONSTITUTION, 2),
                        ]
                    ),
                    spell=ClericLevel4Spells.GUARDIAN_OF_FAITH,
                ),
                9: ClericLevel9(
                    spell_1=ClericLevel5Spells.MASS_CURE_WOUNDS,
                    spell_2=ClericLevel5Spells.GEAS,
                ),
                10: ClericLevel10(
                    cantrip=ClericLevel0Spells.MENDING,
                    spell=ClericLevel5Spells.INSECT_PLAGUE,
                ),
                11: ClericLevel11(
                    spell=ClericLevel6Spells.HARM,
                ),
                12: ClericLevel12(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.WISDOM, 1),
                            (Ability.CONSTITUTION, 1),
                        ]
                    ),
                ),
                13: ClericLevel13(
                    spell=ClericLevel7Spells.CONJURE_CELESTIAL,
                ),
                14: ClericLevel14(),
                15: ClericLevel15(
                    spell=ClericLevel7Spells.REGENERATE,
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
                19: ClericLevel19(
                    epic_boon=EpicBoon.DummyEpicBoon(),
                    spell=ClericLevel9Spells.MASS_HEAL,
                ),
                18: ClericLevel18(
                    spell=ClericLevel9Spells.POWER_WORD_HEAL,
                ),
                20: ClericLevel20(
                    spell=ClericLevel9Spells.ASTRAL_PROJECTION,
                ),
            },
            subclass_features_by_level={
                3: ClericGraveLevel3(),
                5: ClericGraveLevel5(),
                6: ClericGraveLevel6(),
                7: ClericGraveLevel7(),
                9: ClericGraveLevel9(),
                17: ClericGraveLevel17(),
            },
        ),
        replace_spells={},
    )


class ExampleClericGraveCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Example Grave Cleric",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Elf.ElfSpeciesBuilder(
                elven_lineage=Elf.ElvenLineage.HIGH_ELF,
                skill_proficiency=Skill.INSIGHT,
            ),
        )
