from Core.Definitions import (
    BARBARIAN_HIT_DIE,
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


class Frenzy(Feature):
    def __init__(self):
        super().__init__(
            name="Frenzy",
            origin="Path Of The Berserker Barbarian Level 3",
            usage_tags=["damage"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Trigger", "You use Reckless Attack while your Rage is active"),
                    (
                        "Damage",
                        "The first target you hit on your turn with a Strength-based attack takes extra damage: a number of d6s equal to your Rage Damage bonus",
                    ),
                    ("Type", "Same as the weapon or Unarmed Strike used"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "If you use Reckless Attack while your Rage is active, you deal extra damage to the first target you hit on your turn with a Strength-based attack. To determine the extra damage, roll a number of d6s equal to your Rage Damage bonus, and add them together. The damage has the same type as the weapon or Unarmed Strike used for the attack."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class MindlessRage(Feature):
    def __init__(self):
        super().__init__(
            name="Mindless Rage",
            origin="Path Of The Berserker Barbarian Level 6",
            usage_tags=["buff"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "While raging",
                        "Immunity to the Charmed and Frightened conditions",
                    ),
                    (
                        "Entering Rage",
                        "If you're Charmed or Frightened, the condition ends",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "You have Immunity to the Charmed and Frightened conditions while your Rage is active. If you're Charmed or Frightened when you enter your Rage, the condition ends on you."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class Retaliation(Feature):
    def __init__(self):
        super().__init__(
            name="Retaliation",
            origin="Path Of The Berserker Barbarian Level 10",
            activation=FeatureActivation(
                action_type=ActionType.REACTION, range="5 Feet"
            ),
            usage_tags=["damage"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Action", "Reaction"),
                    ("Trigger", "You take damage from a creature within 5 feet of you"),
                    (
                        "Effect",
                        "Make one melee attack against it, with a weapon or an Unarmed Strike",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "When you take damage from a creature that is within 5 feet of you, you can take a Reaction to make one melee attack against that creature, using a weapon or an Unarmed Strike."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class IntimidatingPresence(Feature):
    def __init__(self):
        super().__init__(
            name="Intimidating Presence",
            origin="Path Of The Berserker Barbarian Level 14",
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION,
                duration="1 Minute",
                range="30-Foot Emanation",
            ),
            usage_tags=["control"],
            uses=FeatureUses(max_uses=1, regain_all_on="long rest"),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # The once-per-Long-Rest box is in the panel below.
        return [
            Paragraph("Strike terror with your menacing presence."),
            Facts(
                (
                    ("Action", "Bonus Action"),
                    ("Area", "30-foot Emanation"),
                    ("Target", "Each creature of your choice in it"),
                    ("Save", f"Wisdom, DC {dc_formula(Ability.STRENGTH)}"),
                    (
                        "Failed",
                        "Frightened for 1 minute; it repeats the save at the end of each of its turns, ending the effect on a success",
                    ),
                    (
                        "Recharge",
                        "Once per Long Rest, or expend a use of Rage (no action required) to restore it",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "As a Bonus Action, you can strike terror into others with your menacing presence and primal power. When you do so, each creature of your choice in a 30-foot Emanation originating from you must make a Wisdom saving throw (DC 8 plus your Strength modifier and Proficiency Bonus). On a failed save, a creature has the Frightened condition for 1 minute. At the end of each of the Frightened creature's turns, the creature repeats the save, ending the effect on itself on a success.\n"
            "Once you use this feature, you can't use it again until you finish a Long Rest unless you expend a use of your Rage (no action required) to restore your use of it."
        )
        return description

    def calculate_dc(self, character: CharacterView) -> int:
        strength_modifier = character.get_strength_modifier()
        proficiency_bonus = character.get_proficiency_bonus()
        return 8 + strength_modifier + proficiency_bonus

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.AREA
