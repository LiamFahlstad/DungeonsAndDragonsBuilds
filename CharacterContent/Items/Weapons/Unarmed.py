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
        # 2024 Rules Glossary: Unarmed Strike, Grappling, Grappled. The DC is
        # a formula, not a number: this text belongs to the item, which has
        # no character to compute it against (and a Monk may use Dexterity).
        self.description_text = (
            "Choose Damage, Grapple or Shove. Grapple and Shove: target within 5 ft and no more than one size larger (Grapple also needs a free hand); "
            "it makes a Str or Dex saving throw (its choice) against DC 8 + Str mod + Proficiency Bonus (Monk Martial Arts: Dex can replace Str). "
            "Grapple: on a failed save, it is Grappled (Speed 0); moving it costs 1 extra foot per foot unless it is Tiny or two or more sizes smaller. "
            "To escape, it uses an action for a Str (Athletics) or Dex (Acrobatics) check against the same DC. "
            "Shove: on a failed save, push it 5 ft away or knock it Prone."
        )
