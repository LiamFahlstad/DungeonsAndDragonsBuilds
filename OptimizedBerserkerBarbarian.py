import CharacterSheetCreator
import Definitions
from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.BarbarianBase import (
    BarbarianLevel1,
    BarbarianLevel2,
    BarbarianLevel3,
)
from CharacterConfigs.SubClasses.BarbarianPathOfTheBerserker import (
    PathOfTheBerserkerBarbarianLevel3,
    PathOfTheBerserkerBarbarianStarterClassBuilder,
)
from Definitions import Ability, Skill
from Features import Backgrounds, OriginFeats, Weapons
from SpeciesConfigs import Orc
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import BarbarianSkillsStatBlock


def get_data() -> CharacterSheetCreator.CharacterSheetData:
    barbarian_path_of_the_berserker = PathOfTheBerserkerBarbarianStarterClassBuilder(
        barbarian_level=3,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilitiesStatBlock(
            strength=15,
            dexterity=13,
            constitution=14,
            intelligence=8,
            wisdom=12,
            charisma=10,
        ),
        # Choose two skills to be proficient in
        barbarian_skills=BarbarianSkillsStatBlock(
            proficiencies={
                Skill.ANIMAL_HANDLING: False,
                Skill.ATHLETICS: True,
                Skill.INSIGHT: True,
                Skill.INTIMIDATION: False,
                Skill.NATURE: False,
                Skill.PERCEPTION: False,
                Skill.SURVIVAL: False,
            }
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.CONSTITUTION, 2),
                (Ability.STRENGTH, 1),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.INTIMIDATION,
                Skill.PERSUASION,
            ]
        ),
        add_default_equipment=True,
        origin_feat=OriginFeats.Tough(),
        armor=[],
        weapons=[],
        barbarian_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: BarbarianLevel1(
                    weapon_mastery_1=Weapons.Handaxe(),
                    weapon_mastery_2=Weapons.Greataxe(),
                ),
                2: BarbarianLevel2(),
                3: BarbarianLevel3(
                    skill=Definitions.Skill.PERCEPTION,
                ),
            },
            subclass_features_by_level={
                3: PathOfTheBerserkerBarbarianLevel3(),
            },
        ),
    )

    species_data = Orc.orc_character_data(
        origin_feat=OriginFeats.SavageAttacker(),
    )
    character_class_data = barbarian_path_of_the_berserker.create()

    character_sheet_data = CharacterSheetCreator.CharacterSheetData()

    character_sheet_data.character_name = "Olga"
    character_sheet_data.merge_with(character_class_data)
    character_sheet_data.merge_with(species_data)
    return character_sheet_data


if __name__ == "__main__":
    character_sheet_data = get_data()
    character_sheet_data.create_character_sheet()
