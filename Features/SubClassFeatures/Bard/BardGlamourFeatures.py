from Core.Definitions import BARD_HIT_DIE
from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class BeguilingMagic(Feature):
    def __init__(self):
        super().__init__(
            name="Beguiling Magic", origin="College of Glamour Bard Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You always have the Charm Person and Mirror Image spells prepared.\n"
            "In addition, immediately after you cast an Enchantment or Illusion spell using a spell slot, you can cause a creature you can see within 60 feet of yourself to make a Wisdom saving throw against your spell save DC. On a failed save, the target has the Charmed or Frightened condition (your choice) for 1 minute. The target repeats the save at the end of each of its turns, ending the effect on itself on a success.\n"
            "Once you use this benefit, you can't use it again until you finish a Long Rest. You can also restore your use of it by expending one use of your Bardic Inspiration (no action required)."
        )
        return description


class MantleOfInspiration(Feature):
    def __init__(self):
        super().__init__(
            name="Mantle of Inspiration", origin="College of Glamour Bard Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can weave fey magic into a song or dance to fill others with vigor. As a Bonus Action, you can expend a use of Bardic Inspiration, rolling a Bardic Inspiration die. When you do so, choose a number of other creatures within 60 feet of yourself, up to a number equal to your Charisma modifier (minimum of one creature). Each of those creatures gains a number of Temporary Hit Points equal to two times the number rolled on the Bardic Inspiration die, and then each can use its Reaction to move up to its Speed without provoking Opportunity Attacks."
        return description


class MantleOfMajesty(Feature):
    def __init__(self):
        super().__init__(
            name="Mantle of Majesty", origin="College of Glamour Bard Level 6"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You always have the Command spell prepared.\n"
            "As a Bonus Action, you cast Command without expending a spell slot, and you take on an unearthly appearance for 1 minute or until your Concentration ends. During this time, you can cast Command as a Bonus Action without expending a spell slot,\n"
            "Any creature Charmed by you automatically fails its saving throw against the Command you cast with this feature.\n"
            "Once you use this feature, you can't use it again until you finish a Long Rest. You can also restore your use of it by expending a level 3+ spell slot (no action required)."
        )
        return description


class UnbreakableMajesty(Feature):
    def __init__(self):
        super().__init__(
            name="Unbreakable Majesty", origin="College of Glamour Bard Level 14"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "As a Bonus Action, you can assume a magically majestic presence for 1 minute or until you have the Incapacitated condition. For the duration, whenever any creature hits you with an attack roll for the first time on a turn, the attacker must succeed on a Charisma saving throw against your spell save DC, or the attack misses instead, as the creature recoils from your majesty.\n"
            "Once you assume this majestic presence, you can't do so again until you finish a Short or Long Rest."
        )
        return description
