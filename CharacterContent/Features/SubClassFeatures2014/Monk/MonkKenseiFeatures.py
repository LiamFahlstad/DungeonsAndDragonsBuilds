from Model.Content.Feature import (
    Feature,
    FeatureActivation,
    ActionType,
    FeatureTarget,
)
from CharacterContent.Items.Weapons import WeaponDamageRolls
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Paragraph

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


class KenseiWeapons(Feature):
    def __init__(self):
        super().__init__(name="Kensei Weapons", origin="Way of the Kensei Monk Level 3")

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Choose",
                        "One melee and one ranged weapon type: any simple or martial weapon without the heavy and special properties, or a longbow",
                    ),
                    (
                        "Benefit",
                        "You're proficient with them, and they're monk weapons for you. Many Kensei features need them.",
                    ),
                    (
                        "More",
                        "Another type, melee or ranged, at Monk levels 6, 11 and 17",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Choose two types of weapons to be your kensei weapons: one melee weapon and one ranged weapon. "
            "Each of these weapons can be any simple or martial weapon that lacks the heavy and special properties. "
            "The longbow is also a valid choice. You gain proficiency with these weapons if you don't already have it. "
            "Weapons of the chosen types are monk weapons for you. Many of this tradition's features work only with your kensei weapons. "
            "When you reach 6th, 11th, and 17th level in this class, you can choose another type of weapon – either melee or ranged – "
            "to be a kensei weapon for you, following the criteria above."
        )
        return description


class AgileParry(Feature):
    def __init__(self):
        super().__init__(
            name="Agile Parry",
            origin="Way of the Kensei Monk Level 3",
            activation=FeatureActivation(duration="Until Start of Next Turn"),
            usage_tags=["buff"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Trigger",
                        "You make an Unarmed Strike as part of the Attack action on your turn while holding a melee kensei weapon",
                    ),
                    ("Effect", "+2 AC until the start of your next turn"),
                    (
                        "Requirement",
                        "The weapon is in your hand and you aren't Incapacitated",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "If you make an unarmed strike as part of the Attack action on your turn and are holding a kensei weapon, "
            "you can use it to defend yourself if it is a melee weapon. You gain a +2 bonus to AC until the start of your next turn, "
            "while the weapon is in your hand and you aren't incapacitated."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class KenseiShot(Feature):
    def __init__(self):
        super().__init__(
            name="Kensei's Shot",
            origin="Way of the Kensei Monk Level 3",
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION,
                duration="Until End of Current Turn",
            ),
            usage_tags=["damage"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Action", "Bonus Action on your turn"),
                    (
                        "Effect",
                        "Any target you hit with a ranged attack using a kensei weapon takes an extra 1d4 damage of the weapon's type",
                    ),
                    ("Duration", "Until the end of the current turn"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You can use a bonus action on your turn to make your ranged attacks with a kensei weapon more deadly. "
            "When you do so, any target you hit with a ranged attack using a kensei weapon takes an extra 1d4 damage of the weapon's type. "
            "You retain this benefit until the end of the current turn."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class WayOfTheBrush(Feature):
    def __init__(self):
        super().__init__(
            name="Way of the Brush", origin="Way of the Kensei Monk Level 3"
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Tool proficiency",
                        "Calligrapher's Supplies or Painter's Supplies (your choice)",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "You gain proficiency with your choice of calligrapher's supplies or painter's supplies."
        return description


class MagicKenseiWeapons(Feature):
    def __init__(self):
        super().__init__(
            name="Magic Kensei Weapons",
            origin="Way of the Kensei Monk Level 6",
            usage_tags=["buff"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Magical",
                        "Your attacks with kensei weapons count as magical for overcoming Resistance and Immunity to nonmagical attacks and damage",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "Your attacks with your kensei weapons count as magical for the purpose of overcoming resistance and immunity to nonmagical attacks and damage."
        return description


class DeftStrike(Feature):
    def __init__(self):
        super().__init__(
            name="Deft Strike",
            origin="Way of the Kensei Monk Level 6",
            usage_tags=["damage"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Trigger", "You hit a target with a kensei weapon"),
                    ("Cost", "1 ki point"),
                    ("Extra damage", "Your Martial Arts die"),
                    ("Frequency", "Once on each of your turns"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "When you hit a target with a kensei weapon, you can spend 1 ki point to cause the weapon to deal extra damage to the target "
            "equal to your Martial Arts die. You can use this feature only once on each of your turns."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class SharpenTheBlade(Feature):
    def __init__(self):
        super().__init__(
            name="Sharpen the Blade",
            origin="Way of the Kensei Monk Level 11",
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION,
                duration="1 Minute or Until Feature Used Again",
                range="Touch",
            ),
            usage_tags=["buff"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Action", "Bonus Action"),
                    ("Cost", "Up to 3 ki points"),
                    ("Target", "One kensei weapon you touch"),
                    (
                        "Effect",
                        "Bonus to attack and damage rolls with it equal to the ki points spent",
                    ),
                    ("Duration", "1 minute, or until you use this feature again"),
                    (
                        "Exception",
                        "No effect on a magic weapon that already has a bonus to attack and damage rolls",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "As a bonus action, you can expend up to 3 ki points to grant one kensei weapon you touch a bonus to attack and damage rolls "
            "when you attack with it. The bonus equals the number of ki points you spent. This bonus lasts for 1 minute or until you use "
            "this feature again. This feature has no effect on a magic weapon that already has a bonus to attack and damage rolls."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.OBJECT


class UnearringAccuracy(Feature):
    def __init__(self):
        super().__init__(
            name="Unerring Accuracy",
            origin="Way of the Kensei Monk Level 17",
            usage_tags=["buff"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Your mastery of weapons grants you extraordinary accuracy."),
            Facts(
                (
                    (
                        "Trigger",
                        "You miss with an attack roll using a Monk weapon on your turn",
                    ),
                    ("Effect", "Reroll it"),
                    ("Frequency", "Once on each of your turns"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Your mastery of weapons grants you extraordinary accuracy. If you miss with an attack roll using a monk weapon on your turn, "
            "you can reroll it. You can use this feature only once on each of your turns."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF
