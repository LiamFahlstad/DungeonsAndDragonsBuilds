from typing import Callable, NamedTuple

from Core.Weapons import WeaponTraits

# Which weapons a bonus applies to (e.g. "Ranged weapons", "the Longbow and
# Shortbow"), checked against each weapon's traits on read.
WeaponFilter = Callable[[WeaponTraits], bool]


class WeaponBonus(NamedTuple):
    """A flat bonus to attack or damage rolls with the weapons `applies_to`
    accepts, e.g. the Archery fighting style's +2 to attack rolls with Ranged
    weapons."""

    applies_to: WeaponFilter
    value: int
    source: str

    @property
    def label(self) -> str:
        # Same "<value> (<reason>)" shape as a weapon's own bonuses
        # (AddAttackRollBonus / AddDamageRollBonus).
        return f"{self.value} ({self.source})"


class WeaponBonuses:
    """Attack and damage roll bonuses the wielder brings to their weapons
    (fighting styles, Bracers of Archery, ...). Recorded here instead of
    written into the weapon objects, so evaluating a character never changes
    its weapons; a weapon combines these with its own bonuses on read
    (AbstractWeapon.calculate_total_attack_roll_bonus_int and
    calculate_damage_bonus_int).

    Merge rule: sum. Reads list bonuses sorted by (source, value)."""

    def __init__(self):
        self._attack: list[WeaponBonus] = []
        self._damage: list[WeaponBonus] = []

    def add_attack_bonus(self, bonus: WeaponBonus) -> None:
        self._attack.append(bonus)

    def add_damage_bonus(self, bonus: WeaponBonus) -> None:
        self._damage.append(bonus)

    def attack_bonuses(self, weapon: WeaponTraits) -> list[tuple[int, str]]:
        """(value, label) for every attack roll bonus that applies to `weapon`."""
        return _labels(self._attack, weapon)

    def damage_bonuses(self, weapon: WeaponTraits) -> list[tuple[int, str]]:
        """(value, label) for every damage roll bonus that applies to `weapon`."""
        return _labels(self._damage, weapon)


def _labels(bonuses: list[WeaponBonus], weapon: WeaponTraits) -> list[tuple[int, str]]:
    applicable = [b for b in bonuses if b.applies_to(weapon)]
    return [
        (b.value, b.label)
        for b in sorted(applicable, key=lambda b: (b.source, b.value))
    ]
