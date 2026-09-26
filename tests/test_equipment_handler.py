"""
Builds/EquipmentHandler.py: starting gear, starting/current gold, adventuring
gear, dropping and consuming items.
"""

import pytest

from Builds.EquipmentHandler import Bought, EquipmentHandler
from CharacterContent.Items import Armor, Items, Packs, Weapons
from Core.Definitions import CharacterClass


def fighter_handler(**kwargs):
    handler = EquipmentHandler()
    defaults = dict(
        base_class=CharacterClass.FIGHTER,
        default_equipment=[],
        add_default_equipment=False,
    )
    defaults.update(kwargs)
    handler.set_starting_equipment(**defaults)
    return handler


class TestStartingEquipment:
    def test_no_gear_gets_full_starting_gold(self):
        assert fighter_handler().starting_gold == 155

    def test_gear_cost_is_deducted(self):
        handler = fighter_handler(
            weapons=[Weapons.Longsword()], armor=[Armor.LeatherArmor()]
        )
        assert handler.starting_gold == 155 - 15 - 10

    def test_pack_only_with_default_equipment(self):
        without = fighter_handler(default_pack=Packs.DungeoneersPack())
        assert without.items == []
        with_pack = fighter_handler(
            default_pack=Packs.DungeoneersPack(), add_default_equipment=True
        )
        assert with_pack.items

    def test_explicit_body_armor_replaces_default_but_keeps_shield(self):
        handler = fighter_handler(
            default_equipment=[Armor.ChainMailArmor(), Armor.ShieldArmor()],
            add_default_equipment=True,
            armor=[Armor.LeatherArmor()],
        )
        types = sorted(type(a).__name__ for a in handler.armors)
        assert types == ["LeatherArmor", "ShieldArmor"]

    def test_unarmed_strike_added_first_and_proficient(self):
        handler = fighter_handler(weapons=[Weapons.Dagger()])
        assert isinstance(handler.weapons[0], Weapons.UnarmedStrike)
        assert handler.weapons[0].player_is_proficient

    def test_default_unarmed_strike_not_duplicated(self):
        handler = fighter_handler(
            default_equipment=[Weapons.UnarmedStrike()], add_default_equipment=True
        )
        strikes = [w for w in handler.weapons if isinstance(w, Weapons.UnarmedStrike)]
        assert len(strikes) == 1

    def test_second_call_rejected(self):
        handler = fighter_handler()
        with pytest.raises(ValueError):
            handler.set_starting_equipment(CharacterClass.FIGHTER, [], False)


class TestGold:
    def test_found_items_are_free(self):
        handler = fighter_handler()
        handler.add_adventuring_gear("Loot", weapons=[Weapons.Rapier()])
        assert handler.current_gold == 155

    def test_bought_item_pays_catalog_value(self):
        handler = fighter_handler()
        handler.add_adventuring_gear("Shop", weapons=[Bought(Weapons.Rapier())])
        assert handler.current_gold == 155 - 25

    def test_bought_price_override(self):
        handler = fighter_handler()
        handler.add_adventuring_gear(
            "Haggled", weapons=[Bought(Weapons.Rapier(), price=20)]
        )
        assert handler.current_gold == 135

    def test_bought_stack_pays_per_unit_times_quantity(self):
        # Two potions at 50 GP each.
        handler = fighter_handler()
        handler.add_adventuring_gear(
            "Shop", items=[(Bought(Items.PotionOfHealing()), 2)]
        )
        assert handler.current_gold == 155 - 100

    def test_gold_deltas_accumulate(self):
        handler = fighter_handler()
        handler.add_adventuring_gear("Reward", gold=100)
        handler.add_adventuring_gear("Inn", gold=-5)
        assert handler.current_gold == 250
        assert handler.starting_gold == 155

    def test_dropping_bought_item_does_not_refund(self):
        handler = fighter_handler()
        rapier = Weapons.Rapier()
        handler.add_adventuring_gear("Shop", weapons=[Bought(rapier)])
        handler.drop_item(rapier)
        assert handler.current_gold == 130


class TestDropAndConsume:
    def test_drop_by_reference(self):
        sword = Weapons.Longsword()
        handler = fighter_handler(weapons=[sword, Weapons.Longsword()])
        handler.drop_item(sword)
        swords = [w for w in handler.weapons if isinstance(w, Weapons.Longsword)]
        assert len(swords) == 1 and swords[0] is not sword

    def test_drop_by_type_when_unique(self):
        handler = fighter_handler(weapons=[Weapons.Longsword()])
        handler.drop_item(Weapons.Longsword)
        assert not any(isinstance(w, Weapons.Longsword) for w in handler.weapons)

    def test_drop_by_type_ambiguous_raises(self):
        handler = fighter_handler(weapons=[Weapons.Dagger(), Weapons.Dagger()])
        with pytest.raises(ValueError):
            handler.drop_item(Weapons.Dagger)

    def test_drop_unarmed_strike(self):
        handler = fighter_handler()
        handler.drop_item(Weapons.UnarmedStrike)
        assert handler.weapons == []

    def test_get_starting_item_ignores_later_gear(self):
        handler = fighter_handler(weapons=[Weapons.Dagger()])
        handler.add_adventuring_gear("Loot", weapons=[Weapons.Dagger()])
        assert handler.get_starting_item(Weapons.Dagger) is (
            handler.starting_equipment_entry.weapons[0]
        )

    def test_consume_across_entries(self):
        handler = fighter_handler(items=[(Items.PotionOfHealing(), 2)])
        handler.add_adventuring_gear("Loot", items=[(Items.PotionOfHealing(), 3)])
        handler.consume_item(Items.PotionOfHealing, 3)
        assert [q for _, q in handler.items] == [2]
        assert handler.starting_equipment_entry.items == []

    def test_consume_more_than_owned_raises(self):
        handler = fighter_handler(items=[(Items.PotionOfHealing(), 1)])
        with pytest.raises(ValueError):
            handler.consume_item(Items.PotionOfHealing, 2)

    def test_items_merge_same_type_across_entries(self):
        handler = fighter_handler(items=[(Items.Torch(), 5)])
        handler.add_adventuring_gear("Loot", items=[(Items.Torch(), 3)])
        assert [q for _, q in handler.items] == [8]


class TestMisuseIsRejected:
    def test_drop_item_never_added(self):
        handler = fighter_handler()
        with pytest.raises(ValueError, match="Cannot drop"):
            handler.drop_item(Weapons.Longsword())

    def test_drop_same_item_twice(self):
        sword = Weapons.Longsword()
        handler = fighter_handler(weapons=[sword])
        handler.drop_item(sword)
        with pytest.raises(ValueError, match="Cannot drop"):
            handler.drop_item(sword)

    @pytest.mark.parametrize("quantity", [0, -1])
    def test_consume_non_positive_quantity(self, quantity):
        handler = fighter_handler(items=[(Items.PotionOfHealing(), 2)])
        with pytest.raises(ValueError, match="positive"):
            handler.consume_item(Items.PotionOfHealing, quantity)
