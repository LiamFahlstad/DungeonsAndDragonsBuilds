import CharacterSheetCreator
from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.RangerBase import (
    RangerLevel1,
    RangerLevel2,
    RangerLevel3,
    RangerLevel4,
    RangerLevel5,
)
from CharacterConfigs.SubClasses.RangerBeastMaster import (
    BeastMasterRangerLevel3,
    BeastMasterRangerStarterClassBuilder,
)
from Definitions import Ability, CharacterClass, Skill
from Entities import BeastMasterBeastOfTheSky
from Features import Backgrounds, FightingStyles, GeneralFeats, OriginFeats, Weapons
from SpeciesConfigs import Gnome
from Spells.Definitions import RangerLevel1Spells, RangerLevel2Spells
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import RangerSkillsStatBlock


def get_data() -> CharacterSheetCreator.CharacterSheetData:
    battle_master_ranger_starter = BeastMasterRangerStarterClassBuilder(
        ranger_level=5,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilitiesStatBlock(
            strength=10,
            dexterity=15,
            constitution=12,
            intelligence=14,
            wisdom=13,
            charisma=8,
        ),
        # Choose two skills to be proficient in
        ranger_skills=RangerSkillsStatBlock(
            proficiencies={
                Skill.ANIMAL_HANDLING: False,
                Skill.ATHLETICS: True,
                Skill.INSIGHT: False,
                Skill.INVESTIGATION: True,
                Skill.NATURE: False,
                Skill.PERCEPTION: True,
                Skill.STEALTH: False,
                Skill.SURVIVAL: False,
            }
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.DEXTERITY, 2),
                (Ability.WISDOM, 1),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.SLEIGHT_OF_HAND,
                Skill.ACROBATICS,
            ]
        ),
        add_default_equipment=True,
        origin_feat=OriginFeats.Crater(artisans_tools=[]),
        armor=[],
        weapons=[],
        ranger_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: RangerLevel1(
                    weapon_mastery_1=Weapons.Longbow(),
                    weapon_mastery_2=Weapons.Scimitar(),
                    spell_1=RangerLevel1Spells.CURE_WOUNDS,
                    spell_2=RangerLevel1Spells.FOG_CLOUD,
                ),
                2: RangerLevel2(
                    skill=Skill.ACROBATICS,
                    fighting_style=FightingStyles.Archery(),
                    spell=RangerLevel1Spells.JUMP,
                ),
                3: RangerLevel3(
                    spell=RangerLevel1Spells.ALARM,
                ),
                4: RangerLevel4(
                    spell=RangerLevel1Spells.LONGSTRIDER,
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.DEXTERITY, 1),
                            (Ability.INTELLIGENCE, 1),
                        ]
                    ),
                ),
                5: RangerLevel5(
                    spell=RangerLevel2Spells.PASS_WITHOUT_TRACE,
                ),
            },
            subclass_features_by_level={
                3: BeastMasterRangerLevel3(),
            },
        ),
        replace_spells={
            RangerLevel1Spells.ALARM: RangerLevel2Spells.SILENCE,
            RangerLevel1Spells.LONGSTRIDER: RangerLevel2Spells.BEAST_SENSE,
        },
    )
    character_class_data = battle_master_ranger_starter.create()

    species_data = Gnome.rock_gnome_character_data()

    character_sheet_data = CharacterSheetCreator.CharacterSheetData()

    character_sheet_data.character_name = "Jan Heting"
    character_sheet_data.merge_with(character_class_data)
    character_sheet_data.merge_with(species_data)
    return character_sheet_data


if __name__ == "__main__":
    character_sheet_data = get_data()
    character_sheet_data.create_character_sheet()
    output_path = character_sheet_data.get_file_path()

    BeastMasterBeastOfTheSky(
        wisdom_modifier=character_sheet_data.get_ability_modifier(Ability.WISDOM),
        ranger_level=character_sheet_data.get_level_for_class(CharacterClass.RANGER),
        proficiency_bonus=character_sheet_data.character_level // 4 + 2,
        spell_attack_modifier=character_sheet_data.calculate_attack_bonus_for_ability(
            Ability.WISDOM
        ),
    ).write_to_file(output_path, mode="a")
