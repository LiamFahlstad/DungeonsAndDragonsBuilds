from CharacterConfigs.BaseClasses.import ClassBuilder
from CharacterConfigs.BaseClasses.PaladinLevelFeatures import (
    PaladinLevel1,
    PaladinLevel2,
    PaladinLevel3,
    PaladinLevel4,
    PaladinLevel5,
    PaladinLevel6,
    PaladinLevel7,
    PaladinLevel8,
    PaladinLevel9,
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
    PaladinLevel20,
)

import CharacterSheetCreator
from CharacterConfigs.SubClasses.PaladinOathOfGlory import (
    GloryPaladinLevel3,
    GloryPaladinLevel5,
    GloryPaladinLevel7,
    GloryPaladinLevel9,
    GloryPaladinLevel13,
    GloryPaladinLevel15,
    GloryPaladinLevel17,
    GloryPaladinLevel20,
    OathOfGloryPaladinStarterClassBuilder,
)
from Definitions import Ability, Skill
from Features import Backgrounds, FightingStyles, GeneralFeats, OriginFeats, Weapons
from SpeciesConfigs import Human
from Spells.Definitions import (
    PaladinLevel1Spells,
    PaladinLevel2Spells,
    PaladinLevel3Spells,
    PaladinLevel4Spells,
    PaladinLevel5Spells,
)
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import PaladinSkillsStatBlock


def get_data() -> CharacterSheetCreator.CharacterSheetData:
    paladin_oath_of_glory = OathOfGloryPaladinStarterClassBuilder(
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
        paladin_skills=PaladinSkillsStatBlock(
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
        armor=[],
        weapons=[],
        paladin_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: PaladinLevel1(
                    weapon_mastery_1=Weapons.Handaxe(),
                    weapon_mastery_2=Weapons.LightHammer(),
                    spell_1=PaladinLevel1Spells.CURE_WOUNDS,
                    spell_2=PaladinLevel1Spells.DIVINE_FAVOR,
                ),
                2: PaladinLevel2(
                    fighting_style=FightingStyles.TwoWeaponFighting(),
                    spell=PaladinLevel1Spells.SHIELD_OF_FAITH,
                ),
                3: PaladinLevel3(
                    spell=PaladinLevel1Spells.BLESS,
                ),
                4: PaladinLevel4(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.CONSTITUTION, 2),
                        ]
                    ),
                    spell=PaladinLevel1Spells.CURE_WOUNDS,
                ),
                5: PaladinLevel5(
                    spell=PaladinLevel2Spells.ZONE_OF_TRUTH,
                ),
                6: PaladinLevel6(),
                7: PaladinLevel7(
                    spell=PaladinLevel2Spells.LESSER_RESTORATION,
                ),
                8: PaladinLevel8(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.STRENGTH, 2),
                        ]
                    ),
                ),
                9: PaladinLevel9(
                    spell=PaladinLevel3Spells.AURA_OF_VITALITY,
                ),
                10: PaladinLevel10(),
                11: PaladinLevel11(
                    spell=PaladinLevel3Spells.BLINDING_SMITE,
                ),
                12: PaladinLevel12(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.CHARISMA, 2),
                        ]
                    ),
                ),
                13: PaladinLevel13(
                    spell=PaladinLevel4Spells.DEATH_WARD,
                ),
                14: PaladinLevel14(),
                15: PaladinLevel15(
                    spell=PaladinLevel4Spells.AURA_OF_PURITY,
                ),
                16: PaladinLevel16(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.CHARISMA, 2),
                        ]
                    ),
                ),
                17: PaladinLevel17(
                    spell_1=PaladinLevel5Spells.BANISHING_SMITE,
                    spell_2=PaladinLevel5Spells.GEAS,
                ),
                19: PaladinLevel19(
                    spell=PaladinLevel5Spells.CIRCLE_OF_POWER,
                ),
                18: PaladinLevel18(),
                20: PaladinLevel20(),
            },
            subclass_features_by_level={
                3: GloryPaladinLevel3(),
                5: GloryPaladinLevel5(),
                7: GloryPaladinLevel7(),
                9: GloryPaladinLevel9(),
                13: GloryPaladinLevel13(),
                15: GloryPaladinLevel15(),
                17: GloryPaladinLevel17(),
                20: GloryPaladinLevel20(),
            },
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
    return character_sheet_data


if __name__ == "__main__":
    character_sheet_data = get_data()
    character_sheet_data.create_character_sheet()
