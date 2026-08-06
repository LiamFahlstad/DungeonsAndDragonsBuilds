"""Example build: Rogue Scout (2014 rules). Demonstrates the subclass up through level 17."""

import Core.Definitions as Definitions
from Builds.CharacterBuilder import CharacterBuilder
from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterContent.Classes.BaseClasses.RogueBase import (
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
from CharacterContent.Classes.SubClasses2014.RogueScout import (
    RogueScoutCustomStarterClassArgs,
    RogueScoutLevel3,
    RogueScoutLevel9,
    RogueScoutLevel13,
    RogueScoutLevel17,
)
from Core.Definitions import Ability, Skill
from CharacterContent.Features.CharacterFeats import Backgrounds, GeneralFeats, OriginFeats
from CharacterContent.Items import Armor, Weapons
from CharacterContent.Items import Items
from CharacterContent.Species import Elf
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import RogueSkillsStatBlock


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=RogueScoutCustomStarterClassArgs(
            skills=RogueSkillsStatBlock(
                proficiencies={
                    Skill.ACROBATICS: True,
                    Skill.ATHLETICS: False,
                    Skill.DECEPTION: False,
                    Skill.INSIGHT: True,
                    Skill.INTIMIDATION: False,
                    Skill.INVESTIGATION: False,
                    Skill.PERCEPTION: True,
                    Skill.SLEIGHT_OF_HAND: False,
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
            wisdom=14,
            charisma=12,
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.WISDOM, 1),
                (Ability.DEXTERITY, 2),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.ANIMAL_HANDLING,
                Skill.PERSUASION,
            ]
        ),
        add_default_equipment=False,
        origin_feat=OriginFeats.Alert(),
        armor=[
            Armor.LeatherArmor(),
        ],
        weapons=[
            Weapons.Shortbow(),
            Weapons.Shortsword(),
        ],
        items=[
            (Items.ThievesTools(), 1),
        ],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: RogueLevel1(
                    skill_expertise_1=Definitions.Skill.STEALTH,
                    skill_expertise_2=Definitions.Skill.PERCEPTION,
                    weapon_mastery_1=Weapons.Shortbow(),
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
                    skill_expertise_1=Definitions.Skill.ACROBATICS,
                    skill_expertise_2=Definitions.Skill.ANIMAL_HANDLING,
                ),
                7: RogueLevel7(),
                8: RogueLevel8(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[(Ability.WISDOM, 2)]),
                ),
                9: RogueLevel9(),
                10: RogueLevel10(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[(Ability.DEXTERITY, 2)]),
                ),
                11: RogueLevel11(),
                12: RogueLevel12(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[(Ability.WISDOM, 2)]),
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
                3: RogueScoutLevel3(),
                9: RogueScoutLevel9(),
                13: RogueScoutLevel13(),
                17: RogueScoutLevel17(),
            },
        ),
    )


class Y2014RogueScoutFennickQuickstepCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Fennick Quickstep",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Elf.ElfSpeciesBuilder(
                elven_lineage=Elf.ElvenLineage.WOOD_ELF,
                skill_proficiency=Definitions.Skill.SURVIVAL,
            ),
        )
