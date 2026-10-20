from Core.Definitions import CharacterClass, PALADIN_HIT_DIE
from Model.Content.Feature import Feature, FeatureActivation, ActionType, FeatureTarget
from Utils import StringUtils
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Paragraph, Table


class RedemptionSpells(Feature):
    def __init__(self):
        super().__init__(
            name="Oath of Redemption Spells",
            origin="Oath of Redemption Paladin Level 3",
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "From the Paladin level shown, you always have these spells prepared."
            ),
            Table(
                ("Paladin level", "Spells"),
                (
                    ("3", "Sanctuary, Sleep"),
                    ("5", "Calm Emotions, Hold Person"),
                    ("9", "Counterspell, Hypnotic Pattern"),
                    ("13", "Otiluke's Resilient Sphere, Stoneskin"),
                    ("17", "Hold Monster, Wall of Force"),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
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
        super().__init__(
            name="Channel Divinity: Emissary of Peace",
            origin="Oath of Redemption Paladin Level 3",
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION, duration="10 Minutes"
            ),
            usage_tags=["buff"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "Use Channel Divinity to augment your presence with divine power."
            ),
            Facts(
                (
                    ("Action", "Bonus Action"),
                    ("Effect", "+5 to Charisma (Persuasion) checks"),
                    ("Duration", "10 minutes"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "You can use your Channel Divinity to augment your presence with divine power. As a bonus action, you grant yourself a +5 bonus to Charisma (Persuasion) checks for the next 10 minutes."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class RebukeTheViolent(Feature):
    def __init__(self):
        super().__init__(
            name="Channel Divinity: Rebuke the Violent",
            origin="Oath of Redemption Paladin Level 3",
            activation=FeatureActivation(
                action_type=ActionType.REACTION, range="30 Feet"
            ),
            usage_tags=["damage"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Use Channel Divinity to rebuke those who use violence."),
            Facts(
                (
                    ("Action", "Reaction"),
                    (
                        "Trigger",
                        "Immediately after an attacker within 30 feet deals damage with an attack against a creature other than you",
                    ),
                    ("Save", "Wisdom, made by the attacker"),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (
                    (
                        "Radiant damage equal to the damage it just dealt",
                        "Half as much damage",
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "You can use your Channel Divinity to rebuke those who use violence. Immediately after an attacker within 30 feet of you deals damage with an attack against a creature other than you, you can use your reaction to force the attacker to make a Wisdom saving throw. On a failed save, the attacker takes radiant damage equal to the damage it just dealt. On a successful save, it takes half as much damage."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class AuraOfTheGuardian(Feature):
    def __init__(self):
        super().__init__(
            name="Aura of the Guardian",
            origin="Oath of Redemption Paladin Level 7",
            activation=FeatureActivation(
                action_type=ActionType.REACTION, range="10 Feet"
            ),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Shield your allies from harm at the cost of your own health."),
            Facts(
                (
                    ("Action", "Reaction"),
                    ("Trigger", "A creature within 10 feet of you takes damage"),
                    ("Effect", "You magically take that damage instead"),
                    (
                        "Limits",
                        "No other effects that accompany the damage are transferred, and the damage can't be reduced in any way",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "You can shield your allies from harm at the cost of your own health. When a creature within 10 feet of you takes damage, you can use your reaction to magically take that damage, instead of that creature taking it. This feature doesn't transfer any other effects that might accompany the damage, and this damage can't be reduced in any way."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY


class AuraOfTheGuardianExpansion(Feature):
    def __init__(self):
        super().__init__(
            name="Aura of the Guardian Expansion",
            origin="Oath of Redemption Paladin Level 18",
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [Facts((("Aura of the Guardian range", "30 feet"),))]

    def get_description(self, character: CharacterView) -> str:
        description = "The range of your Aura of the Guardian increases to 30 feet."
        return description


class ProtectiveSpirit(Feature):
    def __init__(self):
        super().__init__(
            name="Protective Spirit",
            origin="Oath of Redemption Paladin Level 15",
            usage_tags=["heal"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("A holy presence mends your wounds in combat."),
            Facts(
                (
                    (
                        "Trigger",
                        "You end your turn in combat with fewer than half your Hit Points and aren't Incapacitated",
                    ),
                    ("Healing", "1d6 + half your Paladin level"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "A holy presence mends your wounds in combat. You regain hit points equal to 1d6 + half your Paladin level if you end your turn in combat with fewer than half of your hit points remaining and you aren't incapacitated."
        level = character.get_class_level(CharacterClass.PALADIN)
        description += f"\nRight now: 1d6 + {level // 2} hit points."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class EmissaryOfRedemption(Feature):
    def __init__(self):
        super().__init__(
            name="Emissary of Redemption",
            origin="Oath of Redemption Paladin Level 20",
            usage_tags=["buff", "damage"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("You become an avatar of peace."),
            Facts(
                (
                    (
                        "Resistance",
                        "All damage dealt by other creatures (their attacks, spells and other effects)",
                    ),
                    (
                        "Retribution",
                        "A creature that hits you with an attack takes Radiant damage equal to half the damage you take from it",
                    ),
                    (
                        "Lost",
                        "If you attack a creature, cast a spell on it, or deal damage to it other than by this feature, neither benefit works against it until you finish a Long Rest",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You become an avatar of peace, which gives you two benefits:\n"
            "    * You have resistance to all damage dealt by other creatures (their attacks, spells, and other effects).\n"
            "    * Whenever a creature hits you with an attack, it takes radiant damage equal to half the damage you take from the attack.\n"
            "\n"
            "If you attack a creature, cast a spell on it, or deal damage to it by any means but this feature, neither benefit works against that creature until you finish a long rest."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF
