from Core.Definitions import Ability, Condition, WARLOCK_HIT_DIE
from CharacterContent.Features.Core.BaseFeatures import Feature
from CharacterContent.Features.Core.Improvements import ConditionImmunity
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class ArchfeyExpandedSpells(Feature):
    def __init__(self):
        super().__init__(
            name="Expanded Spell List", origin="The Archfey Patron Warlock Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "The Archfey lets you choose from an expanded list of spells when you learn a Warlock spell. The following spells are added to the Warlock spell list for you.\n"
            "Archfey Expanded Spells\n"
            "Spell Level\tSpells\n"
            "1st\tFaerie Fire, Sleep\n"
            "2nd\tCalm Emotions, Phantasmal Force\n"
            "3rd\tBlink, Plant Growth\n"
            "4th\tDominate Beast, Greater Invisibility\n"
            "5th\tDominate Person, Seeming"
        )
        return description


class FeyPresence(Feature):
    def __init__(self):
        super().__init__(
            name="Fey Presence", origin="The Archfey Patron Warlock Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your patron bestows upon you the ability to project the beguiling and fearsome presence of the fey. As an action, you can cause each creature in a 10-foot cube originating from you to make a Wisdom saving throw against your Warlock spell save DC. The creatures that fail their saving throws are all charmed or frightened by you (your choice) until the end of your next turn.\n"
            "Once you use this feature, you can't use it again until you finish a Short or Long Rest."
        )
        return StringUtils.add_boxes(description, 1, regain_all_on="short or long rest")

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Action", "Action"),
            ("Range", "10-foot cube from you"),
            ("Save", "Wisdom against Warlock spell save DC"),
            ("Effect", "Charmed or frightened (your choice) until end of next turn"),
            ("Recharge", "Short or long rest"),
        ]


class MistyEscape(Feature):
    def __init__(self):
        super().__init__(
            name="Misty Escape", origin="The Archfey Patron Warlock Level 6"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can vanish in a puff of mist in response to harm. When you take damage, you can use your Reaction to turn Invisible and teleport up to 60 feet to an unoccupied space you can see. You remain Invisible until the start of your next turn or until you attack or cast a spell.\n"
            "Once you use this feature, you can't use it again until you finish a Short or Long Rest."
        )
        return StringUtils.add_boxes(description, 1, regain_all_on="short or long rest")

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Trigger", "When you take damage"),
            ("Type", "Reaction"),
            ("Effect", "Turn Invisible and teleport up to 60 feet"),
            ("Duration", "Invisible until start of next turn or until you attack or cast a spell"),
            ("Recharge", "Short or long rest"),
        ]


class BeguilingDefenses(Feature):
    def __init__(self):
        super().__init__(
            name="Beguiling Defenses", origin="The Archfey Patron Warlock Level 10"
        )
        self._immunity = ConditionImmunity(Condition.CHARMED, self.name)

    def apply(self, character_stat_block: CharacterStatBlock):
        self._immunity.apply(character_stat_block)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Your patron teaches you how to turn the mind-affecting magic of your enemies against them. You are immune to being charmed, and when another creature attempts to charm you, you can use your Reaction to attempt to turn the charm back on that creature. The creature must succeed on a Wisdom saving throw against your Warlock spell save DC or be charmed by you for 1 minute or until the creature takes any damage."
        return description


class DarkDelirium(Feature):
    def __init__(self):
        super().__init__(
            name="Dark Delirium", origin="The Archfey Patron Warlock Level 14"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can plunge a creature into an illusory realm. As an action, choose a creature that you can see within 60 feet of yourself. It must make a Wisdom saving throw against your Warlock spell save DC. On a failed save, it is charmed or frightened by you (your choice) for 1 minute or until your concentration is broken (as if you are concentrating on a spell). This effect ends early if the creature takes any damage.\n"
            "Until this illusion ends, the creature thinks it is lost in a misty realm, the appearance of which you choose. The creature can see and hear only itself, you, and the illusion.\n"
            "You must finish a Short or Long Rest before you can use this feature again."
        )
        return StringUtils.add_boxes(description, 1, regain_all_on="short or long rest")

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Action", "Action"),
            ("Range", "60 feet"),
            ("Save", "Wisdom against Warlock spell save DC"),
            ("Effect", "Charmed or frightened (your choice) for 1 minute"),
            ("Concentration", "Yes; breaks on creature damage"),
            ("Recharge", "Short or long rest"),
        ]
