from Builds.CharacterBuilder import CharacterBuilder
from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterConfigs.BaseClasses.MonkBase import MonkLevel1, MonkLevel2, MonkLevel3
from CharacterConfigs.SubClasses2024.MonkElements import (
    MonkElementsCustomStarterClassArgs,
    MonkElementsLevel3,
)
from Core.Definitions import Ability, Skill
from Features.CharacterFeats import Backgrounds, OriginFeats
from Features.SpeciesFeatures import GoliathFeatures
from SpeciesConfigs import Goliath
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import MonkSkillsStatBlock


def get_starter_class_builder():
    monk_level = 3
    return StarterClassBuilder(
        non_generic_arguments=MonkElementsCustomStarterClassArgs(
            skills=MonkSkillsStatBlock(
                proficiencies={
                    Skill.ACROBATICS: False,
                    Skill.ATHLETICS: True,
                    Skill.HISTORY: False,
                    Skill.INSIGHT: True,
                    Skill.RELIGION: False,
                    Skill.STEALTH: False,
                }
            ),
            monk_level=monk_level,
            unarmed_strike=Ability.DEXTERITY,
        ),
        base_class_level=monk_level,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        # Base array: STR 12, DEX 15, CON 14, INT 8, WIS 13, CHA 10
        # After background bonus (DEX +2, WIS +1): STR 12, DEX 17, CON 14, INT 8, WIS 14, CHA 10
        abilities=StandardArrayAbilitiesStatBlock(
            strength=12,
            dexterity=15,
            constitution=14,
            intelligence=8,
            wisdom=13,
            charisma=10,
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.DEXTERITY, 2),
                (Ability.WISDOM, 1),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.ACROBATICS,
                Skill.PERCEPTION,
            ]
        ),
        add_default_equipment=True,
        origin_feat=OriginFeats.TavernBrawler(),
        armor=[],
        weapons=[],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: MonkLevel1(),
                2: MonkLevel2(),
                3: MonkLevel3(),
            },
            subclass_features_by_level={
                3: MonkElementsLevel3(),
            },
        ),
    )


class OptimizedElementsMonkGoliathCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Optimized Elements Monk (Goliath)",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Goliath.GoliathSpeciesBuilder(
                giant_ancestry_type=GoliathFeatures.GiantAncestryType.STONE_GIANT,
            ),
        )
