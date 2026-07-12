from Definitions import Ability
from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils

CLERIC_HIT_DIE = 8


class GraveDomainSpells(Feature):
    def __init__(self):
        super().__init__(
            name="Grave Domain Spells", origin="Grave Domain Cleric Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your connection to this divine domain ensures you always have certain spells ready. When you reach a Cleric level specified in the Grave Domain Spells table, you thereafter always have the listed spells prepared.\n"
            "Grave Domain Spells\n"
            "Cleric Level	Spells\n"
            "3	Detect Evil and Good, False Life, Gentle Repose, Ray of Enfeeblement, Spare the Dying\n"
            "5	Revivify, Vampiric Touch\n"
            "7	Blight, Death Ward\n"
            "9	Dispel Evil and Good, Raise Dead"
        )
        return description


class CircleOfMortality(Feature):
    def __init__(self):
        super().__init__(
            name="Circle of Mortality", origin="Grave Domain Cleric Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can manipulate the balance between life and death, granting you the following benefits.\n"
            "Pull of Death. Once per turn, when you deal damage to a creature that's missing any Hit Points by casting a spell or by hitting with an attack roll, that creature takes an extra 1d4 Necrotic damage. This extra damage increases to 1d6 when you reach Cleric level 11.\n"
            "Return to Life. You can cast Spare the Dying as a Bonus Action.\n"
            "Additionally, when you would normally roll one or more dice to restore Hit Points to a creature at 0 Hit Points with a spell or Channel Divinity, don't roll those dice for the healing; instead, use the highest number possible for each die. For example, instead of restoring 2d4 Hit Points to a creature at 0 Hit Points with a spell, you restore 8."
        )
        return description


class PathToTheGrave(Feature):
    def __init__(self):
        super().__init__(name="Path to the Grave", origin="Grave Domain Cleric Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "As a Bonus Action, you present your Holy Symbol and expend a use of Channel Divinity to curse one creature you can see within 30 feet of yourself until the start of your next turn. While cursed, the creature has Disadvantage on attack rolls and saving throws.\n"
            "When you or an ally you can see hits the cursed target with an attack roll, you can end the curse early (no action required) to make the attack deal extra Necrotic or Radiant damage (your choice) equal to your Cleric level."
        )
        return description


class SentinelAtDeathsDoor(Feature):
    def __init__(self):
        super().__init__(
            name="Sentinel at Death's Door", origin="Grave Domain Cleric Level 6"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        wisdom_modifier = character_stat_block.get_ability_modifier(Ability.WISDOM)
        uses = max(1, wisdom_modifier)
        description = (
            "When you or a Bloodied creature you can see within 60 feet of yourself is hit with an attack roll, you can take a Reaction to halve that attack's damage (round down). If the triggering attack roll was a Critical Hit, any effects triggered by a Critical Hit are canceled.\n"
            "You can use this feature a number of times equal to your Wisdom modifier (minimum of once). You regain all expended uses when you finish a Long Rest."
        )
        return StringUtils.add_boxes(description, uses, regain_all_on="long rest")


class DivineReaper(Feature):
    def __init__(self):
        super().__init__(name="Divine Reaper", origin="Grave Domain Cleric Level 17")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your deep connection to this domain renders you a hallowed harbinger of death, granting you the following benefits.\n"
            "Enhanced Necromancy. When you cast a spell of level 5 or lower from the Necromancy school that targets one creature, or when you cast a spell from the Grave Domain Spells table, you can expend a use of Channel Divinity to target a second creature within the spell's range. If the spell requires costly or consumed Material components, you must provide Material components for each target.\n"
            "Keeper of Souls. When an enemy dies within 60 feet of you, you or one creature you can see within 60 feet of yourself regains Hit Points equal to twice your Cleric level. You can't use this feature if you have the Incapacitated condition. Once you use this feature, you can't use it again until you finish a Short or Long Rest, unless you expend a level 6+ spell slot (no action required) to restore your use of it."
        )
        return description
