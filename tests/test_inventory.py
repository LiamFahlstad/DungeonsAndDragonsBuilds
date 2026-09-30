"""
Model/Inventory.py and Builds/StartingEquipment.py: starting gear,
starting/current gold, adventuring gear, dropping and consuming items.
"""

import pytest

from Builds.StartingEquipment import set_starting_equipment
from Model.Inventory import Bought, Inventory
from CharacterContent.Items import Armor, Items, Packs, Weapons
from Core.Definitions import CharacterClass


def fighter_inventory(**kwargs):
    inventory = Inventory()
    defaults = dict(
        base_class=CharacterClass.FIGHTER,
        default_equipment=[],
        add_default_equipment=False,
    )
    defaults.update(kwargs)
    set_starting_equipment(inventory, **defaults)
    return inventory


class TestStartingEquipment:
    def test_no_gear_gets_full_starting_gold(self):
        assert fighter_inventory().starting_gold == 155

    def test_gear_cost_is_deducted(self):
        inventory = fighter_inventory(
            weapons=[Weapons.Longsword()], armor=[Armor.LeatherArmor()]
        )
        assert inventory.starting_gold == 155 - 15 - 10

    def test_pack_only_with_default_equipment(self):
        without = fighter_inventory(default_pack=Packs.DungeoneersPack())
        assert without.items == []
        with_pack = fighter_inventory(
            default_pack=Packs.DungeoneersPack(), add_default_equipment=True
        )
        assert with_pack.items

    def test_explicit_body_armor_replaces_default_but_keeps_shield(self):
        inventory = fighter_inventory(
            default_equipment=[Armor.ChainMailArmor(), Armor.ShieldArmor()],
            add_default_equipment=True,
            armor=[Armor.LeatherArmor()],
        )
        types = sorted(type(a).__name__ for a in inventory.armors)
        assert types == ["LeatherArmor", "ShieldArmor"]

    def test_unarmed_strike_added_first_and_proficient(self):
        inventory = fighter_inventory(weapons=[Weapons.Dagger()])
        assert isinstance(inventory.weapons[0], Weapons.UnarmedStrike)
        assert inventory.weapons[0].player_is_proficient

    def test_default_unarmed_strike_not_duplicated(self):
        inventory = fighter_inventory(
            default_equipment=[Weapons.UnarmedStrike()], add_default_equipment=True
        )
        strikes = [w for w in inventory.weapons if isinstance(w, Weapons.UnarmedStrike)]
        assert len(strikes) == 1

    def test_second_call_rejected(self):
        inventory = fighter_inventory()
        with pytest.raises(ValueError):
            set_starting_equipment(inventory, CharacterClass.FIGHTER, [], False)


class TestGold:
    def test_found_items_are_free(self):
        inventory = fighter_inventory()
        inventory.add_adventuring_gear("Loot", weapons=[Weapons.Rapier()])
        assert inventory.current_gold == 155

    def test_bought_item_pays_catalog_value(self):
        inventory = fighter_inventory()
        inventory.add_adventuring_gear("Shop", weapons=[Bought(Weapons.Rapier())])
        assert inventory.current_gold == 155 - 25

    def test_bought_price_override(self):
        inventory = fighter_inventory()
        inventory.add_adventuring_gear(
            "Haggled", weapons=[Bought(Weapons.Rapier(), price=20)]
        )
        assert inventory.current_gold == 135

    def test_bought_stack_pays_per_unit_times_quantity(self):
        # Two potions at 50 GP each.
        inventory = fighter_inventory()
        inventory.add_adventuring_gear(
            "Shop", items=[(Bought(Items.PotionOfHealing()), 2)]
        )
        assert inventory.current_gold == 155 - 100

    def test_gold_deltas_accumulate(self):
        inventory = fighter_inventory()
        inventory.add_adventuring_gear("Reward", gold=100)
        inventory.add_adventuring_gear("Inn", gold=-5)
        assert inventory.current_gold == 250
        assert inventory.starting_gold == 155

    def test_dropping_bought_item_does_not_refund(self):
        inventory = fighter_inventory()
        rapier = Weapons.Rapier()
        inventory.add_adventuring_gear("Shop", weapons=[Bought(rapier)])
        inventory.drop_item(rapier)
        assert inventory.current_gold == 130


