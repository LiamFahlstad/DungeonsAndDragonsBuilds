from Core.Definitions import Ability
from Model.Content.Feature import (
    Feature,
    FeatureUses,
    FeatureActivation,
    ActionType,
    FeatureTarget,
)
from Core.Rules import MAX_ABILITY_MODIFIER
from Model.View import CharacterView
from Model.Content.FeatureText import (
    Block,
    Facts,
    Paragraph,
    dc_formula,
)


class ChronalShift(Feature):
    def __init__(self):
        super().__init__(
            name="Chronal Shift",
            origin="Chronurgy Wizard Level 3",
            activation=FeatureActivation(
                action_type=ActionType.REACTION, range="30 Feet"
            ),
            uses=FeatureUses(max_uses=2, regain_all_on="long rest"),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # Uses are in the panel below.
        return [
            Facts(
                (
                    ("Action", "Reaction"),
                    (
                        "Trigger",
                        "After you or a creature you can see within 30 feet makes an attack roll, ability check or saving throw, once you see if it succeeds",
                    ),
                    ("Effect", "It rerolls and must use the new roll"),
                    ("Uses", "Twice per long rest"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "At 2nd level, you can magically exert limited control over the flow of time around a creature. As a reaction, after you or a creature you can see within 30 feet of you makes an attack roll, an ability check, or a saving throw, you can force the creature to reroll. You make this decision after you see whether the roll succeeds or fails. The target must use the result of the second roll.\n"
            "\n"
            "You can use this ability twice, and you regain any expended uses when you finish a long rest."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.CREATURE


class TemporalAwareness(Feature):
    def __init__(self):
        super().__init__(name="Temporal Awareness", origin="Chronurgy Wizard Level 3")

    def get_description(self, character: CharacterView) -> str:
        description = "Starting at 2nd level, you can add your Intelligence modifier to your initiative rolls."
        return description


class MomentaryStasis(Feature):
    def __init__(self):
        super().__init__(
            name="Momentary Stasis",
            origin="Chronurgy Wizard Level 6",
            activation=FeatureActivation(
                action_type=ActionType.ACTION,
                duration="Until End Of Your Next Turn Or Until Takes Damage",
                range="60 Feet",
            ),
            usage_tags=["control"],
            uses=FeatureUses(
                max_uses=MAX_ABILITY_MODIFIER,
                regain_all_on="long rest",
                current_formula="Current amount: equal to your Intelligence modifier.",
            ),
        )

    def calculate_dc(self, character: CharacterView) -> int:
        return character.calculate_difficulty_class_for_ability(Ability.INTELLIGENCE)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # Uses are in the panel below.
        return [
            Facts(
                (
                    ("Action", "Action"),
                    ("Range", "60 feet"),
                    ("Target", "A Large or smaller creature you can see"),
                    (
                        "Save",
                        f"Constitution save against your spell save DC ({dc_formula(Ability.INTELLIGENCE)})",
                    ),
                    (
                        "Failed",
                        "Encased until the end of your next turn or until it takes damage: incapacitated, speed 0",
                    ),
                    ("Uses", "Intelligence modifier (minimum once) per long rest"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "When you reach 6th level, as an action, you can magically force a Large or smaller creature you can see within 60 feet of you to make a Constitution saving throw against your spell save DC. Unless the saving throw is a success, the creature is encased in a field of magical energy until the end of your next turn or until the creature takes any damage. While encased in this way, the creature is incapacitated and has a speed of 0.\n"
            "\n"
            "You can use this feature a number of times equal to your Intelligence modifier (minimum of once), and you regain all expended uses when you finish a long rest."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY

    def number_of_uses(self, character: CharacterView) -> int:
        return max(1, character.get_intelligence_modifier())


class ArcaneAbeyance(Feature):
    def __init__(self):
        super().__init__(
            name="Arcane Abeyance",
            origin="Chronurgy Wizard Level 10",
            activation=FeatureActivation(duration="1 Hour"),
            uses=FeatureUses(max_uses=1, regain_all_on="short or long rest"),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # The once-per-rest box is in the panel below.
        return [
            Paragraph("Freeze a spell in a bead for someone else to release."),
            Facts(
                (
                    (
                        "Trigger",
                        "You cast a spell using a spell slot of 4th level or lower",
                    ),
                    (
                        "Bead",
                        "Tiny, AC 15, 1 hit point, immune to poison and psychic damage. Lasts 1 hour; when it ends or the bead is destroyed, the spell is lost.",
                    ),
                    (
                        "Release",
                        "A creature holding it uses its action; the spell uses your spell attack bonus and save DC, and treats that creature as the caster otherwise",
                    ),
                    ("Limit", "Once per short or long rest"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "At 10th level, when you cast a spell using a spell slot of 4th level or lower, you can condense the spell's magic into a mote. The spell is frozen in time at the moment of casting and held within a gray bead for 1 hour. This bead is a Tiny object with AC 15 and 1 hit point, and it is immune to poison and psychic damage. When the duration ends, or if the bead is destroyed, it vanishes in a flash of light, and the spell is lost.\n"
            "\n"
            "A creature holding the bead can use its action to release the spell within, whereupon the bead disappears. The spell uses your spell attack bonus and save DC, and the spell treats the creature who released it as the caster for all other purposes.\n"
            "\n"
            "Once you create a bead with this feature, you can't do so again until you finish a short or long rest."
        )
        return description


class ConvergentFuture(Feature):
    def __init__(self):
        super().__init__(
            name="Convergent Future",
            origin="Chronurgy Wizard Level 14",
            activation=FeatureActivation(
                action_type=ActionType.REACTION, range="60 Feet"
            ),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Action", "Reaction"),
                    (
                        "Trigger",
                        "You or a creature you can see within 60 feet makes an attack roll, ability check or saving throw",
                    ),
                    (
                        "Effect",
                        "Ignore the die: the roll is exactly the number needed to succeed, or one less (your choice)",
                    ),
                    (
                        "Cost",
                        "You gain one level of exhaustion, removed only by a long rest",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Starting at 14th level, you can peer through possible futures and magically pull one of them into events around you, ensuring a particular outcome. When you or a creature you can see within 60 feet of you makes an attack roll, an ability check, or a saving throw, you can use your reaction to ignore the die roll and decide whether the number rolled is the minimum needed to succeed or one less than that number (your choice).\n"
            "\n"
            "When you use this feature, you gain one level of exhaustion. Only by finishing a long rest can you remove a level of exhaustion gained in this way."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.CREATURE
