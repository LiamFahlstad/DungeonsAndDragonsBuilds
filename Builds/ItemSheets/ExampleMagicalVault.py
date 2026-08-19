from CharacterContent.Items import Armor, Items, Weapons
from Utils.CharacterSheetWriters import HtmlCharacterSheetWriter


def generate_magical_vault_item_sheet():
    """Generate an example item sheet showing a collection of magical items."""
    writer = HtmlCharacterSheetWriter()

    armors = [
        Armor.PlateArmor(),
        Armor.ShieldArmor(),
    ]

    weapons = [
        Weapons.Greatsword(),
        Weapons.Rapier(),
    ]

    items = [
        (Items.PotionOfHealing(), 3),
        (Items.PotionOfInvisibility(), 1),
    ]

    writer.write_item_sheet(
        title="Magical Vault",
        output_path="Output/ItemSheets/MagicalVault.html",
        armors=armors,
        weapons=weapons,
        items=items,
    )