class TestDropAndConsume:
    def test_drop_by_reference(self):
        sword = Weapons.Longsword()
        inventory = fighter_inventory(weapons=[sword, Weapons.Longsword()])
        inventory.drop_item(sword)
        swords = [w for w in inventory.weapons if isinstance(w, Weapons.Longsword)]
        assert len(swords) == 1 and swords[0] is not sword

    def test_drop_by_type_when_unique(self):
        inventory = fighter_inventory(weapons=[Weapons.Longsword()])
        inventory.drop_item(Weapons.Longsword)
        assert not any(isinstance(w, Weapons.Longsword) for w in inventory.weapons)

    def test_drop_by_type_ambiguous_raises(self):
        inventory = fighter_inventory(weapons=[Weapons.Dagger(), Weapons.Dagger()])
        with pytest.raises(ValueError):
            inventory.drop_item(Weapons.Dagger)

    def test_drop_unarmed_strike(self):
        inventory = fighter_inventory()
        inventory.drop_item(Weapons.UnarmedStrike)
        assert inventory.weapons == []

    def test_get_starting_item_ignores_later_gear(self):
        inventory = fighter_inventory(weapons=[Weapons.Dagger()])
        inventory.add_adventuring_gear("Loot", weapons=[Weapons.Dagger()])
        assert inventory.get_starting_item(Weapons.Dagger) is (
            inventory.starting_equipment_entry.weapons[0]
        )

    def test_consume_across_entries(self):
        inventory = fighter_inventory(items=[(Items.PotionOfHealing(), 2)])
        inventory.add_adventuring_gear("Loot", items=[(Items.PotionOfHealing(), 3)])
        inventory.consume_item(Items.PotionOfHealing, 3)
        assert [q for _, q in inventory.items] == [2]
        assert inventory.starting_equipment_entry.items == []

    def test_consume_more_than_owned_raises(self):
        inventory = fighter_inventory(items=[(Items.PotionOfHealing(), 1)])
        with pytest.raises(ValueError):
            inventory.consume_item(Items.PotionOfHealing, 2)

    def test_items_merge_same_type_across_entries(self):
        inventory = fighter_inventory(items=[(Items.Torch(), 5)])
        inventory.add_adventuring_gear("Loot", items=[(Items.Torch(), 3)])
        assert [q for _, q in inventory.items] == [8]


class TestMisuseIsRejected:
    def test_drop_item_never_added(self):
        inventory = fighter_inventory()
        with pytest.raises(ValueError, match="Cannot drop"):
            inventory.drop_item(Weapons.Longsword())

    def test_drop_same_item_twice(self):
        sword = Weapons.Longsword()
        inventory = fighter_inventory(weapons=[sword])
        inventory.drop_item(sword)
        with pytest.raises(ValueError, match="Cannot drop"):
            inventory.drop_item(sword)

    @pytest.mark.parametrize("quantity", [0, -1])
    def test_consume_non_positive_quantity(self, quantity):
        inventory = fighter_inventory(items=[(Items.PotionOfHealing(), 2)])
        with pytest.raises(ValueError, match="positive"):
            inventory.consume_item(Items.PotionOfHealing, quantity)


class TestCopy:
    def test_copy_has_the_same_gear_and_gold(self):
        inventory = fighter_inventory(weapons=[Weapons.Dagger()])
        inventory.add_adventuring_gear("Shop", weapons=[Bought(Weapons.Rapier())])
        copied = inventory.copy()
        assert copied.weapons == inventory.weapons
        assert copied.current_gold == inventory.current_gold
        assert copied.starting_equipment_entry is copied.equipment_entries[0]

    def test_changes_to_either_never_reach_the_other(self):
        dagger = Weapons.Dagger()
        inventory = fighter_inventory(weapons=[dagger])
        copied = inventory.copy()
        inventory.drop_item(dagger)
        copied.add_adventuring_gear("Loot", weapons=[Weapons.Rapier()])
        assert dagger in copied.weapons
        assert not any(isinstance(w, Weapons.Rapier) for w in inventory.weapons)


class TestOtherEquipment:
    def test_direct_adds_share_one_other_equipment_entry(self):
        inventory = fighter_inventory()
        sword, torch = Weapons.Longsword(), Items.Torch()
        inventory.add_weapon(sword)
        inventory.add_item(torch, 2)
        other = inventory.equipment_entries[-1]
        assert other.label == Inventory.OTHER_EQUIPMENT_LABEL
        assert other.weapons == [sword] and other.items == [(torch, 2)]
        assert len(inventory.equipment_entries) == 2
