from abc import ABC, abstractmethod

from Core.Weapons import WeaponProperty, WeaponTraits
from Model.Content.Improvements import (
    ArmorClassBonus,
    WeaponAttackBonus,
    WeaponDamageBonus,
)
from Model.Content.FightingStyle import FightingStyle
from Model.Effects import Effects


class FightStyleModifier(FightingStyle):
    """A fighting style with a computed effect. Like any other effect, apply()
    only records facts on the stat block - weapon bonuses included, which go
    to character.ledger.weapon_bonuses instead of into the weapons."""

    @abstractmethod
    def apply(self, effects: Effects):
        pass


def _is_ranged_weapon(weapon: WeaponTraits) -> bool:
    return weapon.is_ranged


class Archery(FightStyleModifier):
    def apply(self, effects: Effects):
        WeaponAttackBonus(_is_ranged_weapon, 2, "Archery Fighting Style").apply(effects)

    def description(self):
        return "Archery: You gain a +2 bonus to attack rolls you make with Ranged weapons. (calculated automatically)"


class BlindFighting(FightingStyle):
    def description(self):
        return "Blind Fighting: You have Blindsight with a range of 10 feet."


class Defense(FightStyleModifier):
    def apply(self, effects: Effects):
        # A formula, so the armor is checked once everything has applied.
        ArmorClassBonus(lambda cs: 1 if cs.is_wearing_armor else 0).apply(effects)

    def description(self):
        return "Defense: While you're wearing Light, Medium, or Heavy armor, you gain a +1 bonus to Armor Class. (calculated automatically)"


def _is_one_handed_melee_weapon(weapon: WeaponTraits) -> bool:
    return (
        weapon.is_melee
        and WeaponProperty.TWO_HANDED not in weapon.properties
        # An Unarmed Strike isn't a weapon you hold in one hand.
        and not weapon.is_unarmed_strike
    )


class Dueling(FightStyleModifier):
    def apply(self, effects: Effects):
        WeaponDamageBonus(
            _is_one_handed_melee_weapon,
            2,
            "Dueling Fighting Style - Applied if one-handed weapon and no other weapons",
        ).apply(effects)

    def description(self):
        return "Dueling: When you're holding a Melee weapon in one hand and no other weapons, you gain a +2 bonus to damage rolls with that weapon. (calculated automatically)"


class GreatWeaponFighting(FightingStyle):
    def description(self):
        return "Great Weapon Fighting: When you roll damage for an attack you make with a Melee weapon that you are holding with two hands, you can treat any 1 or 2 on a damage die as a 3. The weapon must have the Two-Handed or Versatile property to gain this benefit."


class Interception(FightingStyle):
    def description(self):
        return "Interception: When a creature you can see hits another creature within 5 feet of you with an attack roll, you can take a Reaction to reduce the damage dealt to the target by 1d10 plus your Proficiency Bonus. You must be holding a Shield or a Simple or Martial weapon to use this Reaction. (calculate manually)"


class Protection(FightingStyle):
    def description(self):
        return "Protection: When a creature you can see attacks a target other than you that is within 5 feet of you, you can take a Reaction to interpose your Shield if you're holding one. You impose Disadvantage on the triggering attack roll and all other attack rolls against the target until the start of your next turn if you remain within 5 feet of the target. (calculate manually)"


def _is_thrown_weapon(weapon: WeaponTraits) -> bool:
    return WeaponProperty.THROWN in weapon.properties


class ThrownWeaponFighting(FightStyleModifier):
    def apply(self, effects: Effects):
        WeaponDamageBonus(
            _is_thrown_weapon, 2, "Thrown Weapon Fighting Style - ranged attacks only"
        ).apply(effects)

    def description(self):
        return "Thrown Weapon Fighting: When you hit with a ranged attack roll using a weapon that has the Thrown property, you gain a +2 bonus to the damage roll. (calculate manually)"


class TwoWeaponFighting(FightingStyle):
    def description(self):
        return "Two-Weapon Fighting: When you make an extra attack as a result of using a weapon that has the Light property, you can add your ability modifier to the damage of that attack if you aren't already adding it to the damage. (calculate manually)\n"


class UnarmedFighting(FightingStyle):
    def description(self):
        return (
            "Unarmed Fighting: When you hit with your Unarmed Strike and deal damage,"
            " you can deal Bludgeoning damage equal to 1d6 plus your Strength modifier"
            " instead of the normal damage of an Unarmed Strike."
            " If you aren't holding any weapons or a Shield when you make the attack roll, the d6 becomes a d8."
            " At the start of each of your turns, you can deal 1d4 Bludgeoning damage to one creature Grappled by you."
            " (calculate manually)\n"
        )
