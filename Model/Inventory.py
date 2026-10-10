"""A character's inventory: starting equipment, starting gold, adventuring
gear picked up over time, and dropping items.

Part of the Character model (Model/Character.py), so it imports nothing
from CharacterContent - armor, weapons and items are the base classes in
Model/Content/.
CharacterBuilder seeds an Inventory (Builds/StartingEquipment.py builds the
Starting Equipment entry) and delegates add_adventuring_gear/drop_item/
get_starting_item to it; build() hands each Character its own copy (in its
CharacterSources), whose armors/weapons/items are what AC, attacks and
carrying capacity read. A Character exposes only the reads.
"""

from __future__ import annotations

from typing import Generic, Optional, Sequence, TypeVar

import attr

from Model.Content.Weapon import AbstractWeapon
from Model.Content.Armor import AbstractArmor
from Model.Content.Item import Item

ItemT = TypeVar("ItemT", bound=Item)


class Bought(Generic[ItemT]):
    """Wrap an item passed to add_adventuring_gear() to mark it as
    purchased rather than found. Bought(item) pays the item's own catalog
    value; Bought(item, price=X) overrides the amount actually paid (e.g.
    haggled down, or a price the item's .value doesn't otherwise capture).
    Items left unwrapped are treated as found, not bought."""

    def __init__(
        self,
        item: ItemT,
        price: Optional[float] = None,
    ):
        self.item = item
        self.price = price


@attr.dataclass
class EquipmentEntry:
    """A labeled batch of gear acquired together (e.g. "Starting Equipment",
    "Found in the Goblin Warcamp"), so the sheet can show where a character's
    items came from instead of one undifferentiated pile."""

    label: str
    armors: list[AbstractArmor] = attr.Factory(list)
    weapons: list[AbstractWeapon] = attr.Factory(list)
    items: list[tuple[Item, int]] = attr.Factory(list)
    # (item, amount paid) for every item added via Bought(...); an item with
    # no entry here was found rather than purchased. Matched by identity.
    purchases: list[tuple[Item, float]] = attr.Factory(list)
    # Net GP gained (positive - loot, quest reward, sold something off the
    # sheet) or spent on a non-item cost (negative - lodging, bribes,
    # training) recorded directly on this entry, on top of whatever
    # Bought(...) purchases above already deduct.
    gold: float = 0


def _unwrap_bought(
    maybe_bought: ItemT | Bought[ItemT],
) -> tuple[ItemT, Optional[float]]:
    if isinstance(maybe_bought, Bought):
        price = (
            maybe_bought.price
            if maybe_bought.price is not None
            else (maybe_bought.item.value or 0)
        )
        return maybe_bought.item, price
    return maybe_bought, None


