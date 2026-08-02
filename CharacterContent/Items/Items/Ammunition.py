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
