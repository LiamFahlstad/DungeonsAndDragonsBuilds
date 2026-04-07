from abc import ABC, abstractmethod
from typing import Optional


class Item(ABC):
    def __init__(
        self,
        name: str,
        rarity: str = "common",
        requires_attunement: bool = False,
        category: str = "wondrous",
        weight: Optional[float] = None,
    ):
        self.name = name
        self.rarity = rarity
        self.requires_attunement = requires_attunement
        self.category = category
        self.weight = weight

    @abstractmethod
    def description(self) -> str:
        pass


class Gold(Item):
    def __init__(self):
        super().__init__(f"Gold Pieces", "common", False, "currency", None)

    def description(self) -> str:
        return f"(value=1GP) A stack of gold pieces."


class Silver(Item):
    def __init__(self):
        super().__init__(f"Silver Pieces", "common", False, "currency", None)

    def description(self) -> str:
        return f"(value=0.1GP) A stack of silver pieces."


class Quiver(Item):
    def __init__(self):
        super().__init__(f"Quiver", "uncommon", False, "common", None)

    def description(self) -> str:
        return "A regular quiver"


class ThievesTools(Item):
    def __init__(self):
        super().__init__(f"Thieves' Tools", "uncommon", False, "common", None)

    def description(self) -> str:
        return "Utilize: Pick a lock, or disarm a trap (DEX DC 15)"


class Backpack(Item):
    def __init__(self):
        super().__init__("Backpack", "common", False, "container", None)

    def description(self) -> str:
        return (
            "A backpack that can hold up to 30 pounds of gear within 1 cubic foot. "
            "It can also be strapped to a mount as a saddlebag."
        )


class Caltrops(Item):
    def __init__(self):
        super().__init__("Caltrops", "common", False, "utility", None)

    def description(self) -> str:
        return (
            "As an action, you can spread caltrops to cover a 5-foot-square area within 5 feet. "
            "A creature entering the area must succeed on a DC 15 Dexterity saving throw or take "
            "1 piercing damage and have its speed reduced to 0 until the start of its next turn. "
            "Recovering the caltrops takes 10 minutes."
        )


class Crowbar(Item):
    def __init__(self):
        super().__init__("Crowbar", "common", False, "tool", None)

    def description(self) -> str:
        return "Using a crowbar grants advantage on Strength checks where leverage can be applied."


class Candle(Item):
    def __init__(self):
        super().__init__("Candle", "common", False, "utility", None)

    def description(self) -> str:
        return "For 1 hour, a lit Candle sheds Bright Light in a 5-foot radius and Dim Light for an additional 5 feet."


class BallBearings(Item):
    def __init__(self):
        super().__init__("Ball Bearings", "common", False, "utility", None)

    def description(self) -> str:
        return "As a Utilize action, you can spill Ball Bearings from their pouch. They spread to cover a level, 10-foot-square area within 10 feet of yourself. A creature that enters this area for the first time on a turn must succeed on a DC 10 Dexterity saving throw or have the Prone condition. It takes 10 minutes to recover the Ball Bearings."


class HoodedLantern(Item):
    def __init__(self):
        super().__init__("Hooded Lantern", "common", False, "utility", None)

    def description(self) -> str:
        return "A Hooded Lantern burns Oil as fuel to cast Bright Light in a 30-foot radius and Dim Light for an additional 30 feet. As a Bonus Action, you can lower the hood, reducing the light to Dim Light in a 5-foot radius, or raise it again."


class FlasksOfOil(Item):
    def __init__(self):
        super().__init__("Flask of Oil", "common", False, "utility", None)

    def description(self) -> str:
        return (
            "You can throw this flask (range 20 ft) to coat a creature or object. "
            "On a failed Dexterity save (DC = 8 + Dex mod + proficiency bonus), the target is covered in oil. "
            "If it takes fire damage within 1 minute, it takes an extra 5 fire damage.\n\n"
            "Alternatively, you can pour it on the ground (5-foot-square). If ignited, it burns for 2 rounds, "
            "dealing 5 fire damage to creatures entering or ending their turn in the area (once per turn).\n\n"
            "Oil can also be used as fuel, burning for up to 6 hours in a lamp or lantern."
        )


class Rations(Item):
    def __init__(self):
        super().__init__("Rations", "common", False, "consumable", None)

    def description(self) -> str:
        return (
            "Travel-ready food such as jerky, dried fruit, hardtack, and nuts. "
            "Essential for long journeys; lack of food can lead to malnutrition."
        )


class Antitoxin(Item):
    def __init__(self):
        super().__init__("Antitoxin", "common", False, "consumable", None)

    def description(self) -> str:
        return "As a Bonus Action, you can drink a vial of Antitoxin to gain Advantage on saving throws to avoid or end the Poisoned condition for 1 hour."


class HealersKit(Item):
    def __init__(self):
        super().__init__("Healer's Kit", "common", False, "consumable", None)

    def description(self) -> str:
        return "A Healer's Kit has ten uses. As a Utilize action, you can expend one of its uses to stabilize an Unconscious creature that has 0 Hit Points without needing to make a Wisdom (Medicine) check."


