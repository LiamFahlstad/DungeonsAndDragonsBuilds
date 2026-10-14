from Core.Definitions import WIZARD_HIT_DIE
from Model.Content.Feature import Feature, FeatureActivation, ActionType, FeatureTarget
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Paragraph


class AbjurationSavant(Feature):
    def __init__(self):
        super().__init__(name="Abjuration Savant", origin="Abjurer Wizard Level 3")

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Choose two Wizard spells from the Abjuration school, each of which must be no higher than level 2, and add them to your spellbook for free.\n"
            "In addition, whenever you gain access to a new level of spell slots in this class, you can add one Wizard spell from the Abjuration school to your spell book for free. The chosen spell must be of a level for which you have spell slots."
        )
        return description


class ArcaneWard(Feature):
    def __init__(self):
        super().__init__(
            name="Arcane Ward",
            origin="Abjurer Wizard Level 3",
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION, duration="Until Long Rest"
            ),
            usage_tags=["buff"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Weave a protective ward from your abjuration magic."),
            Facts(
                (
                    (
                        "Create",
                        "When you cast an Abjuration spell with a spell slot. Once per Long Rest; it lasts until your next Long Rest.",
                    ),
                    (
                        "Ward Hit Points",
                        "Maximum 2 x Wizard level + Intelligence modifier",
                    ),
                    (
                        "Absorb",
                        "When you take damage, the ward takes it first (after your Resistances and Vulnerabilities); you take any excess. At 0 it absorbs nothing, but stays.",
                    ),
                    (
                        "Recharge",
                        "Casting an Abjuration spell with a slot restores 2 x the slot's level. Or as a Bonus Action, expend a spell slot to restore 2 x its level.",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You can weave magic around yourself for protection. When you cast an Abjuration spell with a spell slot, you can simultaneously use a strand of the spell's magic to create a magical ward on yourself that lasts until you finish a Long Rest. The ward has a Hit Point maximum equal to twice your Wizard level plus your Intelligence modifier. Whenever you take damage, the ward takes the damage instead, and if you have any Resistances or Vulnerabilities, apply them before reducing the ward's Hit Points. If the damage reduces the ward to 0 Hit Points, you take any remaining damage. While the ward has 0 Hit Points, it can't absorb damage, but its magic remains.\n"
            "Whenever you cast an Abjuration spell with a spell slot, the ward regains a number of Hit Points equal to twice the level of the spell slot. Alternatively, as a Bonus Action, you can expend a spell slot, and the ward regains a number of Hit Points equal to twice the level of the spell slot expended.\n"
            "Once you create the ward, you can't create it again until you finish a Long Rest."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class ProjectedWard(Feature):
    def __init__(self):
        super().__init__(
            name="Projected Ward",
            origin="Abjurer Wizard Level 6",
            activation=FeatureActivation(
                action_type=ActionType.REACTION, range="30 Feet"
            ),
            usage_tags=["buff"],
        )

    def get_description(self, character: CharacterView) -> str:
        description = "When a creature that you can see within 30 feet of yourself takes damage, you can take a Reaction to cause your Arcane Ward to absorb that damage. If this damage reduces the ward to 0 Hit Points, the warded creature takes any remaining damage. If the creature has any Resistances or Vulnerabilities, apply them before reducing the ward's Hit Points."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY


class SpellBreaker(Feature):
    def __init__(self):
        super().__init__(
            name="Spell Breaker",
            origin="Abjurer Wizard Level 10",
            activation=FeatureActivation(action_type=ActionType.BONUS_ACTION),
        )

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You always have the Counterspell and Dispel Magic spells prepared. In addition, you can cast Dispel Magic as a Bonus Action, and you can add your Proficiency Bonus to its ability check.\n"
            "When you cast either spell with a spell slot, that slot isn't expended if the spell fails to stop a spell."
        )
        return description


class SpellResistance(Feature):
    def __init__(self):
        super().__init__(
            name="Spell Resistance",
            origin="Abjurer Wizard Level 14",
            usage_tags=["buff"],
        )

    def get_description(self, character: CharacterView) -> str:
        description = "You have Advantage on saving throws against spells, and you have Resistance to the damage of spells."
        return description
