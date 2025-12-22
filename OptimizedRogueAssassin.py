from CharacterConfigs.Bases.RogueBase import (
    RogueLevel1,
    RogueLevel10,
    RogueLevel11,
    RogueLevel12,
    RogueLevel13,
    RogueLevel14,
    RogueLevel15,
    RogueLevel16,
    RogueLevel17,
    RogueLevel18,
    RogueLevel19,
    RogueLevel2,
    RogueLevel20,
    RogueLevel3,
    RogueLevel4,
    RogueLevel5,
    RogueLevel6,
    RogueLevel7,
    RogueLevel8,
    RogueLevel9,
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
from SpeciesConfigs import Elf
from StatBlocks import AbilitiesStatBlock
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import RogueSkillsStatBlock
from CharacterConfigs.Bases import RogueBase
from CharacterConfigs.RogueAssassin import (
    AssassinRogueLevel3,
    AssassinRogueLevel9,
)


def get_data() -> CharacterSheetCreator.CharacterSheetData:
    rogue_assassin = RogueBase.RogueStarter(
        rogue_level=3,
        subclass=Definitions.RogueSubclass.ASSASSIN,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilitiesStatBlock(
            strength=8,
            dexterity=15,
            constitution=14,
            intelligence=13,
            wisdom=12,
            charisma=10,
        ),
        # Choose two skills to be proficient in
        skills=RogueSkillsStatBlock(
            proficiencies={
                Skill.ACROBATICS: True,
                Skill.ATHLETICS: False,
                Skill.DECEPTION: False,
                Skill.INSIGHT: False,
                Skill.INTIMIDATION: False,
                Skill.INVESTIGATION: True,
                Skill.PERCEPTION: False,
                Skill.SLEIGHT_OF_HAND: True,
                Skill.STEALTH: True,
            }
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.CONSTITUTION, 2),
                (Ability.DEXTERITY, 1),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.NATURE,
                Skill.DECEPTION,
            ]
        ),
        add_default_equipment=True,
        origin_feat=OriginFeats.Alert(),
        weapons=[],
        armor=[],
        rogue_feature_per_level=RogueBase.RogueFeaturePerLevel(
            rogue_level_1=RogueLevel1(
                skill_1=Definitions.Skill.STEALTH,
                skill_2=Definitions.Skill.SLEIGHT_OF_HAND,
                weapon_mastery_1=Weapons.Shortsword(),
                weapon_mastery_2=Weapons.Scimitar(),
            ),
            rogue_level_2=RogueLevel2(),
            rogue_level_3=RogueLevel3(),
            # rogue_level_4=RogueLevel4(
            #     general_feat=GeneralFeats.AbilityScoreImprovement(
            #         [
            #             (Ability.CONSTITUTION, 2),
            #         ]
            #     ),
            #     spell=RogueLevel1Spells.CURE_WOUNDS,
            # ),
            # rogue_level_5=RogueLevel5(
            #     spell=RogueLevel2Spells.ZONE_OF_TRUTH,
            # ),
            # rogue_level_6=RogueLevel6(),
            # rogue_level_7=RogueLevel7(
            #     spell=RogueLevel2Spells.LESSER_RESTORATION,
            # ),
            # rogue_level_8=RogueLevel8(
            #     general_feat=GeneralFeats.AbilityScoreImprovement(
            #         [
            #             (Ability.STRENGTH, 2),
            #         ]
            #     ),
            # ),
            # rogue_level_9=RogueLevel9(
            #     spell=RogueLevel3Spells.AURA_OF_VITALITY,
            # ),
            # rogue_level_10=RogueLevel10(),
            # rogue_level_11=RogueLevel11(
            #     spell=RogueLevel3Spells.BLINDING_SMITE,
            # ),
            # rogue_level_12=RogueLevel12(
            #     general_feat=GeneralFeats.AbilityScoreImprovement(
            #         [
            #             (Ability.CHARISMA, 2),
            #         ]
            #     ),
            # ),
            # rogue_level_13=RogueLevel13(
            #     spell=RogueLevel4Spells.DEATH_WARD,
            # ),
            # rogue_level_14=RogueLevel14(),
            # rogue_level_15=RogueLevel15(
            #     spell=RogueLevel4Spells.AURA_OF_PURITY,
            # ),
            # rogue_level_16=RogueLevel16(
            #     general_feat=GeneralFeats.AbilityScoreImprovement(
            #         [
            #             (Ability.CHARISMA, 2),
            #         ]
            #     ),
            # ),
            # rogue_level_17=RogueLevel17(
            #     spell_1=RogueLevel5Spells.BANISHING_SMITE,
            #     spell_2=RogueLevel5Spells.GEAS,
            # ),
            # rogue_level_19=RogueLevel19(
            #     spell=RogueLevel5Spells.CIRCLE_OF_POWER,
            # ),
            # rogue_level_18=RogueLevel18(),
            # rogue_level_20=RogueLevel20(),
            rogue_subclass_level_3=AssassinRogueLevel3(),
            # rogue_subclass_level_5=AssassinRogueLevel5(),
            # rogue_subclass_level_7=AssassinRogueLevel7(),
            # rogue_subclass_level_9=AssassinRogueLevel9(),
            # rogue_subclass_level_13=AssassinRogueLevel13(),
            # rogue_subclass_level_15=AssassinRogueLevel15(),
            # rogue_subclass_level_17=AssassinRogueLevel17(),
            # rogue_subclass_level_20=AssassinRogueLevel20(),
        ),
        # replace_spells={
        #     RogueLevel1Spells.CURE_WOUNDS: RogueLevel2Spells.MAGIC_WEAPON,
        # },
    )

    character_class_data = rogue_assassin.create()

    def ability_with_highest_modifier(
        abilities: AbilitiesStatBlock.AbilitiesStatBlock,
    ) -> Definitions.Ability:
        highest_ability = None
        highest_modifier = -999
        for ability in [
            Definitions.Ability.INTELLIGENCE,
            Definitions.Ability.WISDOM,
            Definitions.Ability.CHARISMA,
        ]:
            modifier = abilities.get_modifier(ability)
            if modifier > highest_modifier:
                highest_modifier = modifier
                highest_ability = ability
        if highest_ability is None:
            raise ValueError("No abilities found.")
        return highest_ability

    abilities = character_class_data.abilities
    if abilities is None:
        raise ValueError("AbilitiesStatBlock is None.")

    spell_casting_ability = ability_with_highest_modifier(abilities)
    character_class_data.spell_casting_ability = spell_casting_ability
    species_data = Elf.elf_character_data(
        character_level=character_class_data.character_level,
        elven_lineage=Elf.ElvenLineage.WOOD_ELF,
        skill_proficiency=Definitions.Skill.PERCEPTION,
        spell_casting_ability=spell_casting_ability,
    )
    character_sheet_data = CharacterSheetCreator.CharacterSheetData()

    character_sheet_data.character_name = "Dark Shadow Nightmare"
    character_sheet_data.merge_with(character_class_data)
    character_sheet_data.merge_with(species_data)
    return character_sheet_data


if __name__ == "__main__":
    character_sheet_data = get_data()
    character_sheet_data.create_character_sheet()
