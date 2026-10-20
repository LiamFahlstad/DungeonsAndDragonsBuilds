import Core.Definitions as Definitions
from Core.Definitions import ArmorType, DamageType
from Model.Content.Feature import (
    Feature,
    FeatureUses,
    FeatureActivation,
    RegainedOn,
    FeatureTarget,
)
from Model.Content.Improvements import (
    ArmorClassBonus,
    DamageImmunity,
    DamageResistance,
    GrantArmorTraining,
    GrantToolProficiency,
)
from CharacterContent.ToolProficiencies.Proficiencies import SmithsTools
from Model.Ledger.LedgerWriter import LedgerWriter
from Utils import StringUtils
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Paragraph, Table


class BonusProficiencies(Feature):
    def __init__(self):
        super().__init__(
            name="Bonus Proficiencies", origin="Forge Domain Cleric Level 3"
        )

    def apply(self, ledger_writer: LedgerWriter):
        # "You gain proficiency with heavy armor and smith's tools."
        GrantArmorTraining([ArmorType.HEAVY]).apply(ledger_writer)
        GrantToolProficiency([SmithsTools()]).apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Armor proficiency", "Heavy armor"),
                    ("Tool proficiency", "Smith's Tools"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "You gain proficiency with heavy armor and smith's tools."
        return description


class BlessingOfTheForge(Feature):
    def __init__(self):
        super().__init__(
            name="Blessing of the Forge",
            origin="Forge Domain Cleric Level 3",
            activation=FeatureActivation(
                duration="Until End of Next Long Rest or Until You Die"
            ),
            usage_tags=["buff"],
            uses=FeatureUses(max_uses=1, regain_all_on="long rest"),
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.OBJECT

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Imbue magic into a weapon or armor."),
            Facts(
                (
                    ("When", "At the end of a Long Rest"),
                    (
                        "Target",
                        "One nonmagical suit of armor or Simple or Martial weapon you touch",
                    ),
                    ("Armor", "Becomes a magic item with +1 to AC"),
                    (
                        "Weapon",
                        "Becomes a magic item with +1 to attack and damage rolls",
                    ),
                    (
                        "Duration",
                        "Until the end of your next Long Rest or until you die",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You gain the ability to imbue magic into a weapon or armor. At the end of a long rest, you can touch one nonmagical object that is a suit of armor or a simple or martial weapon. Until the end of your next long rest or until you die, the object becomes a magic item, granting a +1 bonus to AC if it's armor or a +1 bonus to attack and damage rolls if it's a weapon.\n"
            "Once you use this feature, you can't use it again until you finish a long rest."
        )
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST


class ForgeDomainSpells(Feature):
    def __init__(self):
        super().__init__(
            name="Forge Domain Spells", origin="Forge Domain Cleric Level 3"
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "From the Cleric level shown, you always have these spells prepared."
            ),
            Table(
                ("Cleric level", "Spells"),
                (
                    ("1", "Identify, Searing Smite"),
                    ("3", "Heat Metal, Magic Weapon"),
                    ("5", "Elemental Weapon, Protection from Energy"),
                    ("7", "Fabricate, Wall of Fire"),
                    ("9", "Animate Objects, Creation"),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Your connection to this divine domain ensures you always have certain spells ready. When you reach a Cleric level specified in the Forge Domain Spells table, you thereafter always have the listed spells prepared.\n"
            "Forge Domain Spells\n"
            "Cleric Level\tSpells\n"
            "1st\tIdentify, Searing Smite\n"
            "3rd\tHeat Metal, Magic Weapon\n"
            "5th\tElemental Weapon, Protection from Energy\n"
            "7th\tFabricate, Wall of Fire\n"
            "9th\tAnimate Objects, Creation"
        )
        return description


class ArtisansBlessingChannelDivinity(Feature):
    def __init__(self):
        super().__init__(
            name="Channel Divinity: Artisan's Blessing",
            origin="Forge Domain Cleric Level 3",
            usage_tags=["utility"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Use Channel Divinity to forge a simple metal item."),
            Facts(
                (
                    (
                        "Ritual",
                        "1 hour; the item appears in an unoccupied space on a surface within 5 feet",
                    ),
                    (
                        "Item",
                        "A nonmagical item with some metal, worth up to 100 gp: a simple or martial weapon, armor, ten pieces of ammunition, a set of tools, or another metal object",
                    ),
                    (
                        "Cost",
                        "Lay out metal (coins count) equal to the item's value; it transforms into the item, even its nonmetal parts",
                    ),
                    (
                        "Duplicate",
                        "Copy a nonmagical item containing metal, such as a key, if you possess the original during the ritual",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You can use your Channel Divinity to create simple items.\n"
            "You conduct an hour-long ritual that crafts a nonmagical item that must include some metal: a simple or martial weapon, a suit of armor, ten pieces of ammunition, a set of tools, or another metal object. The creation is completed at the end of the hour, coalescing in an unoccupied space of your choice on a surface within 5 feet of you.\n"
            "The thing you create can be something that is worth no more than 100 gp. As part of this ritual, you must lay out metal, which can include coins, with a value equal to the creation. The metal irretrievably coalesces and transforms into the creation at the ritual's end, magically forming even nonmetal parts of the creation.\n"
            "The ritual can create a duplicate of a nonmagical item that contains metal, such as a key, if you possess the original during the ritual."
        )
        return description


class SoulOfTheForge(Feature):
    def __init__(self):
        super().__init__(
            name="Soul of the Forge",
            origin="Forge Domain Cleric Level 6",
            passive=True,
            usage_tags=["buff"],
        )
        self._resistance = DamageResistance(DamageType.FIRE)

    def apply(self, ledger_writer: LedgerWriter):
        self._resistance.apply(ledger_writer)
        # "While wearing heavy armor, you gain a +1 bonus to AC."
        ArmorClassBonus(
            lambda cs: 1 if cs.worn_armor_type == ArmorType.HEAVY else 0
        ).apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Resistance", "Fire damage"),
                    ("AC", "+1 while wearing Heavy armor"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Your mastery of the forge grants you special abilities.\n"
            "You gain resistance to fire damage.\n"
            "While wearing heavy armor, you gain a +1 bonus to AC."
        )
        return description


class SaintOfForgeAndFire(Feature):
    def __init__(self):
        super().__init__(
            name="Saint of Forge and Fire",
            origin="Forge Domain Cleric Level 17",
            passive=True,
            usage_tags=["buff"],
        )
        # Only the fire immunity is unconditional; the bludgeoning/piercing/
        # slashing resistance is gated on wearing heavy armor AND only
        # applies to nonmagical attacks (no magical/nonmagical qualifier
        # exists on DamageResistance), so it stays prose-only.
        self._immunity = DamageImmunity(DamageType.FIRE)

    def apply(self, ledger_writer: LedgerWriter):
        self._immunity.apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Immunity", "Fire damage"),
                    (
                        "Resistance",
                        "Bludgeoning, Piercing and Slashing damage from nonmagical attacks, while wearing Heavy armor",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Your blessed affinity with fire and metal becomes more powerful.\n"
            "You gain immunity to fire damage.\n"
            "While wearing heavy armor, you have resistance to bludgeoning, piercing, and slashing damage from nonmagical attacks."
        )
        return description
