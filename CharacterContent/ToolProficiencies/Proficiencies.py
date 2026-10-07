"""The tool proficiencies (Thieves' Tools, a Lute, ...), and the item each one
is the training for (TOOL_ITEMS). ToolProficiency itself is a plain record
in Model/Records/Tools.py, so the Ledger can record it."""

from typing import Callable, Optional

from Core.Definitions import Ability
from CharacterContent.Items import Items
from Model.Records.Tools import ToolProficiency

GAMING_SET_UTILIZE = [
    ("Discern whether someone is cheating", 10),
    ("Win the game", 20),
]

MUSICAL_INSTRUMENT_UTILIZE = [
    ("Play a known tune", 10),
    ("Improvise a song", 15),
]


class NavigatorsTools(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Navigator's Tools",
            category="Other Tool",
            ability=Ability.WISDOM,
            utilize=[("Plot a course", 10), ("Determine position by stargazing", 15)],
        )


class PoisonersKit(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Poisoner's Kit",
            category="Other Tool",
            ability=Ability.INTELLIGENCE,
            utilize=[("Detect a poisoned object", 10)],
            craftables=["Basic Poison"],
        )


class ThievesTools(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Thieves' Tools",
            category="Other Tool",
            ability=Ability.DEXTERITY,
            utilize=[("Pick a lock", 15), ("Disarm a trap", 15)],
        )


class HerbalismKit(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Herbalism Kit",
            category="Other Tool",
            ability=Ability.INTELLIGENCE,
            utilize=[("Identify a plant", 10)],
            craftables=["Antitoxin", "Candle", "Healer's Kit", "Potion of Healing"],
        )


class AlchemistsSupplies(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Alchemist's Supplies",
            category="Artisan's Tools",
            ability=Ability.INTELLIGENCE,
            utilize=[("Identify a substance", 15), ("Start a fire", 15)],
            craftables=[
                "Acid",
                "Alchemist's Fire",
                "Component Pouch",
                "Oil",
                "Paper",
                "Perfume",
            ],
        )


class BrewersSupplies(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Brewer's Supplies",
            category="Artisan's Tools",
            ability=Ability.INTELLIGENCE,
            utilize=[("Detect poisoned drink", 15), ("Identify alcohol", 10)],
            craftables=["Antitoxin"],
        )


class CalligraphersSupplies(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Calligrapher's Supplies",
            category="Artisan's Tools",
            ability=Ability.DEXTERITY,
            utilize=[
                ("Write text with impressive flourishes that guard against forgery", 15)
            ],
            craftables=["Ink", "Spell Scroll"],
        )


class CarpentersTools(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Carpenter's Tools",
            category="Artisan's Tools",
            ability=Ability.STRENGTH,
            utilize=[("Seal or pry open a door or container", 20)],
            craftables=[
                "Club",
                "Greatclub",
                "Quarterstaff",
                "Barrel",
                "Chest",
                "Ladder",
                "Pole",
                "Portable Ram",
                "Torch",
            ],
        )


class CartographersTools(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Cartographer's Tools",
            category="Artisan's Tools",
            ability=Ability.WISDOM,
            utilize=[("Draft a map of a small area", 15)],
            craftables=["Map"],
        )


class CobblersTools(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Cobbler's Tools",
            category="Artisan's Tools",
            ability=Ability.DEXTERITY,
            utilize=[
                (
                    "Modify footwear to give Advantage on the wearer's next Dexterity (Acrobatics) check",
                    10,
                )
            ],
            craftables=["Climber's Kit"],
        )


class CooksUtensils(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Cook's Utensils",
            category="Artisan's Tools",
            ability=Ability.WISDOM,
            utilize=[
                ("Improve food's flavor", 10),
                ("Detect spoiled or poisoned food", 15),
            ],
            craftables=["Rations"],
        )


class GlassblowersTools(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Glassblower's Tools",
            category="Artisan's Tools",
            ability=Ability.INTELLIGENCE,
            utilize=[("Discern what a glass object held in the past 24 hours", 15)],
            craftables=["Glass Bottle", "Magnifying Glass", "Spyglass", "Vial"],
        )


