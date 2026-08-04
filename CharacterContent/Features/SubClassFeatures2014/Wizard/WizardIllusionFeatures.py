from Core.Definitions import WIZARD_HIT_DIE
from CharacterContent.Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class IllusionSavant(Feature):
    def __init__(self):
        super().__init__(name="Illusion Savant", origin="Illusion Wizard Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "The gold and time you must spend to copy an Illusion spell into your spellbook is halved."
        return description


class ImprovedMinorIllusion(Feature):
    def __init__(self):
        super().__init__(name="Improved Minor Illusion", origin="Illusion Wizard Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You learn the Minor Illusion cantrip. If you already know this cantrip, you learn a different wizard cantrip of your choice. The cantrip doesn't count against your number of cantrips known.\n"
            "When you cast Minor Illusion, you can create both a sound and an image with a single casting of the spell."
        )
        return description


class MalleableIllusions(Feature):
    def __init__(self):
        super().__init__(name="Malleable Illusions", origin="Illusion Wizard Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you cast an illusion spell that has a duration of 1 minute or longer, you can use your action to change the nature of that illusion (using the spell's normal parameters for the illusion), provided that you can see the illusion."
        return description


class IllusorySelf(Feature):
    def __init__(self):
        super().__init__(name="Illusory Self", origin="Illusion Wizard Level 10")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can create an illusory duplicate of yourself as an instant, almost instinctual reaction to danger. When a creature makes an attack roll against you, you can use your reaction to interpose the illusory duplicate between the attacker and yourself. The attack automatically misses you, then the illusion dissipates.\n"
            "Once you use this feature, you can't use it again until you finish a short or long rest."
        )
        return StringUtils.add_boxes(description, 1, regain_all_on="short or long rest")


class IllusoryReality(Feature):
    def __init__(self):
        super().__init__(name="Illusory Reality", origin="Illusion Wizard Level 14")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You have learned the secret of weaving shadow magic into your illusions to give them a semi-reality. When you cast an illusion spell of 1st level or higher, you can choose one inanimate, nonmagical object that is part of the illusion and make that object real. You can do this on your turn as a bonus action while the spell is ongoing. The object remains real for 1 minute. For example, you can create an illusion of a bridge over a chasm and then make it real long enough for your allies to cross.\n"
            "The object can't deal damage or otherwise directly harm anyone."
        )
        return description
