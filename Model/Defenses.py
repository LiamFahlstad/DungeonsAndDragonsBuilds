from enum import Enum
from typing import TypeVar

from Core.Definitions import Condition, DamageType
from Model.Recorder import Recorder, records

Key = TypeVar("Key", bound=Enum)


def _canonical(granted: dict[Key, list[str]], keys: type[Key]) -> dict[Key, list[str]]:
    """`granted` with its keys in enum definition order and each key's
    sources sorted, so no read depends on the order they were granted in."""
    return {key: sorted(granted[key]) for key in keys if key in granted}


class Defenses(Recorder):
    """Resistance/immunity to damage types and immunity to conditions, each
    with the sources that granted it (several sources of the same resistance
    are listed, not deduplicated into a bool).

    Merge rule: set union per damage type or condition, keeping every source.
    Reads list keys in enum order and sources sorted."""

    def __init__(self):
        self._damage_resistances: dict[DamageType, list[str]] = {}
        self._damage_immunities: dict[DamageType, list[str]] = {}
        self._condition_immunities: dict[Condition, list[str]] = {}

    @property
    def damage_resistances(self) -> dict[DamageType, list[str]]:
        return _canonical(self._damage_resistances, DamageType)

    @property
    def damage_immunities(self) -> dict[DamageType, list[str]]:
        return _canonical(self._damage_immunities, DamageType)

    @property
    def condition_immunities(self) -> dict[Condition, list[str]]:
        return _canonical(self._condition_immunities, Condition)

    @records
    def add_damage_resistance(self, damage_type: DamageType, source: str) -> None:
        self._damage_resistances.setdefault(damage_type, []).append(source)

    @records
    def add_damage_immunity(self, damage_type: DamageType, source: str) -> None:
        self._damage_immunities.setdefault(damage_type, []).append(source)

    def is_resistant_to_damage(self, damage_type: DamageType) -> bool:
        return damage_type in self._damage_resistances

    def is_immune_to_damage(self, damage_type: DamageType) -> bool:
        return damage_type in self._damage_immunities

    def get_damage_resistance_sources(self, damage_type: DamageType) -> list[str]:
        return sorted(self._damage_resistances.get(damage_type, []))

    def get_damage_immunity_sources(self, damage_type: DamageType) -> list[str]:
        return sorted(self._damage_immunities.get(damage_type, []))

    @records
    def add_condition_immunity(self, condition: Condition, source: str) -> None:
        self._condition_immunities.setdefault(condition, []).append(source)

    def is_immune_to_condition(self, condition: Condition) -> bool:
        return condition in self._condition_immunities

    def get_condition_immunity_sources(self, condition: Condition) -> list[str]:
        return sorted(self._condition_immunities.get(condition, []))
