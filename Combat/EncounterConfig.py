"""A campaign's encounters config, Combat/Campaigns/<Campaign>/encounters.py:
its tracked party (PartySpec: the players' characters and the allies who
travel with them) and every encounter it can run, with the monsters, allies
and party taking part. Combat/Campaigns/ENCOUNTERS.md documents the format.

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
    `group` share one initiative roll and take one turn together. With
    `hidden_from_players`, they're off the players' screen until the GM
    reveals them, for ones that join the fight later."""

    monster: type[BasicCombatantData]
    name: str | None = None
    count: int = 1
    group: str | None = None
    hidden_from_players: bool = False

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
            combatant.hidden_from_players = self.hidden_from_players
            combatants.append(combatant)
        return combatants

    def summary(self) -> str:
        label = self.name or self.monster.__name__
        label = f"{self.count}× {label}" if self.count > 1 else label
        label = f"{label} (one turn: {self.group})" if self.group else label
        return f"{label} (hidden at first)" if self.hidden_from_players else label


@dataclass
class PartySpec:
    """The tracked party: the players' characters (`members`, CharacterBuilder
    classes from Builds/Characters) and the allies who travel with them
    (`allies`, NPCs and creatures such as a hireling or an animal companion).
    Both join every encounter unless its `players` leaves them out, and both
    are tracked from fight to fight in the player log PlayerLogs/<id>.json:
    their Hit Points and conditions carry into the next fight until a long
    rest. Each ally needs a `name`, which is how it's tracked
    (Combat/PartyAllies.py)."""

    members: list[type] = field(default_factory=list)
    allies: list[CombatantSpec] = field(default_factory=list)
    # Names the player log, PlayerLogs/<id>.json.
    id: str = "main_party"

    def ally_names(self) -> list[str]:
        return [n for spec in self.allies for n in spec.names() if n]

    def build_allies(self) -> list[BasicCombatantData]:
        return [c for spec in self.allies for c in spec.build()]


@dataclass
class EncounterSpec:
    id: str
    title: str
    description: str = ""
    difficulty: str = ""
    # Who takes part, as (parts of) the names of the party's members and
    # allies; None means the whole party.
    players: list[str] | None = None
    monsters: list[CombatantSpec] = field(default_factory=list)
    allies: list[CombatantSpec] = field(default_factory=list)
    combatants_per_column: int = 4


@dataclass
class CampaignSpec:
    name: str
    title: str
    description: str
    # The tracked party. A plain list of CharacterBuilder classes (e.g.
    # Y2024PaladinDevotionEdmundCharacterBuilder) is a party of just them.
    party: PartySpec | list[type]
    encounters: list[EncounterSpec]

    def __post_init__(self):
        if not isinstance(self.party, PartySpec):
            self.party = PartySpec(members=list(self.party))

    @property
    def party_spec(self) -> PartySpec:
        assert isinstance(self.party, PartySpec)  # __post_init__ made it one
        return self.party


def build_party(spec: CampaignSpec) -> list:
    return [builder().build() for builder in spec.party_spec.members]


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


def split_taking_part(
    wanted: list[str] | None, member_names: list[str], ally_names: list[str]
) -> tuple[list[str], list[str]]:
    """The party members and the party allies `wanted` names (as
    resolve_players does, against both at once), each in party order."""
    chosen = resolve_players(wanted, member_names + ally_names)
    return (
        [n for n in member_names if n in chosen],
        [n for n in ally_names if n in chosen],
    )


def _combatant_problems(where: str, combatant: CombatantSpec) -> list[str]:
    monster = combatant.monster.__name__
    problems = []
    if combatant.group is not None and not combatant.group.strip():
        problems.append(f"{where}: {monster}: group must be a non-empty name")
    if combatant.count < 1:
        problems.append(f"{where}: {monster}: count must be at least 1")
    return problems


def _party_problems(party: PartySpec, member_names: list[str] | None) -> list[str]:
    """A party id that can't name a log, and allies without a name or sharing
    one (with each other or a member): they're tracked by name."""
    problems = []
    if not ID_PATTERN.match(party.id):
        problems.append(
            f"party id {party.id!r} must be snake_case (it names the player log)"
        )
    names = list(member_names or [])
    for ally in party.allies:
        problems += _combatant_problems("party ally", ally)
        if not ally.name:
            problems.append(
                f"party ally {ally.monster.__name__}: needs a name (it's tracked by it)"
            )
        for name in filter(None, ally.names()):
            if name in names:
                problems.append(f"party ally {name!r}: name used twice in the party")
            names.append(name)
    return problems


def _ally_matches(wanted: list[str], ally_names: list[str]):
    """Without the members' names, only what names an ally can be checked:
    raises KeyError for an entry matching more than one of them."""
    for want in wanted:
        matches = [n for n in ally_names if want.lower() in n.lower()]
        if len(matches) > 1:
            raise KeyError(f"player {want!r} matches {matches} in the party's allies")


def validate(spec: CampaignSpec, party_names: list[str] | None = None) -> list[str]:
    """Everything wrong with the config: bad or repeated ids, party allies
    without a name of their own, players not in the party (checked when
    `party_names`, the members' character names, is given; the party's
    allies count as in it), counts and layout below 1, groups that are empty
    names or span both sides, encounter combatants named like a party ally."""
    problems = []
    if not ID_PATTERN.match(spec.name):
        problems.append(f"campaign name {spec.name!r} must be snake_case")
    party = spec.party_spec
    problems += _party_problems(party, party_names)
    ally_names = party.ally_names()
    party_groups = {c.group for c in party.allies if c.group}
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
            problems += _combatant_problems(where, combatant)
            for name in sorted(set(filter(None, combatant.names())) & set(ally_names)):
                problems.append(
                    f"{where}: {name!r} is a party ally's name; "
                    "the encounter's own monsters and allies need others"
                )
        monster_groups = {c.group for c in encounter.monsters if c.group}
        ally_groups = {c.group for c in encounter.allies if c.group} | party_groups
        for group in sorted(monster_groups & ally_groups):
            problems.append(f"{where}: group {group!r} has monsters and allies")
        try:
            if party_names is not None:
                split_taking_part(encounter.players, party_names, ally_names)
            elif encounter.players is not None:
                _ally_matches(encounter.players, ally_names)
        except KeyError as error:
            problems.append(f"{where}: {error.args[0]}")
    return problems
