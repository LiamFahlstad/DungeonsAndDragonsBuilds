"""Effect: anything that records into a character's Ledger - a feature, an
item, a fighting style, or one improvement granted on its own
(Character.add_effect)."""

from abc import ABC, abstractmethod

from Model.Ledger.LedgerWriter import LedgerWriter


class Effect(ABC):
    # What everything this effect records is listed under ("Darkvision",
    # "Ring of Investigation"): the Character hands apply() a LedgerWriter
    # labeled with it.
    name: str

    @abstractmethod
    def apply(self, effects: LedgerWriter) -> None:
        """Record this effect's facts. Effects apply in no particular order, so
        only record - never read a stat (see Model/Ledger/LedgerWriter.py)."""
