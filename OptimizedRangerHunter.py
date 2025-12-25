from CharacterConfigs.CharacterClasses.RangerBase import (
    RangerLevel1,
    RangerLevel10,
    RangerLevel11,
    RangerLevel12,
    RangerLevel13,
    RangerLevel14,
    RangerLevel15,
    RangerLevel16,
    RangerLevel17,
    RangerLevel18,
    RangerLevel19,
    RangerLevel2,
    RangerLevel20,
    RangerLevel3,
    RangerLevel4,
    RangerLevel5,
    RangerLevel6,
    RangerLevel7,
    RangerLevel8,
    RangerLevel9,
)
from CharacterConfigs.RangerHunter import (
    HunterRangerLevel13,
    HunterRangerLevel15,
    HunterRangerLevel17,
    HunterRangerLevel20,
    HunterRangerLevel3,
    HunterRangerLevel5,
    HunterRangerLevel7,
    HunterRangerLevel9,
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
from SpeciesConfigs import Human
from Spells.Definitions import (
    RangerLevel1Spells,
    RangerLevel2Spells,
    RangerLevel3Spells,
    RangerLevel4Spells,
    RangerLevel5Spells,
)
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import FighterSkillsStatBlock, RangerSkillsStatBlock
from CharacterConfigs.CharacterClasses.import RangerBase
from CharacterConfigs import RangerHunter


def get_data() -> CharacterSheetCreator.CharacterSheetData:
    ranger_hunter = RangerBase.RangerStarter(
        ranger_level=3,
        subclass=Definitions.RangerSubclass.HUNTER,
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
        skills=RangerSkillsStatBlock(
            proficiencies={
                Skill.ANIMAL_HANDLING: False,
                Skill.ATHLETICS: False,
                Skill.INSIGHT: True,
                Skill.INVESTIGATION: False,
                Skill.NATURE: False,
                Skill.PERCEPTION: True,
                Skill.STEALTH: True,
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
        weapons=[],
        armor=[],
        ranger_feature_per_level=RangerBase.RangerFeaturePerLevel(
            ranger_level_1=RangerLevel1(
                weapon_mastery_1=Weapons.Longbow(),
                weapon_mastery_2=Weapons.Scimitar(),
                spell_1=RangerLevel1Spells.CURE_WOUNDS,
                spell_2=RangerLevel1Spells.FOG_CLOUD,
            ),
            ranger_level_2=RangerLevel2(
                skill=Definitions.Skill.STEALTH,
                fighting_style=FightingStyles.Archery(),
                spell=RangerLevel1Spells.LONGSTRIDER,
            ),
            ranger_level_3=RangerLevel3(
                spell=RangerLevel1Spells.JUMP,
            ),
            # ranger_level_4=RangerLevel4(
            #     general_feat=GeneralFeats.AbilityScoreImprovement(
            #         [
            #             (Ability.CONSTITUTION, 2),
            #         ]
            #     ),
            #     spell=RangerLevel1Spells.CURE_WOUNDS,
            # ),
            # ranger_level_5=RangerLevel5(
            #     spell=RangerLevel2Spells.ZONE_OF_TRUTH,
            # ),
            # ranger_level_6=RangerLevel6(),
            # ranger_level_7=RangerLevel7(
            #     spell=RangerLevel2Spells.LESSER_RESTORATION,
            # ),
            # ranger_level_8=RangerLevel8(
            #     general_feat=GeneralFeats.AbilityScoreImprovement(
            #         [
            #             (Ability.STRENGTH, 2),
            #         ]
            #     ),
            # ),
            # ranger_level_9=RangerLevel9(
            #     spell=RangerLevel3Spells.AURA_OF_VITALITY,
            # ),
            # ranger_level_10=RangerLevel10(),
            # ranger_level_11=RangerLevel11(
            #     spell=RangerLevel3Spells.BLINDING_SMITE,
            # ),
            # ranger_level_12=RangerLevel12(
            #     general_feat=GeneralFeats.AbilityScoreImprovement(
            #         [
            #             (Ability.CHARISMA, 2),
            #         ]
            #     ),
            # ),
            # ranger_level_13=RangerLevel13(
            #     spell=RangerLevel4Spells.DEATH_WARD,
            # ),
            # ranger_level_14=RangerLevel14(),
            # ranger_level_15=RangerLevel15(
            #     spell=RangerLevel4Spells.AURA_OF_PURITY,
            # ),
            # ranger_level_16=RangerLevel16(
            #     general_feat=GeneralFeats.AbilityScoreImprovement(
            #         [
            #             (Ability.CHARISMA, 2),
            #         ]
            #     ),
            # ),
            # ranger_level_17=RangerLevel17(
            #     spell_1=RangerLevel5Spells.BANISHING_SMITE,
            #     spell_2=RangerLevel5Spells.GEAS,
            # ),
            # ranger_level_19=RangerLevel19(
            #     spell=RangerLevel5Spells.CIRCLE_OF_POWER,
            # ),
            # ranger_level_18=RangerLevel18(),
            # ranger_level_20=RangerLevel20(),
            ranger_subclass_level_3=HunterRangerLevel3(),
            # ranger_subclass_level_5=HunterRangerLevel5(),
            # ranger_subclass_level_7=HunterRangerLevel7(),
            # ranger_subclass_level_9=HunterRangerLevel9(),
            # ranger_subclass_level_13=HunterRangerLevel13(),
            # ranger_subclass_level_15=HunterRangerLevel15(),
            # ranger_subclass_level_17=HunterRangerLevel17(),
            # ranger_subclass_level_20=HunterRangerLevel20(),
        ),
        # replace_spells={
        #     RangerLevel1Spells.CURE_WOUNDS: RangerLevel2Spells.MAGIC_WEAPON,
        # },
    )

    species_data = Human.human_character_data(
        skill_proficiency=Skill.MEDICINE,
        origin_feat=OriginFeats.Skilled(
            skills=[
                Skill.SURVIVAL,
                Skill.ACROBATICS,
                Skill.ANIMAL_HANDLING,
            ]
        ),
    )
    character_class_data = ranger_hunter.create()

    character_sheet_data = CharacterSheetCreator.CharacterSheetData()

    character_sheet_data.character_name = "Sten"
    character_sheet_data.merge_with(character_class_data)
    character_sheet_data.merge_with(species_data)
    return character_sheet_data


if __name__ == "__main__":
    character_sheet_data = get_data()
    character_sheet_data.create_character_sheet()
