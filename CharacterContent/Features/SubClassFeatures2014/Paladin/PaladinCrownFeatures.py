from Core.Definitions import Ability
from CharacterContent.Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class CrownSpells(Feature):
    def __init__(self):
        super().__init__(name="Oath of the Crown Spells", origin="Oath of the Crown Paladin Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain oath spells at the Paladin levels listed. When you reach a Paladin level specified in the Oath of the Crown Spells table, you thereafter always have the listed spells prepared.\n"
            "Oath of the Crown Spells\n"
            "Paladin Level\tSpells\n"
            "3\tCommand, Compelled Duel\n"
            "5\tWarding Bond, Zone of Truth\n"
            "9\tAura of Vitality, Spirit Guardians\n"
            "13\tBanishment, Guardian of Faith\n"
            "17\tCircle of Power, Geas"
        )
        return description


class ChampionChallenge(Feature):
    def __init__(self):
        super().__init__(name="Channel Divinity: Champion Challenge", origin="Oath of the Crown Paladin Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can use your Channel Divinity to issue a challenge that compels other creatures to do battle with you. As a bonus action, each creature of your choice that you can see within 30 feet of you must make a Wisdom saving throw. On a failed save, a creature can't willingly move more than 30 feet away from you. This effect ends on the creature if you are incapacitated or die or if the creature is more than 30 feet away from you."
        )
        return description

    def get_table_description(self, character_stat_block: CharacterStatBlock) -> list[tuple[str, str]]:
        return [
            ("What", "Issue challenging compulsion"),
            ("Action", "Bonus action"),
            ("Range", "30 feet"),
            ("Save", "Wisdom"),
            ("Effect", "Can't willingly move > 30 feet away from you"),
            ("Ends", "You incapacitated/dead, or creature > 30 feet away"),
        ]


class TurnTheTide(Feature):
    def __init__(self):
        super().__init__(name="Channel Divinity: Turn the Tide", origin="Oath of the Crown Paladin Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        charisma_modifier = character_stat_block.get_ability_modifier(Ability.CHARISMA)
        healing = max(1, charisma_modifier)
        description = (
            f"You can use your Channel Divinity to bolster injured creatures. As a bonus action, each creature of your choice that can hear you within 30 feet of you regains hit points equal to 1d6 + your Charisma modifier (minimum of 1) = 1d6 + {healing} if it has no more than half of its hit points."
        )
        return description

    def get_table_description(self, character_stat_block: CharacterStatBlock) -> list[tuple[str, str]]:
        charisma_modifier = character_stat_block.get_ability_modifier(Ability.CHARISMA)
        healing = max(1, charisma_modifier)
        return [
            ("What", "Bolster injured creatures"),
            ("Action", "Bonus action"),
            ("Range", "30 feet (hearing distance)"),
            ("Effect", f"Regain 1d6 + {healing} HP"),
            ("Condition", "Must have ≤ half HP"),
        ]


class DivineAllegiance(Feature):
    def __init__(self):
        super().__init__(name="Divine Allegiance", origin="Oath of the Crown Paladin Level 7")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When a creature within 5 feet of you takes damage, you can use your reaction to magically substitute your own health for that of the target creature, causing that creature not to take the damage. Instead, you take the damage. This damage to you can't be reduced or prevented in any way."
        )
        return description

    def get_table_description(self, character_stat_block: CharacterStatBlock) -> list[tuple[str, str]]:
        return [
            ("Trigger", "Creature within 5 feet takes damage"),
            ("Action", "Reaction"),
            ("Effect", "You take damage instead of creature"),
            ("Limitation", "Damage can't be reduced or prevented"),
        ]


class UnyieldingSaint(Feature):
    def __init__(self):
        super().__init__(name="Unyielding Saint", origin="Oath of the Crown Paladin Level 15", skippable_in_concise=True)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You have advantage on saving throws to avoid becoming paralyzed or stunned."
        return description


class ExaltedChampion(Feature):
    def __init__(self):
        super().__init__(name="Exalted Champion", origin="Oath of the Crown Paladin Level 20")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your presence on the field of battle is an inspiration to those dedicated to your cause. You can use your action to gain the following benefits for 1 hour:\n"
            "    * You have resistance to bludgeoning, piercing, and slashing damage from nonmagical weapons.\n"
            "    * Your allies have advantage on death saving throws while within 30 feet of you.\n"
            "    * You have advantage on Wisdom saving throws, as do your allies within 30 feet of you.\n"
            "\n"
            "This effect ends early if you are incapacitated or die. Once you use this feature, you can't use it again until you finish a long rest."
        )
        return StringUtils.add_boxes(description, 1, regain_all_on="long rest")

    def get_table_description(self, character_stat_block: CharacterStatBlock) -> list[tuple[str, str]]:
        return [
            ("What", "Inspiration on the field of battle"),
            ("Action", "Action"),
            ("Duration", "1 hour"),
            ("Resistance", "Nonmagical bludgeoning/piercing/slashing"),
            ("Ally Death Saves", "Allies within 30 feet have advantage"),
            ("Wisdom Saves", "You and allies within 30 feet have advantage"),
            ("Recharge", "Long rest"),
        ]
