from abc import ABC, abstractmethod

from Core.Definitions import Ability, Sense
from Core.Weapons import WeaponProperty, WeaponTraits
from Model.Content.Improvements import (
    ArmorClassBonus,
    GrantSense,
    WeaponAttackBonus,
    WeaponDamageBonus,
)
from Model.Content.FeatureText import Block, Facts, Paragraph, Table
from Model.Content.FightingStyle import FightingStyle
from Model.Ledger.LedgerWriter import LedgerWriter
from CharacterContent.Spells.SpellLists import WizardLevel0Spells


class FightStyleModifier(FightingStyle):
    """A fighting style with a computed effect. Like any other effect, apply()
    only records facts on the stat block - weapon bonuses included, which go
    to the Ledger's weapon_bonuses instead of into the weapons."""

    @abstractmethod
    def apply(self, ledger_writer: LedgerWriter):
        pass


def _is_ranged_weapon(weapon: WeaponTraits) -> bool:
    return weapon.is_ranged


class Archery(FightStyleModifier):
    name = "Archery"

    def apply(self, ledger_writer: LedgerWriter):
        WeaponAttackBonus(_is_ranged_weapon, 2, "Archery Fighting Style").apply(
            ledger_writer
        )

    def description(self):
        return "Archery: You gain a +2 bonus to attack rolls you make with Ranged weapons. (calculated automatically)"


class BlindFighting(FightingStyle):
    name = "Blind Fighting"

    def apply(self, ledger_writer: LedgerWriter):
        GrantSense(Sense.BLINDSIGHT, 10).apply(ledger_writer)

    def description(self):
        return "Blind Fighting: You have Blindsight with a range of 10 feet."


class Defense(FightStyleModifier):
    name = "Defense"

    def apply(self, ledger_writer: LedgerWriter):
        # A formula, so the armor is checked once everything has applied.
        ArmorClassBonus(lambda cs: 1 if cs.is_wearing_armor else 0).apply(ledger_writer)

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
    name = "Dueling"

    def apply(self, ledger_writer: LedgerWriter):
        WeaponDamageBonus(
            _is_one_handed_melee_weapon,
            2,
            "Dueling Fighting Style - Applied if one-handed weapon and no other weapons",
        ).apply(ledger_writer)

    def description(self):
        return "Dueling: When you're holding a Melee weapon in one hand and no other weapons, you gain a +2 bonus to damage rolls with that weapon. (calculated automatically)"


class GreatWeaponFighting(FightingStyle):
    name = "Great Weapon Fighting"

    def description(self):
        return "Great Weapon Fighting: When you roll damage for an attack you make with a Melee weapon that you are holding with two hands, you can treat any 1 or 2 on a damage die as a 3. The weapon must have the Two-Handed or Versatile property to gain this benefit."

    def get_improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Weapons",
                        "A Melee weapon you hold with two hands that has the Two-Handed or Versatile property",
                    ),
                    (
                        "Effect",
                        "When you roll its damage, treat any 1 or 2 on a damage die as a 3",
                    ),
                )
            ),
        ]


class Interception(FightingStyle):
    name = "Interception"

    def description(self):
        return "Interception: When a creature you can see hits another creature within 5 feet of you with an attack roll, you can take a Reaction to reduce the damage dealt to the target by 1d10 plus your Proficiency Bonus. You must be holding a Shield or a Simple or Martial weapon to use this Reaction. (calculate manually)"

    def get_improved_description(self) -> list[Block]:
        return [
            Paragraph("Blunt a blow aimed at someone next to you."),
            Facts(
                (
                    ("Action", "Reaction"),
                    (
                        "Trigger",
                        "A creature you can see hits another creature within 5 feet of you with an attack roll",
                    ),
                    (
                        "Requirement",
                        "You're holding a Shield or a Simple or Martial weapon",
                    ),
                    (
                        "Effect",
                        "Reduce the damage to the target by 1d10 + Proficiency Bonus",
                    ),
                )
            ),
        ]


class Protection(FightingStyle):
    name = "Protection"

    def description(self):
        return "Protection: When a creature you can see attacks a target other than you that is within 5 feet of you, you can take a Reaction to interpose your Shield if you're holding one. You impose Disadvantage on the triggering attack roll and all other attack rolls against the target until the start of your next turn if you remain within 5 feet of the target. (calculate manually)"

    def get_improved_description(self) -> list[Block]:
        return [
            Paragraph("Interpose your Shield to protect someone next to you."),
            Facts(
                (
                    ("Action", "Reaction"),
                    (
                        "Trigger",
                        "A creature you can see attacks a target other than you within 5 feet of you",
                    ),
                    ("Requirement", "You're holding a Shield"),
                    (
                        "Effect",
                        "Disadvantage on that attack roll, and on all other attack rolls against the target until the start of your next turn while you stay within 5 feet of it",
                    ),
                )
            ),
        ]


def _is_thrown_weapon(weapon: WeaponTraits) -> bool:
    return WeaponProperty.THROWN in weapon.properties


