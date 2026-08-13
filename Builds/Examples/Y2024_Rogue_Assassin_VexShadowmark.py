"""Example build: Rogue Assassin. Adapted from an optimized reference build to demonstrate this subclass."""

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
)
from CharacterContent.Classes.SubClasses2024.RogueAssassin import (
    RogueAssassinCustomStarterClassArgs,
    RogueAssassinLevel3,
)
from Core.Definitions import Ability, Skill
from CharacterContent.Features.CharacterFeats import Backgrounds, GeneralFeats, OriginFeats
from CharacterContent.Items import Armor, Weapons
from CharacterContent.Items import Items
from CharacterContent.ToolProficiencies.Proficiencies import ThievesTools as ThievesToolsProficiency
from CharacterContent.Species import Elf
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import RogueSkillsStatBlock


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=RogueAssassinCustomStarterClassArgs(
            skills=RogueSkillsStatBlock(
                proficiencies={
                    Skill.ACROBATICS: True,
                    Skill.ATHLETICS: False,
                    Skill.DECEPTION: False,
                    Skill.INSIGHT: False,
                    Skill.INTIMIDATION: False,
                    Skill.INVESTIGATION: True,
                    Skill.PERCEPTION: False,
                    Skill.SLEIGHT_OF_HAND: True,
                    Skill.STEALTH: True,
                }
            ),
        ),
        base_class_level=4,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilitiesStatBlock(
            strength=8,
            dexterity=15,
            constitution=14,
            intelligence=13,
            wisdom=12,
            charisma=10,
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.INTELLIGENCE, 1),
                (Ability.DEXTERITY, 2),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.ARCANA,
                Skill.DECEPTION,
            ]
        ),
        add_default_equipment=False,
        origin_feat=OriginFeats.Alert(),
        armor=[
            Armor.LeatherArmor(),
        ],
        weapons=[
            Weapons.Shortsword(),
            Weapons.Scimitar(),
        ],
        items=[
            (Items.Makarov(), 1),
            (Items.NightVisionGoggles(), 2),
            (Items.ButterflyKnife(), 2),
            (Items.Arrows(), 20),
            (Items.Quiver(), 1),
            (Items.ThievesTools(), 1),
        ],
        tool_proficiencies=[
            ThievesToolsProficiency(),
        ],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: RogueLevel1(
                    skill_expertise_1=Definitions.Skill.STEALTH,
                    skill_expertise_2=Definitions.Skill.SLEIGHT_OF_HAND,
                    weapon_mastery_1=Weapons.Shortsword(),
                    weapon_mastery_2=Weapons.Scimitar(),
                ),
                2: RogueLevel2(),
                3: RogueLevel3(),
                4: RogueLevel4(
                    general_feat=GeneralFeats.DualWielder(
                        character_level=4, ability=Ability.DEXTERITY
                    ),
                ),
                5: RogueLevel5(),
                6: RogueLevel6(
                    skill_expertise_1=Definitions.Skill.ACROBATICS,
                    skill_expertise_2=Definitions.Skill.INVESTIGATION,
                ),
            },
            subclass_features_by_level={
                3: RogueAssassinLevel3(),
            },
        ),
    )


class Y2024RogueAssassinVexShadowmarkCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Vex Shadowmark",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Elf.ElfSpeciesBuilder(
                elven_lineage=Elf.ElvenLineage.WOOD_ELF,
                skill_proficiency=Definitions.Skill.PERCEPTION,
            ),
        )
