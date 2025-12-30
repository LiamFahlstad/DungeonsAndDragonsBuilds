from CharacterConfigs.CharacterClasses import (
    ClassBuilder,
    RogueBase,
    RogueLevelFeatures,
)
from CharacterConfigs import RogueAssassin
from CharacterConfigs.CharacterClasses import WizardBase, WizardLevelFeatures
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
from CharacterConfigs.CharacterClasses import RogueBase
from CharacterConfigs.RogueAssassin import (
    AssassinRogueLevel3,
    AssassinRogueLevel9,
)
import Spells.Definitions as SpellDefinitions


def _get_starter_data() -> CharacterSheetCreator.CharacterSheetData:
    rogue_assassin = RogueAssassin.AssassinRogueStarterClassBuilder(
        rogue_level=3,
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
        rogue_skills=RogueSkillsStatBlock(
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
        rogue_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: RogueLevelFeatures.RogueLevel1(
                    skill_1=Definitions.Skill.STEALTH,
                    skill_2=Definitions.Skill.SLEIGHT_OF_HAND,
                    weapon_mastery_1=Weapons.Shortsword(),
                    weapon_mastery_2=Weapons.Scimitar(),
                ),
                2: RogueLevelFeatures.RogueLevel2(),
                3: RogueLevelFeatures.RogueLevel3(),
            },
            subclass_features_by_level={},
        ),
    )

    character_class_data = rogue_assassin.create()
    return character_class_data


def _get_multiclass_data() -> CharacterSheetCreator.CharacterSheetData:
    wizard_multiclass = WizardBase.WizardMulticlassBuilder(
        wizard_level=1,
        subclass=Definitions.WizardSubclass.BLADESINGER,
        wizard_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: WizardLevelFeatures.WizardLevel1(
                    cantrip_1=SpellDefinitions.WizardLevel0Spells.MAGE_HAND,
                    cantrip_2=SpellDefinitions.WizardLevel0Spells.BLADE_WARD,
                    cantrip_3=SpellDefinitions.WizardLevel0Spells.TRUE_STRIKE,
                    spell_1=SpellDefinitions.WizardLevel1Spells.SHIELD,
                    spell_2=SpellDefinitions.WizardLevel1Spells.MAGIC_MISSILE,
                    spell_3=SpellDefinitions.WizardLevel1Spells.DETECT_MAGIC,
                    spell_4=SpellDefinitions.WizardLevel1Spells.FEATHER_FALL,
                ),
            },
            subclass_features_by_level={},
        ),
    )

    character_class_data = wizard_multiclass.create()
    return character_class_data


def _get_species_data(
    character_level: int, spell_casting_ability: Ability
) -> CharacterSheetCreator.CharacterSheetData:

    species_data = Elf.elf_character_data(
        character_level=character_level,
        elven_lineage=Elf.ElvenLineage.WOOD_ELF,
        skill_proficiency=Definitions.Skill.PERCEPTION,
        spell_casting_ability=spell_casting_ability,
    )
    return species_data


def calculate_ability_with_highest_modifier(
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


def get_data() -> CharacterSheetCreator.CharacterSheetData:

    character_class_data = _get_starter_data()
    character_class_data.merge_with(_get_multiclass_data())

    abilities = character_class_data.abilities
    if abilities is None:
        raise ValueError("AbilitiesStatBlock is None.")
    ability_with_highest_modifier = calculate_ability_with_highest_modifier(abilities)
    character_class_data.spell_casting_ability = ability_with_highest_modifier
    species_data = _get_species_data(
        character_level=character_class_data.character_level,
        spell_casting_ability=ability_with_highest_modifier,
    )
    character_sheet_data = CharacterSheetCreator.CharacterSheetData()
    character_sheet_data.character_name = "Multiclass Test Character"
    character_sheet_data.merge_with(character_class_data)
    character_sheet_data.merge_with(species_data)
    return character_sheet_data


if __name__ == "__main__":
    character_sheet_data = get_data()
    character_sheet_data.create_character_sheet()
