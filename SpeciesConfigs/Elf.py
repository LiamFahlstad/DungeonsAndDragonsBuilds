from enum import Enum

import CharacterSheetCreator
import Definitions
from Features.SpeciesFeatures import ElfFeatures
from SpeciesConfigs.SpeciesBuilder import SpeciesBuilder
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


class ElfSpeciesBuilder(SpeciesBuilder):
    def __init__(
        self,
        elven_lineage: ElvenLineage,
        skill_proficiency: Definitions.Skill,
    ):
        self.elven_lineage = elven_lineage
        self.skill_proficiency = skill_proficiency
        self.character_level = None
        self.spell_casting_ability = None
        super().__init__(
            name="Elf",
        )

    def build(self) -> CharacterSheetCreator.CharacterSheetData:
        if self.character_level is None:
            raise ValueError(
                "Character level must be set before building species data."
            )

        if self.spell_casting_ability is None:
            raise ValueError(
                "Spell casting ability must be set before building species data."
            )

        data = CharacterSheetCreator.CharacterSheetData()

        data.speed = ElfFeatures.SPEED  # Given by your species
        data.size = ElfFeatures.SIZE  # Given by your species

        data.add_feature(ElfFeatures.FeyAncestry())
        data.add_feature(ElfFeatures.KeenSenses(self.skill_proficiency))
        data.add_feature(ElfFeatures.Trance())

        if self.elven_lineage == ElvenLineage.DROW:
            data.add_feature(ElfFeatures.Darkvision(120))
            data.add_cantrip(
                BardLevel0Spells.DANCING_LIGHTS, self.spell_casting_ability
            )
            if self.character_level >= 3:
                data.add_spell(
                    DruidLevel1Spells.FAERIE_FIRE, self.spell_casting_ability
                )
            if self.character_level >= 5:
                data.add_spell(WarlockLevel2Spells.DARKNESS, self.spell_casting_ability)

        elif self.elven_lineage == ElvenLineage.HIGH_ELF:
            data.add_feature(ElfFeatures.Darkvision(60))
            data.add_cantrip(
                SorcererLevel0Spells.PRESTIDIGITATION, self.spell_casting_ability
            )
            if self.character_level >= 3:
                data.add_spell(
                    ClericLevel1Spells.DETECT_MAGIC, self.spell_casting_ability
                )
            if self.character_level >= 5:
                data.add_spell(
                    WarlockLevel2Spells.MISTY_STEP, self.spell_casting_ability
                )

        elif self.elven_lineage == ElvenLineage.WOOD_ELF:
            data.add_feature(ElfFeatures.Darkvision(60))
            data.add_cantrip(DruidLevel0Spells.DRUIDCRAFT, self.spell_casting_ability)
            data.speed = 35
            if self.character_level >= 3:
                data.add_spell(
                    WizardLevel1Spells.LONGSTRIDER, self.spell_casting_ability
                )
            if self.character_level >= 5:
                data.add_spell(
                    DruidLevel2Spells.PASS_WITHOUT_TRACE, self.spell_casting_ability
                )

        elif self.elven_lineage == ElvenLineage.LORWYN_ELF:
            data.add_feature(ElfFeatures.Darkvision(60))
            data.add_cantrip(DruidLevel0Spells.THORN_WHIP, self.spell_casting_ability)
            if self.character_level >= 3:
                data.add_spell(ClericLevel1Spells.COMMAND, self.spell_casting_ability)
            if self.character_level >= 5:
                data.add_spell(ClericLevel2Spells.SILENCE, self.spell_casting_ability)

        elif self.elven_lineage == ElvenLineage.SHADOWMOOR_ELF:
            data.add_feature(ElfFeatures.Darkvision(120))
            data.add_cantrip(DruidLevel0Spells.STARRY_WISP, self.spell_casting_ability)
            if self.character_level >= 3:
                data.add_spell(BardLevel1Spells.HEROISM, self.spell_casting_ability)
            if self.character_level >= 5:
                data.add_spell(
                    WizardLevel2Spells.GENTLE_REPOSE, self.spell_casting_ability
                )
        return data
