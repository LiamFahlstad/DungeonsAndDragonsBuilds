from CharacterConfigs.Bases.BarbarianBase import (
    BarbarianLevel1,
    BarbarianLevel10,
    BarbarianLevel11,
    BarbarianLevel12,
    BarbarianLevel13,
    BarbarianLevel14,
    BarbarianLevel15,
    BarbarianLevel16,
    BarbarianLevel17,
    BarbarianLevel18,
    BarbarianLevel19,
    BarbarianLevel2,
    BarbarianLevel20,
    BarbarianLevel3,
    BarbarianLevel4,
    BarbarianLevel5,
    BarbarianLevel6,
    BarbarianLevel7,
    BarbarianLevel8,
    BarbarianLevel9,
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
from SpeciesConfigs import Orc
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import BarbarianSkillsStatBlock
from CharacterConfigs.Bases import BarbarianBase
from CharacterConfigs.BarbarianPathOfTheBerserker import (
    PathOfTheBerserkerBarbarianLevel3,
    PathOfTheBerserkerBarbarianLevel5,
    PathOfTheBerserkerBarbarianLevel7,
    PathOfTheBerserkerBarbarianLevel9,
)


def get_data() -> CharacterSheetCreator.CharacterSheetData:
    barbarian_path_of_the_berserker = BarbarianBase.BarbarianStarter(
        barbarian_level=3,
        subclass=Definitions.BarbarianSubclass.PATH_OF_THE_BERSERKER,
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
        skills=BarbarianSkillsStatBlock(
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
        weapons=[],
        armor=[],
        barbarian_feature_per_level=BarbarianBase.BarbarianFeaturePerLevel(
            barbarian_level_1=BarbarianLevel1(
                weapon_mastery_1=Weapons.Handaxe(),
                weapon_mastery_2=Weapons.Greataxe(),
            ),
            barbarian_level_2=BarbarianLevel2(),
            barbarian_level_3=BarbarianLevel3(
                skill=Definitions.Skill.PERCEPTION,
            ),
            # barbarian_level_4=BarbarianLevel4(
            #     general_feat=GeneralFeats.AbilityScoreImprovement(
            #         [
            #             (Ability.CONSTITUTION, 2),
            #         ]
            #     ),
            #     spell=BarbarianLevel1Spells.CURE_WOUNDS,
            # ),
            # barbarian_level_5=BarbarianLevel5(
            #     spell=BarbarianLevel2Spells.ZONE_OF_TRUTH,
            # ),
            # barbarian_level_6=BarbarianLevel6(),
            # barbarian_level_7=BarbarianLevel7(
            #     spell=BarbarianLevel2Spells.LESSER_RESTORATION,
            # ),
            # barbarian_level_8=BarbarianLevel8(
            #     general_feat=GeneralFeats.AbilityScoreImprovement(
            #         [
            #             (Ability.STRENGTH, 2),
            #         ]
            #     ),
            # ),
            # barbarian_level_9=BarbarianLevel9(
            #     spell=BarbarianLevel3Spells.AURA_OF_VITALITY,
            # ),
            # barbarian_level_10=BarbarianLevel10(),
            # barbarian_level_11=BarbarianLevel11(
            #     spell=BarbarianLevel3Spells.BLINDING_SMITE,
            # ),
            # barbarian_level_12=BarbarianLevel12(
            #     general_feat=GeneralFeats.AbilityScoreImprovement(
            #         [
            #             (Ability.CHARISMA, 2),
            #         ]
            #     ),
            # ),
            # barbarian_level_13=BarbarianLevel13(
            #     spell=BarbarianLevel4Spells.DEATH_WARD,
            # ),
            # barbarian_level_14=BarbarianLevel14(),
            # barbarian_level_15=BarbarianLevel15(
            #     spell=BarbarianLevel4Spells.AURA_OF_PURITY,
            # ),
            # barbarian_level_16=BarbarianLevel16(
            #     general_feat=GeneralFeats.AbilityScoreImprovement(
            #         [
            #             (Ability.CHARISMA, 2),
            #         ]
            #     ),
            # ),
            # barbarian_level_17=BarbarianLevel17(
            #     spell_1=BarbarianLevel5Spells.BANISHING_SMITE,
            #     spell_2=BarbarianLevel5Spells.GEAS,
            # ),
            # barbarian_level_19=BarbarianLevel19(
            #     spell=BarbarianLevel5Spells.CIRCLE_OF_POWER,
            # ),
            # barbarian_level_18=BarbarianLevel18(),
            # barbarian_level_20=BarbarianLevel20(),
            barbarian_subclass_level_3=PathOfTheBerserkerBarbarianLevel3(),
            # barbarian_subclass_level_5=PathOfTheBerserkerBarbarianLevel5(),
            # barbarian_subclass_level_7=PathOfTheBerserkerBarbarianLevel7(),
            # barbarian_subclass_level_9=PathOfTheBerserkerBarbarianLevel9(),
            # barbarian_subclass_level_13=PathOfTheBerserkerBarbarianLevel13(),
            # barbarian_subclass_level_15=PathOfTheBerserkerBarbarianLevel15(),
            # barbarian_subclass_level_17=PathOfTheBerserkerBarbarianLevel17(),
            # barbarian_subclass_level_20=PathOfTheBerserkerBarbarianLevel20(),
        ),
        # replace_spells={
        #     BarbarianLevel1Spells.CURE_WOUNDS: BarbarianLevel2Spells.MAGIC_WEAPON,
        # },
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
