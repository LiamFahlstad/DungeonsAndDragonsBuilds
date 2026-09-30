from CharacterContent.Features.Core.BaseFeatures import Feature
from Model.Character import Character


class EpicBoon(Feature):
    pass


class DummyEpicBoon(EpicBoon):
    def __init__(self):
        super().__init__(name="Epic Boon", origin="Epic Boon Feature")

    def get_description(self, character: Character) -> str:
        return "This is a dummy epic boon for testing purposes."
