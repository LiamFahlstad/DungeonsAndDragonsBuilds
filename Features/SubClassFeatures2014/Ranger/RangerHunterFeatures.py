from Core.Definitions import RANGER_HIT_DIE
from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class HuntersPrey(Feature):
    def __init__(self):
        super().__init__(name="Hunter's Prey", origin="Hunter Ranger Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain one of the following features of your choice.\n"
            "    * Colossus Slayer: Your tenacity can wear down the most potent foes. When you hit a creature with a weapon attack, the creature takes an extra 1d8 damage if it's below its hit point maximum. You can deal this extra damage only once per turn.\n"
            "    * Giant Killer: When a Large or larger creature within 5 feet of you hits or misses you with an attack, you can use your reaction to attack that creature immediately after its attack, provided that you can see the creature.\n"
            "    * Horde Breaker: Once on each of your turns when you make a weapon attack, you can make another attack with the same weapon against a different creature that is within 5 feet of the original target and within range of your weapon."
        )
        return description


class DefensiveTactics(Feature):
    def __init__(self):
        super().__init__(name="Defensive Tactics", origin="Hunter Ranger Level 7")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain one of the following features of your choice.\n"
            "    * Escape the Horde: Opportunity attacks against you are made with disadvantage.\n"
            "    * Multiattack Defense: When a creature hits you with an attack, you gain a +4 bonus to AC against all subsequent attacks made by that creature for the rest of the turn.\n"
            "    * Steel Will: You have advantage on saving throws against being frightened."
        )
        return description


class Multiattack(Feature):
    def __init__(self):
        super().__init__(name="Multiattack", origin="Hunter Ranger Level 11")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain one of the following features of your choice.\n"
            "    * Volley: You can use your action to make a ranged attack against any number of creatures within 10 feet of a point you can see within your weapon's range. You must have ammunition for each target, as normal, and you make a separate attack roll for each target.\n"
            "    * Whirlwind Attack: You can use your action to make melee attacks against any number of creatures within 5 feet of you, with a separate attack roll for each target."
        )
        return description


class SuperiorHuntersDefense(Feature):
    def __init__(self):
        super().__init__(name="Superior Hunter's Defense", origin="Hunter Ranger Level 15")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain one of the following features of your choice.\n"
            "    * Evasion: When you are subjected to an effect, such as a red dragon's fiery breath or a lightning bolt spell, that allows you to make a Dexterity saving throw to take only half damage, you instead take no damage if you succeed on a saving throw, and only half damage if you fail.\n"
            "    * Stand Against the Tide: When a hostile creature misses you with a melee attack, you can use your reaction to force that creature to repeat the same attack against another creature (other than itself) of your choice.\n"
            "    * Uncanny Dodge: When an attacker that you can see hits you with an attack, you can use your reaction to halve the attack's damage against you."
        )
        return description
