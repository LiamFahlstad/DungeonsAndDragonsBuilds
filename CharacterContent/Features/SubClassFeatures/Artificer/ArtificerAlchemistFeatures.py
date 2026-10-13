from Model.Content.Feature import (
    ActionType,
    Feature,
    FeatureActivation,
    FeatureTarget,
    FeatureUses,
    RegainedOn,
    FeatureDice,
)
from Model.Content.Improvements import ConditionImmunity, DamageResistance
from Core.Definitions import CharacterClass, Condition, DamageType
from Model.Ledger.LedgerWriter import LedgerWriter
from Core.Rules import MAX_ABILITY_MODIFIER
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Option, Paragraph, Table


class ToolsOfTheTrade(Feature):
    def __init__(self):
        super().__init__(
            name="Tools of the Trade",
            origin="Alchemist Artificer Level 3",
            usage_tags=["utility"],
        )

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You gain the following benefits.\n"
            "Tool Proficiency. You gain proficiency with Alchemist's Supplies and the Herbalism Kit. If you already have one of these proficiencies, you gain proficiency with one other type of Artisan's Tools of your choice (or with two other types if you have both).\n"
            "Potion Crafting. When you brew a potion using the crafting rules in the Dungeon Master's Guide, the amount of time required to craft it is halved."
        )
        return description


class Spells(Feature):
    def __init__(self):
        super().__init__(name="Alchemist Spells", origin="Alchemist Artificer Level 3")

    def get_description(self, character: CharacterView) -> str:
        description = (
            "When you reach an Artificer level specified in the Alchemist Spells table, you thereafter always have the listed spells prepared.\n"
            "Alchemist Spells\n"
            "Artificer Level	Spells\n"
            "3	Healing Word, Ray of Sickness\n"
            "5	Flaming Sphere, Melf's Acid Arrow\n"
            "9	Gaseous Form, Mass Healing Word\n"
            "13	Death Ward, Vitriolic Sphere\n"
            "17	Cloudkill, Raise Dead"
        )
        return description


ELIXIR_HEALING_DICE = FeatureDice(
    "Healing Elixir",
    (
        (3, "2d8"),
        (9, "3d8"),
        (15, "4d8"),
    ),
    CharacterClass.ARTIFICER,
    note="+ Intelligence modifier",
)


