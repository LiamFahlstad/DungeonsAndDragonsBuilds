from enum import Enum

from Core.Definitions import Ability, CharacterClass, Sense
from Model.Content.Feature import (
    Feature,
    FeatureUses,
    FeatureActivation,
    RegainedOn,
    FeatureTarget,
)
from Model.Content.Improvements import GrantSense
from Model.Ledger.LedgerWriter import LedgerWriter
from Core.Rules import MAX_ABILITY_MODIFIER
from Model.Spells import FeatureSpell
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Option, Paragraph, Table, dc_formula
from CharacterContent.Spells.SpellLists import (
    AbjurationLevel3Spells,
    TransmutationLevel1Spells,
)


class DemonHunterSpecialization(str, Enum):
    """The extra column of the Demon Hunter Spells table you chose."""

    DEVOURER = "Devourer"
    HAVOC = "Havoc"
    VENGEANCE = "Vengeance"


# The Demon Hunter Spells table, verbatim: (Ranger level, All, Devourer,
# Havoc, Vengeance).
_DEMON_HUNTER_SPELLS_TABLE: tuple[tuple[str, str, str, str, str], ...] = (
    ("3", "Throw Glaive", "Consume Soul", "Fel Rush", "Infernal Strike"),
    ("5", "Sigil of Flame", "Misty Step", "Eye Beam", "Fiery Brand"),
    ("9", "Metamorphosis", "Soul Reap", "Blink", "Demon Spikes"),
    ("13", "Chaos Nova", "Collapsing Star", "Fire Shield", "Banishment"),
    (
        "17",
        "Destructive Wave",
        "Steel Wind Strike",
        "Conjure Volley",
        "Sigil of Chains",
    ),
)


def soul_fragment_count(character: CharacterView) -> int:
    """Soul fragments gained on a Long Rest: Wisdom modifier (minimum one),
    plus one at Ranger level 13 and two at Ranger level 17."""
    ranger_level = character.get_class_level(CharacterClass.RANGER)
    bonus = 2 if ranger_level >= 17 else 1 if ranger_level >= 13 else 0
    return max(1, character.get_wisdom_modifier()) + bonus


