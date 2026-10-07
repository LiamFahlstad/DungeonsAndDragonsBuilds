"""Effect: anything that records into a character's Ledger - a feature, an
item, a fighting style, or one improvement granted on its own
(Character.add_effect)."""

from abc import ABC, abstractmethod

from Model.Effects import Effects


class Effect(ABC):
    @abstractmethod
    def apply(self, effects: Effects) -> None:
        """Record this effect's facts. Effects apply in no particular order, so
        only record - never read a stat (see Model/Effects.py)."""
