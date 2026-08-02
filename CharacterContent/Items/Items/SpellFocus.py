from .Base import Item, ItemCategory, ItemRarity


class ArcaneFocus(Item):
    def __init__(self):
        super().__init__(
            "Arcane Focus",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.SPELL_FOCUS,
            weight=None,
            slots=1,
            description_text="An Arcane Focus takes one of several forms and is bejeweled or carved to channel arcane magic. A Sorcerer, Warlock, or Wizard can use such an item as a Spellcasting Focus.",
            is_homebrew=False,
        )


class ComponentPouch(Item):
    def __init__(self):
        super().__init__(
            "Component Pouch",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.CONTAINER,
            weight=2,
            slots=1,
            description_text="A Component Pouch is watertight and filled with compartments that hold all the free Material components of your spells.",
            is_homebrew=False,
            value=25,
        )


class DruidicFocus(Item):
    def __init__(self):
        super().__init__(
            "Druidic Focus",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.SPELL_FOCUS,
            weight=None,
            slots=1,
            description_text="A Druidic Focus takes one of several forms and is carved, tied with ribbon, or painted to channel primal magic. A Druid or Ranger can use such an object as a Spellcasting Focus.",
            is_homebrew=False,
        )


class HolySymbol(Item):
    def __init__(self):
        super().__init__(
            "Holy Symbol",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.SPELL_FOCUS,
            weight=None,
            slots=1,
            description_text="A Holy Symbol takes one of several forms and is bejeweled or painted to channel divine magic. A Cleric or Paladin can use a Holy Symbol as a Spellcasting Focus.",
            is_homebrew=False,
        )
