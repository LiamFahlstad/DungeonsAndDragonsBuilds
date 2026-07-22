from Core.Definitions import ARTIFICER_HIT_DIE, Ability
from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class AlchemistToolsOfTheTrade(Feature):
    def __init__(self):
        super().__init__(
            name="Tools of the Trade", origin="Alchemist Artificer Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain the following benefits.\n"
            "Tool Proficiency. You gain proficiency with Alchemist's Supplies and the Herbalism Kit. If you already have one of these proficiencies, you gain proficiency with one other type of Artisan's Tools of your choice (or with two other types if you have both).\n"
            "Potion Crafting. When you brew a potion using the crafting rules in the Dungeon Master's Guide, the amount of time required to craft it is halved."
        )
        return description


class AlchemistSpells(Feature):
    def __init__(self):
        super().__init__(name="Alchemist Spells", origin="Alchemist Artificer Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you reach an Artificer level specified in the Alchemist Spells table, you thereafter always have the listed spells prepared.\n"
            "Alchemist Spells\n"
            "Artificer Level	Spells\n"
            "3	Healing Word, Ray of Sickness\n"
            "5	Flaming Sphere, Melf's Acid Arrow\n"
            "9	Gaseous Form, Mass Healing Word\n"
            "13	Death Ward, Vitriolic Sphere\n"
            "17	Cloudkill, Raise Dead"
        )
        return description


class ExperimentalElixir(Feature):
    def __init__(self):
        super().__init__(
            name="Experimental Elixir", origin="Alchemist Artificer Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Whenever you finish a Long Rest while holding Alchemist's Supplies, you can use that tool to magically produce two elixirs. For each elixir, roll on the Experimental Elixir table for the elixir's effect, which is triggered when someone drinks the elixir. The elixir appears in a vial, and the vial vanishes when the elixir is drunk or poured out. If any elixir remains when you finish a Long Rest, the elixir and its vial vanish.\n"
            "Drinking an Elixir. As a Bonus Action, a creature can drink the elixir or administer it to another creature within 5 feet of itself.\n"
            "Creating Additional Elixirs. As a Magic action while holding Alchemist's Supplies, you can expend one spell slot to create another elixir. When you do so, you choose its effect from the Experimental Elixir table rather than rolling.\n"
            "When you reach certain Artificer levels, you can make an additional elixir at the end of each Long Rest: a total of three at level 5, four at level 9, and five at level 15.\n"
            "Experimental Elixir\n"
            "D6	Effect\n"
            "1	Healing. The drinker regains a number of Hit Points equal to 2d8 plus your Intelligence modifier. The number of Hit Points restored increases by 1d8 when you reach Artificer levels 9 (3d8) and 15 (4d8).\n"
            "2	Swiftness. The drinker's Speed increases by 10 feet for 1 hour. This bonus increases when you reach Artificer levels 9 (15 feet) and 15 (20 feet).\n"
            "3	Resilience. The drinker gains a +1 bonus to AC for 10 minutes. The duration increases when you reach Artificer levels 9 (1 hour) and 15 (8 hours).\n"
            "4	Boldness. The drinker can roll 1d4 and add the number rolled to every attack roll and saving throw it makes for the next minute. The duration increases when you reach Artificer levels 9 (10 minutes) and 15 (1 hour).\n"
            "5	Flight. The drinker gains a Fly Speed of 10 feet for 10 minutes. The Fly Speed increases when you reach Artificer levels 9 (20 feet) and 15 (30 feet).\n"
            "6	You determine the elixir's effect by choosing one of the other rows in this table."
        )
        return description


class AlchemicalSavant(Feature):
    def __init__(self):
        super().__init__(name="Alchemical Savant", origin="Alchemist Artificer Level 5")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Whenever you cast a spell using your Alchemist's Supplies as the Spellcasting Focus, you gain a bonus to one roll of the spell. That roll must restore Hit Points or be a damage roll that deals Acid, Fire, or Poison damage. The bonus equals your Intelligence modifier (minimum bonus of +1)."
        return description


class RestorativeReagents(Feature):
    def __init__(self):
        super().__init__(
            name="Restorative Reagents", origin="Alchemist Artificer Level 9"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        intelligence_modifier = character_stat_block.get_ability_modifier(Ability.INTELLIGENCE)
        uses = max(1, intelligence_modifier)
        description = "You can cast Lesser Restoration without expending a spell slot and without preparing the spell, provided you use Alchemist's Supplies as the Spellcasting Focus. You can do so a number of times equal to your Intelligence modifier (minimum of once), and you regain all expended uses when you finish a Long Rest."
        return StringUtils.add_boxes(description, uses, regain_all_on="long rest")


class ChemicalMastery(Feature):
    def __init__(self):
        super().__init__(name="Chemical Mastery", origin="Alchemist Artificer Level 15")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain the following benefits.\n"
            "Alchemical Eruption. When you cast an Artificer spell that deals Acid, Fire, or Poison damage to a target, you can also deal 2d8 Force damage to that target. You can use this benefit only once on each of your turns.\n"
            "Chemical Resistance. You gain Resistance to Acid damage and Poison damage. You also gain Immunity to the Poisoned condition.\n"
            "Conjured Cauldron. You can cast Tasha's Bubbling Cauldron without expending a spell slot, without preparing the spell, and without Material components, provided you use Alchemist's Supplies as the Spellcasting Focus. Once you use this feature, you can't use it again until you finish a Long Rest."
        )
        return description
