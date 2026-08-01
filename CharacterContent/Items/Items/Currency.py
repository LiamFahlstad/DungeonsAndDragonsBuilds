from .Base import Item, ItemCategory, ItemRarity


class Gold(Item):
    def __init__(self):
        super().__init__(
            "Gold Pieces",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.CURRENCY,
            slots=0,
            description_text="A stack of gold pieces.",
            is_homebrew=False,
            value=1,
        )


class Silver(Item):
    def __init__(self):
        super().__init__(
            "Silver Pieces",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.CURRENCY,
            slots=0,
            description_text="A stack of silver pieces.",
            is_homebrew=False,
            value=0.1,
        )