class PotionOfHealing(Item):
    def __init__(self):
        super().__init__("Potion of Healing", "common", False, "consumable", None)

    def description(self) -> str:
        return (
            "You regain 2d4 + 2 Hit Points when you drink this potion.\n"
            "Whatever its potency, the potion's red liquid glimmers when agitated."
        )


class Rope(Item):
    def __init__(self):
        super().__init__("Rope (50 ft)", "common", False, "utility", None)

    def description(self) -> str:
        return (
            "As an action, you can tie a knot with a successful DC 10 Dexterity (Sleight of Hand) check. "
            "The rope can be burst with a DC 20 Strength (Athletics) check.\n\n"
            "You can bind a creature only if it is grappled, incapacitated, or restrained. "
            "If its legs are bound, it becomes restrained. Escaping requires a DC 15 Dexterity "
            "(Acrobatics) check as an action."
        )


class Tinderbox(Item):
    def __init__(self):
        super().__init__("Tinderbox", "common", False, "tool", None)

    def description(self) -> str:
        return (
            "A small container with flint, fire steel, and tinder used to start fires. "
            "Lighting a torch, lamp, lantern, or similar exposed fuel takes a bonus action. "
            "Lighting other fires takes 1 minute."
        )


class Torch(Item):
    def __init__(self):
        super().__init__("Torch", "common", False, "utility", None)

    def description(self) -> str:
        return (
            "Burns for 1 hour, providing bright light in a 20-foot radius and dim light for another 20 feet.\n\n"
            "It can be used as a simple melee weapon. On a hit, it deals 1 fire damage."
        )


class BullseyeLantern(Item):
    def __init__(self):
        super().__init__("Bullseye Lantern", "common", False, "utility", None)

    def description(self) -> str:
        return (
            "Consumes oil as fuel to cast bright light in a 60-foot cone and dim light "
            "for an additional 60 feet. The lantern can be shuttered to block the light."
        )


class Costume(Item):
    def __init__(self):
        super().__init__("Costume", "common", False, "adventuring gear", None)

    def description(self) -> str:
        return (
            "While wearing this costume, you have advantage on ability checks made to "
            "impersonate the person or type of person it represents."
        )


class Mirror(Item):
    def __init__(self):
        super().__init__("Steel Mirror", "common", False, "tool", None)

    def description(self) -> str:
        return (
            "A small handheld mirror useful for personal grooming. It can also be used "
            "to peek around corners without exposing yourself or to reflect light as a signal."
        )


class Typewriter(Item):
    def __init__(self):
        super().__init__("Typewriter", "common", False, "musical instrument", None)

    def description(self) -> str:
        return (
            "A mechanical typewriter that can also be used as a musical instrument, "
            "producing rhythmic clacking sounds."
        )


class NightVisionGoggles(Item):
    def __init__(self):
        super().__init__(
            "Nightvision Goggles", "uncommon", False, "wondrous item", None
        )

    def description(self) -> str:
        return "While wearing these goggles, you gain darkvision out to 120 feet."


class ButterflyKnife(Item):
    def __init__(self):
        super().__init__("Butterfly Knife", "common", False, "weapon", None)

    def description(self) -> str:
        return (
            "A small folding knife that can be quickly deployed. "
            "Functions as a light melee weapon."
        )


class Beans(Item):
    def __init__(self):
        super().__init__("Can of Beans", "common", False, "consumable", None)

    def description(self) -> str:
        return "A simple can of preserved beans. Provides a basic meal when consumed."


class Makarov(Item):
    def __init__(self):
        super().__init__("Makarov", "uncommon", False, "weapon", None)

    def description(self) -> str:
        return (
            "In a fantasy realm, this pistol becomes a magical ranged weapon.\n\n"
            "It has 4 charges. Each shot deals 2d6 + your Dexterity modifier damage. "
            "The weapon regains all charges after a long rest."
        )


class Bedroll(Item):
    def __init__(self):
        super().__init__("Bedroll", "common", False, "adventuring gear", None)

    def description(self) -> str:
        return (
            "A bedroll provides basic sleeping comfort for one Small or Medium creature.\n\n"
            "While resting in a bedroll, you automatically succeed on saving throws "
            "against extreme cold."
        )


class Bell(Item):
    def __init__(self):
        super().__init__("Bell", "common", False, "utility", None)

    def description(self) -> str:
        return "When rung as an action, the bell produces a clear sound audible up to 60 feet away."


class Waterskin(Item):
    def __init__(self):
        super().__init__("Waterskin", "common", False, "container", None)

    def description(self) -> str:
        return "Holds up to 4 pints of liquid. Essential for survival, as insufficient water can lead to dehydration."


class Arrows(Item):
    def __init__(self):
        super().__init__("Arrows", "common", False, "ammunition", None)

    def description(self) -> str:
        return f"A bundle of arrows."


