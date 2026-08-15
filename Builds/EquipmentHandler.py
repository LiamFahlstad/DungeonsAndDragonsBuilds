"""Consolidated equipment/item handling for a character build.

Owns starting equipment, starting gold, adventuring gear picked up over
time, and dropping items - wired into CharacterBuilder, which seeds a
handler from its StarterClassBuilder and delegates add_adventuring_gear/
drop_item/get_starting_item to it. Also owns the EquipmentEntry/Bought
types: they live here (a leaf module with no dependency on
CharacterSheetAccumulator.py or the character sheet writer) rather than on
CharacterSheetData, specifically so CharacterSheetAccumulator.py,
CharacterSheetWriters.py, and CharacterStatBlock.py can all import them as
plain top-level imports instead of needing a TYPE_CHECKING-guarded one to
dodge a circular import.
"""

from typing import Optional

import attr

from CharacterContent.Items import Armor, Items, Packs, Weapons
from Core.Definitions import CharacterClass


class Bought:
    """Wrap an item passed to add_adventuring_gear() to mark it as
    purchased rather than found. Bought(item) pays the item's own catalog
    value; Bought(item, price=X) overrides the amount actually paid (e.g.
    haggled down, or a price the item's .value doesn't otherwise capture).
    Items left unwrapped are treated as found, not bought."""

    def __init__(
        self,
        item: Armor.AbstractArmor | Weapons.AbstractWeapon | Items.Item,
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
    armors: list[Armor.AbstractArmor] = attr.Factory(list)
    weapons: list[Weapons.AbstractWeapon] = attr.Factory(list)
    items: list[tuple[Items.Item, int]] = attr.Factory(list)
    # (item, amount paid) for every item added via Bought(...); an item with
    # no entry here was found rather than purchased. Matched by identity.
    purchases: list[tuple[Armor.AbstractArmor | Weapons.AbstractWeapon | Items.Item, float]] = (
        attr.Factory(list)
    )

# Each class's flat starting gold - the last "Choose A/B/..." alternative in
# its Starting Equipment line in SourceTexts/ClassTexts/<class>.txt (e.g.
# Fighter's "... or (C) 155 GP"), which is always gold with no items.
_BASELINE_STARTING_GOLD: dict[CharacterClass, float] = {
    CharacterClass.ARTIFICER: 150,
    CharacterClass.BARBARIAN: 75,
    CharacterClass.BARD: 90,
    CharacterClass.CLERIC: 110,
    CharacterClass.DRUID: 50,
    CharacterClass.FIGHTER: 155,
    CharacterClass.MONK: 50,
    CharacterClass.PALADIN: 150,
    CharacterClass.RANGER: 150,
    CharacterClass.ROGUE: 100,
    CharacterClass.SORCERER: 50,
    CharacterClass.WARLOCK: 100,
    CharacterClass.WIZARD: 55,
}


def _entry_value(entry: EquipmentEntry) -> float:
    """Total GP value of everything in an entry."""
    total = sum(armor.value or 0 for armor in entry.armors)
    total += sum(weapon.value or 0 for weapon in entry.weapons)
    total += sum((item.value or 0) * quantity for item, quantity in entry.items)
    return total


def _unwrap_bought(
    maybe_bought: Armor.AbstractArmor | Weapons.AbstractWeapon | Items.Item | Bought,
) -> tuple[Armor.AbstractArmor | Weapons.AbstractWeapon | Items.Item, Optional[float]]:
    if isinstance(maybe_bought, Bought):
        price = (
            maybe_bought.price
            if maybe_bought.price is not None
            else (maybe_bought.item.value or 0)
        )
        return maybe_bought.item, price
    return maybe_bought, None


class EquipmentHandler:
    """Owns everything item-related for a single character build: starting
    equipment, starting gold, adventuring gear picked up over time, and
    dropping items. Not yet wired into the build pipeline - see module
    docstring."""

    def __init__(self):
        self._entries: list[EquipmentEntry] = []
        self._starting_entry: Optional[EquipmentEntry] = None
        self._starting_gold: Optional[float] = None
        self._unarmed_strike: Optional[Weapons.UnarmedStrike] = None

    def set_starting_equipment(
        self,
        base_class: CharacterClass,
        default_equipment: list[Weapons.AbstractWeapon | Armor.AbstractArmor],
        add_default_equipment: bool,
        default_pack: Optional[Packs.Pack] = None,
        armor: Optional[list[Armor.AbstractArmor]] = None,
        weapons: Optional[list[Weapons.AbstractWeapon]] = None,
        items: Optional[list[tuple[Items.Item, int]]] = None,
    ) -> EquipmentEntry:
        """Set the character's starting gear and compute starting gold from
        it. Call once - a second call would silently overwrite starting_gold
        and risk double-adding the unarmed strike."""
        if self._starting_entry is not None:
            raise ValueError("set_starting_equipment() was already called.")

        if not any(isinstance(w, Weapons.UnarmedStrike) for w in default_equipment):
            self._unarmed_strike = Weapons.UnarmedStrike(player_is_proficient=True)

        starting_armor: list[Armor.AbstractArmor] = []
        starting_weapons: list[Weapons.AbstractWeapon] = []
        starting_items: list[tuple[Items.Item, int]] = []

        # Explicit body armor replaces the default one (a character can only
        # wear one armor at a time); default shields still apply.
        has_explicit_body_armor = any(not a.is_shield for a in (armor or []))
        if add_default_equipment:
            for equipment_item in default_equipment:
                if isinstance(equipment_item, Weapons.AbstractWeapon):
                    starting_weapons.append(equipment_item)
                elif isinstance(equipment_item, Armor.AbstractArmor):
                    if equipment_item.is_shield or not has_explicit_body_armor:
                        starting_armor.append(equipment_item)

        # The starting pack (Dungeoneer's, Explorer's, ...) is granted
        # regardless of add_default_equipment: a character always gets it,
        # even when the build picks its own weapons/armor instead of the
        # class's default equipment option.
        if default_pack is not None:
            starting_items.extend(default_pack.get_items())

        starting_armor.extend(armor or [])
        starting_weapons.extend(weapons or [])
        starting_items.extend(items or [])

        entry = EquipmentEntry(
            label="Starting Equipment",
            armors=starting_armor,
            weapons=starting_weapons,
            items=starting_items,
        )
        self._starting_entry = entry
        self._entries.append(entry)
        # Never clamp this toward zero here - that's a display-time concern.
        # (merge_with's scalar-merge rule treats a literal 0 as "unset" and
        # drops it, which matters once this gets threaded through
        # CharacterSheetData - not relevant to this standalone file today,
        # but easy to reintroduce by "fixing" a negative value in the wrong
        # place later.)
        self._starting_gold = _BASELINE_STARTING_GOLD[base_class] - _entry_value(entry)
        return entry

    def add_adventuring_gear(
        self,
        label: str,
        armor: Optional[list[Armor.AbstractArmor | Bought]] = None,
        weapons: Optional[list[Weapons.AbstractWeapon | Bought]] = None,
        items: Optional[list[tuple[Items.Item | Bought, int]]] = None,
    ) -> EquipmentEntry:
        """Record gear picked up after character creation as its own labeled
        entry, separate from Starting Equipment. Call as many times as
        needed, e.g. once per adventure. Items are found by default; wrap
        one in Bought(item) - or Bought(item, price=X) to override the
        amount paid - to mark it as purchased instead."""
        entry = EquipmentEntry(label=label)
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
                entry.purchases.append((unwrapped, price))
        self._entries.append(entry)
        return entry

    def get_starting_item(
        self, item_type: type
    ) -> Armor.AbstractArmor | Weapons.AbstractWeapon | Items.Item:
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

    def _find_item_by_type(
        self, item_type: type
    ) -> Armor.AbstractArmor | Weapons.AbstractWeapon | Items.Item:
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

    def drop_item(
        self, item: Armor.AbstractArmor | Weapons.AbstractWeapon | Items.Item | type
    ) -> None:
        """Remove a previously-added item so it no longer applies
        mechanically or shows on the sheet, while the code that added it
        stays in the build as a record of what the character used to carry.
        Pass either the exact object it was added with, or its class to look
        it up by type when there's exactly one instance of it anywhere -
        see get_starting_item() for a lookup scoped to starting gear only."""
        if isinstance(item, type):
            item = self._find_item_by_type(item)
        if self._unarmed_strike is item:
            self._unarmed_strike = None
        for entry in self._entries:
            entry.armors = [a for a in entry.armors if a is not item]
            entry.weapons = [w for w in entry.weapons if w is not item]
            entry.items = [(i, q) for i, q in entry.items if i is not item]

    @property
    def starting_equipment_entry(self) -> Optional[EquipmentEntry]:
        return self._starting_entry

    @property
    def equipment_entries(self) -> list[EquipmentEntry]:
        return list(self._entries)

    @property
    def armors(self) -> list[Armor.AbstractArmor]:
        return [a for entry in self._entries for a in entry.armors]

    @property
    def weapons(self) -> list[Weapons.AbstractWeapon]:
        weapons = [w for entry in self._entries for w in entry.weapons]
        if self._unarmed_strike is not None:
            weapons.insert(0, self._unarmed_strike)
        return weapons

    @property
    def items(self) -> list[tuple[Items.Item, int]]:
        """Same-type item stacks are merged across entries (matching
        CharacterSheetData.add_item), since that's what carrying-capacity
        math expects: the first-seen instance of a type absorbs later
        same-type quantities."""
        merged: list[tuple[Items.Item, int]] = []
        for entry in self._entries:
            for item, quantity in entry.items:
                for i, (existing_item, existing_quantity) in enumerate(merged):
                    if type(existing_item) is type(item):
                        merged[i] = (existing_item, existing_quantity + quantity)
                        break
                else:
                    merged.append((item, quantity))
        return merged

    @property
    def starting_gold(self) -> Optional[float]:
        return self._starting_gold
