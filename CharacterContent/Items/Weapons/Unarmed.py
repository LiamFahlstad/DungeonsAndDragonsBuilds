"""The Unarmed Strike every character has (see Builds/StartingEquipment.py)."""

from typing import Optional

from Core.Definitions import Ability
from Core.Weapons import WeaponDamageRolls, WeaponDamageTypes, WeaponType
from Model.Content.Weapon import AbstractWeapon


class UnarmedStrike(AbstractWeapon):
    is_unarmed_strike = True

    def __init__(
        self,
        ability: Optional[Ability] = None,
        damage_roll: Optional[WeaponDamageRolls] = None,
        **kwargs,
    ):
        if ability is not None and ability not in (
            Ability.STRENGTH,
            Ability.DEXTERITY,
        ):
            raise ValueError("Unarmed Strike ability must be STR or DEX.")
        if kwargs.get("player_has_mastery"):
            raise ValueError("Unarmed Strike cannot have weapon mastery.")
        self._damage_roll_arg: Optional[WeaponDamageRolls] = damage_roll
        super().__init__(ability=ability, **kwargs)

    def base_stats(self) -> None:
        self.name = "Unarmed Strike"
        self.ability = self._ability_override or Ability.STRENGTH
        self.properties = []
        self.mastery = None
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponDamageTypes.BLUDGEONING
        self.damage_roll = self._damage_roll_arg or WeaponDamageRolls.D1
        self.description_text = (
            "You can replace one attack with a grapple or shove. Grapple: target within reach and no more than one size larger, requires a free hand; make an Athletics check contested by Athletics or Acrobatics; on success, the target’s speed becomes 0, you can move it at half speed, and you can release it at any time; it can repeat the check to escape and automatically fails if incapacitated. "
            "Shove: same limits and check; on success, either knock the target prone or push it 5 ft. "
        )
