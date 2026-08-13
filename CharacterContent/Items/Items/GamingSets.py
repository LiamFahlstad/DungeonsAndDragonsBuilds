from .Base import Item, ItemCategory, ItemRarity


class Dice(Item):
    def __init__(self):
        super().__init__(
            "Dice", rarity=ItemRarity.COMMON, category=ItemCategory.TOOL,
            slots=1, value=0.1, is_homebrew=False,
            description_text="Ability: Wisdom. Utilize: Discern whether someone is cheating (DC 10), or win the game (DC 20).",
        )


class Dragonchess(Item):
    def __init__(self):
        super().__init__(
            "Dragonchess", rarity=ItemRarity.COMMON, category=ItemCategory.TOOL,
            slots=1, value=1, is_homebrew=False,
            description_text="Ability: Wisdom. Utilize: Discern whether someone is cheating (DC 10), or win the game (DC 20).",
        )


class PlayingCards(Item):
    def __init__(self):
        super().__init__(
            "Playing Cards", rarity=ItemRarity.COMMON, category=ItemCategory.TOOL,
            slots=1, value=0.5, is_homebrew=False,
            description_text="Ability: Wisdom. Utilize: Discern whether someone is cheating (DC 10), or win the game (DC 20).",
        )


class ThreeDragonAnte(Item):
    def __init__(self):
        super().__init__(
            "Three-Dragon Ante", rarity=ItemRarity.COMMON, category=ItemCategory.TOOL,
            slots=1, value=1, is_homebrew=False,
            description_text="Ability: Wisdom. Utilize: Discern whether someone is cheating (DC 10), or win the game (DC 20).",
        )
