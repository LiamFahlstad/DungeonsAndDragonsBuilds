from enum import Enum
from typing import Any

from Core.Definitions import ArmorType
from Model.Recorder import Recorder, records


class EquipmentTraining(Recorder):
    """Weapon, armor and tool training (PHB 2024 "Equipment Training &
    Proficiencies"), each with the sources that granted it. A weapon works
    out whether its wielder is proficient on read, against
    weapon_proficiencies (AbstractWeapon.is_proficient); typed loosely
    (Enum/Any) since the WeaponProficiency enum and ToolProficiency live in
    CharacterContent, which imports this module.

    Merge rule: set union. Tools are keyed by tool type (tool types take no
    parameters), so the same tool from two sources is listed once. Reads
    list tools sorted by name."""

    def __init__(self):
        self.weapon_proficiencies: set[Enum] = set()
        self.armor_training: set[ArmorType] = set()
        self._tools: dict[type, Any] = {}

    @property
    def tool_proficiencies(self) -> list[Any]:
        return sorted(self._tools.values(), key=lambda tool: tool.name)

    @property
    def has_shield_training(self) -> bool:
        return ArmorType.SHIELD in self.armor_training

    @records
    def add_weapon_proficiency(self, weapon_proficiency: Enum) -> None:
        self.weapon_proficiencies.add(weapon_proficiency)

    @records
    def add_armor_training(self, armor_type: ArmorType) -> None:
        self.armor_training.add(armor_type)

    @records
    def add_tool_proficiency(self, tool_proficiency: Any) -> None:
        """Proficiency with a tool (a ToolProficiency). The same tool from
        several sources is listed once."""
        self._tools.setdefault(type(tool_proficiency), tool_proficiency)
