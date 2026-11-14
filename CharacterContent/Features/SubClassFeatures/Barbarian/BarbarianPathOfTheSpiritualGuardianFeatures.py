import Core.Definitions as Definitions
from Core.Definitions import (
    Ability,
)
from Model.Content.Feature import (
    ActionType,
    Feature,
    FeatureActivation,
    FeatureTarget,
    FeatureUses,
)
from CharacterContent.Features.ClassFeatures.Barbarian.BarbarianFeatures import (
    get_rage_damage_bonus,
)
from CharacterContent.Spells.SpellLists import (
    ClericLevel2Spells,
    ClericLevel3Spells,
)
from Model.Spells import FeatureSpell
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Option, Paragraph


class SpiritualProtectors(Feature):
    def __init__(self):
        super().__init__(
            name="Spiritual Protectors",
            origin="Path Of The Spiritual Guardian Barbarian Level 3",
            usage_tags=["damage", "control"],
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "While your Rage is active, when you hit a creature with a weapon or an Unarmed Strike, the spirits cause one of these effects of your choice:"
            ),
            Option(
                "Distract",
                (
                    Facts(
                        (
                            (
                                "Effect",
                                "Until the start of your next turn, the target has Disadvantage on attack rolls against anyone other than you or another Barbarian with this feature",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Hinder",
                (
                    Facts(
                        (
                            (
                                "Effect",
                                "Activate the Slow mastery property in addition to a different mastery property you're using with that weapon",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Strike",
                (
                    Facts(
                        (
                            (
                                "Damage",
                                "An extra 1d4 Cold, Fire or Lightning damage (your choice)",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Your Rage summons spectral warriors to your aid. While your Rage is active, when you hit a creature with a weapon or an Unarmed Strike, that creature becomes a target of the spirits, which cause one of the following effects of your choice.\n"
            "Distract. Until the start of your next turn, the target has Disadvantage on attack rolls against targets other than you or another Barbarian who has this feature.\n"
            "Hinder. You can activate the Slow mastery property in addition to a different mastery property you're using with that weapon.\n"
            "Strike. The target takes an extra 1d4 damage, which can be Cold, Fire, or Lightning damage (your choice)."
        )
        return description


class SpiritShield(Feature):
    def __init__(self):
        super().__init__(
            name="Spirit Shield",
            origin="Path Of The Spiritual Guardian Barbarian Level 6",
            activation=FeatureActivation(
                action_type=ActionType.REACTION, range="30 Feet"
            ),
            usage_tags=["buff"],
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Your guardian spirits protect those you defend."),
            Facts(
                (
                    ("Action", "Reaction, while your Rage is active"),
                    (
                        "Trigger",
                        "Another creature you can see within 30 feet of you takes damage",
                    ),
                    (
                        "Effect",
                        "Reduce that damage by the total of d6s equal to your Rage Damage bonus",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        level = character.get_class_level(Definitions.CharacterClass.BARBARIAN)
        description = (
            "Your guardian spirits can provide supernatural protection to those you defend. While your Rage is active, when another creature you can see within 30 feet of you takes damage, you can take a Reaction to reduce that damage. To determine the amount the damage is reduced by, roll a number of d6s equal to your Rage Damage bonus, and add them together.\n"
            f"Right now: {get_rage_damage_bonus(level)}d6."
        )
        return description


class ConsultTheSpirits(Feature):
    def __init__(self):
        super().__init__(
            name="Consult the Spirits",
            origin="Path Of The Spiritual Guardian Barbarian Level 10",
            usage_tags=["utility"],
            uses=FeatureUses(max_uses=1, regain_all_on="short or long rest"),
        )

    def granted_spells(self) -> list[FeatureSpell]:
        ruling = "No spell slot or Material components; once per Short or Long Rest (either spell)"
        return [
            FeatureSpell(ClericLevel2Spells.AUGURY, Ability.WISDOM, ruling),
            FeatureSpell(ClericLevel3Spells.CLAIRVOYANCE, Ability.WISDOM, ruling),
        ]

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # The once-per-rest box is in the panel below.
        return [
            Paragraph("You consult with your guardian spirits."),
            Facts(
                (
                    (
                        "Spells",
                        "Augury or Clairvoyance, without a spell slot or Material components",
                    ),
                    (
                        "Clairvoyance",
                        "Instead of a spherical sensor, one of your guardian spirits is invisibly summoned to the chosen location",
                    ),
                    ("Spellcasting ability", "Wisdom"),
                    ("Recharge", "Once per Short or Long Rest"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You gain the ability to consult with your guardian spirits. When you do so, you cast the Augury or Clairvoyance spell without expending a spell slot or needing Material components. Rather than creating a spherical sensor, this use of Clairvoyance invisibly summons one of your guardian spirits to the chosen location. Wisdom is your spellcasting ability for these spells.\n"
            "After you cast either spell in this way, you can't use this feature again until you finish a Short or Long Rest."
        )
        return description


class SpiritsFury(Feature):
    def __init__(self):
        super().__init__(
            name="Spirits' Fury",
            origin="Path Of The Spiritual Guardian Barbarian Level 14",
            usage_tags=["damage"],
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Your spirits hasten your attacks."),
            Facts(
                (
                    (
                        "Trigger",
                        "You roll 18-20 on the d20 for an attack roll with a Melee weapon as part of the Attack action",
                    ),
                    (
                        "Effect",
                        "Make one additional attack roll with the same weapon as part of that action",
                    ),
                    ("Limit", "Once, then not again until the start of your next turn"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "Your spirits hasten your attacks. When you make an attack roll with a Melee weapon as part of the Attack action and roll 18-20 on the d20, you can make one additional attack roll with the same weapon as part of that action. Once you use this feature, you can't do so again until the start of your next turn."
        return description
