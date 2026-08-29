from CharacterContent.Features.Core.BaseFeatures import Feature, FeatureUses, FeatureActivation, ActionType
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class DivinationSavant(Feature):
    def __init__(self):
        super().__init__(name="Divination Savant", origin="Divination Wizard Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "The gold and time you must spend to copy a Divination spell into your spellbook is halved."
        return description


class Portent(Feature):
    def __init__(self):
        super().__init__(name="Portent", origin="Divination Wizard Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Glimpses of the future begin to press in on your awareness. When you finish a long rest, roll two d20s and record the numbers rolled. You can replace any attack roll, saving throw, or ability check made by you or a creature that you can see with one of these foretelling rolls. You must choose to do so before the roll, and you can replace a roll in this way only once per turn.\n"
            "\n"
            "Each foretelling roll can be used only once. When you finish a long rest, you lose any unused foretelling rolls."
        )
        return description


class ExpertDivination(Feature):
    def __init__(self):
        super().__init__(name="Expert Divination", origin="Divination Wizard Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Casting divination spells comes so easily to you that it expends only a fraction of your spellcasting efforts. When you cast a divination spell of 2nd level or higher using a spell slot, you regain one expended spell slot. The slot you regain must be of a level lower than the spell you cast and can't be higher than 5th level."
        return description


class TheThirdEye(Feature):
    def __init__(self):
        super().__init__(
            name="The Third Eye",
            origin="Divination Wizard Level 10",
            activation=FeatureActivation(action_type=ActionType.ACTION, duration="Until Incapacitated Or Until Short Or Long Rest"),
            usage_tags=["utility"],
            uses=FeatureUses(max_uses=1, regain_all_on="short or long rest"),
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can use your action to increase your powers of perception. When you do so, choose one of the following benefits, which lasts until you are incapacitated or you take a short or long rest.\n"
            "\n"
            "    * Darkvision. You gain darkvision out to a range of 60 feet.\n"
            "    * Ethereal Sight. You can see into the Ethereal Plane within 60 feet of you.\n"
            "    * Greater Comprehension. You can read any language.\n"
            "    * See Invisibility. You can see invisible creatures and objects within 10 feet of you that are within line of sight."
        )
        return description


class GreaterPortent(Feature):
    def __init__(self):
        super().__init__(name="Greater Portent", origin="Divination Wizard Level 14")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "The visions in your dreams intensify and paint a more accurate picture in your mind of what is to come. You roll three d20s for your Portent feature, rather than two."
        return description
