from .Base import ConsumableItem, Item, ItemCategory, ItemRarity


class Candle(ConsumableItem):
    def __init__(self):
        super().__init__(
            "Candle",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.UTILITY,
            slots=0,
            description_text="For 1 hour, a lit Candle sheds Bright Light in a 5-foot radius and Dim Light for an additional 5 feet.",
            is_homebrew=False,
            value=0.01,
        )


class FlasksOfOil(ConsumableItem):
    def __init__(self):
        super().__init__(
            "Flask of Oil",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.UTILITY,
            slots=1,
            description_text=(
                "You can throw this flask (range 20 ft) to coat a creature or object. "
                "On a failed Dexterity save (DC = 8 + Dex mod + proficiency bonus), the target is covered in oil. "
                "If it takes fire damage within 1 minute, it takes an extra 5 fire damage.\n\n"
                "Alternatively, you can pour it on the ground (5-foot-square). If ignited, it burns for 2 rounds, "
                "dealing 5 fire damage to creatures entering or ending their turn in the area (once per turn).\n\n"
                "Oil can also be used as fuel, burning for up to 6 hours in a lamp or lantern."
            ),
            is_homebrew=False,
            value=0.1,
        )


class Rations(ConsumableItem):
    def __init__(self):
        super().__init__(
            "Rations",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.CONSUMABLE,
            slots=1,
            description_text=(
                "Travel-ready food such as jerky, dried fruit, hardtack, and nuts. "
                "Essential for long journeys; lack of food can lead to malnutrition."
            ),
            is_homebrew=False,
            value=0.5,
        )


class Antitoxin(ConsumableItem):
    def __init__(self):
        super().__init__(
            "Antitoxin",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.CONSUMABLE,
            slots=0,
            description_text="As a Bonus Action, you can drink a vial of Antitoxin to gain Advantage on saving throws to avoid or end the Poisoned condition for 1 hour.",
            is_homebrew=False,
            value=50,
        )


class HealersKit(ConsumableItem):
    def __init__(self):
        super().__init__(
            "Healer's Kit",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.CONSUMABLE,
            slots=1,
            description_text="A Healer's Kit has ten uses. As a Utilize action, you can expend one of its uses to stabilize an Unconscious creature that has 0 Hit Points without needing to make a Wisdom (Medicine) check.",
            is_homebrew=False,
            value=5,
        )


class Torch(ConsumableItem):
    def __init__(self):
        super().__init__(
            "Torch",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.UTILITY,
            slots=1,
            description_text=(
                "Burns for 1 hour, providing bright light in a 20-foot radius and dim light for another 20 feet.\n\n"
                "It can be used as a simple melee weapon. On a hit, it deals 1 fire damage."
            ),
            is_homebrew=False,
            value=0.01,
        )


class Beans(ConsumableItem):
    def __init__(self):
        super().__init__(
            "Can of Beans",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.CONSUMABLE,
            slots=1,
            description_text="A simple can of preserved beans. Provides a basic meal when consumed.",
        )


class Acid(Item):
    def __init__(self):
        super().__init__(
            "Acid",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.CONSUMABLE,
            weight=1,
            slots=1,
            description_text="When you take the Attack action, you can replace one of your attacks with throwing a vial of Acid. Target one creature or object you can see within 20 feet of yourself. The target must succeed on a Dexterity saving throw (DC 8 plus your Dexterity modifier and Proficiency Bonus) or take 2d6 Acid damage.",
            is_homebrew=False,
            value=25,
        )


class AlchemistsFire(Item):
    def __init__(self):
        super().__init__(
            "Alchemist's Fire",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.CONSUMABLE,
            weight=1,
            slots=1,
            description_text="When you take the Attack action, you can replace one of your attacks with throwing a flask of Alchemist's Fire. Target one creature or object you can see within 20 feet of yourself. The target must succeed on a Dexterity saving throw (DC 8 plus your Dexterity modifier and Proficiency Bonus) or take 1d4 Fire damage and start burning.",
            is_homebrew=False,
            value=50,
        )


class BasicPoison(Item):
    def __init__(self):
        super().__init__(
            "Basic Poison",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.CONSUMABLE,
            weight=None,
            slots=1,
            description_text="As a Bonus Action, you can use a vial of Basic Poison to coat one weapon or up to three pieces of ammunition. A creature that takes Piercing or Slashing damage from the poisoned weapon or ammunition takes an extra 1d4 Poison damage. Once applied, the poison retains potency for 1 minute or until its damage is dealt, whichever comes first.",
            is_homebrew=False,
            value=100,
        )


class HolyWater(Item):
    def __init__(self):
        super().__init__(
            "Holy Water",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.CONSUMABLE,
            weight=1,
            slots=1,
            description_text="When you take the Attack action, you can replace one of your attacks with throwing a flask of Holy Water. Target one creature you can see within 20 feet of yourself. The target must succeed on a Dexterity saving throw (DC 8 plus your Dexterity modifier and Proficiency Bonus) or take 2d8 Radiant damage if it is a Fiend or an Undead.",
            is_homebrew=False,
            value=25,
        )


class SpellScroll(Item):
    def __init__(self):
        super().__init__(
            "Spell Scroll",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.CONSUMABLE,
            weight=None,
            slots=1,
            description_text="A Spell Scroll is a magic item that bears the words of a cantrip or a level 1 spell, determined by the scroll's creator. If the spell is on your class's spell list, you can read the scroll and cast the spell using its normal casting time and without providing any Material components. If the spell requires a saving throw or an attack roll, the spell save DC is 13, and the attack bonus is +5. The scroll disintegrates when the casting is completed.",
            is_homebrew=False,
        )
