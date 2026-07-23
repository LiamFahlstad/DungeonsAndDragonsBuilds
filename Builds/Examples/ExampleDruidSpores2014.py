"""Example build: Druid Circle of Spores (2014 rules). Demonstrates the subclass up through level 14."""

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
)
from CharacterConfigs.SubClasses2014.DruidSpores import (
    DruidSporesCustomStarterClassArgs,
    DruidSporesLevel3,
    DruidSporesLevel6,
    DruidSporesLevel10,
    DruidSporesLevel14,
)
from Combat.Monsters.CR_1.monsters import BrownBear, DireWolf, GiantSpider, Tiger
from Core.Definitions import Ability, Skill
from Features.CharacterFeats import Backgrounds, GeneralFeats, OriginFeats
from Features.CharacterFeats import OriginFeats as SpeciesOriginFeats
from SpeciesConfigs import Human
from Spells.SpellLists import (
    DruidLevel0Spells,
    DruidLevel1Spells,
    DruidLevel2Spells,
    DruidLevel3Spells,
    DruidLevel4Spells,
)
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import DruidSkillsStatBlock


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=DruidSporesCustomStarterClassArgs(
            skills=DruidSkillsStatBlock(
                proficiencies={
                    Skill.ARCANA: False,
                    Skill.ANIMAL_HANDLING: False,
                    Skill.INSIGHT: True,
                    Skill.MEDICINE: False,
                    Skill.NATURE: True,
                    Skill.PERCEPTION: False,
                    Skill.RELIGION: False,
                    Skill.SURVIVAL: False,
                }
            ),
        ),
        base_class_level=14,
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
                Skill.NATURE,
            ]
        ),
        add_default_equipment=True,
        origin_feat=OriginFeats.Tough(),
        armor=[],
        weapons=[],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: DruidLevel1(
                    cantrip_1=DruidLevel0Spells.GUIDANCE,
                    cantrip_2=DruidLevel0Spells.SHILLELAGH,
                    spell_1=DruidLevel1Spells.ENTANGLE,
                    spell_2=DruidLevel1Spells.FAERIE_FIRE,
                    spell_3=DruidLevel1Spells.ANIMAL_FRIENDSHIP,
                    spell_4=DruidLevel1Spells.GOODBERRY,
                ),
                2: DruidLevel2(
                    spell=DruidLevel1Spells.HEALING_WORD,
                    known_forms=[BrownBear, DireWolf, GiantSpider, Tiger],
                ),
                3: DruidLevel3(
                    spell=DruidLevel2Spells.SPIKE_GROWTH,
                ),
                4: DruidLevel4(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.WISDOM, 2),
                        ]),
                    cantrip=DruidLevel0Spells.DRUIDCRAFT,
                    spell=DruidLevel2Spells.HEAT_METAL,
                ),
                5: DruidLevel5(
                    spell_1=DruidLevel3Spells.CALL_LIGHTNING,
                    spell_2=DruidLevel3Spells.DISPEL_MAGIC,
                ),
                6: DruidLevel6(
                    spell=DruidLevel3Spells.MELD_INTO_STONE,
                ),
                7: DruidLevel7(
                    spell=DruidLevel2Spells.LESSER_RESTORATION,
                ),
                8: DruidLevel8(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.CONSTITUTION, 2),
                        ]),
                    spell=DruidLevel4Spells.FREEDOM_OF_MOVEMENT,
                ),
                9: DruidLevel9(
                    spell_1=DruidLevel3Spells.AURA_OF_VITALITY,
                    spell_2=DruidLevel3Spells.CONJURE_ANIMALS,
                ),
                10: DruidLevel10(
                    cantrip=DruidLevel0Spells.PRODUCE_FLAME,
                    spell=DruidLevel3Spells.PLANT_GROWTH,
                ),
                11: DruidLevel11(
                    spell=DruidLevel4Spells.CHARM_MONSTER,
                ),
                12: DruidLevel12(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.WISDOM, 1),
                            (Ability.DEXTERITY, 1),
                        ]),
                ),
                13: DruidLevel13(
                    spell=DruidLevel4Spells.DIVINATION,
                ),
                14: DruidLevel14(),
            },
            subclass_features_by_level={
                3: DruidSporesLevel3(),
                6: DruidSporesLevel6(),
                10: DruidSporesLevel10(),
                14: DruidSporesLevel14(),
            },
        ),
        replace_spells={},
    )


class ExampleDruidSpores2014CharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Example Circle of Spores Druid",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Human.HumanSpeciesBuilder(
                origin_feat=SpeciesOriginFeats.Tough(),
                skill_proficiency=Skill.INSIGHT,
            ),
        )
