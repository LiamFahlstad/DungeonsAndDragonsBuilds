from Core.Definitions import BARD_HIT_DIE
from CharacterContent.Features.Core.BaseFeatures import Feature, FeatureActivation
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class BeguilingMagic(Feature):
    def __init__(self):
        super().__init__(
            name="Beguiling Magic", origin="College of Glamour Bard Level 3", activation=FeatureActivation(duration="1 Minute", range="60 Feet"), usage_tags=["control"]
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You always have the Charm Person and Mirror Image spells prepared.\n"
            "In addition, immediately after you cast an Enchantment or Illusion spell using a spell slot, you can cause a creature you can see within 60 feet of yourself to make a Wisdom saving throw against your spell save DC. On a failed save, the target has the Charmed or Frightened condition (your choice) for 1 minute. The target repeats the save at the end of each of its turns, ending the effect on itself on a success.\n"
            "Once you use this benefit, you can't use it again until you finish a Long Rest. You can also restore your use of it by expending one use of your Bardic Inspiration (no action required)."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Always Prepared", "Charm Person, Mirror Image"),
            ("Trigger", "After casting Enchantment or Illusion spell with spell slot"),
            ("Target", "Creature you can see within 60 feet"),
            ("Save", "Wisdom save vs. your spell save DC"),
            ("Effect", "Failed save: Charmed or Frightened condition (your choice) for 1 minute; repeats save at end of each turn"),
            ("Recharge", "Long Rest (restore early by expending 1 Bardic Inspiration)"),
        ]


class MantleOfInspiration(Feature):
    def __init__(self):
        super().__init__(
            name="Mantle of Inspiration", origin="College of Glamour Bard Level 3", activation=FeatureActivation(action_type="bonus_action", range="60 Feet"), usage_tags=["heal", "buff"]
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can weave fey magic into a song or dance to fill others with vigor. As a Bonus Action, you can expend a use of Bardic Inspiration, rolling a Bardic Inspiration die. When you do so, choose a number of other creatures within 60 feet of yourself, up to a number equal to your Charisma modifier (minimum of one creature). Each of those creatures gains a number of Temporary Hit Points equal to two times the number rolled on the Bardic Inspiration die, and then each can use its Reaction to move up to its Speed without provoking Opportunity Attacks."
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Action", "Bonus Action"),
            ("Cost", "1 use of Bardic Inspiration"),
            ("Targets", "Up to Charisma modifier creatures (minimum 1) within 60 feet"),
            ("Temporary HP", "2 × the number rolled on Bardic Inspiration die"),
            ("Movement", "Each target can use Reaction to move up to its Speed without provoking Opportunity Attacks"),
        ]


class MantleOfMajesty(Feature):
    def __init__(self):
        super().__init__(
            name="Mantle of Majesty", origin="College of Glamour Bard Level 6", activation=FeatureActivation(action_type="bonus_action", duration="1 Minute or Until Concentration Ends"), usage_tags=["control"]
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You always have the Command spell prepared.\n"
            "As a Bonus Action, you cast Command without expending a spell slot, and you take on an unearthly appearance for 1 minute or until your Concentration ends. During this time, you can cast Command as a Bonus Action without expending a spell slot,\n"
            "Any creature Charmed by you automatically fails its saving throw against the Command you cast with this feature.\n"
            "Once you use this feature, you can't use it again until you finish a Long Rest. You can also restore your use of it by expending a level 3+ spell slot (no action required)."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Always Prepared", "Command"),
            ("Action", "Bonus Action (first cast); Bonus Action (subsequent casts during effect)"),
            ("Duration", "1 minute or until Concentration ends"),
            ("Effect", "Cast Command without spell slot; creatures Charmed by you auto-fail its save"),
            ("Recharge", "Long Rest (restore early with level 3+ spell slot)"),
        ]


class UnbreakableMajesty(Feature):
    def __init__(self):
        super().__init__(
            name="Unbreakable Majesty", origin="College of Glamour Bard Level 14", activation=FeatureActivation(action_type="bonus_action", duration="1 Minute or Until Incapacitated"), usage_tags=["buff"]
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "As a Bonus Action, you can assume a magically majestic presence for 1 minute or until you have the Incapacitated condition. For the duration, whenever any creature hits you with an attack roll for the first time on a turn, the attacker must succeed on a Charisma saving throw against your spell save DC, or the attack misses instead, as the creature recoils from your majesty.\n"
            "Once you assume this majestic presence, you can't do so again until you finish a Short or Long Rest."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Action", "Bonus Action"),
            ("Duration", "1 minute or until you have Incapacitated condition"),
            ("Trigger", "Creature hits you with attack roll for first time on a turn"),
            ("Save", "Charisma save vs. your spell save DC"),
            ("Effect", "Failed save: attack misses; creature recoils"),
            ("Recharge", "Short or Long Rest"),
        ]
