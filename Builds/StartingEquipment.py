"""A character's Starting Equipment (and the gold left over after buying it),
worked out from the starting class's default gear and the build's choices.
Lives in the builder layer, not in Model/Inventory.py, because it has to
tell weapons from armor and make an Unarmed Strike - the model package never
imports CharacterContent at runtime."""

from typing import Optional, Sequence

from CharacterContent.Items import Armor, Items, Packs, Weapons
from Core.Definitions import CharacterClass
from Model.Inventory import EquipmentEntry, Inventory
from Model.Content.Weapon import AbstractWeapon
from Model.Content.Armor import AbstractArmor
from Model.Content.Item import Item


def _entry_value(entry: EquipmentEntry) -> float:
    """Total GP value of everything in an entry."""
    total = sum(armor.value or 0 for armor in entry.armors)
    total += sum(weapon.value or 0 for weapon in entry.weapons)
    total += sum((item.value or 0) * quantity for item, quantity in entry.items)
    return total


def set_starting_equipment(
    inventory: Inventory,
    base_class: CharacterClass,
    default_equipment: Sequence[Weapons.AbstractWeapon | Armor.AbstractArmor],
    add_default_equipment: bool,
    default_pack: Optional[Packs.Pack] = None,
    armor: Optional[Sequence[Armor.AbstractArmor]] = None,
    weapons: Optional[Sequence[Weapons.AbstractWeapon]] = None,
    items: Optional[Sequence[tuple[Items.Item, int]]] = None,
) -> EquipmentEntry:
    """Give `inventory` its Starting Equipment and starting gold. Call once
    per inventory - a second call raises."""
    unarmed_strike = None
    if not any(isinstance(w, Weapons.UnarmedStrike) for w in default_equipment):
        unarmed_strike = Weapons.UnarmedStrike(player_is_proficient=True)

    starting_armor: list[AbstractArmor] = []
    starting_weapons: list[AbstractWeapon] = []
    starting_items: list[tuple[Item, int]] = []

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

    # The starting pack (Dungeoneer's, Explorer's, ...) is part of default
    # equipment and is only granted when add_default_equipment is True.
    if add_default_equipment and default_pack is not None:
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
    inventory.set_starting_equipment(
        entry,
        starting_gold=base_class.starting_gold - _entry_value(entry),
        unarmed_strike=unarmed_strike,
    )
    return entry
