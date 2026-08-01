from .base import Item, ItemCategory, ItemRarity


class Costume(Item):
    def __init__(self, is_wearing: bool = True):
        super().__init__(
            "Costume",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.ADVENTURING_GEAR,
            slots=1,
            description_text=(
                "While wearing this costume, you have advantage on ability checks made to "
                "impersonate the person or type of person it represents."
            ),
            is_wearing=is_wearing,
            is_homebrew=False,
            value=5,
        )


class BrightFungalCloak(Item):
    def __init__(self, is_wearing: bool = True):
        super().__init__(
            "Bright Fungal Cloak",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.CLOTHING,
            weight=None,
            slots=1,
            description_text=(
                "While wearing a Bright Fungal Cloak, you can take a Bonus Action to furl or unfurl it. "
                "When the cloak is unfurled, it sheds Bright Light in a 5-foot radius and Dim Light for an "
                "additional 5 feet. One pound of fungus is sewn into a Bright Fungal Cloak. This fungus can "
                "be eaten as food. Once all the fungus is consumed, the cloak becomes a mundane set of "
                "Traveler's Clothes."
            ),
            is_wearing=is_wearing,
            is_homebrew=False,
            value=25,
        )


class DesertClothing(Item):
    def __init__(self, is_wearing: bool = True):
        super().__init__(
            "Desert Clothing",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.CLOTHING,
            weight=None,
            slots=1,
            description_text="When you are wearing Desert Clothing and not wearing Medium or Heavy armor, you automatically succeed on saving throws against the effects of extreme heat.",
            is_wearing=is_wearing,
            is_homebrew=False,
            value=5,
        )


class DevilMask(Item):
    def __init__(self, is_wearing: bool = True):
        super().__init__(
            "Devil Mask",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.CLOTHING,
            weight=None,
            slots=1,
            description_text="While you are wearing a Devil Mask, other creatures have Disadvantage on Intelligence (Investigation) and Wisdom (Insight) checks made to discern your true identity or intentions.",
            is_wearing=is_wearing,
            is_homebrew=False,
            value=25,
        )


class GarbOfLightAndShadow(Item):
    def __init__(self, is_wearing: bool = True):
        super().__init__(
            "Garb of Light and Shadow",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.WONDROUS,
            weight=None,
            slots=1,
            description_text="This garb appeals to Fey from one Domain of Delight, such as the Gloaming Court or the Summer Court. While wearing the garb, you have Advantage on ability checks to influence Fey associated with that Domain of Delight.",
            is_wearing=is_wearing,
            is_homebrew=False,
            value=50,
        )


class GenieRobe(Item):
    def __init__(self, is_wearing: bool = True):
        super().__init__(
            "Genie Robe",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.WONDROUS,
            weight=None,
            slots=1,
            description_text="This robe appeals to Elementals associated with a particular Elemental Plane (Air, Earth, Fire, Water). While wearing a Genie Robe, you have Advantage on ability checks made to influence Elementals associated with that plane.",
            is_wearing=is_wearing,
            is_homebrew=False,
            value=50,
        )


class MonsterCamouflage(Item):
    def __init__(self, is_wearing: bool = True):
        super().__init__(
            "Monster Camouflage",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.CLOTHING,
            weight=None,
            slots=1,
            description_text="A suit of Monster Camouflage looks like a Beast or Monstrosity, such as an owlbear. To discern that you're disguised, a creature must take the Study action to inspect your appearance and succeed on a DC 10 Intelligence (Investigation or Nature) check. The creature has Advantage on this check if it is within 30 feet of you and automatically succeeds on this check if you do anything the monster you're disguised as couldn't do.",
            is_wearing=is_wearing,
            is_homebrew=False,
            value=50,
        )


class WarmFungalClothing(Item):
    def __init__(self, is_wearing: bool = True):
        super().__init__(
            "Warm Fungal Clothing",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.CLOTHING,
            weight=None,
            slots=1,
            description_text=(
                "When you're wearing Warm Fungal Clothing, you automatically succeed on saving throws against "
                "the effects of extreme cold. One pound of fungus is sewn into Fungal Clothing. This fungus can "
                "be eaten as food. Once all the fungus is consumed, this becomes a mundane set of Traveler's Clothes."
            ),
            is_wearing=is_wearing,
            is_homebrew=False,
            value=15,
        )


class WinterCamouflage(Item):
    def __init__(self, is_wearing: bool = True):
        super().__init__(
            "Winter Camouflage",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.CLOTHING,
            weight=None,
            slots=1,
            description_text="While you wear Winter Camouflage in an appropriate environment, you have Advantage on Dexterity (Stealth) checks.",
            is_wearing=is_wearing,
            is_homebrew=False,
            value=50,
        )


class FineClothes(Item):
    def __init__(self):
        super().__init__(
            "Fine Clothes",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.CLOTHING,
            weight=6,
            slots=1,
            description_text="Fine Clothes are made of expensive fabrics and adorned with expertly crafted details. Some events and locations admit only people wearing these clothes.",
            is_homebrew=False,
            value=15,
        )


class Robe(Item):
    def __init__(self):
        super().__init__(
            "Robe",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.CLOTHING,
            weight=4,
            slots=1,
            description_text="A Robe has vocational or ceremonial significance. Some events and locations admit only people wearing a Robe bearing certain colors or symbols.",
            is_homebrew=False,
            value=1,
        )


class TravelersClothes(Item):
    def __init__(self):
        super().__init__(
            "Traveler's Clothes",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.CLOTHING,
            weight=4,
            slots=1,
            description_text="Traveler's Clothes are resilient garments designed for travel in various environments.",
            is_homebrew=False,
            value=2,
        )
