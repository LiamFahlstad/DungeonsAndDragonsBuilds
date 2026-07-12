"""Example build: Druid Circle of the Sea. Adapted from an optimized reference build to demonstrate this subclass."""

from Builds.CharacterBuilder import CharacterBuilder
from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterConfigs.BaseClasses.DruidBase import (
    DruidLevel1,
    DruidLevel2,
    DruidLevel3,
    DruidLevel4,
    DruidLevel5,
    DruidLevel6,
    DruidLevel7,
    DruidLevel8,
    DruidLevel9,
    DruidLevel10,
    DruidLevel11,
    DruidLevel12,
    DruidLevel13,
    DruidLevel14,
    DruidLevel15,
    DruidLevel16,
    DruidLevel17,
    DruidLevel18,
    DruidLevel19,
    DruidLevel20,
)
from CharacterConfigs.SubClasses.DruidSea import (
    DruidSeaLevel3,
    DruidSeaLevel5,
    DruidSeaLevel6,
    DruidSeaLevel7,
    DruidSeaLevel9,
    DruidSeaLevel10,
    DruidSeaLevel14,
    DruidSeaCustomStarterClassArgs,
)
from Combat.Monsters.CR_0.monsters import Crab, Octopus, ReefShark, GiantSeahorse
from Definitions import Ability, Skill
from Features.CharacterFeats import Backgrounds, EpicBoon, GeneralFeats, OriginFeats
from SpeciesConfigs.Elf import ElfSpeciesBuilder, ElvenLineage
from Spells.Definitions import (
    DruidLevel0Spells,
    DruidLevel1Spells,
    DruidLevel2Spells,
    DruidLevel3Spells,
    DruidLevel4Spells,
    DruidLevel5Spells,
    DruidLevel6Spells,
    DruidLevel7Spells,
    DruidLevel9Spells,
)
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import DruidSkillsStatBlock


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=DruidSeaCustomStarterClassArgs(
            skills=DruidSkillsStatBlock(
                proficiencies={
                    Skill.ARCANA: False,
                    Skill.ANIMAL_HANDLING: True,
                    Skill.INSIGHT: False,
                    Skill.MEDICINE: False,
                    Skill.NATURE: False,
                    Skill.PERCEPTION: True,
                    Skill.RELIGION: False,
                    Skill.SURVIVAL: False,
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
                Skill.NATURE,
                Skill.SURVIVAL,
            ]
        ),
        add_default_equipment=True,
        origin_feat=OriginFeats.Tough(),
        armor=[],
        weapons=[],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: DruidLevel1(
                    cantrip_1=DruidLevel0Spells.THUNDERCLAP,
                    cantrip_2=DruidLevel0Spells.SHILLELAGH,
                    spell_1=DruidLevel1Spells.ENTANGLE,
                    spell_2=DruidLevel1Spells.FAERIE_FIRE,
                    spell_3=DruidLevel1Spells.ANIMAL_FRIENDSHIP,
                    spell_4=DruidLevel1Spells.GOODBERRY,
                ),
                2: DruidLevel2(
                    spell=DruidLevel1Spells.HEALING_WORD,
                    known_forms=[Crab, Octopus, ReefShark, GiantSeahorse],
                ),
                3: DruidLevel3(
                    spell=DruidLevel2Spells.SPIKE_GROWTH,
                ),
                4: DruidLevel4(
                    general_feat=GeneralFeats.WarCaster(
                        character_level=4,
                        ability=Ability.WISDOM,
                    ),
                    cantrip=DruidLevel0Spells.ELEMENTALISM,
                    spell=DruidLevel2Spells.AID,
                ),
                5: DruidLevel5(
                    spell_1=DruidLevel3Spells.CALL_LIGHTNING,
                    spell_2=DruidLevel3Spells.AURA_OF_VITALITY,
                ),
                6: DruidLevel6(
                    spell=DruidLevel3Spells.DISPEL_MAGIC,
                ),
                7: DruidLevel7(
                    spell=DruidLevel2Spells.LESSER_RESTORATION,
                ),
                8: DruidLevel8(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.WISDOM, 2),
                        ]
                    ),
                    spell=DruidLevel4Spells.FREEDOM_OF_MOVEMENT,
                ),
                9: DruidLevel9(
                    spell_1=DruidLevel5Spells.CONTAGION,
                    spell_2=DruidLevel5Spells.GEAS,
                ),
                10: DruidLevel10(
                    cantrip=DruidLevel0Spells.GUIDANCE,
                    spell=DruidLevel5Spells.ANTILIFE_SHELL,
                ),
                11: DruidLevel11(
                    spell=DruidLevel6Spells.CONJURE_FEY,
                ),
                12: DruidLevel12(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.CONSTITUTION, 2),
                        ]
                    ),
                ),
                13: DruidLevel13(
                    spell=DruidLevel7Spells.FIRE_STORM,
                ),
                14: DruidLevel14(),
                15: DruidLevel15(
                    spell=DruidLevel7Spells.REGENERATE,
                ),
                16: DruidLevel16(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.WISDOM, 2),
                        ]
                    ),
                ),
                17: DruidLevel17(
                    spell=DruidLevel9Spells.STORM_OF_VENGEANCE,
                ),
                19: DruidLevel19(
                    epic_boon=EpicBoon.DummyEpicBoon(),
                    spell=DruidLevel9Spells.SHAPECHANGE,
                ),
                18: DruidLevel18(
                    spell=DruidLevel9Spells.TRUE_RESURRECTION,
                ),
                20: DruidLevel20(
                    spell=DruidLevel9Spells.FORESIGHT,
                ),
            },
            subclass_features_by_level={
                3: DruidSeaLevel3(),
                5: DruidSeaLevel5(),
                6: DruidSeaLevel6(),
                7: DruidSeaLevel7(),
                9: DruidSeaLevel9(),
                10: DruidSeaLevel10(),
                14: DruidSeaLevel14(),
            },
        ),
        replace_spells={},
    )


class ExampleDruidSeaCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Example Sea Druid",
            starter_class_builder=get_starter_class_builder(),
            species_builder=ElfSpeciesBuilder(
                elven_lineage=ElvenLineage.WOOD_ELF,
                skill_proficiency=Skill.PERCEPTION,
            ),
        )