class JewelersTools(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Jeweler's Tools",
            category="Artisan's Tools",
            ability=Ability.INTELLIGENCE,
            utilize=[("Discern a gem's value", 15)],
            craftables=["Arcane Focus", "Holy Symbol"],
        )


class LeatherworkersTools(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Leatherworker's Tools",
            category="Artisan's Tools",
            ability=Ability.DEXTERITY,
            utilize=[("Add a design to a leather item", 10)],
            craftables=[
                "Sling",
                "Whip",
                "Leather Armor",
                "Studded Leather Armor",
                "Backpack",
                "Crossbow Bolt Case",
                "Map or Scroll Case",
                "Parchment",
                "Pouch",
                "Quiver",
                "Waterskin",
            ],
        )


class MasonsTools(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Mason's Tools",
            category="Artisan's Tools",
            ability=Ability.STRENGTH,
            utilize=[("Chisel a symbol or hole in stone", 10)],
            craftables=["Block and Tackle"],
        )


class PaintersSupplies(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Painter's Supplies",
            category="Artisan's Tools",
            ability=Ability.WISDOM,
            utilize=[("Paint a recognizable image of something you've seen", 10)],
            craftables=["Druidic Focus", "Holy Symbol"],
        )


class PottersTools(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Potter's Tools",
            category="Artisan's Tools",
            ability=Ability.INTELLIGENCE,
            utilize=[("Discern what a ceramic object held in the past 24 hours", 15)],
            craftables=["Jug", "Lamp"],
        )


class SmithsTools(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Smith's Tools",
            category="Artisan's Tools",
            ability=Ability.STRENGTH,
            utilize=[("Pry open a door or container", 20)],
            craftables=[
                "Ball Bearings",
                "Bucket",
                "Caltrops",
                "Chain",
                "Crowbar",
                "Grappling Hook",
                "Iron Pot",
                "Iron Spikes",
            ],
        )


class TinkersTools(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Tinker's Tools",
            category="Artisan's Tools",
            ability=Ability.DEXTERITY,
            utilize=[
                (
                    "Assemble a Tiny item composed of scrap, which falls apart in 1 minute",
                    20,
                )
            ],
            craftables=[
                "Musket",
                "Pistol",
                "Bell",
                "Bullseye Lantern",
                "Flask",
                "Hooded Lantern",
                "Hunting Trap",
                "Lock",
                "Manacles",
                "Steel Mirror",
                "Shovel",
                "Signal Whistle",
                "Tinderbox",
            ],
        )


class WeaversTools(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Weaver's Tools",
            category="Artisan's Tools",
            ability=Ability.DEXTERITY,
            utilize=[("Mend a tear in clothing", 10), ("Sew a Tiny design", 10)],
            craftables=[
                "Basket",
                "Bedroll",
                "Blanket",
                "Fine Clothes",
                "Net",
                "Robe",
                "Rope (50 ft)",
                "Sack",
                "String",
                "Tent",
                "Traveler's Clothes",
            ],
        )


class WoodcarversTools(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Woodcarver's Tools",
            category="Artisan's Tools",
            ability=Ability.DEXTERITY,
            utilize=[("Carve a pattern in wood", 10)],
            craftables=[
                "Club",
                "Greatclub",
                "Quarterstaff",
                "Arcane Focus",
                "Arrows",
                "Druidic Focus",
                "Ink Pen",
            ],
        )


class DisguiseKit(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Disguise Kit",
            category="Other Tool",
            ability=Ability.CHARISMA,
            utilize=[("Apply makeup", 10)],
            craftables=["Costume"],
        )


class ForgeryKit(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Forgery Kit",
            category="Other Tool",
            ability=Ability.DEXTERITY,
            utilize=[
                ("Mimic 10 or fewer words of someone else's handwriting", 15),
                ("Duplicate a wax seal", 20),
            ],
        )


class Dice(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Dice",
            category="Gaming Set",
            ability=Ability.WISDOM,
            utilize=GAMING_SET_UTILIZE,
        )


class Dragonchess(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Dragonchess",
            category="Gaming Set",
            ability=Ability.WISDOM,
            utilize=GAMING_SET_UTILIZE,
        )


class PlayingCards(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Playing Cards",
            category="Gaming Set",
            ability=Ability.WISDOM,
            utilize=GAMING_SET_UTILIZE,
        )


