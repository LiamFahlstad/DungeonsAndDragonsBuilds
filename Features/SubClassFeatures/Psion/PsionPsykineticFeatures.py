from Core.Definitions import PSION_HIT_DIE
from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class StrongerTelekinesis(Feature):
    def __init__(self):
        super().__init__(name="Stronger Telekinesis", origin="Psykinetic Psion Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you cast Mage Hand, its range increases by 30\n"
            "feet when you cast it, and the hand can carry up to\n"
            "20 pounds."
        )
        return description


class TelekineticTechniques(Feature):
    def __init__(self):
        super().__init__(
            name="Telekinetic Techniques", origin="Psykinetic Psion Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you use Telekinetic Propel, you can roll 1d4\n"
            "and use the number rolled instead of expending a\n"
            "Psionic Energy Die.\n"
            "In addition, when a target fails the saving throw\n"
            "against your Telekinetic Propel, you can impose one\n"
            "of the following effects on that target\n"
            "Boost. The target's Speed increases by 10 feet\n"
            "until the start of your next turn.\n"
            "Disorient. The target can't make Opportunity\n"
            "Attacks until the start of its next turn.\n"
            "Telekinetic Bolt. The target takes Force damage\n"
            "equal to the number rolled on the Psionic Energy\n"
            "Die."
        )
        return description


class DestructiveTrance(Feature):
    def __init__(self):
        super().__init__(name="Destructive Trance", origin="Psykinetic Psion Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "At the start of your turn, you can expend one Psionic\n"
            "Energy Die to enter a destructive state. For the next\n"
            "10 minutes, you gain a Fly Speed of 20 feet and can\n"
            "hover, and when you cast a Psion spell that expends\n"
            "a spell slot, you can roll your Psionic Energy Die and\n"
            "add the number rolled to one damage roll of that\n"
            "spell. This roll doesn't expend the Psionic Energy\n"
            "Die."
        )
        return description


class ReboundingField(Feature):
    def __init__(self):
        super().__init__(name="Rebounding Field", origin="Psykinetic Psion Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you cast Shield in response to being hit by an\n"
            "attack roll and cause the triggering attack to miss,\n"
            "you can expend one Psionic Energy Die to launch the\n"
            "force back at the attacker. The attacker makes a\n"
            "Dexterity saving throw. Roll one Psionic Energy Die.\n"
            "On a failed save, the attacker takes Force damage\n"
            "equal to the amount rolled plus your Intelligence\n"
            "modifier. On a successful save, the attacker takes\n"
            "half as much damage only. Whether the target fails\n"
            "or succeeds on the saving throw, you gain\n"
            "Temporary Hit Points equal to the amount of\n"
            "damage dealt."
        )
        return description


class EnhancedTelekineticCrush(Feature):
    def __init__(self):
        super().__init__(
            name="Enhanced Telekinetic Crush", origin="Psykinetic Psion Level 10"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you cast Telekinetic Crush, you can expend one\n"
            "Psionic Energy Die to modify the spell so that\n"
            "whether a creature fails or succeeds on the saving\n"
            "throw against the spell, its Speed is halved until the\n"
            "start of your next turn. In addition, you can roll the\n"
            "expended Psionic Energy Die and add the number\n"
            "rolled to one damage roll of the spell."
        )
        return description


class HeightenedTelekinesis(Feature):
    def __init__(self):
        super().__init__(
            name="Heightened Telekinesis", origin="Psykinetic Psion Level 14"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can cast Telekinesis without expending a spell\n"
            "slot by instead expending four Psionic Energy Dice.\n"
            "When you cast Telekinesis without expending a spell\n"
            "slot using this feature, you can modify the spell so\n"
            "that it doesn't require Concentration. If you do so,\n"
            "the spell's duration becomes 1 minute for that\n"
            "casting, and you can concentrate on another spell as normal."
        )
        return description
