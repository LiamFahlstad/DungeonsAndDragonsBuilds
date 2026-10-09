from Core.Definitions import Ability
from CharacterContent.Features.SpeciesFeatures import AasimarFeatures
from CharacterContent.Species.SpeciesBuilder import SpeciesBuilder, SpeciesGrants
from CharacterContent.Spells.SpellLists import SorcererLevel0Spells


class AasimarSpeciesBuilder(SpeciesBuilder):
    def __init__(self):
        super().__init__(
            name="Aasimar",
        )

    def _grant(self, data: SpeciesGrants) -> None:
        data.base_speed = AasimarFeatures.SPEED  # Given by your species
        data.size = AasimarFeatures.SIZE  # Given by your species

        data.add_feature(AasimarFeatures.Darkvision())
        data.add_feature(AasimarFeatures.CelestialResistance())
        data.add_feature(AasimarFeatures.LightBearer())
        data.add_cantrip(SorcererLevel0Spells.LIGHT, Ability.CHARISMA)
        data.add_feature(AasimarFeatures.HealingHands())
        if data.character_level >= 3:
            data.add_feature(AasimarFeatures.CelestialRevelation())
