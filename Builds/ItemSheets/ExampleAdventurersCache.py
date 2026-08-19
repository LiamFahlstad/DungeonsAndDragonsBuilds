from CharacterContent.Items import Armor, Items, Weapons
from Utils.CharacterSheetWriters import HtmlCharacterSheetWriter


def generate_adventurers_cache_item_sheet():
    """Generate an example item sheet showing a typical adventurer's collection."""
    writer = HtmlCharacterSheetWriter()

    armors = [
        Armor.LeatherArmor(),
        Armor.ChainMailArmor(),
    ]

    weapons = [
        Weapons.Longsword(),
        Weapons.Longbow(),
        Weapons.Dagger(),
    ]

    items = [
        (Items.Bedroll(), 1),
        (Items.Rope(), 1),
        (Items.Torch(), 5),
        (Items.Waterskin(), 2),
        (Items.Backpack(), 1),
    ]

    writer.write_item_sheet(
        title="Adventurer's Cache",
        output_path="Output/ItemSheets/AdventurersCache.html",
        armors=armors,
        weapons=weapons,
        items=items,
    )