class Inventory:
    """Everything item-related for a single character: starting equipment,
    starting gold, adventuring gear picked up over time, and dropping
    items. The gear is grouped into labeled EquipmentEntry batches, so the
    sheet can show where each item came from; armors/weapons/items are the
    flat views everything else reads."""

    # Entry for gear added straight to a sheet (Character.add_armor
    # and friends) rather than through starting equipment or
    # add_adventuring_gear.
    OTHER_EQUIPMENT_LABEL = "Other Equipment"

    def __init__(self):
        self._entries: list[EquipmentEntry] = []
        self._starting_entry: Optional[EquipmentEntry] = None
        self._starting_gold: Optional[float] = None
        self._unarmed_strike: Optional[AbstractWeapon] = None
        self._other_entry: Optional[EquipmentEntry] = None

    def copy(self) -> "Inventory":
        """An independent Inventory holding the same gear: adding, dropping
        or consuming on either one never changes the other. The item objects
        themselves are shared - nothing changes an item once it's made
        (weapon bonuses are recorded on the stat block, see
        Model/Ledger/WeaponBonuses.py)."""
        copied = Inventory()
        for entry in self._entries:
            entry_copy = attr.evolve(
                entry,
                armors=list(entry.armors),
                weapons=list(entry.weapons),
                items=list(entry.items),
                purchases=list(entry.purchases),
            )
            copied._entries.append(entry_copy)
            if entry is self._starting_entry:
                copied._starting_entry = entry_copy
            if entry is self._other_entry:
                copied._other_entry = entry_copy
        copied._starting_gold = self._starting_gold
        copied._unarmed_strike = self._unarmed_strike
        return copied

    def _get_other_entry(self) -> EquipmentEntry:
        if self._other_entry is None:
            self._other_entry = EquipmentEntry(label=self.OTHER_EQUIPMENT_LABEL)
            self._entries.append(self._other_entry)
        return self._other_entry

    def add_armor(self, armor: AbstractArmor) -> None:
        self._get_other_entry().armors.append(armor)

    def add_weapon(self, weapon: AbstractWeapon) -> None:
        self._get_other_entry().weapons.append(weapon)

    def add_item(self, item: Item, quantity: int = 1) -> None:
        self._get_other_entry().items.append((item, quantity))

    def set_starting_equipment(
        self,
        entry: EquipmentEntry,
        starting_gold: float,
        unarmed_strike: Optional[AbstractWeapon],
    ) -> None:
        """Set the Starting Equipment entry, the gold left over after buying
        it, and the Unarmed Strike every character has unless its starting
        gear already holds one (see Builds/StartingEquipment.py, which works
        all three out). Call once."""
        if self._starting_entry is not None:
            raise ValueError("set_starting_equipment() was already called.")
        self._unarmed_strike = unarmed_strike
        self._starting_entry = entry
        self._entries.append(entry)
        # Never clamp this toward zero here - that's a display-time concern.
        self._starting_gold = starting_gold

    def add_adventuring_gear(
        self,
        label: str,
        armor: Optional[Sequence[AbstractArmor | Bought[AbstractArmor]]] = None,
        weapons: Optional[Sequence[AbstractWeapon | Bought[AbstractWeapon]]] = None,
        items: Optional[Sequence[tuple[Item | Bought[Item], int]]] = None,
        gold: float = 0,
    ) -> EquipmentEntry:
        """Record gear picked up after character creation as its own labeled
        entry, separate from Starting Equipment. Call as many times as
        needed, e.g. once per adventure. Items are found by default; wrap
        one in Bought(item) - or Bought(item, price=X) to override the
        amount paid - to mark it as purchased instead. Pass gold=X for a
        net GP change from this entry that isn't tied to a specific item
        (loot found, a cost paid) - positive gains, negative spends."""
        entry = EquipmentEntry(label=label, gold=gold)
        for a in armor or []:
            unwrapped, price = _unwrap_bought(a)
            entry.armors.append(unwrapped)
            if price is not None:
                entry.purchases.append((unwrapped, price))
        for w in weapons or []:
            unwrapped, price = _unwrap_bought(w)
            entry.weapons.append(unwrapped)
            if price is not None:
                entry.purchases.append((unwrapped, price))
        for raw_item, quantity in items or []:
            unwrapped, price = _unwrap_bought(raw_item)
            entry.items.append((unwrapped, quantity))
            if price is not None:
                # Catalog value is per unit; an explicit
                # Bought(price=X) is the total actually paid for the stack.
                if isinstance(raw_item, Bought) and raw_item.price is None:
                    price *= quantity
                entry.purchases.append((unwrapped, price))
        self._entries.append(entry)
        return entry

    def get_starting_item(self, item_type: type) -> Item:
        """Look up a single starting-equipment item by class, for a later
        drop_item() call. Stays unambiguous no matter how much later
        adventuring gear introduces more items of the same class, since it
        only ever looks at Starting Equipment."""
        if self._starting_entry is None:
            raise ValueError("set_starting_equipment() must be called first.")
        matches = [a for a in self._starting_entry.armors if type(a) is item_type]
        matches += [w for w in self._starting_entry.weapons if type(w) is item_type]
        matches += [
            i for i, _quantity in self._starting_entry.items if type(i) is item_type
        ]
        if not matches:
            raise ValueError(f"No {item_type.__name__} found in starting equipment.")
        if len(matches) > 1:
            raise ValueError(
                f"{len(matches)} {item_type.__name__} instances found in starting "
                "equipment - pass the exact object reference instead."
            )
        return matches[0]

    def _find_item_by_type(self, item_type: type) -> Item:
        """Resolve an item class to the single matching instance across
        everything (starting gear, all adventuring gear, and the unarmed
        strike)."""
        matches = [a for a in self.armors if type(a) is item_type]
        matches += [w for w in self.weapons if type(w) is item_type]
        matches += [i for i, _quantity in self.items if type(i) is item_type]
        if not matches:
            raise ValueError(f"No {item_type.__name__} found to drop.")
        if len(matches) > 1:
            raise ValueError(
                f"{len(matches)} {item_type.__name__} instances found - "
                "pass the exact object reference to drop_item() instead of the class."
            )
        return matches[0]

    def drop_item(self, item: Item | type) -> None:
        """Remove a previously-added item so it no longer applies
        mechanically or shows on the sheet, while the code that added it
        stays in the build as a record of what the character used to carry.
        Pass either the exact object it was added with, or its class to look
        it up by type when there's exactly one instance of it anywhere -
        see get_starting_item() for a lookup scoped to starting gear only."""
        if isinstance(item, type):
            item = self._find_item_by_type(item)
        if not any(owned is item for owned in self._all_gear()):
            raise ValueError(
                f"Cannot drop {item.name!r}: it isn't in this "
                "character's equipment (already dropped, or never added?)."
            )
        if self._unarmed_strike is item:
            self._unarmed_strike = None
        for entry in self._entries:
            entry.armors = [a for a in entry.armors if a is not item]
            entry.weapons = [w for w in entry.weapons if w is not item]
            entry.items = [(i, q) for i, q in entry.items if i is not item]

    def _all_gear(self) -> list[Item]:
        """Every armor, weapon and item instance in every entry, plus the
        Unarmed Strike (unstacked: one entry per instance added)."""
        gear: list[Item] = []
        if self._unarmed_strike is not None:
            gear.append(self._unarmed_strike)
        for entry in self._entries:
            gear.extend(entry.armors)
            gear.extend(entry.weapons)
            gear.extend(item for item, _quantity in entry.items)
        return gear

    def consume_item(self, item_type: type, quantity: int = 1) -> None:
        """Reduce a stackable item's quantity (use 1 of 5 potions, fire 3 of
        20 arrows) instead of dropping the whole stack. Decrements from
        whichever entries hold it, in the order they were added, removing an
        entry's row entirely once its share hits zero. Raises ValueError if
        fewer than `quantity` are owned anywhere."""
        if quantity < 1:
            raise ValueError(f"Can only consume a positive quantity, got {quantity}.")
        total_owned = sum(q for i, q in self.items if type(i) is item_type)
        if total_owned < quantity:
            raise ValueError(
                f"Only {total_owned} {item_type.__name__} owned, cannot consume {quantity}."
            )
        remaining = quantity
        for entry in self._entries:
            if remaining <= 0:
                break
            new_items = []
            for item, q in entry.items:
                if remaining > 0 and type(item) is item_type:
                    take = min(q, remaining)
                    remaining -= take
                    if q - take > 0:
                        new_items.append((item, q - take))
                else:
                    new_items.append((item, q))
            entry.items = new_items

    @property
    def starting_equipment_entry(self) -> Optional[EquipmentEntry]:
        return self._starting_entry

    @property
    def equipment_entries(self) -> list[EquipmentEntry]:
        return list(self._entries)

    @property
    def armors(self) -> list[AbstractArmor]:
        return [a for entry in self._entries for a in entry.armors]

    @property
    def weapons(self) -> list[AbstractWeapon]:
        weapons = [w for entry in self._entries for w in entry.weapons]
        if self._unarmed_strike is not None:
            weapons.insert(0, self._unarmed_strike)
        return weapons

    @property
    def items(self) -> list[tuple[Item, int]]:
        """Same-type item stacks are merged across entries, since that's what
        carrying-capacity math expects: the first-seen instance of a type
        absorbs later same-type quantities."""
        first_of_type: dict[type, Item] = {}
        quantity_of_type: dict[type, int] = {}
        for entry in self._entries:
            for item, quantity in entry.items:
                item_type = type(item)
                if item_type not in first_of_type:
                    first_of_type[item_type] = item
                    quantity_of_type[item_type] = 0
                quantity_of_type[item_type] += quantity
        return [
            (item, quantity_of_type[item_type])
            for item_type, item in first_of_type.items()
        ]

    @property
    def starting_gold(self) -> Optional[float]:
        return self._starting_gold

    @property
    def current_gold(self) -> Optional[float]:
        """Starting gold, plus every add_adventuring_gear(gold=...) delta
        since, minus every Bought(...) purchase price recorded since - the
        character's running GP total. Starting Equipment's own cost is
        already netted out of starting_gold, so it contributes 0 here."""
        if self._starting_gold is None:
            return None
        total = self._starting_gold
        for entry in self._entries:
            total += entry.gold
            total -= sum(price for _item, price in entry.purchases)
        return total
