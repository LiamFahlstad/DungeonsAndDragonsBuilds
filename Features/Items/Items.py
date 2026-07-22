from typing import Optional

from Definitions import Ability, Skill
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

    An item has metadata (rarity, attunement, category, weight, slots) and can:
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
    ):
        super().__init__(name=name, origin=category)
        self.rarity = rarity
        self.requires_attunement = requires_attunement
        self.category = category
        self.weight = weight
        self.slots = slots
        self.description_text = description_text
        self.subfeatures = subfeatures or []

    def apply(self, character_stat_block: CharacterStatBlock):
        """Apply all subfeatures to the character."""
        for subfeature in self.subfeatures:
            subfeature.apply(character_stat_block)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str | None:
        """Return the item description. Subclasses can override."""
        if self.description_text:
            return self.description_text
        return None

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
            description_text="(value=1GP) A stack of gold pieces.",
        )


class Silver(Item):
    def __init__(self):
        super().__init__(
            "Silver Pieces",
            rarity="common",
            category="currency",
            slots=0,
            description_text="(value=0.1GP) A stack of silver pieces.",
        )


class Quiver(Item):
    def __init__(self):
        super().__init__(
            "Quiver",
            rarity="uncommon",
            category="common",
            slots=1,
            description_text="A regular quiver",
        )


class ThievesTools(Item):
    def __init__(self):
        super().__init__(
            "Thieves' Tools",
            rarity="uncommon",
            category="common",
            slots=1,
            description_text="Utilize: Pick a lock, or disarm a trap (DEX DC 15)",
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
        )


class Crowbar(Item):
    def __init__(self):
        super().__init__(
            "Crowbar",
            rarity="common",
            category="tool",
            slots=1,
            description_text="Using a crowbar grants advantage on Strength checks where leverage can be applied.",
        )


class Candle(ConsumableItem):
    def __init__(self):
        super().__init__(
            "Candle",
            rarity="common",
            category="utility",
            slots=0,
            description_text="For 1 hour, a lit Candle sheds Bright Light in a 5-foot radius and Dim Light for an additional 5 feet.",
        )


class BallBearings(Item):
    def __init__(self):
        super().__init__(
            "Ball Bearings",
            rarity="common",
            category="utility",
            slots=1,
            description_text="As a Utilize action, you can spill Ball Bearings from their pouch. They spread to cover a level, 10-foot-square area within 10 feet of yourself. A creature that enters this area for the first time on a turn must succeed on a DC 10 Dexterity saving throw or have the Prone condition. It takes 10 minutes to recover the Ball Bearings.",
        )


class HoodedLantern(Item):
    def __init__(self):
        super().__init__(
            "Hooded Lantern",
            rarity="common",
            category="utility",
            slots=1,
            description_text="A Hooded Lantern burns Oil as fuel to cast Bright Light in a 30-foot radius and Dim Light for an additional 30 feet. As a Bonus Action, you can lower the hood, reducing the light to Dim Light in a 5-foot radius, or raise it again.",
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
        )


class Antitoxin(ConsumableItem):
    def __init__(self):
        super().__init__(
            "Antitoxin",
            rarity="common",
            category="consumable",
            slots=0,
            description_text="As a Bonus Action, you can drink a vial of Antitoxin to gain Advantage on saving throws to avoid or end the Poisoned condition for 1 hour.",
        )


class HealersKit(ConsumableItem):
    def __init__(self):
        super().__init__(
            "Healer's Kit",
            rarity="common",
            category="consumable",
            slots=1,
            description_text="A Healer's Kit has ten uses. As a Utilize action, you can expend one of its uses to stabilize an Unconscious creature that has 0 Hit Points without needing to make a Wisdom (Medicine) check.",
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
        )


class Bell(Item):
    def __init__(self):
        super().__init__(
            "Bell",
            rarity="common",
            category="utility",
            slots=0,
            description_text="When rung as an action, the bell produces a clear sound audible up to 60 feet away.",
        )


class Waterskin(Item):
    def __init__(self):
        super().__init__(
            "Waterskin",
            rarity="common",
            category="container",
            slots=1,
            description_text="Holds up to 4 pints of liquid. Essential for survival, as insufficient water can lead to dehydration.",
        )


class Arrows(Item):
    def __init__(self):
        super().__init__(
            "Arrows",
            rarity="common",
            category="ammunition",
            slots=1,
            description_text="A bundle of arrows.",
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
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
        )

class AlchemistsFire(Item):
    def __init__(self):
        super().__init__(
            "Alchemist's Fire",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
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
        )

class ArcaneFocus(Item):
    def __init__(self):
        super().__init__(
            "Arcane Focus",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
        )

class Barrel(Item):
    def __init__(self):
        super().__init__(
            "Barrel",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
        )

class BasicPoison(Item):
    def __init__(self):
        super().__init__(
            "Basic Poison",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
        )

class Basket(Item):
    def __init__(self):
        super().__init__(
            "Basket",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
        )

