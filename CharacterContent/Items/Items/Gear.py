from .Base import Item, ItemCategory, ItemRarity


class Caltrops(Item):
    def __init__(self):
        super().__init__(
            "Caltrops",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.UTILITY,
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
            category=ItemCategory.UTILITY,
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
            category=ItemCategory.UTILITY,
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
            category=ItemCategory.UTILITY,
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


class Tinderbox(Item):
    def __init__(self):
        super().__init__(
            "Tinderbox",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.TOOL,
            slots=0,
            description_text=(
                "A small container with flint, fire steel, and tinder used to start fires. "
                "Lighting a torch, lamp, lantern, or similar exposed fuel takes a bonus action. "
                "Lighting other fires takes 1 minute."
            ),
            is_homebrew=False,
            value=0.5,
        )


class BullseyeLantern(Item):
    def __init__(self):
        super().__init__(
            "Bullseye Lantern",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.UTILITY,
            slots=1,
            description_text=(
                "Consumes oil as fuel to cast bright light in a 60-foot cone and dim light "
                "for an additional 60 feet. The lantern can be shuttered to block the light."
            ),
            is_homebrew=False,
            value=10,
        )


class Mirror(Item):
    def __init__(self):
        super().__init__(
            "Steel Mirror",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.TOOL,
            slots=0,
            description_text=(
                "A small handheld mirror useful for personal grooming. It can also be used "
                "to peek around corners without exposing yourself or to reflect light as a signal."
            ),
            is_homebrew=False,
            value=5,
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
            category=ItemCategory.UTILITY,
            slots=0,
            description_text="When rung as an action, the bell produces a clear sound audible up to 60 feet away.",
            is_homebrew=False,
            value=1,
        )


class Waterskin(Item):
    def __init__(self):
        super().__init__(
            "Waterskin",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.CONTAINER,
            slots=1,
            description_text="Holds up to 4 pints of liquid. Essential for survival, as insufficient water can lead to dehydration.",
            is_homebrew=False,
            value=0.2,
        )


class Blanket(Item):
    def __init__(self):
        super().__init__(
            "Blanket",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.GEAR,
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
            category=ItemCategory.GEAR,
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
            category=ItemCategory.GEAR,
            weight=10,
            slots=1,
            description_text="As a Utilize action, you can wrap a Chain around an unwilling creature within 5 feet of yourself that has the Grappled, Incapacitated, or Restrained condition if you succeed on a DC 13 Strength (Athletics) check. If the creature's legs are bound, the creature has the Restrained condition until it escapes. Escaping the Chain requires the creature to make a successful DC 18 Dexterity (Acrobatics) check as an action. Bursting the Chain requires a successful DC 20 Strength (Athletics) check as an action.",
            is_homebrew=False,
            value=5,
        )


class Flask(Item):
    def __init__(self):
        super().__init__(
            "Flask",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.GEAR,
            weight=1,
            slots=1,
            description_text="A Flask holds up to 1 pint.",
            is_homebrew=False,
            value=0.02,
        )


class GlassBottle(Item):
    def __init__(self):
        super().__init__(
            "Glass Bottle",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.CONTAINER,
            weight=2,
            slots=1,
            description_text="A Glass Bottle holds up to 1½ pints.",
            is_homebrew=False,
            value=2,
        )


class HideArmor(Item):
    def __init__(self):
        super().__init__(
            "Hide Armor",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.PLACEHOLDER,
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
            is_homebrew=False,
        )


class Ink(Item):
    def __init__(self):
        super().__init__(
            "Ink",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.GEAR,
            weight=None,
            slots=1,
            description_text="Ink comes in a 1-ounce bottle, which provides enough ink to write about 500 pages.",
            is_homebrew=False,
            value=10,
        )


class InkPen(Item):
    def __init__(self):
        super().__init__(
            "Ink Pen",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.GEAR,
            weight=None,
            slots=1,
            description_text="Using Ink, an Ink Pen is used to write or draw.",
            is_homebrew=False,
            value=0.02,
        )


class IronSpikes(Item):
    def __init__(self):
        super().__init__(
            "Iron Spikes",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.GEAR,
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
            category=ItemCategory.GEAR,
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
            category=ItemCategory.GEAR,
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
            category=ItemCategory.GEAR,
            weight=None,
            slots=1,
            description_text="If you consult an accurate Map, you gain a +5 bonus to Wisdom (Survival) checks you make to find your way in the place represented on it.",
            is_homebrew=False,
            value=1,
        )


class Needles(Item):
    def __init__(self):
        super().__init__(
            "Needles",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.PLACEHOLDER,
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
            is_homebrew=False,
        )


class Net(Item):
    def __init__(self):
        super().__init__(
            "Net",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.GEAR,
            weight=3,
            slots=1,
            description_text="When you take the Attack action, you can replace one of your attacks with throwing a Net. Target a creature you can see within 15 feet of yourself. The target must succeed on a Dexterity saving throw (DC 8 plus your Dexterity modifier and Proficiency Bonus) or have the Restrained condition until it escapes. To escape, the target or a creature within 5 feet of it must take an action to make a DC 10 Strength (Athletics) check, freeing the Restrained creature on a success.",
            is_homebrew=False,
            value=1,
        )


class Oil(Item):
    def __init__(self):
        super().__init__(
            "Oil",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.GEAR,
            weight=1,
            slots=1,
            description_text="You can douse a creature, object, or space with Oil or use it as fuel. When you take the Attack action, you can replace one of your attacks with throwing an Oil flask; the target must succeed on a Dexterity saving throw (DC 8 plus your Dexterity modifier and Proficiency Bonus) or be covered in oil, taking an extra 5 Fire damage from burning oil if it takes Fire damage before the oil dries. Oil also serves as fuel for Lamps and Lanterns, burning for 6 hours once lit.",
            is_homebrew=False,
            value=0.1,
        )


class PaddedArmor(Item):
    def __init__(self):
        super().__init__(
            "Padded Armor",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.PLACEHOLDER,
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
            is_homebrew=False,
        )


class Paper(Item):
    def __init__(self):
        super().__init__(
            "Paper",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.GEAR,
            weight=None,
            slots=1,
            description_text="One sheet of Paper can hold about 250 handwritten words.",
            is_homebrew=False,
            value=0.2,
        )


class Parchment(Item):
    def __init__(self):
        super().__init__(
            "Parchment",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.GEAR,
            weight=None,
            slots=1,
            description_text="One sheet of Parchment can hold about 250 handwritten words.",
            is_homebrew=False,
            value=0.1,
        )


class Perfume(Item):
    def __init__(self):
        super().__init__(
            "Perfume",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.GEAR,
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
            category=ItemCategory.GEAR,
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
            category=ItemCategory.GEAR,
            weight=1,
            slots=1,
            description_text="Objects viewed through a Spyglass are magnified to twice their size.",
            is_homebrew=False,
            value=1000,
        )


class String(Item):
    def __init__(self):
        super().__init__(
            "String",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.GEAR,
            weight=None,
            slots=1,
            description_text="String is 10 feet long. You can tie a knot in it as a Utilize action.",
            is_homebrew=False,
            value=0.1,
        )


class Tent(Item):
    def __init__(self):
        super().__init__(
            "Tent",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.GEAR,
            weight=20,
            slots=1,
            description_text="A Tent sleeps up to two Small or Medium creatures.",
            is_homebrew=False,
            value=2,
        )


class Vial(Item):
    def __init__(self):
        super().__init__(
            "Vial",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.CONTAINER,
            weight=None,
            slots=1,
            description_text="A Vial holds up to 4 ounces.",
            is_homebrew=False,
            value=1,
        )