class HobbyHorse(Item):
    def __init__(self):
        super().__init__("Käpphäst", "uncommon", False, "wondrous item", None)

    def description(self) -> str:
        return (
            "A simple hobby horse that transforms into a real mount when brought into a fantasy realm.\n"
            "While mounted, mounting or dismounting the käpphäst costs half your movement.\n"
            "If you take damage while mounted, you must succeed on a Strength or Dexterity saving throw "
            "(your choice). The DC equals the higher of 10 or half the damage taken rounded down. On a failure, you fall "
            "from the mount and are knocked prone."
        )


class DramaticRainBottle(Item):
    def __init__(self):
        super().__init__("Dramatic Rain in a Bottle", "common", False, "wondrous", None)
        self.duration = 60  # minutes

    def description(self) -> str:
        return (
            f"Uncorking this bottle summons a personal raincloud that follows you "
            f"for {self.duration} minutes, raining gently and dramatically—even indoors. "
            f"The rain causes no harm but is perfect for brooding, monologues, or emotional exits. "
            f"Purely theatrical."
        )


class RobeOfLevitation(Item):
    def __init__(self):
        super().__init__("Robe of Levitation", "common", False, "wondrous", None)

    def description(self) -> str:
        return (
            "While wearing this robe, you hover 1 foot above the ground at all times. "
            "This provides no mechanical benefit—you cannot cross gaps or avoid terrain. "
            "Your robe billows dramatically as if in constant wind. "
            "You leave faint traces beneath you, and your movement produces a soft windy sound "
            "as loud as footsteps. You always look slightly more epic than others."
        )


class HeartseekersCompass(Item):
    def __init__(self):
        super().__init__("Heartseeker’s Compass", "uncommon", True, "wondrous", None)

    def description(self) -> str:
        return (
            "This brass compass does not point north. Instead, it points toward the nearest "
            "creature within 1 mile that it ‘likes,’ based on emotional resonance such as kindness "
            "or affinity. The criteria are mysterious and determined by the DM."
        )


class MinorDeathNote(Item):
    def __init__(self):
        super().__init__("Minor Death Note", "common", False, "wondrous", None)

    def description(self) -> str:
        return (
            "When you write a creature’s name in this notebook, that creature immediately receives "
            "a papercut. The effect can only occur once per creature. Harmless, but very annoying."
        )


class CoinOfTwoFacedJustice(Item):
    def __init__(self):
        super().__init__(
            "Coin of Two-Faced Justice", "uncommon", False, "wondrous", None
        )

    def description(self) -> str:
        return (
            "As a bonus action, call and flip this coin. If you call it correctly, you gain advantage "
            "on your next roll; otherwise, you have disadvantage. This effect does not stack and cannot "
            "apply to the coin flip itself."
        )


class GoldenFrog(Item):
    def __init__(self):
        super().__init__(
            "Golden Frog with a Golden Voice", "rare", False, "wondrous", None
        )

    def description(self) -> str:
        return (
            "This golden frog, once a prince, has a flawless voice and knows every song in the multiverse. "
            "It can perfectly reproduce vocals and instruments. The frog cannot fight, speak normally, "
            "or act outside of music, and may sing randomly unless commanded to remain silent."
        )


class ButtonOfNobleSacrifice(Item):
    def __init__(self):
        super().__init__(
            "Button of Noble Sacrifice", "legendary", False, "wondrous", None
        )

    def description(self) -> str:
        return (
            "When a creature presses this button, they instantly and irrevocably die. In doing so, "
            "a more pure and deserving creature—fated to die—is spared instead. "
            "The user must know the button’s function, but need not believe it. "
            "No one learns who was saved. The user cannot be revived except by Wish or divine intervention."
        )


class DoomScroll(Item):
    def __init__(self):
        super().__init__("Doom Scroll", "common", False, "wondrous", None)

    def description(self) -> str:
        return (
            "This scroll displays an endless feed of fascinating but useless information from across the multiverse. "
            "When you read it, you must succeed on a DC 13 Intelligence saving throw or continue reading until the "
            "start of your next turn. Afterward, you have disadvantage on your next Intelligence roll."
        )


class Kamikaze(Item):
    def __init__(self):
        super().__init__("Kamikaze", "uncommon", False, "wondrous", None)

    def description(self) -> str:
        return (
            "As an action, you activate this item to immediately cast Fireball centered on yourself. "
            "You automatically fail the saving throw."
        )


class FingerGunRing(Item):
    def __init__(self):
        super().__init__("Ring of Finger Guns", "common", False, "ring", None)

    def description(self) -> str:
        return (
            "While wearing this ring, forming finger guns and saying 'pew' creates a tiny harmless spark "
            "and sound effect. The spark can light candles but deals no damage."
        )


class BadFriendGlasses(Item):
    def __init__(self):
        super().__init__("A Bad Friend Glasses", "uncommon", False, "wondrous", None)

    def description(self) -> str:
        return (
            "While wearing these glasses, you may redirect damage you would take to another player character "
            "with the lowest hit points. You are, objectively, a terrible friend."
        )
