from Core.Definitions import Ability
from CharacterContent.Features.Core.Improvements import AbilityScoreBonus, ArmorClassBonus
from .Base import Item, ItemCategory, ItemRarity


class NightVisionGoggles(Item):
    def __init__(self, is_wearing: bool = True):
        super().__init__(
            "Nightvision Goggles",
            rarity=ItemRarity.UNCOMMON,
            category=ItemCategory.WONDROUS,
            slots=1,
            description_text="While wearing these goggles, you gain darkvision out to 120 feet.",
            is_wearing=is_wearing,
        )


class HobbyHorse(Item):
    def __init__(self):
        super().__init__(
            "Käpphäst",
            rarity=ItemRarity.UNCOMMON,
            category=ItemCategory.WONDROUS,
            slots=2,
            description_text=(
                "A simple hobby horse that transforms into a real mount when brought into a fantasy realm.\n"
                "While mounted, mounting or dismounting the käpphäst costs half your movement.\n"
                "If you take damage while mounted, you must succeed on a Strength or Dexterity saving throw "
                "(your choice). The DC equals the higher of 10 or half the damage taken rounded down. On a failure, you fall "
                "from the mount and are knocked prone."
            ),
        )


class DramaticRainBottle(Item):
    def __init__(self):
        super().__init__(
            "Dramatic Rain in a Bottle",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.WONDROUS,
            slots=2,
            description_text=(
                f"Uncorking this bottle summons a personal raincloud that follows you "
                f"for 60 minutes, raining gently and dramatically—even indoors. "
                f"The rain causes no harm but is perfect for brooding, monologues, or emotional exits. "
                f"Purely theatrical."
            ),
        )


class RobeOfLevitation(Item):
    def __init__(self, is_wearing: bool = True):
        super().__init__(
            "Robe of Levitation",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.WONDROUS,
            slots=2,
            description_text=(
                "While wearing this robe, you hover 1 foot above the ground at all times. "
                "This provides no mechanical benefit—you cannot cross gaps or avoid terrain. "
                "Your robe billows dramatically as if in constant wind. "
                "You leave faint traces beneath you, and your movement produces a soft windy sound "
                "as loud as footsteps. You always look slightly more epic than others."
            ),
            is_wearing=is_wearing,
        )


class HeartseekersCompass(Item):
    def __init__(self):
        super().__init__(
            "Heartseeker's Compass",
            rarity=ItemRarity.UNCOMMON,
            requires_attunement=True,
            category=ItemCategory.WONDROUS,
            slots=1,
            description_text=(
                "This brass compass does not point north. Instead, it points toward the nearest "
                "creature within 1 mile that it 'likes,' based on emotional resonance such as kindness "
                "or affinity. The criteria are mysterious and determined by the DM."
            ),
        )


class MinorDeathNote(Item):
    def __init__(self):
        super().__init__(
            "Minor Death Note",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.WONDROUS,
            slots=0,
            description_text=(
                "When you write a creature's name in this notebook, that creature immediately receives "
                "a papercut. The effect can only occur once per creature. Harmless, but very annoying."
            ),
        )


class CoinOfTwoFacedJustice(Item):
    def __init__(self):
        super().__init__(
            "Coin of Two-Faced Justice",
            rarity=ItemRarity.UNCOMMON,
            category=ItemCategory.WONDROUS,
            slots=0,
            description_text=(
                "As a bonus action, call and flip this coin. If you call it correctly, you gain advantage "
                "on your next roll; otherwise, you have disadvantage. This effect does not stack and cannot "
                "apply to the coin flip itself."
            ),
        )


class GoldenFrog(Item):
    def __init__(self):
        super().__init__(
            "Golden Frog with a Golden Voice",
            rarity=ItemRarity.RARE,
            category=ItemCategory.WONDROUS,
            slots=2,
            description_text=(
                "This golden frog, once a prince, has a flawless voice and knows every song in the multiverse. "
                "It can perfectly reproduce vocals and instruments. The frog cannot fight, speak normally, "
                "or act outside of music, and may sing randomly unless commanded to remain silent."
            ),
        )


