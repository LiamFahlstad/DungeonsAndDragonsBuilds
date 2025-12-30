from CharacterConfigs.CharacterClasses.RogueLevelFeatures import (
    RogueLevel1,
    RogueLevel10,
    RogueLevel11,
    RogueLevel12,
    RogueLevel13,
    RogueLevel14,
    RogueLevel15,
    RogueLevel16,
    RogueLevel17,
    RogueLevel18,
    RogueLevel19,
    RogueLevel2,
    RogueLevel20,
    RogueLevel3,
    RogueLevel4,
    RogueLevel5,
    RogueLevel6,
    RogueLevel7,
    RogueLevel8,
    RogueLevel9,
)
import CharacterSheetCreator
from Definitions import (
    Ability,
    Skill,
)
import Definitions
from Features import (
    Backgrounds,
    FightingStyles,
    GeneralFeats,
    OriginFeats,
    Weapons,
)
from SpeciesConfigs import Elf
from StatBlocks import AbilitiesStatBlock
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import RogueSkillsStatBlock
from CharacterConfigs.CharacterClasses import RogueBase, ClassBuilder
from CharacterConfigs.RogueAssassin import (
    AssassinRogueLevel3,
    AssassinRogueLevel9,
)
from CharacterConfigs.RogueAssassin import (
    AssassinRogueStarterClassBuilder,
)


def get_data() -> CharacterSheetCreator.CharacterSheetData:
    rogue_assassin = AssassinRogueStarterClassBuilder(
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

    character_class_data = rogue_assassin.create()

    def ability_with_highest_modifier(
        abilities: AbilitiesStatBlock.AbilitiesStatBlock,
    ) -> Definitions.Ability:
        highest_ability = None
        highest_modifier = -999
        for ability in [
            Definitions.Ability.INTELLIGENCE,
            Definitions.Ability.WISDOM,
            Definitions.Ability.CHARISMA,
        ]:
            modifier = abilities.get_modifier(ability)
            if modifier > highest_modifier:
                highest_modifier = modifier
                highest_ability = ability
        if highest_ability is None:
            raise ValueError("No abilities found.")
        return highest_ability

    abilities = character_class_data.abilities
    if abilities is None:
        raise ValueError("AbilitiesStatBlock is None.")

    spell_casting_ability = ability_with_highest_modifier(abilities)
    character_class_data.spell_casting_ability = spell_casting_ability
    species_data = Elf.elf_character_data(
        character_level=character_class_data.character_level,
        elven_lineage=Elf.ElvenLineage.WOOD_ELF,
        skill_proficiency=Definitions.Skill.PERCEPTION,
        spell_casting_ability=spell_casting_ability,
    )
    character_sheet_data = CharacterSheetCreator.CharacterSheetData()

    character_sheet_data.character_name = "Dark Shadow Nightmare"
    character_sheet_data.merge_with(character_class_data)
    character_sheet_data.merge_with(species_data)
    return character_sheet_data


if __name__ == "__main__":
    character_sheet_data = get_data()
    character_sheet_data.create_character_sheet()
