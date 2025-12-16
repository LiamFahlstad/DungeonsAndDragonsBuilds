from CharacterConfigs.PaladinBase import (
    PaladinLevel1,
    PaladinLevel10,
    PaladinLevel11,
    PaladinLevel12,
    PaladinLevel13,
    PaladinLevel14,
    PaladinLevel15,
    PaladinLevel16,
    PaladinLevel17,
    PaladinLevel18,
    PaladinLevel19,
    PaladinLevel2,
    PaladinLevel20,
    PaladinLevel3,
    PaladinLevel4,
    PaladinLevel5,
    PaladinLevel6,
    PaladinLevel7,
    PaladinLevel8,
    PaladinLevel9,
)
from CharacterConfigs.PaladinOathOfGlory import (
    GloryPaladinLevel13,
    GloryPaladinLevel15,
    GloryPaladinLevel17,
    GloryPaladinLevel20,
    GloryPaladinLevel3,
    GloryPaladinLevel5,
    GloryPaladinLevel7,
    GloryPaladinLevel9,
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
    PaladinLevel1Spells,
    PaladinLevel2Spells,
    PaladinLevel3Spells,
    PaladinLevel4Spells,
    PaladinLevel5Spells,
)
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import FighterSkillsStatBlock, PaladinSkillsStatBlock
from CharacterConfigs import PaladinBase
from CharacterConfigs import PaladinOathOfGlory

if __name__ == "__main__":
    paladin_oath_of_glory = PaladinBase.PaladinStarter(
        paladin_level=20,
        subclass=Definitions.PaladinSubclass.OATH_OF_GLORY,
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
        paladin_feature_per_level=PaladinBase.PaladinFeaturePerLevel(
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
            paladin_level_6=PaladinLevel6(),
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
            paladin_level_10=PaladinLevel10(),
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
            paladin_level_14=PaladinLevel14(),
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
            paladin_level_18=PaladinLevel18(),
            paladin_level_20=PaladinLevel20(),
            paladin_subclass_level_3=GloryPaladinLevel3(),
            paladin_subclass_level_5=GloryPaladinLevel5(),
            paladin_subclass_level_7=GloryPaladinLevel7(),
            paladin_subclass_level_9=GloryPaladinLevel9(),
            paladin_subclass_level_13=GloryPaladinLevel13(),
            paladin_subclass_level_15=GloryPaladinLevel15(),
            paladin_subclass_level_17=GloryPaladinLevel17(),
            paladin_subclass_level_20=GloryPaladinLevel20(),
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
    character_class_data = paladin_oath_of_glory.create()

    character_sheet_data = CharacterSheetCreator.CharacterSheetData()

    character_sheet_data.character_name = "Sten"
    character_sheet_data.merge_with(character_class_data)
    character_sheet_data.merge_with(species_data)
    character_sheet_data.create_character_sheet()
