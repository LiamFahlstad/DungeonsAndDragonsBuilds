from .Base import Item, ItemCategory, ItemRarity


class Arrows(Item):
    def __init__(self):
        super().__init__(
            "Arrows",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.AMMUNITION,
            slots=1,
            description_text="A bundle of arrows.",
            is_homebrew=False,
        )


class Bolts(Item):
    def __init__(self):
        super().__init__(
            "Bolts",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.PLACEHOLDER,
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
            is_homebrew=False,
        )


class FirearmBullets(Item):
    def __init__(self):
        super().__init__(
            "Firearm Bullets",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.PLACEHOLDER,
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
            is_homebrew=False,
        )


class SlingBullets(Item):
    def __init__(self):
        super().__init__(
            "Sling Bullets",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.PLACEHOLDER,
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
            is_homebrew=False,
        )
