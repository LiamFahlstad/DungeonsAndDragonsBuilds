from Core.Rules import MAX_ABILITY_MODIFIER
from Model.Content.Feature import (
    ActionType,
    Feature,
    FeatureActivation,
    FeatureTarget,
    FeatureUses,
    RegainedOn,
)
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Paragraph


class ConjurationSavant(Feature):
    def __init__(self):
        super().__init__(name="Conjuration Savant", origin="Conjurer Wizard Level 3")

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Add Conjuration spells to your spellbook for free."),
            Facts(
                (
                    (
                        "Now",
                        "Two Wizard Conjuration spells, each no higher than level 2",
                    ),
                    (
                        "New spell slot levels",
                        "Whenever you gain access to a new level of spell slots in this class, one Wizard Conjuration spell of a level you have slots for",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Choose two Wizard spells from the Conjuration school, each of which must be no higher than level 2, and add them to your spellbook for free.\n"
            "In addition, whenever you gain access to a new level of spell slots in this class, you can add one Wizard spell from the Conjuration school to your spellbook for free. The chosen spell must be of a level for which you have spell slots."
        )
        return description


class BenignTransposition(Feature):
    def __init__(self):
        super().__init__(
            name="Benign Transposition",
            origin="Conjurer Wizard Level 3",
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION, range="30 Feet"
            ),
            usage_tags=["utility"],
            uses=FeatureUses(
                max_uses=MAX_ABILITY_MODIFIER,
                regain_all_on="long rest",
                current_formula="Current amount: equal to your Intelligence modifier (minimum of once).",
            ),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # Uses (Intelligence modifier, minimum of once) are in the panel below.
        return [
            Paragraph("Teleport across the battlefield, alone or by swapping places."),
            Facts(
                (
                    ("Action", "Bonus Action"),
                    ("Range", "30 feet (60 feet from Wizard level 6)"),
                    ("Teleport", "To an unoccupied space you can see"),
                    (
                        "Swap",
                        "Instead choose a space occupied by a willing Medium or smaller creature: you both teleport, swapping places",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "As a Bonus Action, you teleport up to 30 feet to an unoccupied space that you can see. Alternatively, you can choose a space within range that is occupied by a Medium or smaller creature. If that creature is willing, you both teleport, swapping places.\n"
            "You can use this feature a number of times equal to your Intelligence modifier (minimum of once), and you regain all expended uses when you finish a Long Rest."
        )
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF

    def number_of_uses(self, character: CharacterView) -> int:
        return max(1, character.get_intelligence_modifier())


class DistantTransposition(Feature):
    def __init__(self):
        super().__init__(
            name="Distant Transposition",
            origin="Conjurer Wizard Level 6",
            activation=FeatureActivation(range="60 Feet"),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Range", "Benign Transposition's range increases to 60 feet"),
                    (
                        "Restore",
                        "Expend a level 3+ spell slot (no action required) to restore one use",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "The range of your Benign Transposition feature increases to 60 feet. Additionally, you can restore one use of it by expending a level 3+ spell slot (no action required)."
        return description


class DurableSummons(Feature):
    def __init__(self):
        super().__init__(
            name="Durable Summons",
            origin="Conjurer Wizard Level 6",
            usage_tags=["buff"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Trigger",
                        "You cast a Conjuration spell using a spell slot to summon or create a creature",
                    ),
                    (
                        "Temporary Hit Points",
                        "Twice your Wizard level, when the creature first appears",
                    ),
                    (
                        "Resistance",
                        "While it has these Temporary Hit Points: every damage type except Force, Necrotic, Psychic and Radiant",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "When you cast a Conjuration spell to summon or create a creature using a spell slot, that creature gains Temporary Hit Points equal to twice your Wizard level when it first appears. While it has these Temporary Hit Points, the creature has Resistance to every damage type except Force, Necrotic, Psychic, and Radiant."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY


class FocusedConjuration(Feature):
    def __init__(self):
        super().__init__(name="Focused Conjuration", origin="Conjurer Wizard Level 10")

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "Taking damage can't break your Concentration on Conjuration spells."
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Taking damage can't break your Concentration on Conjuration spells."
        )
        return description


class SplinteredSummons(Feature):
    def __init__(self):
        super().__init__(
            name="Splintered Summons",
            origin="Conjurer Wizard Level 14",
            usage_tags=["summon"],
            uses=FeatureUses(max_uses=1, regain_all_on="long rest"),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # The once-per-Long-Rest box is in the panel below.
        return [
            Paragraph("Split one summoned spirit into two weaker copies."),
            Facts(
                (
                    (
                        "Trigger",
                        "You use a spell slot to cast a Conjuration spell that summons a spirit whose stat block is in the spell description, such as Summon Aberration",
                    ),
                    (
                        "Effect",
                        "Summon two creatures instead of one, each of the same kind and using the spell's stat block and rules, in different unoccupied spaces of your choice within the spell's range",
                    ),
                    (
                        "Drawback",
                        "Each creature's Hit Point maximum and current Hit Points are halved. If you lose Concentration, both disappear.",
                    ),
                    (
                        "Restore",
                        "Expend a level 5+ spell slot (no action required)",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "When you use a spell slot to cast a Conjuration spell that summons a spirit whose stat block is included in the spell description, such as Summon Aberration, you can modify the spell to summon two creatures with the spell instead of one. Each creature is of the same kind, uses the stat block and rules denoted by the spell, and manifests in a different unoccupied space of your choice within the spell's range, but the summoned creatures' Hit Point maximums and current Hit Points are halved. If you lose Concentration on the spell, both creatures disappear.\n"
            "Once you use this feature to modify a spell in this way, you must finish a Long Rest before you can do so again. You can also restore your use of it by expending a level 5+ spell slot (no action required)."
        )
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY
