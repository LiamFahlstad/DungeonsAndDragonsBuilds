import CharacterSheetCreator
from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.BardBase import (
    BardLevel1,
    BardLevel2,
    BardLevel3,
    BardLevel4,
    BardLevel5,
    BardLevel6,
    BardLevel7,
    BardLevel8,
    BardLevel9,
    BardLevel10,
    BardLevel11,
    BardLevel12,
    BardLevel13,
    BardLevel14,
    BardLevel15,
    BardLevel16,
    BardLevel17,
    BardLevel18,
    BardLevel19,
    BardLevel20,
)
from CharacterConfigs.SubClasses.BardLore import (
    LoreBardLevel3,
    LoreBardLevel6,
    LoreBardLevel14,
    LoreBardStarterClassBuilder,
)
from Definitions import Ability, Skill
from Features import Backgrounds, EpicBoon, GeneralFeats, OriginFeats
from SpeciesConfigs import Gnome
from Spells.Definitions import (
    BardLevel0Spells,
    BardLevel1Spells,
    BardLevel2Spells,
    BardLevel3Spells,
    BardLevel4Spells,
    BardLevel5Spells,
    BardLevel6Spells,
    BardLevel7Spells,
    BardLevel8Spells,
    BardLevel9Spells,
    WizardLevel3Spells,
)
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import BardSkillsStatBlock


def get_data() -> CharacterSheetCreator.CharacterSheetData:
    bard_lore = LoreBardStarterClassBuilder(
        bard_level=20,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilitiesStatBlock(
            strength=8,
            dexterity=14,
            constitution=13,
            intelligence=10,
            wisdom=12,
            charisma=15,
        ),
        # Choose two skills to be proficient in
        bard_skills=BardSkillsStatBlock(
            proficiencies={
                Skill.PERFORMANCE: True,
                Skill.PERSUASION: True,
                Skill.DECEPTION: True,
            }
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.CHARISMA, 2),
                (Ability.DEXTERITY, 1),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.INSIGHT,
                Skill.PERCEPTION,
            ]
        ),
        add_default_equipment=True,
        origin_feat=OriginFeats.Tough(),
        armor=[],
        weapons=[],
        bard_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: BardLevel1(
                    cantrip_1=BardLevel0Spells.THUNDERCLAP,
                    cantrip_2=BardLevel0Spells.MAGE_HAND,
                    spell_1=BardLevel1Spells.HEALING_WORD,
                    spell_2=BardLevel1Spells.FAERIE_FIRE,
                    spell_3=BardLevel1Spells.ANIMAL_FRIENDSHIP,
                    spell_4=BardLevel1Spells.HEROISM,
                ),
                2: BardLevel2(
                    spell=BardLevel1Spells.CHARM_PERSON,
                    skill_1=Skill.PERFORMANCE,
                    skill_2=Skill.PERSUASION,
                ),
                3: BardLevel3(
                    spell=BardLevel1Spells.COMMAND,
                ),
                4: BardLevel4(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.CHARISMA, 1),
                            (Ability.DEXTERITY, 1),
                        ]
                    ),
                    cantrip=BardLevel0Spells.BLADE_WARD,
                    spell=BardLevel2Spells.AID,
                ),
                5: BardLevel5(
                    spell_1=BardLevel3Spells.BESTOW_CURSE,
                    spell_2=BardLevel3Spells.FEAR,
                ),
                6: BardLevel6(
                    spell=BardLevel3Spells.DISPEL_MAGIC,
                ),
                7: BardLevel7(
                    spell=BardLevel2Spells.LESSER_RESTORATION,
                ),
                8: BardLevel8(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.DEXTERITY, 2),
                        ]
                    ),
                    spell=BardLevel4Spells.FREEDOM_OF_MOVEMENT,
                ),
                9: BardLevel9(
                    spell_1=BardLevel5Spells.ALUSTRIELS_MOONCLOAK,
                    spell_2=BardLevel5Spells.GEAS,
                    skill_1=Skill.STEALTH,
                    skill_2=Skill.PERCEPTION,
                ),
                10: BardLevel10(
                    cantrip=BardLevel0Spells.VICIOUS_MOCKERY,
                    spell=BardLevel5Spells.LEGEND_LORE,
                ),
                11: BardLevel11(
                    spell=BardLevel6Spells.TRUE_SEEING,
                ),
                12: BardLevel12(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.CHARISMA, 1),
                            (Ability.CONSTITUTION, 1),
                        ]
                    ),
                ),
                13: BardLevel13(
                    spell=BardLevel7Spells.MORDENKAINENS_SWORD,
                ),
                14: BardLevel14(),
                15: BardLevel15(
                    spell=BardLevel7Spells.REGENERATE,
                ),
                16: BardLevel16(
                    general_feat=GeneralFeats.WarCaster(
                        character_level=16,
                        ability=Ability.CHARISMA,
                    ),
                ),
                17: BardLevel17(
                    spell=BardLevel9Spells.PRISMATIC_WALL,
                ),
                19: BardLevel19(
                    epic_boon=EpicBoon.DummyEpicBoon(),
                    spell=BardLevel8Spells.BEFUDDLEMENT,
                ),
                18: BardLevel18(
                    spell=BardLevel9Spells.TRUE_POLYMORPH,
                ),
                20: BardLevel20(
                    spell=BardLevel9Spells.FORESIGHT,
                ),
            },
            subclass_features_by_level={
                3: LoreBardLevel3(
                    skill_1=Skill.STEALTH,
                    skill_2=Skill.SLEIGHT_OF_HAND,
                    skill_3=Skill.ACROBATICS,
                ),
                6: LoreBardLevel6(
                    spell=WizardLevel3Spells.FIREBALL,
                ),
                14: LoreBardLevel14(),
            },
        ),
        replace_spells={},
    )

    species_data = Gnome.forest_gnome_character_data(
        spell_casting_ability=Ability.CHARISMA
    )
    character_class_data = bard_lore.create()

    character_sheet_data = CharacterSheetCreator.CharacterSheetData()

    character_sheet_data.character_name = "Optimized Lore Bard"
    character_sheet_data.merge_with(character_class_data)
    character_sheet_data.merge_with(species_data)
    return character_sheet_data


if __name__ == "__main__":
    character_sheet_data = get_data()
    character_sheet_data.create_character_sheet()
