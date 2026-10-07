"""FightingStyle: the base of every fighting style (CharacterContent/Features/
CombatFeatures/FightingStyles.py)."""

from abc import abstractmethod

from Model.Content.Effect import Effect
from Model.Effects import Effects


class FightingStyle(Effect):
    """A fighting style is a feature that modifies a character's combat abilities."""

    @abstractmethod
    def description(self) -> str:
        pass

    def apply(self, effects: Effects) -> None:
        """Most fighting styles only describe what they do at the table and
        record nothing; FightStyleModifier is the kind with a computed
        effect."""
