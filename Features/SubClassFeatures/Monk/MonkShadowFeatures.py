from Definitions import MONK_HIT_DIE
from Features.Core.BaseFeatures import Feature
from Features.Equipment.Weapons import WeaponsDamageRolls
from StatBlocks.CharacterStatBlock import CharacterStatBlock

LEVEL_TO_MARTIAL_ARTS_DIE = {
    1: WeaponsDamageRolls.D6,
    2: WeaponsDamageRolls.D6,
    3: WeaponsDamageRolls.D6,
    4: WeaponsDamageRolls.D6,
    5: WeaponsDamageRolls.D8,
    6: WeaponsDamageRolls.D8,
    7: WeaponsDamageRolls.D8,
    8: WeaponsDamageRolls.D8,
    9: WeaponsDamageRolls.D8,
    10: WeaponsDamageRolls.D8,
    11: WeaponsDamageRolls.D10,
    12: WeaponsDamageRolls.D10,
    13: WeaponsDamageRolls.D10,
    14: WeaponsDamageRolls.D10,
    15: WeaponsDamageRolls.D10,
    16: WeaponsDamageRolls.D10,
    17: WeaponsDamageRolls.D12,
    18: WeaponsDamageRolls.D12,
    19: WeaponsDamageRolls.D12,
    20: WeaponsDamageRolls.D12,
}

LEVEL_TO_FOCUS_POINTS = {
    1: 0,
    2: 2,
    3: 3,
    4: 4,
    5: 5,
    6: 6,
    7: 7,
    8: 8,
    9: 9,
    10: 10,
    11: 11,
    12: 12,
    13: 13,
    14: 14,
    15: 15,
    16: 16,
    17: 17,
    18: 18,
    19: 19,
    20: 20,
}


class ShadowArts(Feature):
    def __init__(self):
        super().__init__(name="Shadow Arts", origin="Warrior of Shadow Monk Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You have learned to draw on the power of the Shadowfell, gaining the following benefits.\n"
            "Darkness. You can expend 1 Focus Point to cast the Darkness spell without spell components. You can see within the spell's area when you cast it with this feature. While the spell persists, you can move its area of Darkness to a space within 60 feet of yourself at the start of each of your turns.\n"
            "Darkvision. You gain Darkvision with a range of 60 feet. If you already have Darkvision, its range increases by 60 feet.\n"
            "Shadowy Figments. You know the Minor Illusion spell. Wisdom is your spellcasting ability for it."
        )
        return description


class ShadowStep(Feature):
    def __init__(self):
        super().__init__(name="Shadow Step", origin="Warrior of Shadow Monk Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "While entirely within Dim Light or Darkness, you can use a Bonus Action to teleport up to 60 feet to an unoccupied space you can see that is also in Dim Light or Darkness. You then have Advantage on the next melee attack you make before the end of the current turn."
        return description


class ImprovedShadowStep(Feature):
    def __init__(self):
        super().__init__(
            name="Improved Shadow Step", origin="Warrior of Shadow Monk Level 11"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can draw on your Shadowfell connection to empower your teleportation. When you use your Shadow Step, you can expend 1 Focus Point to remove the requirement that you must start and end in Dim Light or Darkness for that use of the feature. As part of this Bonus Action, you can make an Unarmed Strike immediately after you teleport."
        return description


class CloakOfShadows(Feature):
    def __init__(self):
        super().__init__(
            name="Cloak of Shadows", origin="Warrior of Shadow Monk Level 17"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "As a Magic action while entirely within Dim Light or Darkness, you can expend 3 Focus Points to shroud yourself with shadows for 1 minute, until you have the Incapacitated condition, or until you end your turn in Bright Light. While shrouded by these shadows, you gain the following benefits.\n"
            "Invisibility. You have the Invisible condition.\n"
            "Partially Incorporeal. You can move through occupied spaces as if they were Difficult Terrain. If you end your turn in such a space, you are shunted to the last unoccupied space you were in.\n"
            "Shadow Flurry. You can use your Flurry of Blows without expending any Focus Points."
        )
        return description
