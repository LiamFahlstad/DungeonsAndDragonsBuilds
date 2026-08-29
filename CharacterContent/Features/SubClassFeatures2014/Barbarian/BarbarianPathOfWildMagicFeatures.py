import Core.Definitions as Definitions
from CharacterContent.Features.Core.BaseFeatures import Feature, FeatureActivation, ActionType
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class MagicAwareness(Feature):
    def __init__(self):
        super().__init__(name="Magic Awareness", origin="Path Of Wild Magic Barbarian Level 3", activation=FeatureActivation(action_type=ActionType.ACTION, duration="Until the End of Your Next Turn", range="60 Feet"), usage_tags=["utility"], uses=FeatureUses(max_uses=Definitions.MAX_PROFICIENCY_BONUS, regain_all_on="long rest", current_formula="Current amount: equal to your proficiency bonus."))

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        proficiency_bonus = character_stat_block.get_proficiency_bonus()
        description = (
            "When you choose this path at 3rd level, as an action, you can open your awareness to the presence of concentrated magic. Until the end of your next turn, you know the location of any spell or magic item within 60 feet of you that isn't behind total cover. When you sense a spell, you learn which school of magic it belongs to.\n"
            "\n"
            "You can use this feature a number of times equal to your proficiency bonus, and you regain all expended uses when you finish a long rest."
        )
        return description