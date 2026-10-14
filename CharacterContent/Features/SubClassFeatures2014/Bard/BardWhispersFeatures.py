from Core.Definitions import (
    BARD_HIT_DIE,
    CharacterClass,
    Ability,
)
from Model.Content.Feature import (
    FeatureUses,
    Feature,
    FeatureActivation,
    ActionType,
    FeatureTarget,
    FeatureDice,
)
from Utils import StringUtils
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Option, Paragraph, dc_formula

PSYCHIC_BLADES_DICE = FeatureDice(
    "Psychic Damage",
    (
        (3, "2d6"),
        (5, "3d6"),
        (10, "5d6"),
        (15, "8d6"),
    ),
    CharacterClass.BARD,
)


class PsychicBlades(Feature):
    def __init__(self):
        super().__init__(
            name="Psychic Blades",
            origin="College of Whispers Bard Level 3",
            usage_tags=["damage"],
            dice=PSYCHIC_BLADES_DICE,
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY

    def get_description(self, character: CharacterView) -> str:
        if character.get_class_level(CharacterClass.BARD) < 5:
            psychic_damage = "2d6"
        elif character.get_class_level(CharacterClass.BARD) < 10:
            psychic_damage = "3d6"
        elif character.get_class_level(CharacterClass.BARD) < 15:
            psychic_damage = "5d6"
        else:
            psychic_damage = "8d6"

        description = (
            "When you join the College of Whispers at 3rd level, you gain the ability to make your weapon attacks magically toxic to a creature's mind.\n"
            "\n"
            f"When you hit a creature with a weapon attack, you can expend one use of your Bardic Inspiration to deal an additional {psychic_damage} psychic damage to that target. You can do so only once per round on your turn.\n"
            "\n"
            "The psychic damage increases when you reach certain levels in this class, increasing to 3d6 at 5th level, 5d6 at 10th level, and 8d6 at 15th level."
        )
        return description


class WordsOfTerror(Feature):
    def __init__(self):
        super().__init__(
            name="Words of Terror",
            origin="College of Whispers Bard Level 3",
            activation=FeatureActivation(
                duration="1 Hour or Until Attacked or Damaged"
            ),
            usage_tags=["control"],
            uses=FeatureUses(max_uses=1, regain_all_on="short or long rest"),
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY

    def get_description(self, character: CharacterView) -> str:
        description = (
            "At 3rd level, you learn to infuse innocent-seeming words with an insidious magic that can inspire terror.\n"
            "\n"
            "If you speak to a humanoid alone for at least 1 minute, you can attempt to seed paranoia and fear into its mind. At the end of the conversation, the target must succeed on a Wisdom saving throw against your spell save DC or be frightened of you or another creature of your choice. The target is frightened in this way for 1 hour, until it is attacked or damaged, or until it witnesses its allies being attacked or damaged.\n"
            "\n"
            "If the target succeeds on its saving throw, the target has no hint that you tried to frighten it.\n"
            "\n"
            "Once you use this feature, you can't use it again until you finish a short rest or long rest."
        )
        return description


class MantleOfWhispers(Feature):
    def __init__(self):
        super().__init__(
            name="Mantle of Whispers",
            origin="College of Whispers Bard Level 6",
            activation=FeatureActivation(
                action_type=ActionType.ACTION,
                duration="1 Hour or Until Ended",
                range="30 Feet",
            ),
            usage_tags=["utility"],
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Steal a dead humanoid's shadow and wear their persona."),
            Option(
                "Capture a shadow",
                (
                    Facts(
                        (
                            ("Action", "Reaction"),
                            ("Trigger", "A humanoid dies within 30 feet of you"),
                            ("Keep it", "Until you use it or finish a Long Rest"),
                            ("Limit", "Once per Short or Long Rest"),
                        )
                    ),
                ),
            ),
            Option(
                "Use the shadow",
                (
                    Facts(
                        (
                            ("Action", "Action; the shadow vanishes"),
                            (
                                "Disguise",
                                "You look like the dead person, healthy and alive, for 1 hour or until you end it as a Bonus Action",
                            ),
                            (
                                "Knowledge",
                                "You know what the humanoid would freely share with a casual acquaintance (no secrets), enough to pass as them",
                            ),
                            (
                                "Seeing through it",
                                "A creature's Wisdom (Insight) check contested by your Charisma (Deception) check, with +5 to your check",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "At 6th level, you gain the ability to adopt a humanoid's persona. When a humanoid dies within 30 feet of you, you can magically capture its shadow using your reaction. You retain this shadow until you use it or you finish a long rest.\n"
            "\n"
            "You can use the shadow as an action. When you do so, it vanishes, magically transforming into a disguise that appears on you. You now look like the dead person, but healthy and alive. This disguise lasts for 1 hour or until you end it as a bonus action.\n"
            "\n"
            "While you're in the disguise, you gain access to all information that the humanoid would freely share with a casual acquaintance. Such information includes general details on its background and personal life, but doesn't include secrets. The information is enough that you can pass yourself off as the person by drawing on its memories.\n"
            "\n"
            "Another creature can see through this disguise by succeeding on a Wisdom (Insight) check contested by your Charisma (Deception) check. You gain a +5 bonus to your check.\n"
            "\n"
            "Once you capture a shadow with this feature, you can't capture another one with it until you finish a short or long rest."
        )
        return description


class ShadowLore(Feature):
    def __init__(self):
        super().__init__(
            name="Shadow Lore",
            origin="College of Whispers Bard Level 14",
            activation=FeatureActivation(
                action_type=ActionType.ACTION,
                duration="8 Hours or Until Attacked or Damaged",
                range="30 Feet",
            ),
            usage_tags=["control"],
            uses=FeatureUses(max_uses=1, regain_all_on="long rest"),
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # The once-per-Long-Rest box is in the panel below.
        return [
            Paragraph("Whisper a phrase that taps a creature's deepest fears."),
            Facts(
                (
                    ("Action", "Action"),
                    ("Range", "30 feet"),
                    (
                        "Target",
                        "One creature that can hear you and shares a language with you (otherwise it succeeds automatically)",
                    ),
                    (
                        "Save",
                        f"Wisdom save against your spell save DC ({dc_formula(Ability.CHARISMA)}). Succeeded: no effect.",
                    ),
                    (
                        "Failed",
                        "Charmed by you for 8 hours, or until you or your allies attack or damage it. It believes you know its most mortifying secret.",
                    ),
                    (
                        "While Charmed",
                        "It obeys your commands and grants you favors as a close friend would, but won't risk its life or fight for you unless already inclined to",
                    ),
                    ("Afterwards", "It has no idea why it feared you"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "At 14th level, you gain the ability to weave dark magic into your words and tap into a creature's deepest fears.\n"
            "\n"
            "As an action, you magically whisper a phrase that only one creature of your choice within 30 feet of you can hear. The target must make a Wisdom saving throw against your spell save DC. It automatically succeeds if it doesn't share a language with you or if it can't hear you. On a successful saving throw, your whisper sounds like unintelligible mumbling and has no effect.\n"
            "\n"
            "If the target fails its saving throw, it is charmed by you for the next 8 hours or until you or your allies attack or damage it. It interprets the whispers as a description of its most mortifying secret.\n"
            "\n"
            "While you gain no knowledge of this secret, the target is convinced you know it. While charmed in this way, the creature obeys your commands for fear that you will reveal its secret. It won't risk its life for you or fight for you, unless it was already inclined to do so. It grants you favors and gifts it would offer to a close friend.\n"
            "\n"
            "When the effect ends, the creature has no understanding of why it held you in such fear.\n"
            "\n"
            "Once you use this feature, you can't use it again until you finish a long rest."
        )
        return description
