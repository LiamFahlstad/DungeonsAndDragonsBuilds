from .Base import Item, ItemCategory, ItemRarity


class ThievesTools(Item):
    def __init__(self):
        super().__init__(
            "Thieves' Tools",
            rarity=ItemRarity.UNCOMMON,
            category=ItemCategory.TOOL,
            weight=1.0,
            slots=1,
            value=25,
            description_text="Ability: Dexterity. Utilize: Pick a lock (DC 15), or disarm a trap (DC 15).",
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
            slots=2,
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


class PortableRam(Item):
    def __init__(self):
        super().__init__(
            "Portable Ram",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.TOOL,
            weight=35,
            slots=3,
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


class Tinderbox(Item):
    def __init__(self):
        super().__init__(
            "Tinderbox",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.TOOL,
            slots=1,
            description_text=(
                "A small container with flint, fire steel, and tinder used to start fires. "
                "Lighting a torch, lamp, lantern, or similar exposed fuel takes a bonus action. "
                "Lighting other fires takes 1 minute."
            ),
            is_homebrew=False,
            value=0.5,
        )


class Mirror(Item):
    def __init__(self):
        super().__init__(
            "Steel Mirror",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.TOOL,
            slots=1,
            description_text=(
                "A small handheld mirror useful for personal grooming. It can also be used "
                "to peek around corners without exposing yourself or to reflect light as a signal."
            ),
            is_homebrew=False,
            value=5,
        )


class NavigatorsTools(Item):
    def __init__(self):
        super().__init__(
            "Navigator's Tools", rarity=ItemRarity.COMMON, category=ItemCategory.TOOL,
            weight=2.0, slots=1, value=25, is_homebrew=False,
            description_text="Ability: Wisdom. Utilize: Plot a course (DC 10), or determine position by stargazing (DC 15).",
        )


class PoisonersKit(Item):
    def __init__(self):
        super().__init__(
            "Poisoner's Kit", rarity=ItemRarity.UNCOMMON, category=ItemCategory.TOOL,
            weight=2.0, slots=1, value=50, is_homebrew=False,
            description_text="Ability: Intelligence. Utilize: Detect a poisoned object (DC 10).",
        )


class HerbalismKit(Item):
    def __init__(self):
        super().__init__(
            "Herbalism Kit", rarity=ItemRarity.COMMON, category=ItemCategory.TOOL,
            weight=3.0, slots=1, value=5, is_homebrew=False,
            description_text="Ability: Intelligence. Utilize: Identify a plant (DC 10).",
        )


class DisguiseKit(Item):
    def __init__(self):
        super().__init__(
            "Disguise Kit", rarity=ItemRarity.COMMON, category=ItemCategory.TOOL,
            weight=3.0, slots=1, value=25, is_homebrew=False,
            description_text="Ability: Charisma. Utilize: Apply makeup (DC 10).",
        )


class ForgeryKit(Item):
    def __init__(self):
        super().__init__(
            "Forgery Kit", rarity=ItemRarity.COMMON, category=ItemCategory.TOOL,
            weight=5.0, slots=1, value=15, is_homebrew=False,
            description_text="Ability: Dexterity. Utilize: Mimic 10 or fewer words of someone else's handwriting (DC 15), or duplicate a wax seal (DC 20).",
        )
