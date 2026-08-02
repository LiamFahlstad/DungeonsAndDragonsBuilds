from .Base import Item, ItemCategory, ItemRarity


class SpellScroll(Item):
    def __init__(self):
        super().__init__(
            "Spell Scroll",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.SCROLL,
            weight=None,
            slots=1,
            description_text="A Spell Scroll is a magic item that bears the words of a cantrip or a level 1 spell, determined by the scroll's creator. If the spell is on your class's spell list, you can read the scroll and cast the spell using its normal casting time and without providing any Material components. If the spell requires a saving throw or an attack roll, the spell save DC is 13, and the attack bonus is +5. The scroll disintegrates when the casting is completed.",
            is_homebrew=False,
            is_consumable=True,
        )
