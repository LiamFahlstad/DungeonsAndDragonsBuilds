"""
Skeleton build for Grabriel's Cleric (level 3, Light Domain).

This is a minimal starting point, not a finished build. Every line marked
TODO is a placeholder value you should replace with your own choice. See
Y2024_Cleric_Light_SolenneBrightward.py in this same folder for a fully
worked out, higher-level example of the same subclass.
"""

from Builds.CharacterBuilder import CharacterBuilder
from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterContent.Classes.BaseClasses.ClericBase import (
    ClericLevel1,
    ClericLevel2,
    ClericLevel3,
)
from CharacterContent.Classes.SubClasses2024.ClericLight import (
    ClericLightCustomStarterClassArgs,
    ClericLightLevel3,
)
from Core.Definitions import Ability, Skill
from CharacterContent.Features.CharacterFeats import Backgrounds, OriginFeats
from CharacterContent.Species import Dwarf
from CharacterContent.Spells.SpellLists import (
    ClericLevel0Spells,
    ClericLevel1Spells,
    ClericLevel2Spells,
)
from StatBlocks.AbilitiesStatBlock import PointBuyAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import ClericSkillsStatBlock


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=ClericLightCustomStarterClassArgs(
            skills=ClericSkillsStatBlock(
                proficiencies={
                    # TODO: pick exactly 2 skills as True, from: History,
                    # Insight, Medicine, Persuasion, Religion.
                    Skill.MEDICINE: True,
                    Skill.RELIGION: True,
                }
            ),
        ),
        base_class_level=3,
        # TODO: Point Buy - spend exactly 27 points across your six abilities.
        # Each score must be between 8 and 15. Costs per score:
        #   8 -> 0 pts   10 -> 2 pts   12 -> 4 pts   14 -> 7 pts
        #   9 -> 1 pt    11 -> 3 pts   13 -> 5 pts   15 -> 9 pts
        abilities=PointBuyAbilitiesStatBlock(
            strength=8,
            dexterity=13,
            constitution=14,
            intelligence=10,
            wisdom=15,
            charisma=12,
        ),
        # TODO: replace with your actual background's ability bonuses (PHB background list).
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.WISDOM, 2),
                (Ability.CONSTITUTION, 1),
            ]
        ),
        # TODO: replace with your actual background's skill proficiencies.
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.ANIMAL_HANDLING,
                Skill.PERCEPTION,
            ]
        ),
        add_default_equipment=True,
        # TODO: choose your origin feat (PHB feat list). Tough is a simple, safe placeholder.
        origin_feat=OriginFeats.Tough(),
        armor=[],
        weapons=[],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: ClericLevel1(
                    # TODO: choose your 3 cantrips.
                    cantrip_1=ClericLevel0Spells.GUIDANCE,
                    cantrip_2=ClericLevel0Spells.TOLL_THE_DEAD,
                    cantrip_3=ClericLevel0Spells.SACRED_FLAME,
                    # TODO: choose your prepared level 1 spells.
                    spell_1=ClericLevel1Spells.HEALING_WORD,
                    spell_2=ClericLevel1Spells.BANE,
                    spell_3=ClericLevel1Spells.CREATE_OR_DESTROY_WATER,
                    spell_4=ClericLevel1Spells.GUIDING_BOLT,
                ),
                2: ClericLevel2(
                    # TODO: choose a spell to add to your prepared list.
                    spell=ClericLevel1Spells.BLESS,
                ),
                3: ClericLevel3(
                    # TODO: choose a spell to add to your prepared list.
                    spell=ClericLevel2Spells.ENHANCE_ABILITY,
                ),
            },
            subclass_features_by_level={
                3: ClericLightLevel3(),
            },
        ),
    )


class Y2024ClericLightGrabrielCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Grabriel",
            starter_class_builder=get_starter_class_builder(),
            # TODO: choose your species. Dwarf is used here as a simple
            # placeholder with no extra sub-choices required.
            species_builder=Dwarf.DwarfSpeciesBuilder(),
        )
