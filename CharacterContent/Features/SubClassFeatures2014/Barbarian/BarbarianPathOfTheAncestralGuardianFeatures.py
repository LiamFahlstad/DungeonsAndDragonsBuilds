from Core.Definitions import CharacterClass
from Model.Content.Feature import (
    Feature,
    FeatureUses,
    FeatureActivation,
    ActionType,
    FeatureTarget,
    RegainedOn,
    FeatureDice,
)
from Utils import StringUtils
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Paragraph


class AncestralProtectors(Feature):
    def __init__(self):
        super().__init__(
            name="Ancestral Protectors",
            origin="Path Of The Ancestral Guardian Barbarian Level 3",
            activation=FeatureActivation(duration="Until the Start of Your Next Turn"),
            usage_tags=["control"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Spectral warriors appear when you rage."),
            Facts(
                (
                    (
                        "Trigger",
                        "While raging, the first creature you hit with an attack on your turn",
                    ),
                    (
                        "Hindered",
                        "Until the start of your next turn, it has disadvantage on attack rolls not against you, and anyone else it hits has resistance to that damage",
                    ),
                    ("Ends", "Early if your rage ends"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "Starting when you choose this path at 3rd level, spectral warriors appear when you enter your rage. While you're raging, the first creature you hit with an attack on your turn becomes the target of the warriors, which hinder its attacks. Until the start of your next turn, that target has disadvantage on any attack roll that isn't against you, and when the target hits a creature other than you with an attack, that creature has resistance to the damage dealt by the attack. The effect on the target ends early if your rage ends."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


SPIRIT_SHIELD_DICE = FeatureDice(
    "Damage Reduction",
    (
        (6, "2d6"),
        (10, "3d6"),
        (14, "4d6"),
    ),
    CharacterClass.BARBARIAN,
)


class SpiritShield(Feature):
    def __init__(self):
        super().__init__(
            name="Spirit Shield",
            origin="Path Of The Ancestral Guardian Barbarian Level 6",
            activation=FeatureActivation(
                action_type=ActionType.REACTION,
                duration="Ends When Your Rage Ends",
                range="30 Feet",
            ),
            usage_tags=["buff"],
            dice=SPIRIT_SHIELD_DICE,
        )

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Beginning at 6th level, the guardian spirits that aid you can provide supernatural protection to those you defend. If you are raging and another creature you can see within 30 feet of you takes damage, you can use your reaction to reduce that damage by 2d6.\n"
            "\n"
            "When you reach certain levels in this class, you can reduce the damage by more: by 3d6 at 10th level and by 4d6 at 14th level."
        )
        level = character.get_class_level(CharacterClass.BARBARIAN)
        description += (
            f"\nRight now: reduce the damage by {2 + (level >= 10) + (level >= 14)}d6."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY


class ConsultTheSpirits(Feature):
    def __init__(self):
        super().__init__(
            name="Consult the Spirits",
            origin="Path Of The Ancestral Guardian Barbarian Level 10",
            usage_tags=["utility"],
            uses=FeatureUses(max_uses=1, regain_all_on="short or long rest"),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Spells",
                        "Cast Augury or Clairvoyance without a spell slot or material components; Wisdom is the spellcasting ability",
                    ),
                    (
                        "Clairvoyance",
                        "Summons one of your ancestral spirits, invisibly, instead of a sensor",
                    ),
                    ("Limit", "Once per short or long rest"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "At 10th level, you gain the ability to consult with your ancestral spirits. When you do so, you cast the Augury or Clairvoyance spell, without using a spell slot or material components. Rather than creating a spherical sensor, this use of clairvoyance invisibly summons one of your ancestral spirits to the chosen location. Wisdom is your spellcasting ability for these spells.\n"
            "\n"
            "After you cast either spell in this way, you can't use this feature again until you finish a short or long rest."
        )
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.SHORT_OR_LONG_REST


class VengefulAncestors(Feature):
    def __init__(self):
        super().__init__(
            name="Vengeful Ancestors",
            origin="Path Of The Ancestral Guardian Barbarian Level 14",
            usage_tags=["damage"],
        )

    def get_description(self, character: CharacterView) -> str:
        description = "At 14th level, your ancestral spirits grow powerful enough to retaliate. When you use your Spirit Shield to reduce the damage of an attack, the attacker takes an amount of force damage that your Spirit Shield prevents."
        return description
