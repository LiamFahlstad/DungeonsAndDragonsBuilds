from Core.Definitions import Ability, Condition, WARLOCK_HIT_DIE
import Core.Definitions as Definitions
from CharacterContent.Features.Core.BaseFeatures import Feature, FeatureUses, FeatureActivation, ActionType, RegainedOn
from CharacterContent.Features.Core.Improvements import ConditionImmunity
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
            name="Steps of the Fey", origin="Archfey Patron Warlock Level 3", usage_tags=["heal", "control"]
        , uses=FeatureUses(max_uses=Definitions.MAX_ABILITY_MODIFIER, regain_all_on="long rest", current_formula="Current amount: equal to your Charisma modifier."))

    def calculate_dc(self, character_stat_block: CharacterStatBlock) -> int:
        return character_stat_block.calculate_difficulty_class()


    def regained_on(self, character_stat_block: CharacterStatBlock) -> "RegainedOn | None":
        return RegainedOn.LONG_REST
    def number_of_uses(self, character_stat_block: CharacterStatBlock) -> int:
        return max(1, character_stat_block.get_charisma_modifier())
    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your patron grants you the ability to move between the boundaries of the planes. You can cast Misty Step without expending a spell slot a number of times equal to your Charisma modifier (minimum of once), and you regain all expended uses when you finish a Long Rest.\n"
            "In addition, whenever you cast that spell, you can choose one of the following additional effects.\n"
            "    * Refreshing Step: Immediately after you teleport, you or one creature you can see within 10 feet of yourself gains 1d10 Temporary Hit Points.\n"
            "    * Taunting Step: Creatures within 5 feet of the space you left must succeed on a Wisdom saving throw against your spell save DC or have Disadvantage on attack rolls against creatures other than you until the start of your next turn."
        )
        return description

class MistyEscape(Feature):
    def __init__(self):
        super().__init__(name="Misty Escape", origin="Archfey Patron Warlock Level 6", activation=FeatureActivation(action_type=ActionType.REACTION), usage_tags=["buff", "damage"])

    def calculate_dc(self, character_stat_block: CharacterStatBlock) -> int:
        return character_stat_block.calculate_difficulty_class()

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
            name="Beguiling Defenses", origin="Archfey Patron Warlock Level 10", activation=FeatureActivation(action_type=ActionType.REACTION), usage_tags=["buff", "damage"]
        )
        self._immunity = ConditionImmunity(Condition.CHARMED, self.name)

    def apply(self, character_stat_block: CharacterStatBlock):
        self._immunity.apply(character_stat_block)

    def calculate_dc(self, character_stat_block: CharacterStatBlock) -> int:
        return character_stat_block.calculate_difficulty_class()

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your patron teaches you how to guard your mind and body. You are immune to the Charmed condition.\n"
            "In addition, immediately after a creature you can see hits you with an attack roll, you can take a Reaction to reduce the damage you take by half (round down), and you can force the attacker to make a Wisdom saving throw against your spell save DC. On a failed save, the attacker takes Psychic damage equal to the damage you take. Once you use this Reaction, you can't use it again until you finish a Long Rest unless you expend a Pact Magic spell slot (no action required) to restore your use of it."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Passive", "Immunity to Charmed condition"),
            ("Trigger", "Creature hits you with attack roll"),
            ("Reaction Effect", "Reduce damage by half (round down); force Wisdom save DC"),
            ("Save Effect", "On fail: attacker takes Psychic damage = damage you took"),
            ("Recharge", "Long Rest or expend Pact Magic spell slot"),
        ]


class BewitchingMagic(Feature):
    def __init__(self):
        super().__init__(
            name="Bewitching Magic", origin="Archfey Patron Warlock Level 14"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Your patron grants you the ability to weave your magic with teleportation. Immediately after you cast an Enchantment or Illusion spell using an action and a spell slot, you can cast Misty Step as part of the same action and without expending a spell slot."
        return description
