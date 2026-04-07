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
