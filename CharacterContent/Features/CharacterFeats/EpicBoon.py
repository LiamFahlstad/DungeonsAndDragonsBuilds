from CharacterContent.Features.Core.BaseFeatures import Feature
from Model.Records.GrantStamp import GrantStamp
from Model.View import CharacterView


class EpicBoon(Feature):
    # A feat can be taken once, unless it says it's Repeatable (see
    # Character._validate_feats_taken_once).
    repeatable = False

    labeled_by_class_level = True


class DummyEpicBoon(EpicBoon):
    def __init__(self):
        super().__init__(name="Epic Boon", origin="Epic Boon Feature")

    def get_description(self, character: CharacterView) -> str:
        return "This is a dummy epic boon for testing purposes."
