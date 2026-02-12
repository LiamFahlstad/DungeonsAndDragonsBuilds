import CharacterSheetCreator
from Features.SpeciesFeatures import DragonbornFeatures
from SpeciesConfigs.SpeciesBuilder import SpeciesBuilder


class DragonbornSpeciesBuilder(SpeciesBuilder):
    def __init__(
        self,
        dragon_ancestry_color: DragonbornFeatures.DragonColor,
    ):
        self.dragon_ancestry_color = dragon_ancestry_color
        super().__init__(
            name="Dragonborn",
        )

    def build(self) -> CharacterSheetCreator.CharacterSheetData:
        data = CharacterSheetCreator.CharacterSheetData()

        data.speed = DragonbornFeatures.SPEED  # Given by your species
        data.size = DragonbornFeatures.SIZE  # Given by your species

        data.add_feature(DragonbornFeatures.Darkvision())
        data.add_feature(DragonbornFeatures.BreathWeapon(self.dragon_ancestry_color))
        data.add_feature(
            DragonbornFeatures.DamageResistance(self.dragon_ancestry_color)
        )
        data.add_feature(DragonbornFeatures.DraconicFlight())

        return data
