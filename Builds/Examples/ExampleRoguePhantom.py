"""Example build: Rogue Phantom. Adapted from an optimized reference build to demonstrate this subclass."""

import Definitions
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
from CharacterConfigs.SubClasses.RoguePhantom import (
    RoguePhantomLevel3,
    RoguePhantomLevel9,
    RoguePhantomLevel13,
    RoguePhantomLevel17,
    RoguePhantomCustomStarterClassArgs,
)
from Definitions import Ability, Skill
from Features.CharacterFeats import Backgrounds, GeneralFeats, OriginFeats
from Features.Equipment import Armor, Weapons
from Features.Items import Items, Packs
from SpeciesConfigs import Elf
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import RogueSkillsStatBlock


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=RoguePhantomCustomStarterClassArgs(
            skills=RogueSkillsStatBlock(
                proficiencies={
                    Skill.ACROBATICS: True,
                    Skill.ATHLETICS: False,
                    Skill.DECEPTION: False,
                    Skill.INSIGHT: True,
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
            constitution=14,
            intelligence=10,
            wisdom=13,
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
                Skill.RELIGION,
                Skill.INSIGHT,
            ]
        ),
        add_default_equipment=False,
        origin_feat=OriginFeats.Alert(),
        armor=[
            Armor.LeatherArmor(),
        ],
        weapons=[
            Weapons.Shortsword(player_is_proficient=True),
            Weapons.Dagger(player_is_proficient=True),
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
                    weapon_mastery_1=Weapons.Shortsword(),
                    weapon_mastery_2=Weapons.Dagger(),
                ),
                2: RogueLevel2(),
                3: RogueLevel3(),
                4: RogueLevel4(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[(Ability.DEXTERITY, 2)],
                    ),
                ),
                5: RogueLevel5(),
                6: RogueLevel6(
                    skill_1=Definitions.Skill.ACROBATICS,
                    skill_2=Definitions.Skill.INSIGHT,
                ),
                7: RogueLevel7(),
                8: RogueLevel8(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[(Ability.WISDOM, 2)],
                    ),
                ),
                9: RogueLevel9(),
                10: RogueLevel10(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[(Ability.DEXTERITY, 2)],
                    ),
                ),
                11: RogueLevel11(),
                12: RogueLevel12(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[(Ability.CONSTITUTION, 2)],
                    ),
                ),
                13: RogueLevel13(),
                14: RogueLevel14(),
                15: RogueLevel15(),
                16: RogueLevel16(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[(Ability.DEXTERITY, 2)],
                    ),
                ),
                17: RogueLevel17(),
            },
            subclass_features_by_level={
                3: RoguePhantomLevel3(),
                9: RoguePhantomLevel9(),
                13: RoguePhantomLevel13(),
                17: RoguePhantomLevel17(),
            },
        ),
    )


class ExampleRoguePhantomCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Example Rogue Phantom",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Elf.ElfSpeciesBuilder(
                elven_lineage=Elf.ElvenLineage.WOOD_ELF,
                skill_proficiency=Definitions.Skill.PERCEPTION,
            ),
        )
