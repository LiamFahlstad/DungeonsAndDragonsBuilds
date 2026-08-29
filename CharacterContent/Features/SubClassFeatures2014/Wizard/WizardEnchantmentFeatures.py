from Core import Definitions
from Core.Definitions import Ability, WIZARD_HIT_DIE
from CharacterContent.Features.Core.BaseFeatures import Feature, FeatureActivation
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class EnchantmentSavant(Feature):
    def __init__(self):
        super().__init__(name="Enchantment Savant", origin="Enchantment Wizard Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "The gold and time you must spend to copy an Enchantment spell into your spellbook is halved."
        return description


class HypnoticGaze(Feature):
    def __init__(self):
        super().__init__(name="Hypnotic Gaze", origin="Enchantment Wizard Level 3", activation=FeatureActivation(action_type="action", duration="Until End Of Your Next Turn", range="5 Feet"), usage_tags=["control"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your soft words and enchanting gaze can magically enthrall another creature. As an action, choose one creature that you can see within 5 feet of you. If the target can see or hear you, it must succeed on a Wisdom saving throw against your wizard spell save DC or be charmed by you until the end of your next turn. The charmed creature's speed drops to 0, and the creature is incapacitated and visibly dazed.\n"
            "On subsequent turns, you can use your action to maintain this effect, extending its duration until the end of your next turn. However, the effect ends if you move more than 5 feet away from the creature, if the creature can neither see nor hear you, or if the creature takes damage.\n"
            "Once the effect ends, or if the creature succeeds on its initial saving throw against this effect, you can't use this feature on that creature again until you finish a long rest."
        )
        return description

    def get_table_description(self, character_stat_block: CharacterStatBlock) -> list[tuple[str, str]]:
        return [
            ("Action", "Action"),
            ("Target", "One creature within 5 feet that can see or hear you"),
            ("Save", "Wisdom saving throw vs spell save DC"),
            ("Effect", "Charmed, speed 0, incapacitated and dazed"),
            ("Duration", "Until end of your next turn"),
            ("Maintain", "Use action on subsequent turns to extend"),
            ("Ends if", "You move >5 feet away, creature can't see/hear you, or takes damage"),
            ("Recharge", "Long rest (per target)"),
        ]


class InstinctiveCharm(Feature):
    def __init__(self):
        super().__init__(name="Instinctive Charm", origin="Enchantment Wizard Level 6", activation=FeatureActivation(action_type="reaction", range="30 Feet"), usage_tags=["control"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When a creature you can see within 30 feet of you makes an attack roll against you, you can use your reaction to divert the attack, provided that another creature is within the attack's range. The attacker must make a Wisdom saving throw against your wizard spell save DC. On a failed save, the attacker must target the creature that is closest to it, not including you or itself. If multiple creatures are closest, the attacker chooses which one to target.\n"
            "On a successful save, you can't use this feature on the attacker again until you finish a long rest.\n"
            "You must choose to use this feature before knowing whether the attack hits or misses. Creatures that can't be charmed are immune to this effect."
        )
        return description

    def get_table_description(self, character_stat_block: CharacterStatBlock) -> list[tuple[str, str]]:
        return [
            ("Trigger", "Creature within 30 feet makes attack roll against you"),
            ("Action", "Reaction"),
            ("Requirement", "Another creature must be within attack's range"),
            ("Save", "Wisdom saving throw vs spell save DC"),
            ("On Fail", "Attacker must target nearest creature (not you, not self)"),
            ("On Success", "Can't use on this attacker until long rest"),
            ("Timing", "Declare before knowing if attack hits"),
            ("Immunity", "Creatures that can't be charmed are immune"),
        ]


class SplitEnchantment(Feature):
    def __init__(self):
        super().__init__(name="Split Enchantment", origin="Enchantment Wizard Level 10")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you cast an enchantment spell of 1st level or higher that targets only one creature, you can have it target a second creature."
        return description


class AlterMemories(Feature):
    def __init__(self):
        super().__init__(name="Alter Memories", origin="Enchantment Wizard Level 14", activation=FeatureActivation(action_type="action"), usage_tags=["control"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        cha_mod = character_stat_block.get_ability_modifier(Ability.CHARISMA)
        memory_loss = max(1, 1 + cha_mod)
        description = (
            "You gain the ability to make a creature unaware of your magical influence on it. When you cast an enchantment spell to charm one or more creatures, you can alter one creature's understanding so that it remains unaware of being charmed.\n"
            f"Additionally, once before the spell expires, you can use your action to try to make the chosen creature forget some of the time it spent charmed. The creature must succeed on an Intelligence saving throw against your wizard spell save DC or lose a number of hours of its memories equal to 1 + your Charisma modifier ({memory_loss}). You can make the creature forget less time, and the amount of time can't exceed the duration of your enchantment spell."
        )
        return description
