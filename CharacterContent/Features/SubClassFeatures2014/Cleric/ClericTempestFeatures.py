from Core.Definitions import Ability, ArmorType
from Model.Content.Feature import (
    Feature,
    FeatureUses,
    FeatureActivation,
    ActionType,
    RegainedOn,
    FeatureTarget,
)
from Model.Content.Improvements import GrantArmorTraining, GrantWeaponProficiency
from CharacterContent.Items.Weapons import WeaponProficiency
from Model.Ledger.LedgerWriter import LedgerWriter
from Core.Rules import MAX_ABILITY_MODIFIER
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Paragraph, Table, dc_formula


class BonusProficiencies(Feature):
    def __init__(self):
        super().__init__(
            name="Bonus Proficiencies", origin="Tempest Domain Cleric Level 3"
        )

    def apply(self, ledger_writer: LedgerWriter):
        # "You gain proficiency with martial weapons and heavy armor."
        GrantWeaponProficiency([WeaponProficiency.MARTIAL]).apply(ledger_writer)
        GrantArmorTraining([ArmorType.HEAVY]).apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Weapon proficiency", "Martial weapons"),
                    ("Armor proficiency", "Heavy armor"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "You gain proficiency with martial weapons and heavy armor."
        return description


class WrathOfTheStorm(Feature):
    def __init__(self):
        super().__init__(
            name="Wrath of the Storm",
            origin="Tempest Domain Cleric Level 3",
            activation=FeatureActivation(
                action_type=ActionType.REACTION, range="5 Feet"
            ),
            usage_tags=["damage"],
            uses=FeatureUses(
                max_uses=MAX_ABILITY_MODIFIER,
                regain_all_on="long rest",
                current_formula="Current amount: equal to your Wisdom modifier.",
            ),
        )

    def calculate_dc(self, character: CharacterView) -> int:
        return character.calculate_difficulty_class_for_ability(Ability.WISDOM)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # Uses are in the panel below.
        return [
            Facts(
                (
                    ("Action", "Reaction"),
                    (
                        "Trigger",
                        "A creature you can see within 5 feet hits you with an attack",
                    ),
                    (
                        "Save",
                        f"Dexterity save against your spell save DC ({dc_formula(Ability.WISDOM)})",
                    ),
                    ("Failed", "2d8 lightning or thunder damage (your choice)"),
                    ("Succeeded", "Half damage"),
                    ("Uses", "Wisdom modifier (minimum once) per long rest"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You can thunderously rebuke attackers. When a creature within 5 feet of you that you can see hits you with an attack, you can use your reaction to cause the creature to make a Dexterity saving throw. The creature takes 2d8 lightning or thunder damage (your choice) on a failed saving throw, and half as much damage on a successful one.\n"
            "You can use this feature a number of times equal to your Wisdom modifier (a minimum of once). You regain all expended uses when you finish a long rest."
        )
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY

    def number_of_uses(self, character: CharacterView) -> int:
        return max(1, character.get_wisdom_modifier())


class TempestDomainSpells(Feature):
    def __init__(self):
        super().__init__(
            name="Tempest Domain Spells", origin="Tempest Domain Cleric Level 3"
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "From the Cleric level shown, you always have these spells prepared."
            ),
            Table(
                ("Cleric level", "Spells"),
                (
                    ("1", "Fog Cloud, Thunderwave"),
                    ("3", "Gust of Wind, Shatter"),
                    ("5", "Call Lightning, Sleet Storm"),
                    ("7", "Control Water, Ice Storm"),
                    ("9", "Destructive Wave, Insect Plague"),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Your connection to this divine domain ensures you always have certain spells ready. When you reach a Cleric level specified in the Tempest Domain Spells table, you thereafter always have the listed spells prepared.\n"
            "Tempest Domain Spells\n"
            "Cleric Level\tSpells\n"
            "1st\tFog Cloud, Thunderwave\n"
            "3rd\tGust of Wind, Shatter\n"
            "5th\tCall Lightning, Sleet Storm\n"
            "7th\tControl Water, Ice Storm\n"
            "9th\tDestructive Wave, Insect Plague"
        )
        return description


class DestructiveWrathChannelDivinity(Feature):
    def __init__(self):
        super().__init__(
            name="Channel Divinity: Destructive Wrath",
            origin="Tempest Domain Cleric Level 3",
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "Use Channel Divinity to wield the power of the storm with unchecked ferocity."
            ),
            Facts(
                (
                    ("Trigger", "You roll Lightning or Thunder damage"),
                    ("Effect", "Deal maximum damage instead of rolling"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "You can use your Channel Divinity to wield the power of the storm with unchecked ferocity.\nWhen you roll lightning or thunder damage, you can use your Channel Divinity to deal maximum damage, instead of rolling."
        return description


class ThunderousStrike(Feature):
    def __init__(self):
        super().__init__(
            name="Thunderous Strike",
            origin="Tempest Domain Cleric Level 6",
            usage_tags=["control"],
            activation=FeatureActivation(range="10 Feet"),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Trigger",
                        "You deal Lightning damage to a Large or smaller creature",
                    ),
                    ("Effect", "Push it up to 10 feet away from you"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "When you deal lightning damage to a Large or smaller creature, you can also push it up to 10 feet away from you."
        return description


class Stormborn(Feature):
    def __init__(self):
        super().__init__(
            name="Stormborn",
            origin="Tempest Domain Cleric Level 17",
            usage_tags=["utility"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Fly Speed", "Equal to your current walking speed"),
                    ("Requirement", "You aren't underground or indoors"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "You have a flying speed equal to your current walking speed whenever you are not underground or indoors."
        return description
