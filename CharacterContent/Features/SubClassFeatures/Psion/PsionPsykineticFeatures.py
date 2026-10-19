from Core.Definitions import PSION_HIT_DIE, Ability
from Model.Content.Feature import Feature, FeatureActivation, FeatureTarget
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Option, Paragraph, dc_formula


class StrongerTelekinesis(Feature):
    def __init__(self):
        super().__init__(name="Stronger Telekinesis", origin="Psykinetic Psion Level 3")

    def get_description(self, character: CharacterView) -> str:
        description = (
            "When you cast Mage Hand, its range increases by 30 "
            "feet when you cast it, and the hand can carry up to "
            "20 pounds."
        )
        return description


class TelekineticTechniques(Feature):
    def __init__(self):
        super().__init__(
            name="Telekinetic Techniques",
            origin="Psykinetic Psion Level 3",
            usage_tags=["buff", "control", "damage"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Telekinetic Propel improves."),
            Facts(
                (("Free die", "Roll 1d4 instead of expending a Psionic Energy Die"),)
            ),
            Option(
                "On a failed save, add one",
                (
                    Facts(
                        (
                            (
                                "Boost",
                                "Its Speed increases by 10 feet until the start of your next turn",
                            ),
                            (
                                "Disorient",
                                "It can't make Opportunity Attacks until the start of its next turn",
                            ),
                            (
                                "Telekinetic Bolt",
                                "It takes Force damage equal to the Psionic Energy Die roll",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "When you use Telekinetic Propel, you can roll 1d4 "
            "and use the number rolled instead of expending a "
            "Psionic Energy Die.\n"
            "In addition, when a target fails the saving throw "
            "against your Telekinetic Propel, you can impose one "
            "of the following effects on that target "
            "Boost. The target's Speed increases by 10 feet "
            "until the start of your next turn.\n"
            "Disorient. The target can't make Opportunity "
            "Attacks until the start of its next turn.\n"
            "Telekinetic Bolt. The target takes Force damage "
            "equal to the number rolled on the Psionic Energy "
            "Die."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class DestructiveTrance(Feature):
    def __init__(self):
        super().__init__(
            name="Destructive Trance",
            origin="Psykinetic Psion Level 6",
            activation=FeatureActivation(duration="10 Minutes"),
            usage_tags=["buff", "damage", "utility"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("When", "At the start of your turn"),
                    ("Cost", "One Psionic Energy Die"),
                    ("Duration", "10 minutes"),
                    ("Flight", "A Fly Speed of 20 feet, and you can hover"),
                    (
                        "Damage",
                        "When you cast a Psion spell that expends a spell slot, roll your Psionic Energy Die and add it to one damage roll (the roll doesn't expend the die)",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "At the start of your turn, you can expend one Psionic "
            "Energy Die to enter a destructive state. For the next "
            "10 minutes, you gain a Fly Speed of 20 feet and can "
            "hover, and when you cast a Psion spell that expends "
            "a spell slot, you can roll your Psionic Energy Die and "
            "add the number rolled to one damage roll of that "
            "spell. This roll doesn't expend the Psionic Energy "
            "Die."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class ReboundingField(Feature):
    def __init__(self):
        super().__init__(
            name="Rebounding Field",
            origin="Psykinetic Psion Level 6",
            usage_tags=["damage", "buff"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Launch a blocked attack's force back at the attacker."),
            Facts(
                (
                    (
                        "Trigger",
                        "Your Shield, cast when hit by an attack roll, makes the attack miss",
                    ),
                    ("Cost", "One Psionic Energy Die; roll it"),
                    (
                        "Save",
                        f"The attacker makes a Dexterity save against your spell save DC ({dc_formula(Ability.INTELLIGENCE)})",
                    ),
                    (
                        "Failed",
                        "Force damage equal to the roll + Intelligence modifier",
                    ),
                    ("Succeeded", "Half damage"),
                    ("You", "Gain Temporary Hit Points equal to the damage dealt"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "When you cast Shield in response to being hit by an "
            "attack roll and cause the triggering attack to miss, "
            "you can expend one Psionic Energy Die to launch the "
            "force back at the attacker. The attacker makes a "
            "Dexterity saving throw. Roll one Psionic Energy Die. "
            "On a failed save, the attacker takes Force damage "
            "equal to the amount rolled plus your Intelligence "
            "modifier. On a successful save, the attacker takes "
            "half as much damage only. Whether the target fails "
            "or succeeds on the saving throw, you gain "
            "Temporary Hit Points equal to the amount of "
            "damage dealt."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class EnhancedTelekineticCrush(Feature):
    def __init__(self):
        super().__init__(
            name="Enhanced Telekinetic Crush",
            origin="Psykinetic Psion Level 10",
            usage_tags=["damage", "control"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Trigger", "You cast Telekinetic Crush"),
                    ("Cost", "One Psionic Energy Die"),
                    (
                        "Slow",
                        "Whether a creature fails or succeeds on its save, its Speed is halved until the start of your next turn",
                    ),
                    ("Damage", "Roll the expended die and add it to one damage roll"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "When you cast Telekinetic Crush, you can expend one "
            "Psionic Energy Die to modify the spell so that "
            "whether a creature fails or succeeds on the saving "
            "throw against the spell, its Speed is halved until the "
            "start of your next turn. In addition, you can roll the "
            "expended Psionic Energy Die and add the number "
            "rolled to one damage roll of the spell."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class HeightenedTelekinesis(Feature):
    def __init__(self):
        super().__init__(
            name="Heightened Telekinesis", origin="Psykinetic Psion Level 14"
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Free casting",
                        "Cast Telekinesis by expending four Psionic Energy Dice instead of a spell slot",
                    ),
                    (
                        "No Concentration",
                        "Cast that way, it can skip Concentration: it lasts 1 minute, and you can concentrate on another spell",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You can cast Telekinesis without expending a spell "
            "slot by instead expending four Psionic Energy Dice. "
            "When you cast Telekinesis without expending a spell "
            "slot using this feature, you can modify the spell so "
            "that it doesn't require Concentration. If you do so, "
            "the spell's duration becomes 1 minute for that "
            "casting, and you can concentrate on another spell as normal."
        )
        return description
