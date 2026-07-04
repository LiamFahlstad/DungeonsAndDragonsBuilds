from dataclasses import dataclass, field
from typing import Callable

from Combat.Definitions import BasicCombatantData


@dataclass
class CombatScenario:
    """A named, reusable combat setup: who's fighting, which character sheets to show, and layout."""

    name: str
    combatants: Callable[[], list[BasicCombatantData]]
    character_sheets: Callable[[], list] = field(default=lambda: [])
    combatants_per_column: int = 4

    def build_combatants(self) -> list[BasicCombatantData]:
        return self.combatants()

    def build_character_sheets(self) -> list:
        return self.character_sheets()
