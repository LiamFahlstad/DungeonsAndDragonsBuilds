from typing import Optional

from Core.Definitions import Ability
from CharacterContent.Features.Core.BaseFeatures import Feature
from CharacterContent.Items import Armor, Weapons
from CharacterContent.Items import Items
from Model.Character import Character


class ToolProficiency(Feature):
    """Represents training with a tool, not the tool itself - see the
    matching class in CharacterContent.Items.Items for the tool's weight,
    cost, and what it physically does. This grants your proficiency bonus
    on ability checks made with the tool, the things it lets you do with the
    Utilize action (each with its DC) and, where listed, the ability to craft
    certain items with it during downtime."""

    def __init__(
        self,
        name: str,
        category: str,
        ability: Ability,
        utilize: list[tuple[str, int]],
        craftables: Optional[list[Items.Item]] = None,
    ):
        super().__init__(name=name)
        self.category = category
        self.ability = ability
        # (what you can do, DC) pairs - one of these per Utilize action.
        self.utilize = utilize
        self.craftables = craftables if craftables is not None else []

    def utilize_text(self) -> str:
        options = [f"{action} (DC {dc})" for action, dc in self.utilize]
        # Each option is stored capitalized; lower-case all but the first so
        # they read as one sentence ("Pick a lock (DC 15), or disarm a trap").
        options[1:] = [option[0].lower() + option[1:] for option in options[1:]]
        return ", or ".join(options)

    def craft_text(self) -> str:
        return ", ".join(item.name for item in self.craftables)

    def make_item(self) -> Optional[Items.Item]:
        """A new instance of the tool itself: the Items class sharing this
        proficiency's class name (Proficiencies.Lute / Items.Lute), or None
        when there isn't one."""
        item_class = getattr(Items, type(self).__name__, None)
        return item_class() if item_class is not None else None

    def get_description(self, character: Character) -> str | None:
        lines = [
            f"Add your proficiency bonus to {self.ability.value} checks made with {self.name}.",
            f"Utilize: {self.utilize_text()}.",
        ]
        if self.craftables:
            lines.append(f"Craft: {self.craft_text()}.")
        return "\n".join(lines)

    def get_table_description(
        self, character: Character
    ) -> list[tuple[str, str]] | None:
        rows = [("Ability", self.ability.value), ("Utilize", self.utilize_text())]
        if self.craftables:
            rows.append(("Craft", self.craft_text()))
        return rows


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
            craftables=[Items.BasicPoison()],
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
            craftables=[
                Items.Antitoxin(),
                Items.Candle(),
                Items.HealersKit(),
                Items.PotionOfHealing(),
            ],
        )


class AlchemistsSupplies(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Alchemist's Supplies",
            category="Artisan's Tools",
            ability=Ability.INTELLIGENCE,
            utilize=[("Identify a substance", 15), ("Start a fire", 15)],
            craftables=[
                Items.Acid(),
                Items.AlchemistsFire(),
                Items.ComponentPouch(),
                Items.Oil(),
                Items.Paper(),
                Items.Perfume(),
            ],
        )


class BrewersSupplies(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Brewer's Supplies",
            category="Artisan's Tools",
            ability=Ability.INTELLIGENCE,
            utilize=[("Detect poisoned drink", 15), ("Identify alcohol", 10)],
            craftables=[Items.Antitoxin()],
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
            craftables=[Items.Ink(), Items.SpellScroll()],
        )


class CarpentersTools(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Carpenter's Tools",
            category="Artisan's Tools",
            ability=Ability.STRENGTH,
            utilize=[("Seal or pry open a door or container", 20)],
            craftables=[
                Weapons.Club(),
                Weapons.Greatclub(),
                Weapons.Quarterstaff(),
                Items.Barrel(),
                Items.Chest(),
                Items.Ladder(),
                Items.Pole(),
                Items.PortableRam(),
                Items.Torch(),
            ],
        )


