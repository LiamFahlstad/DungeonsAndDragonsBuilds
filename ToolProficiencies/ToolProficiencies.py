from typing import Optional

from Definitions import Ability
from Features.Core.BaseFeatures import Feature
from Features.Items import Items
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class ToolProficiency(Feature):
    def __init__(
        self,
        name: str,
        category: str,
        ability: Ability,
        weight: Optional[float],
        cost: float,
        utilize: str,
        craftables: Optional[list[Items.Item]] = None,
    ):
        super().__init__(name=name)
        self.category = category
        self.ability = ability
        self.weight = weight
        self.cost = cost
        self.utilize = utilize
        self.craftables = craftables if craftables is not None else []

    def description(self) -> str:
        parts = [f"Utilize: {self.utilize}."]
        if self.craftables:
            parts.append(f"Craft: {', '.join(item.name for item in self.craftables)}.")
        return " ".join(parts)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str | None:
        return self.description()


class NavigatorsTools(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Navigator's Tools",
            category="Other Tool",
            ability=Ability.WISDOM,
            weight=2.0,
            cost=25,
            utilize="Plot a course (DC 10), or determine position by stargazing (DC 15)",
        )


class PoisonersKit(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Poisoner's Kit",
            category="Other Tool",
            ability=Ability.INTELLIGENCE,
            weight=2.0,
            cost=50,
            utilize="Detect a poisoned object (DC 10)",
            craftables=[Items.BasicPoison()],
        )


class ThievesTools(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Thieves' Tools",
            category="Other Tool",
            ability=Ability.DEXTERITY,
            weight=1.0,
            cost=25,
            utilize="Pick a lock (DC 15), or disarm a trap (DC 15)",
        )


class HerbalismKit(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Herbalism Kit",
            category="Other Tool",
            ability=Ability.INTELLIGENCE,
            weight=3.0,
            cost=5,
            utilize="Identify a plant (DC 10)",
            craftables=[Items.Antitoxin(), Items.Candle(), Items.HealersKit(), Items.PotionOfHealing()],
        )


class AlchemistsSupplies(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Alchemist's Supplies",
            category="Artisan's Tools",
            ability=Ability.INTELLIGENCE,
            weight=8.0,
            cost=50,
            utilize="Identify a substance (DC 15), or start a fire (DC 15)",
            craftables=[Items.Acid(), Items.AlchemistsFire(), Items.ComponentPouch(), Items.Oil(), Items.Paper(), Items.Perfume()],
        )


class BrewersSupplies(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Brewer's Supplies",
            category="Artisan's Tools",
            ability=Ability.INTELLIGENCE,
            weight=9.0,
            cost=20,
            utilize="Detect poisoned drink (DC 15), or identify alcohol (DC 10)",
            craftables=[Items.Antitoxin()],
        )


class CalligraphersSupplies(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Calligrapher's Supplies",
            category="Artisan's Tools",
            ability=Ability.DEXTERITY,
            weight=5.0,
            cost=10,
            utilize="Write text with impressive flourishes that guard against forgery (DC 15)",
            craftables=[Items.Ink(), Items.SpellScroll()],
        )


class CarpentersTools(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Carpenter's Tools",
            category="Artisan's Tools",
            ability=Ability.STRENGTH,
            weight=6.0,
            cost=8,
            utilize="Seal or pry open a door or container (DC 20)",
            craftables=[Items.Club(), Items.Greatclub(), Items.Quarterstaff(), Items.Barrel(), Items.Chest(), Items.Ladder(), Items.Pole(), Items.PortableRam(), Items.Torch()],
        )


class CartographersTools(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Cartographer's Tools",
            category="Artisan's Tools",
            ability=Ability.WISDOM,
            weight=6.0,
            cost=15,
            utilize="Draft a map of a small area (DC 15)",
            craftables=[Items.Map()],
        )


class CobblersTools(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Cobbler's Tools",
            category="Artisan's Tools",
            ability=Ability.DEXTERITY,
            weight=5.0,
            cost=5,
            utilize="Modify footwear to give Advantage on the wearer's next Dexterity (Acrobatics) check (DC 10)",
            craftables=[Items.ClimbersKit()],
        )