class ThreeDragonAnte(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Three-Dragon Ante",
            category="Gaming Set",
            ability=Ability.WISDOM,
            utilize=GAMING_SET_UTILIZE,
        )


class Bagpipes(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Bagpipes",
            category="Musical Instrument",
            ability=Ability.CHARISMA,
            utilize=MUSICAL_INSTRUMENT_UTILIZE,
        )


class Drum(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Drum",
            category="Musical Instrument",
            ability=Ability.CHARISMA,
            utilize=MUSICAL_INSTRUMENT_UTILIZE,
        )


class Dulcimer(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Dulcimer",
            category="Musical Instrument",
            ability=Ability.CHARISMA,
            utilize=MUSICAL_INSTRUMENT_UTILIZE,
        )


class Flute(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Flute",
            category="Musical Instrument",
            ability=Ability.CHARISMA,
            utilize=MUSICAL_INSTRUMENT_UTILIZE,
        )


class Horn(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Horn",
            category="Musical Instrument",
            ability=Ability.CHARISMA,
            utilize=MUSICAL_INSTRUMENT_UTILIZE,
        )


class Lute(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Lute",
            category="Musical Instrument",
            ability=Ability.CHARISMA,
            utilize=MUSICAL_INSTRUMENT_UTILIZE,
        )


class Lyre(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Lyre",
            category="Musical Instrument",
            ability=Ability.CHARISMA,
            utilize=MUSICAL_INSTRUMENT_UTILIZE,
        )


class PanFlute(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Pan Flute",
            category="Musical Instrument",
            ability=Ability.CHARISMA,
            utilize=MUSICAL_INSTRUMENT_UTILIZE,
        )


class Shawm(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Shawm",
            category="Musical Instrument",
            ability=Ability.CHARISMA,
            utilize=MUSICAL_INSTRUMENT_UTILIZE,
        )


class Viol(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Viol",
            category="Musical Instrument",
            ability=Ability.CHARISMA,
            utilize=MUSICAL_INSTRUMENT_UTILIZE,
        )


# The item each tool proficiency is the training for (same name in
# CharacterContent/Items/Items), as its no-argument constructor.
TOOL_ITEMS: dict[type[ToolProficiency], Callable[[], Items.Item]] = {
    AlchemistsSupplies: Items.AlchemistsSupplies,
    Bagpipes: Items.Bagpipes,
    BrewersSupplies: Items.BrewersSupplies,
    CalligraphersSupplies: Items.CalligraphersSupplies,
    CarpentersTools: Items.CarpentersTools,
    CartographersTools: Items.CartographersTools,
    CobblersTools: Items.CobblersTools,
    CooksUtensils: Items.CooksUtensils,
    Dice: Items.Dice,
    DisguiseKit: Items.DisguiseKit,
    Dragonchess: Items.Dragonchess,
    Drum: Items.Drum,
    Dulcimer: Items.Dulcimer,
    Flute: Items.Flute,
    ForgeryKit: Items.ForgeryKit,
    GlassblowersTools: Items.GlassblowersTools,
    HerbalismKit: Items.HerbalismKit,
    Horn: Items.Horn,
    JewelersTools: Items.JewelersTools,
    LeatherworkersTools: Items.LeatherworkersTools,
    Lute: Items.Lute,
    Lyre: Items.Lyre,
    MasonsTools: Items.MasonsTools,
    NavigatorsTools: Items.NavigatorsTools,
    PaintersSupplies: Items.PaintersSupplies,
    PanFlute: Items.PanFlute,
    PlayingCards: Items.PlayingCards,
    PoisonersKit: Items.PoisonersKit,
    PottersTools: Items.PottersTools,
    Shawm: Items.Shawm,
    SmithsTools: Items.SmithsTools,
    ThievesTools: Items.ThievesTools,
    ThreeDragonAnte: Items.ThreeDragonAnte,
    TinkersTools: Items.TinkersTools,
    Viol: Items.Viol,
    WeaversTools: Items.WeaversTools,
    WoodcarversTools: Items.WoodcarversTools,
}


def tool_item(tool: ToolProficiency) -> Optional[Items.Item]:
    """A new instance of the tool itself, or None when it has no item."""
    item_class = TOOL_ITEMS.get(type(tool))
    return item_class() if item_class is not None else None
