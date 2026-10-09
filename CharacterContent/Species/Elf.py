from enum import Enum

import Core.Definitions as Definitions
from CharacterContent.Features.SpeciesFeatures import ElfFeatures
from CharacterContent.Species.SpeciesBuilder import SpeciesBuilder, SpeciesGrants
from CharacterContent.Spells.SpellLists import (
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
        super().__init__(
            name="Elf",
        )

    def _grant(self, data: SpeciesGrants) -> None:
        data.base_speed = ElfFeatures.SPEED  # Given by your species
        data.size = ElfFeatures.SIZE  # Given by your species

        data.add_feature(ElfFeatures.FeyAncestry())
        data.add_feature(ElfFeatures.KeenSenses(self.skill_proficiency))
        data.add_feature(ElfFeatures.Trance())

        additional_ruling = "You always have that spell prepared. You can cast it once without a spell slot, and you regain the ability to cast it in that way when you finish a Long Rest. You can also cast the spell using any spell slots you have of the appropriate level."

        if self.elven_lineage == ElvenLineage.DROW:
            data.add_feature(ElfFeatures.Darkvision(120))
            data.add_cantrip(
                BardLevel0Spells.DANCING_LIGHTS, data.spell_casting_ability
            )
            if data.character_level >= 3:
                data.add_spell(
                    DruidLevel1Spells.FAERIE_FIRE,
                    data.spell_casting_ability,
                    additional_ruling,
                )
            if data.character_level >= 5:
                data.add_spell(
                    WarlockLevel2Spells.DARKNESS,
                    data.spell_casting_ability,
                    additional_ruling,
                )

        elif self.elven_lineage == ElvenLineage.HIGH_ELF:
            data.add_feature(ElfFeatures.Darkvision(60))
            data.add_cantrip(
                SorcererLevel0Spells.PRESTIDIGITATION, data.spell_casting_ability
            )

            if data.character_level >= 3:
                data.add_spell(
                    ClericLevel1Spells.DETECT_MAGIC,
                    data.spell_casting_ability,
                    additional_ruling,
                )
            if data.character_level >= 5:
                data.add_spell(
                    WarlockLevel2Spells.MISTY_STEP,
                    data.spell_casting_ability,
                    additional_ruling,
                )

        elif self.elven_lineage == ElvenLineage.WOOD_ELF:
            data.add_feature(ElfFeatures.Darkvision(60))
            data.add_cantrip(DruidLevel0Spells.DRUIDCRAFT, data.spell_casting_ability)
            data.base_speed = 35
            if data.character_level >= 3:
                data.add_spell(
                    WizardLevel1Spells.LONGSTRIDER,
                    data.spell_casting_ability,
                    additional_ruling,
                )
            if data.character_level >= 5:
                data.add_spell(
                    DruidLevel2Spells.PASS_WITHOUT_TRACE,
                    data.spell_casting_ability,
                    additional_ruling,
                )

        elif self.elven_lineage == ElvenLineage.LORWYN_ELF:
            data.add_feature(ElfFeatures.Darkvision(60))
            data.add_cantrip(DruidLevel0Spells.THORN_WHIP, data.spell_casting_ability)
            if data.character_level >= 3:
                data.add_spell(
                    ClericLevel1Spells.COMMAND,
                    data.spell_casting_ability,
                    additional_ruling,
                )
            if data.character_level >= 5:
                data.add_spell(
                    ClericLevel2Spells.SILENCE,
                    data.spell_casting_ability,
                    additional_ruling,
                )

        elif self.elven_lineage == ElvenLineage.SHADOWMOOR_ELF:
            data.add_feature(ElfFeatures.Darkvision(120))
            data.add_cantrip(DruidLevel0Spells.STARRY_WISP, data.spell_casting_ability)
            if data.character_level >= 3:
                data.add_spell(
                    BardLevel1Spells.HEROISM,
                    data.spell_casting_ability,
                    additional_ruling,
                )
            if data.character_level >= 5:
                data.add_spell(
                    WizardLevel2Spells.GENTLE_REPOSE,
                    data.spell_casting_ability,
                    additional_ruling,
                )
