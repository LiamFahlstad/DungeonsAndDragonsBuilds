from Core.Definitions import DamageType
from Model.Content.Feature import (
    ActionType,
    Feature,
    FeatureActivation,
    FeatureTarget,
    FeatureUses,
    RegainedOn,
)
from Model.Content.Improvements import DamageResistance
from Model.Ledger.LedgerWriter import LedgerWriter
from CharacterContent.Spells.SpellLists import (
    NecromancyLevel3Spells,
    WizardLevel1Spells,
)
from Model.Spells import FeatureSpell
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Option, Paragraph, Table


class NecromancySavant(Feature):
    def __init__(self):
        super().__init__(name="Necromancy Savant", origin="Necromancer Wizard Level 3")

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Add Necromancy spells to your spellbook for free."),
            Facts(
                (
                    (
                        "Now",
                        "Two Wizard Necromancy spells, each no higher than level 2",
                    ),
                    (
                        "New spell slot levels",
                        "Whenever you gain access to a new level of spell slots in this class, one Wizard Necromancy spell of a level you have slots for",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Choose two Wizard spells from the Necromancy school, each of which must be no higher than level 2, and add them to your spellbook for free.\n"
            "In addition, whenever you gain access to a new level of spell slots in this class, you can add one Wizard spell from the Necromancy school to your spellbook for free. The chosen spell must be of a level for which you have spell slots."
        )
        return description


class NecromancySpellbook(Feature):
    def __init__(self):
        super().__init__(
            name="Necromancy Spellbook",
            origin="Necromancer Wizard Level 3",
            usage_tags=["heal", "summon"],
        )
        self._resistance = DamageResistance(DamageType.NECROTIC)

    def granted_spells(self) -> list[FeatureSpell]:
        return [
            FeatureSpell(
                WizardLevel1Spells.FIND_FAMILIAR,
                ruling="In your spellbook; can take a Skeleton or Zombie form, or a normal form with the Undead creature type",
            )
        ]

    def apply(self, ledger_writer: LedgerWriter):
        self._resistance.apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "Your spellbook's necromantic secrets grant you additional powers."
            ),
            Option(
                "Necrotic Resistance",
                (Paragraph("You have Resistance to Necrotic damage."),),
            ),
            Option(
                "Undead Familiar",
                (
                    Facts(
                        (
                            ("Spell", "Find Familiar appears in your spellbook"),
                            (
                                "Forms",
                                "A normal familiar form (whose creature type can be Undead), or a Skeleton or Zombie (Player's Handbook, appendix B)",
                            ),
                            (
                                "Attack",
                                "When you take the Attack action, forgo one of your attacks to let your familiar make one attack of its own with its Reaction",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Undead Vitality",
                (
                    Facts(
                        (
                            (
                                "Trigger",
                                "You cast a Necromancy spell using a spell slot",
                            ),
                            ("Range", "60 feet"),
                            ("Target", "One Undead creature you can see"),
                            (
                                "Heal",
                                "It regains Hit Points equal to the slot's level + your Wizard level",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Your spellbook's necromantic secrets grant you additional powers. You gain the following benefits.\n"
            "    * Necrotic Resistance: You have Resistance to Necrotic damage.\n"
            "    * Undead Familiar: The Find Familiar spell appears in your spellbook. When you cast the spell, you choose one of the normal forms for your familiar or one of the following special forms: Skeleton or Zombie (see appendix B of the Player's Handbook for the familiar's stat block). When you choose one of the normal forms, you can choose Undead as its creature type. Additionally, when you take the Attack action, you can forgo one of your own attacks to allow your familiar to make one attack of its own with its Reaction.\n"
            "    * Undead Vitality: When you cast a Necromancy spell using a spell slot, you can choose an Undead creature you can see within 60 feet of yourself to regain a number of Hit Points equal to the level of the spell slot expended plus your Wizard level."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY


class GravePower(Feature):
    def __init__(self):
        super().__init__(name="Grave Power", origin="Necromancer Wizard Level 6")

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("While holding your spellbook, you gain these benefits."),
            Facts(
                (
                    (
                        "Grave Resilience",
                        "When you use Arcane Recovery, your Exhaustion level, if any, decreases by 1",
                    ),
                    (
                        "Overwhelming Necrosis",
                        "Damage from your Wizard spells and Wizard features ignores Resistance to Necrotic damage",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You have discovered more necromantic insights and inscribed them in your spellbook. While holding your spellbook, you gain the following benefits.\n"
            "    * Grave Resilience: When you use Arcane Recovery, your Exhaustion level, if any, decreases by 1.\n"
            "    * Overwhelming Necrosis: Damage from your Wizard spells and Wizard features ignores Resistance to Necrotic damage."
        )
        return description


class UndeadThralls(Feature):
    def __init__(self):
        super().__init__(
            name="Undead Thralls",
            origin="Necromancer Wizard Level 6",
            activation=FeatureActivation(range="60 Feet"),
            usage_tags=["summon", "damage"],
            uses=FeatureUses(max_uses=1, regain_all_on="long rest"),
        )

    def granted_spells(self) -> list[FeatureSpell]:
        return [
            FeatureSpell(
                NecromancyLevel3Spells.ANIMATE_DEAD,
                ruling="Always prepared; cast once without a spell slot per Long Rest. Whenever you start casting it, you can increase its effective level by 1",
            )
        ]

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # The free casting's once-per-Long-Rest box is in the panel below.
        return [
            Paragraph(
                "You always have Animate Dead prepared, and you can cast it once without a spell slot per Long Rest. Whenever you start casting it, you can increase its effective level by 1."
            ),
            Option(
                "While holding your spellbook",
                (
                    Facts(
                        (
                            (
                                "Undead Fortitude",
                                "An Undead you create or summon with a Necromancy spell has its Hit Point maximum and current Hit Points increased by your Intelligence modifier + half your Wizard level (round down)",
                            ),
                            (
                                "Withering Strike",
                                "An Undead you control within 60 feet of you that hits with an attack roll deals extra Necrotic damage equal to your Intelligence modifier (minimum of 1)",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You always have Animate Dead prepared and can cast it without expending a spell slot, but you must finish a Long Rest before you can cast it in this way again. Whenever you start casting the spell, you can increase the spell's effective level by 1.\n"
            "In addition, while holding your spellbook, you gain the following benefits.\n"
            "    * Undead Fortitude: Whenever you cast a Necromancy spell that creates or summons an Undead, the Undead's Hit Point maximum and current Hit Points increase by a number equal to your Intelligence modifier plus half your Wizard level (round down).\n"
            "    * Withering Strike: Whenever an Undead you control within 60 feet of you hits a creature with an attack roll, the Undead deals extra Necrotic damage equal to your Intelligence modifier (minimum of 1 Necrotic damage)."
        )
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY


class HarvestUndead(Feature):
    def __init__(self):
        super().__init__(
            name="Harvest Undead",
            origin="Necromancer Wizard Level 10",
            activation=FeatureActivation(action_type=ActionType.REACTION),
            usage_tags=["heal"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Drain one of your Undead to keep yourself standing."),
            Facts(
                (
                    ("Action", "Reaction"),
                    (
                        "Trigger",
                        "Immediately after you become Bloodied from taking damage but aren't reduced to 0 Hit Points",
                    ),
                    (
                        "Target",
                        "An Undead creature under your control that you can see; it drops to 0 Hit Points",
                    ),
                    ("Heal", "You regain Hit Points equal to your Wizard level"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "You have learned more secrets about the nuances of life and death. Immediately after you become Bloodied but aren't reduced to 0 Hit Points from taking damage, you can take a Reaction to reduce an Undead creature under your control that you can see to 0 Hit Points. You then immediately regain a number of Hit Points equal to your Wizard level."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class DeathsMaster(Feature):
    def __init__(self):
        super().__init__(
            name="Death's Master",
            origin="Necromancer Wizard Level 14",
            activation=FeatureActivation(range="60 Feet"),
            usage_tags=["buff", "damage"],
            uses=FeatureUses(max_uses=1, regain_all_on="long rest"),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # Bolster Undead's once-per-Long-Rest box is in the panel below.
        return [
            Paragraph("While holding your spellbook, you gain these benefits."),
            Option(
                "Bolster Undead",
                (
                    Facts(
                        (
                            ("Action", "Bonus Action, once per Long Rest"),
                            ("Range", "60 feet"),
                            (
                                "Target",
                                "Any number of Undead you created or summoned with a Necromancy spell",
                            ),
                            (
                                "Effect",
                                "Each gains Temporary Hit Points equal to your Wizard level",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Extinguish Undead",
                (
                    Facts(
                        (
                            (
                                "Trigger",
                                "An Undead creature you can see is reduced to 0 Hit Points",
                            ),
                            (
                                "Damage",
                                "Roll d6s equal to half its unexpended Hit Dice (round up, minimum of 1d6)",
                            ),
                            (
                                "Area",
                                "Each creature in a 10-foot Emanation from the Undead makes a Dexterity save",
                            ),
                            (
                                "Cost",
                                "None for an Undead you control; for one you don't, take a Reaction and expend a level 5+ spell slot",
                            ),
                        )
                    ),
                    Table(
                        ("Save", "Result"),
                        (
                            (
                                "Failed",
                                "Necrotic damage equal to the roll, and it can't take Reactions until the start of its next turn",
                            ),
                            ("Succeeded", "Half as much damage only"),
                        ),
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Abstruse rituals within your spellbook allow you mastery over undeath. While holding your spellbook, you gain the following benefits.\n"
            "    * Bolster Undead: As a Bonus Action, choose any number of Undead you have created or summoned with a Necromancy spell that are within 60 feet of you. Those Undead each gain Temporary Hit Points equal to your Wizard level. Once you use this Bonus Action, you can't do so again until you finish a Long Rest.\n"
            "    * Extinguish Undead: When an Undead creature you can see is reduced to 0 Hit Points, you can cause it to explode with necrotic energy. Roll a number of d6s equal to half the creature's unexpended Hit Dice (round up, minimum of 1d6), and add them together. Each creature in a 10-foot Emanation originating from the Undead makes a Dexterity saving throw. On a failed save, a target takes Necrotic damage equal to the number rolled and can't take Reactions until the start of its next turn. On a successful save, a target takes half as much damage only. When you use this feature to explode an Undead creature you don't control, you must take a Reaction and expend a level 5+ spell slot to do so."
        )
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY
