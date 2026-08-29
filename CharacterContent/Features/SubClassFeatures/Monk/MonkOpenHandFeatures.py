import Core.Definitions as Definitions
from Core.Definitions import MONK_HIT_DIE
from CharacterContent.Features.Core.BaseFeatures import Feature, FeatureUses
from CharacterContent.Items.Weapons import WeaponDamageRolls
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils

LEVEL_TO_MARTIAL_ARTS_DIE = {
    1: WeaponDamageRolls.D6,
    2: WeaponDamageRolls.D6,
    3: WeaponDamageRolls.D6,
    4: WeaponDamageRolls.D6,
    5: WeaponDamageRolls.D8,
    6: WeaponDamageRolls.D8,
    7: WeaponDamageRolls.D8,
    8: WeaponDamageRolls.D8,
    9: WeaponDamageRolls.D8,
    10: WeaponDamageRolls.D8,
    11: WeaponDamageRolls.D10,
    12: WeaponDamageRolls.D10,
    13: WeaponDamageRolls.D10,
    14: WeaponDamageRolls.D10,
    15: WeaponDamageRolls.D10,
    16: WeaponDamageRolls.D10,
    17: WeaponDamageRolls.D12,
    18: WeaponDamageRolls.D12,
    19: WeaponDamageRolls.D12,
    20: WeaponDamageRolls.D12,
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
            name="Open Hand Technique", origin="Warrior of the Open Hand Monk Level 3", usage_tags=["control"]
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Whenever you hit a creature with an attack granted by your Flurry of Blows, you can impose one of the following effects on that target.\n"
            "Addle. The target can't make Opportunity Attacks until the start of its next turn.\n"
            "Push. The target must succeed on a Strength saving throw or be pushed up to 15 feet away from you.\n"
            "Topple. The target must succeed on a Dexterity saving throw or have the Prone condition."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Addle", "Target can't make Opportunity Attacks until start of next turn"),
            ("Push", "Strength save or pushed up to 15 feet away"),
            ("Topple", "Dexterity save or Prone condition"),
        ]


class WholenessOfBody(Feature):
    def __init__(self):
        super().__init__(
            name="Wholeness of Body", origin="Warrior of the Open Hand Monk Level 6", action_type="bonus_action", usage_tags=["heal"]
        , uses=FeatureUses(max_uses=Definitions.MAX_ABILITY_MODIFIER, regain_all_on="long rest", current_formula="Current amount: equal to your Wisdom modifier."))

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain the ability to heal yourself. As a Bonus Action, you can roll your Martial Arts die. You regain a number of Hit Points equal to the number rolled plus your Wisdom modifier (minimum of 1 Hit Point regained).\n"
            "You can use this feature a number of times equal to your Wisdom modifier (minimum of once), and you regain all expended uses when you finish a Long Rest."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        wisdom_modifier = character_stat_block.get_ability_modifier(
            Definitions.Ability.WISDOM
        )
        uses = max(1, wisdom_modifier)
        return [
            ("Action", "Bonus Action"),
            ("Effect", f"Roll Martial Arts die + {wisdom_modifier:+d} (Wisdom) Hit Points (minimum 1)"),
            ("Uses", f"{uses}/Long Rest"),
        ]


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
            name="Quivering Palm", origin="Warrior of the Open Hand Monk Level 17", duration="Monk Level Days", usage_tags=["damage"]
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain the ability to set up lethal vibrations in someone's body. When you hit a creature with an Unarmed Strike, you can expend 4 Focus Points to start these imperceptible vibrations, which last for a number of days equal to your Monk level. The vibrations are harmless unless you take an action to end them. Alternatively, when you take the Attack action on your turn, you can forgo one of the attacks to end the vibrations. To end them, you and the target must be on the same plane of existence. When you end them, the target must make a Constitution saving throw, taking 10d12 Force damage on a failed save or half as much damage on a successful one.\n"
            "You can have only one creature under the effect of this feature at a time. You can end the vibrations harmlessly (no action required)."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        monk_level = character_stat_block.get_class_level(
            Definitions.CharacterClass.MONK
        )
        return [
            ("Trigger", "Hit with Unarmed Strike"),
            ("Cost", "4 Focus Points"),
            ("Duration", f"{monk_level} days"),
            ("Activation", "Action required to end (or forgo Attack)"),
            ("Save", "Constitution (to take damage)"),
            ("Damage", "10d12 Force on failed save, half on successful save"),
            ("Special", "Only one creature at a time; can end harmlessly with no action"),
        ]
