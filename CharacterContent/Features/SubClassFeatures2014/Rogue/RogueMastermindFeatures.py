from CharacterContent.Features.Core.BaseFeatures import (
    Feature,
    FeatureActivation,
    ActionType,
    FeatureTarget,
)
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class MasterOfIntrigue(Feature):
    def __init__(self):
        super().__init__(name="Master of Intrigue", origin="Mastermind Rogue Level 3", usage_tags=["utility"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain proficiency with the disguise kit, the forgery kit, and one gaming set of your choice. You also learn two languages of your choice.\n"
            "Additionally, you can unerringly mimic the speech patterns and accent of a creature that you hear speak for at least 1 minute, enabling you to pass yourself off as a native speaker of a particular land, provided that you know the language."
        )
        return description

    def target(self, character_stat_block: CharacterStatBlock) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class MasterOfTactics(Feature):
    def __init__(self):
        super().__init__(name="Master of Tactics", origin="Mastermind Rogue Level 3", activation=FeatureActivation(action_type=ActionType.BONUS_ACTION, range="30 Feet"), usage_tags=["buff"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can use the Help action as a bonus action. Additionally, when you use the Help action to aid an ally in attacking a creature, the target of that attack can be within 30 feet of you, rather than 5 feet of you, if the target can see or hear you."
        return description

    def target(self, character_stat_block: CharacterStatBlock) -> "FeatureTarget | None":
        return FeatureTarget.ALLY


class InsightfulManipulator(Feature):
    def __init__(self):
        super().__init__(name="Insightful Manipulator", origin="Mastermind Rogue Level 9", usage_tags=["utility"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "If you spend at least 1 minute observing or interacting with another creature outside combat, you can learn certain information about its capabilities compared to your own. The DM tells you if the creature is your equal, superior, or inferior in regard to two of the following characteristics of your choice:\n"
            "    * Intelligence score\n"
            "    * Wisdom score\n"
            "    * Charisma score\n"
            "    * Class levels (if any)\n"
            "At the DM's option, you might also realize you know a piece of the creature's history or one of its personality traits, if it has any."
        )
        return description

    def target(self, character_stat_block: CharacterStatBlock) -> "FeatureTarget | None":
        return FeatureTarget.CREATURE


class Misdirection(Feature):
    def __init__(self):
        super().__init__(name="Misdirection", origin="Mastermind Rogue Level 13", activation=FeatureActivation(action_type=ActionType.REACTION, range="5 Feet"), usage_tags=["control"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can sometimes cause another creature to suffer an attack meant for you. When you are targeted by an attack while a creature within 5 feet of you is granting you cover against that attack, you can use your reaction to have the attack target that creature instead of you."
        return description

    def target(self, character_stat_block: CharacterStatBlock) -> "FeatureTarget | None":
        return FeatureTarget.CREATURE


class SoulOfDeceit(Feature):
    def __init__(self):
        super().__init__(name="Soul of Deceit", origin="Mastermind Rogue Level 17", usage_tags=["utility"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your thoughts can't be read by telepathy or other means, unless you allow it. You can present false thoughts by making a Charisma (Deception) check contested by the mind reader's Wisdom (Insight) check.\n"
            "Additionally, no matter what you say, magic that would determine if you are telling the truth indicates you are being truthful if you so choose, and you can't be compelled to tell the truth by magic."
        )
        return description

    def target(self, character_stat_block: CharacterStatBlock) -> "FeatureTarget | None":
        return FeatureTarget.SELF
