
from Definitions import Ability
from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils

RANGER_HIT_DIE = 10


class FrigidExplorer(Feature):
    def __init__(self):
        super().__init__(name="Frigid Explorer", origin="Winter Walker Ranger Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain the following benefits.\n"
            "Biting Cold. Damage from your weapon attacks, Ranger spells, and Ranger features ignores Resistance to Cold damage.\n"
            "Frost Resistance. You have Resistance to Cold damage.\n"
            "Polar Strikes. When you hit a creature with an attack roll using a weapon, you can deal an extra 1d4 Cold damage to the target, which can take this extra damage only once per turn. When you reach Ranger level 11, this extra damage increases to 1d6."
        )
        return description


class HuntersRime(Feature):
    def __init__(self):
        super().__init__(name="Hunter's Rime", origin="Winter Walker Ranger Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Ice rimes you and your prey, protecting you and hindering them. When you cast Hunter's Mark, you gain Temporary Hit Points equal to 1d10 plus your Ranger level.\n"
            "Additionally, while a creature is marked by your Hunter's Mark, it can't take the Disengage action."
        )
        return description


class WinterWalkerSpells(Feature):
    def __init__(self):
        super().__init__(
            name="Winter Walker Spells", origin="Winter Walker Ranger Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you reach a Ranger level specified in the Winter Walker Spells table, you thereafter always have the listed spells prepared.\n"
            "Winter Walker Spells\n"
            "Ranger Level	Spells\n"
            "3	Ice Knife\n"
            "5	Hold Person\n"
            "9	Remove Curse\n"
            "13	Ice Storm\n"
            "17	Cone of Cold"
        )
        return description


class FortifyingSoul(Feature):
    def __init__(self):
        super().__init__(name="Fortifying Soul", origin="Winter Walker Ranger Level 7")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your experience surviving harrowing environments allows you to bolster your allies in addition to yourself. As a Magic action, choose a number of creatures you can see equal to your Wisdom modifier (minimum of one). Each chosen creature regains Hit Points equal to 1d10 plus your Ranger level and has Advantage on saving throws to avoid or end the Frightened condition for 1 hour.\n"
            "Once you use this feature, you can't use it again until you finish a Long Rest."
        )
        return description


class ChillingRetribution(Feature):
    def __init__(self):
        super().__init__(
            name="Chilling Retribution", origin="Winter Walker Ranger Level 11"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        wis_mod = character_stat_block.get_ability_modifier(Ability.WISDOM)
        uses = max(1, wis_mod)
        description = (
            "When a creature hits you with an attack roll, you can take a Reaction to force the creature to make a Wisdom saving throw against your spell save DC. On a failed save, the target has the Stunned condition until the end of your next turn. While the target is Stunned, its Speed is reduced to 0 feet.\n"
            "You can use this feature a number of times equal to your Wisdom modifier (minimum of once), and you regain all expended uses when you finish a Long Rest."
        )
        return StringUtils.add_boxes(description, uses, regain_all_on="long rest")


class FrozenHaunt(Feature):
    def __init__(self):
        super().__init__(name="Frozen Haunt", origin="Winter Walker Ranger Level 15")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you cast Hunter's Mark, you can adopt a ghostly, snowy form. This form lasts until the spell ends, and while you are in this form, you gain the following benefits. Once you use this feature, you can't use it again until you finish a Long Rest unless you expend a level 4+ spell slot (no action required).\n"
            "Frozen Soul. You have Immunity to Cold damage. When you first adopt this form and at the start of each of your subsequent turns, each creature of your choice in a 15-foot Emanation originating from you takes 2d4 Cold damage.\n"
            "Partially Incorporeal. You have Immunity to the Grappled, Prone, and Restrained conditions. You can move through creatures and objects as if they were Difficult Terrain, but you take 1d10 Force damage if you end your turn inside a creature or an object. If the form ends while you are inside a creature or an object, you are shunted to the nearest unoccupied space."
        )
        return description
