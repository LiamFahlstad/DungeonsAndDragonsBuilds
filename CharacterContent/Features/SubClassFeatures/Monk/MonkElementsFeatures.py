from Core.Definitions import (
    MONK_HIT_DIE,
    Ability,
)
from Model.Content.Feature import Feature, FeatureActivation, ActionType, FeatureTarget
from CharacterContent.Items.Weapons import WeaponDamageRolls
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Option, Paragraph, dc_formula

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


class ElementalAttunement(Feature):
    def __init__(self):
        super().__init__(
            name="Elemental Attunement",
            origin="Warrior of the Elements Monk Level 3",
            activation=FeatureActivation(duration="10 Minutes or Until Incapacitated"),
            usage_tags=["damage", "control"],
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Imbue yourself with elemental energy."),
            Facts(
                (
                    ("When", "At the start of your turn"),
                    ("Cost", "1 Focus Point"),
                    ("Duration", "10 minutes, or until you're Incapacitated"),
                )
            ),
            Option(
                "While attuned",
                (
                    Facts(
                        (
                            ("Reach", "Your Unarmed Strikes have 10 feet more reach"),
                            (
                                "Elemental Strikes",
                                f"An Unarmed Strike that hits can deal Acid, Cold, Fire, Lightning or Thunder damage instead. If it does, the target can be forced to make a Strength save ({dc_formula(Ability.WISDOM)}); on a failure you move it up to 10 feet toward or away from you.",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "At the start of your turn, you can expend 1 Focus Point to imbue yourself with elemental energy. The energy lasts for 10 minutes or until you have the Incapacitated condition. You gain the following benefits while this feature is active.\n"
            "Reach. When you make an Unarmed Strike, your reach is 10 feet greater than normal, as elemental energy extends from you.\n"
            "Elemental Strikes. Whenever you hit with your Unarmed Strike, you can cause it to deal your choice of Acid, Cold, Fire, Lightning, or Thunder damage rather than its normal damage type. When you deal one of these types with it, you can also force the target to make a Strength saving throw. On a failed save, you can move the target up to 10 feet toward or away from you, as elemental energy swirls around it."
        )
        return description


class ManipulateElements(Feature):
    def __init__(self):
        super().__init__(
            name="Manipulate Elements", origin="Warrior of the Elements Monk Level 3"
        )

    def get_description(self, character: CharacterView) -> str:
        description = "You know the Elementalism spell. Wisdom is your spellcasting ability for it."
        return description


class ElementalBurst(Feature):
    def __init__(self):
        super().__init__(
            name="Elemental Burst",
            origin="Warrior of the Elements Monk Level 6",
            activation=FeatureActivation(
                action_type=ActionType.ACTION, range="120 Feet (20-Foot-Radius Sphere)"
            ),
            usage_tags=["damage"],
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.AREA

    def get_description(self, character: CharacterView) -> str:
        description = (
            "As a Magic action, you can expend 2 Focus Points to cause elemental energy to burst in a 20-foot-radius Sphere centered on a point within 120 feet of yourself. Choose a damage type: Acid, Cold, Fire, Lightning, or Thunder.\n"
            "Each creature in the Sphere must make a Dexterity saving throw. On a failed save, a creature takes damage of the chosen type equal to three rolls of your Martial Arts die. On a successful save, a creature takes half as much damage."
        )
        return description


class StrideOfTheElements(Feature):
    def __init__(self):
        super().__init__(
            name="Stride of the Elements",
            origin="Warrior of the Elements Monk Level 11",
            usage_tags=["buff", "utility"],
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF

    def get_description(self, character: CharacterView) -> str:
        description = "While your Elemental Attunement is active, you also have a Fly Speed and a Swim Speed equal to your Speed."
        return description


class ElementalEpitome(Feature):
    def __init__(self):
        super().__init__(
            name="Elemental Epitome",
            origin="Warrior of the Elements Monk Level 17",
            activation=FeatureActivation(range="5 Feet"),
            usage_tags=["buff", "damage"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("While Elemental Attunement is active:"),
            Facts(
                (
                    (
                        "Damage Resistance",
                        "Resistance to Acid, Cold, Fire, Lightning or Thunder (your choice; change it at the start of each of your turns)",
                    ),
                    (
                        "Destructive Stride",
                        "When you use Step of the Wind, Speed +20 feet for the turn, and creatures of your choice take one roll of your Martial Arts die (Acid, Cold, Fire, Lightning or Thunder) when you enter a space within 5 feet of them, once per turn each",
                    ),
                    (
                        "Empowered Strikes",
                        "Once on each of your turns, an Unarmed Strike that hits deals an extra roll of your Martial Arts die, of the strike's damage type",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "While your Elemental Attunement is active, you also gain the following benefits.\n"
            "Damage Resistance. You gain Resistance to one of the following damage types of your choice: Acid, Cold, Fire, Lightning, or Thunder. At the start of each of your turns, you can change this choice.\n"
            "Destructive Stride. When you use your Step of the Wind, your Speed increases by 20 feet until the end of the turn. For that duration, any creature of your choice takes damage equal to one roll of your Martial Arts die when you enter a space within 5 feet of it. The damage type is your choice of Acid, Cold, Fire, Lightning, or Thunder. A creature can take this damage only once per turn.\n"
            "Empowered Strikes. Once on each of your turns, you can deal extra damage to a target equal to one roll of your Martial Arts die when you hit it with an Unarmed Strike. The extra damage is the same type dealt by that strike."
        )
        return description
