from Core.Definitions import Ability
from Model.Content.Feature import Feature, FeatureActivation, ActionType, FeatureTarget
from Model.Content.Improvements import MultiAbilityArmorClass
from Model.Ledger.LedgerWriter import LedgerWriter
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Paragraph


class DazzlingFootwork(Feature):
    def __init__(self):
        super().__init__(
            name="Dazzling Footwork",
            origin="College of Dance Bard Level 3",
            usage_tags=["buff", "damage"],
        )
        # "While you aren't wearing armor or wielding a Shield... Unarmored
        # Defense. Your base Armor Class equals 10 plus your Dexterity and
        # Charisma modifiers."
        self._ac = MultiAbilityArmorClass(
            10, [Ability.DEXTERITY, Ability.CHARISMA], allows_shield=False
        )

    def apply(self, ledger_writer: LedgerWriter):
        self._ac.apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("While you aren't wearing armor or wielding a Shield:"),
            Facts(
                (
                    (
                        "Dance Virtuoso",
                        "Advantage on Charisma (Performance) checks that involve dancing",
                    ),
                    (
                        "Unarmored Defense",
                        "Base AC = 10 + Dexterity modifier + Charisma modifier",
                    ),
                    (
                        "Agile Strikes",
                        "When you expend Bardic Inspiration as part of an action, Bonus Action or Reaction, make one Unarmed Strike as part of it",
                    ),
                    (
                        "Bardic Damage",
                        "Use Dexterity for Unarmed Strike attack rolls. Damage: Bludgeoning equal to a roll of your Bardic Inspiration die + Dexterity modifier, without expending the die.",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "While you aren't wearing armor or wielding a Shield, you gain the following benefits.\n"
            "Dance Virtuoso. You have Advantage on any Charisma (Performance) check you make that involves you dancing.\n"
            "Unarmored Defense. Your base Armor Class equals 10 plus your Dexterity and Charisma modifiers.\n"
            "Agile Strikes. When you expend a use of your Bardic Inspiration as part of an action, a Bonus Action, or a Reaction, you can make one Unarmed Strike as part of that action, Bonus Action, or Reaction.\n"
            "Bardic Damage. You can use Dexterity instead of Strength for the attack rolls of your Unarmed Strikes. When you deal damage with an Unarmed Strike, you can deal Bludgeoning damage equal to a roll of your Bardic Inspiration die plus your Dexterity modifier, instead of the strike's normal damage. This roll doesn't expend the die."
        )
        return description


class InspiringMovement(Feature):
    def __init__(self):
        super().__init__(
            name="Inspiring Movement",
            origin="College of Dance Bard Level 6",
            activation=FeatureActivation(
                action_type=ActionType.REACTION, range="30 Feet"
            ),
            usage_tags=["buff"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Action", "Reaction"),
                    (
                        "Trigger",
                        "An enemy you can see ends its turn within 5 feet of you",
                    ),
                    ("Cost", "One use of Bardic Inspiration"),
                    (
                        "Effect",
                        "Move up to half your Speed; then one ally of your choice within 30 feet can use its Reaction to move up to half its Speed",
                    ),
                    ("Safe", "None of this movement provokes Opportunity Attacks"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "When an enemy you can see ends its turn within 5 feet of you, you can take a Reaction and expend one use of your Bardic Inspiration to move up to half your Speed. Then one ally of your choice within 30 feet of you can also move up to half their Speed using their Reaction.\n"
            "None of this feature's movement provokes Opportunity Attacks."
        )
        return description


class TandemFootwork(Feature):
    def __init__(self):
        super().__init__(
            name="Tandem Footwork",
            origin="College of Dance Bard Level 6",
            activation=FeatureActivation(range="30 Feet"),
            usage_tags=["buff"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Trigger",
                        "You roll Initiative and don't have the Incapacitated condition",
                    ),
                    ("Cost", "One use of Bardic Inspiration"),
                    (
                        "Effect",
                        "Roll your Bardic Inspiration die; you and each ally within 30 feet who can see or hear you add it to Initiative",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "When you roll Initiative, you can expend one use of your Bardic Inspiration if you don't have the Incapacitated condition. When you do so, roll your Bardic Inspiration die; you and each ally within 30 feet of you who can see or hear you gains a bonus to Initiative equal to the number rolled."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY


class LeadingEvasion(Feature):
    def __init__(self):
        super().__init__(
            name="Leading Evasion",
            origin="College of Dance Bard Level 14",
            activation=FeatureActivation(range="5 Feet"),
            usage_tags=["buff"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Trigger",
                        "An effect lets you make a Dexterity save to take only half damage",
                    ),
                    ("Succeeded", "No damage"),
                    ("Failed", "Half damage"),
                    (
                        "Shared",
                        "Creatures within 5 feet of you making the same save gain this benefit too",
                    ),
                    (
                        "Exception",
                        "Can't be used while you have the Incapacitated condition",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "When you are subjected to an effect that allows you to make a Dexterity saving throw to take only half damage, you instead take no damage if you succeed on the saving throw and only half damage if you fail. If any creatures within 5 feet of you are making the same Dexterity saving throw, you can share this benefit with them for that save.\n"
            "You can't use this feature if you have the Incapacitated condition."
        )
        return description
