from Features.BaseFeatures import CharacterFeature, TextFeature
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class EpicBoonCharacterFeature(CharacterFeature):
    pass


class EpicBoonTextFeature(TextFeature):
    pass


EpicBoon = EpicBoonCharacterFeature | EpicBoonTextFeature


class DummyEpicBoon(EpicBoonTextFeature):
    def __init__(self):
        super().__init__(name="Epic Boon", origin="Epic Boon Feature")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "This is a dummy epic boon for testing purposes."
