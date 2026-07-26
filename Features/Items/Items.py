from typing import Optional

from Core.Definitions import Ability, Skill
from Features.Core.BaseFeatures import Feature
from Features.Core.SubFeatures import (
    AbilityScoreBonus,
    ArmorClassBonus,
    CarryingCapacityBonus,
    SkillBonus,
    SubFeature,
)
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class Item(Feature):
    """
    Base class for all items. Items are now Features, allowing them to be
    either description-only or to modify a character via SubFeatures.

    An item has metadata (rarity, attunement, category, weight, slots, value,
    homebrew status) and can:
    - Provide a description via get_description()
    - Apply mechanical effects via subfeatures and apply()
    - Take up carrying capacity slots
    """

    def __init__(
        self,
        name: str,
        rarity: str = "common",
        requires_attunement: bool = False,
        category: str = "wondrous",
        weight: Optional[float] = None,
        slots: int = 1,
        description_text: str = "",
        subfeatures: Optional[list[SubFeature]] = None,
        is_homebrew: bool = True,
        value: Optional[float] = None,
    ):
        super().__init__(name=name, origin=category)
        self.rarity = rarity
        self.requires_attunement = requires_attunement
        self.category = category
        self.weight = weight
        self.slots = slots
        self.description_text = description_text
        self.subfeatures = subfeatures or []
        self.is_homebrew = is_homebrew
        # Value in gold pieces (GP). None means unknown/unpriced and should
        # not be displayed.
        self.value = value

    def apply(self, character_stat_block: CharacterStatBlock):
        """Apply all subfeatures to the character."""
        for subfeature in self.subfeatures:
            subfeature.apply(character_stat_block)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str | None:
        """Return the item description. Subclasses can override."""
        if self.description_text:
            return self.description_text
        return None

    def get_value_display(self) -> Optional[str]:
        """Return the item's value as a display string (e.g. '25 GP'), or None if unpriced."""
        if self.value is None:
            return None
        if self.value == int(self.value):
            return f"{int(self.value)} GP"
        return f"{self.value:g} GP"

    def description(self) -> str:
        """Backward compatibility: returns description_text (no character stat block needed)."""
        return self.description_text


# ══════════════════════════════════════════════════════════════════════════════
# WearableItem: Items that must be worn to apply their effects
# ══════════════════════════════════════════════════════════════════════════════


class WearableItem(Item):
    """
    An item that must be worn for its effects to apply.
    Subfeatures only activate when is_wearing is True.
    """

    def __init__(
        self,
        name: str,
        rarity: str = "common",
        requires_attunement: bool = False,
        category: str = "wondrous",
        weight: Optional[float] = None,
        slots: int = 1,
        description_text: str = "",
        subfeatures: Optional[list[SubFeature]] = None,
        is_wearing: bool = True,
        is_homebrew: bool = True,
        value: Optional[float] = None,
    ):
        super().__init__(
            name=name,
            rarity=rarity,
            requires_attunement=requires_attunement,
            category=category,
            weight=weight,
            slots=slots,
            description_text=description_text,
            subfeatures=subfeatures,
            is_homebrew=is_homebrew,
            value=value,
        )
        self.is_wearing = is_wearing

    def apply(self, character_stat_block: CharacterStatBlock):
        """Only apply subfeatures if the item is being worn."""
        if self.is_wearing:
            for subfeature in self.subfeatures:
                subfeature.apply(character_stat_block)


# ══════════════════════════════════════════════════════════════════════════════
# ConsumableItem: Items consumed on use
# ══════════════════════════════════════════════════════════════════════════════


class ConsumableItem(Item):
    """
    An item consumed on use (potions, rations, torches, etc.).
    These items track usage via checkboxes on the character sheet.
    """

    def __init__(
        self,
        name: str,
        rarity: str = "common",
        category: str = "consumable",
        weight: Optional[float] = None,
        slots: int = 1,
        description_text: str = "",
        subfeatures: Optional[list[SubFeature]] = None,
        is_homebrew: bool = True,
        value: Optional[float] = None,
    ):
        super().__init__(
            name=name,
            rarity=rarity,
            requires_attunement=False,
            category=category,
            weight=weight,
            slots=slots,
            description_text=description_text,
            subfeatures=subfeatures,
            is_homebrew=is_homebrew,
            value=value,
        )
        # Consumables are typically never attuned
        self.requires_attunement = False


# ══════════════════════════════════════════════════════════════════════════════
# Simple Description-Only Items
# ══════════════════════════════════════════════════════════════════════════════


class Gold(Item):
    def __init__(self):
        super().__init__(
            "Gold Pieces",
            rarity="common",
            category="currency",
            slots=0,
            description_text="A stack of gold pieces.",
            is_homebrew=False,
            value=1,
        )


class Silver(Item):
    def __init__(self):
        super().__init__(
            "Silver Pieces",
            rarity="common",
            category="currency",
            slots=0,
            description_text="A stack of silver pieces.",
            is_homebrew=False,
            value=0.1,
        )


class Quiver(Item):
    def __init__(self):
        super().__init__(
            "Quiver",
            rarity="uncommon",
            category="common",
            slots=1,
            description_text="A regular quiver",
            is_homebrew=False,
            value=1,
        )


class ThievesTools(Item):
    def __init__(self):
        super().__init__(
            "Thieves' Tools",
            rarity="uncommon",
            category="common",
            slots=1,
            description_text="Utilize: Pick a lock, or disarm a trap (DEX DC 15)",
            is_homebrew=False,
        )


