from enum import Enum
from typing import Optional

from CharacterContent.Features.Core.BaseFeatures import Feature
from CharacterContent.Features.Core.Improvements import (
    CharacterImprovement,
    ItemImprovement,
)
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class ItemRarity(str, Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    VERY_RARE = "very rare"
    LEGENDARY = "legendary"
    ARTIFACT = "artifact"


class ItemCategory(str, Enum):
    ADVENTURING_GEAR = "adventuring gear"  # general exploration and survival equipment
    AMMUNITION = "ammunition"  # arrows, bolts, bullets, and other ranged ammo
    ARMOR = "armor"  # wearable armor
    CARRYING_GEAR = "carrying gear"  # worn items that increase carrying capacity
    CLOTHING = "clothing"  # mundane, non-armor garments
    COMMON = "common"  # items of no particular interest like paper and pen
    CONTAINER = "container"  # bags, sacks, and other things that hold items
    CURRENCY = "currency"  # coins and other forms of money
    MUSICAL_INSTRUMENT = "musical instrument"  # instruments for playing music
    POISON = "poison"  # substances applied to weapons or ammunition
    POTION = "potion"  # drinkable magical liquids
    SCROLL = "scroll"  # single-use spell scrolls
    SPELL_FOCUS = "spell focus"  # spellcasting focuses and component pouches
    TOOL = "tool"  # tools and kits used for skill checks or crafting
    TRINKETS = "trinkets"  # rings, necklaces, and other small wearable curios
    WEAPON = "weapon"  # melee and ranged weapons
    WONDROUS = "wondrous"  # magical items


class Item(Feature):
    """
    Base class for all items. Items are now Features, allowing them to be
    either description-only or to modify a character via CharacterImprovements.

    An item has metadata (rarity, attunement, category, weight, slots, value,
    homebrew status) and can:
    - Provide a description via get_description()
    - Apply mechanical effects via improvements and apply()
    - Take up carrying capacity slots

    is_wearing is None for items with no wearable concept at all (most
    items); it's a real bool for items that must be worn/wielded for their
    improvements to apply (weapons, armor, rings, cloaks, ...) - see
    AbstractWeapon/AbstractArmor and the is_wearing-accepting items below.
    """

    def __init__(
        self,
        name: str,
        rarity: ItemRarity = ItemRarity.COMMON,
        requires_attunement: bool = False,
        category: ItemCategory = ItemCategory.WONDROUS,
        weight: Optional[float] = None,
        slots: int = 1,
        description_text: str = "",
        improvements: Optional[list[CharacterImprovement]] = None,
        is_homebrew: bool = True,
        value: Optional[float] = None,
        is_wearing: Optional[bool] = None,
        is_consumable: bool = False,
    ):
        # Populated by subclasses that compose CharacterImprovements before
        # calling Item.__init__ (see AbstractWeapon, AbstractArmor) - not
        # assigned here since add_character_improvement() must work during
        # their base_stats()/setup_improvements(), which run before this
        # __init__; the annotation alone tells the type checker it exists.
        self.character_improvements: list[CharacterImprovement]
        super().__init__(name=name, origin=category)
        self.rarity = rarity
        self.requires_attunement = requires_attunement
        self.category = category
        self.weight = weight
        self.slots = slots
        self.description_text = description_text
        self.improvements = improvements or []
        self.is_homebrew = is_homebrew
        # Value in gold pieces (GP). None means unknown/unpriced and should
        # not be displayed.
        self.value = value
        self.is_wearing = is_wearing
        self.is_consumable = is_consumable

    def apply(self, character_stat_block: CharacterStatBlock):
        """Apply all improvements to the character - unless this is a
        wearable item currently not being worn."""
        if self.is_wearing is False:
            return
        for improvement in self.improvements:
            improvement.apply(character_stat_block)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str | None:
        """Return the item description. Subclasses can override for a description
        that depends on the character (e.g. scaling with level or ability scores)."""
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

    def add_improvement(self, improvement: ItemImprovement) -> None:
        """Apply a single ItemImprovement to this item. This is the generic,
        low-level access point every type-specific improvement method
        (AbstractWeapon.add_weapon_improvement, AbstractArmor.add_armor_improvement,
        ...) delegates to; prefer those clearer, item-type-specific names
        over calling this directly."""
        improvement.apply(self)

    def setup_improvements(self) -> None:
        """Override to bake in this item's default improvements, e.g.:

            def setup_improvements(self) -> None:
                self.add_weapon_improvement(Reskin("Frostbrand Blade", "..."))

        Called once during __init__, after any improvements passed in via
        the subclass's own improvement-list constructor parameter (e.g.
        AbstractWeapon's `weapon_improvements=`, AbstractArmor's
        `armor_improvements=`). Only meaningful for items that compose
        ItemImprovements (see AbstractWeapon, AbstractArmor)."""

    def add_character_improvement(self, improvement: CharacterImprovement) -> None:
        """Attach a CharacterImprovement to this item at
        construction time - the same kind RingOfIntellect passes via
        `improvements=`, but composable at the class level. Call from
        base_stats() (or setup_improvements()) to distinguish "this affects
        the wielder/wearer" from add_weapon_improvement/add_armor_improvement,
        which affect the item itself. Requires self.character_improvements
        to already exist (see AbstractWeapon / AbstractArmor, which
        initialize it before calling base_stats())."""
        self.character_improvements.append(improvement)


# ══════════════════════════════════════════════════════════════════════════════
# Simple Description-Only Items
# ══════════════════════════════════════════════════════════════════════════════