class ButtonOfNobleSacrifice(Item):
    def __init__(self):
        super().__init__(
            "Button of Noble Sacrifice",
            rarity=ItemRarity.LEGENDARY,
            category=ItemCategory.WONDROUS,
            slots=2,
            description_text=(
                "When a creature presses this button, they instantly and irrevocably die. In doing so, "
                "a more pure and deserving creature—fated to die—is spared instead. "
                "The user must know the button's function, but need not believe it. "
                "No one learns who was saved. The user cannot be revived except by Wish or divine intervention."
            ),
        )


class DoomScroll(Item):
    def __init__(self):
        super().__init__(
            "Doom Scroll",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.WONDROUS,
            slots=1,
            description_text=(
                "This scroll displays an endless feed of fascinating but useless information from across the multiverse. "
                "When you read it, you must succeed on a DC 13 Intelligence saving throw or continue reading until the "
                "start of your next turn. Afterward, you have disadvantage on your next Intelligence roll."
            ),
        )


class Kamikaze(Item):
    def __init__(self):
        super().__init__(
            "Kamikaze",
            rarity=ItemRarity.UNCOMMON,
            category=ItemCategory.WONDROUS,
            slots=1,
            description_text=(
                "As an action, you activate this item to immediately cast Fireball centered on yourself. "
                "You automatically fail the saving throw."
            ),
        )


class BadFriendGlasses(Item):
    def __init__(self, is_wearing: bool = True):
        super().__init__(
            "A Bad Friend Glasses",
            rarity=ItemRarity.UNCOMMON,
            category=ItemCategory.WONDROUS,
            slots=1,
            description_text=(
                "While wearing these glasses, you may redirect damage you would take to another player character "
                "with the lowest hit points. You are, objectively, a terrible friend."
            ),
            is_wearing=is_wearing,
        )


# ══════════════════════════════════════════════════════════════════════════════
# Mechanical Items (with CharacterImprovements)
# ══════════════════════════════════════════════════════════════════════════════


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


# ══════════════════════════════════════════════════════════════════════════════
# Mechanical Items (with CharacterImprovements)
# ══════════════════════════════════════════════════════════════════════════════


class CloakOfProtection(Item):
    """A magical cloak that grants +1 AC."""

    def __init__(self, is_wearing: bool = True):
        super().__init__(
            "Cloak of Protection",
            rarity=ItemRarity.UNCOMMON,
            requires_attunement=True,
            category=ItemCategory.WONDROUS,
            description_text=(
                "You gain a +1 bonus to AC while wearing this cloak.\n\n"
                "This silken cloak shimmers with protective magic and feels warm to the touch."
            ),
            is_wearing=is_wearing,
            improvements=[ArmorClassBonus(1)],
            is_homebrew=False,
        )


class BracersOfArchery(Item):
    """Magical bracers that grant +2 Dexterity for ranged combat."""

    def __init__(self, is_wearing: bool = True):
        super().__init__(
            "Bracers of Archery",
            rarity=ItemRarity.UNCOMMON,
            requires_attunement=True,
            category=ItemCategory.WONDROUS,
            description_text=(
                "While wearing these bracers, you gain a +2 bonus to your Dexterity score.\n\n"
                "These leather bracers are reinforced with magical sinew, enhancing the wielder's precision."
            ),
            is_wearing=is_wearing,
            improvements=[
                AbilityScoreBonus(
                    bonuses=[(Ability.DEXTERITY, 2)],
                    total=2,
                    error_prefix="Bracers of Archery bonus",
                )
            ],
            is_homebrew=False,
        )


class GauntletsOfStrength(Item):
    """Magical gauntlets that increase Strength by 2."""

    def __init__(self, is_wearing: bool = True):
        super().__init__(
            "Gauntlets of Strength",
            rarity=ItemRarity.RARE,
            requires_attunement=True,
            category=ItemCategory.WONDROUS,
            slots=0,
            description_text=(
                "While wearing these gauntlets, your Strength score increases by 2.\n\n"
                "These steel gauntlets hum with raw, restrained power."
            ),
            is_wearing=is_wearing,
            improvements=[
                AbilityScoreBonus(
                    bonuses=[(Ability.STRENGTH, 2)],
                    total=2,
                    error_prefix="Gauntlets of Strength bonus",
                )
            ],
        )
