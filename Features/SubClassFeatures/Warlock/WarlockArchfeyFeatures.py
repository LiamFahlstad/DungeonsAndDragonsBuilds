from Core.Definitions import Ability, WARLOCK_HIT_DIE
from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class ArchfeySpells(Feature):
    def __init__(self):
        super().__init__(name="Archfey Spells", origin="Archfey Patron Warlock Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "The magic of your patron ensures you always have certain spells ready; when you reach a Warlock level specified in the Archfey Spells table, you thereafter always have the listed spells prepared."
        return description


class StepsOfTheFey(Feature):
    def __init__(self):
        super().__init__(
            name="Steps of the Fey", origin="Archfey Patron Warlock Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        charisma_modifier = character_stat_block.get_ability_modifier(Ability.CHARISMA)
        uses = max(1, charisma_modifier)
        description = (
            "Your patron grants you the ability to move between the boundaries of the planes. You can cast Misty Step without expending a spell slot a number of times equal to your Charisma modifier (minimum of once), and you regain all expended uses when you finish a Long Rest.\n"
            "In addition, whenever you cast that spell, you can choose one of the following additional effects.\n"
            "    * Refreshing Step: Immediately after you teleport, you or one creature you can see within 10 feet of yourself gains 1d10 Temporary Hit Points.\n"
            "    * Taunting Step: Creatures within 5 feet of the space you left must succeed on a Wisdom saving throw against your spell save DC or have Disadvantage on attack rolls against creatures other than you until the start of your next turn."
        )
        return StringUtils.add_boxes(description, uses, regain_all_on="long rest")


class MistyEscape(Feature):
    def __init__(self):
        super().__init__(name="Misty Escape", origin="Archfey Patron Warlock Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can cast Misty Step as a Reaction in response to taking damage.\n"
            "In addition, the following effects are now among your Steps of the Fey options.\n"
            "Disappearing Step. You have the Invisible condition until the start of your next turn or until immediately after you make an attack roll, deal damage, or cast a spell.\n"
            "Dreadful Step. Creatures within 5 feet of the space you left or the space you appear in (your choice) must succeed on a Wisdom saving throw against your spell save DC or take 2d10 Psychic damage."
        )
        return description


class BeguilingDefenses(Feature):
    def __init__(self):
        super().__init__(
            name="Beguiling Defenses", origin="Archfey Patron Warlock Level 10"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your patron teaches you how to guard your mind and body. You are immune to the Charmed condition.\n"
            "In addition, immediately after a creature you can see hits you with an attack roll, you can take a Reaction to reduce the damage you take by half (round down), and you can force the attacker to make a Wisdom saving throw against your spell save DC. On a failed save, the attacker takes Psychic damage equal to the damage you take. Once you use this Reaction, you can't use it again until you finish a Long Rest unless you expend a Pact Magic spell slot (no action required) to restore your use of it."
        )
        return description


class BewitchingMagic(Feature):
    def __init__(self):
        super().__init__(
            name="Bewitching Magic", origin="Archfey Patron Warlock Level 14"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Your patron grants you the ability to weave your magic with teleportation. Immediately after you cast an Enchantment or Illusion spell using an action and a spell slot, you can cast Misty Step as part of the same action and without expending a spell slot."
        return description
