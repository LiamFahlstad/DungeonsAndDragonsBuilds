import CharacterSheetCreator
from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.FighterBase import (
    FighterLevel1,
    FighterLevel2,
    FighterLevel3,
    FighterLevel4,
    FighterLevel5,
)
from CharacterConfigs.SubClasses.FighterBattleMaster import (
    BattleMasterFighterLevel3,
    BattleMasterFighterStarterClassBuilder,
)
from Definitions import Ability, Skill
from Features import (
    Backgrounds,
    FightingStyles,
    GeneralFeats,
    Maneuvers,
    OriginFeats,
    Weapons,
)
from SpeciesConfigs import Human
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import FighterSkillsStatBlock


def get_data() -> CharacterSheetCreator.CharacterSheetData:
    battle_master_fighter_starter = BattleMasterFighterStarterClassBuilder(
        fighter_level=5,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilitiesStatBlock(
            strength=15,
            dexterity=12,
            constitution=14,
            intelligence=8,
            wisdom=10,
            charisma=13,
        ),
        # Choose two skills to be proficient in
        fighter_skills=FighterSkillsStatBlock(
            proficiencies={
                Skill.ACROBATICS: True,
                Skill.ANIMAL_HANDLING: False,
                Skill.ATHLETICS: True,
                Skill.HISTORY: False,
                Skill.INSIGHT: False,
                Skill.INTIMIDATION: False,
                Skill.PERCEPTION: False,
                Skill.SURVIVAL: False,
            }
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.CONSTITUTION, 2),
                (Ability.CHARISMA, 1),
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
        weapons=[Weapons.Handaxe()],
        fighter_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: FighterLevel1(
                    weapon_mastery_1=Weapons.Longsword(),
                    weapon_mastery_2=Weapons.Flail(),
                    weapon_mastery_3=Weapons.Greatsword(),
                    fighting_style=FightingStyles.Defense(),
                ),
                2: FighterLevel2(),
                3: FighterLevel3(),
                4: FighterLevel4(
                    weapon_mastery=Weapons.Handaxe(),
                    general_feat=GeneralFeats.Sentinel(
                        character_level=4,
                        ability=Ability.STRENGTH,
                    ),
                ),
                5: FighterLevel5(),
            },
            subclass_features_by_level={
                3: BattleMasterFighterLevel3(
                    maneuver_1=Maneuvers.GoadingAttack(),
                    maneuver_2=Maneuvers.PushingAttack(),
                    maneuver_3=Maneuvers.Riposte(),
                ),
            },
        ),
    )
    character_class_data = battle_master_fighter_starter.create()

    species_data = Human.human_character_data(
        skill_proficiency=Skill.SURVIVAL,
        origin_feat=OriginFeats.Skilled(
            skills=[
                Skill.PERCEPTION,
                Skill.INSIGHT,
                Skill.HISTORY,
            ]
        ),
    )

    character_sheet_data = CharacterSheetCreator.CharacterSheetData()

    character_sheet_data.character_name = "Sten"
    character_sheet_data.merge_with(character_class_data)
    character_sheet_data.merge_with(species_data)
    return character_sheet_data


if __name__ == "__main__":
    character_sheet_data = get_data()
    character_sheet_data.create_character_sheet()
