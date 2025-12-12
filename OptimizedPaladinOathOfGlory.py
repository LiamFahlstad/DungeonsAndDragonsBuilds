from CharacterConfigs import BattleMasterFighter
from CharacterConfigs import PaladinOathOfGlory
from CharacterConfigs.PaladinBase import (
    PaladinLevel1,
    PaladinLevel11,
    PaladinLevel12,
    PaladinLevel13,
    PaladinLevel15,
    PaladinLevel16,
    PaladinLevel17,
    PaladinLevel19,
    PaladinLevel2,
    PaladinLevel3,
    PaladinLevel4,
    PaladinLevel5,
    PaladinLevel7,
    PaladinLevel8,
    PaladinLevel9,
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
from Spells.Definitions import (
    PaladinLevel1Spells,
    PaladinLevel2Spells,
    PaladinLevel3Spells,
    PaladinLevel4Spells,
    PaladinLevel5Spells,
)
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import FighterSkillsStatBlock, PaladinSkillsStatBlock


if __name__ == "__main__":
    character_class_data = PaladinOathOfGlory.create(
        paladin_level=20,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilitiesStatBlock(
            strength=13,
            dexterity=10,
            constitution=15,
            intelligence=12,
            wisdom=8,
            charisma=14,
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
        weapons=[],
        armor=[],
        paladin_level_1=PaladinLevel1(
            weapon_mastery_1=Weapons.Handaxe(),
            weapon_mastery_2=Weapons.LightHammer(),
            spell_1=PaladinLevel1Spells.CURE_WOUNDS,
            spell_2=PaladinLevel1Spells.DIVINE_FAVOR,
        ),
        paladin_level_2=PaladinLevel2(
            fighting_style=FightingStyles.TwoWeaponFighting(),
            spell=PaladinLevel1Spells.SHIELD_OF_FAITH,
        ),
        paladin_level_3=PaladinLevel3(
            spell=PaladinLevel1Spells.BLESS,
        ),
        paladin_level_4=PaladinLevel4(
            general_feat=GeneralFeats.AbilityScoreImprovement(
                [
                    (Ability.CONSTITUTION, 2),
                ]
            ),
            spell=PaladinLevel1Spells.CURE_WOUNDS,
        ),
        paladin_level_5=PaladinLevel5(
            spell=PaladinLevel2Spells.ZONE_OF_TRUTH,
        ),
        paladin_level_7=PaladinLevel7(
            spell=PaladinLevel2Spells.LESSER_RESTORATION,
        ),
        paladin_level_8=PaladinLevel8(
            general_feat=GeneralFeats.AbilityScoreImprovement(
                [
                    (Ability.STRENGTH, 2),
                ]
            ),
        ),
        paladin_level_9=PaladinLevel9(
            spell=PaladinLevel3Spells.AURA_OF_VITALITY,
        ),
        paladin_level_11=PaladinLevel11(
            spell=PaladinLevel3Spells.BLINDING_SMITE,
        ),
        paladin_level_12=PaladinLevel12(
            general_feat=GeneralFeats.AbilityScoreImprovement(
                [
                    (Ability.CHARISMA, 2),
                ]
            ),
        ),
        paladin_level_13=PaladinLevel13(
            spell=PaladinLevel4Spells.DEATH_WARD,
        ),
        paladin_level_15=PaladinLevel15(
            spell=PaladinLevel4Spells.AURA_OF_PURITY,
        ),
        paladin_level_16=PaladinLevel16(
            general_feat=GeneralFeats.AbilityScoreImprovement(
                [
                    (Ability.CHARISMA, 2),
                ]
            ),
        ),
        paladin_level_17=PaladinLevel17(
            spell_1=PaladinLevel5Spells.BANISHING_SMITE,
            spell_2=PaladinLevel5Spells.GEAS,
        ),
        paladin_level_19=PaladinLevel19(
            spell=PaladinLevel5Spells.CIRCLE_OF_POWER,
        ),
        replace_spells={
            PaladinLevel1Spells.CURE_WOUNDS: PaladinLevel2Spells.MAGIC_WEAPON,
        },
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
