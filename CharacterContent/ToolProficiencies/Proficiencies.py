from typing import Optional

from Core.Definitions import Ability
from CharacterContent.Features.Core.BaseFeatures import Feature
from CharacterContent.Items import Armor, Weapons
from CharacterContent.Items import Items
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class ToolProficiency(Feature):
    """Represents training with a tool, not the tool itself - see the
    matching class in CharacterContent.Items.Items for the tool's weight,
    cost, and what it physically does. This grants your proficiency bonus
    on ability checks made with the tool and, where listed, the ability to
    craft certain items with it during downtime."""

    def __init__(
        self,
        name: str,
        category: str,
        ability: Ability,
        craftables: Optional[list[Items.Item]] = None,
    ):
        super().__init__(name=name)
        self.category = category
        self.ability = ability
        self.craftables = craftables if craftables is not None else []

    def get_description(self, character_stat_block: CharacterStatBlock) -> str | None:
        parts = [f"Add your proficiency bonus to {self.ability.value} checks made with {self.name}."]
        if self.craftables:
            parts.append(f"Craft: {', '.join(item.name for item in self.craftables)}.")
        return " ".join(parts)


class NavigatorsTools(ToolProficiency):
    def __init__(self):
        super().__init__(name="Navigator's Tools", category="Other Tool", ability=Ability.WISDOM)


class PoisonersKit(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Poisoner's Kit", category="Other Tool", ability=Ability.INTELLIGENCE,
            craftables=[Items.BasicPoison()],
        )


class ThievesTools(ToolProficiency):
    def __init__(self):
        super().__init__(name="Thieves' Tools", category="Other Tool", ability=Ability.DEXTERITY)


class HerbalismKit(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Herbalism Kit", category="Other Tool", ability=Ability.INTELLIGENCE,
            craftables=[Items.Antitoxin(), Items.Candle(), Items.HealersKit(), Items.PotionOfHealing()],
        )


class AlchemistsSupplies(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Alchemist's Supplies", category="Artisan's Tools", ability=Ability.INTELLIGENCE,
            craftables=[Items.Acid(), Items.AlchemistsFire(), Items.ComponentPouch(), Items.Oil(), Items.Paper(), Items.Perfume()],
        )


class BrewersSupplies(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Brewer's Supplies", category="Artisan's Tools", ability=Ability.INTELLIGENCE,
            craftables=[Items.Antitoxin()],
        )


class CalligraphersSupplies(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Calligrapher's Supplies", category="Artisan's Tools", ability=Ability.DEXTERITY,
            craftables=[Items.Ink(), Items.SpellScroll()],
        )


class CarpentersTools(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Carpenter's Tools", category="Artisan's Tools", ability=Ability.STRENGTH,
            craftables=[Weapons.Club(), Weapons.Greatclub(), Weapons.Quarterstaff(), Items.Barrel(), Items.Chest(), Items.Ladder(), Items.Pole(), Items.PortableRam(), Items.Torch()],
        )


class CartographersTools(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Cartographer's Tools", category="Artisan's Tools", ability=Ability.WISDOM,
            craftables=[Items.Map()],
        )


class CobblersTools(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Cobbler's Tools", category="Artisan's Tools", ability=Ability.DEXTERITY,
            craftables=[Items.ClimbersKit()],
        )


class CooksUtensils(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Cook's Utensils", category="Artisan's Tools", ability=Ability.WISDOM,
            craftables=[Items.Rations()],
        )


class GlassblowersTools(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Glassblower's Tools", category="Artisan's Tools", ability=Ability.INTELLIGENCE,
            craftables=[Items.GlassBottle(), Items.MagnifyingGlass(), Items.Spyglass(), Items.Vial()],
        )


class JewelersTools(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Jeweler's Tools", category="Artisan's Tools", ability=Ability.INTELLIGENCE,
            craftables=[Items.ArcaneFocus(), Items.HolySymbol()],
        )


class LeatherworkersTools(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Leatherworker's Tools", category="Artisan's Tools", ability=Ability.DEXTERITY,
            craftables=[Weapons.Sling(), Weapons.Whip(), Armor.LeatherArmor(), Armor.StuddedLeatherArmor(), Items.Backpack(), Items.CrossbowBoltCase(), Items.MapOrScrollCase(), Items.Parchment(), Items.Pouch(), Items.Quiver(), Items.Waterskin()],
        )


class MasonsTools(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Mason's Tools", category="Artisan's Tools", ability=Ability.STRENGTH,
            craftables=[Items.BlockAndTackle()],
        )


