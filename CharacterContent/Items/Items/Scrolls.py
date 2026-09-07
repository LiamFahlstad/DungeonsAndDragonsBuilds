from CharacterContent.Spells.SpellFactory.Factory import SpellFactory

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


_SCROLL_LEVEL_RARITY = {
    0: ItemRarity.COMMON,
    1: ItemRarity.COMMON,
    2: ItemRarity.UNCOMMON,
    3: ItemRarity.UNCOMMON,
    4: ItemRarity.RARE,
    5: ItemRarity.RARE,
    6: ItemRarity.VERY_RARE,
    7: ItemRarity.VERY_RARE,
    8: ItemRarity.VERY_RARE,
    9: ItemRarity.LEGENDARY,
}

_SCROLL_LEVEL_VALUE = {
    0: 30,
    1: 50,
    2: 150,
    3: 300,
    4: 500,
    5: 1500,
    6: 3000,
    7: 9000,
    8: 12000,
    9: 20000,
}


class Scroll(Item):
    """A spell scroll for one specific spell, e.g. Scroll("Fog Cloud") -> "Scroll of 'Fog Cloud'"."""

    def __init__(self, spell_name: str):
        spell = SpellFactory.create(spell_name)
        self.spell_name = spell.name
        level_text = "cantrip" if spell.level == 0 else f"level {spell.level}"
        description_text = (
            f"A scroll inscribed with the {spell.school} {level_text} spell "
            f"'{spell.name}'. Casting time: {spell.casting_time}. Range: {spell.range}. "
            f"Duration: {spell.duration}. {spell.description}"
        )
        super().__init__(
            f"Scroll of '{spell.name}'",
            rarity=_SCROLL_LEVEL_RARITY.get(spell.level, ItemRarity.COMMON),
            category=ItemCategory.SCROLL,
            weight=None,
            slots=1,
            description_text=description_text,
            is_homebrew=False,
            is_consumable=True,
            value=_SCROLL_LEVEL_VALUE.get(spell.level, None),
        )
