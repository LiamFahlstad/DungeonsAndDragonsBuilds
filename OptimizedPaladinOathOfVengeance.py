from CharacterConfigs import BattleMasterFighter
from CharacterConfigs import PaladinOathOfVengeance
from CharacterConfigs.PaladinBase import (
    PaladinLevel1,
    PaladinLevel2,
    PaladinLevel3,
    PaladinLevel4,
    PaladinLevel5,
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
from StatBlocks.SkillsStatBlock import FighterSkillsStatBlock, PaladinSkillsStatBlock


if __name__ == "__main__":
    character_class_data = PaladinOathOfVengeance.create(
        paladin_level=6,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilitiesStatBlock(
            strength=15,
            dexterity=10,
            constitution=14,
            intelligence=12,
            wisdom=8,
            charisma=13,
        ),
        # Choose two skills to be proficient in
        skills=PaladinSkillsStatBlock(
            proficiencies={
                Skill.ATHLETICS: True,
                Skill.INSIGHT: False,
                Skill.INTIMIDATION: False,
                Skill.MEDICINE: True,
                Skill.PERSUASION: False,
                Skill.RELIGION: False,
            }
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.STRENGTH, 2),
                (Ability.CONSTITUTION, 1),
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
        weapons=[
            Weapons.Handaxe(player_is_proficient=True),
            Weapons.LightHammer(player_is_proficient=True),
        ],
        armor=[],
        paladin_level_1=PaladinLevel1(
            weapon_mastery_1=Weapons.Handaxe(),
            weapon_mastery_2=Weapons.LightHammer(),
            spell_1="Cure Wounds",
            spell_2="Divine Favor",
        ),
        paladin_level_2=PaladinLevel2(
            fighting_style=FightingStyles.TwoWeaponFighting(),
            spell="Shield of Faith",
        ),
        paladin_level_3=PaladinLevel3(
            spell="Bless",
        ),
        paladin_level_4=PaladinLevel4(
            general_feat=GeneralFeats.AbilityScoreImprovement(
                [
                    (Ability.STRENGTH, 1),
                    (Ability.CONSTITUTION, 1),
                ]
            ),
            spell="Magic Weapon",
        ),
        paladin_level_5=PaladinLevel5(
            spell="Dispel Magic",
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
