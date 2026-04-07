from abc import ABC, abstractmethod
from typing import Optional

from Items import Items


class ToolProficiency(ABC):
    def __init__(
        self,
        name: str,
        ability: str,
        weight: Optional[float],
        cost: int,
    ):
        self.name = name
        self.ability = ability
        self.weight = weight
        self.cost = cost

    @abstractmethod
    def description(self) -> str:
        pass


class NavigatorsTools(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Navigator's Tools",
            ability="Wisdom",
            weight=2.0,
            cost=25,
        )

    def description(self) -> str:
        return (
            "Utilize: Plot a course (DC 10), "
            "or determine position by stargazing (DC 15)."
        )


class PoisonersKit(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Poisoner's Kit",
            ability="Intelligence",
            weight=2.0,
            cost=50,
        )

    def description(self) -> str:
        return "Utilize: Detect a poisoned object (DC 10). " "Craft: Basic Poison."


class ThievesTools(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Thieves' Tools",
            ability="Dexterity",
            weight=1.0,
            cost=25,
        )

    def description(self) -> str:
        return "Utilize: Pick a lock (DC 15), " "or disarm a trap (DC 15)."


from typing import List


class HerbalismKit(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Herbalism Kit",
            ability="Intelligence",
            weight=3.0,
            cost=5,
        )

    def craftable_items(self) -> List[Items.Item]:
        return [
            Items.Antitoxin(),
            Items.Candle(),
            Items.HealersKit(),
            Items.PotionOfHealing(),
        ]

    def description(self) -> str:
        craftables = ", ".join(item.name for item in self.craftable_items())
        return "Utilize: Identify a plant (DC 10). " f"Craft: {craftables}."
