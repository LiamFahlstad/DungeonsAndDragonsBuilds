from CharacterContent.Features.Core.BaseFeatures import Feature
from Model.Character import Character
from Model.Records.GrantStamp import GrantStamp


class EpicBoon(Feature):
    # A feat can be taken once, unless it says it's Repeatable (see
    # Character._validate_feats_taken_once).
    repeatable = False

    labeled_by_class_level = True


class DummyEpicBoon(EpicBoon):
    def __init__(self):
        super().__init__(name="Epic Boon", origin="Epic Boon Feature")

    def get_description(self, character: Character) -> str:
        return "This is a dummy epic boon for testing purposes."
