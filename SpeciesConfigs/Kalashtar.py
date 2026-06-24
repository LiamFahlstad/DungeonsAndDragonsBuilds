import CharacterSheetCreator
from Definitions import CreatureSize
from Features.SpeciesFeatures import KalashtarFeatures
from SpeciesConfigs.SpeciesBuilder import SpeciesBuilder


class KalashtarSpeciesBuilder(SpeciesBuilder):
    def __init__(self):
        super().__init__(
            name="Kalashtar",
        )

    def build(self) -> CharacterSheetCreator.CharacterSheetData:
        data = CharacterSheetCreator.CharacterSheetData()

        data.speed = KalashtarFeatures.SPEED  # Given by your species
        data.size = CreatureSize.MEDIUM  # Given by your species

        data.add_feature(KalashtarFeatures.DualMind())
        data.add_feature(KalashtarFeatures.MentalDiscipline())
        data.add_feature(KalashtarFeatures.MindLink())
        data.add_feature(KalashtarFeatures.SeveredFromDreams())

        return data
