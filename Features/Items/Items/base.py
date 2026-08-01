from enum import Enum
from typing import Optional
from Features.Core.BaseFeatures import Feature
from Features.Core.Improvements import ItemImprovement, CharacterImprovement
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class ItemRarity(str, Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    VERY_RARE = "very rare"
    LEGENDARY = "legendary"
    ARTIFACT = "artifact"


class ItemCategory(str, Enum):
    ADVENTURING_GEAR = "adventuring gear"
    AMMUNITION = "ammunition"
    ARMOR = "armor"
    CLOTHING = "clothing"
    COMMON = "common"
    CONSUMABLE = "consumable"
    CONTAINER = "container"
    CURRENCY = "currency"
    FOCUS = "focus"
    GEAR = "gear"
    MUSICAL_INSTRUMENT = "musical instrument"
    PLACEHOLDER = "placeholder"
    RING = "ring"
    TOOL = "tool"
    UTILITY = "utility"
    WEAPON = "weapon"
    WONDROUS = "wondrous"
    WONDROUS_ITEM = "wondrous item"


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
        construction time - the same kind RingOfIntelligence passes via
        `improvements=`, but composable at the class level. Call from
        base_stats() (or setup_improvements()) to distinguish "this affects
        the wielder/wearer" from add_weapon_improvement/add_armor_improvement,
        which affect the item itself. Requires self.character_improvements
        to already exist (see AbstractWeapon / AbstractArmor, which
        initialize it before calling base_stats())."""
        self.character_improvements.append(improvement)


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
        rarity: ItemRarity = ItemRarity.COMMON,
        category: ItemCategory = ItemCategory.CONSUMABLE,
        weight: Optional[float] = None,
        slots: int = 1,
        description_text: str = "",
        improvements: Optional[list[CharacterImprovement]] = None,
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
            improvements=improvements,
            is_homebrew=is_homebrew,
            value=value,
        )
        # Consumables are typically never attuned
        self.requires_attunement = False


# ══════════════════════════════════════════════════════════════════════════════
# Simple Description-Only Items
# ══════════════════════════════════════════════════════════════════════════════
