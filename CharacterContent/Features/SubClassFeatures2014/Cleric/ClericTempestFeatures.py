import Core.Definitions as Definitions
from Core.Definitions import Ability
from CharacterContent.Features.Core.BaseFeatures import Feature, FeatureUses, FeatureActivation, ActionType, RegainedOn, FeatureTarget
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class BonusProficiencies(Feature):
    def __init__(self):
        super().__init__(name="Bonus Proficiencies", origin="Tempest Domain Cleric Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You gain proficiency with martial weapons and heavy armor."
        return description


class WrathOfTheStorm(Feature):
    def __init__(self):
        super().__init__(
            name="Wrath of the Storm",
            origin="Tempest Domain Cleric Level 3",
            activation=FeatureActivation(action_type=ActionType.REACTION, range="5 Feet"),
            usage_tags=["damage"],
            uses=FeatureUses(max_uses=Definitions.MAX_ABILITY_MODIFIER, regain_all_on="long rest", current_formula="Current amount: equal to your Wisdom modifier."),
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can thunderously rebuke attackers. When a creature within 5 feet of you that you can see hits you with an attack, you can use your reaction to cause the creature to make a Dexterity saving throw. The creature takes 2d8 lightning or thunder damage (your choice) on a failed saving throw, and half as much damage on a successful one.\n"
            "You can use this feature a number of times equal to your Wisdom modifier (a minimum of once). You regain all expended uses when you finish a long rest."
        )
        return description

    def regained_on(self, character_stat_block: CharacterStatBlock) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def target(
        self, character_stat_block: CharacterStatBlock
    ) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY

    def number_of_uses(self, character_stat_block: CharacterStatBlock) -> int:
        return character_stat_block.get_wisdom_modifier()