from .Base import Item, ItemCategory, ItemRarity


class Typewriter(Item):
    def __init__(self):
        super().__init__(
            "Typewriter",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.MUSICAL_INSTRUMENT,
            slots=1,
            description_text=(
                "A mechanical typewriter that can also be used as a musical instrument, "
                "producing rhythmic clacking sounds."
            ),
        )