class PaintersSupplies(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Painter's Supplies", category="Artisan's Tools", ability=Ability.WISDOM,
            craftables=[Items.DruidicFocus(), Items.HolySymbol()],
        )


class PottersTools(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Potter's Tools", category="Artisan's Tools", ability=Ability.INTELLIGENCE,
            craftables=[Items.Jug(), Items.Lamp()],
        )


class SmithsTools(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Smith's Tools", category="Artisan's Tools", ability=Ability.STRENGTH,
            craftables=[Items.BallBearings(), Items.Bucket(), Items.Caltrops(), Items.Chain(), Items.Crowbar(), Items.GrapplingHook(), Items.IronPot(), Items.IronSpikes()],
        )


class TinkersTools(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Tinker's Tools", category="Artisan's Tools", ability=Ability.DEXTERITY,
            craftables=[Weapons.Musket(), Weapons.Pistol(), Items.Bell(), Items.BullseyeLantern(), Items.Flask(), Items.HoodedLantern(), Items.HuntingTrap(), Items.Lock(), Items.Manacles(), Items.Mirror(), Items.Shovel(), Items.SignalWhistle(), Items.Tinderbox()],
        )


class WeaversTools(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Weaver's Tools", category="Artisan's Tools", ability=Ability.DEXTERITY,
            craftables=[Items.Basket(), Items.Bedroll(), Items.Blanket(), Items.FineClothes(), Items.Net(), Items.Robe(), Items.Rope(), Items.Sack(), Items.String(), Items.Tent(), Items.TravelersClothes()],
        )


class WoodcarversTools(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Woodcarver's Tools", category="Artisan's Tools", ability=Ability.DEXTERITY,
            craftables=[Weapons.Club(), Weapons.Greatclub(), Weapons.Quarterstaff(), Items.ArcaneFocus(), Items.Arrows(), Items.DruidicFocus(), Items.InkPen()],
        )


class DisguiseKit(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Disguise Kit", category="Other Tool", ability=Ability.CHARISMA,
            craftables=[Items.Costume()],
        )


class ForgeryKit(ToolProficiency):
    def __init__(self):
        super().__init__(name="Forgery Kit", category="Other Tool", ability=Ability.DEXTERITY)


class Dice(ToolProficiency):
    def __init__(self):
        super().__init__(name="Dice", category="Gaming Set", ability=Ability.WISDOM)


class Dragonchess(ToolProficiency):
    def __init__(self):
        super().__init__(name="Dragonchess", category="Gaming Set", ability=Ability.WISDOM)


class PlayingCards(ToolProficiency):
    def __init__(self):
        super().__init__(name="Playing Cards", category="Gaming Set", ability=Ability.WISDOM)


class ThreeDragonAnte(ToolProficiency):
    def __init__(self):
        super().__init__(name="Three-Dragon Ante", category="Gaming Set", ability=Ability.WISDOM)


class Bagpipes(ToolProficiency):
    def __init__(self):
        super().__init__(name="Bagpipes", category="Musical Instrument", ability=Ability.CHARISMA)


class Drum(ToolProficiency):
    def __init__(self):
        super().__init__(name="Drum", category="Musical Instrument", ability=Ability.CHARISMA)


class Dulcimer(ToolProficiency):
    def __init__(self):
        super().__init__(name="Dulcimer", category="Musical Instrument", ability=Ability.CHARISMA)


class Flute(ToolProficiency):
    def __init__(self):
        super().__init__(name="Flute", category="Musical Instrument", ability=Ability.CHARISMA)


class Horn(ToolProficiency):
    def __init__(self):
        super().__init__(name="Horn", category="Musical Instrument", ability=Ability.CHARISMA)


class Lute(ToolProficiency):
    def __init__(self):
        super().__init__(name="Lute", category="Musical Instrument", ability=Ability.CHARISMA)


class Lyre(ToolProficiency):
    def __init__(self):
        super().__init__(name="Lyre", category="Musical Instrument", ability=Ability.CHARISMA)


class PanFlute(ToolProficiency):
    def __init__(self):
        super().__init__(name="Pan Flute", category="Musical Instrument", ability=Ability.CHARISMA)


class Shawm(ToolProficiency):
    def __init__(self):
        super().__init__(name="Shawm", category="Musical Instrument", ability=Ability.CHARISMA)


class Viol(ToolProficiency):
    def __init__(self):
        super().__init__(name="Viol", category="Musical Instrument", ability=Ability.CHARISMA)
