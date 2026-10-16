from dataclasses import dataclass, field
from typing import Callable

from Model.Creatures.Combatants import BasicCombatantData


@dataclass
class CombatScenario:
    """A named, reusable combat setup: who's fighting, which character sheets to show, and layout.

    `combatants` are the hostile side; `allies` are friendly NPCs fighting with the
    party. Both are shown in the combat window, but only `combatants` count toward
    the encounter's XP and difficulty."""

    name: str
    combatants: Callable[[], list[BasicCombatantData]]
    allies: Callable[[], list[BasicCombatantData]] = field(default=lambda: [])
    character_sheets: Callable[[], list] = field(default=lambda: [])
    combatants_per_column: int = 4

    def build_combatants(self) -> list[BasicCombatantData]:
        return self.combatants()

    def build_allies(self) -> list[BasicCombatantData]:
        return self.allies()

    def build_character_sheets(self) -> list:
        return self.character_sheets()
