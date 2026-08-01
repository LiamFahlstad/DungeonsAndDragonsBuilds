from .Base import Item, ItemCategory, ItemRarity


class ThievesTools(Item):
    def __init__(self):
        super().__init__(
            "Thieves' Tools",
            rarity=ItemRarity.UNCOMMON,
            category=ItemCategory.COMMON,
            slots=1,
            description_text="Utilize: Pick a lock, or disarm a trap (DEX DC 15)",
            is_homebrew=False,
        )


class Crowbar(Item):
    def __init__(self):
        super().__init__(
            "Crowbar",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.TOOL,
            slots=1,
            description_text="Using a crowbar grants advantage on Strength checks where leverage can be applied.",
            is_homebrew=False,
            value=2,
        )


class BlockAndTackle(Item):
    def __init__(self):
        super().__init__(
            "Block and Tackle",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.TOOL,
            weight=5,
            slots=1,
            description_text="A Block and Tackle allows you to hoist up to four times the weight you can normally lift.",
            is_homebrew=False,
            value=1,
        )


class ClimbersKit(Item):
    def __init__(self):
        super().__init__(
            "Climber's Kit",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.TOOL,
            weight=12,
            slots=1,
            description_text="A Climber's Kit includes boot tips, gloves, pitons, and a harness. As a Utilize action, you can use the Climber's Kit to anchor yourself; when you do, you can't fall more than 25 feet from the anchor point, and you can't move more than 25 feet from there without undoing the anchor as a Bonus Action.",
            is_homebrew=False,
            value=25,
        )


class GrapplingHook(Item):
    def __init__(self):
        super().__init__(
            "Grappling Hook",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.TOOL,
            weight=4,
            slots=1,
            description_text="As a Utilize action, you can throw the Grappling Hook at a railing, a ledge, or another catch within 50 feet of yourself, and the hook catches on if you succeed on a DC 13 Dexterity (Acrobatics) check. If you tied a Rope to the hook, you can then climb it.",
            is_homebrew=False,
            value=5,
        )


class HuntingTrap(Item):
    def __init__(self):
        super().__init__(
            "Hunting Trap",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.GEAR,
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
            category=ItemCategory.GEAR,
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
            category=ItemCategory.GEAR,
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
            category=ItemCategory.GEAR,
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
            category=ItemCategory.GEAR,
            weight=7,
            slots=1,
            description_text="A Pole is 10 feet long. You can use it to touch something up to 10 feet away. If you must make a Strength (Athletics) check as part of a High or Long Jump, you can use the Pole to vault, giving yourself Advantage on the check.",
            is_homebrew=False,
            value=0.05,
        )


class PortableRam(Item):
    def __init__(self):
        super().__init__(
            "Portable Ram",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.TOOL,
            weight=35,
            slots=1,
            description_text="You can use a Portable Ram to break down doors. When doing so, you gain a +4 bonus to the Strength check. One other character can help you use the ram, giving you Advantage on this check.",
            is_homebrew=False,
            value=4,
        )


class Shovel(Item):
    def __init__(self):
        super().__init__(
            "Shovel",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.TOOL,
            weight=5,
            slots=1,
            description_text="Working for 1 hour, you can use a Shovel to dig a hole that is 5 feet on each side in soil or similar material.",
            is_homebrew=False,
            value=2,
        )
