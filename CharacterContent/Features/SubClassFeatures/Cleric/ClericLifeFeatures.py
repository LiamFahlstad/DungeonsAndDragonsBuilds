from Model.Content.Feature import Feature, FeatureActivation, ActionType, FeatureTarget
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Paragraph, Table


class DiscipleOfLife(Feature):
    def __init__(self):
        super().__init__(
            name="Disciple of Life",
            origin="Life Domain Cleric Level 3",
            usage_tags=["heal"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Trigger",
                        "A spell you cast with a spell slot restores Hit Points to a creature",
                    ),
                    (
                        "Effect",
                        "It regains an extra 2 + the slot's level Hit Points, on the turn you cast the spell",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "When a spell you cast with a spell slot restores Hit Points to a creature, that creature regains additional Hit Points on the turn you cast the spell. The additional Hit Points equal 2 plus the spell slot's level."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY


class LifeDomainSpells(Feature):
    def __init__(self):
        super().__init__(name="Life Domain Spells", origin="Life Domain Cleric Level 3")

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "From the Cleric level shown, you always have these spells prepared."
            ),
            Table(
                ("Cleric level", "Spells"),
                (
                    ("3", "Aid, Bless, Cure Wounds, Lesser Restoration"),
                    ("5", "Mass Healing Word, Revivify"),
                    ("7", "Aura of Life, Death Ward"),
                    ("9", "Greater Restoration, Mass Cure Wounds"),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "Your connection to this divine domain ensures you always have certain spells ready. When you reach a Cleric level specified in the Life Domain Spells table, you thereafter always have the listed spells prepared."
        return description


class PreserveLife(Feature):
    def __init__(self):
        super().__init__(
            name="Preserve Life",
            origin="Life Domain Cleric Level 3",
            activation=FeatureActivation(
                action_type=ActionType.ACTION, range="30 Feet"
            ),
            usage_tags=["heal"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Present your Holy Symbol to evoke healing energy."),
            Facts(
                (
                    ("Action", "Magic action"),
                    ("Cost", "One use of Channel Divinity"),
                    ("Target", "Bloodied creatures within 30 feet (can include you)"),
                    (
                        "Heal",
                        "Five times your Cleric level Hit Points, divided among them",
                    ),
                    ("Limit", "No creature is healed above half its Hit Point maximum"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "As a Magic action, you present your Holy Symbol and expend a use of your Channel Divinity to evoke healing energy that can restore a number of Hit Points equal to five times your Cleric level. Choose Bloodied creatures within 30 feet of yourself (which can include you), and divide those Hit Points among them. This feature can restore a creature to no more than half its Hit Point maximum."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY


class BlessedHealer(Feature):
    def __init__(self):
        super().__init__(
            name="Blessed Healer",
            origin="Life Domain Cleric Level 6",
            usage_tags=["heal"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Trigger",
                        "You cast a spell with a spell slot that restores Hit Points to one or more creatures other than you",
                    ),
                    (
                        "Effect",
                        "Immediately after, you regain 2 + the slot's level Hit Points",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "The healing spells you cast on others heal you as well. Immediately after you cast a spell with a spell slot that restores Hit Points to one or more creatures other than yourself, you regain Hit Points equal to 2 plus the spell slot's level."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class SupremeHealing(Feature):
    def __init__(self):
        super().__init__(
            name="Supreme Healing",
            origin="Life Domain Cleric Level 17",
            usage_tags=["heal"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Trigger",
                        "You'd roll dice to restore Hit Points with a spell or Channel Divinity",
                    ),
                    (
                        "Effect",
                        "Don't roll: use the highest number on each die (2d6 restores 12)",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "When you would normally roll one or more dice to restore Hit Points to a creature with a spell or Channel Divinity, don't roll those dice for the healing; instead use the highest number possible for each die. For example, instead of restoring 2d6 Hit Points to a creature with a spell, you restore 12."
        return description
