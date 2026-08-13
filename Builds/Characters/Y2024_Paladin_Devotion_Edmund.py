"""
Skeleton build for Edmund's Paladin (level 3, Oath of Devotion).

This is a minimal starting point, not a finished build. Every line marked
TODO is a placeholder value you should replace with your own choice. See
Y2024_Paladin_Glory_BalderSunoath.py in this same folder for a fully
worked out, higher-level example of the same class.
"""

from Builds.CharacterBuilder import CharacterBuilder
from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterContent.Classes.BaseClasses.PaladinBase import (
    PaladinLevel1,
    PaladinLevel2,
    PaladinLevel3,
)
from CharacterContent.Classes.SubClasses2024.PaladinDevotion import (
    PaladinDevotionCustomStarterClassArgs,
    PaladinDevotionLevel3,
)
from Core.Definitions import Ability, Skill
from CharacterContent.Features.CharacterFeats import Backgrounds, OriginFeats
from CharacterContent.Features.CombatFeatures import FightingStyles
from CharacterContent.Items import Weapons
from CharacterContent.Species import Dwarf
from CharacterContent.Spells.SpellLists import PaladinLevel1Spells
from StatBlocks.AbilitiesStatBlock import PointBuyAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import PaladinSkillsStatBlock


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=PaladinDevotionCustomStarterClassArgs(
            skills=PaladinSkillsStatBlock(
                proficiencies={
                    # TODO: pick exactly 2 skills as True, from: Athletics,
                    # Insight, Intimidation, Medicine, Persuasion, Religion.
                    Skill.ATHLETICS: True,
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
            strength=15,
            dexterity=10,
            constitution=13,
            intelligence=8,
            wisdom=12,
            charisma=14,
        ),
        # TODO: replace with your actual background's ability bonuses (PHB background list).
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.STRENGTH, 2),
                (Ability.CHARISMA, 1),
            ]
        ),
        # TODO: replace with your actual background's skill proficiencies.
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.INTIMIDATION,
                Skill.MEDICINE,
            ]
        ),
        add_default_equipment=True,
        # TODO: choose your origin feat (PHB feat list). Tough is a simple, safe placeholder.
        origin_feat=OriginFeats.Tough(),
        armor=[],
        weapons=[],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: PaladinLevel1(
                    # TODO: choose 2 weapons to gain Weapon Mastery with.
                    weapon_mastery_1=Weapons.Handaxe(),
                    weapon_mastery_2=Weapons.LightHammer(),
                    # TODO: choose your 2 prepared level 1 spells.
                    spell_1=PaladinLevel1Spells.DETECT_POISON_AND_DISEASE,
                    spell_2=PaladinLevel1Spells.DIVINE_FAVOR,
                ),
                2: PaladinLevel2(
                    # TODO: choose your Fighting Style.
                    fighting_style=FightingStyles.Defense(),
                    # TODO: choose a spell to add to your prepared list.
                    spell=PaladinLevel1Spells.BLESS,
                ),
                3: PaladinLevel3(
                    # TODO: choose a spell to add to your prepared list.
                    spell=PaladinLevel1Spells.DETECT_MAGIC,
                ),
            },
            subclass_features_by_level={
                3: PaladinDevotionLevel3(),
            },
        ),
    )


class Y2024PaladinDevotionEdmundCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            # TODO: replace with your character's name.
            name="Edmund",
            starter_class_builder=get_starter_class_builder(),
            # TODO: choose your species. Dwarf is used here as a simple
            # placeholder with no extra sub-choices required.
            species_builder=Dwarf.DwarfSpeciesBuilder(),
        )
