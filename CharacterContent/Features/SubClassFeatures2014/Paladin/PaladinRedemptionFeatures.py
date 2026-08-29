from Core.Definitions import PALADIN_HIT_DIE
from CharacterContent.Features.Core.BaseFeatures import Feature, FeatureActivation, ActionType
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class RedemptionSpells(Feature):
    def __init__(self):
        super().__init__(name="Oath of Redemption Spells", origin="Oath of Redemption Paladin Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain oath spells at the Paladin levels listed. When you reach a Paladin level specified in the Oath of Redemption Spells table, you thereafter always have the listed spells prepared.\n"
            "Oath of Redemption Spells\n"
            "Paladin Level	Spells\n"
            "3	Sanctuary, Sleep\n"
            "5	Calm Emotions, Hold Person\n"
            "9	Counterspell, Hypnotic Pattern\n"
            "13	Otiluke's Resilient Sphere, Stoneskin\n"
            "17	Hold Monster, Wall of Force"
        )
        return description


class EmissaryOfPeace(Feature):
    def __init__(self):
        super().__init__(name="Channel Divinity: Emissary of Peace", origin="Oath of Redemption Paladin Level 3", activation=FeatureActivation(action_type=ActionType.BONUS_ACTION, duration="10 Minutes"), usage_tags=["buff"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can use your Channel Divinity to augment your presence with divine power. As a bonus action, you grant yourself a +5 bonus to Charisma (Persuasion) checks for the next 10 minutes."
        )
        return description


class RebukeTheViolent(Feature):
    def __init__(self):
        super().__init__(name="Channel Divinity: Rebuke the Violent", origin="Oath of Redemption Paladin Level 3", activation=FeatureActivation(action_type=ActionType.REACTION, range="30 Feet"), usage_tags=["damage"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can use your Channel Divinity to rebuke those who use violence. Immediately after an attacker within 30 feet of you deals damage with an attack against a creature other than you, you can use your reaction to force the attacker to make a Wisdom saving throw. On a failed save, the attacker takes radiant damage equal to the damage it just dealt. On a successful save, it takes half as much damage."
        )
        return description

    def get_table_description(self, character_stat_block: CharacterStatBlock) -> list[tuple[str, str]]:
        return [
            ("Trigger", "Attacker within 30 feet hits another creature"),
            ("Action", "Reaction"),
            ("Save", "Wisdom"),
            ("Damage (fail)", "Radiant = damage dealt"),
            ("Damage (success)", "Half damage dealt"),
        ]


class AuraOfTheGuardian(Feature):
    def __init__(self):
        super().__init__(name="Aura of the Guardian", origin="Oath of Redemption Paladin Level 7", activation=FeatureActivation(action_type=ActionType.REACTION, range="10 Feet"))

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can shield your allies from harm at the cost of your own health. When a creature within 10 feet of you takes damage, you can use your reaction to magically take that damage, instead of that creature taking it. This feature doesn't transfer any other effects that might accompany the damage, and this damage can't be reduced in any way."
        )
        return description

    def get_table_description(self, character_stat_block: CharacterStatBlock) -> list[tuple[str, str]]:
        return [
            ("Range", "10 feet (30 at 18th level)"),
            ("Trigger", "Creature takes damage"),
            ("Action", "Reaction"),
            ("Effect", "You take damage instead of creature"),
            ("Limitation", "Damage can't be reduced; doesn't transfer other effects"),
        ]


class AuraOfTheGuardianExpansion(Feature):
    def __init__(self):
        super().__init__(name="Aura of the Guardian Expansion", origin="Oath of Redemption Paladin Level 18")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "The range of your Aura of the Guardian increases to 30 feet."
        return description


class ProtectiveSpirit(Feature):
    def __init__(self):
        super().__init__(name="Protective Spirit", origin="Oath of Redemption Paladin Level 15", usage_tags=["heal"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "A holy presence mends your wounds in combat. You regain hit points equal to 1d6 + half your Paladin level if you end your turn in combat with fewer than half of your hit points remaining and you aren't incapacitated."
        )
        return description

    def get_table_description(self, character_stat_block: CharacterStatBlock) -> list[tuple[str, str]]:
        half_level = character_stat_block.character_level // 2
        return [
            ("Trigger", "End turn in combat with < half HP"),
            ("Effect", f"Regain 1d6 + {half_level} HP"),
            ("Condition", "Not incapacitated"),
        ]


class EmissaryOfRedemption(Feature):
    def __init__(self):
        super().__init__(name="Emissary of Redemption", origin="Oath of Redemption Paladin Level 20", usage_tags=["buff", "damage"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You become an avatar of peace, which gives you two benefits:\n"
            "    * You have resistance to all damage dealt by other creatures (their attacks, spells, and other effects).\n"
            "    * Whenever a creature hits you with an attack, it takes radiant damage equal to half the damage you take from the attack.\n"
            "\n"
            "If you attack a creature, cast a spell on it, or deal damage to it by any means but this feature, neither benefit works against that creature until you finish a long rest."
        )
        return description

    def get_table_description(self, character_stat_block: CharacterStatBlock) -> list[tuple[str, str]]:
        return [
            ("What", "Avatar of peace"),
            ("Resistance", "All damage from creatures"),
            ("Damage Return", "Creatures that hit you take radiant damage = half damage to you"),
            ("Deactivation", "If you attack/spell/damage a creature: benefits don't work against it for 24 hours"),
        ]
