from enum import Enum
import CharacterSheetCreator
import Definitions
from Features import ElfFeatures
from Features import OriginFeats
from Spells.Definitions import (
    BardLevel0Spells,
    BardLevel1Spells,
    ClericLevel1Spells,
    ClericLevel2Spells,
    DruidLevel0Spells,
    DruidLevel1Spells,
    DruidLevel2Spells,
    SorcererLevel0Spells,
    WarlockLevel2Spells,
    WizardLevel1Spells,
    WizardLevel2Spells,
)


class ElvenLineage(str, Enum):
    HIGH_ELF = "High Elf"
    WOOD_ELF = "Wood Elf"
    DROW = "Drow"
    LORWYN_ELF = "Lorwyn Elf"
    SHADOWMOOR_ELF = "Shadowmoor Elf"


def forest_Elf_character_data(
    character_level: int,
    elven_lineage: ElvenLineage,
    skill_proficiency: Definitions.Skill,
    origin_feat: OriginFeats.OriginCharacterFeat | OriginFeats.OriginTextFeat,
) -> CharacterSheetCreator.CharacterSheetData:

    data = CharacterSheetCreator.CharacterSheetData()

    data.speed = ElfFeatures.SPEED  # Given by your species
    data.size = ElfFeatures.SIZE  # Given by your species
    data.add_feature(origin_feat)

    data.add_feature(ElfFeatures.FeyAncestry())
    data.add_feature(ElfFeatures.KeenSenses(skill_proficiency))
    data.add_feature(ElfFeatures.Trance())

    if elven_lineage == ElvenLineage.DROW:
        data.add_feature(ElfFeatures.Darkvision(120))
        data.add_cantrip(BardLevel0Spells.DANCING_LIGHTS)
        if character_level >= 3:
            data.add_spell(DruidLevel1Spells.FAERIE_FIRE)
        if character_level >= 5:
            data.add_spell(WarlockLevel2Spells.DARKNESS)

    elif elven_lineage == ElvenLineage.HIGH_ELF:
        data.add_feature(ElfFeatures.Darkvision(60))
        data.add_cantrip(SorcererLevel0Spells.PRESTIDIGITATION)
        if character_level >= 3:
            data.add_spell(ClericLevel1Spells.DETECT_MAGIC)
        if character_level >= 5:
            data.add_spell(WarlockLevel2Spells.MISTY_STEP)

    elif elven_lineage == ElvenLineage.WOOD_ELF:
        data.add_feature(ElfFeatures.Darkvision(60))
        data.add_cantrip(DruidLevel0Spells.DRUIDCRAFT)
        data.speed = 35
        if character_level >= 3:
            data.add_spell(WizardLevel1Spells.LONGSTRIDER)
        if character_level >= 5:
            data.add_spell(DruidLevel2Spells.PASS_WITHOUT_TRACE)

    elif elven_lineage == ElvenLineage.LORWYN_ELF:
        data.add_feature(ElfFeatures.Darkvision(60))
        data.add_cantrip(DruidLevel0Spells.THORN_WHIP)
        if character_level >= 3:
            data.add_spell(ClericLevel1Spells.COMMAND)
        if character_level >= 5:
            data.add_spell(ClericLevel2Spells.SILENCE)

    elif elven_lineage == ElvenLineage.SHADOWMOOR_ELF:
        data.add_feature(ElfFeatures.Darkvision(120))
        data.add_cantrip(DruidLevel0Spells.STARRY_WISP)
        if character_level >= 3:
            data.add_spell(BardLevel1Spells.HEROISM)
        if character_level >= 5:
            data.add_spell(WizardLevel2Spells.GENTLE_REPOSE)
    return data
