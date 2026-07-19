import Definitions
from Features.Core.BaseFeatures import Feature
from Features.Equipment.Weapons import WeaponsDamageRolls
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils

MONK_HIT_DIE = 8

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


class OpenHandTechnique(Feature):
    def __init__(self):
        super().__init__(
            name="Open Hand Technique", origin="Warrior of the Open Hand Monk Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Whenever you hit a creature with an attack granted by your Flurry of Blows, you can impose one of the following effects on that target.\n"
            "Addle. The target can't make Opportunity Attacks until the start of its next turn.\n"
            "Push. The target must succeed on a Strength saving throw or be pushed up to 15 feet away from you.\n"
            "Topple. The target must succeed on a Dexterity saving throw or have the Prone condition."
        )
        return description


class WholenessOfBody(Feature):
    def __init__(self):
        super().__init__(
            name="Wholeness of Body", origin="Warrior of the Open Hand Monk Level 6"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        wisdom_modifier = character_stat_block.get_ability_modifier(
            Definitions.Ability.WISDOM
        )
        uses = max(1, wisdom_modifier)
        description = (
            "You gain the ability to heal yourself. As a Bonus Action, you can roll your Martial Arts die. You regain a number of Hit Points equal to the number rolled plus your Wisdom modifier (minimum of 1 Hit Point regained).\n"
            "You can use this feature a number of times equal to your Wisdom modifier (minimum of once), and you regain all expended uses when you finish a Long Rest."
        )
        return StringUtils.add_boxes(description, uses, regain_all_on="long rest")


class FleetStep(Feature):
    def __init__(self):
        super().__init__(
            name="Fleet Step", origin="Warrior of the Open Hand Monk Level 11"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you take a Bonus Action other than Step of the Wind, you can also use Step of the Wind immediately after that Bonus Action."
        return description


class QuiveringPalm(Feature):
    def __init__(self):
        super().__init__(
            name="Quivering Palm", origin="Warrior of the Open Hand Monk Level 17"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain the ability to set up lethal vibrations in someone's body. When you hit a creature with an Unarmed Strike, you can expend 4 Focus Points to start these imperceptible vibrations, which last for a number of days equal to your Monk level. The vibrations are harmless unless you take an action to end them. Alternatively, when you take the Attack action on your turn, you can forgo one of the attacks to end the vibrations. To end them, you and the target must be on the same plane of existence. When you end them, the target must make a Constitution saving throw, taking 10d12 Force damage on a failed save or half as much damage on a successful one.\n"
            "You can have only one creature under the effect of this feature at a time. You can end the vibrations harmlessly (no action required)."
        )
        return description
