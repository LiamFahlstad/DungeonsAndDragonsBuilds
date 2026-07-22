from Core.Definitions import WIZARD_HIT_DIE
from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class DivinationSavant(Feature):
    def __init__(self):
        super().__init__(name="Divination Savant", origin="Diviner Wizard Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Choose two Wizard spells from the Divination school, each of which must be no higher than level 2, and add them to your spellbook for free.\n"
            "In addition, whenever you gain access to a new level of spell slots in this class, you can add one Wizard spell from the Divination school to your spellbook for free. The chosen spell must be of a level for which you have spell slots."
        )
        return description


class Portent(Feature):
    def __init__(self):
        super().__init__(name="Portent", origin="Diviner Wizard Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Glimpses of the future begin to press on your awareness. Whenever you finish a Long Rest, roll two d20s and record the numbers rolled. You can replace any D20 Test made by you or a creature that you can see with one of these foretelling rolls. You must choose to do so before the roll, and you can replace a roll in this way only once per turn.\n"
            "Each foretelling roll can be used only once. When you finish a Long Rest, you lose any unused foretelling rolls."
        )
        return description


class ExpertDivination(Feature):
    def __init__(self):
        super().__init__(name="Expert Divination", origin="Diviner Wizard Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Casting Divination spells comes so easily to you that it expends only a fraction of your spellcasting efforts. When you cast a Divination spell using a level 2+ spell slot, you regain one expended spell slot. The slot you regain must be of a level lower than the slot you expended and can't be higher than level 5.\n"
        return description


class TheThirdEye(Feature):
    def __init__(self):
        super().__init__(name="The Third Eye", origin="Diviner Wizard Level 10")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can increase your powers of perception. As a Bonus Action, choose one of the following benefits, which lasts until you start a Short or Long Rest. You can't use this feature again until you finish a Short or Long Rest.\n"
            "    * Darkvision: You gain Darkvision with a range of 120 feet.\n"
            "    * Greater Comprehension: You can read any language.\n"
            "    * See Invisibility: You can cast See Invisibility without expending a spell slot."
        )
        return description


class GreaterPortent(Feature):
    def __init__(self):
        super().__init__(name="Greater Portent", origin="Diviner Wizard Level 14")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "The visions in your dreams intensify and paint a more accurate picture in your mind of what is to come. Roll three d20s for your Portent feature rather than two."
        return description
