from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils

ROGUE_HIT_DIE = 8


class FancyFootwork(Feature):
    def __init__(self):
        super().__init__(name="Fancy Footwork", origin="Swashbuckler Rogue Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You learn how to land a strike and then slip away without reprisal. During your turn, "
            "if you make a melee attack against a creature, that creature can't make opportunity attacks "
            "against you for the rest of your turn."
        )
        return description


class RakishAudacity(Feature):
    def __init__(self):
        super().__init__(name="Rakish Audacity", origin="Swashbuckler Rogue Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your confidence propels you into battle. You gain a bonus to your initiative rolls equal to "
            "your Charisma modifier.\n"
            "You also gain an additional way to use your Sneak Attack; you don't need advantage on the "
            "attack roll to use your Sneak Attack against a creature if you are within 5 feet of it, no "
            "other creatures are within 5 feet of you, and you don't have disadvantage on the attack roll. "
            "All the other rules for Sneak Attack still apply to you."
        )
        return description


class Panache(Feature):
    def __init__(self):
        super().__init__(name="Panache", origin="Swashbuckler Rogue Level 9")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your charm becomes extraordinarily beguiling. As an action, you can make a Charisma "
            "(Persuasion) check contested by a creature's Wisdom (Insight) check. The creature must be "
            "able to hear you, and the two of you must share a language.\n"
            "If you succeed on the check and the creature is hostile to you, it has disadvantage on "
            "attack rolls against targets other than you and can't make opportunity attacks against "
            "targets other than you. This effect lasts for 1 minute, until one of your companions attacks "
            "the target or affects it with a spell, or until you and the target are more than 60 feet "
            "apart.\n"
            "If you succeed on the check and the creature isn't hostile to you, it is charmed by you for "
            "1 minute. While charmed, it regards you as a friendly acquaintance. This effect ends "
            "immediately if you or your companions do anything harmful to it."
        )
        return description


class ElegantManeuver(Feature):
    def __init__(self):
        super().__init__(name="Elegant Maneuver", origin="Swashbuckler Rogue Level 13")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can use a bonus action on your turn to gain advantage on the next Dexterity (Acrobatics) "
            "or Strength (Athletics) check you make during the same turn."
        )
        return description


class MasterDuelist(Feature):
    def __init__(self):
        super().__init__(name="Master Duelist", origin="Swashbuckler Rogue Level 17")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your mastery of the blade lets you turn failure into success in combat. If you miss with an "
            "attack roll, you can roll it again with advantage. Once you do so, you can't use this feature "
            "again until you finish a short or long rest."
        )
        return StringUtils.add_boxes(description, 1, regain_all_on="short or long rest")
