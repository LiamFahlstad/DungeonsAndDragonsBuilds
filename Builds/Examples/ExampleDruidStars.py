"""Example build: Druid Circle of the Stars. Adapted from an optimized reference build to demonstrate this subclass."""

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
from CharacterConfigs.SubClasses2024.DruidStars import (
    DruidStarsCustomStarterClassArgs,
    DruidStarsLevel3,
    DruidStarsLevel6,
    DruidStarsLevel10,
    DruidStarsLevel14,
)
from Combat.Monsters.CR_1.monsters import BrownBear, DireWolf, GiantSpider, Tiger
from Core.Definitions import Ability, Skill
from Features.CharacterFeats import Backgrounds, EpicBoon, GeneralFeats, OriginFeats
from SpeciesConfigs import Gnome
from Spells.SpellLists import (
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
        non_generic_arguments=DruidStarsCustomStarterClassArgs(
            skills=DruidSkillsStatBlock(
                proficiencies={
                    Skill.ARCANA: True,
                    Skill.ANIMAL_HANDLING: False,
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
            dexterity=14,
            constitution=13,
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
                Skill.INTIMIDATION,
                Skill.PERSUASION,
            ]
        ),
        add_default_equipment=True,
        origin_feat=OriginFeats.Tough(),
        armor=[],
        weapons=[],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: DruidLevel1(
                    cantrip_1=DruidLevel0Spells.STARRY_WISP,
                    cantrip_2=DruidLevel0Spells.THORN_WHIP,
                    spell_1=DruidLevel1Spells.FAERIE_FIRE,
                    spell_2=DruidLevel1Spells.DETECT_MAGIC,
                    spell_3=DruidLevel1Spells.ANIMAL_FRIENDSHIP,
                    spell_4=DruidLevel1Spells.GOODBERRY,
                ),
                2: DruidLevel2(
                    spell=DruidLevel1Spells.HEALING_WORD,
                    known_forms=[BrownBear, DireWolf, GiantSpider, Tiger],
                ),
                3: DruidLevel3(
                    spell=DruidLevel2Spells.AID,
                ),
                4: DruidLevel4(
                    general_feat=GeneralFeats.WarCaster(
                        character_level=4,
                        ability=Ability.WISDOM,
                    ),
                    cantrip=DruidLevel0Spells.ELEMENTALISM,
                    spell=DruidLevel2Spells.MOONBEAM,
                ),
                5: DruidLevel5(
                    spell_1=DruidLevel3Spells.CALL_LIGHTNING,
                    spell_2=DruidLevel3Spells.DAYLIGHT,
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
                            (Ability.DEXTERITY, 2),
                        ]),
                    spell=DruidLevel4Spells.FREEDOM_OF_MOVEMENT,
                ),
                9: DruidLevel9(
                    spell_1=DruidLevel5Spells.CONTAGION,
                    spell_2=DruidLevel5Spells.GEAS,
                ),
                10: DruidLevel10(
                    cantrip=DruidLevel0Spells.RESISTANCE,
                    spell=DruidLevel5Spells.ANTILIFE_SHELL,
                ),
                11: DruidLevel11(
                    spell=DruidLevel6Spells.CONJURE_FEY,
                ),
                12: DruidLevel12(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.WISDOM, 2),
                        ]),
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
                            (Ability.CONSTITUTION, 2),
                        ]),
                ),
                17: DruidLevel17(
                    spell=DruidLevel9Spells.STORM_OF_VENGEANCE,
                ),
                18: DruidLevel18(
                    spell=DruidLevel9Spells.TRUE_RESURRECTION,
                ),
                19: DruidLevel19(
                    epic_boon=EpicBoon.DummyEpicBoon(),
                    spell=DruidLevel9Spells.SHAPECHANGE,
                ),
                20: DruidLevel20(
                    spell=DruidLevel9Spells.FORESIGHT,
                ),
            },
            subclass_features_by_level={
                3: DruidStarsLevel3(),
                6: DruidStarsLevel6(),
                10: DruidStarsLevel10(),
                14: DruidStarsLevel14(),
            },
        ),
        replace_spells={},
    )


class ExampleDruidStarsCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Example Stars Druid",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Gnome.ForestGnomeSpeciesBuilder(
                spell_casting_ability=Ability.WISDOM
            ),
        )
