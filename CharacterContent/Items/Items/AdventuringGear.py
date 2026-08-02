from .Base import Item, ItemCategory, ItemRarity


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


class Candle(Item):
    def __init__(self):
        super().__init__(
            "Candle",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.ADVENTURING_GEAR,
            slots=0,
            description_text="For 1 hour, a lit Candle sheds Bright Light in a 5-foot radius and Dim Light for an additional 5 feet.",
            is_homebrew=False,
            value=0.01,
            is_consumable=True,
        )


class FlasksOfOil(Item):
    def __init__(self):
        super().__init__(
            "Flask of Oil",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.ADVENTURING_GEAR,
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
            is_consumable=True,
        )


class Rations(Item):
    def __init__(self):
        super().__init__(
            "Rations",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.ADVENTURING_GEAR,
            slots=1,
            description_text=(
                "Travel-ready food such as jerky, dried fruit, hardtack, and nuts. "
                "Essential for long journeys; lack of food can lead to malnutrition."
            ),
            is_homebrew=False,
            value=0.5,
            is_consumable=True,
        )


class Antitoxin(Item):
    def __init__(self):
        super().__init__(
            "Antitoxin",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.ADVENTURING_GEAR,
            slots=0,
            description_text="As a Bonus Action, you can drink a vial of Antitoxin to gain Advantage on saving throws to avoid or end the Poisoned condition for 1 hour.",
            is_homebrew=False,
            value=50,
            is_consumable=True,
        )


class HealersKit(Item):
    def __init__(self):
        super().__init__(
            "Healer's Kit",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.ADVENTURING_GEAR,
            slots=1,
            description_text="A Healer's Kit has ten uses. As a Utilize action, you can expend one of its uses to stabilize an Unconscious creature that has 0 Hit Points without needing to make a Wisdom (Medicine) check.",
            is_homebrew=False,
            value=5,
            is_consumable=True,
        )


class Torch(Item):
    def __init__(self):
        super().__init__(
            "Torch",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.ADVENTURING_GEAR,
            slots=1,
            description_text=(
                "Burns for 1 hour, providing bright light in a 20-foot radius and dim light for another 20 feet.\n\n"
                "It can be used as a simple melee weapon. On a hit, it deals 1 fire damage."
            ),
            is_homebrew=False,
            value=0.01,
            is_consumable=True,
        )


class Beans(Item):
    def __init__(self):
        super().__init__(
            "Can of Beans",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.ADVENTURING_GEAR,
            slots=1,
            description_text="A simple can of preserved beans. Provides a basic meal when consumed.",
            is_consumable=True,
        )


class Acid(Item):
    def __init__(self):
        super().__init__(
            "Acid",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.ADVENTURING_GEAR,
            weight=1,
            slots=1,
            description_text="When you take the Attack action, you can replace one of your attacks with throwing a vial of Acid. Target one creature or object you can see within 20 feet of yourself. The target must succeed on a Dexterity saving throw (DC 8 plus your Dexterity modifier and Proficiency Bonus) or take 2d6 Acid damage.",
            is_homebrew=False,
            value=25,
            is_consumable=True,
        )


class AlchemistsFire(Item):
    def __init__(self):
        super().__init__(
            "Alchemist's Fire",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.ADVENTURING_GEAR,
            weight=1,
            slots=1,
            description_text="When you take the Attack action, you can replace one of your attacks with throwing a flask of Alchemist's Fire. Target one creature or object you can see within 20 feet of yourself. The target must succeed on a Dexterity saving throw (DC 8 plus your Dexterity modifier and Proficiency Bonus) or take 1d4 Fire damage and start burning.",
            is_homebrew=False,
            value=50,
            is_consumable=True,
        )


