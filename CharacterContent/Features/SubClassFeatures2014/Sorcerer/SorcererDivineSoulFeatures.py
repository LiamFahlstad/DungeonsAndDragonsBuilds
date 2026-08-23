import Core.Definitions as Definitions
from Core.Definitions import SORCERER_HIT_DIE
from CharacterContent.Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class DivineMagic(Feature):
    def __init__(self):
        super().__init__(name="Divine Magic", origin="Divine Soul Sorcerer Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your link to the divine allows you to learn spells normally associated with the cleric class. When your Spellcasting feature lets you learn a sorcerer cantrip or a sorcerer spell of 1st level or higher, you can choose the new spell from the cleric spell list or the sorcerer spell list. You must otherwise obey all the restrictions for selecting the spell, and it becomes a sorcerer spell for you.\n"
            "\n"
            "In addition, choose an affinity for the source of your divine power: good, evil, law, chaos, or neutrality. You learn an additional spell based on that affinity, as shown below. It is a sorcerer spell for you, but it doesn't count against your number of sorcerer spells known. If you later replace this spell, you must replace it with a spell from the cleric spell list.\n"
            "\n"
            "Affinity\tSpell\n"
            "Good\tCure Wounds\n"
            "Evil\tInflict Wounds\n"
            "Law\tBless\n"
            "Chaos\tBane\n"
            "Neutrality\tProtection from Evil and Good"
        )
        return description


class FavoredByTheGods(Feature):
    def __init__(self):
        super().__init__(name="Favored by the Gods", origin="Divine Soul Sorcerer Level 3", usage_tags=["buff"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Divine power guards your destiny. If you fail a saving throw or miss with an attack roll, you can roll 2d4 and add it to the total, possibly changing the outcome.\n"
            "\n"
            "Once you use this feature, you can't use it again until you finish a short or long rest."
        )
        return StringUtils.add_boxes(description, 1, regain_all_on="short or long rest")

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Trigger", "Fail saving throw or miss attack roll"),
            ("Effect", "Roll 2d4 and add to total"),
            ("Recharge", "Short or long rest"),
        ]


class EmpoweredHealing(Feature):
    def __init__(self):
        super().__init__(name="Empowered Healing", origin="Divine Soul Sorcerer Level 6", range="5 Feet", usage_tags=["buff", "heal"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "The divine energy coursing through you can empower healing spells. Whenever you or an ally within 5 feet of you rolls dice to determine the number of hit points a spell restores, you can spend 1 sorcery point to reroll any number of those dice once, provided you aren't incapacitated. You can use this feature only once per turn."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Trigger", "You or ally within 5 feet rolls healing dice"),
            ("Cost", "1 sorcery point"),
            ("Effect", "Reroll any number of those dice once"),
            ("Restriction", "Once per turn, not while incapacitated"),
        ]


class AngelicForm(Feature):
    def __init__(self):
        super().__init__(name="Angelic Form", origin="Divine Soul Sorcerer Level 14", action_type="bonus_action", duration="Until Incapacitated, Dead, or Dismissed", range="Self", usage_tags=["utility"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can use a bonus action to manifest a pair of spectral wings from your back. While the wings are present, you have a flying speed of 30 feet. The wings last until you're incapacitated, you die, or you dismiss them as a bonus action.\n"
            "\n"
            "The affinity you chose for your Divine Magic feature determines the appearance of the spectral wings: eagle wings for good or law, bat wings for evil or chaos, and dragonfly wings for neutrality."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Action", "Bonus action"),
            ("Effect", "Manifest spectral wings"),
            ("Flying Speed", "30 feet"),
            ("Duration", "Until incapacitated, dead, or dismissed (bonus action)"),
        ]


class UnearthlyRecovery(Feature):
    def __init__(self):
        super().__init__(name="Unearthly Recovery", origin="Divine Soul Sorcerer Level 18", action_type="bonus_action", range="Self", usage_tags=["heal"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain the ability to overcome grievous injuries. As a bonus action when you have fewer than half of your hit points remaining, you can regain a number of hit points equal to half your hit point maximum.\n"
            "\n"
            "Once you use this feature, you can't use it again until you finish a long rest."
        )
        return StringUtils.add_boxes(description, 1, regain_all_on="long rest")

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Trigger", "At fewer than half your hit points"),
            ("Action", "Bonus action"),
            ("Effect", "Regain hit points equal to half your HP maximum"),
            ("Recharge", "Long rest"),
        ]
