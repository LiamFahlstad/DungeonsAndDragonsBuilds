from dataclasses import dataclass
from typing import Optional

from .Enums import WeaponDamageRolls, WeaponDamageTypes


@dataclass
class ExtraDamage:
    """Represents bonus damage added to a weapon attack. A leaf module, so
    both Base.py (weapons carry it) and Improvements.py (AddExtraDamage
    grants it) can import it."""

    damage_roll: WeaponDamageRolls
    damage_type: WeaponDamageTypes
    note: Optional[str] = None  # e.g. "chosen type, activate as bonus action"

    def format_damage(self) -> str:
        """Format as '1d6 Fire' or similar."""
        return f"{self.damage_roll.value} {self.damage_type.value}"
