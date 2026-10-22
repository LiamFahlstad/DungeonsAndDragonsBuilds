from Model.Content.Feature import (
    Feature,
    FeatureActivation,
    ActionType,
    FeatureTarget,
)
from Model.Content.Improvements import InitiativeBonus
from Model.Ledger.LedgerWriter import LedgerWriter
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Option, Paragraph, Table


class FancyFootwork(Feature):
    def __init__(self):
        super().__init__(
            name="Fancy Footwork",
            origin="Swashbuckler Rogue Level 3",
            activation=FeatureActivation(duration="Until End of Your Turn"),
            usage_tags=["buff"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Land a strike and then slip away without reprisal."),
            Facts(
                (
                    (
                        "Trigger",
                        "You make a melee attack against a creature on your turn",
                    ),
                    (
                        "Effect",
                        "That creature can't make Opportunity Attacks against you for the rest of your turn",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You learn how to land a strike and then slip away without reprisal. During your turn, "
            "if you make a melee attack against a creature, that creature can't make opportunity attacks "
            "against you for the rest of your turn."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class RakishAudacity(Feature):
    def __init__(self):
        super().__init__(
            name="Rakish Audacity",
            origin="Swashbuckler Rogue Level 3",
            activation=FeatureActivation(range="5 Feet"),
            usage_tags=["buff"],
        )

    def apply(self, ledger_writer: LedgerWriter):
        InitiativeBonus(lambda cs: cs.get_charisma_modifier()).apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Your confidence propels you into battle."),
            Facts(
                (
                    ("Initiative", "+ Charisma modifier"),
                    (
                        "Sneak Attack",
                        "No Advantage needed if you're within 5 feet of the target, no other creatures are within 5 feet of you, and you don't have Disadvantage",
                    ),
                    ("Other rules", "All other Sneak Attack rules still apply"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Your confidence propels you into battle. You gain a bonus to your initiative rolls equal to "
            "your Charisma modifier.\n"
            "You also gain an additional way to use your Sneak Attack; you don't need advantage on the "
            "attack roll to use your Sneak Attack against a creature if you are within 5 feet of it, no "
            "other creatures are within 5 feet of you, and you don't have disadvantage on the attack roll. "
            "All the other rules for Sneak Attack still apply to you."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class Panache(Feature):
    def __init__(self):
        super().__init__(
            name="Panache",
            origin="Swashbuckler Rogue Level 9",
            activation=FeatureActivation(
                action_type=ActionType.ACTION, duration="1 Minute"
            ),
            usage_tags=["control"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Your charm becomes extraordinarily beguiling."),
            Facts(
                (
                    ("Action", "Action"),
                    (
                        "Target",
                        "A creature that can hear you and shares a language with you",
                    ),
                    (
                        "Contest",
                        "Your Charisma (Persuasion) against its Wisdom (Insight)",
                    ),
                )
            ),
            Option(
                "You win",
                (
                    Table(
                        ("Target is", "Effect"),
                        (
                            (
                                "Hostile",
                                "For 1 minute it has disadvantage on attacks against anyone but you and can't make opportunity attacks against anyone but you. Ends if a companion attacks it or affects it with a spell, or you're more than 60 feet apart.",
                            ),
                            (
                                "Not hostile",
                                "Charmed by you for 1 minute, regarding you as a friendly acquaintance. Ends at once if you or your companions harm it.",
                            ),
                        ),
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Your charm becomes extraordinarily beguiling. As an action, you can make a Charisma "
            "(Persuasion) check contested by a creature's Wisdom (Insight) check. The creature must be "
            "able to hear you, and the two of you must share a language.\n"
            "If you succeed on the check and the creature is hostile to you, it has disadvantage on "
            "attack rolls against targets other than you and can't make opportunity attacks against "
            "targets other than you. This effect lasts for 1 minute, until one of your companions attacks "
            "the target or affects it with a spell, or until you and the target are more than 60 feet "
            "apart.\n"
            "If you succeed on the check and the creature isn't hostile to you, it is charmed by you for "
            "1 minute. While charmed, it regards you as a friendly acquaintance. This effect ends "
            "immediately if you or your companions do anything harmful to it."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.CREATURE


class ElegantManeuver(Feature):
    def __init__(self):
        super().__init__(
            name="Elegant Maneuver",
            origin="Swashbuckler Rogue Level 13",
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION, duration="Until End of Your Turn"
            ),
            usage_tags=["buff"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Action", "Bonus Action on your turn"),
                    (
                        "Effect",
                        "Advantage on the next Dexterity (Acrobatics) or Strength (Athletics) check you make during the same turn",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You can use a bonus action on your turn to gain advantage on the next Dexterity (Acrobatics) "
            "or Strength (Athletics) check you make during the same turn."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class MasterDuelist(Feature):
    def __init__(self):
        super().__init__(
            name="Master Duelist",
            origin="Swashbuckler Rogue Level 17",
            usage_tags=["buff"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "Your mastery of the blade lets you turn failure into success in combat."
            ),
            Facts(
                (
                    ("Trigger", "You miss with an attack roll"),
                    ("Effect", "Roll it again with Advantage"),
                    ("Frequency", "Once per Short or Long Rest"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Your mastery of the blade lets you turn failure into success in combat. If you miss with an "
            "attack roll, you can roll it again with advantage. Once you do so, you can't use this feature "
            "again until you finish a short or long rest."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF
