from Core.Definitions import Ability, PALADIN_HIT_DIE
from CharacterContent.Features.Core.BaseFeatures import Feature, FeatureActivation, ActionType, RegainedOn, FeatureUses, FeatureTarget
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class ConquestSpells(Feature):
    def __init__(self):
        super().__init__(name="Oath of Conquest Spells", origin="Oath of Conquest Paladin Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain oath spells at the Paladin levels listed. When you reach a Paladin level specified in the Oath of Conquest Spells table, you thereafter always have the listed spells prepared.\n"
            "Oath of Conquest Spells\n"
            "Paladin Level	Spells\n"
            "3	Armor of Agathys, Command\n"
            "5	Hold Person, Spiritual Weapon\n"
            "9	Bestow Curse, Fear\n"
            "13	Dominate Beast, Stoneskin\n"
            "17	Cloudkill, Dominate Person"
        )
        return description


class ConqueringPresence(Feature):
    def __init__(self):
        super().__init__(name="Channel Divinity: Conquering Presence", origin="Oath of Conquest Paladin Level 3", activation=FeatureActivation(action_type=ActionType.ACTION, duration="1 Minute", range="30 Feet"), usage_tags=["control"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can use your Channel Divinity to exude a terrifying presence. As an action, you force each creature of your choice that you can see within 30 feet of you to make a Wisdom saving throw. On a failed save, a creature becomes frightened of you for 1 minute. The frightened creature can repeat this saving throw at the end of each of its turns, ending the effect on itself on a success."
        )
        return description

    def target(self, character_stat_block: CharacterStatBlock) -> "FeatureTarget | None":
        return FeatureTarget.AREA

    def get_table_description(self, character_stat_block: CharacterStatBlock) -> list[tuple[str, str]]:
        return [
            ("What", "Exude terrifying presence"),
            ("Action", "Action"),
            ("Range", "30 feet"),
            ("Save", "Wisdom"),
            ("Effect", "Frightened for 1 minute; can repeat save at end of each turn"),
        ]


class GuidedStrike(Feature):
    def __init__(self):
        super().__init__(name="Channel Divinity: Guided Strike", origin="Oath of Conquest Paladin Level 3", usage_tags=["buff"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can use your Channel Divinity to strike with supernatural accuracy. When you make an attack roll, you can use your Channel Divinity to gain a +10 bonus to the roll. You make this choice after you see the roll, but before the DM says whether the attack hits or misses."
        )
        return description

    def target(self, character_stat_block: CharacterStatBlock) -> "FeatureTarget | None":
        return FeatureTarget.SELF

    def get_table_description(self, character_stat_block: CharacterStatBlock) -> list[tuple[str, str]]:
        return [
            ("What", "Gain accuracy bonus to attack roll"),
            ("Effect", "+10 to attack roll"),
            ("Timing", "After seeing roll, before DM announces hit/miss"),
        ]


class AuraOfConquest(Feature):
    def __init__(self):
        super().__init__(name="Aura of Conquest", origin="Oath of Conquest Paladin Level 7", activation=FeatureActivation(range="10 Feet (30 at 18th Level)"), usage_tags=["damage", "control"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Starting at 7th level, you constantly emanate a menacing aura while you're not incapacitated. The aura extends 10 feet from you in every direction, but not through total cover.\n"
            "\n"
            "If a creature is frightened of you, its speed is reduced to 0 while in the aura, and that creature takes psychic damage equal to half your paladin level if it starts its turn there.\n"
            "\n"
            "At 18th level, the range of this aura increases to 30 feet."
        )
        return description

    def target(self, character_stat_block: CharacterStatBlock) -> "FeatureTarget | None":
        return FeatureTarget.AREA

    def get_table_description(self, character_stat_block: CharacterStatBlock) -> list[tuple[str, str]]:
        half_paladin_level = character_stat_block.character_level // 2
        range_text = "10 feet (30 at 18th level)"
        return [
            ("Range", range_text),
            ("Condition", "When creature is frightened of you"),
            ("Speed Effect", "Reduced to 0"),
            ("Damage", f"Psychic damage = half paladin level ({half_paladin_level})"),
        ]


class AuraOfConquestExpansion(Feature):
    def __init__(self):
        super().__init__(name="Aura of Conquest Expansion", origin="Oath of Conquest Paladin Level 18")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "The range of your Aura of Conquest increases to 30 feet."
        return description


class ScornfulRebuke(Feature):
    def __init__(self):
        super().__init__(name="Scornful Rebuke", origin="Oath of Conquest Paladin Level 15", usage_tags=["damage"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Starting at 15th level, those who dare to strike you are psychically punished for their audacity. Whenever a creature hits you with an attack, that creature takes psychic damage equal to your Charisma modifier (minimum of 1 hp) if you're not incapacitated."
        )
        return description

    def target(self, character_stat_block: CharacterStatBlock) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class InvincibleConqueror(Feature):
    def __init__(self):
        super().__init__(name="Invincible Conqueror", origin="Oath of Conquest Paladin Level 20", activation=FeatureActivation(action_type=ActionType.ACTION, duration="1 Minute"), usage_tags=["buff"], uses=FeatureUses(max_uses=1, regain_all_on="long rest"))

    def regained_on(self, character_stat_block: CharacterStatBlock) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def target(self, character_stat_block: CharacterStatBlock) -> "FeatureTarget | None":
        return FeatureTarget.SELF

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "At 20th level, you gain the ability to harness extraordinary martial prowess. As an action, you can magically become an avatar of conquest, gaining the following benefits for 1 minute:\n"
            "    * You have resistance to all damage.\n"
            "    * When you take the Attack action on your turn, you can make one additional attack as part of that action.\n"
            "    * Your melee weapon attacks score a critical hit on a roll of 19 or 20 on the d20.\n"
            "\n"
            "Once you use this feature, you can't use it again until you finish a long rest."
        )
        return description