from dataclasses import dataclass, field
from typing import Callable

from Combat.EncounterConfig import (
    CombatantSpec,
    EncounterSpec,
    PartySpec,
    split_taking_part,
)
from Model.Creatures.Combatants import BasicCombatantData


@dataclass
class CombatScenario:
    """One encounter of a campaign, as its encounters.py describes it
    (Combat/Campaigns/ENCOUNTERS.md): who's fighting, who takes part, and the
    layout. Its log is CombatLogs/<name>.json: an empty {} until the combat
    window opens the encounter, which sets the log up from this.

    `combatants` are the hostile side; `allies` are friendly NPCs fighting with the
    party in this encounter only. `party_allies` are the party's own allies
    (PartySpec.allies), tracked from fight to fight (Combat/PartyAllies.py):
    those of them `players` names take part. All are shown in the combat
    window, but only `combatants` count toward the encounter's XP and
    difficulty."""

    name: str
    combatants: Callable[[], list[BasicCombatantData]]
    allies: Callable[[], list[BasicCombatantData]] = field(default=lambda: [])
    combatants_per_column: int = 4
    title: str = ""
    description: str = ""
    difficulty: str = ""
    # Who takes part, as (parts of) the names of the party's members and
    # allies; None means the whole party.
    players: list[str] | None = None
    # One line per group of monsters / allies, e.g. "2× Goblin Boss".
    monster_summary: list[str] = field(default_factory=list)
    ally_summary: list[str] = field(default_factory=list)
    # The party's allies (PartySpec.allies), whether or not they take part.
    party_allies: list[CombatantSpec] = field(default_factory=list)

    @classmethod
    def from_spec(
        cls, spec: EncounterSpec, party: PartySpec | None = None
    ) -> "CombatScenario":
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
            party_allies=list(party.allies) if party else [],
        )

    @property
    def display_title(self) -> str:
        return self.title or self.name.replace("_", " ").title()

    @property
    def party_ally_names(self) -> list[str]:
        """Every party ally's name, whether or not it takes part."""
        return [n for s in self.party_allies for n in s.names() if n]

    def members_taking_part(self, member_names: list[str]) -> list[str]:
        """The party members (of `member_names`, their character names) who
        take part. Raises KeyError for a `players` entry that matches none
        or several of the party's members and allies."""
        return split_taking_part(self.players, member_names, self.party_ally_names)[0]

    def party_allies_taking_part(self) -> list[str]:
        """The names of the party allies who take part: all of them, unless
        `players` names who does (validate() checks no entry is ambiguous)."""
        names = self.party_ally_names
        if self.players is None:
            return names
        wanted = [w.lower() for w in self.players]
        return [n for n in names if any(w in n.lower() for w in wanted)]

    def build_combatants(self) -> list[BasicCombatantData]:
        return self.combatants()

    def build_party_allies(self) -> list[BasicCombatantData]:
        """The party allies taking part, as their stat blocks say (full Hit
        Points); the player log brings them to how they are now."""
        taking_part = set(self.party_allies_taking_part())
        return [
            c
            for s in self.party_allies
            for c, name in zip(s.build(), s.names())
            if name in taking_part
        ]

    def build_allies(self) -> list[BasicCombatantData]:
        """Everyone on the party's side but the players: the party allies
        taking part, then the encounter's own allies."""
        return self.build_party_allies() + self.allies()
