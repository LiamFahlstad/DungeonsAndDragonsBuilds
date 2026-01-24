import CharacterSheetCreator
import Definitions
from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.MonkBase import MonkLevel1, MonkLevel2, MonkLevel3
from CharacterConfigs.SubClasses.MonkShadow import (
    ShadowMonkLevel3,
    ShadowMonkStarterClassBuilder,
)
from Definitions import Ability, Skill
from Features import Backgrounds, OriginFeats
from SpeciesConfigs import Elf
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import MonkSkillsStatBlock


def get_data() -> CharacterSheetCreator.CharacterSheetData:
    monk_shadow = ShadowMonkStarterClassBuilder(
        monk_level=3,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilitiesStatBlock(
            strength=8,
            dexterity=15,
            constitution=13,
            intelligence=12,
            wisdom=14,
            charisma=10,
        ),
        # Choose two skills to be proficient in
        monk_skills=MonkSkillsStatBlock(
            proficiencies={
                Skill.ACROBATICS: True,
                Skill.ATHLETICS: False,
                Skill.HISTORY: False,
                Skill.INSIGHT: False,
                Skill.RELIGION: False,
                Skill.STEALTH: True,
            }
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.WISDOM, 1),
                (Ability.DEXTERITY, 2),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.SLEIGHT_OF_HAND,
                Skill.INSIGHT,
            ]
        ),
        add_default_equipment=True,
        origin_feat=OriginFeats.Alert(),
        armor=[],
        weapons=[],
        monk_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: MonkLevel1(),
                2: MonkLevel2(),
                3: MonkLevel3(),
            },
            subclass_features_by_level={
                3: ShadowMonkLevel3(),
            },
        ),
    )

    character_class_data = monk_shadow.create()

    abilities = character_class_data.abilities
    if abilities is None:
        raise ValueError("AbilitiesStatBlock is None.")

    spell_casting_ability = abilities.get_spellcasting_ability_with_highest_modifier()
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
