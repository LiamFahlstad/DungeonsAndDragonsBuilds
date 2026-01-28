from abc import abstractmethod

from pyparsing import ABC

from Features.Weapons import AbstractWeapon, WeaponProperty, WeaponType
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class FightingStyle(ABC):
    """A fighting style is a feature that modifies a character's combat abilities."""

    @abstractmethod
    def write_to_file(self, file):
        pass


class FightStyleCharacterFeature(FightingStyle):
    @abstractmethod
    def modify(self, character_stat_block: CharacterStatBlock):
        pass


class FightStyleWeaponFeature(FightingStyle):
    @abstractmethod
    def modify(self, weapons: list[AbstractWeapon]):
        pass


# Archery
class Archery(FightStyleWeaponFeature):
    def modify(self, weapons: list[AbstractWeapon]):
        for weapon in weapons:
            if weapon.stats().weapon_type in (
                WeaponType.MARTIAL_RANGED,
                WeaponType.SIMPLE_RANGED,
            ):
                weapon.attack_roll_bonuses.append((2, "2 (Archery Fighting Style)"))

    def write_to_file(self, file):
        file.write(
            "Archery: You gain a +2 bonus to attack rolls you make with Ranged weapons. (calculated automatically)\n"
        )


class BlindFighting(FightingStyle):
    def write_to_file(self, file):
        file.write("Blind Fighting: You have Blindsight with a range of 10 feet.\n")


class Defense(FightStyleCharacterFeature):
    def modify(self, character_stat_block: CharacterStatBlock):
        character_stat_block.combat.increase_armor_class(1)

    def write_to_file(self, file):
        file.write(
            "Defense: While you're wearing Light, Medium, or Heavy armor, you gain a +1 bonus to Armor Class. (calculated automatically)\n"
        )


class Dueling(FightStyleWeaponFeature):
    def modify(self, weapons: list[AbstractWeapon]):
        for weapon in weapons:
            if weapon.stats().weapon_type in (
                WeaponType.MARTIAL_MELEE,
                WeaponType.SIMPLE_MELEE,
            ):
                weapon.attack_roll_bonuses.append(
                    (
                        2,
                        "2 (Dueling Fighting Style - Applied if one-handed weapon and no other weapons)",
                    )
                )

    def write_to_file(self, file):
        file.write(
            "Dueling: When you're holding a Melee weapon in one hand and no other weapons, you gain a +2 bonus to damage rolls with that weapon. (calculated automatically)\n"
        )


class GreatWeaponFighting(FightingStyle):
    def write_to_file(self, file):
        file.write(
            "Great Weapon Fighting: When you roll damage for an attack you make with a Melee weapon that you are holding with two hands, you can treat any 1 or 2 on a damage die as a 3. The weapon must have the Two-Handed or Versatile property to gain this benefit. (calculate manually)\n"
        )


class Interception(FightingStyle):
    def write_to_file(self, file):
        file.write(
            "Interception: When a creature you can see hits another creature within 5 feet of you with an attack roll, you can take a Reaction to reduce the damage dealt to the target by 1d10 plus your Proficiency Bonus. You must be holding a Shield or a Simple or Martial weapon to use this Reaction. (calculate manually)\n"
        )


class Protection(FightingStyle):
    def write_to_file(self, file):
        file.write(
            "Protection: When a creature you can see attacks a target other than you that is within 5 feet of you, you can take a Reaction to interpose your Shield if you're holding one. You impose Disadvantage on the triggering attack roll and all other attack rolls against the target until the start of your next turn if you remain within 5 feet of the target. (calculate manually)\n"
        )


class ThrownWeaponFighting(FightStyleWeaponFeature):
    def modify(self, weapons: list[AbstractWeapon]):
        for weapon in weapons:
            # Only apply to simple melee weapons
            if weapon.stats().weapon_type not in (
                WeaponType.SIMPLE_RANGED,
                WeaponType.MARTIAL_RANGED,
            ):
                continue

            # Only apply to weapons with the Thrown property
            for prop in weapon.stats().properties:
                if prop.name == WeaponProperty.THROWN:
                    weapon.attack_roll_bonuses.append(
                        (2, "2 (Thrown Weapon Fighting Style)")
                    )
                    break

    def write_to_file(self, file):
        file.write(
            "Thrown Weapon Fighting: When you hit with a ranged attack roll using a weapon that has the Thrown property, you gain a +2 bonus to the damage roll. (calculate manually)\n"
        )


class TwoWeaponFighting(FightingStyle):
    def write_to_file(self, file):
        file.write(
            "Two-Weapon Fighting: When you make an extra attack as a result of using a weapon that has the Light property, you can add your ability modifier to the damage of that attack if you aren't already adding it to the damage. (calculate manually)\n"
        )


class UnarmedFighting(FightingStyle):
    def write_to_file(self, file):
        text = (
            "Unarmed Fighting: When you hit with your Unarmed Strike and deal damage,"
            " you can deal Bludgeoning damage equal to 1d6 plus your Strength modifier"
            " instead of the normal damage of an Unarmed Strike."
            " If you aren't holding any weapons or a Shield when you make the attack roll, the d6 becomes a d8."
            " At the start of each of your turns, you can deal 1d4 Bludgeoning damage to one creature Grappled by you."
            " (calculate manually)\n"
        )
        file.write(text)