class Blanket(Item):
    def __init__(self):
        super().__init__(
            "Blanket",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
        )

class BlockAndTackle(Item):
    def __init__(self):
        super().__init__(
            "Block and Tackle",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
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
        )

class Bucket(Item):
    def __init__(self):
        super().__init__(
            "Bucket",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
        )

class Chain(Item):
    def __init__(self):
        super().__init__(
            "Chain",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
        )

class Chest(Item):
    def __init__(self):
        super().__init__(
            "Chest",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
        )

class ClimbersKit(Item):
    def __init__(self):
        super().__init__(
            "Climber's Kit",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
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
        )

class ComponentPouch(Item):
    def __init__(self):
        super().__init__(
            "Component Pouch",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
        )

class CrossbowBoltCase(Item):
    def __init__(self):
        super().__init__(
            "Crossbow Bolt Case",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
        )

class DruidicFocus(Item):
    def __init__(self):
        super().__init__(
            "Druidic Focus",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
        )

class FineClothes(Item):
    def __init__(self):
        super().__init__(
            "Fine Clothes",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
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
        )

class Flask(Item):
    def __init__(self):
        super().__init__(
            "Flask",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
        )

class GlassBottle(Item):
    def __init__(self):
        super().__init__(
            "Glass Bottle",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
        )

class GrapplingHook(Item):
    def __init__(self):
        super().__init__(
            "Grappling Hook",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
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
        )

class HolySymbol(Item):
    def __init__(self):
        super().__init__(
            "Holy Symbol",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
        )

class HuntingTrap(Item):
    def __init__(self):
        super().__init__(
            "Hunting Trap",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
        )

class Ink(Item):
    def __init__(self):
        super().__init__(
            "Ink",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
        )

class InkPen(Item):
    def __init__(self):
        super().__init__(
            "Ink Pen",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
        )

class IronPot(Item):
    def __init__(self):
        super().__init__(
            "Iron Pot",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
        )

class IronSpikes(Item):
    def __init__(self):
        super().__init__(
            "Iron Spikes",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
        )

class Jug(Item):
    def __init__(self):
        super().__init__(
            "Jug",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
        )

class Ladder(Item):
    def __init__(self):
        super().__init__(
            "Ladder",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
        )

class Lamp(Item):
    def __init__(self):
        super().__init__(
            "Lamp",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
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
        )

class Lock(Item):
    def __init__(self):
        super().__init__(
            "Lock",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
        )

class MagnifyingGlass(Item):
    def __init__(self):
        super().__init__(
            "Magnifying Glass",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
        )

class Manacles(Item):
    def __init__(self):
        super().__init__(
            "Manacles",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
        )

class Map(Item):
    def __init__(self):
        super().__init__(
            "Map",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
        )

class MapOrScrollCase(Item):
    def __init__(self):
        super().__init__(
            "Map or Scroll Case",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
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
        )

class MirrorPlaceholder(Item):
    def __init__(self):
        super().__init__(
            "Mirror",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
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
        )

class Net(Item):
    def __init__(self):
        super().__init__(
            "Net",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
        )

class Oil(Item):
    def __init__(self):
        super().__init__(
            "Oil",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
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
        )

class Paper(Item):
    def __init__(self):
        super().__init__(
            "Paper",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
        )

class Parchment(Item):
    def __init__(self):
        super().__init__(
            "Parchment",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
        )

class Perfume(Item):
    def __init__(self):
        super().__init__(
            "Perfume",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
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
        )

class Pole(Item):
    def __init__(self):
        super().__init__(
            "Pole",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
        )

class PortableRam(Item):
    def __init__(self):
        super().__init__(
            "Portable Ram",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
        )

class Pouch(Item):
    def __init__(self):
        super().__init__(
            "Pouch",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
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
        )

class Robe(Item):
    def __init__(self):
        super().__init__(
            "Robe",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
        )

class RopePlaceholder(Item):
    def __init__(self):
        super().__init__(
            "Rope",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
        )

class Sack(Item):
    def __init__(self):
        super().__init__(
            "Sack",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
        )

class Shovel(Item):
    def __init__(self):
        super().__init__(
            "Shovel",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
        )

class SignalWhistle(Item):
    def __init__(self):
        super().__init__(
            "Signal Whistle",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
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
        )

class SpellScroll(Item):
    def __init__(self):
        super().__init__(
            "Spell Scroll",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
        )

class Spyglass(Item):
    def __init__(self):
        super().__init__(
            "Spyglass",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
        )

class StringItem(Item):
    def __init__(self):
        super().__init__(
            "String",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
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
        )

class Tent(Item):
    def __init__(self):
        super().__init__(
            "Tent",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
        )

class TravelersClothes(Item):
    def __init__(self):
        super().__init__(
            "Traveler's Clothes",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
        )

class Vial(Item):
    def __init__(self):
        super().__init__(
            "Vial",
            rarity="common",
            category="placeholder",
            weight=None,
            slots=1,
            description_text="Placeholder item — full stats not yet defined.",
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
        )

