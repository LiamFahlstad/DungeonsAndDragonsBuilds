from enum import Enum

from CharacterContent.Features.SpeciesFeatures import TieflingFeatures
from CharacterContent.Species.SpeciesBuilder import SpeciesBuilder, SpeciesGrants
from CharacterContent.Spells.SpellLists import (
    EnchantmentLevel2Spells,
    EvocationLevel0Spells,
    EvocationLevel1Spells,
    EvocationLevel2Spells,
    NecromancyLevel0Spells,
    NecromancyLevel1Spells,
    NecromancyLevel2Spells,
    TransmutationLevel0Spells,
)


class FiendishLineage(str, Enum):
    ABYSSAL = "Abyssal"
    CHTHONIC = "Chthonic"
    Infernal = "Infernal"


class TieflingSpeciesBuilder(SpeciesBuilder):
    def __init__(
        self,
        fiendish_lineage: FiendishLineage,
    ):
        self.fiendish_lineage = fiendish_lineage
        super().__init__(
            name="Tiefling",
        )

    def _grant(self, data: SpeciesGrants) -> None:
        data.base_speed = TieflingFeatures.SPEED  # Given by your species
        data.size = TieflingFeatures.SIZE  # Given by your species

        data.add_feature(TieflingFeatures.Darkvision(60))
        data.add_feature(TieflingFeatures.OtherworldlyPresence())
        data.add_cantrip(
            TransmutationLevel0Spells.THAUMATURGY, data.spell_casting_ability
        )

        spell_1 = None
        spell_2 = None

        if self.fiendish_lineage == FiendishLineage.ABYSSAL:
            cantrip = NecromancyLevel0Spells.POISON_SPRAY
            data.add_feature(TieflingFeatures.FiendishResistance("Poison"))
            if data.character_level >= 3:
                spell_1 = NecromancyLevel1Spells.RAY_OF_SICKNESS
            if data.character_level >= 5:
                spell_2 = EnchantmentLevel2Spells.HOLD_PERSON

        elif self.fiendish_lineage == FiendishLineage.CHTHONIC:
            cantrip = NecromancyLevel0Spells.CHILL_TOUCH
            data.add_feature(TieflingFeatures.FiendishResistance("Necrotic"))
            if data.character_level >= 3:
                spell_1 = NecromancyLevel1Spells.FALSE_LIFE
            if data.character_level >= 5:
                spell_2 = NecromancyLevel2Spells.RAY_OF_ENFEEBLEMENT

        elif self.fiendish_lineage == FiendishLineage.Infernal:
            cantrip = EvocationLevel0Spells.FIRE_BOLT
            data.add_feature(TieflingFeatures.FiendishResistance("Fire"))
            if data.character_level >= 3:
                spell_1 = EvocationLevel1Spells.HELLISH_REBUKE
            if data.character_level >= 5:
                spell_2 = EvocationLevel2Spells.DARKNESS

        else:
            raise ValueError(f"Invalid fiendish lineage: {self.fiendish_lineage}")

        data.add_cantrip(cantrip, data.spell_casting_ability)
        if spell_1 is not None:
            data.add_spell(spell_1, data.spell_casting_ability)
        if spell_2 is not None:
            data.add_spell(spell_2, data.spell_casting_ability)
        data.add_feature(
            TieflingFeatures.FiendishLegacy(
                cantrip=cantrip, spell_1=spell_1, spell_2=spell_2
            )
        )
