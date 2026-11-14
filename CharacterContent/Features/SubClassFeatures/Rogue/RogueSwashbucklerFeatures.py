from Model.Content.Feature import (
    Feature,
    FeatureActivation,
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
                        "You make a melee attack roll against a creature during your turn",
                    ),
                    (
                        "Effect",
                        "That creature can't make Opportunity Attacks against you for the rest of that turn",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "You've learned how to land a strike and then slip away without reprisal. If you make a melee attack roll against a creature during your turn, that creature can't make Opportunity Attacks against you for the rest of that turn."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class RakishAudacity(Feature):
    def __init__(self):
        super().__init__(
            name="Rakish Audacity",
            origin="Swashbuckler Rogue Level 3",
            usage_tags=["buff"],
        )

    def apply(self, ledger_writer: LedgerWriter):
        # "When you roll Initiative, you can give yourself a bonus to the
        # roll equal to your Charisma modifier."
        InitiativeBonus(lambda cs: cs.get_charisma_modifier()).apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Initiative", "+ Charisma modifier"),
                    (
                        "Sneak Attack",
                        "No Advantage needed if you're within 5 feet of the target, no other creatures are within 5 feet of you, and you don't have Disadvantage on the attack roll",
                    ),
                    ("Other rules", "All other Sneak Attack rules still apply"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "When you roll Initiative, you can give yourself a bonus to the roll equal to your Charisma modifier.\n"
            "You also gain an additional way to use your Sneak Attack: You don't need Advantage on the attack roll to use your Sneak Attack against a creature if you are within 5 feet of it, no other creatures are within 5 feet of you, and you don't have Disadvantage on the attack roll. All the other rules for Sneak Attack still apply to you."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class Panache(Feature):
    def __init__(self):
        super().__init__(
            name="Panache",
            origin="Swashbuckler Rogue Level 9",
            usage_tags=["control"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("New Cunning Strike effects, using your Cunning Strike save DC."),
            Option(
                "New effects",
                (
                    Table(
                        ("Effect", "Cost", "Result"),
                        (
                            (
                                "Goad",
                                "1d6",
                                "Wisdom save. Failed: until the end of its next turn, Disadvantage on attack rolls against targets other than you, and it can't make Opportunity Attacks against targets other than you.",
                            ),
                            (
                                "Awe",
                                "3d6",
                                "Each creature of your choice within 30 feet of you makes a Wisdom save. Failed: Charmed until the end of your next turn.",
                            ),
                        ),
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You have practiced new ways to use your Sneak Attack. The following effects are now among your Cunning Strike options.\n"
            "Goad (Cost: 1d6). The target must succeed on a Wisdom saving throw, or until the end of its next turn, the target has Disadvantage on attack rolls against targets other than you and can't make Opportunity Attacks against targets other than you.\n"
            "Awe (Cost: 3d6). Each creature of your choice within 30 feet of you must succeed on a Wisdom saving throw or have the Charmed condition until the end of your next turn."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class DashingStrikes(Feature):
    def __init__(self):
        super().__init__(
            name="Dashing Strikes",
            origin="Swashbuckler Rogue Level 13",
            usage_tags=["buff"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("New Cunning Strike effects."),
            Option(
                "New effects",
                (
                    Table(
                        ("Effect", "Cost", "Result"),
                        (
                            (
                                "Invigorate",
                                "2d6",
                                "A creature you can see within 30 feet: until the end of its next turn, it adds 1d6 to each attack roll and saving throw it makes.",
                            ),
                            (
                                "Parrying Stance",
                                "2d6",
                                "Roll 1d6. Until the start of your next turn, you gain that much bonus to your AC.",
                            ),
                        ),
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You have practiced new ways to use your Sneak Attack. The following effects are now among your Cunning Strike options.\n"
            "Invigorate (Cost: 2d6). Choose a creature you can see within 30 feet of yourself. Until the end of that creature's next turn, whenever it makes an attack roll or a saving throw, it can roll 1d6 and add the number rolled to the attack roll or saving throw.\n"
            "Parrying Stance (Cost: 2d6). Roll 1d6. Until the start of your next turn, you gain a bonus to your AC equal to the number rolled."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.CREATURE


class MasterDuelist(Feature):
    def __init__(self):
        super().__init__(
            name="Master Duelist",
            origin="Swashbuckler Rogue Level 17",
            usage_tags=["damage"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Trigger", "Immediately after you use your Sneak Attack"),
                    ("Effect", "Make another attack against the same target"),
                    (
                        "Requirement",
                        "You're within 5 feet of the target and no other creatures are within 5 feet of you",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "Immediately after you use your Sneak Attack, you can make another attack against the same target, provided you are within 5 feet of it and no other creatures are within 5 feet of you."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY
