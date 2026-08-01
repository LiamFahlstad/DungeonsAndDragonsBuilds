from CharacterContent.Features.Core.Improvements import CarryingCapacityBonus
from .base import Item, ItemCategory, ItemRarity


class Quiver(Item):
    def __init__(self):
        super().__init__(
            "Quiver",
            rarity=ItemRarity.UNCOMMON,
            category=ItemCategory.COMMON,
            slots=1,
            description_text="A regular quiver",
            is_homebrew=False,
            value=1,
        )


class Backpack(Item):
    def __init__(self, is_wearing: bool = True):
        super().__init__(
            "Backpack",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.CONTAINER,
            slots=1,
            description_text=(
                "A backpack that can hold up to 30 pounds of gear within 1 cubic foot. "
                "It can also be strapped to a mount as a saddlebag."
            ),
            improvements=[CarryingCapacityBonus(10, source="Backpack")],
            is_wearing=is_wearing,
            is_homebrew=False,
            value=2,
        )


class Barrel(Item):
    def __init__(self):
        super().__init__(
            "Barrel",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.GEAR,
            weight=70,
            slots=1,
            description_text="A Barrel holds up to 40 gallons of liquid or up to 4 cubic feet of dry goods.",
            is_homebrew=False,
            value=2,
        )


class Basket(Item):
    def __init__(self):
        super().__init__(
            "Basket",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.GEAR,
            weight=2,
            slots=1,
            description_text="A Basket holds up to 40 pounds within 2 cubic feet.",
            is_homebrew=False,
            value=0.4,
        )


class Bucket(Item):
    def __init__(self):
        super().__init__(
            "Bucket",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.GEAR,
            weight=2,
            slots=1,
            description_text="A Bucket holds up to half a cubic foot of contents.",
            is_homebrew=False,
            value=0.05,
        )


class Chest(Item):
    def __init__(self):
        super().__init__(
            "Chest",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.CONTAINER,
            weight=25,
            slots=1,
            description_text="A Chest holds up to 12 cubic feet of contents.",
            is_homebrew=False,
            value=5,
        )


class CrossbowBoltCase(Item):
    def __init__(self):
        super().__init__(
            "Crossbow Bolt Case",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.CONTAINER,
            weight=1,
            slots=1,
            description_text="A Crossbow Bolt Case holds up to 20 Bolts.",
            is_homebrew=False,
            value=1,
        )


class IronPot(Item):
    def __init__(self):
        super().__init__(
            "Iron Pot",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.GEAR,
            weight=10,
            slots=1,
            description_text="An Iron Pot holds up to 1 gallon.",
            is_homebrew=False,
            value=2,
        )


class Jug(Item):
    def __init__(self):
        super().__init__(
            "Jug",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.CONTAINER,
            weight=4,
            slots=1,
            description_text="A Jug holds up to 1 gallon.",
            is_homebrew=False,
            value=0.02,
        )


class MapOrScrollCase(Item):
    def __init__(self):
        super().__init__(
            "Map or Scroll Case",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.CONTAINER,
            weight=1,
            slots=1,
            description_text="A Map or Scroll Case holds up to 10 sheets of paper or 5 sheets of parchment.",
            is_homebrew=False,
            value=1,
        )


class Pouch(Item):
    def __init__(self):
        super().__init__(
            "Pouch",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.CONTAINER,
            weight=1,
            slots=1,
            description_text="A Pouch holds up to 6 pounds within one-fifth of a cubic foot.",
            is_homebrew=False,
            value=0.5,
        )


class Sack(Item):
    def __init__(self):
        super().__init__(
            "Sack",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.CONTAINER,
            weight=0.5,
            slots=1,
            description_text="A Sack holds up to 30 pounds within 1 cubic foot.",
            is_homebrew=False,
            value=0.01,
        )
