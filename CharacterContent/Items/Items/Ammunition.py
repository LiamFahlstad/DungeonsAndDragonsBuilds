from .Base import Item, ItemCategory, ItemRarity


class Arrows(Item):
    def __init__(self):
        super().__init__(
            "Arrows",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.AMMUNITION,
            weight=1,
            slots=1,
            description_text="A bundle of 20 arrows, for use with a Shortbow or Longbow.",
            is_homebrew=False,
            value=1,
        )


class CrossbowBolts(Item):
    def __init__(self):
        super().__init__(
            "Crossbow Bolts",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.AMMUNITION,
            weight=1.5,
            slots=1,
            description_text="A case of 20 bolts, for use with a Light, Hand, or Heavy Crossbow.",
            is_homebrew=False,
            value=1,
        )


class SlingBullets(Item):
    def __init__(self):
        super().__init__(
            "Sling Bullets",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.AMMUNITION,
            weight=1.5,
            slots=1,
            description_text="A pouch of 20 bullets, for use with a Sling.",
            is_homebrew=False,
            value=0.04,
        )


class BlowgunNeedles(Item):
    def __init__(self):
        super().__init__(
            "Blowgun Needles",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.AMMUNITION,
            weight=1,
            slots=1,
            description_text="A case of 50 needles, for use with a Blowgun.",
            is_homebrew=False,
            value=1,
        )
