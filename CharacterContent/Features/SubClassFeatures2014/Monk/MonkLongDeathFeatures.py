from Core.Definitions import Ability
from CharacterContent.Features.Core.BaseFeatures import Feature, FeatureActivation, ActionType, FeatureTarget
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class TouchOfDeath(Feature):
    def __init__(self):
        super().__init__(name="Touch of Death", origin="Way of the Long Death Monk Level 3", activation=FeatureActivation(range="5 Feet"), usage_tags=["heal"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your study of death allows you to extract vitality from another creature as it nears its demise. When you reduce a creature within 5 feet of you to 0 hit points, you gain temporary hit points equal to your Wisdom modifier + your monk level (minimum of 1 temporary hit point)."
        )
        return description

    def target(self, character_stat_block: CharacterStatBlock) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class HourOfReaping(Feature):
    def __init__(self):
        super().__init__(name="Hour of Reaping", origin="Way of the Long Death Monk Level 6", activation=FeatureActivation(action_type=ActionType.ACTION, duration="Until End of Next Turn", range="30 Feet"), usage_tags=["control"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain the ability to unsettle or terrify those around you as an action, for your soul has been touched by the shadow of death. When you take this action, each creature within 30 feet of you that can see you must succeed on a Wisdom saving throw or be frightened of you until the end of your next turn."
        )
        return description

    def target(self, character_stat_block: CharacterStatBlock) -> "FeatureTarget | None":
        return FeatureTarget.AREA

    def get_table_description(self, character_stat_block: CharacterStatBlock) -> list[tuple[str, str]]:
        return [
            ("Action", "Action"),
            ("Range", "30 feet (creatures that can see you)"),
            ("Save", "Wisdom"),
            ("Effect", "Frightened until end of your next turn"),
        ]


class MasteryOfDeath(Feature):
    def __init__(self):
        super().__init__(name="Mastery of Death", origin="Way of the Long Death Monk Level 11", usage_tags=["heal"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You use your familiarity with death to escape its grasp. When you are reduced to 0 hit points, you can expend 1 ki point (no action required) to have 1 hit point instead."
        )
        return description

    def target(self, character_stat_block: CharacterStatBlock) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class TouchOfTheLongDeath(Feature):
    def __init__(self):
        super().__init__(name="Touch of the Long Death", origin="Way of the Long Death Monk Level 17", activation=FeatureActivation(action_type=ActionType.ACTION, range="Touch (5 Feet)"), usage_tags=["damage"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your touch can channel the energy of death into a creature. As an action, you touch one creature within 5 feet of you, and you expend 1 to 10 ki points. The target must make a Constitution saving throw, and it takes 2d10 necrotic damage per ki point spent on a failed save, or half as much damage on a successful one."
        )
        return description

    def target(self, character_stat_block: CharacterStatBlock) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY

    def get_table_description(self, character_stat_block: CharacterStatBlock) -> list[tuple[str, str]]:
        return [
            ("Action", "Action"),
            ("Range", "Touch (5 feet)"),
            ("Cost", "1-10 ki points"),
            ("Save", "Constitution"),
            ("Damage", "2d10 necrotic per ki point spent (failed save); half on success"),
        ]
