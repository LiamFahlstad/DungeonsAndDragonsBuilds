from CharacterConfigs import BattleMasterFighter
from CharacterConfigs.BattleMasterFighter import (
    FighterLevel1,
    FighterLevel3,
    FighterLevel4,
)
import CharacterSheetCreator
from Definitions import (
    Ability,
    Skill,
)
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


if __name__ == "__main__":
    character_class_data = BattleMasterFighter.create_battle_master_fighter_data(
        fighter_level=5,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilitiesStatBlock(
            strength=14,
            dexterity=12,
            constitution=15,
            intelligence=8,
            wisdom=10,
            charisma=13,
        ),
        # Choose two skills to be proficient in
        skills=FighterSkillsStatBlock(
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
                (Ability.STRENGTH, 1),
                (Ability.CONSTITUTION, 2),
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
        fighter_level_1=FighterLevel1(
            weapon_mastery_1=Weapons.Longsword(),
            weapon_mastery_2=Weapons.Flail(),
            weapon_mastery_3=Weapons.Greatsword(),
            fighting_style=FightingStyles.Defense(),
        ),
        fighter_level_3=FighterLevel3(
            maneuver_1=Maneuvers.GoadingAttack(),
            maneuver_2=Maneuvers.PushingAttack(),
            maneuver_3=Maneuvers.Riposte(),
        ),
        fighter_level_4=FighterLevel4(
            general_feat=GeneralFeats.AbilityScoreImprovement(
                [
                    (Ability.STRENGTH, 1),
                    (Ability.CONSTITUTION, 1),
                ]
            )
        ),
    )

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
    character_sheet_data.create_character_sheet()