class HolyWater(Item):
    def __init__(self):
        super().__init__(
            "Holy Water",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.ADVENTURING_GEAR,
            weight=1,
            slots=1,
            description_text="When you take the Attack action, you can replace one of your attacks with throwing a flask of Holy Water. Target one creature you can see within 20 feet of yourself. The target must succeed on a Dexterity saving throw (DC 8 plus your Dexterity modifier and Proficiency Bonus) or take 2d8 Radiant damage if it is a Fiend or an Undead.",
            is_homebrew=False,
            value=25,
            is_consumable=True,
        )


class IronPot(Item):
    def __init__(self):
        super().__init__(
            "Iron Pot",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.ADVENTURING_GEAR,
            weight=10,
            slots=1,
            description_text="An Iron Pot holds up to 1 gallon.",
            is_homebrew=False,
            value=2,
        )


class Caltrops(Item):
    def __init__(self):
        super().__init__(
            "Caltrops",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.ADVENTURING_GEAR,
            slots=1,
            description_text=(
                "As an action, you can spread caltrops to cover a 5-foot-square area within 5 feet. "
                "A creature entering the area must succeed on a DC 15 Dexterity saving throw or take "
                "1 piercing damage and have its speed reduced to 0 until the start of its next turn. "
                "Recovering the caltrops takes 10 minutes."
            ),
            is_homebrew=False,
            value=1,
        )


class BallBearings(Item):
    def __init__(self):
        super().__init__(
            "Ball Bearings",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.ADVENTURING_GEAR,
            slots=1,
            description_text="As a Utilize action, you can spill Ball Bearings from their pouch. They spread to cover a level, 10-foot-square area within 10 feet of yourself. A creature that enters this area for the first time on a turn must succeed on a DC 10 Dexterity saving throw or have the Prone condition. It takes 10 minutes to recover the Ball Bearings.",
            is_homebrew=False,
            value=1,
        )


class HoodedLantern(Item):
    def __init__(self):
        super().__init__(
            "Hooded Lantern",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.ADVENTURING_GEAR,
            slots=1,
            description_text="A Hooded Lantern burns Oil as fuel to cast Bright Light in a 30-foot radius and Dim Light for an additional 30 feet. As a Bonus Action, you can lower the hood, reducing the light to Dim Light in a 5-foot radius, or raise it again.",
            is_homebrew=False,
            value=5,
        )


class Rope(Item):
    def __init__(self):
        super().__init__(
            "Rope (50 ft)",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.ADVENTURING_GEAR,
            description_text=(
                "As an action, you can tie a knot with a successful DC 10 Dexterity (Sleight of Hand) check. "
                "The rope can be burst with a DC 20 Strength (Athletics) check.\n\n"
                "You can bind a creature only if it is grappled, incapacitated, or restrained. "
                "If its legs are bound, it becomes restrained. Escaping requires a DC 15 Dexterity "
                "(Acrobatics) check as an action."
            ),
            is_homebrew=False,
            value=1,
        )


class BullseyeLantern(Item):
    def __init__(self):
        super().__init__(
            "Bullseye Lantern",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.ADVENTURING_GEAR,
            slots=1,
            description_text=(
                "Consumes oil as fuel to cast bright light in a 60-foot cone and dim light "
                "for an additional 60 feet. The lantern can be shuttered to block the light."
            ),
            is_homebrew=False,
            value=10,
        )


class Bedroll(Item):
    def __init__(self):
        super().__init__(
            "Bedroll",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.ADVENTURING_GEAR,
            slots=1,
            description_text=(
                "A bedroll provides basic sleeping comfort for one Small or Medium creature.\n\n"
                "While resting in a bedroll, you automatically succeed on saving throws "
                "against extreme cold."
            ),
            is_homebrew=False,
            value=1,
        )


class Bell(Item):
    def __init__(self):
        super().__init__(
            "Bell",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.ADVENTURING_GEAR,
            slots=0,
            description_text="When rung as an action, the bell produces a clear sound audible up to 60 feet away.",
            is_homebrew=False,
            value=1,
        )


class Blanket(Item):
    def __init__(self):
        super().__init__(
            "Blanket",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.ADVENTURING_GEAR,
            weight=3,
            slots=1,
            description_text="While wrapped in a blanket, you have Advantage on saving throws against extreme cold.",
            is_homebrew=False,
            value=0.5,
        )


