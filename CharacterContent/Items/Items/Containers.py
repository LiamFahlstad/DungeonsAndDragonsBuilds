from .Base import Item, ItemCategory, ItemRarity


class Quiver(Item):
    def __init__(self):
        super().__init__(
            "Quiver",
            rarity=ItemRarity.UNCOMMON,
            category=ItemCategory.CONTAINER,
            slots=1,
            description_text="A regular quiver",
            is_homebrew=False,
            value=1,
        )


class Barrel(Item):
    def __init__(self):
        super().__init__(
            "Barrel",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.CONTAINER,
            weight=70,
            slots=5,
            description_text="A Barrel holds up to 40 gallons of liquid or up to 4 cubic feet of dry goods.",
            is_homebrew=False,
            value=2,
        )


class Basket(Item):
    def __init__(self):
        super().__init__(
            "Basket",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.CONTAINER,
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
            category=ItemCategory.CONTAINER,
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
            slots=3,
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


class Waterskin(Item):
    def __init__(self):
        super().__init__(
            "Waterskin",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.CONTAINER,
            slots=1,
            description_text="Holds up to 4 pints of liquid. Essential for survival, as insufficient water can lead to dehydration.",
            is_homebrew=False,
            value=0.2,
        )


class Flask(Item):
    def __init__(self):
        super().__init__(
            "Flask",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.CONTAINER,
            weight=1,
            slots=1,
            description_text="A Flask holds up to 1 pint.",
            is_homebrew=False,
            value=0.02,
        )


class GlassBottle(Item):
    def __init__(self):
        super().__init__(
            "Glass Bottle",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.CONTAINER,
            weight=2,
            slots=1,
            description_text="A Glass Bottle holds up to 1½ pints.",
            is_homebrew=False,
            value=2,
        )


class Vial(Item):
    def __init__(self):
        super().__init__(
            "Vial",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.CONTAINER,
            weight=None,
            slots=1,
            description_text="A Vial holds up to 4 ounces.",
            is_homebrew=False,
            value=1,
        )
