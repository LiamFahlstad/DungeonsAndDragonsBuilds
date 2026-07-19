from Definitions import Ability, CLERIC_HIT_DIE
from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class GuidedStrike(Feature):
    def __init__(self):
        super().__init__(name="Guided Strike", origin="War Domain Cleric Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you or a creature within 30 feet of you misses with an attack roll, you can expend one use of your Channel Divinity and give that roll a +10 bonus, potentially causing it to hit. When you use this feature to benefit another creature's attack roll, you must take a Reaction to do so."
        return description


class WarDomainSpells(Feature):
    def __init__(self):
        super().__init__(name="War Domain Spells", origin="War Domain Cleric Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Your connection to this divine domain ensures you always have certain spells ready. When you reach a Cleric level specified in the War Domain Spells table, you thereafter always have the listed spells prepared."
        return description


class WarPriest(Feature):
    def __init__(self):
        super().__init__(name="War Priest", origin="War Domain Cleric Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        wisdom_modifier = character_stat_block.get_ability_modifier(Ability.WISDOM)
        uses = max(1, wisdom_modifier)
        description = "As a Bonus Action, you can make one attack with a weapon or an Unarmed Strike. You can use this Bonus Action a number of times equal to your Wisdom modifier (minimum of once). You regain all expended uses when you finish a Short or Long Rest."
        return StringUtils.add_boxes(
            description, uses, regain_all_on="short or long rest"
        )


class WarGodsBlessing(Feature):
    def __init__(self):
        super().__init__(name="War God's Blessing", origin="War Domain Cleric Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can expend a use of your Channel Divinity to cast Shield of Faith or Spiritual Weapon rather than expending a spell slot. When you cast either spell in this way, the spell doesn't require Concentration. Instead the spell lasts for 1 minute, but it ends early if you cast that spell again, have the Incapacitated condition, or die."
        return description


class AvatarOfBattle(Feature):
    def __init__(self):
        super().__init__(name="Avatar of Battle", origin="War Domain Cleric Level 17")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain Resistance to Bludgeoning, Piercing, and Slashing damage."
        )
        return description
