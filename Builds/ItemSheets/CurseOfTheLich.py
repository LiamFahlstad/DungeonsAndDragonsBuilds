from CharacterContent.Items import Armor, Items, Weapons
from CharacterContent.Items.Weapons.MartialMelee import Scimitar
from CharacterContent.Items.Weapons.Ranged import HandCrossbow
from CharacterContent.Spells import SpellLists
from Utils.CharacterSheetWriters import HtmlCharacterSheetWriter


def generate_stonehill_armory_upgrade_item_sheet():
    """Generate item sheet for the party's Stonehill Armory Upgrade gear."""
    writer = HtmlCharacterSheetWriter()

    armors = [
        Armor.BreastplateArmor(),  # Obmar
        Armor.BreastplateArmor(),  # Clover
        Armor.BreastplateArmor(),  # Gabriel
        Armor.SplintArmor(),  # Edmund
        Armor.StuddedLeatherArmor(),  # Thum
    ]

    weapons = [
        Weapons.LightHammer(),  # Obmar
        Weapons.Scimitar(),  # Clover
        Weapons.Longbow(),  # Clover
        Weapons.Quarterstaff(),  # Gabriel
        Weapons.LightCrossbow(),  # Gabriel
        Weapons.Handaxe(),  # Edmund
        Weapons.Greatsword(),  # Edmund
        Weapons.Longbow(),  # Edmund
        Scimitar(),  # Thum
        HandCrossbow(),  # Thum
        HandCrossbow(),  # Thum
    ]

    items = [
        (Items.PotionOfHealing(), 2),  # Kivi
        (Items.PotionOfInvisibility(), 1),  # Kivi
        (Items.PotionOfSpeed(), 1),  # Kivi
        (Items.PotionOfResistance(), 1),  # Kivi
        (Items.Scroll(SpellLists.AbjurationLevel1Spells.HEALING_WORD), 1),  # Kivi
        (Items.Scroll(SpellLists.ConjurationLevel2Spells.MISTY_STEP), 1),  # Kivi
    ]

    writer.write_item_sheet(
        title="Stonehill Armory Upgrade",
        output_path="Output/ItemSheets/CurseOfTheLich/StonehillArmoryUpgrade.html",
        armors=armors,
        weapons=weapons,
        items=items,
    )


def generate_adventure_to_ashelm_item_sheet():
    """Generate item sheet for the party's Adventure to Ashelm gear."""
    writer = HtmlCharacterSheetWriter()

    weapons = [
        Weapons.SulvesburgsFolly(),  # Obmar
        Weapons.ModarinsWrath(),  # Gabriel
        Weapons.AHushedBell(),  # Edmund
        Weapons.HalflingssTrick(),  # Thum
    ]

    items = [
        (Items.MirinelsBootsOfElvenSpeed(), 1),  # Clover
        (Items.CurseEnergyBandage(), 1),  # Kivi
    ]

    writer.write_item_sheet(
        title="Adventure to Ashelm",
        output_path="Output/ItemSheets/CurseOfTheLich/AdventureToAshelm.html",
        weapons=weapons,
        items=items,
    )


def generate_starting_equipment_item_sheet():
    """Generate item sheet for the party's starting equipment."""
    writer = HtmlCharacterSheetWriter()

    armors = [
        Armor.StuddedLeatherArmor(),  # Obmar
        Armor.ShieldArmor(),  # Obmar
        Armor.LeatherArmor(),  # Clover
        Armor.ShieldArmor(),  # Clover
        Armor.ChainShirtArmor(),  # Gabriel
        Armor.ShieldArmor(),  # Gabriel
        Armor.ChainMailArmor(),  # Edmund
        Armor.ShieldArmor(),  # Edmund
        Armor.LeatherArmor(),  # Thum
    ]

    weapons = [
        Weapons.Dagger(),  # Obmar
        Weapons.Spear(),  # Obmar
        Weapons.Shortsword(),  # Clover
        Weapons.Mace(),  # Gabriel
        Weapons.Dagger(),  # Kivi
        Weapons.Longsword(),  # Edmund
        Weapons.Dagger(),  # Edmund
        Weapons.Dagger(),  # Thum
        Weapons.Shortsword(),  # Thum
    ]

    items = [
        (Items.Backpack(), 1),  # Clover
        (Items.Bell(), 1),  # Clover
        (Items.Costume(), 1),  # Clover
        (Items.Mirror(), 1),  # Clover
        (Items.FlasksOfOil(), 1),  # Clover
        (Items.Rations(), 3),  # Clover
        (Items.Tinderbox(), 1),  # Clover
        (Items.Waterskin(), 1),  # Clover
        (Items.Backpack(), 1),  # Kivi
        (Items.Bedroll(), 1),  # Kivi
        (Items.FlasksOfOil(), 2),  # Kivi
        (Items.Rations(), 10),  # Kivi
        (Items.Rope(), 1),  # Kivi
        (Items.Tinderbox(), 1),  # Kivi
        (Items.Torch(), 10),  # Kivi
        (Items.Waterskin(), 1),  # Kivi
        (Items.Drum(), 1),  # Kivi
        (Items.HolySymbol(), 1),  # Edmund
        (Items.Bedroll(), 1),  # Edmund
        (Items.Tinderbox(), 1),  # Edmund
        (Items.NavigatorsTools(), 1),  # Edmund
        (Items.InkPen(), 1),  # Edmund
        (Items.Paper(), 1),  # Edmund
        (Items.Map(), 1),  # Edmund
        (Items.Rations(), 3),  # Edmund
        (Items.Backpack(), 1),  # Thum
        (Items.Map(), 1),  # Thum
        (Items.Rations(), 1),  # Thum
        (Items.Gold(), 38),  # Thum
        (Items.Silver(), 5),  # Thum
    ]

    writer.write_item_sheet(
        title="Starting Equipment",
        output_path="Output/ItemSheets/CurseOfTheLich/StartingEquipment.html",
        armors=armors,
        weapons=weapons,
        items=items,
    )
