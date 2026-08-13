from .Base import Item, ItemCategory, ItemRarity


class AlchemistsSupplies(Item):
    def __init__(self):
        super().__init__(
            "Alchemist's Supplies", rarity=ItemRarity.COMMON, category=ItemCategory.TOOL,
            weight=8.0, slots=1, value=50, is_homebrew=False,
            description_text="Ability: Intelligence. Utilize: Identify a substance (DC 15), or start a fire (DC 15).",
        )


class BrewersSupplies(Item):
    def __init__(self):
        super().__init__(
            "Brewer's Supplies", rarity=ItemRarity.COMMON, category=ItemCategory.TOOL,
            weight=9.0, slots=1, value=20, is_homebrew=False,
            description_text="Ability: Intelligence. Utilize: Detect poisoned drink (DC 15), or identify alcohol (DC 10).",
        )


class CalligraphersSupplies(Item):
    def __init__(self):
        super().__init__(
            "Calligrapher's Supplies", rarity=ItemRarity.COMMON, category=ItemCategory.TOOL,
            weight=5.0, slots=1, value=10, is_homebrew=False,
            description_text="Ability: Dexterity. Utilize: Write text with impressive flourishes that guard against forgery (DC 15).",
        )


class CarpentersTools(Item):
    def __init__(self):
        super().__init__(
            "Carpenter's Tools", rarity=ItemRarity.COMMON, category=ItemCategory.TOOL,
            weight=6.0, slots=1, value=8, is_homebrew=False,
            description_text="Ability: Strength. Utilize: Seal or pry open a door or container (DC 20).",
        )


class CartographersTools(Item):
    def __init__(self):
        super().__init__(
            "Cartographer's Tools", rarity=ItemRarity.COMMON, category=ItemCategory.TOOL,
            weight=6.0, slots=1, value=15, is_homebrew=False,
            description_text="Ability: Wisdom. Utilize: Draft a map of a small area (DC 15).",
        )


class CobblersTools(Item):
    def __init__(self):
        super().__init__(
            "Cobbler's Tools", rarity=ItemRarity.COMMON, category=ItemCategory.TOOL,
            weight=5.0, slots=1, value=5, is_homebrew=False,
            description_text="Ability: Dexterity. Utilize: Modify footwear to give Advantage on the wearer's next Dexterity (Acrobatics) check (DC 10).",
        )


class CooksUtensils(Item):
    def __init__(self):
        super().__init__(
            "Cook's Utensils", rarity=ItemRarity.COMMON, category=ItemCategory.TOOL,
            weight=8.0, slots=1, value=1, is_homebrew=False,
            description_text="Ability: Wisdom. Utilize: Improve food's flavor (DC 10), or detect spoiled or poisoned food (DC 15).",
        )


class GlassblowersTools(Item):
    def __init__(self):
        super().__init__(
            "Glassblower's Tools", rarity=ItemRarity.COMMON, category=ItemCategory.TOOL,
            weight=5.0, slots=1, value=30, is_homebrew=False,
            description_text="Ability: Intelligence. Utilize: Discern what a glass object held in the past 24 hours (DC 15).",
        )


class JewelersTools(Item):
    def __init__(self):
        super().__init__(
            "Jeweler's Tools", rarity=ItemRarity.COMMON, category=ItemCategory.TOOL,
            weight=2.0, slots=1, value=25, is_homebrew=False,
            description_text="Ability: Intelligence. Utilize: Discern a gem's value (DC 15).",
        )


class LeatherworkersTools(Item):
    def __init__(self):
        super().__init__(
            "Leatherworker's Tools", rarity=ItemRarity.COMMON, category=ItemCategory.TOOL,
            weight=5.0, slots=1, value=5, is_homebrew=False,
            description_text="Ability: Dexterity. Utilize: Add a design to a leather item (DC 10).",
        )


class MasonsTools(Item):
    def __init__(self):
        super().__init__(
            "Mason's Tools", rarity=ItemRarity.COMMON, category=ItemCategory.TOOL,
            weight=8.0, slots=1, value=10, is_homebrew=False,
            description_text="Ability: Strength. Utilize: Chisel a symbol or hole in stone (DC 10).",
        )


class PaintersSupplies(Item):
    def __init__(self):
        super().__init__(
            "Painter's Supplies", rarity=ItemRarity.COMMON, category=ItemCategory.TOOL,
            weight=5.0, slots=1, value=10, is_homebrew=False,
            description_text="Ability: Wisdom. Utilize: Paint a recognizable image of something you've seen (DC 10).",
        )


class PottersTools(Item):
    def __init__(self):
        super().__init__(
            "Potter's Tools", rarity=ItemRarity.COMMON, category=ItemCategory.TOOL,
            weight=3.0, slots=1, value=10, is_homebrew=False,
            description_text="Ability: Intelligence. Utilize: Discern what a ceramic object held in the past 24 hours (DC 15).",
        )


class SmithsTools(Item):
    def __init__(self):
        super().__init__(
            "Smith's Tools", rarity=ItemRarity.COMMON, category=ItemCategory.TOOL,
            weight=8.0, slots=1, value=20, is_homebrew=False,
            description_text="Ability: Strength. Utilize: Pry open a door or container (DC 20).",
        )


class TinkersTools(Item):
    def __init__(self):
        super().__init__(
            "Tinker's Tools", rarity=ItemRarity.COMMON, category=ItemCategory.TOOL,
            weight=10.0, slots=1, value=50, is_homebrew=False,
            description_text="Ability: Dexterity. Utilize: Assemble a Tiny item composed of scrap, which falls apart in 1 minute (DC 20).",
        )


class WeaversTools(Item):
    def __init__(self):
        super().__init__(
            "Weaver's Tools", rarity=ItemRarity.COMMON, category=ItemCategory.TOOL,
            weight=5.0, slots=1, value=1, is_homebrew=False,
            description_text="Ability: Dexterity. Utilize: Mend a tear in clothing (DC 10), or sew a Tiny design (DC 10).",
        )


class WoodcarversTools(Item):
    def __init__(self):
        super().__init__(
            "Woodcarver's Tools", rarity=ItemRarity.COMMON, category=ItemCategory.TOOL,
            weight=5.0, slots=1, value=1, is_homebrew=False,
            description_text="Ability: Dexterity. Utilize: Carve a pattern in wood (DC 10).",
        )