class ThrownWeaponFighting(FightStyleModifier):
    name = "Thrown Weapon Fighting"

    def apply(self, ledger_writer: LedgerWriter):
        WeaponDamageBonus(
            _is_thrown_weapon, 2, "Thrown Weapon Fighting Style - ranged attacks only"
        ).apply(ledger_writer)

    def description(self):
        return "Thrown Weapon Fighting: When you hit with a ranged attack roll using a weapon that has the Thrown property, you gain a +2 bonus to the damage roll. (added automatically to the damage of every weapon with the Thrown property; leave it out when you make a melee attack with one, such as a Handaxe or Dagger)"

    def get_improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Effect",
                        "+2 to the damage roll when you hit with a ranged attack using a Thrown weapon",
                    ),
                    (
                        "On this sheet",
                        "Already added to every Thrown weapon's damage; leave it out when you make a melee attack with one (such as a Handaxe or Dagger)",
                    ),
                )
            ),
        ]


class TwoWeaponFighting(FightingStyle):
    name = "Two-Weapon Fighting"

    def description(self):
        return "Two-Weapon Fighting: When you make an extra attack as a result of using a weapon that has the Light property, you can add your ability modifier to the damage of that attack if you aren't already adding it to the damage. (calculate manually)\n"

    def get_improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Trigger",
                        "You make the extra attack from a weapon with the Light property",
                    ),
                    (
                        "Effect",
                        "Add your ability modifier to that attack's damage, if you aren't already",
                    ),
                    (
                        "On this sheet",
                        "Not included in the weapon damage shown; add it yourself",
                    ),
                )
            ),
        ]


class UnarmedFighting(FightingStyle):
    name = "Unarmed Fighting"

    def description(self):
        return (
            "Unarmed Fighting: When you hit with your Unarmed Strike and deal damage,"
            " you can deal Bludgeoning damage equal to 1d6 plus your Strength modifier"
            " instead of the normal damage of an Unarmed Strike."
            " If you aren't holding any weapons or a Shield when you make the attack roll, the d6 becomes a d8."
            " At the start of each of your turns, you can deal 1d4 Bludgeoning damage to one creature Grappled by you."
            " (calculate manually)\n"
        )

    def get_improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "When your Unarmed Strike hits and deals damage, it deals this instead of its normal damage:"
            ),
            Table(
                ("When you attack, you hold", "Damage"),
                (
                    ("A weapon or a Shield", "1d6 + Strength modifier Bludgeoning"),
                    ("No weapons and no Shield", "1d8 + Strength modifier Bludgeoning"),
                ),
            ),
            Facts(
                (
                    (
                        "Grapple",
                        "At the start of each of your turns, deal 1d4 Bludgeoning damage to one creature Grappled by you",
                    ),
                    (
                        "On this sheet",
                        "Not included in the Unarmed Strike damage shown; use the table",
                    ),
                )
            ),
        ]


class ArcaneWarrior(FightingStyle):
    name = "Arcane Warrior"

    def __init__(
        self,
        cantrip_1: WizardLevel0Spells,
        cantrip_2: WizardLevel0Spells,
        spellcasting_ability: Ability,
    ):
        if cantrip_1 == cantrip_2:
            raise ValueError("Arcane Warrior requires two different Wizard cantrips.")
        if spellcasting_ability not in (
            Ability.INTELLIGENCE,
            Ability.WISDOM,
            Ability.CHARISMA,
        ):
            raise ValueError(
                "Arcane Warrior spellcasting ability must be Intelligence, Wisdom, or Charisma."
            )
        self.cantrip_1 = cantrip_1
        self.cantrip_2 = cantrip_2
        self.spellcasting_ability = spellcasting_ability

    def description(self):
        return (
            f"Arcane Warrior: You learn two Wizard cantrips of your choice: {self.cantrip_1.value} and {self.cantrip_2.value}. "
            f"Your spellcasting ability for these spells is {self.spellcasting_ability.value}. "
            "Whenever you gain a level, you can replace one of these cantrips with another Wizard cantrip."
        )

    def get_improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Cantrips",
                        f"{self.cantrip_1.value} and {self.cantrip_2.value} (Wizard)",
                    ),
                    ("Spellcasting ability", self.spellcasting_ability.value),
                    (
                        "Swap",
                        "Whenever you gain a level, replace one with another Wizard cantrip",
                    ),
                )
            ),
        ]


class PackFighting(FightingStyle):
    name = "Pack Fighting"

    def description(self):
        return (
            "Pack Fighting: When you make a melee attack with a weapon or an Unarmed Strike against a creature, you gain a +1 bonus to the damage roll if at least one of your allies is within 5 feet of the creature and the ally doesn't have the Incapacitated condition. "
            "If at least one ally within 5 feet of the creature also has this feat and doesn't have the Incapacitated condition, this bonus increases to +2. (calculate manually)"
        )

    def get_improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "Melee attacks with a weapon or an Unarmed Strike deal bonus damage when an ally is next to the target."
            ),
            Table(
                ("Within 5 feet of the target (not Incapacitated)", "Damage bonus"),
                (
                    ("At least one of your allies", "+1"),
                    ("At least one ally who also has Pack Fighting", "+2"),
                ),
            ),
            Facts(
                (
                    (
                        "On this sheet",
                        "Not included in the weapon damage shown; add it yourself",
                    ),
                )
            ),
        ]


class ProneFighting(FightingStyle):
    name = "Prone Fighting"

    def description(self):
        return "Prone Fighting: While you have the Prone condition, you don't have Disadvantage due to the Prone condition on attack rolls, and the Prone condition doesn't grant Advantage on attack rolls made against you."
