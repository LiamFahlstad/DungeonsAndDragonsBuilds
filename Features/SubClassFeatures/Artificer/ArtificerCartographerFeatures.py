from Definitions import Ability
from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils

ARTIFICER_HIT_DIE = 8


class CartographerToolsOfTheTrade(Feature):
    def __init__(self):
        super().__init__(
            name="Tools of the Trade", origin="Cartographer Artificer Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain the following benefits.\n"
            "Tool Proficiency. You gain proficiency with Calligrapher's Supplies and Cartographer's Tools. If you already have one of these proficiencies, you gain proficiency with one other type of Artisan's Tools of your choice (or with two other types if you have both).\n"
            "Scroll Crafting. When you scribe a Spell Scroll using the crafting rules in the Player's Handbook, the amount of time required to craft it is halved."
        )
        return description


class CartographerSpells(Feature):
    def __init__(self):
        super().__init__(
            name="Cartographer Spells", origin="Cartographer Artificer Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you reach an Artificer level specified in the Cartographer Spells table, you thereafter always have the listed spells prepared.\n"
            "Cartographer Spells\n"
            "Artificer Level	Spells\n"
            "3	Faerie Fire, Guiding Bolt, Healing Word\n"
            "5	Locate Object, Mind Spike\n"
            "9	Call Lightning, Clairvoyance\n"
            "13	Banishment, Locate Creature\n"
            "17	Scrying, Teleportation Circle"
        )
        return description


class AdventurersAtlas(Feature):
    def __init__(self):
        super().__init__(
            name="Adventurer's Atlas", origin="Cartographer Artificer Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Whenever you finish a Long Rest while holding Cartographer's Tools, you can use that tool to create a set of magical maps by touching at least two creatures (one of whom can be yourself), up to a maximum number of creatures equal to 1 plus your Intelligence modifier (minimum of two creatures). Each target receives a magical map, which constantly updates to show the relative position of all the map holders but is illegible to all others. The maps last until you die or until you use this feature again, at which point any existing maps created by this feature immediately vanish.\n"
            "While carrying the map, a target gains the following benefits.\n"
            "Awareness. The target adds 1d4 to its Initiative rolls.\n"
            "Positioning. The target knows the location of all other map holders that are on the same plane of existence as itself. When casting a spell or creating another effect that requires being able to see the effect's target, a map holder can target another map holder regardless of sight or cover, so long as the other map holder is still within the effect's range."
        )
        return description


class MappingMagic(Feature):
    def __init__(self):
        super().__init__(name="Mapping Magic", origin="Cartographer Artificer Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        intelligence_modifier = character_stat_block.get_ability_modifier(Ability.INTELLIGENCE)
        uses = max(1, intelligence_modifier)
        description = (
            "You gain the following benefits.\n"
            "Illuminated Cartography. You can cast Faerie Fire without expending a spell slot, outlining the affected creatures as if in ink. You can do so a number of times equal to your Intelligence modifier (minimum of once), and you regain all expended uses when you finish a Long Rest.\n"
            "Portal Jump. On your turn, you can spend an amount of movement equal to half your Speed (round down) to teleport to an unoccupied space you can see within 10 feet of yourself or within 5 feet of a creature that is within 30 feet of you and holding one of your Adventurer's Atlas maps. You can't use this benefit if your Speed is 0."
        )
        return StringUtils.add_boxes(description, uses, regain_all_on="long rest")


class GuidedPrecision(Feature):
    def __init__(self):
        super().__init__(
            name="Guided Precision", origin="Cartographer Artificer Level 5"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Once per turn, whenever you cast a spell from your Cartographer Spells list or hit a creature affected by your Faerie Fire with an attack roll, you can add your Intelligence modifier to one damage roll of the spell or attack.\n"
            "In addition, taking damage can't cause you to lose Concentration on Faerie Fire."
        )
        return description


class IngeniousMovement(Feature):
    def __init__(self):
        super().__init__(
            name="Ingenious Movement", origin="Cartographer Artificer Level 9"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you use your Flash of Genius, you or a willing creature of your choice that you can see within 30 feet of yourself can teleport up to 30 feet to an unoccupied space you can see as part of that same Reaction."
        return description


class SuperiorAtlas(Feature):
    def __init__(self):
        super().__init__(
            name="Superior Atlas", origin="Cartographer Artificer Level 15"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your Adventurer's Atlas improves, gaining the following benefits.\n"
            "Safe Haven. When a map holder would be reduced to 0 Hit Points but not killed outright, that creature can destroy its map. The creature's Hit Points instead change to a number equal to twice your Artificer level, and the creature is teleported to an unoccupied space within 5 feet of you or another map holder of its choice.\n"
            "Unerring Path. If you are one of the map holders for your Adventurer's Atlas, you can cast Find the Path without expending a spell slot, without preparing the spell, and without needing spell components. Once you use this benefit, you can't use it again until you finish a Long Rest."
        )
        return description
