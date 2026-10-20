import Core.Definitions as Definitions
from Core.Definitions import ArmorType
from Model.Content.Feature import (
    Feature,
    FeatureUses,
    FeatureActivation,
    ActionType,
    RegainedOn,
    FeatureTarget,
)
from Model.Content.Improvements import GrantArmorTraining
from Model.Ledger.LedgerWriter import LedgerWriter
from Core.Rules import MAX_ABILITY_MODIFIER
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Paragraph, Table


class BonusProficiencies(Feature):
    def __init__(self):
        super().__init__(
            name="Bonus Proficiencies", origin="Order Domain Cleric Level 3"
        )

    def apply(self, ledger_writer: LedgerWriter):
        # "You gain proficiency with heavy armor." (the skill choice isn't modelled)
        GrantArmorTraining([ArmorType.HEAVY]).apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Armor proficiency", "Heavy armor"),
                    ("Skill proficiency", "Intimidation or Persuasion (your choice)"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "You gain proficiency with heavy armor. You also gain proficiency in the Intimidation or Persuasion skill (your choice)."
        return description


class VoiceOfAuthority(Feature):
    def __init__(self):
        super().__init__(
            name="Voice of Authority",
            origin="Order Domain Cleric Level 3",
            usage_tags=["utility"],
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Invoke the power of law to embolden an ally to attack."),
            Facts(
                (
                    (
                        "Trigger",
                        "You cast a spell with a level 1+ spell slot that targets an ally",
                    ),
                    (
                        "Ally's attack",
                        "Immediately after the spell, it can use its Reaction to make one weapon attack",
                    ),
                    ("Attack target", "A creature of your choice that you can see"),
                    (
                        "Several allies",
                        "If the spell targets more than one ally, you choose which one attacks",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You can invoke the power of law to embolden an ally to attack. If you cast a spell with a spell slot of 1st level or higher and target an ally with the spell, that ally can use their reaction immediately after the spell to make one weapon attack against a creature of your choice that you can see.\n"
            "If the spell targets more than one ally, you choose the ally who can make the attack."
        )
        return description


class OrderDomainSpells(Feature):
    def __init__(self):
        super().__init__(
            name="Order Domain Spells", origin="Order Domain Cleric Level 3"
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "From the Cleric level shown, you always have these spells prepared."
            ),
            Table(
                ("Cleric level", "Spells"),
                (
                    ("1", "Command, Heroism"),
                    ("3", "Hold Person, Zone of Truth"),
                    ("5", "Mass Healing Word, Slow"),
                    ("7", "Compulsion, Locate Creature"),
                    ("9", "Commune, Dominate Person"),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Your connection to this divine domain ensures you always have certain spells ready. When you reach a Cleric level specified in the Order Domain Spells table, you thereafter always have the listed spells prepared.\n"
            "Order Domain Spells\n"
            "Cleric Level\tSpells\n"
            "1st\tCommand, Heroism\n"
            "3rd\tHold Person, Zone of Truth\n"
            "5th\tMass Healing Word, Slow\n"
            "7th\tCompulsion, Locate Creature\n"
            "9th\tCommune, Dominate Person"
        )
        return description


class OrdersDemandChannelDivinity(Feature):
    def __init__(self):
        super().__init__(
            name="Channel Divinity: Order's Demand",
            origin="Order Domain Cleric Level 3",
            activation=FeatureActivation(
                action_type=ActionType.ACTION,
                duration="Until End of Your Next Turn or Until Takes Damage",
                range="30 Feet",
            ),
            usage_tags=["control"],
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "Use Channel Divinity to exert an intimidating presence over others."
            ),
            Facts(
                (
                    ("Action", "Action, presenting your holy symbol"),
                    (
                        "Target",
                        "Each creature of your choice within 30 feet that can see or hear you",
                    ),
                    ("Save", "Wisdom"),
                    (
                        "Failed save",
                        "Charmed by you until the end of your next turn or until it takes any damage",
                    ),
                    ("Disarm", "You can also make it drop what it's holding"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You can use your Channel Divinity to exert an intimidating presence over others.\n"
            "As an action, you present your holy symbol, and each creature of your choice that can see or hear you within 30 feet of you must succeed on a Wisdom saving throw or be charmed by you until the end of your next turn or until the charmed creature takes any damage. You can also cause any of the charmed creatures to drop what they are holding when they fail the saving throw."
        )
        return description


class EmbodimentOfTheLaw(Feature):
    def __init__(self):
        super().__init__(
            name="Embodiment of the Law",
            origin="Order Domain Cleric Level 6",
            usage_tags=["utility"],
            uses=FeatureUses(
                max_uses=MAX_ABILITY_MODIFIER,
                regain_all_on="long rest",
                current_formula="Current amount: equal to your Wisdom modifier.",
            ),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # Uses (Wisdom modifier, minimum of once) are in the panel below.
        return [
            Paragraph(
                "You become remarkably adept at channeling magical energy to compel others."
            ),
            Facts(
                (
                    (
                        "Applies to",
                        "Enchantment spells cast with a level 1+ spell slot whose casting time is normally 1 action",
                    ),
                    (
                        "Effect",
                        "Change the casting time to 1 Bonus Action for this casting",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You become remarkably adept at channeling magical energy to compel others.\n"
            "If you cast a spell of the enchantment school using a spell slot of 1st level or higher, you can change the spell's casting time to 1 bonus action for this casting, provided the spell's casting time is normally 1 action.\n"
            "You can use this feature a number of times equal to your Wisdom modifier (minimum of once), and you regain all expended uses of it when you finish a long rest."
        )
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def number_of_uses(self, character: CharacterView) -> int:
        return max(1, character.get_wisdom_modifier())


class OrdersWrath(Feature):
    def __init__(self):
        super().__init__(
            name="Order's Wrath",
            origin="Order Domain Cleric Level 17",
            usage_tags=["damage", "control"],
            activation=FeatureActivation(duration="Until Start of Your Next Turn"),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "Enemies you designate for destruction wilt under the combined efforts of you and your allies."
            ),
            Facts(
                (
                    (
                        "Trigger",
                        "You deal your Divine Strike damage to a creature on your turn",
                    ),
                    (
                        "Curse",
                        "The creature is cursed until the start of your next turn",
                    ),
                    (
                        "Effect",
                        "The next time an ally hits it with an attack, it also takes 2d8 Psychic damage and the curse ends",
                    ),
                    ("Frequency", "Once per turn"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "Enemies you designate for destruction wilt under the combined efforts of you and your allies. If you deal your Divine Strike damage to a creature on your turn, you can curse that creature until the start of your next turn. The next time one of your allies hits the cursed creature with an attack, the target also takes 2d8 psychic damage, and the curse ends. You can curse a creature in this way only once per turn."
        return description