class Book(Item):
    def __init__(self):
        super().__init__(
            "Book",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.ADVENTURING_GEAR,
            weight=5,
            slots=1,
            description_text="A Book contains fiction or nonfiction. If you consult an accurate nonfiction Book about its topic, you gain a +5 bonus to Intelligence (Arcana, History, Nature, or Religion) checks you make about that topic.",
            is_homebrew=False,
            value=25,
        )


class Chain(Item):
    def __init__(self):
        super().__init__(
            "Chain",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.ADVENTURING_GEAR,
            weight=10,
            slots=1,
            description_text="As a Utilize action, you can wrap a Chain around an unwilling creature within 5 feet of yourself that has the Grappled, Incapacitated, or Restrained condition if you succeed on a DC 13 Strength (Athletics) check. If the creature's legs are bound, the creature has the Restrained condition until it escapes. Escaping the Chain requires the creature to make a successful DC 18 Dexterity (Acrobatics) check as an action. Bursting the Chain requires a successful DC 20 Strength (Athletics) check as an action.",
            is_homebrew=False,
            value=5,
        )


class IronSpikes(Item):
    def __init__(self):
        super().__init__(
            "Iron Spikes",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.ADVENTURING_GEAR,
            weight=5,
            slots=1,
            description_text="Iron Spikes come in bundles of ten. As a Utilize action, you can use a blunt object, such as a Light Hammer, to hammer a spike into wood, earth, or a similar material. You can do so to jam a door shut or to then tie a Rope or Chain to the Spike.",
            is_homebrew=False,
            value=1,
        )


class Lamp(Item):
    def __init__(self):
        super().__init__(
            "Lamp",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.ADVENTURING_GEAR,
            weight=1,
            slots=1,
            description_text="A Lamp burns Oil as fuel to cast Bright Light in a 15-foot radius and Dim Light for an additional 30 feet.",
            is_homebrew=False,
            value=0.5,
        )


class MagnifyingGlass(Item):
    def __init__(self):
        super().__init__(
            "Magnifying Glass",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.ADVENTURING_GEAR,
            weight=None,
            slots=1,
            description_text="A Magnifying Glass grants Advantage on any ability check made to appraise or inspect a highly detailed item. Lighting a fire with a Magnifying Glass requires light as bright as sunlight to focus, tinder to ignite, and about 5 minutes for the fire to ignite.",
            is_homebrew=False,
            value=100,
        )


class Map(Item):
    def __init__(self):
        super().__init__(
            "Map",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.ADVENTURING_GEAR,
            weight=None,
            slots=1,
            description_text="If you consult an accurate Map, you gain a +5 bonus to Wisdom (Survival) checks you make to find your way in the place represented on it.",
            is_homebrew=False,
            value=1,
        )


class Oil(Item):
    def __init__(self):
        super().__init__(
            "Oil",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.ADVENTURING_GEAR,
            weight=1,
            slots=1,
            description_text="You can douse a creature, object, or space with Oil or use it as fuel. When you take the Attack action, you can replace one of your attacks with throwing an Oil flask; the target must succeed on a Dexterity saving throw (DC 8 plus your Dexterity modifier and Proficiency Bonus) or be covered in oil, taking an extra 5 Fire damage from burning oil if it takes Fire damage before the oil dries. Oil also serves as fuel for Lamps and Lanterns, burning for 6 hours once lit.",
            is_homebrew=False,
            value=0.1,
        )


class Perfume(Item):
    def __init__(self):
        super().__init__(
            "Perfume",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.ADVENTURING_GEAR,
            weight=None,
            slots=1,
            description_text="Perfume comes in a 4-ounce vial. For 1 hour after applying Perfume to yourself, you have Advantage on Charisma (Persuasion) checks made to influence an Indifferent Humanoid within 5 feet of yourself.",
            is_homebrew=False,
            value=5,
        )


