from .base import Item, ItemCategory, ItemRarity
from .gear import Mirror, Rope


class AnyMeleeWeaponPlaceholder(Item):
    def __init__(self):
        super().__init__(
            "Any Melee weapon (except Club, Greatclub, Quarterstaff, and Whip)",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.PLACEHOLDER,
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
            is_homebrew=False,
        )


class HeavyArmorPlaceholder(Item):
    def __init__(self):
        super().__init__(
            "Heavy armor",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.PLACEHOLDER,
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
            is_homebrew=False,
        )


class MediumArmorPlaceholder(Item):
    def __init__(self):
        super().__init__(
            "Medium armor (except Hide)",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.PLACEHOLDER,
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
            is_homebrew=False,
        )


class MirrorPlaceholder(Item):
    def __init__(self):
        super().__init__(
            "Mirror",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.GEAR,
            weight=0.5,
            slots=1,
            description_text="A handheld steel Mirror is useful for personal cosmetics but also for peeking around corners and reflecting light as a signal.",
            is_homebrew=False,
            value=5,
        )


class RangedWeaponsPlaceholder(Item):
    def __init__(self):
        super().__init__(
            "Ranged weapons (except Pistol, Musket, and Sling)",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.PLACEHOLDER,
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
            is_homebrew=False,
        )


class RopePlaceholder(Item):
    def __init__(self):
        super().__init__(
            "Rope",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.GEAR,
            weight=5,
            slots=1,
            description_text="As a Utilize action, you can tie a knot with Rope if you succeed on a DC 10 Dexterity (Sleight of Hand) check. The Rope can be burst with a successful DC 20 Strength (Athletics) check. You can bind an unwilling creature with the Rope only if the creature has the Grappled, Incapacitated, or Restrained condition. Escaping the Rope requires the creature to make a successful DC 15 Dexterity (Acrobatics) check as an action.",
            is_homebrew=False,
            value=1,
        )
