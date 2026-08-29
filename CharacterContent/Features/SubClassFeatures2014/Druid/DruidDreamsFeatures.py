import Core.Definitions as Definitions
from CharacterContent.Features.Core.BaseFeatures import Feature, FeatureActivation, ActionType
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class BalmOfTheSummerCourt(Feature):
    def __init__(self):
        super().__init__(name="Balm of the Summer Court", origin="Circle of Dreams Druid Level 3", activation=FeatureActivation(action_type=ActionType.BONUS_ACTION, range="120 Feet"), usage_tags=["heal"], uses=FeatureUses(max_uses=20, regain_all_on="long rest", current_formula="Current amount: equal to your Druid level."))

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        druid_level = character_stat_block.get_class_level(Definitions.CharacterClass.DRUID)
        half_druid_level = max(1, druid_level // 2)
        description = (
            "At 2nd level, you become imbued with the blessings of the Summer Court. You are a font of energy that offers respite from injuries. You have a pool of fey energy represented by a number of d6s equal to your druid level.\n"
            "\n"
            "As a bonus action, you can choose an ally you can see within 120 feet of you and spend a number of those dice equal to half your druid level or less. Roll the spent dice and add them together. The target regains a number of hit points equal to the total. The target also gains 1 temporary hit point per die spent.\n"
            "\n"
            "You regain the expended dice when you finish a long rest."
        )
        return description