class Backpack(WearableItem):
    def __init__(self, is_wearing: bool = True):
        super().__init__(
            "Backpack",
            rarity="common",
            category="container",
            slots=1,
            description_text=(
                "A backpack that can hold up to 30 pounds of gear within 1 cubic foot. "
                "It can also be strapped to a mount as a saddlebag."
            ),
            subfeatures=[CarryingCapacityBonus(10, source="Backpack")],
            is_wearing=is_wearing,
            is_homebrew=False,
            value=2,
        )


class Caltrops(Item):
    def __init__(self):
        super().__init__(
            "Caltrops",
            rarity="common",
            category="utility",
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


class Crowbar(Item):
    def __init__(self):
        super().__init__(
            "Crowbar",
            rarity="common",
            category="tool",
            slots=1,
            description_text="Using a crowbar grants advantage on Strength checks where leverage can be applied.",
            is_homebrew=False,
            value=2,
        )


class Candle(ConsumableItem):
    def __init__(self):
        super().__init__(
            "Candle",
            rarity="common",
            category="utility",
            slots=0,
            description_text="For 1 hour, a lit Candle sheds Bright Light in a 5-foot radius and Dim Light for an additional 5 feet.",
            is_homebrew=False,
            value=0.01,
        )


class BallBearings(Item):
    def __init__(self):
        super().__init__(
            "Ball Bearings",
            rarity="common",
            category="utility",
            slots=1,
            description_text="As a Utilize action, you can spill Ball Bearings from their pouch. They spread to cover a level, 10-foot-square area within 10 feet of yourself. A creature that enters this area for the first time on a turn must succeed on a DC 10 Dexterity saving throw or have the Prone condition. It takes 10 minutes to recover the Ball Bearings.",
            is_homebrew=False,
            value=1,
        )


class HoodedLantern(Item):
    def __init__(self):
        super().__init__(
            "Hooded Lantern",
            rarity="common",
            category="utility",
            slots=1,
            description_text="A Hooded Lantern burns Oil as fuel to cast Bright Light in a 30-foot radius and Dim Light for an additional 30 feet. As a Bonus Action, you can lower the hood, reducing the light to Dim Light in a 5-foot radius, or raise it again.",
            is_homebrew=False,
            value=5,
        )


class FlasksOfOil(ConsumableItem):
    def __init__(self):
        super().__init__(
            "Flask of Oil",
            rarity="common",
            category="utility",
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
            rarity="common",
            category="consumable",
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
            rarity="common",
            category="consumable",
            slots=0,
            description_text="As a Bonus Action, you can drink a vial of Antitoxin to gain Advantage on saving throws to avoid or end the Poisoned condition for 1 hour.",
            is_homebrew=False,
            value=50,
        )


class HealersKit(ConsumableItem):
    def __init__(self):
        super().__init__(
            "Healer's Kit",
            rarity="common",
            category="consumable",
            slots=1,
            description_text="A Healer's Kit has ten uses. As a Utilize action, you can expend one of its uses to stabilize an Unconscious creature that has 0 Hit Points without needing to make a Wisdom (Medicine) check.",
            is_homebrew=False,
            value=5,
        )


class PotionOfHealing(ConsumableItem):
    def __init__(self):
        super().__init__(
            "Potion of Healing",
            rarity="common",
            category="consumable",
            slots=1,
            description_text=(
                "You regain 2d4 + 2 Hit Points when you drink this potion.\n"
                "Whatever its potency, the potion's red liquid glimmers when agitated."
            ),
            is_homebrew=False,
            value=50,
        )


class Rope(Item):
    def __init__(self):
        super().__init__(
            "Rope (50 ft)",
            rarity="common",
            category="utility",
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
            rarity="common",
            category="tool",
            slots=0,
            description_text=(
                "A small container with flint, fire steel, and tinder used to start fires. "
                "Lighting a torch, lamp, lantern, or similar exposed fuel takes a bonus action. "
                "Lighting other fires takes 1 minute."
            ),
            is_homebrew=False,
            value=0.5,
        )


class Torch(ConsumableItem):
    def __init__(self):
        super().__init__(
            "Torch",
            rarity="common",
            category="utility",
            slots=1,
            description_text=(
                "Burns for 1 hour, providing bright light in a 20-foot radius and dim light for another 20 feet.\n\n"
                "It can be used as a simple melee weapon. On a hit, it deals 1 fire damage."
            ),
            is_homebrew=False,
            value=0.01,
        )


class BullseyeLantern(Item):
    def __init__(self):
        super().__init__(
            "Bullseye Lantern",
            rarity="common",
            category="utility",
            slots=1,
            description_text=(
                "Consumes oil as fuel to cast bright light in a 60-foot cone and dim light "
                "for an additional 60 feet. The lantern can be shuttered to block the light."
            ),
            is_homebrew=False,
            value=10,
        )


class Costume(WearableItem):
    def __init__(self, is_wearing: bool = True):
        super().__init__(
            "Costume",
            rarity="common",
            category="adventuring gear",
            slots=1,
            description_text=(
                "While wearing this costume, you have advantage on ability checks made to "
                "impersonate the person or type of person it represents."
            ),
            is_wearing=is_wearing,
            is_homebrew=False,
            value=5,
        )


class Mirror(Item):
    def __init__(self):
        super().__init__(
            "Steel Mirror",
            rarity="common",
            category="tool",
            slots=0,
            description_text=(
                "A small handheld mirror useful for personal grooming. It can also be used "
                "to peek around corners without exposing yourself or to reflect light as a signal."
            ),
            is_homebrew=False,
            value=5,
        )


class Typewriter(Item):
    def __init__(self):
        super().__init__(
            "Typewriter",
            rarity="common",
            category="musical instrument",
            slots=1,
            description_text=(
                "A mechanical typewriter that can also be used as a musical instrument, "
                "producing rhythmic clacking sounds."
            ),
        )


class NightVisionGoggles(WearableItem):
    def __init__(self, is_wearing: bool = True):
        super().__init__(
            "Nightvision Goggles",
            rarity="uncommon",
            category="wondrous item",
            slots=1,
            description_text="While wearing these goggles, you gain darkvision out to 120 feet.",
            is_wearing=is_wearing,
        )


class ButterflyKnife(Item):
    def __init__(self):
        super().__init__(
            "Butterfly Knife",
            rarity="common",
            category="weapon",
            slots=1,
            description_text=(
                "A small folding knife that can be quickly deployed. "
                "Functions as a light melee weapon."
            ),
        )


class Beans(ConsumableItem):
    def __init__(self):
        super().__init__(
            "Can of Beans",
            rarity="common",
            category="consumable",
            slots=1,
            description_text="A simple can of preserved beans. Provides a basic meal when consumed.",
        )


class Makarov(Item):
    def __init__(self):
        super().__init__(
            "Makarov",
            rarity="uncommon",
            category="weapon",
            slots=1,
            description_text=(
                "In a fantasy realm, this pistol becomes a magical ranged weapon.\n\n"
                "It has 4 charges. Each shot deals 2d6 + your Dexterity modifier damage. "
                "The weapon regains all charges after a long rest."
            ),
        )


class Bedroll(Item):
    def __init__(self):
        super().__init__(
            "Bedroll",
            rarity="common",
            category="adventuring gear",
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
            rarity="common",
            category="utility",
            slots=0,
            description_text="When rung as an action, the bell produces a clear sound audible up to 60 feet away.",
            is_homebrew=False,
            value=1,
        )


class Waterskin(Item):
    def __init__(self):
        super().__init__(
            "Waterskin",
            rarity="common",
            category="container",
            slots=1,
            description_text="Holds up to 4 pints of liquid. Essential for survival, as insufficient water can lead to dehydration.",
            is_homebrew=False,
            value=0.2,
        )


class Arrows(Item):
    def __init__(self):
        super().__init__(
            "Arrows",
            rarity="common",
            category="ammunition",
            slots=1,
            description_text="A bundle of arrows.",
            is_homebrew=False,
        )


class HobbyHorse(Item):
    def __init__(self):
        super().__init__(
            "Käpphäst",
            rarity="uncommon",
            category="wondrous item",
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
            rarity="common",
            category="wondrous",
            slots=2,
            description_text=(
                f"Uncorking this bottle summons a personal raincloud that follows you "
                f"for 60 minutes, raining gently and dramatically—even indoors. "
                f"The rain causes no harm but is perfect for brooding, monologues, or emotional exits. "
                f"Purely theatrical."
            ),
        )


class RobeOfLevitation(WearableItem):
    def __init__(self, is_wearing: bool = True):
        super().__init__(
            "Robe of Levitation",
            rarity="common",
            category="wondrous",
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
            rarity="uncommon",
            requires_attunement=True,
            category="wondrous",
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
            rarity="common",
            category="wondrous",
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
            rarity="uncommon",
            category="wondrous",
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
            rarity="rare",
            category="wondrous",
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
            rarity="legendary",
            category="wondrous",
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
            rarity="common",
            category="wondrous",
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
            rarity="uncommon",
            category="wondrous",
            slots=1,
            description_text=(
                "As an action, you activate this item to immediately cast Fireball centered on yourself. "
                "You automatically fail the saving throw."
            ),
        )


class FingerGunRing(WearableItem):
    def __init__(self, is_wearing: bool = True):
        super().__init__(
            "Ring of Finger Guns",
            rarity="common",
            category="ring",
            slots=0,
            description_text=(
                "While wearing this ring, forming finger guns and saying 'pew' creates a tiny harmless spark "
                "and sound effect. The spark can light candles but deals no damage."
            ),
            is_wearing=is_wearing,
        )


class BadFriendGlasses(WearableItem):
    def __init__(self, is_wearing: bool = True):
        super().__init__(
            "A Bad Friend Glasses",
            rarity="uncommon",
            category="wondrous",
            slots=1,
            description_text=(
                "While wearing these glasses, you may redirect damage you would take to another player character "
                "with the lowest hit points. You are, objectively, a terrible friend."
            ),
            is_wearing=is_wearing,
        )


# ══════════════════════════════════════════════════════════════════════════════
# Mechanical Items (with SubFeatures)
# ══════════════════════════════════════════════════════════════════════════════


class CloakOfProtection(WearableItem):
    """A magical cloak that grants +1 AC."""

    def __init__(self, is_wearing: bool = True):
        super().__init__(
            "Cloak of Protection",
            rarity="uncommon",
            requires_attunement=True,
            category="wondrous item",
            description_text=(
                "You gain a +1 bonus to AC while wearing this cloak.\n\n"
                "This silken cloak shimmers with protective magic and feels warm to the touch."
            ),
            is_wearing=is_wearing,
            subfeatures=[ArmorClassBonus(1)],
            is_homebrew=False,
        )


class PlusOneWeapon(Item):
    """A magical weapon that grants +1 to ability scores (e.g. Dexterity for finesse weapons)."""

    def __init__(
        self, weapon_name: str = "Longsword", ability: Ability = Ability.DEXTERITY
    ):
        self.ability = ability
        super().__init__(
            f"+1 {weapon_name}",
            rarity="uncommon",
            category="weapon",
            description_text=(
                f"This magical {weapon_name.lower()} grants you a +1 bonus to attack rolls and damage rolls made with it.\n\n"
                "The blade gleams with enchantment."
            ),
            subfeatures=[
                AbilityScoreBonus(
                    bonuses=[(ability, 1)],
                    total=1,
                    error_prefix=f"+1 {weapon_name} bonus",
            is_homebrew=False,
                )
            ],
        )


class BracersOfArchery(WearableItem):
    """Magical bracers that grant +2 Dexterity for ranged combat."""

    def __init__(self, is_wearing: bool = True):
        super().__init__(
            "Bracers of Archery",
            rarity="uncommon",
            requires_attunement=True,
            category="wondrous item",
            description_text=(
                "While wearing these bracers, you gain a +2 bonus to your Dexterity score.\n\n"
                "These leather bracers are reinforced with magical sinew, enhancing the wielder's precision."
            ),
            is_wearing=is_wearing,
            subfeatures=[
                AbilityScoreBonus(
                    bonuses=[(Ability.DEXTERITY, 2)],
                    total=2,
                    error_prefix="Bracers of Archery bonus",
            is_homebrew=False,
                )
            ],
        )


class GauntletsOfStrength(WearableItem):
    """Magical gauntlets that increase Strength by 2."""

    def __init__(self, is_wearing: bool = True):
        super().__init__(
            "Gauntlets of Strength",
            rarity="rare",
            requires_attunement=True,
            category="wondrous item",
            slots=0,
            description_text=(
                "While wearing these gauntlets, your Strength score increases by 2.\n\n"
                "These steel gauntlets hum with raw, restrained power."
            ),
            is_wearing=is_wearing,
            subfeatures=[
                AbilityScoreBonus(
                    bonuses=[(Ability.STRENGTH, 2)],
                    total=2,
                    error_prefix="Gauntlets of Strength bonus",
                )
            ],
        )


class RingOfIntelligence(WearableItem):
    """A mystical ring that increases Intelligence by 2."""

    def __init__(self, is_wearing: bool = True):
        super().__init__(
            "Ring of Intellect",
            rarity="rare",
            requires_attunement=True,
            category="ring",
            description_text=(
                "While wearing this ring, your Intelligence score increases by 2, as does your Intelligence saving throw.\n\n"
                "This silver ring is inscribed with arcane runes that glow faintly when worn."
            ),
            is_wearing=is_wearing,
            subfeatures=[
                AbilityScoreBonus(
                    bonuses=[(Ability.INTELLIGENCE, 2)],
                    total=2,
                    error_prefix="Ring of Intellect bonus",
                )
            ],
        )


class RingOfInvestigation(WearableItem):
    """A ring that grants +1 to Investigation checks."""

    def __init__(self, is_wearing: bool = True):
        super().__init__(
            "Ring of Investigation",
            rarity="uncommon",
            requires_attunement=False,
            category="ring",
            description_text=(
                "While wearing this ring, you gain a +1 bonus to Intelligence (Investigation) checks.\n\n"
                "A slender copper band set with a tiny magnifying lens that focuses the wearer's attention on overlooked details."
            ),
            is_wearing=is_wearing,
            subfeatures=[
                SkillBonus(Skill.INVESTIGATION, 1, source="Ring of Investigation")
            ],
        )


# Placeholder Craftable Items (TODO: fill in real stats)

class Acid(Item):
    def __init__(self):
        super().__init__(
            "Acid",
            rarity="common",
            category="consumable",
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
            rarity="common",
            category="consumable",
            weight=1,
            slots=1,
            description_text="When you take the Attack action, you can replace one of your attacks with throwing a flask of Alchemist's Fire. Target one creature or object you can see within 20 feet of yourself. The target must succeed on a Dexterity saving throw (DC 8 plus your Dexterity modifier and Proficiency Bonus) or take 1d4 Fire damage and start burning.",
            is_homebrew=False,
            value=50,
        )

class AnyMeleeWeaponPlaceholder(Item):
    def __init__(self):
        super().__init__(
            "Any Melee weapon (except Club, Greatclub, Quarterstaff, and Whip)",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
            is_homebrew=False,
        )

class ArcaneFocus(Item):
    def __init__(self):
        super().__init__(
            "Arcane Focus",
            rarity="common",
            category="focus",
            weight=None,
            slots=1,
            description_text="An Arcane Focus takes one of several forms and is bejeweled or carved to channel arcane magic. A Sorcerer, Warlock, or Wizard can use such an item as a Spellcasting Focus.",
            is_homebrew=False,
        )

class Barrel(Item):
    def __init__(self):
        super().__init__(
            "Barrel",
            rarity="common",
            category="gear",
            weight=70,
            slots=1,
            description_text="A Barrel holds up to 40 gallons of liquid or up to 4 cubic feet of dry goods.",
            is_homebrew=False,
            value=2,
        )

class BasicPoison(Item):
    def __init__(self):
        super().__init__(
            "Basic Poison",
            rarity="common",
            category="consumable",
            weight=None,
            slots=1,
            description_text="As a Bonus Action, you can use a vial of Basic Poison to coat one weapon or up to three pieces of ammunition. A creature that takes Piercing or Slashing damage from the poisoned weapon or ammunition takes an extra 1d4 Poison damage. Once applied, the poison retains potency for 1 minute or until its damage is dealt, whichever comes first.",
            is_homebrew=False,
            value=100,
        )

class Basket(Item):
    def __init__(self):
        super().__init__(
            "Basket",
            rarity="common",
            category="gear",
            weight=2,
            slots=1,
            description_text="A Basket holds up to 40 pounds within 2 cubic feet.",
            is_homebrew=False,
            value=0.4,
        )

class Blanket(Item):
    def __init__(self):
        super().__init__(
            "Blanket",
            rarity="common",
            category="gear",
            weight=3,
            slots=1,
            description_text="While wrapped in a blanket, you have Advantage on saving throws against extreme cold.",
            is_homebrew=False,
            value=0.5,
        )

class BlockAndTackle(Item):
    def __init__(self):
        super().__init__(
            "Block and Tackle",
            rarity="common",
            category="tool",
            weight=5,
            slots=1,
            description_text="A Block and Tackle allows you to hoist up to four times the weight you can normally lift.",
            is_homebrew=False,
            value=1,
        )

class Bolts(Item):
    def __init__(self):
        super().__init__(
            "Bolts",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
            is_homebrew=False,
        )

class Bucket(Item):
    def __init__(self):
        super().__init__(
            "Bucket",
            rarity="common",
            category="gear",
            weight=2,
            slots=1,
            description_text="A Bucket holds up to half a cubic foot of contents.",
            is_homebrew=False,
            value=0.05,
        )

class BrightFungalCloak(WearableItem):
    def __init__(self, is_wearing: bool = True):
        super().__init__(
            "Bright Fungal Cloak",
            rarity="common",
            category="clothing",
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

class Book(Item):
    def __init__(self):
        super().__init__(
            "Book",
            rarity="common",
            category="gear",
            weight=5,
            slots=1,
            description_text="A Book contains fiction or nonfiction. If you consult an accurate nonfiction Book about its topic, you gain a +5 bonus to Intelligence (Arcana, History, Nature, or Religion) checks you make about that topic.",
            is_homebrew=False,
            value=25,
        )

class DesertClothing(WearableItem):
    def __init__(self, is_wearing: bool = True):
        super().__init__(
            "Desert Clothing",
            rarity="common",
            category="clothing",
            weight=None,
            slots=1,
            description_text="When you are wearing Desert Clothing and not wearing Medium or Heavy armor, you automatically succeed on saving throws against the effects of extreme heat.",
            is_wearing=is_wearing,
            is_homebrew=False,
            value=5,
        )

class DevilMask(WearableItem):
    def __init__(self, is_wearing: bool = True):
        super().__init__(
            "Devil Mask",
            rarity="common",
            category="clothing",
            weight=None,
            slots=1,
            description_text="While you are wearing a Devil Mask, other creatures have Disadvantage on Intelligence (Investigation) and Wisdom (Insight) checks made to discern your true identity or intentions.",
            is_wearing=is_wearing,
            is_homebrew=False,
            value=25,
        )

class GarbOfLightAndShadow(WearableItem):
    def __init__(self, is_wearing: bool = True):
        super().__init__(
            "Garb of Light and Shadow",
            rarity="common",
            category="wondrous",
            weight=None,
            slots=1,
            description_text="This garb appeals to Fey from one Domain of Delight, such as the Gloaming Court or the Summer Court. While wearing the garb, you have Advantage on ability checks to influence Fey associated with that Domain of Delight.",
            is_wearing=is_wearing,
            is_homebrew=False,
            value=50,
        )

class GenieRobe(WearableItem):
    def __init__(self, is_wearing: bool = True):
        super().__init__(
            "Genie Robe",
            rarity="common",
            category="wondrous",
            weight=None,
            slots=1,
            description_text="This robe appeals to Elementals associated with a particular Elemental Plane (Air, Earth, Fire, Water). While wearing a Genie Robe, you have Advantage on ability checks made to influence Elementals associated with that plane.",
            is_wearing=is_wearing,
            is_homebrew=False,
            value=50,
        )

class HolyWater(Item):
    def __init__(self):
        super().__init__(
            "Holy Water",
            rarity="common",
            category="consumable",
            weight=1,
            slots=1,
            description_text="When you take the Attack action, you can replace one of your attacks with throwing a flask of Holy Water. Target one creature you can see within 20 feet of yourself. The target must succeed on a Dexterity saving throw (DC 8 plus your Dexterity modifier and Proficiency Bonus) or take 2d8 Radiant damage if it is a Fiend or an Undead.",
            is_homebrew=False,
            value=25,
        )

class LockingSpellbook(Item):
    def __init__(self):
        super().__init__(
            "Locking Spellbook",
            rarity="common",
            category="gear",
            weight=None,
            slots=1,
            description_text="This 100-page leather-bound tome can be used as a Spellbook. It is closed with a lock that comes with a key. As a Utilize action, a creature can try to pick the lock using Thieves' Tools, doing so with a successful DC 15 Dexterity (Sleight of Hand) check.",
            is_homebrew=False,
            value=35,
        )

class MonsterCamouflage(WearableItem):
    def __init__(self, is_wearing: bool = True):
        super().__init__(
            "Monster Camouflage",
            rarity="common",
            category="clothing",
            weight=None,
            slots=1,
            description_text="A suit of Monster Camouflage looks like a Beast or Monstrosity, such as an owlbear. To discern that you're disguised, a creature must take the Study action to inspect your appearance and succeed on a DC 10 Intelligence (Investigation or Nature) check. The creature has Advantage on this check if it is within 30 feet of you and automatically succeeds on this check if you do anything the monster you're disguised as couldn't do.",
            is_wearing=is_wearing,
            is_homebrew=False,
            value=50,
        )

class WarmFungalClothing(WearableItem):
    def __init__(self, is_wearing: bool = True):
        super().__init__(
            "Warm Fungal Clothing",
            rarity="common",
            category="clothing",
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

class WinterCamouflage(WearableItem):
    def __init__(self, is_wearing: bool = True):
        super().__init__(
            "Winter Camouflage",
            rarity="common",
            category="clothing",
            weight=None,
            slots=1,
            description_text="While you wear Winter Camouflage in an appropriate environment, you have Advantage on Dexterity (Stealth) checks.",
            is_wearing=is_wearing,
            is_homebrew=False,
            value=50,
        )

class Chain(Item):
    def __init__(self):
        super().__init__(
            "Chain",
            rarity="common",
            category="gear",
            weight=10,
            slots=1,
            description_text="As a Utilize action, you can wrap a Chain around an unwilling creature within 5 feet of yourself that has the Grappled, Incapacitated, or Restrained condition if you succeed on a DC 13 Strength (Athletics) check. If the creature's legs are bound, the creature has the Restrained condition until it escapes. Escaping the Chain requires the creature to make a successful DC 18 Dexterity (Acrobatics) check as an action. Bursting the Chain requires a successful DC 20 Strength (Athletics) check as an action.",
            is_homebrew=False,
            value=5,
        )

class Chest(Item):
    def __init__(self):
        super().__init__(
            "Chest",
            rarity="common",
            category="container",
            weight=25,
            slots=1,
            description_text="A Chest holds up to 12 cubic feet of contents.",
            is_homebrew=False,
            value=5,
        )

class ClimbersKit(Item):
    def __init__(self):
        super().__init__(
            "Climber's Kit",
            rarity="common",
            category="tool",
            weight=12,
            slots=1,
            description_text="A Climber's Kit includes boot tips, gloves, pitons, and a harness. As a Utilize action, you can use the Climber's Kit to anchor yourself; when you do, you can't fall more than 25 feet from the anchor point, and you can't move more than 25 feet from there without undoing the anchor as a Bonus Action.",
            is_homebrew=False,
            value=25,
        )

class Club(Item):
    def __init__(self):
        super().__init__(
            "Club",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
            is_homebrew=False,
        )

class ComponentPouch(Item):
    def __init__(self):
        super().__init__(
            "Component Pouch",
            rarity="common",
            category="gear",
            weight=2,
            slots=1,
            description_text="A Component Pouch is watertight and filled with compartments that hold all the free Material components of your spells.",
            is_homebrew=False,
            value=25,
        )

class CrossbowBoltCase(Item):
    def __init__(self):
        super().__init__(
            "Crossbow Bolt Case",
            rarity="common",
            category="container",
            weight=1,
            slots=1,
            description_text="A Crossbow Bolt Case holds up to 20 Bolts.",
            is_homebrew=False,
            value=1,
        )

class DruidicFocus(Item):
    def __init__(self):
        super().__init__(
            "Druidic Focus",
            rarity="common",
            category="focus",
            weight=None,
            slots=1,
            description_text="A Druidic Focus takes one of several forms and is carved, tied with ribbon, or painted to channel primal magic. A Druid or Ranger can use such an object as a Spellcasting Focus.",
            is_homebrew=False,
        )

class FineClothes(Item):
    def __init__(self):
        super().__init__(
            "Fine Clothes",
            rarity="common",
            category="clothing",
            weight=6,
            slots=1,
            description_text="Fine Clothes are made of expensive fabrics and adorned with expertly crafted details. Some events and locations admit only people wearing these clothes.",
            is_homebrew=False,
            value=15,
        )

class FirearmBullets(Item):
    def __init__(self):
        super().__init__(
            "Firearm Bullets",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
            is_homebrew=False,
        )

class Flask(Item):
    def __init__(self):
        super().__init__(
            "Flask",
            rarity="common",
            category="gear",
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
            rarity="common",
            category="container",
            weight=2,
            slots=1,
            description_text="A Glass Bottle holds up to 1½ pints.",
            is_homebrew=False,
            value=2,
        )

class GrapplingHook(Item):
    def __init__(self):
        super().__init__(
            "Grappling Hook",
            rarity="common",
            category="tool",
            weight=4,
            slots=1,
            description_text="As a Utilize action, you can throw the Grappling Hook at a railing, a ledge, or another catch within 50 feet of yourself, and the hook catches on if you succeed on a DC 13 Dexterity (Acrobatics) check. If you tied a Rope to the hook, you can then climb it.",
            is_homebrew=False,
            value=5,
        )

class Greatclub(Item):
    def __init__(self):
        super().__init__(
            "Greatclub",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
            is_homebrew=False,
        )

class HeavyArmorPlaceholder(Item):
    def __init__(self):
        super().__init__(
            "Heavy armor",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
            is_homebrew=False,
        )

class HideArmor(Item):
    def __init__(self):
        super().__init__(
            "Hide Armor",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
            is_homebrew=False,
        )

class HolySymbol(Item):
    def __init__(self):
        super().__init__(
            "Holy Symbol",
            rarity="common",
            category="focus",
            weight=None,
            slots=1,
            description_text="A Holy Symbol takes one of several forms and is bejeweled or painted to channel divine magic. A Cleric or Paladin can use a Holy Symbol as a Spellcasting Focus.",
            is_homebrew=False,
        )

class HuntingTrap(Item):
    def __init__(self):
        super().__init__(
            "Hunting Trap",
            rarity="common",
            category="gear",
            weight=25,
            slots=1,
            description_text="As a Utilize action, you can set a Hunting Trap, which is a sawtooth steel ring that snaps shut when a creature steps on a pressure plate in the center. A creature that steps on the plate must succeed on a DC 13 Dexterity saving throw or take 1d4 Piercing damage and have its Speed reduced to 0 until the start of its next turn. A creature can use its action to make a DC 13 Strength (Athletics) check, freeing itself or another creature within its reach on a success.",
            is_homebrew=False,
            value=5,
        )

class Ink(Item):
    def __init__(self):
        super().__init__(
            "Ink",
            rarity="common",
            category="gear",
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
            rarity="common",
            category="gear",
            weight=None,
            slots=1,
            description_text="Using Ink, an Ink Pen is used to write or draw.",
            is_homebrew=False,
            value=0.02,
        )

class IronPot(Item):
    def __init__(self):
        super().__init__(
            "Iron Pot",
            rarity="common",
            category="gear",
            weight=10,
            slots=1,
            description_text="An Iron Pot holds up to 1 gallon.",
            is_homebrew=False,
            value=2,
        )

class IronSpikes(Item):
    def __init__(self):
        super().__init__(
            "Iron Spikes",
            rarity="common",
            category="gear",
            weight=5,
            slots=1,
            description_text="Iron Spikes come in bundles of ten. As a Utilize action, you can use a blunt object, such as a Light Hammer, to hammer a spike into wood, earth, or a similar material. You can do so to jam a door shut or to then tie a Rope or Chain to the Spike.",
            is_homebrew=False,
            value=1,
        )

class Jug(Item):
    def __init__(self):
        super().__init__(
            "Jug",
            rarity="common",
            category="container",
            weight=4,
            slots=1,
            description_text="A Jug holds up to 1 gallon.",
            is_homebrew=False,
            value=0.02,
        )

class Ladder(Item):
    def __init__(self):
        super().__init__(
            "Ladder",
            rarity="common",
            category="gear",
            weight=25,
            slots=1,
            description_text="A Ladder is 10 feet tall. You must climb to move up or down it.",
            is_homebrew=False,
            value=0.1,
        )

class Lamp(Item):
    def __init__(self):
        super().__init__(
            "Lamp",
            rarity="common",
            category="gear",
            weight=1,
            slots=1,
            description_text="A Lamp burns Oil as fuel to cast Bright Light in a 15-foot radius and Dim Light for an additional 30 feet.",
            is_homebrew=False,
            value=0.5,
        )

class LeatherArmor(Item):
    def __init__(self):
        super().__init__(
            "Leather Armor",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
            is_homebrew=False,
        )

class Lock(Item):
    def __init__(self):
        super().__init__(
            "Lock",
            rarity="common",
            category="gear",
            weight=1,
            slots=1,
            description_text="A Lock comes with a key. Without the key, a creature can use Thieves' Tools to pick this Lock with a successful DC 15 Dexterity (Sleight of Hand) check.",
            is_homebrew=False,
            value=10,
        )

class MagnifyingGlass(Item):
    def __init__(self):
        super().__init__(
            "Magnifying Glass",
            rarity="common",
            category="gear",
            weight=None,
            slots=1,
            description_text="A Magnifying Glass grants Advantage on any ability check made to appraise or inspect a highly detailed item. Lighting a fire with a Magnifying Glass requires light as bright as sunlight to focus, tinder to ignite, and about 5 minutes for the fire to ignite.",
            is_homebrew=False,
            value=100,
        )

class Manacles(Item):
    def __init__(self):
        super().__init__(
            "Manacles",
            rarity="common",
            category="gear",
            weight=6,
            slots=1,
            description_text="As a Utilize action, you can use Manacles to bind an unwilling Small or Medium creature within 5 feet of yourself that has the Grappled, Incapacitated, or Restrained condition if you succeed on a DC 13 Dexterity (Sleight of Hand) check. While bound, a creature has Disadvantage on attack rolls, and the creature is Restrained if the Manacles are attached to a chain or hook that is fixed in place. Escaping the Manacles requires a successful DC 20 Dexterity (Sleight of Hand) check as an action. Bursting them requires a successful DC 25 Strength (Athletics) check as an action. Each set of Manacles comes with a key.",
            is_homebrew=False,
            value=2,
        )

class Map(Item):
    def __init__(self):
        super().__init__(
            "Map",
            rarity="common",
            category="gear",
            weight=None,
            slots=1,
            description_text="If you consult an accurate Map, you gain a +5 bonus to Wisdom (Survival) checks you make to find your way in the place represented on it.",
            is_homebrew=False,
            value=1,
        )

class MapOrScrollCase(Item):
    def __init__(self):
        super().__init__(
            "Map or Scroll Case",
            rarity="common",
            category="container",
            weight=1,
            slots=1,
            description_text="A Map or Scroll Case holds up to 10 sheets of paper or 5 sheets of parchment.",
            is_homebrew=False,
            value=1,
        )

class MediumArmorPlaceholder(Item):
    def __init__(self):
        super().__init__(
            "Medium armor (except Hide)",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
            is_homebrew=False,
        )

class MirrorPlaceholder(Item):
    def __init__(self):
        super().__init__(
            "Mirror",
            rarity="common",
            category="gear",
            weight=0.5,
            slots=1,
            description_text="A handheld steel Mirror is useful for personal cosmetics but also for peeking around corners and reflecting light as a signal.",
            is_homebrew=False,
            value=5,
        )

class Musket(Item):
    def __init__(self):
        super().__init__(
            "Musket",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
            is_homebrew=False,
        )

class Needles(Item):
    def __init__(self):
        super().__init__(
            "Needles",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
            is_homebrew=False,
        )

class Net(Item):
    def __init__(self):
        super().__init__(
            "Net",
            rarity="common",
            category="gear",
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
            rarity="common",
            category="gear",
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
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
            is_homebrew=False,
        )

class Paper(Item):
    def __init__(self):
        super().__init__(
            "Paper",
            rarity="common",
            category="gear",
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
            rarity="common",
            category="gear",
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
            rarity="common",
            category="gear",
            weight=None,
            slots=1,
            description_text="Perfume comes in a 4-ounce vial. For 1 hour after applying Perfume to yourself, you have Advantage on Charisma (Persuasion) checks made to influence an Indifferent Humanoid within 5 feet of yourself.",
            is_homebrew=False,
            value=5,
        )

class Pistol(Item):
    def __init__(self):
        super().__init__(
            "Pistol",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
            is_homebrew=False,
        )

class Pole(Item):
    def __init__(self):
        super().__init__(
            "Pole",
            rarity="common",
            category="gear",
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
            rarity="common",
            category="tool",
            weight=35,
            slots=1,
            description_text="You can use a Portable Ram to break down doors. When doing so, you gain a +4 bonus to the Strength check. One other character can help you use the ram, giving you Advantage on this check.",
            is_homebrew=False,
            value=4,
        )

class Pouch(Item):
    def __init__(self):
        super().__init__(
            "Pouch",
            rarity="common",
            category="container",
            weight=1,
            slots=1,
            description_text="A Pouch holds up to 6 pounds within one-fifth of a cubic foot.",
            is_homebrew=False,
            value=0.5,
        )

class Quarterstaff(Item):
    def __init__(self):
        super().__init__(
            "Quarterstaff",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
            is_homebrew=False,
        )

class RangedWeaponsPlaceholder(Item):
    def __init__(self):
        super().__init__(
            "Ranged weapons (except Pistol, Musket, and Sling)",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
            is_homebrew=False,
        )

class Robe(Item):
    def __init__(self):
        super().__init__(
            "Robe",
            rarity="common",
            category="clothing",
            weight=4,
            slots=1,
            description_text="A Robe has vocational or ceremonial significance. Some events and locations admit only people wearing a Robe bearing certain colors or symbols.",
            is_homebrew=False,
            value=1,
        )

class RopePlaceholder(Item):
    def __init__(self):
        super().__init__(
            "Rope",
            rarity="common",
            category="gear",
            weight=5,
            slots=1,
            description_text="As a Utilize action, you can tie a knot with Rope if you succeed on a DC 10 Dexterity (Sleight of Hand) check. The Rope can be burst with a successful DC 20 Strength (Athletics) check. You can bind an unwilling creature with the Rope only if the creature has the Grappled, Incapacitated, or Restrained condition. Escaping the Rope requires the creature to make a successful DC 15 Dexterity (Acrobatics) check as an action.",
            is_homebrew=False,
            value=1,
        )

class Sack(Item):
    def __init__(self):
        super().__init__(
            "Sack",
            rarity="common",
            category="container",
            weight=0.5,
            slots=1,
            description_text="A Sack holds up to 30 pounds within 1 cubic foot.",
            is_homebrew=False,
            value=0.01,
        )

class Shovel(Item):
    def __init__(self):
        super().__init__(
            "Shovel",
            rarity="common",
            category="tool",
            weight=5,
            slots=1,
            description_text="Working for 1 hour, you can use a Shovel to dig a hole that is 5 feet on each side in soil or similar material.",
            is_homebrew=False,
            value=2,
        )

class SignalWhistle(Item):
    def __init__(self):
        super().__init__(
            "Signal Whistle",
            rarity="common",
            category="gear",
            weight=None,
            slots=1,
            description_text="When blown as a Utilize action, a Signal Whistle produces a sound that can be heard up to 600 feet away.",
            is_homebrew=False,
            value=0.05,
        )

class Sling(Item):
    def __init__(self):
        super().__init__(
            "Sling",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
            is_homebrew=False,
        )

class SlingBullets(Item):
    def __init__(self):
        super().__init__(
            "Sling Bullets",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
            is_homebrew=False,
        )

class SpellScroll(Item):
    def __init__(self):
        super().__init__(
            "Spell Scroll",
            rarity="common",
            category="consumable",
            weight=None,
            slots=1,
            description_text="A Spell Scroll is a magic item that bears the words of a cantrip or a level 1 spell, determined by the scroll's creator. If the spell is on your class's spell list, you can read the scroll and cast the spell using its normal casting time and without providing any Material components. If the spell requires a saving throw or an attack roll, the spell save DC is 13, and the attack bonus is +5. The scroll disintegrates when the casting is completed.",
            is_homebrew=False,
        )

class Spyglass(Item):
    def __init__(self):
        super().__init__(
            "Spyglass",
            rarity="common",
            category="gear",
            weight=1,
            slots=1,
            description_text="Objects viewed through a Spyglass are magnified to twice their size.",
            is_homebrew=False,
            value=1000,
        )

class StringItem(Item):
    def __init__(self):
        super().__init__(
            "String",
            rarity="common",
            category="gear",
            weight=None,
            slots=1,
            description_text="String is 10 feet long. You can tie a knot in it as a Utilize action.",
            is_homebrew=False,
            value=0.1,
        )

class StuddedLeatherArmor(Item):
    def __init__(self):
        super().__init__(
            "Studded Leather Armor",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
            is_homebrew=False,
        )

class Tent(Item):
    def __init__(self):
        super().__init__(
            "Tent",
            rarity="common",
            category="gear",
            weight=20,
            slots=1,
            description_text="A Tent sleeps up to two Small or Medium creatures.",
            is_homebrew=False,
            value=2,
        )

class TravelersClothes(Item):
    def __init__(self):
        super().__init__(
            "Traveler's Clothes",
            rarity="common",
            category="clothing",
            weight=4,
            slots=1,
            description_text="Traveler's Clothes are resilient garments designed for travel in various environments.",
            is_homebrew=False,
            value=2,
        )

class Vial(Item):
    def __init__(self):
        super().__init__(
            "Vial",
            rarity="common",
            category="container",
            weight=None,
            slots=1,
            description_text="A Vial holds up to 4 ounces.",
            is_homebrew=False,
            value=1,
        )

class Whip(Item):
    def __init__(self):
        super().__init__(
            "Whip",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
            is_homebrew=False,
        )

