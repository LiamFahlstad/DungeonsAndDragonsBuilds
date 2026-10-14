import Core.Definitions as Definitions
from Core.Definitions import (
    BARBARIAN_HIT_DIE,
    Ability,
)
from Model.Content.Feature import Feature, FeatureActivation, ActionType, FeatureTarget
from CharacterContent.Features.ClassFeatures.Barbarian.BarbarianFeatures import (
    get_rage_damage_bonus,
)
from Model.View import CharacterView
from Model.Content.FeatureText import (
    Block,
    Facts,
    Paragraph,
    dc_formula,
)


def _vitality_current_values(character: CharacterView) -> str:
    level = character.get_class_level(Definitions.CharacterClass.BARBARIAN)
    return (
        f"Right now: {level} Temporary Hit Points when you Rage; "
        f"{get_rage_damage_bonus(level)}d6 for the other creature."
    )


class VitalityOfTheTree(Feature):
    def __init__(self):
        super().__init__(
            name="Vitality of the Tree",
            origin="Path Of The World Tree Barbarian Level 3",
            activation=FeatureActivation(range="10 Feet"),
            usage_tags=["heal"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Your Rage taps the life force of the World Tree."),
            Facts(
                (
                    (
                        "Vitality Surge",
                        "When you activate your Rage, gain Temporary Hit Points equal to your Barbarian level",
                    ),
                    (
                        "Life-Giving Force",
                        "At the start of each of your turns while raging, another creature within 10 feet gains Temporary Hit Points: roll d6s equal to your Rage Damage bonus. They vanish when your Rage ends.",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Your Rage taps into the life force of the World Tree. You gain the following benefits.\n"
            "Vitality Surge. When you activate your Rage, you gain a number of Temporary Hit Points equal to your Barbarian level.\n"
            "Life-Giving Force. At the start of each of your turns while your Rage is active, you can choose another creature within 10 feet of yourself to gain Temporary Hit Points. To determine the number of Temporary Hit Points, roll a number of d6s equal to your Rage Damage bonus, and add them together. If any of these Temporary Hit Points remain when your Rage ends, they vanish.\n"
            + _vitality_current_values(character)
        )
        return description


class BranchesOfTheTree(Feature):
    def __init__(self):
        super().__init__(
            name="Branches of the Tree",
            origin="Path Of The World Tree Barbarian Level 6",
            activation=FeatureActivation(
                action_type=ActionType.REACTION, range="30 Feet"
            ),
            usage_tags=["control"],
        )

    def calculate_dc(self, character: CharacterView) -> int:
        strength_modifier = character.get_strength_modifier()
        proficiency_bonus = character.get_proficiency_bonus()
        return 8 + strength_modifier + proficiency_bonus

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Spectral branches of the World Tree pull a foe to you."),
            Facts(
                (
                    ("Action", "Reaction, while your Rage is active"),
                    (
                        "Trigger",
                        "A creature you can see starts its turn within 30 feet of you",
                    ),
                    ("Save", f"Strength, DC {dc_formula(Ability.STRENGTH)}"),
                    (
                        "Failed",
                        "Teleported to an unoccupied space you can see within 5 feet of you (or the nearest one); you can then make its Speed 0 until the end of the turn",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "Whenever a creature you can see starts its turn within 30 feet of you while your Rage is active, you can take a Reaction to summon spectral branches of the World Tree around it. The target must succeed on a Strength saving throw (DC 8 plus your Strength modifier and Proficiency Bonus) or be teleported to an unoccupied space you can see within 5 feet of yourself or in the nearest unoccupied space you can see. After the target teleports, you can reduce its Speed to 0 until the end of the current turn."
        return description


class BatteringRoots(Feature):
    def __init__(self):
        super().__init__(
            name="Battering Roots",
            origin="Path Of The World Tree Barbarian Level 10",
            usage_tags=["buff", "control"],
        )

    def get_description(self, character: CharacterView) -> str:
        description = "During your turn, your reach is 10 feet greater with any Melee weapon that has the Heavy or Versatile property, as tendrils of the World Tree extend from you. When you hit with such a weapon on your turn, you can activate the Push or Topple mastery property in addition to a different mastery property you're using with that weapon."
        return description


class TravelAlongTheTree(Feature):
    def __init__(self):
        super().__init__(
            name="Travel along the Tree",
            origin="Path Of The World Tree Barbarian Level 14",
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION, range="60 Feet"
            ),
            usage_tags=["buff"],
        )

    def get_description(self, character: CharacterView) -> str:
        description = "When you activate your Rage and as a Bonus Action while your Rage is active, you can teleport up to 60 feet to an unoccupied space you can see. In addition, once per Rage, you can increase the range of that teleport to 150 feet. When you do so, you can also bring up to six willing creatures who are within 10 feet of you. Each creature teleports to an unoccupied space of your choice within 10 feet of your destination space."
        return description
