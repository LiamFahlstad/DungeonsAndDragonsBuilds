from Core.Definitions import Ability, WARLOCK_HIT_DIE
import Core.Definitions as Definitions
from CharacterContent.Features.Core.BaseFeatures import Feature, FeatureUses
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class FiendSpells(Feature):
    def __init__(self):
        super().__init__(name="Fiend Spells", origin="Fiend Patron Warlock Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "The magic of your patron ensures you always have certain spells ready; when you reach a Warlock level specified in the Fiend Spells table, you thereafter always have the listed spells prepared."
        return description


class DarkOnesBlessing(Feature):
    def __init__(self):
        super().__init__(
            name="Dark One's Blessing", origin="Fiend Patron Warlock Level 3", usage_tags=["heal"]
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you reduce an enemy to 0 Hit Points, you gain Temporary Hit Points equal to your Charisma modifier plus your Warlock level (minimum of 1 Temporary Hit Point). You also gain this benefit if someone else reduces an enemy within 10 feet of you to 0 Hit Points."
        return description


class DarkOnesOwnLuck(Feature):
    def __init__(self):
        super().__init__(
            name="Dark One's Own Luck", origin="Fiend Patron Warlock Level 6", usage_tags=["buff"]
        , uses=FeatureUses(max_uses=Definitions.MAX_ABILITY_MODIFIER, regain_all_on="long rest", current_formula="Current amount: equal to your Charisma modifier."))

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can call on your fiendish patron to alter fate in your favor. When you make an ability check or a saving throw, you can use this feature to add 1d10 to your roll. You can do so after seeing the roll but before any of the roll's effects occur.\n"
            "You can use this feature a number of times equal to your Charisma modifier (minimum of once), but you can use it no more than once per roll. You regain all expended uses when you finish a Long Rest."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        charisma_modifier = character_stat_block.get_ability_modifier(Ability.CHARISMA)
        uses = max(1, charisma_modifier)
        return [
            ("When", "Ability check or saving throw (after seeing roll)"),
            ("Effect", "Add 1d10 to your roll"),
            ("Limit", "No more than once per roll"),
            ("Uses", f"{uses} per Long Rest"),
            ("Recharge", "Long Rest"),
        ]


class FiendishResilience(Feature):
    def __init__(self):
        super().__init__(
            name="Fiendish Resilience", origin="Fiend Patron Warlock Level 10", usage_tags=["buff"]
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Choose one damage type, other than Force, whenever you finish a Short or Long Rest. You have Resistance to that damage type until you choose a different one with this feature."
        return description


class HurlThroughHell(Feature):
    def __init__(self):
        super().__init__(
            name="Hurl Through Hell", origin="Fiend Patron Warlock Level 14", usage_tags=["damage", "control"]
        )

    def calculate_dc(self, character_stat_block: CharacterStatBlock) -> int:
        return character_stat_block.calculate_difficulty_class()

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Once per turn when you hit a creature with an attack roll, you can try to instantly transport the target through the Lower Planes. The target must succeed on a Charisma saving throw against your spell save DC, or the target disappears and hurtles through a nightmare landscape. The target takes 8d10 Psychic damage if it isn't a Fiend, and it has the Incapacitated condition until the end of your next turn, when it returns to the space it previously occupied or the nearest unoccupied space.\n"
            "Once you use this feature, you can't use it again until you finish a Long Rest unless you expend a Pact Magic spell slot (no action required) to restore your use of it."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Frequency", "Once per turn"),
            ("Trigger", "Hit creature with attack roll"),
            ("Save", "Charisma save DC"),
            ("Effect on Fail", "8d10 Psychic damage (non-Fiends only); Incapacitated until end of your next turn"),
            ("Recharge", "Long Rest or expend Pact Magic spell slot"),
        ]
