from typing import Optional

from Core.Definitions import ArmorType
from Model.Recorder import Recorder, records


class WornArmor(Recorder):
    """What's worn: the body armor's type and display name, and whether a
    Shield is wielded. Untrained-armor Disadvantage, spellcasting warnings,
    the Defense fighting style, Unarmored Movement and Fast Movement, and
    ArmorClass.calculate all read this - none of it is their own concern, so
    it lives here on its own instead of inside ArmorClass."""

    def __init__(self):
        self.body_armor_type: Optional[ArmorType] = None
        self.body_armor_name: Optional[str] = None
        self.shield_wielded = False

    @property
    def is_wearing_armor(self) -> bool:
        """Wearing Light, Medium or Heavy armor (a Shield alone doesn't count)."""
        return self.body_armor_type is not None

    @records
    def set_body_armor(self, armor_type: ArmorType, name: str) -> None:
        self.body_armor_type = armor_type
        self.body_armor_name = name

    @records
    def wield_shield(self) -> None:
        self.shield_wielded = True
