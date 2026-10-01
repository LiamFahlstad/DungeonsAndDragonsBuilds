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
    CharacterContent, which imports this module."""

    def __init__(self):
        self.weapon_proficiencies: set[Enum] = set()
        self.armor_training: set[ArmorType] = set()
        self.tool_proficiencies: list[Any] = []

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
        if not any(type(t) is type(tool_proficiency) for t in self.tool_proficiencies):
            self.tool_proficiencies.append(tool_proficiency)
