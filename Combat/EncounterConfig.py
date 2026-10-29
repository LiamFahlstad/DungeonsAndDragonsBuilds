"""A campaign's encounters config, Combat/Campaigns/<Campaign>/encounters.json:
its tracked party and every encounter it can run, with the monsters, allies
and players taking part. Combat/Campaigns/ENCOUNTERS.md documents the format.

Nothing here imports Qt. Monster and build classes are looked up by name
only when they're needed, so reading a config stays cheap."""

import importlib
import inspect
import json
import pkgutil
import re
from dataclasses import dataclass, field
from functools import cache
from pathlib import Path

CONFIG_FILE = "encounters.json"
# Encounter ids name their log (CombatLogs/<id>.json) and the --scenario flag.
ID_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")


class ConfigError(ValueError):
    """An encounters.json that can't be read as a config at all."""


@dataclass(frozen=True)
class CombatantSpec:
    """One line of an encounter's monsters or allies: `count` of the stat
    block `monster`, called `name` (numbered 1..count when there are several),
    or by their type when `name` is left out."""

    monster: str
    name: str | None = None
    count: int = 1

    def names(self) -> list[str | None]:
        if self.count == 1:
            return [self.name]
        base = self.name or self.monster
        return [f"{base} {i}" for i in range(1, self.count + 1)]

    def build(self) -> list:
        cls = monster_class(self.monster)
        combatants = []
        for name in self.names():
            combatant = cls()
            if name:
                combatant.set_name(name)
            combatants.append(combatant)
        return combatants

    def summary(self) -> str:
        label = self.name or self.monster
        return f"{self.count}× {label}" if self.count > 1 else label


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
    # Build modules in Builds/Characters, e.g. "Y2024_Paladin_Devotion_Edmund".
    party: list[str]
    encounters: list[EncounterSpec]


def _combatants(raw, where: str) -> list[CombatantSpec]:
    if not isinstance(raw, list):
        raise ConfigError(f"{where} must be a list")
    specs = []
    for item in raw:
        if not isinstance(item, dict) or "monster" not in item:
            raise ConfigError(f'{where}: every entry needs a "monster"')
        unknown = set(item) - {"monster", "name", "count"}
        if unknown:
            raise ConfigError(f"{where}: unknown keys {sorted(unknown)}")
        specs.append(
            CombatantSpec(item["monster"], item.get("name"), item.get("count", 1))
        )
    return specs


def load(folder: str | Path) -> CampaignSpec:
    """Read <folder>/encounters.json. Raises ConfigError when it isn't shaped
    like a config; validate() checks what it refers to."""
    path = Path(folder) / CONFIG_FILE
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ConfigError(f"{path}: {error}") from error
    encounter_keys = {
        "id",
        "title",
        "description",
        "difficulty",
        "players",
        "monsters",
        "allies",
        "combatants_per_column",
    }
    encounters = []
    for item in raw.get("encounters", []):
        unknown = set(item) - encounter_keys
        if unknown:
            raise ConfigError(
                f"{path}: {item.get('id')}: unknown keys {sorted(unknown)}"
            )
        where = f"{path}: {item.get('id')}"
        encounters.append(
            EncounterSpec(
                id=item["id"],
                title=item["title"],
                description=item.get("description", ""),
                difficulty=item.get("difficulty", ""),
                players=item.get("players"),
                monsters=_combatants(item.get("monsters", []), f"{where}: monsters"),
                allies=_combatants(item.get("allies", []), f"{where}: allies"),
                combatants_per_column=item.get("combatants_per_column", 4),
            )
        )
    return CampaignSpec(
        name=raw["campaign"],
        title=raw.get("title", ""),
        description=raw.get("description", ""),
        party=list(raw.get("party", [])),
        encounters=encounters,
    )


@cache
def _monster_classes() -> dict[str, type]:
    """Every stat block by class name: Combat.Monsters (official and
    homebrew), then Combat.Combatants for the few only it has."""
    import Combat.Combatants as Combatants
    import Combat.Monsters as Monsters
    from Model.Creatures.Combatants import BasicCombatantData

    classes: dict[str, type] = {}
    for info in pkgutil.walk_packages(Monsters.__path__, "Combat.Monsters."):
        module = importlib.import_module(info.name)
        for name, cls in inspect.getmembers(module, inspect.isclass):
            if cls.__module__ == module.__name__ and issubclass(
                cls, BasicCombatantData
            ):
                classes.setdefault(name, cls)
    for name, cls in inspect.getmembers(Combatants, inspect.isclass):
        if cls.__module__ == Combatants.__name__:
            classes.setdefault(name, cls)
    return classes


def monster_class(name: str) -> type:
    """The stat block class called `name`, e.g. "GoblinBoss". A name both
    Combat.Monsters and Combat.Combatants define means the Monsters one; write
    "Combatants.Priest" for the other."""
    if name.startswith("Combatants."):
        import Combat.Combatants as Combatants

        cls = getattr(Combatants, name.split(".", 1)[1], None)
        if inspect.isclass(cls):
            return cls
        raise KeyError(name)
    return _monster_classes()[name]


def builder_class(build: str) -> type:
    """The CharacterBuilder class in Builds/Characters/<build>.py."""
    module = importlib.import_module(f"Builds.Characters.{build}")
    builders = [
        cls
        for name, cls in inspect.getmembers(module, inspect.isclass)
        if cls.__module__ == module.__name__ and name.endswith("CharacterBuilder")
    ]
    if len(builders) != 1:
        raise KeyError(f"{build}: expected one CharacterBuilder, found {len(builders)}")
    return builders[0]


def build_party(spec: CampaignSpec) -> list:
    return [builder_class(build)().build() for build in spec.party]


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
    """Everything wrong with the config: bad or repeated ids, monsters and
    builds that don't exist, players not in the party (checked when
    `party_names` is given), counts and layout below 1."""
    problems = []
    if not ID_PATTERN.match(spec.name):
        problems.append(f"campaign name {spec.name!r} must be snake_case")
    for build in spec.party:
        try:
            builder_class(build)
        except (ImportError, KeyError) as error:
            problems.append(f"party: build {build!r}: {error}")
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
            try:
                monster_class(combatant.monster)
            except KeyError:
                problems.append(f"{where}: no stat block called {combatant.monster!r}")
            if not isinstance(combatant.count, int) or combatant.count < 1:
                problems.append(
                    f"{where}: {combatant.monster}: count must be at least 1"
                )
        if party_names is not None:
            try:
                resolve_players(encounter.players, party_names)
            except KeyError as error:
                problems.append(f"{where}: {error.args[0]}")
    return problems
