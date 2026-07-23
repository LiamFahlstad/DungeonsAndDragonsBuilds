"""Example build: Sorcerer Draconic Bloodline. Adapted from an optimized reference build to demonstrate this subclass."""

from Builds.CharacterBuilder import CharacterBuilder
from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterConfigs.BaseClasses.SorcererBase import (
    SorcererLevel1,
    SorcererLevel2,
    SorcererLevel3,
    SorcererLevel4,
    SorcererLevel5,
)
from CharacterConfigs.SubClasses2024.SorcererDraconic import (
    SorcererDraconicCustomStarterClassArgs,
    SorcererDraconicLevel3,
)
from Core.Definitions import Ability, Skill
from Features.CharacterFeats import Backgrounds, GeneralFeats, OriginFeats
from Features.Equipment import Weapons
from Features.SpeciesFeatures import DragonbornFeatures
from SpeciesConfigs import Dragonborn
from Spells import SpellLists as SpellDefinitions
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import SorcererSkillsStatBlock


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=SorcererDraconicCustomStarterClassArgs(
            skills=SorcererSkillsStatBlock(
                proficiencies={
                    Skill.ARCANA: True,
                    Skill.DECEPTION: False,
                    Skill.INSIGHT: False,
                    Skill.INTIMIDATION: True,
                    Skill.PERSUASION: False,
                    Skill.RELIGION: False,
                }
            ),
        ),
        base_class_level=5,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilitiesStatBlock(
            strength=8,
            dexterity=13,
            constitution=14,
            intelligence=10,
            wisdom=12,
            charisma=15,
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.CHARISMA, 2),
                (Ability.DEXTERITY, 1),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.INSIGHT,
                Skill.PERSUASION,
            ]
        ),
        add_default_equipment=False,
        origin_feat=OriginFeats.Lucky(),
        weapons=[
            Weapons.Spear(),
            Weapons.Dagger(),
        ],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: SorcererLevel1(
                    cantrip_1=SpellDefinitions.SorcererLevel0Spells.FIRE_BOLT,
                    cantrip_2=SpellDefinitions.SorcererLevel0Spells.PRESTIDIGITATION,
                    cantrip_3=SpellDefinitions.SorcererLevel0Spells.LIGHT,
                    cantrip_4=SpellDefinitions.SorcererLevel0Spells.SHOCKING_GRASP,
                    spell_1=SpellDefinitions.SorcererLevel1Spells.SHIELD,
                    spell_2=SpellDefinitions.SorcererLevel1Spells.BURNING_HANDS,
                ),
                2: SorcererLevel2(
                    spell_1=SpellDefinitions.SorcererLevel1Spells.FALSE_LIFE,
                    spell_2=SpellDefinitions.SorcererLevel1Spells.MAGIC_MISSILE,
                ),
                3: SorcererLevel3(
                    spell_1=SpellDefinitions.SorcererLevel2Spells.SCORCHING_RAY,
                    spell_2=SpellDefinitions.SorcererLevel2Spells.MIRROR_IMAGE,
                ),
                4: SorcererLevel4(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [(Ability.CHARISMA, 2)]
                    ),
                    cantrip=SpellDefinitions.SorcererLevel0Spells.MAGE_HAND,
                    spell=SpellDefinitions.SorcererLevel2Spells.MISTY_STEP,
                ),
                5: SorcererLevel5(
                    spell_1=SpellDefinitions.SorcererLevel3Spells.FIREBALL,
                    spell_2=SpellDefinitions.SorcererLevel3Spells.COUNTERSPELL,
                ),
            },
            subclass_features_by_level={
                3: SorcererDraconicLevel3(),
            },
        ),
    )


class ExampleSorcererDraconicCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Example Draconic Sorcerer",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Dragonborn.DragonbornSpeciesBuilder(
                dragon_ancestry_color=DragonbornFeatures.DragonColor.RED,
            ),
        )
