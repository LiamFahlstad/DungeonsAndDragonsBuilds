from Definitions import Ability
from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils

PALADIN_HIT_DIE = 10


class InspiringSmite(Feature):
    def __init__(self):
        super().__init__(name="Inspiring Smite", origin="Oath of Glory Paladin Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Immediately after you cast Divine Smite, you can expend one use of your Channel Divinity and distribute Temporary Hit Points to creatures of your choice within 30 feet of yourself, which can include you. The total number of Temporary Hit Points equals 2d8 plus your Paladin level, divided among the chosen creatures however you like."
        return description


class GlorySpells(Feature):
    def __init__(self):
        super().__init__(
            name="Oath of Glory Spells", origin="Oath of Glory Paladin Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "The magic of your oath ensures you always have certain spells ready; when you reach a Paladin level specified in the Oath of Glory Spells table, you thereafter always have the listed spells prepared.\n"
            "Oath of Glory Spells\n"
            "Paladin Level	Spells\n"
            "3	Guiding Bolt, Heroism\n"
            "5	Enhance Ability, Magic Weapon\n"
            "9	Haste, Protection from Energy\n"
            "13	Compulsion, Freedom of Movement\n"
            "17	Legend Lore, Yolande's Regal Presence"
        )
        return description


class PeerlessAthlete(Feature):
    def __init__(self):
        super().__init__(
            name="Peerless Athlete", origin="Oath of Glory Paladin Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "As a Bonus Action, you can expend one use of your Channel Divinity to augment your athleticism. For 1 hour, you have Advantage on Strength (Athletics) and Dexterity (Acrobatics) checks, and the distance of your Long and High Jumps increases by 10 feet (this extra distance costs movement as normal)."
        return description


class AuraOfAlacrity(Feature):
    def __init__(self):
        super().__init__(
            name="Aura of Alacrity", origin="Oath of Glory Paladin Level 7"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your Speed increases by 10 feet.\n"
            "In addition, whenever an ally enters your Aura of Protection for the first time on a turn or starts their turn there, the ally's Speed increases by 10 feet until the end of their next turn."
        )
        return description


class GloriousDefense(Feature):
    def __init__(self):
        super().__init__(
            name="Glorious Defense", origin="Oath of Glory Paladin Level 15"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        charisma_modifier = character_stat_block.get_ability_modifier(Ability.CHARISMA)
        uses = max(1, charisma_modifier)
        description = (
            "You can turn defense into a sudden strike. When you or another creature you can see within 10 feet of you is hit by an attack roll, you can take a Reaction to grant a bonus to the target's AC against that attack, potentially causing it to miss. The bonus equals your Charisma modifier (minimum of +1). If the attack misses, you can make one attack with a weapon against the attacker as part of this Reaction if the attacker is within your weapon's range.\n"
            "You can use this feature a number of times equal to your Charisma modifier (minimum of once), and you regain all expended uses when you finish a Long Rest."
        )
        return StringUtils.add_boxes(description, uses, regain_all_on="long rest")


class LivingLegend(Feature):
    def __init__(self):
        super().__init__(name="Living Legend", origin="Oath of Glory Paladin Level 20")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can empower yourself with the legends—whether true or exaggerated—of your great deeds. As a Bonus Action, you gain the following benefits for 10 minutes. Once you use this feature, you can't use it again until you finish a Long Rest. You can also restore your use of it by expending a level 5 spell slot (no action required).\n"
            "Charismatic. You are blessed with an otherworldly presence and have Advantage on all Charisma checks.\n"
            "Saving Throw Reroll. If you fail a saving throw, you can take a Reaction to reroll it. You must use this new roll.\n"
            "Unerring Strike. Once on each of your turns when you make an attack roll with a weapon and miss, you can cause that attack to hit instead."
        )
        return description
