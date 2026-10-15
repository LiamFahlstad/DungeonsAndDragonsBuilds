from Core.Definitions import PALADIN_HIT_DIE
from Model.Content.Feature import (
    ActionType,
    Feature,
    FeatureActivation,
    FeatureTarget,
    FeatureUses,
)
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Paragraph, Table


class OathOfDevotionSpells(Feature):
    def __init__(self):
        super().__init__(
            name="Oath of Devotion Spells", origin="Oath of Devotion Paladin Level 3"
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "From the Paladin level shown, you always have these spells prepared."
            ),
            Table(
                ("Paladin level", "Spells"),
                (
                    ("3", "Protection from Evil and Good, Shield of Faith"),
                    ("5", "Aid, Zone of Truth"),
                    ("9", "Beacon of Hope, Dispel Magic"),
                    ("13", "Freedom of Movement, Guardian of Faith"),
                    ("17", "Commune, Flame Strike"),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "The magic of your oath ensures you always have certain spells ready; when you reach a Paladin level specified in the Oath of Devotion Spells table, you thereafter always have the listed spells prepared.\n"
            "Oath of Devotion Spells\n"
            "Paladin Level	Spells\n"
            "3	Protection from Evil and Good, Shield of Faith\n"
            "5	Aid, Zone of Truth\n"
            "9	Beacon of Hope, Dispel Magic\n"
            "13	Freedom of Movement, Guardian of Faith\n"
            "17	Commune, Flame Strike"
        )
        return description


class SacredWeapon(Feature):
    def __init__(self):
        super().__init__(
            name="Sacred Weapon",
            origin="Oath of Devotion Paladin Level 3",
            activation=FeatureActivation(
                duration="10 Minutes or Until Used Again", range="20-Foot Radius"
            ),
            usage_tags=["buff"],
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.OBJECT

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Imbue a weapon with positive energy."),
            Facts(
                (
                    ("Trigger", "You take the Attack action"),
                    ("Cost", "One use of Channel Divinity"),
                    ("Target", "One Melee weapon you're holding"),
                    (
                        "Duration",
                        "10 minutes, or until you use it again, end it (no action required) or stop carrying the weapon",
                    ),
                    (
                        "Attack",
                        "Add your Charisma modifier (minimum +1) to attack rolls with it",
                    ),
                    (
                        "Damage",
                        "Its normal damage type or Radiant, your choice on each hit",
                    ),
                    (
                        "Light",
                        "Bright Light in a 20-foot radius and Dim Light 20 feet beyond",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "When you take the Attack action, you can expend one use of your Channel Divinity to imbue one Melee weapon that you are holding with positive energy. For 10 minutes or until you use this feature again, you add your Charisma modifier to attack rolls you make with that weapon (minimum bonus of +1), and each time you hit with it, you cause it to deal its normal damage type or Radiant Damage.\n"
            "The weapon also emits Bright Light in a 20-foot radius and Dim Light 20 feet beyond that.\n"
            "You can end this effect early (no action required). This effect also ends if you aren't carrying the weapon."
        )
        return description


class AuraOfDevotion(Feature):
    def __init__(self):
        super().__init__(
            name="Aura of Devotion",
            origin="Oath of Devotion Paladin Level 7",
            usage_tags=["buff"],
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Immunity",
                        "You and your allies are immune to the Charmed condition while in your Aura of Protection",
                    ),
                    (
                        "Already Charmed",
                        "An ally who enters the aura while Charmed ignores the condition while there",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "You and your allies have Immunity to the Charmed condition while in your Aura of Protection. If a Charmed ally enters the aura, that condition has no effect on that ally while there."
        return description


class SmiteOfProtection(Feature):
    def __init__(self):
        super().__init__(
            name="Smite of Protection",
            origin="Oath of Devotion Paladin Level 15",
            activation=FeatureActivation(duration="Until Start of Next Turn"),
            usage_tags=["buff"],
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Your smite radiates protective energy."),
            Facts(
                (
                    ("Trigger", "Whenever you cast Divine Smite"),
                    (
                        "Effect",
                        "You and your allies have Half Cover while in your Aura of Protection",
                    ),
                    ("Duration", "Until the start of your next turn"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "Your magical smite now radiates protective energy. Whenever you cast Divine Smite, you and your allies have Half Cover while in your Aura of Protection. The aura has this benefit until the start of your next turn."
        return description


class HolyNimbus(Feature):
    def __init__(self):
        super().__init__(
            name="Holy Nimbus",
            origin="Oath of Devotion Paladin Level 20",
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION,
                duration="10 Minutes or Until Ended",
            ),
            usage_tags=["buff", "damage"],
            uses=FeatureUses(max_uses=1, regain_all_on="long rest"),
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF

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
                    (
                        "Holy Ward",
                        "Advantage on saving throws a Fiend or an Undead forces you to make",
                    ),
                    (
                        "Radiant Damage",
                        "An enemy that starts its turn in the aura takes Charisma modifier + Proficiency Bonus Radiant damage",
                    ),
                    (
                        "Sunlight",
                        "The aura is filled with Bright Light that is sunlight",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "As a Bonus Action, you can imbue your Aura of Protection with holy power, granting the benefits below for 10 minutes or until you end them (no action required). Once you use this feature, you can't use it again until you finish a Long Rest. You can also restore your use of it by expending a level 5 spell slot (no action required).\n"
            "Holy Ward. You have Advantage on any saving throw you are forced to make by a Fiend or an Undead.\n"
            "Radiant Damage. Whenever an enemy starts its turn in the aura, that creature takes Radiant damage equal to your Charisma modifier plus your Proficiency Bonus.\n"
            "Sunlight. The aura is filled with Bright Light that is sunlight."
        )
        return description
