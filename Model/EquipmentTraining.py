from Core.Definitions import ArmorType
from Core.Weapons import WeaponProficiency
from Model.Recorder import Recorder, records
from Model.Records.Tools import ToolProficiency


class EquipmentTraining(Recorder):
    """Weapon, armor and tool training (PHB 2024 "Equipment Training &
    Proficiencies"). Whether a wielder is proficient with a weapon is worked
    out on read from the weapon's traits (Core.Weapons.weapon_matches_proficiency).

    Merge rule: set union. Tools are keyed by name, so the same tool from two
    sources is listed once. Reads list tools sorted by name."""

    def __init__(self):
        self.weapon_proficiencies: set[WeaponProficiency] = set()
        self.armor_training: set[ArmorType] = set()
        self._tools: dict[str, ToolProficiency] = {}

    @property
    def tool_proficiencies(self) -> list[ToolProficiency]:
        return [self._tools[name] for name in sorted(self._tools)]

    @property
    def has_shield_training(self) -> bool:
        return ArmorType.SHIELD in self.armor_training

    @records
    def add_weapon_proficiency(self, weapon_proficiency: WeaponProficiency) -> None:
        self.weapon_proficiencies.add(weapon_proficiency)

    @records
    def add_armor_training(self, armor_type: ArmorType) -> None:
        self.armor_training.add(armor_type)

    @records
    def add_tool_proficiency(self, tool_proficiency: ToolProficiency) -> None:
        """Proficiency with a tool. The same tool from several sources is
        listed once."""
        self._tools.setdefault(tool_proficiency.name, tool_proficiency)
