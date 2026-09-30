from Core.Definitions import Condition, DamageType


class Defenses:
    """Resistance/immunity to damage types and immunity to conditions, each
    with the sources that granted it (several sources of the same resistance
    are listed, not deduplicated into a bool)."""

    def __init__(self):
        self.damage_resistances: dict[DamageType, list[str]] = {}
        self.damage_immunities: dict[DamageType, list[str]] = {}
        self.condition_immunities: dict[Condition, list[str]] = {}

    def add_damage_resistance(self, damage_type: DamageType, source: str) -> None:
        self.damage_resistances.setdefault(damage_type, []).append(source)

    def add_damage_immunity(self, damage_type: DamageType, source: str) -> None:
        self.damage_immunities.setdefault(damage_type, []).append(source)

    def is_resistant_to_damage(self, damage_type: DamageType) -> bool:
        return damage_type in self.damage_resistances

    def is_immune_to_damage(self, damage_type: DamageType) -> bool:
        return damage_type in self.damage_immunities

    def get_damage_resistance_sources(self, damage_type: DamageType) -> list[str]:
        return self.damage_resistances.get(damage_type, [])

    def get_damage_immunity_sources(self, damage_type: DamageType) -> list[str]:
        return self.damage_immunities.get(damage_type, [])

    def add_condition_immunity(self, condition: Condition, source: str) -> None:
        self.condition_immunities.setdefault(condition, []).append(source)

    def is_immune_to_condition(self, condition: Condition) -> bool:
        return condition in self.condition_immunities

    def get_condition_immunity_sources(self, condition: Condition) -> list[str]:
        return self.condition_immunities.get(condition, [])