class DemonHunterSpellcasting(Feature):
    def __init__(self):
        super().__init__(
            name="Demon Hunter Spellcasting",
            origin="Demon Hunter Ranger Level 3",
            passive=True,
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Spellcasting Focus",
                        "An Arcane Focus (not a Druidic Focus) for your Ranger spells",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "You can use an Arcane Focus (not a Druidic Focus) as a Spellcasting Focus for your Ranger spells."
        return description


class DemonHunterLanguages(Feature):
    def __init__(self):
        super().__init__(
            name="Demon Hunter Languages",
            origin="Demon Hunter Ranger Level 3",
            passive=True,
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Deft Explorer languages",
                        "Choose from the language tables in chapter 2; Eredun and Nathrezim are recommended",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "When you choose languages for the Deft Explorer class feature, choose from the language tables in chapter 2. Eredun and Nathrezim are recommended."
        return description


class VoidWarrior(Feature):
    def __init__(self):
        super().__init__(
            name="Void Warrior",
            origin="Demon Hunter Ranger Level 3",
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "As a Demon Hunter, your Fighting Style can be a Fighting Style feat, the Druidic Warrior option in the Player's Handbook, or Void Warrior."
            ),
            Option(
                "Void Warrior",
                (
                    Facts(
                        (
                            (
                                "Cantrips",
                                "Two Warlock cantrips of your choice (Chill Touch and Mind Sliver are recommended). They count as Ranger spells for you.",
                            ),
                            ("Spellcasting ability", "Wisdom"),
                            (
                                "Replacing",
                                "Whenever you gain a Ranger level, replace one with another Warlock cantrip",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "As a Demon Hunter, you can choose a Fighting Style feat, the Druidic Warrior option in the Player's Handbook, or the Void Warrior option below.\n"
            "Void Warrior. You learn two Warlock cantrips of your choice. Chill Touch and Mind Sliver are recommended. The chosen cantrips count as Ranger spells for you, and Wisdom is your spellcasting ability for them. Whenever you gain a Ranger level, you can replace one of these cantrips with another Warlock cantrip."
        )
        return description


class DemonHunterSpells(Feature):
    def __init__(self, specialization: DemonHunterSpecialization):
        super().__init__(
            name="Demon Hunter Spells", origin="Demon Hunter Ranger Level 3"
        )
        self.specialization = specialization

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "From the Ranger level shown, you always have the Spells (All) spell prepared, plus the spell of one other column of your choice."
            ),
            Facts((("Chosen column", self.specialization.value),)),
            Table(
                (
                    "Ranger level",
                    "Spells (All)",
                    "Spells (Devourer)",
                    "Spells (Havoc)",
                    "Spells (Vengeance)",
                ),
                _DEMON_HUNTER_SPELLS_TABLE,
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "When you reach a Ranger level specified in the Demon Hunter Spells table, you thereafter always have the spell in the Spells (All) column prepared. You also have the additional spells listed in one other column of your choice.\n"
            f"Chosen column: {self.specialization.value}.\n"
            "Ranger Level\tSpells (All)\tSpells (Devourer)\tSpells (Havoc)\tSpells (Vengeance)\n"
            + "".join("\t".join(row) + "\n" for row in _DEMON_HUNTER_SPELLS_TABLE)
        ).rstrip("\n")
        return description


class SoulFragments(Feature):
    def __init__(self):
        super().__init__(
            name="Soul Fragments",
            origin="Demon Hunter Ranger Level 3",
            activation=FeatureActivation(range="10-Foot Emanation"),
            usage_tags=["damage", "heal", "utility"],
            uses=FeatureUses(
                max_uses=MAX_ABILITY_MODIFIER + 2,
                regain_all_on="long rest",
                current_formula="Current amount: equal to your Wisdom modifier (minimum of one), plus one at Ranger level 13 and two at Ranger level 17.",
            ),
        )

    def granted_spells(self) -> list[FeatureSpell]:
        return [
            FeatureSpell(
                TransmutationLevel1Spells.FEATHER_FALL,
                ruling="Double Jump: expend one soul fragment to cast it without a spell slot",
            ),
            FeatureSpell(
                TransmutationLevel1Spells.JUMP,
                ruling="Double Jump: expend one soul fragment to cast it without a spell slot",
            ),
        ]

    def calculate_dc(self, character: CharacterView) -> int:
        return character.calculate_difficulty_class_for_ability(Ability.WISDOM)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "You harvest the energy of souls as Tiny crystal soul fragments that fuel your special powers."
            ),
            Facts(
                (
                    (
                        "Gained",
                        "When you finish a Long Rest: Wisdom modifier (minimum one); +1 at Ranger level 13, +2 at Ranger level 17",
                    ),
                    (
                        "Lasting",
                        "Until you finish another Long Rest, when they disintegrate",
                    ),
                    (
                        "Range",
                        "A fragment more than 30 feet from you teleports onto your person",
                    ),
                    (
                        "Save DC",
                        f"Your Ranger spell save DC ({dc_formula(Ability.WISDOM)})",
                    ),
                )
            ),
            Option(
                "Double Jump",
                (
                    Facts(
                        (
                            ("Cost", "1 soul fragment"),
                            (
                                "Effect",
                                "Cast Feather Fall or Jump without expending a spell slot",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Soul Cleave",
                (
                    Facts(
                        (
                            ("Cost", "1 soul fragment"),
                            (
                                "When",
                                "Once on each of your turns, replace one attack of your Attack action",
                            ),
                            ("Area", "10-foot Emanation originating from you"),
                            ("Save", "Dexterity, each creature in the area"),
                            ("Failed", "1d12 + Wisdom modifier Psychic damage"),
                            (
                                "Healing",
                                "You regain Hit Points equal to your Wisdom modifier",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Regaining Soul Fragments",
                (
                    Facts(
                        (
                            ("Action", "Reaction"),
                            (
                                "Trigger",
                                "An enemy you can see within 30 feet of you dies",
                            ),
                            ("Effect", "Regain one expended soul fragment"),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You harvest the energy of souls to fuel some of your special powers. Whenever you finish a Long Rest, you gain a number of soul fragments equal to your Wisdom modifier (minimum of one fragment); each soul fragment is a Tiny object in the form of a crystal. These fragments last until you finish another Long Rest, at which point they disintegrate. If you ever move more than 30 feet from a fragment, the fragment immediately teleports to you, appearing somewhere on your person.\n"
            "If a soul fragment effect requires a saving throw, the DC equals your Ranger spell save DC.\n"
            "The number of soul fragments you gain when you finish a Long Rest increases when you reach Ranger levels 13 (Wisdom modifier plus one soul fragment) and 17 (Wisdom modifier plus two soul fragments).\n"
            "Using Soul Fragments. You can use soul fragments in the following ways:\n"
            "Double Jump. You can expend one soul fragment to cast Feather Fall or Jump without expending a spell slot.\n"
            "Soul Cleave. Once on each of your turns, when you take the Attack action, you can expend one soul fragment and replace one of your attacks with a whirlwind of soul energy. Each creature in a 10-foot Emanation originating from you makes a Dexterity saving throw. On a failed save, a creature takes Psychic damage equal to 1d12 plus your Wisdom modifier, and you regain Hit Points equal to your Wisdom modifier.\n"
            "Regaining Soul Fragments. When an enemy you can see within 30 feet of you dies, you can take a Reaction to regain one expended soul fragment."
        )
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def number_of_uses(self, character: CharacterView) -> int:
        return soul_fragment_count(character)

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.AREA


class SpectralSight(Feature):
    def __init__(self):
        super().__init__(
            name="Spectral Sight",
            origin="Demon Hunter Ranger Level 3",
            activation=FeatureActivation(range="10 Feet"),
        )
        self._blindsight = GrantSense(Sense.BLINDSIGHT, 10)

    def apply(self, ledger_writer: LedgerWriter):
        self._blindsight.apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [Facts((("Blindsight", "10 feet"),))]

    def get_description(self, character: CharacterView) -> str:
        description = "You have Blindsight with a range of 10 feet."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class Torment(Feature):
    def __init__(self):
        super().__init__(
            name="Torment",
            origin="Demon Hunter Ranger Level 7",
            usage_tags=["control", "damage"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Taunt",
                        "A creature marked by your Hunter's Mark has Disadvantage on attack rolls against targets other than you",
                    ),
                    (
                        "Trigger",
                        "Once per turn, you hit a creature marked by your Hunter's Mark with an attack roll with a weapon or a Ranger spell",
                    ),
                    ("Effect", "Impose one of the options below (your choice)"),
                )
            ),
            Option(
                "Aura of Pain",
                (
                    Facts(
                        (
                            (
                                "Effect",
                                "The target subtracts 1d4 from the next saving throw it makes before the end of your next turn",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Chaos Strike",
                (Facts((("Damage", "An extra 1d8 Fire damage"),)),),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "A creature marked by your Hunter's Mark spell has Disadvantage on attack rolls against targets other than you.\n"
            "Additionally, once per turn when you hit a creature marked by your Hunter's Mark with an attack roll with a weapon or a Ranger spell, you can impose one of the following effects on the target (your choice):\n"
            "Aura of Pain. The target subtracts 1d4 from the next saving throw it makes before the end of your next turn.\n"
            "Chaos Strike. The target takes an extra 1d8 Fire damage."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class IllidariKnowledge(Feature):
    def __init__(self):
        super().__init__(
            name="Illidari Knowledge",
            origin="Demon Hunter Ranger Level 11",
            usage_tags=["control"],
        )

    def granted_spells(self) -> list[FeatureSpell]:
        # Warglaive Mastery's Throw Glaive is a World of Warcraft spell that
        # isn't in the spell data yet, so only Disrupt's Counterspell is granted.
        return [
            FeatureSpell(
                AbjurationLevel3Spells.COUNTERSPELL,
                ability=Ability.WISDOM,
                ruling="Disrupt: expend two soul fragments to cast it in response to its trigger",
            ),
        ]

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("You gain new ways to use soul fragments."),
            Option(
                "Disrupt",
                (
                    Facts(
                        (
                            ("Cost", "2 soul fragments"),
                            (
                                "Effect",
                                "Cast Counterspell in response to that spell's trigger, using your spellcasting ability",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Warglaive Mastery",
                (
                    Facts(
                        (
                            ("Action", "Bonus Action"),
                            ("Cost", "1 soul fragment"),
                            (
                                "Effect",
                                "Cast Throw Glaive without expending a spell slot",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You gain new mastery over souls, granting you new ways to use soul fragments:\n"
            "Disrupt. You can expend two soul fragments to cast Counterspell in response to that spell's trigger, using your spellcasting ability.\n"
            "Warglaive Mastery. As a Bonus Action, you can expend one soul fragment to cast Throw Glaive without expending a spell slot."
        )
        return description


class SoulShatter(Feature):
    def __init__(self):
        super().__init__(
            name="Soul Shatter",
            origin="Demon Hunter Ranger Level 15",
            usage_tags=["damage"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Your mastery of fel magic reaches new heights."),
            Facts(
                (
                    (
                        "Soul Cleave damage",
                        "2d12 + Wisdom modifier (instead of 1d12)",
                    ),
                    (
                        "Rolling Initiative",
                        "Regain one soul fragment if you have none",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Your mastery of fel magic reaches new heights. When you use the Soul Cleave option of Soul Fragments, the damage increases to 2d12 plus your Wisdom modifier.\n"
            "In addition, when you roll Initiative, you regain one soul fragment if you have none."
        )
        return description


class ImprovedSpectralSight(Feature):
    def __init__(self):
        super().__init__(
            name="Improved Spectral Sight",
            origin="Demon Hunter Ranger Level 18",
            activation=FeatureActivation(range="30 Feet"),
        )
        self._truesight = GrantSense(Sense.TRUESIGHT, 30)

    def apply(self, ledger_writer: LedgerWriter):
        self._truesight.apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Replaces", "The Ranger's Feral Senses feature"),
                    ("Truesight", "30 feet"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "This feature replaces the Ranger's Feral Senses feature.\n"
            "You have Truesight with a range of 30 feet."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF
