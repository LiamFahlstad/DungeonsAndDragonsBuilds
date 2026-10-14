"""FightingStyle: the base of every fighting style (CharacterContent/Features/
CombatFeatures/FightingStyles.py)."""

from abc import abstractmethod

from Model.Content.Effect import Effect
from Model.Content.FeatureText import Block
from Model.Ledger.LedgerWriter import LedgerWriter


class FightingStyle(Effect):
    """A fighting style is a feature that modifies a character's combat abilities.
    Each one sets `name` (e.g. "Archery")."""

    @abstractmethod
    def description(self) -> str:
        pass

    def get_improved_description(self) -> "list[Block] | None":
        """Override to give the card a clearer layout of the same rules as
        description(), like Feature.get_improved_description (see
        Model/Content/FeatureText.py). The sheet shows it instead of
        description() unless RunCharacterCreator.py --source-text is set.
        Return None (default) to show description()."""
        return None

    def apply(self, ledger_writer: LedgerWriter) -> None:
        """Most fighting styles only describe what they do at the table and
        record nothing; FightStyleModifier is the kind with a computed
        effect."""
