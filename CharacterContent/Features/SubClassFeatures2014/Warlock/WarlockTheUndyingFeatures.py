import Core.Definitions as Definitions
from Core.Definitions import Ability, WARLOCK_HIT_DIE
from CharacterContent.Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class UndyingExpandedSpells(Feature):
    def __init__(self):
        super().__init__(
            name="Expanded Spell List", origin="The Undying Patron Warlock Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "The Undying lets you choose from an expanded list of spells when you learn a warlock spell. The following spells are added to the warlock spell list for you.\n"
            "Undying Expanded Spells\n"
            "Spell Level\tSpells\n"
            "1st\tFalse Life, Ray of Sickness\n"
            "2nd\tBlindness/Deafness, Silence\n"
            "3rd\tFeign Death, Speak with Dead\n"
            "4th\tAura of Life, Death Ward\n"
            "5th\tContagion, Legend Lore"
        )
        return description


class AmongTheDead(Feature):
    def __init__(self):
        super().__init__(
            name="Among the Dead", origin="The Undying Patron Warlock Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Starting at 1st level, you learn the Spare the Dying cantrip, which counts as a warlock cantrip for you. You also have advantage on saving throws against any disease.\n"
            "\n"
            "Additionally, undead have difficulty harming you. If an undead targets you directly with an attack or a harmful spell, that creature must make a Wisdom saving throw against your spell save DC (an undead needn't make the save when it includes you in an area effect, such as the explosion of Fireball). On a failed save, the creature must choose a new target or forfeit targeting someone instead of you, potentially wasting the attack or spell. On a successful save, the creature is immune to this effect for 24 hours. An undead is also immune to this effect for 24 hours if you target it with an attack or a harmful spell."
        )
        return description


class DefyDeath(Feature):
    def __init__(self):
        super().__init__(
            name="Defy Death", origin="The Undying Patron Warlock Level 6"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        con_mod = character_stat_block.get_ability_modifier(Ability.CONSTITUTION)
        description = (
            f"Starting at 6th level, you can give yourself vitality when you cheat death or when you help someone else cheat it. You can regain hit points equal to 1d8 + your Constitution modifier ({con_mod}) (minimum of 1 hit point) when you succeed on a death saving throw or when you stabilize a creature with Spare the Dying.\n"
            "\n"
            "Once you use this feature, you can't use it again until you finish a long rest."
        )
        return StringUtils.add_boxes(description, 1, regain_all_on="long rest")

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        con_mod = character_stat_block.get_ability_modifier(Ability.CONSTITUTION)
        return [
            ("Trigger", "Succeed on death saving throw OR stabilize creature with Spare the Dying"),
            ("Effect", f"Regain 1d8 + Constitution modifier ({con_mod}) HP (min 1)"),
            ("Recharge", "Long rest"),
        ]


class UndyingNature(Feature):
    def __init__(self):
        super().__init__(
            name="Undying Nature", origin="The Undying Patron Warlock Level 10"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Beginning at 10th level, you can hold your breath indefinitely, and you don't require food, water, or sleep, although you still require rest to reduce exhaustion and still benefit from finishing short and long rests.\n"
            "\n"
            "In addition, you age at a slower rate. For every 10 years that pass, your body ages only 1 year, and you are immune to being magically aged."
        )
        return description


class IndestructibleLife(Feature):
    def __init__(self):
        super().__init__(
            name="Indestructible Life", origin="The Undying Patron Warlock Level 14"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        warlock_level = character_stat_block.get_class_level(
            Definitions.CharacterClass.WARLOCK
        )
        description = (
            f"When you reach 14th level, you partake of some of the true secrets of the Undying. On your turn, you can use a bonus action to regain hit points equal to 1d8 + your warlock level ({warlock_level}). Additionally, if you put a severed body part of yours back in place when you use this feature, the part reattaches.\n"
            "\n"
            "Once you use this feature, you can't use it again until you finish a short or long rest."
        )
        return StringUtils.add_boxes(description, 1, regain_all_on="short or long rest")

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        warlock_level = character_stat_block.get_class_level(
            Definitions.CharacterClass.WARLOCK
        )
        return [
            ("Action", "Bonus action on your turn"),
            ("Effect", f"Regain 1d8 + Warlock level ({warlock_level}) HP"),
            ("Bonus", "Reattach severed body parts"),
            ("Recharge", "Short or long rest"),
        ]
