from dataclasses import dataclass, field
from typing import Callable

from Combat.EncounterConfig import EncounterSpec
from Model.Creatures.Combatants import BasicCombatantData


@dataclass
class CombatScenario:
    """One encounter of a campaign, as its encounters.json describes it
    (Combat/Campaigns/ENCOUNTERS.md): who's fighting, who takes part, and the
    layout. Its log is CombatLogs/<name>.json, written by
    `python -m Combat.Tools.prepare_encounters` before it can be played.

    `combatants` are the hostile side; `allies` are friendly NPCs fighting with the
    party. Both are shown in the combat window, but only `combatants` count toward
    the encounter's XP and difficulty."""

    name: str
    combatants: Callable[[], list[BasicCombatantData]]
    allies: Callable[[], list[BasicCombatantData]] = field(default=lambda: [])
    combatants_per_column: int = 4
    title: str = ""
    description: str = ""
    difficulty: str = ""
    # Who takes part, as (parts of) character names; None means the whole party.
    players: list[str] | None = None
    # One line per group of monsters / allies, e.g. "2× Goblin Boss".
    monster_summary: list[str] = field(default_factory=list)
    ally_summary: list[str] = field(default_factory=list)

    @classmethod
    def from_spec(cls, spec: EncounterSpec) -> "CombatScenario":
        return cls(
            name=spec.id,
            combatants=lambda: [c for s in spec.monsters for c in s.build()],
            allies=lambda: [c for s in spec.allies for c in s.build()],
            combatants_per_column=spec.combatants_per_column,
            title=spec.title,
            description=spec.description,
            difficulty=spec.difficulty,
            players=spec.players,
            monster_summary=[s.summary() for s in spec.monsters],
            ally_summary=[s.summary() for s in spec.allies],
        )

    @property
    def display_title(self) -> str:
        return self.title or self.name.replace("_", " ").title()

    def build_combatants(self) -> list[BasicCombatantData]:
        return self.combatants()

    def build_allies(self) -> list[BasicCombatantData]:
        return self.allies()
