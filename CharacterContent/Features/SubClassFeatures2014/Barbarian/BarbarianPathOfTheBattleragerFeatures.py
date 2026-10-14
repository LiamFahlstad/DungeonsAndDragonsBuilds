from Model.Content.Feature import Feature, FeatureActivation, ActionType, FeatureTarget
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts


class BattleragerArmor(Feature):
    def __init__(self):
        super().__init__(
            name="Battlerager Armor",
            origin="Path Of The Battlerager Barbarian Level 3",
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION, range="5 Feet"
            ),
            usage_tags=["damage"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Restriction", "Only dwarves can follow this path"),
                    (
                        "Spike attack",
                        "While raging in spiked armor: bonus action melee weapon attack with the spikes against a target within 5 feet, Strength for attack and damage, 1d4 piercing damage",
                    ),
                    (
                        "Grapple",
                        "When you use the Attack action to grapple and succeed, the target takes 3 piercing damage",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Restriction: Only dwarves can follow the Path of the Battlerager.\n"
            "\n"
            "When you choose this path at 3rd level, you gain the ability to use spiked armor as a weapon.\n"
            "\n"
            "While you are wearing spiked armor and are raging, you can use a bonus action to make one melee weapon attack with your armor spikes against a target within 5 feet of you. If the attack hits, the spikes deal 1d4 piercing damage. You use your Strength modifier for the attack and damage rolls.\n"
            "\n"
            "Additionally, when you use the Attack action to grapple a creature, the target takes 3 piercing damage if your grapple check succeeds."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class RecklessAbandon(Feature):
    def __init__(self):
        super().__init__(
            name="Reckless Abandon",
            origin="Path Of The Battlerager Barbarian Level 6",
            activation=FeatureActivation(duration="Until Your Rage Ends"),
            usage_tags=["heal"],
        )

    def get_description(self, character: CharacterView) -> str:
        description = "Beginning at 6th level, when you use Reckless Attack while raging, you also gain temporary hit points equal to your Constitution modifier (minimum of 1). They vanish if any of them are left when your rage ends."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class BattleragerCharge(Feature):
    def __init__(self):
        super().__init__(
            name="Battlerager Charge",
            origin="Path Of The Battlerager Barbarian Level 10",
            activation=FeatureActivation(action_type=ActionType.BONUS_ACTION),
            usage_tags=["utility"],
        )

    def get_description(self, character: CharacterView) -> str:
        description = "Beginning at 10th level, you can take the Dash action as a bonus action while you are raging."
        return description


class SpikedRetribution(Feature):
    def __init__(self):
        super().__init__(
            name="Spiked Retribution",
            origin="Path Of The Battlerager Barbarian Level 14",
            activation=FeatureActivation(range="5 Feet"),
            usage_tags=["damage"],
        )

    def get_description(self, character: CharacterView) -> str:
        description = "Starting at 14th level, when a creature within 5 feet of you hits you with a melee attack, the attacker takes 3 piercing damage if you are raging, aren't incapacitated, and are wearing spiked armor."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY
