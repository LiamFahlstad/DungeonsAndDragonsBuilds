from Model.Content.Feature import (
    Feature,
    FeatureUses,
    FeatureActivation,
    FeatureTarget,
    RegainedOn,
)
from Core.Rules import MAX_ABILITY_MODIFIER
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Option, Paragraph, Table


class CartographerToolsOfTheTrade(Feature):
    def __init__(self):
        super().__init__(
            name="Tools of the Trade",
            origin="Cartographer Artificer Level 3",
            usage_tags=["utility"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Tool Proficiency",
                        "Calligrapher's Supplies and Cartographer's Tools. For each you already have, gain another type of Artisan's Tools of your choice instead.",
                    ),
                    (
                        "Scroll Crafting",
                        "Scribing a Spell Scroll (Player's Handbook crafting rules) takes half the time",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You gain the following benefits.\n"
            "Tool Proficiency. You gain proficiency with Calligrapher's Supplies and Cartographer's Tools. If you already have one of these proficiencies, you gain proficiency with one other type of Artisan's Tools of your choice (or with two other types if you have both).\n"
            "Scroll Crafting. When you scribe a Spell Scroll using the crafting rules in the Player's Handbook, the amount of time required to craft it is halved."
        )
        return description


class CartographerSpells(Feature):
    def __init__(self):
        super().__init__(
            name="Cartographer Spells", origin="Cartographer Artificer Level 3"
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "From the Artificer level shown, you always have these spells prepared."
            ),
            Table(
                ("Artificer level", "Spells"),
                (
                    ("3", "Faerie Fire, Guiding Bolt, Healing Word"),
                    ("5", "Locate Object, Mind Spike"),
                    ("9", "Call Lightning, Clairvoyance"),
                    ("13", "Banishment, Locate Creature"),
                    ("17", "Scrying, Teleportation Circle"),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "When you reach an Artificer level specified in the Cartographer Spells table, you thereafter always have the listed spells prepared.\n"
            "Cartographer Spells\n"
            "Artificer Level	Spells\n"
            "3	Faerie Fire, Guiding Bolt, Healing Word\n"
            "5	Locate Object, Mind Spike\n"
            "9	Call Lightning, Clairvoyance\n"
            "13	Banishment, Locate Creature\n"
            "17	Scrying, Teleportation Circle"
        )
        return description


class AdventurersAtlas(Feature):
    def __init__(self):
        super().__init__(
            name="Adventurer's Atlas",
            origin="Cartographer Artificer Level 3",
            usage_tags=["buff"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Draw magical maps that link your allies."),
            Facts(
                (
                    (
                        "When",
                        "Whenever you finish a Long Rest, holding Cartographer's Tools",
                    ),
                    (
                        "Map holders",
                        "Touch 2 to 1 + Intelligence modifier creatures (you can be one)",
                    ),
                    (
                        "Map",
                        "Constantly shows where all map holders are relative to each other; illegible to anyone else",
                    ),
                    (
                        "Lasts",
                        "Until you die or use this feature again (the old maps vanish)",
                    ),
                )
            ),
            Option(
                "Carrying a map",
                (
                    Facts(
                        (
                            ("Awareness", "Add 1d4 to Initiative rolls"),
                            (
                                "Positioning",
                                "Know where every other map holder on the same plane is, and target another map holder with a spell or effect regardless of sight or cover, if it's in range",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Whenever you finish a Long Rest while holding Cartographer's Tools, you can use that tool to create a set of magical maps by touching at least two creatures (one of whom can be yourself), up to a maximum number of creatures equal to 1 plus your Intelligence modifier (minimum of two creatures). Each target receives a magical map, which constantly updates to show the relative position of all the map holders but is illegible to all others. The maps last until you die or until you use this feature again, at which point any existing maps created by this feature immediately vanish.\n"
            "While carrying the map, a target gains the following benefits.\n"
            "Awareness. The target adds 1d4 to its Initiative rolls.\n"
            "Positioning. The target knows the location of all other map holders that are on the same plane of existence as itself. When casting a spell or creating another effect that requires being able to see the effect's target, a map holder can target another map holder regardless of sight or cover, so long as the other map holder is still within the effect's range."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY


class MappingMagic(Feature):
    def __init__(self):
        super().__init__(
            name="Mapping Magic",
            origin="Cartographer Artificer Level 3",
            activation=FeatureActivation(range="30 Feet"),
            usage_tags=["utility"],
            uses=FeatureUses(
                max_uses=MAX_ABILITY_MODIFIER,
                regain_all_on="long rest",
                current_formula="Current amount: equal to your Intelligence modifier.",
            ),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # Illuminated Cartography's uses are in the panel below.
        return [
            Option(
                "Illuminated Cartography",
                (
                    Facts(
                        (
                            (
                                "Effect",
                                "Cast Faerie Fire without a spell slot, outlining creatures as if in ink; Intelligence modifier (minimum once) times per Long Rest",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Portal Jump",
                (
                    Facts(
                        (
                            (
                                "Cost",
                                "Half your Speed (round down) of movement, on your turn; not if your Speed is 0",
                            ),
                            (
                                "Teleport",
                                "To an unoccupied space you can see within 10 feet, or within 5 feet of a creature within 30 feet that holds one of your Adventurer's Atlas maps",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You gain the following benefits.\n"
            "Illuminated Cartography. You can cast Faerie Fire without expending a spell slot, outlining the affected creatures as if in ink. You can do so a number of times equal to your Intelligence modifier (minimum of once), and you regain all expended uses when you finish a Long Rest.\n"
            "Portal Jump. On your turn, you can spend an amount of movement equal to half your Speed (round down) to teleport to an unoccupied space you can see within 10 feet of yourself or within 5 feet of a creature that is within 30 feet of you and holding one of your Adventurer's Atlas maps. You can't use this benefit if your Speed is 0."
        )
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def number_of_uses(self, character: CharacterView) -> int:
        return max(1, character.get_intelligence_modifier())


class GuidedPrecision(Feature):
    def __init__(self):
        super().__init__(
            name="Guided Precision",
            origin="Cartographer Artificer Level 5",
            usage_tags=["damage"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Damage",
                        "Once per turn, when you cast a spell from your Cartographer Spells list, or hit a creature affected by your Faerie Fire with an attack roll, add your Intelligence modifier to one damage roll of it",
                    ),
                    (
                        "Concentration",
                        "Taking damage can't make you lose Concentration on Faerie Fire",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Once per turn, whenever you cast a spell from your Cartographer Spells list or hit a creature affected by your Faerie Fire with an attack roll, you can add your Intelligence modifier to one damage roll of the spell or attack.\n"
            "In addition, taking damage can't cause you to lose Concentration on Faerie Fire."
        )
        return description


class IngeniousMovement(Feature):
    def __init__(self):
        super().__init__(
            name="Ingenious Movement",
            origin="Cartographer Artificer Level 9",
            activation=FeatureActivation(range="30 Feet"),
            usage_tags=["buff", "utility"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Trigger", "You use Flash of Genius"),
                    (
                        "Effect",
                        "As part of that Reaction, you or a willing creature you can see within 30 feet teleports up to 30 feet to an unoccupied space you can see",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "When you use your Flash of Genius, you or a willing creature of your choice that you can see within 30 feet of yourself can teleport up to 30 feet to an unoccupied space you can see as part of that same Reaction."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY


class SuperiorAtlas(Feature):
    def __init__(self):
        super().__init__(
            name="Superior Atlas",
            origin="Cartographer Artificer Level 15",
            usage_tags=["heal", "utility"],
            uses=FeatureUses(
                max_uses=1,
                regain_all_on="long rest",
                current_formula="Used by Unerring Path.",
            ),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # Unerring Path's once-per-Long-Rest box is in the panel below.
        return [
            Paragraph("Your Adventurer's Atlas improves."),
            Facts(
                (
                    (
                        "Safe Haven",
                        "When a map holder would drop to 0 Hit Points but not die, it can destroy its map: its Hit Points become 2 x your Artificer level, and it teleports to an unoccupied space of its choice within 5 feet of you or another map holder",
                    ),
                    (
                        "Unerring Path",
                        "If you hold a map, cast Find the Path without a spell slot, preparation or components. Once per Long Rest.",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Your Adventurer's Atlas improves, gaining the following benefits.\n"
            "Safe Haven. When a map holder would be reduced to 0 Hit Points but not killed outright, that creature can destroy its map. The creature's Hit Points instead change to a number equal to twice your Artificer level, and the creature is teleported to an unoccupied space within 5 feet of you or another map holder of its choice.\n"
            "Unerring Path. If you are one of the map holders for your Adventurer's Atlas, you can cast Find the Path without expending a spell slot, without preparing the spell, and without needing spell components. Once you use this benefit, you can't use it again until you finish a Long Rest."
        )
        return description
