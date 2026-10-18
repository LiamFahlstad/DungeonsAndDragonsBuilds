from Core.Definitions import (
    MONK_HIT_DIE,
    Ability,
)
from Model.Content.Feature import (
    Feature,
    FeatureUses,
    FeatureActivation,
    ActionType,
    RegainedOn,
    FeatureTarget,
)
from CharacterContent.Items.Weapons import WeaponDamageRolls
from Utils import StringUtils
from Core.Rules import MAX_ABILITY_MODIFIER
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Paragraph, Table, dc_formula

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
            name="Open Hand Technique",
            origin="Warrior of the Open Hand Monk Level 3",
            usage_tags=["control"],
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Trigger",
                        "You hit a creature with an attack granted by Flurry of Blows",
                    ),
                    ("Effect", "Impose one of the effects below"),
                    ("Save DC", f"Your Focus save DC ({dc_formula(Ability.WISDOM)})"),
                )
            ),
            Table(
                ("Effect", "Result"),
                (
                    (
                        "Addle",
                        "It can't make Opportunity Attacks until the start of its next turn",
                    ),
                    ("Push", "Strength save, or pushed up to 15 feet away from you"),
                    ("Topple", "Dexterity save, or it has the Prone condition"),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
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
            name="Wholeness of Body",
            origin="Warrior of the Open Hand Monk Level 6",
            activation=FeatureActivation(action_type=ActionType.BONUS_ACTION),
            usage_tags=["heal"],
            uses=FeatureUses(
                max_uses=MAX_ABILITY_MODIFIER,
                regain_all_on="long rest",
                current_formula="Current amount: equal to your Wisdom modifier.",
            ),
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # Uses (Wisdom modifier, minimum of once) are in the panel below.
        return [
            Facts(
                (
                    ("Action", "Bonus Action"),
                    (
                        "Heal",
                        "Roll your Martial Arts die + Wisdom modifier (minimum of 1 Hit Point)",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You gain the ability to heal yourself. As a Bonus Action, you can roll your Martial Arts die. You regain a number of Hit Points equal to the number rolled plus your Wisdom modifier (minimum of 1 Hit Point regained).\n"
            "You can use this feature a number of times equal to your Wisdom modifier (minimum of once), and you regain all expended uses when you finish a Long Rest."
        )
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def number_of_uses(self, character: CharacterView) -> int:
        return max(1, character.get_wisdom_modifier())


class FleetStep(Feature):
    def __init__(self):
        super().__init__(
            name="Fleet Step", origin="Warrior of the Open Hand Monk Level 11"
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Trigger", "You take a Bonus Action other than Step of the Wind"),
                    ("Effect", "Use Step of the Wind immediately after it"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "When you take a Bonus Action other than Step of the Wind, you can also use Step of the Wind immediately after that Bonus Action."
        return description


class QuiveringPalm(Feature):
    def __init__(self):
        super().__init__(
            name="Quivering Palm",
            origin="Warrior of the Open Hand Monk Level 17",
            activation=FeatureActivation(duration="Monk Level Days"),
            usage_tags=["damage"],
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Set up lethal vibrations in a creature's body."),
            Facts(
                (
                    ("Trigger", "You hit a creature with an Unarmed Strike"),
                    ("Cost", "4 Focus Points"),
                    (
                        "Lasts",
                        "Days equal to your Monk level; harmless until you end them",
                    ),
                    (
                        "End them",
                        "Take an action, or forgo one attack of your Attack action; you must be on the same plane",
                    ),
                    (
                        "Save",
                        f"Constitution save ({dc_formula(Ability.WISDOM)}): 10d12 Force damage, half on a success",
                    ),
                    (
                        "Limit",
                        "One creature at a time; you can end the vibrations harmlessly (no action required)",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You gain the ability to set up lethal vibrations in someone's body. When you hit a creature with an Unarmed Strike, you can expend 4 Focus Points to start these imperceptible vibrations, which last for a number of days equal to your Monk level. The vibrations are harmless unless you take an action to end them. Alternatively, when you take the Attack action on your turn, you can forgo one of the attacks to end the vibrations. To end them, you and the target must be on the same plane of existence. When you end them, the target must make a Constitution saving throw, taking 10d12 Force damage on a failed save or half as much damage on a successful one.\n"
            "You can have only one creature under the effect of this feature at a time. You can end the vibrations harmlessly (no action required)."
        )
        return description
