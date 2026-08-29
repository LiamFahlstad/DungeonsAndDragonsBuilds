from CharacterContent.Features.Core.BaseFeatures import Feature, FeatureUses
from CharacterContent.Features.Core.Improvements import InitiativeProficiency
from Core.Definitions import Ability
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class WatchersSpells(Feature):
    def __init__(self):
        super().__init__(
            name="Oath of the Watchers Spells",
            origin="Oath of the Watchers Paladin Level 3",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain oath spells at the Paladin levels listed. When you reach a Paladin level specified in the Oath of the Watchers Spells table, you thereafter always have the listed spells prepared.\n"
            "Oath of the Watchers Spells\n"
            "Paladin Level\tSpells\n"
            "3\tAlarm, Detect Magic\n"
            "5\tMoonbeam, See Invisibility\n"
            "9\tCounterspell, Nondetection\n"
            "13\tAura of Purity, Banishment\n"
            "17\tHold Monster, Scrying"
        )
        return description


class WatchersWill(Feature):
    def __init__(self):
        super().__init__(
            name="Channel Divinity: Watcher's Will",
            origin="Oath of the Watchers Paladin Level 3",
            action_type="action",
            duration="1 Minute",
            range="30 Feet",
            usage_tags=["buff"],
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        charisma_modifier = character_stat_block.get_ability_modifier(Ability.CHARISMA)
        creature_count = max(1, charisma_modifier)
        description = (
            "You can use your Channel Divinity to invest your presence with the warding power of your faith. As an action, you can choose a number of creatures you can see within 30 feet of you, "
            f"up to a number equal to your Charisma modifier (minimum of one creature) = {creature_count}. For 1 minute, you and the chosen creatures have advantage on Intelligence, Wisdom, and Charisma saving throws."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        charisma_modifier = character_stat_block.get_ability_modifier(Ability.CHARISMA)
        creature_count = max(1, charisma_modifier)
        return [
            ("Action", "Action"),
            ("Range", "30 feet"),
            ("Targets", f"Up to {creature_count} creatures plus yourself"),
            ("Duration", "1 minute"),
            ("Effect", "Advantage on INT, WIS, CHA saves"),
        ]


class AbjureTheExtraplanar(Feature):
    def __init__(self):
        super().__init__(
            name="Channel Divinity: Abjure the Extraplanar",
            origin="Oath of the Watchers Paladin Level 3",
            action_type="action",
            duration="1 Minute or Until Takes Damage",
            range="30 Feet",
            usage_tags=["control"],
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can use your Channel Divinity to castigate unworldly beings. As an action, you present your holy symbol and each aberration, celestial, elemental, fey, or fiend within 30 feet of you that can hear you must make a Wisdom saving throw. On a failed save, the creature is turned for 1 minute or until it takes damage.\n"
            "\n"
            "A turned creature must spend its turns trying to move as far away from you as it can, and it can't willingly end its move in a space within 30 feet of you. For its action, it can use only the Dash action or try to escape from an effect that prevents it from moving. If there's nowhere to move, the creature can take the Dodge action."
        )
        return description


class AuraOfTheSentinel(Feature):
    def __init__(self):
        super().__init__(
            name="Aura of the Sentinel",
            origin="Oath of the Watchers Paladin Level 7",
            range="10 Feet (30 at 18th Level)",
            usage_tags=["buff"],
        )

    def apply(self, character_stat_block: CharacterStatBlock):
        InitiativeProficiency().apply(character_stat_block)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        proficiency_bonus = character_stat_block.get_proficiency_bonus()
        description = (
            "You emit an aura of alertness while you aren't incapacitated. When you and any creatures of your choice within 10 feet of you roll initiative, you all gain a bonus to initiative equal to your proficiency bonus "
            f"({proficiency_bonus}).\n"
            "\n"
            "At 18th level, the range of this aura increases to 30 feet."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        proficiency_bonus = character_stat_block.get_proficiency_bonus()
        return [
            ("Range", "10 feet (30 at 18th level)"),
            ("Trigger", "Roll initiative"),
            ("Effect", f"+{proficiency_bonus} to initiative"),
            ("Condition", "Not incapacitated"),
        ]


class AuraOfTheSentinelExpansion(Feature):
    def __init__(self):
        super().__init__(
            name="Aura of the Sentinel Expansion",
            origin="Oath of the Watchers Paladin Level 18",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "The range of your Aura of the Sentinel increases to 30 feet."
        return description


class VigilantRebuke(Feature):
    def __init__(self):
        super().__init__(
            name="Vigilant Rebuke",
            origin="Oath of the Watchers Paladin Level 15",
            action_type="reaction",
            range="30 Feet",
            usage_tags=["damage"],
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        charisma_modifier = character_stat_block.get_ability_modifier(Ability.CHARISMA)
        description = (
            "You've learned how to chastise anyone who dares wield beguilements against you and your wards. Whenever you or a creature you can see within 30 feet of you succeeds on an Intelligence, a Wisdom, or a Charisma saving throw, you can use your reaction to deal "
            f"2d8 + your Charisma modifier ({charisma_modifier}) force damage to the creature that forced the saving throw."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        charisma_modifier = character_stat_block.get_ability_modifier(Ability.CHARISMA)
        return [
            ("Trigger", "You or ally within 30 feet succeeds on INT/WIS/CHA save"),
            ("Action", "Reaction"),
            ("Effect", f"2d8 + {charisma_modifier} force damage to caster"),
        ]


class MortalBulwark(Feature):
    def __init__(self):
        super().__init__(
            name="Mortal Bulwark",
            origin="Oath of the Watchers Paladin Level 20",
            action_type="bonus_action",
            duration="1 Minute",
            range="120 Feet (Truesight)",
            usage_tags=["buff", "control"],
            uses=FeatureUses(max_uses=1, regain_all_on="long rest"),
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You manifest a spark of divine power in defense of the mortal realms. As a bonus action, you gain the following benefits for 1 minute:\n"
            "    * You gain truesight with a range of 120 feet.\n"
            "    * You have advantage on attack rolls against aberrations, celestials, elementals, fey, and fiends.\n"
            "    * When you hit a creature with an attack roll and deal damage to it, you can also force it to make a Charisma saving throw against your spell save DC. On a failed save, the creature is magically banished to its native plane of existence if it's currently not there. On a successful save, the creature can't be banished by this feature for 24 hours.\n"
            "\n"
            "Once you use this bonus action, you can't use it again until you finish a long rest, unless you expend a 5th-level spell slot to use it again."
        )
        return description
