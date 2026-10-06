from CharacterContent.Features.Core.BaseFeatures import Feature
from Model.Character import Character, GrantStamp


class EpicBoon(Feature):
    def _label_for(self, stamp: GrantStamp) -> str:
        """Taken at a class level, it's labeled with that level ("Fighter
        Level 8"); its own origin only says when it's available."""
        if stamp.kind in ("class", "subclass"):
            return f"{stamp.granted_by} Level {stamp.level}"
        return super()._label_for(stamp)


class DummyEpicBoon(EpicBoon):
    def __init__(self):
        super().__init__(name="Epic Boon", origin="Epic Boon Feature")

    def get_description(self, character: Character) -> str:
        return "This is a dummy epic boon for testing purposes."
