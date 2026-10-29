"""A campaign's encounters config, Combat/Campaigns/<Campaign>/encounters.py:
its tracked party and every encounter it can run, with the monsters, allies
and players taking part. Combat/Campaigns/ENCOUNTERS.md documents the format.

The config imports the stat-block and builder classes it uses, so a typo in
one fails at import. Nothing here imports Qt."""

import re
from dataclasses import dataclass, field

from Model.Creatures.Combatants import BasicCombatantData

# Encounter ids name their log (CombatLogs/<id>.json) and the --scenario flag.
ID_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")


@dataclass(frozen=True)
class CombatantSpec:
    """One line of an encounter's monsters or allies: `count` of the stat
    block `monster`, called `name` (numbered 1..count when there are several),
    or by their type when `name` is left out. Combatants with the same
    `group` share one initiative roll and take one turn together."""

    monster: type[BasicCombatantData]
    name: str | None = None
    count: int = 1
    group: str | None = None

    def names(self) -> list[str | None]:
        if self.count == 1:
            return [self.name]
        base = self.name or self.monster.__name__
        return [f"{base} {i}" for i in range(1, self.count + 1)]

    def build(self) -> list[BasicCombatantData]:
        combatants = []
        for name in self.names():
            # Stat-block classes fill in the base class's fields themselves.
            combatant = self.monster()  # type: ignore[call-arg]
            if name:
                combatant.set_name(name)
            combatant.initiative_group = self.group
            combatants.append(combatant)
        return combatants

    def summary(self) -> str:
        label = self.name or self.monster.__name__
        label = f"{self.count}× {label}" if self.count > 1 else label
        return f"{label} (one turn: {self.group})" if self.group else label


@dataclass
class EncounterSpec:
    id: str
    title: str
    description: str = ""
    difficulty: str = ""
    # Who takes part, as (parts of) character names; None means the whole party.
    players: list[str] | None = None
    monsters: list[CombatantSpec] = field(default_factory=list)
    allies: list[CombatantSpec] = field(default_factory=list)
    combatants_per_column: int = 4


@dataclass
class CampaignSpec:
    name: str
    title: str
    description: str
    # CharacterBuilder classes from Builds/Characters, e.g.
    # Y2024PaladinDevotionEdmundCharacterBuilder.
    party: list[type]
    encounters: list[EncounterSpec]


def build_party(spec: CampaignSpec) -> list:
    return [builder().build() for builder in spec.party]


def resolve_players(wanted: list[str] | None, party_names: list[str]) -> list[str]:
    """The party members `wanted` names, in party order: each entry is a
    character name or a case-insensitive part of exactly one. None means the
    whole party. Raises KeyError naming what doesn't match."""
    if wanted is None:
        return list(party_names)
    chosen = set()
    for want in wanted:
        matches = [n for n in party_names if want.lower() in n.lower()]
        if len(matches) != 1:
            raise KeyError(
                f"player {want!r} matches {matches or 'no one'} in the party {party_names}"
            )
        chosen.add(matches[0])
    return [n for n in party_names if n in chosen]


def validate(spec: CampaignSpec, party_names: list[str] | None = None) -> list[str]:
    """Everything wrong with the config: bad or repeated ids, players not in
    the party (checked when `party_names` is given), counts and layout below
    1, groups that are empty names or span both sides."""
    problems = []
    if not ID_PATTERN.match(spec.name):
        problems.append(f"campaign name {spec.name!r} must be snake_case")
    seen = set()
    for encounter in spec.encounters:
        where = f"encounter {encounter.id!r}"
        if not ID_PATTERN.match(encounter.id):
            problems.append(f"{where}: id must be snake_case (it names the log file)")
        if encounter.id in seen:
            problems.append(f"{where}: id used twice")
        seen.add(encounter.id)
        if not encounter.title:
            problems.append(f"{where}: needs a title")
        if encounter.combatants_per_column < 1:
            problems.append(f"{where}: combatants_per_column must be at least 1")
        for combatant in encounter.monsters + encounter.allies:
            monster = combatant.monster.__name__
            if combatant.group is not None and not combatant.group.strip():
                problems.append(f"{where}: {monster}: group must be a non-empty name")
            if combatant.count < 1:
                problems.append(f"{where}: {monster}: count must be at least 1")
        monster_groups = {c.group for c in encounter.monsters if c.group}
        ally_groups = {c.group for c in encounter.allies if c.group}
        for group in sorted(monster_groups & ally_groups):
            problems.append(f"{where}: group {group!r} has monsters and allies")
        if party_names is not None:
            try:
                resolve_players(encounter.players, party_names)
            except KeyError as error:
                problems.append(f"{where}: {error.args[0]}")
    return problems
