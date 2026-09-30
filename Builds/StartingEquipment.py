"""A character's Starting Equipment (and the gold left over after buying it),
worked out from the starting class's default gear and the build's choices.
Lives in the builder layer, not in Model/Inventory.py, because it has to
tell weapons from armor and make an Unarmed Strike - the model package never
imports CharacterContent at runtime."""

from typing import Optional

from CharacterContent.Items import Armor, Items, Packs, Weapons
from Core.Definitions import CharacterClass
from Model.Inventory import EquipmentEntry, Inventory

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


def set_starting_equipment(
    inventory: Inventory,
    base_class: CharacterClass,
    default_equipment: list[Weapons.AbstractWeapon | Armor.AbstractArmor],
    add_default_equipment: bool,
    default_pack: Optional[Packs.Pack] = None,
    armor: Optional[list[Armor.AbstractArmor]] = None,
    weapons: Optional[list[Weapons.AbstractWeapon]] = None,
    items: Optional[list[tuple[Items.Item, int]]] = None,
) -> EquipmentEntry:
    """Give `inventory` its Starting Equipment and starting gold. Call once
    per inventory - a second call raises."""
    unarmed_strike = None
    if not any(isinstance(w, Weapons.UnarmedStrike) for w in default_equipment):
        unarmed_strike = Weapons.UnarmedStrike(player_is_proficient=True)

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
        starting_gold=_BASELINE_STARTING_GOLD[base_class] - _entry_value(entry),
        unarmed_strike=unarmed_strike,
    )
    return entry
