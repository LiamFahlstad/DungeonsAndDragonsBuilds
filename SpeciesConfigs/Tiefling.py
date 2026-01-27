from enum import Enum

import CharacterSheetCreator
from Features import OriginFeats
from Features.SpeciesFeatures import TieflingFeatures
from SpeciesConfigs.SpeciesBuilder import SpeciesBuilder
from Spells.Definitions import (
    ClericLevel2Spells,
    SorcererLevel0Spells,
    SorcererLevel1Spells,
    WarlockLevel1Spells,
    WizardLevel2Spells,
)


class FiendishLineage(str, Enum):
    ABYSSAL = "Abyssal"
    Chthonic = "Chthonic"
    Infernal = "Infernal"


class TieflingSpeciesBuilder(SpeciesBuilder):
    def __init__(
        self,
        origin_feat: OriginFeats.OriginFeat,
        character_level: int,
        fiendish_lineage: FiendishLineage,
    ):
        self.origin_feat = origin_feat
        self.character_level = character_level
        self.fiendish_lineage = fiendish_lineage
        super().__init__(
            name="Tiefling",
        )

    def build(self) -> CharacterSheetCreator.CharacterSheetData:
        data = CharacterSheetCreator.CharacterSheetData()

        data.speed = TieflingFeatures.SPEED  # Given by your species
        data.size = TieflingFeatures.SIZE  # Given by your species
        data.add_feature(self.origin_feat)

        data.add_feature(TieflingFeatures.Darkvision(60))
        data.add_feature(TieflingFeatures.OtherworldlyPresence())

        cantrip = ""
        spell_1 = ""
        spell_2 = ""
        if self.fiendish_lineage == FiendishLineage.ABYSSAL:
            cantrip = SorcererLevel0Spells.POISON_SPRAY
            if self.character_level >= 3:
                spell_1 = SorcererLevel1Spells.RAY_OF_SICKNESS
            if self.character_level >= 5:
                spell_2 = ClericLevel2Spells.HOLD_PERSON

        elif self.fiendish_lineage == FiendishLineage.Chthonic:
            cantrip = SorcererLevel0Spells.CHILL_TOUCH
            if self.character_level >= 3:
                spell_1 = SorcererLevel1Spells.FALSE_LIFE
            if self.character_level >= 5:
                spell_2 = WizardLevel2Spells.RAY_OF_ENFEEBLEMENT

        elif self.fiendish_lineage == FiendishLineage.Infernal:
            cantrip = SorcererLevel0Spells.FIRE_BOLT
            if self.character_level >= 3:
                spell_1 = WarlockLevel1Spells.HELLISH_REBUKE
            if self.character_level >= 5:
                spell_2 = WizardLevel2Spells.DARKNESS

        data.add_cantrip(cantrip)
        data.add_spell(spell_1)
        data.add_spell(spell_2)
        data.add_feature(
            TieflingFeatures.FiendishLegacy(
                cantrip=cantrip, spell_1=spell_1, spell_2=spell_2
            )
        )
        return data