class ExperimentalElixir(Feature):
    def __init__(self):
        super().__init__(
            name="Experimental Elixir",
            origin="Alchemist Artificer Level 3",
            activation=FeatureActivation(action_type=ActionType.ACTION),
            usage_tags=["heal", "buff", "utility"],
            dice=ELIXIR_HEALING_DICE,
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # The Healing elixir's dice are in the panel below.
        return [
            Paragraph("Brew magical elixirs with random effects."),
            Facts(
                (
                    (
                        "After a Long Rest",
                        "Holding Alchemist's Supplies, make 2 elixirs (3 from Artificer level 5, 4 from 9, 5 from 15); roll each one's effect on the table",
                    ),
                    (
                        "Extra elixirs",
                        "Magic action, holding Alchemist's Supplies: expend a spell slot to make one more, choosing its effect",
                    ),
                    (
                        "Drinking",
                        "Bonus Action: the creature drinks it or gives it to a creature within 5 feet",
                    ),
                    ("Lasts", "Until drunk or poured out, or your next Long Rest"),
                )
            ),
            Option(
                "Experimental Elixir",
                (
                    Table(
                        ("d6", "Elixir", "Effect"),
                        (
                            (
                                "1",
                                "Healing",
                                "Regain Healing Elixir dice (see Dice below) + your Intelligence modifier Hit Points",
                            ),
                            (
                                "2",
                                "Swiftness",
                                "Speed +10 feet for 1 hour (+15 feet from Artificer level 9, +20 from 15)",
                            ),
                            (
                                "3",
                                "Resilience",
                                "+1 AC for 10 minutes (1 hour from Artificer level 9, 8 hours from 15)",
                            ),
                            (
                                "4",
                                "Boldness",
                                "Add 1d4 to attack rolls and saving throws for 1 minute (10 minutes from Artificer level 9, 1 hour from 15)",
                            ),
                            (
                                "5",
                                "Flight",
                                "Fly Speed of 10 feet for 10 minutes (20 feet from Artificer level 9, 30 from 15)",
                            ),
                            ("6", "Your choice", "Choose one of the other effects"),
                        ),
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Whenever you finish a Long Rest while holding Alchemist's Supplies, you can use that tool to magically produce two elixirs. For each elixir, roll on the Experimental Elixir table for the elixir's effect, which is triggered when someone drinks the elixir. The elixir appears in a vial, and the vial vanishes when the elixir is drunk or poured out. If any elixir remains when you finish a Long Rest, the elixir and its vial vanish.\n"
            "Drinking an Elixir. As a Bonus Action, a creature can drink the elixir or administer it to another creature within 5 feet of itself.\n"
            "Creating Additional Elixirs. As a Magic action while holding Alchemist's Supplies, you can expend one spell slot to create another elixir. When you do so, you choose its effect from the Experimental Elixir table rather than rolling.\n"
            "When you reach certain Artificer levels, you can make an additional elixir at the end of each Long Rest: a total of three at level 5, four at level 9, and five at level 15.\n"
            "Experimental Elixir\n"
            "D6	Effect\n"
            "1	Healing. The drinker regains a number of Hit Points equal to 2d8 plus your Intelligence modifier. The number of Hit Points restored increases by 1d8 when you reach Artificer levels 9 (3d8) and 15 (4d8).\n"
            "2	Swiftness. The drinker's Speed increases by 10 feet for 1 hour. This bonus increases when you reach Artificer levels 9 (15 feet) and 15 (20 feet).\n"
            "3	Resilience. The drinker gains a +1 bonus to AC for 10 minutes. The duration increases when you reach Artificer levels 9 (1 hour) and 15 (8 hours).\n"
            "4	Boldness. The drinker can roll 1d4 and add the number rolled to every attack roll and saving throw it makes for the next minute. The duration increases when you reach Artificer levels 9 (10 minutes) and 15 (1 hour).\n"
            "5	Flight. The drinker gains a Fly Speed of 10 feet for 10 minutes. The Fly Speed increases when you reach Artificer levels 9 (20 feet) and 15 (30 feet).\n"
            "6	You determine the elixir's effect by choosing one of the other rows in this table.\n"
            + self._current_values(character)
        )
        return description

    @staticmethod
    def _current_values(character: CharacterView) -> str:
        """The elixir count and each effect at the character's Artificer level."""
        level = character.get_class_level(CharacterClass.ARTIFICER)
        tier = 2 if level >= 15 else 1 if level >= 9 else 0
        elixirs = 5 if level >= 15 else 4 if level >= 9 else 3 if level >= 5 else 2
        healing = ELIXIR_HEALING_DICE.at(character)
        speed = (10, 15, 20)[tier]
        resilience = ("10 minutes", "1 hour", "8 hours")[tier]
        boldness = ("1 minute", "10 minutes", "1 hour")[tier]
        fly = (10, 20, 30)[tier]
        intelligence_modifier = character.get_intelligence_modifier()
        return (
            f"Your elixirs right now: {elixirs} per Long Rest. "
            f"Healing {healing} + {intelligence_modifier} Hit Points; "
            f"Swiftness +{speed} feet Speed for 1 hour; "
            f"Resilience +1 AC for {resilience}; "
            f"Boldness +1d4 for {boldness}; "
            f"Flight {fly} feet Fly Speed for 10 minutes."
        )

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY


class AlchemicalSavant(Feature):
    def __init__(self):
        super().__init__(
            name="Alchemical Savant",
            origin="Alchemist Artificer Level 5",
            usage_tags=["damage", "heal"],
        )

    def get_description(self, character: CharacterView) -> str:
        description = "Whenever you cast a spell using your Alchemist's Supplies as the Spellcasting Focus, you gain a bonus to one roll of the spell. That roll must restore Hit Points or be a damage roll that deals Acid, Fire, or Poison damage. The bonus equals your Intelligence modifier (minimum bonus of +1)."
        return description


class RestorativeReagents(Feature):
    def __init__(self):
        super().__init__(
            name="Restorative Reagents",
            origin="Alchemist Artificer Level 9",
            usage_tags=["heal", "utility"],
            uses=FeatureUses(
                max_uses=MAX_ABILITY_MODIFIER,
                regain_all_on="long rest",
                current_formula="Current amount: equal to your Intelligence modifier.",
            ),
        )

    def get_description(self, character: CharacterView) -> str:
        description = "You can cast Lesser Restoration without expending a spell slot and without preparing the spell, provided you use Alchemist's Supplies as the Spellcasting Focus. You can do so a number of times equal to your Intelligence modifier (minimum of once), and you regain all expended uses when you finish a Long Rest."
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def number_of_uses(self, character: CharacterView) -> int:
        return max(1, character.get_intelligence_modifier())


class ChemicalMastery(Feature):
    def __init__(self):
        super().__init__(
            name="Chemical Mastery",
            origin="Alchemist Artificer Level 15",
            usage_tags=["damage", "buff", "utility"],
            uses=FeatureUses(
                max_uses=1,
                regain_all_on="long rest",
                current_formula="Used by Conjured Cauldron.",
            ),
        )
        self._resistances = [
            DamageResistance(DamageType.ACID),
            DamageResistance(DamageType.POISON),
        ]
        self._immunity = ConditionImmunity(Condition.POISONED)

    def apply(self, ledger_writer: LedgerWriter):
        for resistance in self._resistances:
            resistance.apply(ledger_writer)
        self._immunity.apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # Conjured Cauldron's once-per-Long-Rest box is in the panel below.
        return [
            Facts(
                (
                    (
                        "Alchemical Eruption",
                        "Once on each of your turns, when an Artificer spell you cast deals Acid, Fire or Poison damage to a target, also deal 2d8 Force damage to it",
                    ),
                    (
                        "Chemical Resistance",
                        "Resistance to Acid and Poison damage, and Immunity to the Poisoned condition",
                    ),
                    (
                        "Conjured Cauldron",
                        "Cast Tasha's Bubbling Cauldron without a spell slot, preparation or Material components, using Alchemist's Supplies as the focus. Once per Long Rest.",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You gain the following benefits.\n"
            "Alchemical Eruption. When you cast an Artificer spell that deals Acid, Fire, or Poison damage to a target, you can also deal 2d8 Force damage to that target. You can use this benefit only once on each of your turns.\n"
            "Chemical Resistance. You gain Resistance to Acid damage and Poison damage. You also gain Immunity to the Poisoned condition.\n"
            "Conjured Cauldron. You can cast Tasha's Bubbling Cauldron without expending a spell slot, without preparing the spell, and without Material components, provided you use Alchemist's Supplies as the Spellcasting Focus. Once you use this feature, you can't use it again until you finish a Long Rest."
        )
        return description

    def get_table_description(self, character: CharacterView) -> list[tuple[str, str]]:
        return [
            (
                "Alchemical Eruption",
                "When you cast an Artificer spell dealing Acid, Fire, or Poison damage, also deal 2d8 Force damage. Once per turn.",
            ),
            (
                "Chemical Resistance",
                "Resistance to Acid and Poison damage; Immunity to Poisoned condition",
            ),
            (
                "Conjured Cauldron",
                "Cast Tasha's Bubbling Cauldron with no slot, preparation, or components (Alchemist's Supplies as focus). 1/LR",
            ),
        ]