class CooksUtensils(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Cook's Utensils",
            category="Artisan's Tools",
            ability=Ability.WISDOM,
            weight=8.0,
            cost=1,
            utilize="Improve food's flavor (DC 10), or detect spoiled or poisoned food (DC 15)",
            craftables=[Items.Rations()],
        )


class GlassblowersTools(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Glassblower's Tools",
            category="Artisan's Tools",
            ability=Ability.INTELLIGENCE,
            weight=5.0,
            cost=30,
            utilize="Discern what a glass object held in the past 24 hours (DC 15)",
            craftables=[Items.GlassBottle(), Items.MagnifyingGlass(), Items.Spyglass(), Items.Vial()],
        )


class JewelersTools(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Jeweler's Tools",
            category="Artisan's Tools",
            ability=Ability.INTELLIGENCE,
            weight=2.0,
            cost=25,
            utilize="Discern a gem's value (DC 15)",
            craftables=[Items.ArcaneFocus(), Items.HolySymbol()],
        )


class LeatherworkersTools(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Leatherworker's Tools",
            category="Artisan's Tools",
            ability=Ability.DEXTERITY,
            weight=5.0,
            cost=5,
            utilize="Add a design to a leather item (DC 10)",
            craftables=[Items.Sling(), Items.Whip(), Items.HideArmor(), Items.LeatherArmor(), Items.StuddedLeatherArmor(), Items.Backpack(), Items.CrossbowBoltCase(), Items.MapOrScrollCase(), Items.Parchment(), Items.Pouch(), Items.Quiver(), Items.Waterskin()],
        )


class MasonsTools(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Mason's Tools",
            category="Artisan's Tools",
            ability=Ability.STRENGTH,
            weight=8.0,
            cost=10,
            utilize="Chisel a symbol or hole in stone (DC 10)",
            craftables=[Items.BlockAndTackle()],
        )


class PaintersSupplies(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Painter's Supplies",
            category="Artisan's Tools",
            ability=Ability.WISDOM,
            weight=5.0,
            cost=10,
            utilize="Paint a recognizable image of something you've seen (DC 10)",
            craftables=[Items.DruidicFocus(), Items.HolySymbol()],
        )


class PottersTools(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Potter's Tools",
            category="Artisan's Tools",
            ability=Ability.INTELLIGENCE,
            weight=3.0,
            cost=10,
            utilize="Discern what a ceramic object held in the past 24 hours (DC 15)",
            craftables=[Items.Jug(), Items.Lamp()],
        )


class SmithsTools(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Smith's Tools",
            category="Artisan's Tools",
            ability=Ability.STRENGTH,
            weight=8.0,
            cost=20,
            utilize="Pry open a door or container (DC 20)",
            craftables=[Items.AnyMeleeWeaponPlaceholder(), Items.MediumArmorPlaceholder(), Items.HeavyArmorPlaceholder(), Items.BallBearings(), Items.Bucket(), Items.Caltrops(), Items.Chain(), Items.Crowbar(), Items.FirearmBullets(), Items.GrapplingHook(), Items.IronPot(), Items.IronSpikes(), Items.SlingBullets()],
        )


class TinkersTools(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Tinker's Tools",
            category="Artisan's Tools",
            ability=Ability.DEXTERITY,
            weight=10.0,
            cost=50,
            utilize="Assemble a Tiny item composed of scrap, which falls apart in 1 minute (DC 20)",
            craftables=[Items.Musket(), Items.Pistol(), Items.Bell(), Items.BullseyeLantern(), Items.Flask(), Items.HoodedLantern(), Items.HuntingTrap(), Items.Lock(), Items.Manacles(), Items.MirrorPlaceholder(), Items.Shovel(), Items.SignalWhistle(), Items.Tinderbox()],
        )


class WeaversTools(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Weaver's Tools",
            category="Artisan's Tools",
            ability=Ability.DEXTERITY,
            weight=5.0,
            cost=1,
            utilize="Mend a tear in clothing (DC 10), or sew a Tiny design (DC 10)",
            craftables=[Items.PaddedArmor(), Items.Basket(), Items.Bedroll(), Items.Blanket(), Items.FineClothes(), Items.Net(), Items.Robe(), Items.RopePlaceholder(), Items.Sack(), Items.StringItem(), Items.Tent(), Items.TravelersClothes()],
        )


class WoodcarversTools(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Woodcarver's Tools",
            category="Artisan's Tools",
            ability=Ability.DEXTERITY,
            weight=5.0,
            cost=1,
            utilize="Carve a pattern in wood (DC 10)",
            craftables=[Items.Club(), Items.Greatclub(), Items.Quarterstaff(), Items.RangedWeaponsPlaceholder(), Items.ArcaneFocus(), Items.Arrows(), Items.Bolts(), Items.DruidicFocus(), Items.InkPen(), Items.Needles()],
        )


class DisguiseKit(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Disguise Kit",
            category="Other Tool",
            ability=Ability.CHARISMA,
            weight=3.0,
            cost=25,
            utilize="Apply makeup (DC 10)",
            craftables=[Items.Costume()],
        )


class ForgeryKit(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Forgery Kit",
            category="Other Tool",
            ability=Ability.DEXTERITY,
            weight=5.0,
            cost=15,
            utilize="Mimic 10 or fewer words of someone else's handwriting (DC 15), or duplicate a wax seal (DC 20)",
        )


class Dice(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Dice",
            category="Gaming Set",
            ability=Ability.WISDOM,
            weight=None,
            cost=0.1,
            utilize="Discern whether someone is cheating (DC 10), or win the game (DC 20)",
        )


class Dragonchess(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Dragonchess",
            category="Gaming Set",
            ability=Ability.WISDOM,
            weight=None,
            cost=1,
            utilize="Discern whether someone is cheating (DC 10), or win the game (DC 20)",
        )


class PlayingCards(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Playing Cards",
            category="Gaming Set",
            ability=Ability.WISDOM,
            weight=None,
            cost=0.5,
            utilize="Discern whether someone is cheating (DC 10), or win the game (DC 20)",
        )


class ThreeDragonAnte(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Three-Dragon Ante",
            category="Gaming Set",
            ability=Ability.WISDOM,
            weight=None,
            cost=1,
            utilize="Discern whether someone is cheating (DC 10), or win the game (DC 20)",
        )


class Bagpipes(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Bagpipes",
            category="Musical Instrument",
            ability=Ability.CHARISMA,
            weight=6.0,
            cost=30,
            utilize="Play a known tune (DC 10), or improvise a song (DC 15)",
        )


class Drum(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Drum",
            category="Musical Instrument",
            ability=Ability.CHARISMA,
            weight=3.0,
            cost=6,
            utilize="Play a known tune (DC 10), or improvise a song (DC 15)",
        )


class Dulcimer(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Dulcimer",
            category="Musical Instrument",
            ability=Ability.CHARISMA,
            weight=10.0,
            cost=25,
            utilize="Play a known tune (DC 10), or improvise a song (DC 15)",
        )


class Flute(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Flute",
            category="Musical Instrument",
            ability=Ability.CHARISMA,
            weight=1.0,
            cost=2,
            utilize="Play a known tune (DC 10), or improvise a song (DC 15)",
        )


class Horn(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Horn",
            category="Musical Instrument",
            ability=Ability.CHARISMA,
            weight=2.0,
            cost=3,
            utilize="Play a known tune (DC 10), or improvise a song (DC 15)",
        )


class Lute(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Lute",
            category="Musical Instrument",
            ability=Ability.CHARISMA,
            weight=2.0,
            cost=35,
            utilize="Play a known tune (DC 10), or improvise a song (DC 15)",
        )


class Lyre(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Lyre",
            category="Musical Instrument",
            ability=Ability.CHARISMA,
            weight=2.0,
            cost=30,
            utilize="Play a known tune (DC 10), or improvise a song (DC 15)",
        )


class PanFlute(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Pan Flute",
            category="Musical Instrument",
            ability=Ability.CHARISMA,
            weight=2.0,
            cost=12,
            utilize="Play a known tune (DC 10), or improvise a song (DC 15)",
        )


class Shawm(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Shawm",
            category="Musical Instrument",
            ability=Ability.CHARISMA,
            weight=1.0,
            cost=2,
            utilize="Play a known tune (DC 10), or improvise a song (DC 15)",
        )


class Viol(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Viol",
            category="Musical Instrument",
            ability=Ability.CHARISMA,
            weight=1.0,
            cost=30,
            utilize="Play a known tune (DC 10), or improvise a song (DC 15)",
        )
