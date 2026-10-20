from Model.Content.Feature import Feature, FeatureActivation, ActionType, FeatureTarget
from Model.Content.Improvements import GrantArmorTraining
from Core.Definitions import ArmorType
from Model.Ledger.LedgerWriter import LedgerWriter
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Paragraph, Table


class AcolyteOfNature(Feature):
    def __init__(self):
        super().__init__(
            name="Acolyte of Nature", origin="Nature Domain Cleric Level 3"
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Cantrip",
                        "One from the Druid spell list; it counts as a Cleric cantrip but not against your number of Cleric cantrips known",
                    ),
                    (
                        "Skill proficiency",
                        "Animal Handling, Nature or Survival (your choice)",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "You learn one cantrip of your choice from the druid spell list. This cantrip counts as a cleric cantrip for you, but it doesn't count against the number of cleric cantrips you know. You also gain proficiency in one of the following skills of your choice: Animal Handling, Nature, or Survival."
        return description


class BonusProficiency(Feature):
    def __init__(self):
        super().__init__(
            name="Bonus Proficiency", origin="Nature Domain Cleric Level 3"
        )

    def apply(self, ledger_writer: LedgerWriter):
        # "You gain proficiency with heavy armor."
        GrantArmorTraining([ArmorType.HEAVY]).apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [Facts((("Armor proficiency", "Heavy armor"),))]

    def get_description(self, character: CharacterView) -> str:
        description = "You gain proficiency with heavy armor."
        return description


class NatureDomainSpells(Feature):
    def __init__(self):
        super().__init__(
            name="Nature Domain Spells", origin="Nature Domain Cleric Level 3"
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "From the Cleric level shown, you always have these spells prepared."
            ),
            Table(
                ("Cleric level", "Spells"),
                (
                    ("1", "Animal Friendship, Speak with Animals"),
                    ("3", "Barkskin, Spike Growth"),
                    ("5", "Plant Growth, Wind Wall"),
                    ("7", "Dominate Beast, Grasping Vine"),
                    ("9", "Insect Plague, Tree Stride"),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Your connection to this divine domain ensures you always have certain spells ready. When you reach a Cleric level specified in the Nature Domain Spells table, you thereafter always have the listed spells prepared.\n"
            "Nature Domain Spells\n"
            "Cleric Level\tSpells\n"
            "1st\tAnimal Friendship, Speak with Animals\n"
            "3rd\tBarkskin, Spike Growth\n"
            "5th\tPlant Growth, Wind Wall\n"
            "7th\tDominate Beast, Grasping Vine\n"
            "9th\tInsect Plague, Tree Stride"
        )
        return description


class CharmAnimalsAndPlantsChannelDivinity(Feature):
    def __init__(self):
        super().__init__(
            name="Channel Divinity: Charm Animals and Plants",
            origin="Nature Domain Cleric Level 3",
            activation=FeatureActivation(
                action_type=ActionType.ACTION,
                duration="1 Minute or Until Takes Damage",
                range="30 Feet",
            ),
            usage_tags=["control"],
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.CREATURE

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Use Channel Divinity to charm animals and plants."),
            Facts(
                (
                    (
                        "Action",
                        "Action, presenting your holy symbol and invoking your deity",
                    ),
                    (
                        "Target",
                        "Each Beast or Plant creature within 30 feet that can see you",
                    ),
                    ("Save", "Wisdom"),
                    (
                        "Failed save",
                        "Charmed by you for 1 minute or until it takes damage",
                    ),
                    (
                        "While charmed",
                        "It's friendly to you and creatures you designate",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You can use your Channel Divinity to charm animals and plants.\n"
            "As an action, you present your holy symbol and invoke the name of your deity. Each beast or plant creature that can see you within 30 feet of you must make a Wisdom saving throw. If the creature fails its saving throw, it is charmed by you for 1 minute or until it takes damage. While it is charmed by you, it is friendly to you and other creatures you designate."
        )
        return description


class DampenElements(Feature):
    def __init__(self):
        super().__init__(
            name="Dampen Elements",
            origin="Nature Domain Cleric Level 6",
            activation=FeatureActivation(
                action_type=ActionType.REACTION, range="30 Feet"
            ),
            usage_tags=["buff"],
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Action", "Reaction"),
                    (
                        "Trigger",
                        "You or a creature within 30 feet takes Acid, Cold, Fire, Lightning or Thunder damage",
                    ),
                    (
                        "Effect",
                        "The creature has Resistance to that instance of the damage",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "When you or a creature within 30 feet of you takes acid, cold, fire, lightning, or thunder damage, you can use your reaction to grant resistance to the creature against that instance of the damage."
        return description


class MasterOfNature(Feature):
    def __init__(self):
        super().__init__(
            name="Master of Nature",
            origin="Nature Domain Cleric Level 17",
            activation=FeatureActivation(action_type=ActionType.BONUS_ACTION),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("You gain the ability to command animals and plant creatures."),
            Facts(
                (
                    ("Action", "Bonus Action on your turn"),
                    (
                        "Target",
                        "Creatures charmed by your Charm Animals and Plants",
                    ),
                    (
                        "Effect",
                        "Verbally command what each of them will do on its next turn",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "You gain the ability to command animals and plant creatures. While creatures are charmed by your Charm Animals and Plants feature, you can take a bonus action on your turn to verbally command what each of those creatures will do on its next turn."
        return description
