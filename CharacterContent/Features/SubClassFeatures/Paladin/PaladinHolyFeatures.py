from Model.Content.Feature import (
    Feature,
    FeatureUses,
    FeatureActivation,
    ActionType,
    RegainedOn,
    FeatureTarget,
)
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Option, Paragraph


class BeaconOfLight(Feature):
    def __init__(self):
        super().__init__(
            name="Beacon of Light",
            origin="Oath of the Holy Paladin Level 3",
            activation=FeatureActivation(
                action_type=ActionType.ACTION, duration="1 Minute", range="60 Feet"
            ),
            usage_tags=["heal"],
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Action", "Magic action"),
                    ("Cost", "One use of Channel Divinity"),
                    ("Target", "An ally within 60 feet"),
                    ("Duration", "1 minute"),
                    (
                        "Effect",
                        "Whenever you heal another creature with a spell or your Lay On Hands, the ally also regains half as many Hit Points",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "As a Magic action, you can expend one use of your Channel Divinity to wrap an ally within 60 feet in holy energy. For 1 minute, anytime you heal a creature other than the affected ally with a spell or your Lay On Hands, the chosen ally also regains half as many Hit Points."
        return description


class LightbringersAura(Feature):
    def __init__(self):
        super().__init__(
            name="Lightbringer's Aura",
            origin="Oath of the Holy Paladin Level 7",
            usage_tags=["heal"],
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Trigger",
                        "You cast a spell or use Lay On Hands to restore Hit Points to a Bloodied creature within your Aura of Protection",
                    ),
                    ("Extra healing", "1d6 Hit Points"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "Whenever you cast a spell or use Lay On Hands to restore Hit Points to a Bloodied creature within your Aura of Protection, the creature regains an extra 1d6 Hit Points."
        return description


class InfusionOfLight(Feature):
    def __init__(self):
        super().__init__(
            name="Infusion of Light",
            origin="Oath of the Holy Paladin Level 15",
            usage_tags=["heal"],
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Trigger", "You cast a spell that deals Radiant damage"),
                    (
                        "Effect",
                        "Your Lay On Hands pool regains Hit Points equal to the total rolled for the spell's Radiant damage",
                    ),
                    ("Maximum", "Five times your Paladin level"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "Whenever you cast a spell that deals Radiant damage, you refresh the pool of healing power that fuels your Lay On Hands feature. Your pool of healing power regains a number of Hit Points equal to the total number rolled for the spell's Radiant damage, to a maximum of five times your Paladin level."
        return description


class HolyDeliverance(Feature):
    def __init__(self):
        super().__init__(
            name="Holy Deliverance",
            origin="Oath of the Holy Paladin Level 20",
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION, duration="10 Minutes"
            ),
            usage_tags=["heal", "utility"],
            uses=FeatureUses(max_uses=1, regain_all_on="long rest"),
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # The once-per-Long-Rest box is in the panel below.
        return [
            Paragraph("Imbue your Aura of Protection with holy power."),
            Facts(
                (
                    ("Action", "Bonus Action"),
                    (
                        "Duration",
                        "10 minutes, or until you end it (no action required)",
                    ),
                    (
                        "Recharge",
                        "Once per Long Rest, or expend a level 5 spell slot (no action required) to restore it",
                    ),
                )
            ),
            Option(
                "Benefits",
                (
                    Facts(
                        (
                            (
                                "Healing Power",
                                "An ally that starts its turn Bloodied and in the aura regains Hit Points equal to your Charisma modifier + Proficiency Bonus",
                            ),
                            (
                                "Sunlight",
                                "The aura is filled with Bright Light that is sunlight",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "As a Bonus Action, you can imbue your Aura of Protection with holy power, granting the benefits below for 10 minutes or until you end them (no action required). Once you use this feature, you can't use it again until you finish a Long Rest. You can also restore your use of it by expending a level 5 spell slot (no action required).\n"
            "Healing Power. Whenever an ally starts its turn Bloodied and in the aura, that creature regains Hit Points equal to your Charisma modifier plus your Proficiency Bonus.\n"
            "Sunlight. The aura is filled with Bright Light that is sunlight."
        )
        return description