class CartographersTools(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Cartographer's Tools",
            category="Artisan's Tools",
            ability=Ability.WISDOM,
            utilize=[("Draft a map of a small area", 15)],
            craftables=[Items.Map()],
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
            craftables=[Items.ClimbersKit()],
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
            craftables=[Items.Rations()],
        )


class GlassblowersTools(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Glassblower's Tools",
            category="Artisan's Tools",
            ability=Ability.INTELLIGENCE,
            utilize=[("Discern what a glass object held in the past 24 hours", 15)],
            craftables=[
                Items.GlassBottle(),
                Items.MagnifyingGlass(),
                Items.Spyglass(),
                Items.Vial(),
            ],
        )


class JewelersTools(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Jeweler's Tools",
            category="Artisan's Tools",
            ability=Ability.INTELLIGENCE,
            utilize=[("Discern a gem's value", 15)],
            craftables=[Items.ArcaneFocus(), Items.HolySymbol()],
        )


class LeatherworkersTools(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Leatherworker's Tools",
            category="Artisan's Tools",
            ability=Ability.DEXTERITY,
            utilize=[("Add a design to a leather item", 10)],
            craftables=[
                Weapons.Sling(),
                Weapons.Whip(),
                Armor.LeatherArmor(),
                Armor.StuddedLeatherArmor(),
                Items.Backpack(),
                Items.CrossbowBoltCase(),
                Items.MapOrScrollCase(),
                Items.Parchment(),
                Items.Pouch(),
                Items.Quiver(),
                Items.Waterskin(),
            ],
        )


class MasonsTools(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Mason's Tools",
            category="Artisan's Tools",
            ability=Ability.STRENGTH,
            utilize=[("Chisel a symbol or hole in stone", 10)],
            craftables=[Items.BlockAndTackle()],
        )


class PaintersSupplies(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Painter's Supplies",
            category="Artisan's Tools",
            ability=Ability.WISDOM,
            utilize=[("Paint a recognizable image of something you've seen", 10)],
            craftables=[Items.DruidicFocus(), Items.HolySymbol()],
        )


class PottersTools(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Potter's Tools",
            category="Artisan's Tools",
            ability=Ability.INTELLIGENCE,
            utilize=[("Discern what a ceramic object held in the past 24 hours", 15)],
            craftables=[Items.Jug(), Items.Lamp()],
        )


class SmithsTools(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Smith's Tools",
            category="Artisan's Tools",
            ability=Ability.STRENGTH,
            utilize=[("Pry open a door or container", 20)],
            craftables=[
                Items.BallBearings(),
                Items.Bucket(),
                Items.Caltrops(),
                Items.Chain(),
                Items.Crowbar(),
                Items.GrapplingHook(),
                Items.IronPot(),
                Items.IronSpikes(),
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
                Weapons.Musket(),
                Weapons.Pistol(),
                Items.Bell(),
                Items.BullseyeLantern(),
                Items.Flask(),
                Items.HoodedLantern(),
                Items.HuntingTrap(),
                Items.Lock(),
                Items.Manacles(),
                Items.Mirror(),
                Items.Shovel(),
                Items.SignalWhistle(),
                Items.Tinderbox(),
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
                Items.Basket(),
                Items.Bedroll(),
                Items.Blanket(),
                Items.FineClothes(),
                Items.Net(),
                Items.Robe(),
                Items.Rope(),
                Items.Sack(),
                Items.String(),
                Items.Tent(),
                Items.TravelersClothes(),
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
                Weapons.Club(),
                Weapons.Greatclub(),
                Weapons.Quarterstaff(),
                Items.ArcaneFocus(),
                Items.Arrows(),
                Items.DruidicFocus(),
                Items.InkPen(),
            ],
        )


class DisguiseKit(ToolProficiency):
    def __init__(self):
        super().__init__(
            name="Disguise Kit",
            category="Other Tool",
            ability=Ability.CHARISMA,
            utilize=[("Apply makeup", 10)],
            craftables=[Items.Costume()],
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