class SignalWhistle(Item):
    def __init__(self):
        super().__init__(
            "Signal Whistle",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.ADVENTURING_GEAR,
            weight=None,
            slots=1,
            description_text="When blown as a Utilize action, a Signal Whistle produces a sound that can be heard up to 600 feet away.",
            is_homebrew=False,
            value=0.05,
        )


class Spyglass(Item):
    def __init__(self):
        super().__init__(
            "Spyglass",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.ADVENTURING_GEAR,
            weight=1,
            slots=1,
            description_text="Objects viewed through a Spyglass are magnified to twice their size.",
            is_homebrew=False,
            value=1000,
        )


class Tent(Item):
    def __init__(self):
        super().__init__(
            "Tent",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.ADVENTURING_GEAR,
            weight=20,
            slots=1,
            description_text="A Tent sleeps up to two Small or Medium creatures.",
            is_homebrew=False,
            value=2,
        )


class HuntingTrap(Item):
    def __init__(self):
        super().__init__(
            "Hunting Trap",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.ADVENTURING_GEAR,
            weight=25,
            slots=1,
            description_text="As a Utilize action, you can set a Hunting Trap, which is a sawtooth steel ring that snaps shut when a creature steps on a pressure plate in the center. A creature that steps on the plate must succeed on a DC 13 Dexterity saving throw or take 1d4 Piercing damage and have its Speed reduced to 0 until the start of its next turn. A creature can use its action to make a DC 13 Strength (Athletics) check, freeing itself or another creature within its reach on a success.",
            is_homebrew=False,
            value=5,
        )


class Ladder(Item):
    def __init__(self):
        super().__init__(
            "Ladder",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.ADVENTURING_GEAR,
            weight=25,
            slots=1,
            description_text="A Ladder is 10 feet tall. You must climb to move up or down it.",
            is_homebrew=False,
            value=0.1,
        )


class Lock(Item):
    def __init__(self):
        super().__init__(
            "Lock",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.ADVENTURING_GEAR,
            weight=1,
            slots=1,
            description_text="A Lock comes with a key. Without the key, a creature can use Thieves' Tools to pick this Lock with a successful DC 15 Dexterity (Sleight of Hand) check.",
            is_homebrew=False,
            value=10,
        )


class Manacles(Item):
    def __init__(self):
        super().__init__(
            "Manacles",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.ADVENTURING_GEAR,
            weight=6,
            slots=1,
            description_text="As a Utilize action, you can use Manacles to bind an unwilling Small or Medium creature within 5 feet of yourself that has the Grappled, Incapacitated, or Restrained condition if you succeed on a DC 13 Dexterity (Sleight of Hand) check. While bound, a creature has Disadvantage on attack rolls, and the creature is Restrained if the Manacles are attached to a chain or hook that is fixed in place. Escaping the Manacles requires a successful DC 20 Dexterity (Sleight of Hand) check as an action. Bursting them requires a successful DC 25 Strength (Athletics) check as an action. Each set of Manacles comes with a key.",
            is_homebrew=False,
            value=2,
        )


class Pole(Item):
    def __init__(self):
        super().__init__(
            "Pole",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.ADVENTURING_GEAR,
            weight=7,
            slots=1,
            description_text="A Pole is 10 feet long. You can use it to touch something up to 10 feet away. If you must make a Strength (Athletics) check as part of a High or Long Jump, you can use the Pole to vault, giving yourself Advantage on the check.",
            is_homebrew=False,
            value=0.05,
        )


class LockingSpellbook(Item):
    def __init__(self):
        super().__init__(
            "Locking Spellbook",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.ADVENTURING_GEAR,
            weight=None,
            slots=1,
            description_text="This 100-page leather-bound tome can be used as a Spellbook. It is closed with a lock that comes with a key. As a Utilize action, a creature can try to pick the lock using Thieves' Tools, doing so with a successful DC 15 Dexterity (Sleight of Hand) check.",
            is_homebrew=False,
            value=35,
        )
