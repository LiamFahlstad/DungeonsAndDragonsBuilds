"""Example build: Rogue Swashbuckler (2014 rules). Demonstrates the subclass up through level 17."""

import Core.Definitions as Definitions
from Builds.CharacterBuilder import CharacterBuilder
from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterConfigs.BaseClasses.RogueBase import (
    RogueLevel1,
    RogueLevel2,
    RogueLevel3,
    RogueLevel4,
    RogueLevel5,
    RogueLevel6,
    RogueLevel7,
    RogueLevel8,
    RogueLevel9,
    RogueLevel10,
    RogueLevel11,
    RogueLevel12,
    RogueLevel13,
    RogueLevel14,
    RogueLevel15,
    RogueLevel16,
    RogueLevel17,
)
from CharacterConfigs.SubClasses2014.RogueSwashbuckler import (
    RogueSwashbucklerCustomStarterClassArgs,
    RogueSwashbucklerLevel3,
    RogueSwashbucklerLevel9,
    RogueSwashbucklerLevel13,
    RogueSwashbucklerLevel17,
)
from Core.Definitions import Ability, Skill
from Features.CharacterFeats import Backgrounds, GeneralFeats, OriginFeats
from Features.Equipment import Armor, Weapons
from Features.Items import Items, Packs
from SpeciesConfigs import Elf
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import RogueSkillsStatBlock


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=RogueSwashbucklerCustomStarterClassArgs(
            skills=RogueSkillsStatBlock(
                proficiencies={
                    Skill.ACROBATICS: True,
                    Skill.ATHLETICS: True,
                    Skill.DECEPTION: False,
                    Skill.INSIGHT: False,
                    Skill.INTIMIDATION: False,
                    Skill.INVESTIGATION: False,
                    Skill.PERCEPTION: False,
                    Skill.SLEIGHT_OF_HAND: True,
                    Skill.STEALTH: True,
                }
            ),
        ),
        base_class_level=17,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilitiesStatBlock(
            strength=8,
            dexterity=15,
            constitution=13,
            intelligence=10,
            wisdom=12,
            charisma=14,
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.CHARISMA, 1),
                (Ability.DEXTERITY, 2),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.PERSUASION,
                Skill.PERFORMANCE,
            ]
        ),
        add_default_equipment=False,
        origin_feat=OriginFeats.Alert(),
        armor=[
            Armor.LeatherArmor(),
        ],
        weapons=[
            Weapons.Rapier(),
            Weapons.Shortsword(),
        ],
        items=Packs.BurglarsPack().get_items()
        + [
            (Items.ThievesTools(), 1),
        ],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: RogueLevel1(
                    skill_1=Definitions.Skill.STEALTH,
                    skill_2=Definitions.Skill.SLEIGHT_OF_HAND,
                    weapon_mastery_1=Weapons.Rapier(),
                    weapon_mastery_2=Weapons.Shortsword(),
                ),
                2: RogueLevel2(),
                3: RogueLevel3(),
                4: RogueLevel4(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[(Ability.DEXTERITY, 2)]),
                ),
                5: RogueLevel5(),
                6: RogueLevel6(
                    skill_1=Definitions.Skill.ACROBATICS,
                    skill_2=Definitions.Skill.ATHLETICS,
                ),
                7: RogueLevel7(),
                8: RogueLevel8(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[(Ability.CHARISMA, 2)]),
                ),
                9: RogueLevel9(),
                10: RogueLevel10(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[(Ability.DEXTERITY, 2)]),
                ),
                11: RogueLevel11(),
                12: RogueLevel12(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[(Ability.CHARISMA, 2)]),
                ),
                13: RogueLevel13(),
                14: RogueLevel14(),
                15: RogueLevel15(),
                16: RogueLevel16(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[(Ability.DEXTERITY, 2)]),
                ),
                17: RogueLevel17(),
            },
            subclass_features_by_level={
                3: RogueSwashbucklerLevel3(),
                9: RogueSwashbucklerLevel9(),
                13: RogueSwashbucklerLevel13(),
                17: RogueSwashbucklerLevel17(),
            },
        ),
    )


class ExampleRogueSwashbuckler2014CharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Example Rogue Swashbuckler",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Elf.ElfSpeciesBuilder(
                elven_lineage=Elf.ElvenLineage.DROW,
                skill_proficiency=Definitions.Skill.PERCEPTION,
            ),
        )
