from Model.Content.Feature import (
    FeatureUses,
    Feature,
    FeatureActivation,
    ActionType,
    RegainedOn,
    FeatureTarget,
)
from Core.Rules import MAX_ABILITY_MODIFIER
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Option, Paragraph


class ManifestEcho(Feature):
    def __init__(self):
        super().__init__(
            name="Manifest Echo",
            origin="Echo Knight Fighter Level 3",
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION, range="15 Feet"
            ),
            usage_tags=["damage", "utility"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Manifest a translucent gray echo of yourself to fight from."),
            Facts(
                (
                    ("Action", "Bonus Action"),
                    ("Range", "An unoccupied space you can see within 15 feet"),
                    (
                        "Lasts",
                        "Until it's destroyed, you dismiss it (Bonus Action), you manifest another, or you're Incapacitated",
                    ),
                    (
                        "Echo",
                        "AC 14 + Proficiency Bonus, 1 Hit Point, immune to all conditions; uses your saving throw bonuses; your size, and it occupies its space",
                    ),
                )
            ),
            Option(
                "Using the echo",
                (
                    Facts(
                        (
                            (
                                "Move it",
                                "On your turn, up to 30 feet in any direction (no action required). It's destroyed if it ends your turn more than 30 feet from you.",
                            ),
                            (
                                "Swap",
                                "Bonus Action: teleport to swap places with it, costing 15 feet of movement",
                            ),
                            (
                                "Attack",
                                "Each attack of your Attack action can come from your space or the echo's",
                            ),
                            (
                                "Opportunity Attack",
                                "Reaction when a creature you can see within 5 feet of the echo moves 5 feet or more away from it, as if you were in the echo's space",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "At 3rd level, you can use a bonus action to magically manifest an echo of yourself in an unoccupied space you can see within 15 feet of you. This echo is a magical, translucent, gray image of you that lasts until it is destroyed, until you dismiss it as a bonus action, until you manifest another echo, or until you're incapacitated.\n"
            "\n"
            "Your echo has AC 14 + your proficiency bonus, 1 hit point, and immunity to all conditions. If it has to make a saving throw, it uses your saving throw bonus for the roll. It is the same size as you, and it occupies its space. On your turn, you can mentally command the echo to move up to 30 feet in any direction (no action required). If your echo is ever more than 30 feet from you at the end of your turn, it is destroyed.\n"
            "\n"
            "As a bonus action, you can teleport, magically swapping places with your echo at a cost of 15 feet of your movement, regardless of the distance between the two of you.\n"
            "\n"
            "When you take the Attack action on your turn, any attack you make with that action can originate from your space or the echo's space. You make this choice for each attack.\n"
            "\n"
            "When a creature that you can see within 5 feet of your echo moves at least 5 feet away from it, you can use your reaction to make an opportunity attack against that creature as if you were in the echo's space."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY


class UnleashIncarnation(Feature):
    def __init__(self):
        super().__init__(
            name="Unleash Incarnation",
            origin="Echo Knight Fighter Level 3",
            usage_tags=["damage"],
            uses=FeatureUses(
                max_uses=MAX_ABILITY_MODIFIER,
                regain_all_on="long rest",
                current_formula="Current amount: equal to your Constitution modifier.",
            ),
        )

    def number_of_uses(self, character: CharacterView) -> int:
        return max(1, character.get_constitution_modifier())

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # Uses (Constitution modifier, minimum of once) are in the panel below.
        return [
            Paragraph("Heighten your echo's fury."),
            Facts(
                (
                    ("Trigger", "You take the Attack action"),
                    (
                        "Effect",
                        "Make one additional melee attack from the echo's position",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "At 3rd level, you can heighten your echo's fury. Whenever you take the Attack action, you can make one additional melee attack from the echo's position.\n"
            "\n"
            "You can use this feature a number of times equal to your Constitution modifier (a minimum of once). You regain all expended uses when you finish a long rest."
        )
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class EchoAvatar(Feature):
    def __init__(self):
        super().__init__(
            name="Echo Avatar",
            origin="Echo Knight Fighter Level 7",
            activation=FeatureActivation(
                action_type=ActionType.ACTION,
                duration="Up to 10 Minutes",
                range="1,000 Feet",
            ),
            usage_tags=["utility"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Temporarily transfer your consciousness to your echo."),
            Facts(
                (
                    ("Action", "Action"),
                    (
                        "Effect",
                        "See through your echo's eyes and hear through its ears",
                    ),
                    ("Drawback", "You're Blinded and Deafened while you do"),
                    ("Duration", "Up to 10 minutes; end it at any time (no action)"),
                    (
                        "Range",
                        "Your echo can be up to 1,000 feet away without being destroyed",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "Starting at 7th level, you can temporarily transfer your consciousness to your echo. As an action, you can see through your echo's eyes and hear through its ears. During this time, you are deafened and blinded. You can sustain this effect for up to 10 minutes, and you can end it at any time (requires no action). While your echo is being used in this way, it can be up to 1,000 feet away from you without being destroyed."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class ShadowMartyr(Feature):
    def __init__(self):
        super().__init__(
            name="Shadow Martyr",
            origin="Echo Knight Fighter Level 10",
            activation=FeatureActivation(
                action_type=ActionType.REACTION, range="5 Feet"
            ),
            usage_tags=["buff"],
            uses=FeatureUses(max_uses=1, regain_all_on="short or long rest"),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # The once-per-Short-or-Long-Rest box is in the panel below.
        return [
            Paragraph(
                "Make your echo throw itself in front of an attack directed at another creature."
            ),
            Facts(
                (
                    ("Action", "Reaction, before the attack roll is made"),
                    (
                        "Trigger",
                        "An attack is directed at another creature you can see",
                    ),
                    (
                        "Effect",
                        "Teleport the echo to an unoccupied space within 5 feet of the targeted creature; the attack roll is made against the echo instead",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "Starting at 10th level, you can make your echo throw itself in front of an attack directed at another creature that you can see. Before the attack roll is made, you can use your reaction to teleport the echo to an unoccupied space within 5 feet of the targeted creature. The attack roll that triggered the reaction is instead made against your echo.\n\nOnce you use this feature, you can't use it again until you finish a short or long rest."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY


class ReclaimPotential(Feature):
    def __init__(self):
        super().__init__(
            name="Reclaim Potential",
            origin="Echo Knight Fighter Level 15",
            usage_tags=["buff"],
            uses=FeatureUses(
                max_uses=MAX_ABILITY_MODIFIER,
                regain_all_on="long rest",
                current_formula="Current amount: equal to your Constitution modifier.",
            ),
        )

    def number_of_uses(self, character: CharacterView) -> int:
        return max(1, character.get_constitution_modifier())

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # Uses (Constitution modifier, minimum of once) are in the panel below.
        return [
            Paragraph("Absorb the fleeting magic of your echo."),
            Facts(
                (
                    ("Trigger", "An echo of yours is destroyed by taking damage"),
                    ("Temporary HP", "2d6 + Constitution modifier"),
                    ("Requirement", "You don't already have Temporary Hit Points"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "By 15th level, you've learned to absorb the fleeting magic of your echo. When an echo of yours is destroyed by taking damage, you can gain a number of temporary hit points equal to 2d6 + your Constitution modifier, provided you don't already have temporary hit points.\n"
            "\n"
            "You can use this feature a number of times equal to your Constitution modifier (a minimum of once). You regain all expended uses when you finish a long rest."
        )
        description += f"\nRight now: 2d6 + {character.get_constitution_modifier()} temporary hit points."
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class LegionOfOne(Feature):
    def __init__(self):
        super().__init__(
            name="Legion of One",
            origin="Echo Knight Fighter Level 18",
            activation=FeatureActivation(action_type=ActionType.BONUS_ACTION),
            usage_tags=["damage", "utility"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Two echoes",
                        "As a Bonus Action, create two echoes with Manifest Echo; they can co-exist",
                    ),
                    ("Third echo", "Creating one destroys the previous two"),
                    (
                        "Either position",
                        "Anything you can do from one echo's position can be done from the other's instead",
                    ),
                    (
                        "Initiative",
                        "If you have no uses of Unleash Incarnation left, regain one",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "At 18th level, you can use a bonus action to create two echoes with your Manifest Echo feature, and these echoes can co-exist. If you try to create a third echo, the previous two echoes are destroyed. Anything you can do from one echo's position can be done from the other's instead.\n"
            "\n"
            "In addition, when you roll initiative and have no uses of your Unleash Incarnation feature left, you regain one use of that feature."
        )
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.INITIATIVE_ROLL
