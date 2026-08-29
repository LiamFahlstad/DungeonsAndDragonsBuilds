"""
Skeleton build for Kivi Jätti's Monk (level 3, Way of the Four Elements).

This is a minimal starting point, not a finished build. Every line marked
TODO is a placeholder value you should replace with your own choice. See
Y2024_Monk_Elements_KragStormfist.py in this same folder for a fully worked
out example of the same subclass.
"""

from Builds.CharacterBuilder import CharacterBuilder
from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterContent.Classes.BaseClasses.MonkBase import (
    MonkLevel1,
    MonkLevel2,
    MonkLevel3,
)
from CharacterContent.Classes.SubClasses2024.MonkElements import (
    MonkElementsCustomStarterClassArgs,
    MonkElementsLevel3,
)
from CharacterContent.Features.CharacterFeats import Backgrounds, OriginFeats
from CharacterContent.Features.ClassFeatures.Monk import MonkFeatures
from CharacterContent.Features.SpeciesFeatures import GoliathFeatures
from CharacterContent.Items import Items, Weapons
from CharacterContent.Species import Goliath
from CharacterContent.ToolProficiencies.Proficiencies import Drum, NavigatorsTools
from Core.Definitions import Ability, Skill
from StatBlocks.AbilitiesStatBlock import PointBuyAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import MonkSkillsStatBlock


def get_starter_class_builder():
    monk_level = 3
    martial_arts_die = MonkFeatures.LEVEL_TO_MARTIAL_ARTS_DIE[monk_level]
    return StarterClassBuilder(
        non_generic_arguments=MonkElementsCustomStarterClassArgs(
            skills=MonkSkillsStatBlock(
                proficiencies={
                    Skill.ACROBATICS: True,
                    Skill.ATHLETICS: False,
                    Skill.HISTORY: False,
                    Skill.INSIGHT: False,
                    Skill.RELIGION: False,
                    Skill.STEALTH: True,
                }
            ),
            monk_level=monk_level,
            unarmed_strike=Ability.DEXTERITY,
        ),
        base_class_level=monk_level,
        # TODO: Point Buy - spend exactly 27 points across your six abilities.
        # Each score must be between 8 and 15. Costs per score:
        #   8 -> 0 pts   10 -> 2 pts   12 -> 4 pts   14 -> 7 pts
        #   9 -> 1 pt    11 -> 3 pts   13 -> 5 pts   15 -> 9 pts
        abilities=PointBuyAbilitiesStatBlock(
            strength=12,  # 4 pts
            dexterity=15,  # 9 pts
            constitution=13,  # 5 pts
            intelligence=8,  # 0 pts
            wisdom=15,  # 9 pts
            charisma=8,  # 0 pts
        ),
        # TODO: replace with your actual background's ability bonuses (PHB background list).
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.DEXTERITY, 2),
                (Ability.WISDOM, 1),
            ]
        ),
        # TODO: replace with your actual background's skill proficiencies.
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.PERCEPTION,
                Skill.ATHLETICS,
            ]
        ),
        add_default_equipment=False,
        origin_feat=OriginFeats.TavernBrawler(),
        armor=[],
        weapons=[
            Weapons.UnarmedStrike(
                player_is_proficient=True,
                ability=Ability.DEXTERITY,
                damage_roll=martial_arts_die,
            ),
            Weapons.Dagger(),
        ],
        tool_proficiencies=[
            NavigatorsTools(),
            Drum(),
        ],
        # Explorer's Pack contents, listed explicitly.
        items=[
            (Items.Backpack(), 1),
            (Items.Bedroll(), 1),
            (Items.FlasksOfOil(), 2),
            (Items.Rations(), 10),
            (Items.Rope(), 1),
            (Items.Tinderbox(), 1),
            (Items.Torch(), 10),
            (Items.Waterskin(), 1),
            (Items.Drum(), 1),
        ],
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


class Y2024MonkElementsKiviJattiCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Kivi Jätti",
            starter_class_builder=get_starter_class_builder(),
            # TODO: choose your species. Goliath is used here as a simple
            # placeholder with no extra sub-choices required.
            species_builder=Goliath.GoliathSpeciesBuilder(
                giant_ancestry_type=GoliathFeatures.GiantAncestryType.STONE_GIANT
            ),
        )
