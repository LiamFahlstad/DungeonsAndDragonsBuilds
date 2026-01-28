import Definitions
from Builds.CharacterBuilder import CharacterBuilder
from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.RogueBase import RogueLevel1, RogueLevel2, RogueLevel3
from CharacterConfigs.SubClasses.RogueAssassin import (
    AssassinRogueLevel3,
    AssassinRogueStarterClassBuilder,
)
from Definitions import Ability, Skill
from Features import Backgrounds, OriginFeats, Weapons
from SpeciesConfigs import Elf
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import RogueSkillsStatBlock


def get_starter_class_builder():
    return AssassinRogueStarterClassBuilder(
        rogue_level=3,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilitiesStatBlock(
            strength=8,
            dexterity=15,
            constitution=14,
            intelligence=13,
            wisdom=12,
            charisma=10,
        ),
        # Choose two skills to be proficient in
        rogue_skills=RogueSkillsStatBlock(
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
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.CONSTITUTION, 2),
                (Ability.DEXTERITY, 1),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.NATURE,
                Skill.DECEPTION,
            ]
        ),
        add_default_equipment=True,
        origin_feat=OriginFeats.Alert(),
        armor=[],
        weapons=[],
        rogue_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: RogueLevel1(
                    skill_1=Definitions.Skill.STEALTH,
                    skill_2=Definitions.Skill.SLEIGHT_OF_HAND,
                    weapon_mastery_1=Weapons.Shortsword(),
                    weapon_mastery_2=Weapons.Scimitar(),
                ),
                2: RogueLevel2(),
                3: RogueLevel3(),
            },
            subclass_features_by_level={
                3: AssassinRogueLevel3(),
            },
        ),
    )


class OptimizedAssassinRogueCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Optimized Rogue Assassin",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Elf.ElfSpeciesBuilder(
                elven_lineage=Elf.ElvenLineage.WOOD_ELF,
                skill_proficiency=Definitions.Skill.PERCEPTION,
            ),
        )
