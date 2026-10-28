from Model.Content.Feature import (
    ActionType,
    Feature,
    FeatureActivation,
    FeatureTarget,
    FeatureUses,
    FeatureDice,
)
from Core.Definitions import CharacterClass
from CharacterContent.Spells.SpellLists import WizardLevel7Spells
from Model.Spells import FeatureSpell
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Paragraph, Table


class HorizonWalkerSpells(Feature):
    def __init__(self):
        super().__init__(
            name="Horizon Walker Spells", origin="Horizon Walker Ranger Level 3"
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Learned", "The spells below, from the Ranger level shown"),
                    (
                        "Spells known",
                        "They're Ranger spells for you but don't count against your Ranger spells known",
                    ),
                )
            ),
            Table(
                ("Ranger level", "Spell"),
                (
                    ("3", "Protection from Evil and Good"),
                    ("5", "Misty Step"),
                    ("9", "Haste"),
                    ("13", "Banishment"),
                    ("17", "Teleportation Circle"),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You learn an additional spell when you reach certain levels in this class, as shown in the Horizon Walker Spells table. The spell counts as a ranger spell for you, but it doesn't count against the number of ranger spells you know.\n"
            "Horizon Walker Spells\n"
            "Ranger Level\tSpells\n"
            "3rd\tProtection from Evil and Good\n"
            "5th\tMisty Step\n"
            "9th\tHaste\n"
            "13th\tBanishment\n"
            "17th\tTeleportation Circle"
        )
        return description


class DetectPortal(Feature):
    def __init__(self):
        super().__init__(
            name="Detect Portal",
            origin="Horizon Walker Ranger Level 3",
            activation=FeatureActivation(action_type=ActionType.ACTION, range="1 Mile"),
            usage_tags=["utility"],
            uses=FeatureUses(max_uses=1, regain_all_on="short or long rest"),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # The once-per-Short-or-Long-Rest box is in the panel below.
        return [
            Paragraph("Magically sense the presence of a planar portal."),
            Facts(
                (
                    ("Action", "Action"),
                    (
                        "Effect",
                        "Learn the distance and direction to the closest planar portal within 1 mile",
                    ),
                    (
                        "Examples",
                        'See "Planar Travel" in chapter 2 of the Dungeon Master\'s Guide',
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You gain the ability to magically sense the presence of a planar portal. As an action, you detect the distance and direction to the closest planar portal within 1 mile of you.\n"
            "Once you use this feature, you can't use it again until you finish a short or long rest.\n"
            'See the "Planar Travel" section in chapter 2 of the Dungeon Master\'s Guide for examples of planar portals.'
        )
        return description


PLANAR_WARRIOR_DICE = FeatureDice(
    "Extra Force Damage",
    (
        (3, "1d8"),
        (11, "2d8"),
    ),
    CharacterClass.RANGER,
)


class PlanarWarrior(Feature):
    def __init__(self):
        super().__init__(
            name="Planar Warrior",
            origin="Horizon Walker Ranger Level 3",
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION,
                duration="Until Next Hit on This Turn",
                range="30 Feet",
            ),
            usage_tags=["damage", "buff"],
            dice=PLANAR_WARRIOR_DICE,
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # The extra damage die by Ranger level is in the panel below.
        return [
            Paragraph("Draw on the energy of the multiverse to augment your attacks."),
            Facts(
                (
                    ("Action", "Bonus Action"),
                    ("Target", "One creature you can see within 30 feet"),
                    (
                        "Effect",
                        "The next time you hit it this turn with a weapon attack, all the attack's damage becomes Force damage",
                    ),
                    ("Extra Force damage", "Your Planar Warrior die (below)"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You learn to draw on the energy of the multiverse to augment your attacks.\n"
            "As a bonus action, choose one creature you can see within 30 feet of you. The next time you hit that creature on this turn with a weapon attack, all damage dealt by the attack becomes force damage, and the creature takes an extra 1d8 force damage from the attack. When you reach 11th level in this class, the extra damage increases to 2d8."
        )
        level = character.get_class_level(CharacterClass.RANGER)
        description += (
            f"\nRight now: {'2d8' if level >= 11 else '1d8'} extra force damage."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class EtherealStep(Feature):
    def __init__(self):
        super().__init__(
            name="Ethereal Step",
            origin="Horizon Walker Ranger Level 7",
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION,
                duration="Until End of Current Turn",
            ),
            usage_tags=["utility"],
            uses=FeatureUses(max_uses=1, regain_all_on="short or long rest"),
        )

    def granted_spells(self) -> list[FeatureSpell]:
        return [
            FeatureSpell(
                WizardLevel7Spells.ETHEREALNESS,
                ruling="Cast without a spell slot once per Short or Long Rest via Ethereal Step; spell ends at the end of the current turn",
            )
        ]

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # The once-per-Short-or-Long-Rest box is in the panel below.
        return [
            Paragraph("Step through the Ethereal Plane."),
            Facts(
                (
                    ("Action", "Bonus Action on your turn"),
                    ("Spell", "Etherealness, without expending a spell slot"),
                    ("Duration", "The spell ends at the end of the current turn"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You learn to step through the Ethereal Plane. As a bonus action on your turn, you can cast the Etherealness spell with this feature, without expending a spell slot, but the spell ends at the end of the current turn.\n"
            "Once you use this feature, you can't use it again until you finish a short or long rest."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class DistantStrike(Feature):
    def __init__(self):
        super().__init__(
            name="Distant Strike",
            origin="Horizon Walker Ranger Level 11",
            usage_tags=["damage", "utility"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Pass between the planes in the blink of an eye."),
            Facts(
                (
                    (
                        "Teleport",
                        "When you use the Attack action, teleport up to 10 feet before each attack to an unoccupied space you can see",
                    ),
                    (
                        "Extra attack",
                        "If you attack at least two different creatures with the action, make one additional attack against a third creature",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You gain the ability to pass between the planes in a blink of an eye. When you use the Attack action, you can teleport up to 10 feet before each attack to an unoccupied space you can see.\n"
            "If you attack at least two different creatures with the action, you can make one additional attack with it against a third creature."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class SpectralDefense(Feature):
    def __init__(self):
        super().__init__(
            name="Spectral Defense",
            origin="Horizon Walker Ranger Level 15",
            activation=FeatureActivation(
                action_type=ActionType.REACTION, duration="Until End of This Turn"
            ),
            usage_tags=["buff"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "Slip through the planar boundaries to lessen the harm done to you in battle."
            ),
            Facts(
                (
                    ("Action", "Reaction"),
                    ("Trigger", "You take damage from an attack"),
                    (
                        "Effect",
                        "Resistance to all of that attack's damage on this turn",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "Your ability to move between planes enables you to slip through the planar boundaries to lessen the harm done to you during battle. When you take damage from an attack, you can use your reaction to give yourself resistance to all of that attack's damage on this turn."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF
