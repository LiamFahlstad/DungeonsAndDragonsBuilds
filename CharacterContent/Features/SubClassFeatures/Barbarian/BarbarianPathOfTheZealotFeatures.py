import Core.Definitions as Definitions
from Model.Content.Feature import (
    FeatureUses,
    Feature,
    FeatureActivation,
    ActionType,
    FeatureTarget,
    RegainedOn,
)
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Paragraph


class DivineFury(Feature):
    def __init__(self):
        super().__init__(
            name="Divine Fury",
            origin="Path Of The Zealot Barbarian Level 3",
            usage_tags=["damage"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Trigger",
                        "On each of your turns while raging, the first creature you hit with a weapon or an Unarmed Strike",
                    ),
                    (
                        "Damage",
                        "Extra 1d6 + half your Barbarian level (round down), Necrotic or Radiant (choose each time)",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "You can channel divine power into your strikes. On each of your turns while your Rage is active, the first creature you hit with a weapon or an Unarmed Strike takes extra damage equal to 1d6 plus half your Barbarian level (round down). The extra damage is Necrotic or Radiant; you choose the type each time you deal the damage."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class WarriorOfTheGods(Feature):
    def __init__(self):
        super().__init__(
            name="Warrior of the Gods",
            origin="Path Of The Zealot Barbarian Level 3",
            activation=FeatureActivation(action_type=ActionType.BONUS_ACTION),
            usage_tags=["heal"],
            # The pool of d12s: 4, then 5/6/7 at Barbarian levels 6/12/17.
            uses=FeatureUses(
                max_uses=7,
                regain_all_on="long rest",
                current_formula="Current amount: 4 d12s, 5 at Barbarian level 6, 6 at 12, 7 at 17.",
                gained_at=[3, 3, 3, 3, 6, 12, 17],
            ),
        )

    def number_of_uses(self, character: CharacterView) -> int:
        level = character.get_class_level(Definitions.CharacterClass.BARBARIAN)
        return 4 + (level >= 6) + (level >= 12) + (level >= 17)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # The pool of d12s and its recharge are in the panel below.
        return [
            Paragraph("A divine entity helps ensure you can continue the fight."),
            Facts(
                (
                    ("Action", "Bonus Action"),
                    (
                        "Heal",
                        "Expend and roll any number of d12s from the pool; regain Hit Points equal to the total",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "A divine entity helps ensure you can continue the fight. You have a pool of four d12s that you can spend to heal yourself. As a Bonus Action, you can expend dice from the pool, roll them, and regain a number of Hit Points equal to the roll’s total.\n"
            "Your pool regains all expended dice when you finish a Long Rest.\n"
            "The pool’s maximum number of dice increases by one when you reach Barbarian levels 6 (5 dice), 12 (6 dice), and 17 (7 dice)."
        )
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class FanaticalFocus(Feature):
    def __init__(self):
        super().__init__(
            name="Fanatical Focus",
            origin="Path Of The Zealot Barbarian Level 6",
            usage_tags=["buff"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Trigger", "You fail a saving throw"),
                    (
                        "Effect",
                        "Reroll it with a bonus equal to your Rage Damage bonus; you must use the new roll",
                    ),
                    ("Limit", "Once per active Rage"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "Once per active Rage, if you fail a saving throw, you can reroll it with a bonus equal to your Rage Damage bonus, and you must use the new roll."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class ZealousPresence(Feature):
    def __init__(self):
        super().__init__(
            name="Zealous Presence",
            origin="Path Of The Zealot Barbarian Level 10",
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION,
                duration="Until Start of Your Next Turn",
                range="60 Feet",
            ),
            usage_tags=["buff"],
            uses=FeatureUses(max_uses=1, regain_all_on="long rest"),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # The once-per-Long-Rest box is in the panel below.
        return [
            Paragraph("Unleash a battle cry infused with divine energy."),
            Facts(
                (
                    ("Action", "Bonus Action"),
                    (
                        "Target",
                        "Up to ten other creatures of your choice within 60 feet",
                    ),
                    (
                        "Effect",
                        "Advantage on attack rolls and saving throws until the start of your next turn",
                    ),
                    (
                        "Restore",
                        "Expend a use of Rage (no action required) to regain the use",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "As a Bonus Action, you unleash a battle cry infused with divine energy. Up to ten other creatures of your choice within 60 feet of you gain Advantage on attack rolls and saving throws until the start of your next turn.\n"
            "Once you use this feature, you can’t use it again until you finish a Long Rest unless you expend a use of your Rage (no action required) to restore your use of it."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY


class RageOfTheGods(Feature):
    def __init__(self):
        super().__init__(
            name="Rage of the Gods",
            origin="Path Of The Zealot Barbarian Level 14",
            activation=FeatureActivation(
                duration="1 Minute or Until You Drop to 0 Hit Points", range="30 Feet"
            ),
            usage_tags=["buff", "heal", "utility"],
            uses=FeatureUses(max_uses=1, regain_all_on="long rest"),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # The once-per-Long-Rest box is in the panel below.
        return [
            Paragraph("Take the form of a divine warrior when you Rage."),
            Facts(
                (
                    ("Trigger", "You activate your Rage"),
                    ("Duration", "1 minute, or until you drop to 0 Hit Points"),
                    ("Limit", "Once per Long Rest"),
                    ("Flight", "Fly Speed equal to your Speed, and you can hover"),
                    ("Resistance", "Necrotic, Psychic and Radiant damage"),
                    (
                        "Revivification",
                        "Reaction when a creature within 30 feet would drop to 0 Hit Points: expend a use of Rage to set its Hit Points to your Barbarian level instead",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "When you activate your Rage, you can assume the form of a divine warrior. This form lasts for 1 minute or until you drop to 0 Hit Points. Once you use this feature, you can’t do so again until you finish a Long Rest.\n"
            "While in this form, you gain the benefits below.\n"
            "Flight. You have a Fly Speed equal to your Speed and can hover.\n"
            "Resistance. You have Resistance to Necrotic, Psychic, and Radiant damage.\n"
            "Revivification. When a creature within 30 feet of you would drop to 0 Hit Points, you can take a Reaction to expend a use of your Rage to instead change the target’s Hit Points to a number equal to your Barbarian level."
        )
        return description
