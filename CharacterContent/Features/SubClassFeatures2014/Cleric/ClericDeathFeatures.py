from Core.Definitions import CharacterClass
from Model.Content.Feature import Feature, FeatureTarget
from Model.Content.Improvements import GrantWeaponProficiency
from CharacterContent.Items.Weapons import WeaponProficiency
from Model.Ledger.LedgerWriter import LedgerWriter
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Paragraph, Table


class BonusProficiency(Feature):
    def __init__(self):
        super().__init__(name="Bonus Proficiency", origin="Death Domain Cleric Level 3")

    def apply(self, ledger_writer: LedgerWriter):
        # "You gain proficiency with martial weapons."
        GrantWeaponProficiency([WeaponProficiency.MARTIAL]).apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [Facts((("Weapon proficiency", "Martial weapons"),))]

    def get_description(self, character: CharacterView) -> str:
        description = "You gain proficiency with martial weapons."
        return description


class Reaper(Feature):
    def __init__(self):
        super().__init__(name="Reaper", origin="Death Domain Cleric Level 3")

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Cantrip",
                        "One Necromancy cantrip of your choice from any spell list",
                    ),
                    (
                        "Second target",
                        "A Necromancy cantrip that normally targets one creature can instead target two within range and within 5 feet of each other",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "You learn one necromancy cantrip of your choice from any spell list. When you cast a necromancy cantrip that normally targets only one creature, the spell can instead target two creatures within range and within 5 feet of each other."
        return description


class DeathDomainSpells(Feature):
    def __init__(self):
        super().__init__(
            name="Death Domain Spells", origin="Death Domain Cleric Level 3"
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "From the Cleric level shown, you always have these spells prepared."
            ),
            Table(
                ("Cleric level", "Spells"),
                (
                    ("1", "False Life, Ray of Sickness"),
                    ("3", "Blindness/Deafness, Ray of Enfeeblement"),
                    ("5", "Animate Dead, Vampiric Touch"),
                    ("7", "Blight, Death Ward"),
                    ("9", "Antilife Shell, Cloudkill"),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Your connection to this divine domain ensures you always have certain spells ready. When you reach a Cleric level specified in the Death Domain Spells table, you thereafter always have the listed spells prepared.\n"
            "Death Domain Spells\n"
            "Cleric Level\tSpells\n"
            "1st\tFalse Life, Ray of Sickness\n"
            "3rd\tBlindness/Deafness, Ray of Enfeeblement\n"
            "5th\tAnimate Dead, Vampiric Touch\n"
            "7th\tBlight, Death Ward\n"
            "9th\tAntilife Shell, Cloudkill"
        )
        return description


class TouchOfDeathChannelDivinity(Feature):
    def __init__(self):
        super().__init__(
            name="Channel Divinity: Touch of Death",
            origin="Death Domain Cleric Level 3",
            usage_tags=["damage"],
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "Use Channel Divinity to destroy another creature's life force by touch."
            ),
            Facts(
                (
                    ("Trigger", "You hit a creature with a melee attack"),
                    ("Extra Necrotic damage", "5 + twice your Cleric level"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "You can use Channel Divinity to destroy another creature's life force by touch. When you hit a creature with a melee attack, you can use Channel Divinity to deal extra necrotic damage to the target. The damage equals 5 + twice your cleric level."
        level = character.get_class_level(CharacterClass.CLERIC)
        description += f"\nRight now: {5 + 2 * level} extra necrotic damage."
        return description


class InescapableDestruction(Feature):
    def __init__(self):
        super().__init__(
            name="Inescapable Destruction", origin="Death Domain Cleric Level 6"
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Your ability to channel negative energy becomes more potent."),
            Facts(
                (
                    ("Applies to", "Your Cleric spells and Channel Divinity options"),
                    (
                        "Effect",
                        "Their Necrotic damage ignores Resistance to Necrotic damage",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "Your ability to channel negative energy becomes more potent. Necrotic damage dealt by your cleric spells and Channel Divinity options ignores resistance to necrotic damage."
        return description


class ImprovedReaper(Feature):
    def __init__(self):
        super().__init__(name="Improved Reaper", origin="Death Domain Cleric Level 17")

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Applies to",
                        "Necromancy spells of levels 1-5 that target only one creature",
                    ),
                    (
                        "Second target",
                        "Target two creatures within range and within 5 feet of each other",
                    ),
                    (
                        "Consumed components",
                        "You must provide them for each target",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "When you cast a necromancy spell of 1st through 5th level that targets only one creature, the spell can instead target two creatures within range and within 5 feet of each other. If the spell consumes its material components, you must provide them for each target."
        return description
