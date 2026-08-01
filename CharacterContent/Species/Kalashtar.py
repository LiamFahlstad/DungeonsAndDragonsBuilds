from Builds import CharacterSheetAccumulator
from Core.Definitions import CreatureSize
from CharacterContent.Features.SpeciesFeatures import KalashtarFeatures
from CharacterContent.Species.SpeciesBuilder import SpeciesBuilder


class KalashtarSpeciesBuilder(SpeciesBuilder):
    def __init__(self):
        super().__init__(
            name="Kalashtar",
        )

    def build(self) -> CharacterSheetAccumulator.CharacterSheetData:
        data = CharacterSheetAccumulator.CharacterSheetData()

        data.speed = KalashtarFeatures.SPEED  # Given by your species
        data.size = CreatureSize.MEDIUM  # Given by your species

        data.add_feature(KalashtarFeatures.DualMind())
        data.add_feature(KalashtarFeatures.MentalDiscipline())
        data.add_feature(KalashtarFeatures.MindLink())
        data.add_feature(KalashtarFeatures.SeveredFromDreams())

        return data
