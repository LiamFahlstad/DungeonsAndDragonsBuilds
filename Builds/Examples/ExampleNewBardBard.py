"""
Example: A simple Bard build created from the template.

This file demonstrates how to take _TEMPLATE.py and create a complete,
working character build. Follow the same steps to create your own builds.
"""

from Builds.CharacterBuilder import CharacterBuilder
from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterConfigs.BaseClasses.BardBase import BardLevel1
from CharacterConfigs.SubClasses.BardLore import BardLoreCustomStarterClassArgs
from Definitions import Ability, Skill
from Features.CharacterFeats import Backgrounds, GeneralFeats, OriginFeats
from SpeciesConfigs import Human
from Spells.SpellLists import (
    BardLevel0Spells,
    BardLevel1Spells,
)
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import BardSkillsStatBlock


def get_starter_class_builder():
    """Bard College of Lore, level 3."""
    return StarterClassBuilder(
        non_generic_arguments=BardLoreCustomStarterClassArgs(
            skills=BardSkillsStatBlock(
                proficiencies={
                    Skill.ACROBATICS: True,
                    Skill.ANIMAL_HANDLING: False,
                    Skill.ARCANA: True,
                    Skill.DECEPTION: True,
                    Skill.HISTORY: False,
                    Skill.INSIGHT: False,
                    Skill.INTIMIDATION: False,
                    Skill.INVESTIGATION: False,
                    Skill.MEDICINE: False,
                    Skill.NATURE: False,
                    Skill.PERCEPTION: False,
                    Skill.PERFORMANCE: False,
                    Skill.PERSUASION: False,
                    Skill.RELIGION: False,
                    Skill.SLEIGHT_OF_HAND: False,
                    Skill.STEALTH: False,
                    Skill.SURVIVAL: False,
                }
            ),
        ),
        base_class_level=1,
        # Standard array: 15, 14, 13, 12, 10, 8
        # Bard is Charisma-primary for spellcasting and class features
        abilities=StandardArrayAbilitiesStatBlock(
            strength=8,
            dexterity=14,
            constitution=13,
            intelligence=12,
            wisdom=10,
            charisma=15,  # Primary for Bard
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.CHARISMA, 2),
                (Ability.DEXTERITY, 1),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.DECEPTION,
                Skill.PERFORMANCE,
            ]
        ),
        add_default_equipment=True,  # Use default Bard equipment
        origin_feat=OriginFeats.Musician(),
        armor=[],  # Bards use light armor by default
        weapons=[],  # Bards get simple weapons by default
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: BardLevel1(
                    # Bard cantrips and spells (needs 2 cantrips, 4 spells)
                    cantrip_1=BardLevel0Spells.VICIOUS_MOCKERY,
                    cantrip_2=BardLevel0Spells.PRESTIDIGITATION,
                    spell_1=BardLevel1Spells.HEALING_WORD,
                    spell_2=BardLevel1Spells.CHARM_PERSON,
                    spell_3=BardLevel1Spells.FAERIE_FIRE,
                    spell_4=BardLevel1Spells.HEROISM,
                ),
            },
            subclass_features_by_level={},
        ),
    )


class ExampleNewBardCharacterBuilder(CharacterBuilder):
    """A simple Bard build to show the template in action."""

    def __init__(self):
        super().__init__(
            name="Lyra the Bard",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Human.HumanSpeciesBuilder(
                origin_feat=OriginFeats.Musician(),
                skill_proficiency=Skill.PERFORMANCE,
            ),
        )
