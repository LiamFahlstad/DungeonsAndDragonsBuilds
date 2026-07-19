from Definitions import CLERIC_HIT_DIE
from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class DiscipleofLife(Feature):
    def __init__(self):
        super().__init__(name="Disciple of Life", origin="Life Domain Cleric Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When a spell you cast with a spell slot restores Hit Points to a creature, that creature regains additional Hit Points on the turn you cast the spell. The additional Hit Points equal 2 plus the spell slot's level."
        return description


class LifeDomainSpells(Feature):
    def __init__(self):
        super().__init__(name="Life Domain Spells", origin="Life Domain Cleric Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Your connection to this divine domain ensures you always have certain spells ready. When you reach a Cleric level specified in the Life Domain Spells table, you thereafter always have the listed spells prepared."
        return description


class PreserveLife(Feature):
    def __init__(self):
        super().__init__(name="Preserve Life", origin="Life Domain Cleric Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "As a Magic action, you present your Holy Symbol and expend a use of your Channel Divinity to evoke healing energy that can restore a number of Hit Points equal to five times your Cleric level. Choose Bloodied creatures within 30 feet of yourself (which can include you), and divide those Hit Points among them. This feature can restore a creature to no more than half its Hit Point maximum."
        return description


class BlessedHealer(Feature):
    def __init__(self):
        super().__init__(name="Blessed Healer", origin="Life Domain Cleric Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "The healing spells you cast on others heal you as well. Immediately after you cast a spell with a spell slot that restores Hit Points to one or more creatures other than yourself, you regain Hit Points equal to 2 plus the spell slot's level."
        return description


class SupremeHealing(Feature):
    def __init__(self):
        super().__init__(name="Supreme Healing", origin="Life Domain Cleric Level 17")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you would normally roll one or more dice to restore Hit Points to a creature with a spell or Channel Divinity, don't roll those dice for the healing; instead use the highest number possible for each die. For example, instead of restoring 2d6 Hit Points to a creature with a spell, you restore 12."
        return description
