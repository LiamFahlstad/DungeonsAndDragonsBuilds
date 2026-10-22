from Model.Content.Feature import (
    Feature,
    FeatureUses,
    FeatureActivation,
    ActionType,
    RegainedOn,
    FeatureTarget,
)
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Option, Paragraph, Table


class DivineMagic(Feature):
    def __init__(self):
        super().__init__(name="Divine Magic", origin="Divine Soul Sorcerer Level 3")

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Cleric spells",
                        "Whenever you learn a sorcerer cantrip or spell, you can pick it from the cleric list instead (other restrictions still apply); it becomes a sorcerer spell for you",
                    ),
                    (
                        "Affinity spell",
                        "One extra spell from your divine affinity (below). It doesn't count against your spells known; replace it only with a cleric spell.",
                    ),
                )
            ),
            Option(
                "Divine affinity",
                (
                    Table(
                        ("Affinity", "Spell"),
                        (
                            ("Good", "Cure Wounds"),
                            ("Evil", "Inflict Wounds"),
                            ("Law", "Bless"),
                            ("Chaos", "Bane"),
                            ("Neutrality", "Protection from Evil and Good"),
                        ),
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Your link to the divine allows you to learn spells normally associated with the cleric class. When your Spellcasting feature lets you learn a sorcerer cantrip or a sorcerer spell of 1st level or higher, you can choose the new spell from the cleric spell list or the sorcerer spell list. You must otherwise obey all the restrictions for selecting the spell, and it becomes a sorcerer spell for you.\n"
            "\n"
            "In addition, choose an affinity for the source of your divine power: good, evil, law, chaos, or neutrality. You learn an additional spell based on that affinity, as shown below. It is a sorcerer spell for you, but it doesn't count against your number of sorcerer spells known. If you later replace this spell, you must replace it with a spell from the cleric spell list.\n"
            "\n"
            "Affinity\tSpell\n"
            "Good\tCure Wounds\n"
            "Evil\tInflict Wounds\n"
            "Law\tBless\n"
            "Chaos\tBane\n"
            "Neutrality\tProtection from Evil and Good"
        )
        return description


class FavoredByTheGods(Feature):
    def __init__(self):
        super().__init__(
            name="Favored by the Gods",
            origin="Divine Soul Sorcerer Level 3",
            usage_tags=["buff"],
            uses=FeatureUses(max_uses=1, regain_all_on="short or long rest"),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # The once-per-Short-or-Long-Rest box is in the panel below.
        return [
            Paragraph("Divine power guards your destiny."),
            Facts(
                (
                    ("Trigger", "You fail a saving throw or miss with an attack roll"),
                    (
                        "Effect",
                        "Roll 2d4 and add it to the total, possibly changing the outcome",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Divine power guards your destiny. If you fail a saving throw or miss with an attack roll, you can roll 2d4 and add it to the total, possibly changing the outcome.\n"
            "\n"
            "Once you use this feature, you can't use it again until you finish a short or long rest."
        )
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.SHORT_OR_LONG_REST

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class EmpoweredHealing(Feature):
    def __init__(self):
        super().__init__(
            name="Empowered Healing",
            origin="Divine Soul Sorcerer Level 6",
            activation=FeatureActivation(range="5 Feet"),
            usage_tags=["buff", "heal"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "The divine energy coursing through you can empower healing spells."
            ),
            Facts(
                (
                    (
                        "Trigger",
                        "You or an ally within 5 feet rolls dice for the Hit Points a spell restores",
                    ),
                    ("Cost", "1 Sorcery Point"),
                    ("Effect", "Reroll any number of those dice once"),
                    ("Requirement", "You aren't Incapacitated"),
                    ("Frequency", "Once per turn"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "The divine energy coursing through you can empower healing spells. Whenever you or an ally within 5 feet of you rolls dice to determine the number of hit points a spell restores, you can spend 1 sorcery point to reroll any number of those dice once, provided you aren't incapacitated. You can use this feature only once per turn."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY


class AngelicForm(Feature):
    def __init__(self):
        super().__init__(
            name="Angelic Form",
            origin="Divine Soul Sorcerer Level 14",
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION,
                duration="Until Incapacitated, Dead, or Dismissed",
                range="Self",
            ),
            usage_tags=["utility"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Manifest a pair of spectral wings from your back."),
            Facts(
                (
                    ("Action", "Bonus Action"),
                    ("Fly Speed", "30 feet while the wings are present"),
                    (
                        "Duration",
                        "Until you're Incapacitated, you die, or you dismiss them as a Bonus Action",
                    ),
                )
            ),
            Table(
                ("Divine Magic affinity", "Wings"),
                (
                    ("Good or law", "Eagle"),
                    ("Evil or chaos", "Bat"),
                    ("Neutrality", "Dragonfly"),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You can use a bonus action to manifest a pair of spectral wings from your back. While the wings are present, you have a flying speed of 30 feet. The wings last until you're incapacitated, you die, or you dismiss them as a bonus action.\n"
            "\n"
            "The affinity you chose for your Divine Magic feature determines the appearance of the spectral wings: eagle wings for good or law, bat wings for evil or chaos, and dragonfly wings for neutrality."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class UnearthlyRecovery(Feature):
    def __init__(self):
        super().__init__(
            name="Unearthly Recovery",
            origin="Divine Soul Sorcerer Level 18",
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION, range="Self"
            ),
            usage_tags=["heal"],
            uses=FeatureUses(max_uses=1, regain_all_on="long rest"),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # The once-per-Long-Rest box is in the panel below.
        return [
            Paragraph("Overcome grievous injuries."),
            Facts(
                (
                    ("Action", "Bonus Action"),
                    ("Requirement", "You have fewer than half your Hit Points"),
                    ("Healing", "Half your Hit Point maximum"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You gain the ability to overcome grievous injuries. As a bonus action when you have fewer than half of your hit points remaining, you can regain a number of hit points equal to half your hit point maximum.\n"
            "\n"
            "Once you use this feature, you can't use it again until you finish a long rest."
        )
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF
