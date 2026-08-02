from CharacterContent.Features.Core.Improvements import CarryingCapacityBonus

from .Base import Item, ItemCategory, ItemRarity


class Pouch(Item):
    def __init__(self, is_wearing: bool = True):
        super().__init__(
            "Pouch",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.CARRYING_GEAR,
            slots=1,
            description_text="A small belt pouch holding up to 6 pounds within one-fifth of a cubic foot.",
            improvements=[CarryingCapacityBonus(2, source="Pouch")],
            is_wearing=is_wearing,
            is_homebrew=False,
            value=0.5,
        )


class Satchel(Item):
    def __init__(self, is_wearing: bool = True):
        super().__init__(
            "Satchel",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.CARRYING_GEAR,
            weight=3,
            slots=1,
            description_text=(
                "A shoulder-slung bag with a few compartments, holding up to 15 pounds of gear."
            ),
            improvements=[CarryingCapacityBonus(3, source="Satchel")],
            is_wearing=is_wearing,
            is_homebrew=False,
            value=2,
        )


class SidePack(Item):
    def __init__(self, is_wearing: bool = True):
        super().__init__(
            "Side Pack",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.CARRYING_GEAR,
            weight=4,
            slots=1,
            description_text=(
                "A reinforced pack that straps to your hip or thigh, holding up to 20 pounds of gear. "
                "Smaller than a full Backpack, but quicker to reach into mid-combat."
            ),
            improvements=[CarryingCapacityBonus(4, source="Side Pack")],
            is_wearing=is_wearing,
            is_homebrew=False,
            value=3,
        )


class Backpack(Item):
    def __init__(self, is_wearing: bool = True):
        super().__init__(
            "Backpack",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.CARRYING_GEAR,
            slots=1,
            description_text=(
                "A backpack that can hold up to 30 pounds of gear within 1 cubic foot. "
                "It can also be strapped to a mount as a saddlebag."
            ),
            improvements=[CarryingCapacityBonus(8, source="Backpack")],
            is_wearing=is_wearing,
            is_homebrew=False,
            value=2,
        )
