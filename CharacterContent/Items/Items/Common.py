from .Base import Item, ItemCategory, ItemRarity


class Ink(Item):
    def __init__(self):
        super().__init__(
            "Ink",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.COMMON,
            weight=None,
            slots=1,
            description_text="Ink comes in a 1-ounce bottle, which provides enough ink to write about 500 pages.",
            is_homebrew=False,
            value=10,
        )


class InkPen(Item):
    def __init__(self):
        super().__init__(
            "Ink Pen",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.COMMON,
            weight=None,
            slots=1,
            description_text="Using Ink, an Ink Pen is used to write or draw.",
            is_homebrew=False,
            value=0.02,
        )


class Paper(Item):
    def __init__(self):
        super().__init__(
            "Paper",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.COMMON,
            weight=None,
            slots=1,
            description_text="One sheet of Paper can hold about 250 handwritten words.",
            is_homebrew=False,
            value=0.2,
        )


class Parchment(Item):
    def __init__(self):
        super().__init__(
            "Parchment",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.COMMON,
            weight=None,
            slots=1,
            description_text="One sheet of Parchment can hold about 250 handwritten words.",
            is_homebrew=False,
            value=0.1,
        )


class String(Item):
    def __init__(self):
        super().__init__(
            "String",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.COMMON,
            weight=None,
            slots=1,
            description_text="String is 10 feet long. You can tie a knot in it as a Utilize action.",
            is_homebrew=False,
            value=0.1,
        )
