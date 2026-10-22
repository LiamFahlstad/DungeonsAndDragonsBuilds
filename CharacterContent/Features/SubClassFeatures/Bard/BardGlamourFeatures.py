from Core.Definitions import (
    Ability,
)
from Model.Content.Feature import (
    ActionType,
    Feature,
    FeatureActivation,
    FeatureTarget,
    FeatureUses,
)
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Paragraph, dc_formula


class BeguilingMagic(Feature):
    def __init__(self):
        super().__init__(
            name="Beguiling Magic",
            origin="College of Glamour Bard Level 3",
            activation=FeatureActivation(duration="1 Minute", range="60 Feet"),
            usage_tags=["control"],
            uses=FeatureUses(max_uses=1, regain_all_on="long rest"),
        )

    def calculate_dc(self, character: CharacterView) -> int:
        return character.calculate_difficulty_class_for_ability(Ability.CHARISMA)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # The once-per-Long-Rest box is in the panel below.
        return [
            Paragraph("You always have Charm Person and Mirror Image prepared."),
            Facts(
                (
                    (
                        "Trigger",
                        "Immediately after you cast an Enchantment or Illusion spell using a spell slot",
                    ),
                    ("Target", "A creature you can see within 60 feet"),
                    (
                        "Save",
                        f"Wisdom save against your spell save DC ({dc_formula(Ability.CHARISMA)})",
                    ),
                    (
                        "Failed",
                        "Charmed or Frightened (your choice) for 1 minute; it repeats the save at the end of each of its turns, ending the effect on a success",
                    ),
                    (
                        "Limit",
                        "Once per Long Rest; expend a Bardic Inspiration use (no action required) to use it again",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You always have the Charm Person and Mirror Image spells prepared.\n"
            "In addition, immediately after you cast an Enchantment or Illusion spell using a spell slot, you can cause a creature you can see within 60 feet of yourself to make a Wisdom saving throw against your spell save DC. On a failed save, the target has the Charmed or Frightened condition (your choice) for 1 minute. The target repeats the save at the end of each of its turns, ending the effect on itself on a success.\n"
            "Once you use this benefit, you can't use it again until you finish a Long Rest. You can also restore your use of it by expending one use of your Bardic Inspiration (no action required)."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class MantleOfInspiration(Feature):
    def __init__(self):
        super().__init__(
            name="Mantle of Inspiration",
            origin="College of Glamour Bard Level 3",
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION, range="60 Feet"
            ),
            usage_tags=["heal", "buff"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Fill others with vigor through fey song or dance."),
            Facts(
                (
                    ("Action", "Bonus Action"),
                    ("Cost", "One use of Bardic Inspiration; roll the die"),
                    ("Range", "60 feet"),
                    ("Target", "Up to Charisma modifier (minimum one) other creatures"),
                    (
                        "Effect",
                        "Each gains 2 x the roll Temporary Hit Points, then can use its Reaction to move up to its Speed without provoking Opportunity Attacks",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "You can weave fey magic into a song or dance to fill others with vigor. As a Bonus Action, you can expend a use of Bardic Inspiration, rolling a Bardic Inspiration die. When you do so, choose a number of other creatures within 60 feet of yourself, up to a number equal to your Charisma modifier (minimum of one creature). Each of those creatures gains a number of Temporary Hit Points equal to two times the number rolled on the Bardic Inspiration die, and then each can use its Reaction to move up to its Speed without provoking Opportunity Attacks."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY


class MantleOfMajesty(Feature):
    def __init__(self):
        super().__init__(
            name="Mantle of Majesty",
            origin="College of Glamour Bard Level 6",
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION,
                duration="1 Minute or Until Concentration Ends",
            ),
            usage_tags=["control"],
            uses=FeatureUses(max_uses=1, regain_all_on="long rest"),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # The once-per-Long-Rest box is in the panel below.
        return [
            Facts(
                (
                    ("Command", "Always prepared"),
                    (
                        "Action",
                        "Bonus Action: cast Command without a spell slot and take on an unearthly appearance",
                    ),
                    ("Duration", "1 minute, or until your Concentration ends"),
                    (
                        "Meanwhile",
                        "Cast Command as a Bonus Action without a spell slot each turn. Creatures Charmed by you automatically fail their saves against it.",
                    ),
                    (
                        "Recharge",
                        "Once per Long Rest, or expend a level 3+ spell slot (no action required)",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You always have the Command spell prepared.\n"
            "As a Bonus Action, you cast Command without expending a spell slot, and you take on an unearthly appearance for 1 minute or until your Concentration ends. During this time, you can cast Command as a Bonus Action without expending a spell slot,\n"
            "Any creature Charmed by you automatically fails its saving throw against the Command you cast with this feature.\n"
            "Once you use this feature, you can't use it again until you finish a Long Rest. You can also restore your use of it by expending a level 3+ spell slot (no action required)."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class UnbreakableMajesty(Feature):
    def __init__(self):
        super().__init__(
            name="Unbreakable Majesty",
            origin="College of Glamour Bard Level 14",
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION,
                duration="1 Minute or Until Incapacitated",
            ),
            usage_tags=["buff"],
        )

    def calculate_dc(self, character: CharacterView) -> int:
        return character.calculate_difficulty_class_for_ability(Ability.CHARISMA)

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Assume a magically majestic presence."),
            Facts(
                (
                    ("Action", "Bonus Action"),
                    ("Duration", "1 minute, or until you're Incapacitated"),
                    (
                        "Trigger",
                        "A creature hits you with an attack roll for the first time on a turn",
                    ),
                    (
                        "Save",
                        f"Charisma save against your spell save DC ({dc_formula(Ability.CHARISMA)})",
                    ),
                    ("Failed", "The attack misses instead"),
                    ("Limit", "Once per Short or Long Rest"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "As a Bonus Action, you can assume a magically majestic presence for 1 minute or until you have the Incapacitated condition. For the duration, whenever any creature hits you with an attack roll for the first time on a turn, the attacker must succeed on a Charisma saving throw against your spell save DC, or the attack misses instead, as the creature recoils from your majesty.\n"
            "Once you assume this majestic presence, you can't do so again until you finish a Short or Long Rest."
        )
        return description
