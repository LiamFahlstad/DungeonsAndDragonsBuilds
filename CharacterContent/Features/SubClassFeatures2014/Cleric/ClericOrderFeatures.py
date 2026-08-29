import Core.Definitions as Definitions
from Core.Definitions import Ability
from CharacterContent.Features.Core.BaseFeatures import Feature, FeatureActivation, ActionType
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class BonusProficiencies(Feature):
    def __init__(self):
        super().__init__(name="Bonus Proficiencies", origin="Order Domain Cleric Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You gain proficiency with heavy armor. You also gain proficiency in the Intimidation or Persuasion skill (your choice)."
        return description


class VoiceOfAuthority(Feature):
    def __init__(self):
        super().__init__(name="Voice of Authority", origin="Order Domain Cleric Level 3", usage_tags=["utility"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can invoke the power of law to embolden an ally to attack. If you cast a spell with a spell slot of 1st level or higher and target an ally with the spell, that ally can use their reaction immediately after the spell to make one weapon attack against a creature of your choice that you can see.\n"
            "If the spell targets more than one ally, you choose the ally who can make the attack."
        )
        return description


class OrderDomainSpells(Feature):
    def __init__(self):
        super().__init__(name="Order Domain Spells", origin="Order Domain Cleric Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
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
            activation=FeatureActivation(action_type=ActionType.ACTION, duration="Until End of Your Next Turn or Until Takes Damage", range="30 Feet"),
            usage_tags=["control"],
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can use your Channel Divinity to exert an intimidating presence over others.\n"
            "As an action, you present your holy symbol, and each creature of your choice that can see or hear you within 30 feet of you must succeed on a Wisdom saving throw or be charmed by you until the end of your next turn or until the charmed creature takes any damage. You can also cause any of the charmed creatures to drop what they are holding when they fail the saving throw."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Action", "Action"),
            ("Range", "30 feet"),
            ("Target", "Creatures you can see or hear"),
            ("Save", "Wisdom saving throw"),
            ("Duration", "Until end of your next turn or until takes damage"),
            ("Effect", "Charmed; optionally drop held items"),
        ]


class EmbodimentOfTheLaw(Feature):
    def __init__(self):
        super().__init__(name="Embodiment of the Law", origin="Order Domain Cleric Level 6", usage_tags=["utility"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        wis_mod = character_stat_block.get_ability_modifier(Ability.WISDOM)
        uses = max(1, wis_mod)
        description = (
            "You become remarkably adept at channeling magical energy to compel others.\n"
            "If you cast a spell of the enchantment school using a spell slot of 1st level or higher, you can change the spell's casting time to 1 bonus action for this casting, provided the spell's casting time is normally 1 action.\n"
            "You can use this feature a number of times equal to your Wisdom modifier (minimum of once), and you regain all expended uses of it when you finish a long rest."
        )
        return StringUtils.add_boxes(description, uses, regain_all_on="long rest")