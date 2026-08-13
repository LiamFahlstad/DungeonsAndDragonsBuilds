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


class Bagpipes(Item):
    def __init__(self):
        super().__init__(
            "Bagpipes", rarity=ItemRarity.COMMON, category=ItemCategory.MUSICAL_INSTRUMENT,
            weight=6.0, slots=1, value=30, is_homebrew=False,
            description_text="Ability: Charisma. Utilize: Play a known tune (DC 10), or improvise a song (DC 15).",
        )


class Drum(Item):
    def __init__(self):
        super().__init__(
            "Drum", rarity=ItemRarity.COMMON, category=ItemCategory.MUSICAL_INSTRUMENT,
            weight=3.0, slots=1, value=6, is_homebrew=False,
            description_text="Ability: Charisma. Utilize: Play a known tune (DC 10), or improvise a song (DC 15).",
        )


class Dulcimer(Item):
    def __init__(self):
        super().__init__(
            "Dulcimer", rarity=ItemRarity.COMMON, category=ItemCategory.MUSICAL_INSTRUMENT,
            weight=10.0, slots=1, value=25, is_homebrew=False,
            description_text="Ability: Charisma. Utilize: Play a known tune (DC 10), or improvise a song (DC 15).",
        )


class Flute(Item):
    def __init__(self):
        super().__init__(
            "Flute", rarity=ItemRarity.COMMON, category=ItemCategory.MUSICAL_INSTRUMENT,
            weight=1.0, slots=1, value=2, is_homebrew=False,
            description_text="Ability: Charisma. Utilize: Play a known tune (DC 10), or improvise a song (DC 15).",
        )


class Horn(Item):
    def __init__(self):
        super().__init__(
            "Horn", rarity=ItemRarity.COMMON, category=ItemCategory.MUSICAL_INSTRUMENT,
            weight=2.0, slots=1, value=3, is_homebrew=False,
            description_text="Ability: Charisma. Utilize: Play a known tune (DC 10), or improvise a song (DC 15).",
        )


class Lute(Item):
    def __init__(self):
        super().__init__(
            "Lute", rarity=ItemRarity.COMMON, category=ItemCategory.MUSICAL_INSTRUMENT,
            weight=2.0, slots=1, value=35, is_homebrew=False,
            description_text="Ability: Charisma. Utilize: Play a known tune (DC 10), or improvise a song (DC 15).",
        )


class Lyre(Item):
    def __init__(self):
        super().__init__(
            "Lyre", rarity=ItemRarity.COMMON, category=ItemCategory.MUSICAL_INSTRUMENT,
            weight=2.0, slots=1, value=30, is_homebrew=False,
            description_text="Ability: Charisma. Utilize: Play a known tune (DC 10), or improvise a song (DC 15).",
        )


class PanFlute(Item):
    def __init__(self):
        super().__init__(
            "Pan Flute", rarity=ItemRarity.COMMON, category=ItemCategory.MUSICAL_INSTRUMENT,
            weight=2.0, slots=1, value=12, is_homebrew=False,
            description_text="Ability: Charisma. Utilize: Play a known tune (DC 10), or improvise a song (DC 15).",
        )


class Shawm(Item):
    def __init__(self):
        super().__init__(
            "Shawm", rarity=ItemRarity.COMMON, category=ItemCategory.MUSICAL_INSTRUMENT,
            weight=1.0, slots=1, value=2, is_homebrew=False,
            description_text="Ability: Charisma. Utilize: Play a known tune (DC 10), or improvise a song (DC 15).",
        )


class Viol(Item):
    def __init__(self):
        super().__init__(
            "Viol", rarity=ItemRarity.COMMON, category=ItemCategory.MUSICAL_INSTRUMENT,
            weight=1.0, slots=1, value=30, is_homebrew=False,
            description_text="Ability: Charisma. Utilize: Play a known tune (DC 10), or improvise a song (DC 15).",
        )
