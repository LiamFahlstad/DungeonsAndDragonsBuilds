from typing import Optional

from Core.Definitions import ArmorType
from Model.Recorder import Recorder, records


class WornArmor(Recorder):
    """What's worn: the body armor's type and display name, and whether a
    Shield is wielded. Untrained-armor Disadvantage, spellcasting warnings,
    the Defense fighting style, Unarmored Movement and Fast Movement, and
    ArmorClass.calculate all read this - none of it is their own concern, so
    it lives here on its own instead of inside ArmorClass.

    Merge rule: at most one body armor; a second raises. Wielding a Shield is
    a flag, so recording it twice changes nothing."""

    def __init__(self):
        self._body_armor: Optional[tuple[ArmorType, str]] = None
        self.shield_wielded = False

    @property
    def body_armor_type(self) -> Optional[ArmorType]:
        return self._body_armor[0] if self._body_armor is not None else None

    @property
    def body_armor_name(self) -> Optional[str]:
        return self._body_armor[1] if self._body_armor is not None else None

    @property
    def is_wearing_armor(self) -> bool:
        """Wearing Light, Medium or Heavy armor (a Shield alone doesn't count)."""
        return self.body_armor_type is not None

    @records
    def set_body_armor(self, armor_type: ArmorType, name: str) -> None:
        if self._body_armor is not None:
            raise ValueError(
                f"Character cannot wear multiple armors at once: "
                f"{self._body_armor[1]} and {name}."
            )
        self._body_armor = (armor_type, name)

    @records
    def wield_shield(self) -> None:
        self.shield_wielded = True
