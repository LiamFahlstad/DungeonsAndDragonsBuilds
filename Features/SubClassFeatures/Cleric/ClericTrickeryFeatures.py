from Core.Definitions import CLERIC_HIT_DIE
from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class BlessingOfTheTrickster(Feature):
    def __init__(self):
        super().__init__(
            name="Blessing of the Trickster", origin="Trickery Domain Cleric Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "As a Magic action, you can choose yourself or a willing creature within 30 feet of yourself to have Advantage on Dexterity (Stealth) checks. This blessing lasts until you finish a Long Rest or you use this feature again."
        return description


class TrickeryDomainSpells(Feature):
    def __init__(self):
        super().__init__(
            name="Trickery Domain Spells", origin="Trickery Domain Cleric Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Your connection to this divine domain ensures you always have certain spells ready. When you reach a Cleric level specified in the Trickery Domain Spells table, you thereafter always have the listed spells prepared."
        return description


class InvokeDuplicity(Feature):
    def __init__(self):
        super().__init__(
            name="Invoke Duplicity", origin="Trickery Domain Cleric Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "As a Bonus Action, you can expend one use of your Channel Divinity to create a perfect visual illusion of yourself in an unoccupied space you can see within 30 feet of yourself. The illusion is intangible and doesn't occupy its space. It lasts for 1 minute, but it ends early if you dismiss it (no action required) or have the Incapacitated condition. The illusion is animated and mimics your expressions and gestures. While it persists, you gain the following benefits.\n"
            "Cast Spells. You can cast spells as though you were in the illusion's space, but you must use your own senses.\n"
            "Distract. When both you and your illusion are within 5 feet of a creature that can see the illusion, you have Advantage on attack rolls against that creature, given how distracting the illusion is to the target.\n"
            "Move. As a Bonus Action, you can move the illusion up to 30 feet to an unoccupied space you can see that is within 120 feet of yourself."
        )
        return description


class TrickstersTransposition(Feature):
    def __init__(self):
        super().__init__(
            name="Trickster's Transposition", origin="Trickery Domain Cleric Level 6"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Whenever you take the Bonus Action to create or move the illusion of your Invoke Duplicity, you can teleport, swapping places with the illusion."
        return description


class ImprovedDuplicity(Feature):
    def __init__(self):
        super().__init__(
            name="Improved Duplicity", origin="Trickery Domain Cleric Level 17"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "The illusion of your Invoke Duplicity has grown more powerful in the following ways.\n"
            "Shared Distraction. When you and your allies make attack rolls against a creature within 5 feet of the illusion, the attack rolls have Advantage.\n"
            "Healing Illusion. When the illusion ends, you or a creature of your choice within 5 feet of it regains a number of Hit Points equal to your Cleric level."
        )
        return description
