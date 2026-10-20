from Core.Definitions import (
    Ability,
    DRUID_HIT_DIE,
    CharacterClass,
)
from Model.Content.Feature import (
    Feature,
    FeatureUses,
    FeatureActivation,
    ActionType,
    RegainedOn,
    FeatureTarget,
    FeatureDice,
)
from Utils import StringUtils
from Core.Rules import MAX_ABILITY_MODIFIER
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Option, Paragraph


class StarMap(Feature):
    def __init__(self):
        super().__init__(
            name="Star Map",
            origin="Circle of the Stars Druid Level 3",
            uses=FeatureUses(
                max_uses=MAX_ABILITY_MODIFIER,
                regain_all_on="long rest",
                current_formula="Current amount: equal to your Wisdom modifier.",
            ),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # Free Guiding Bolt uses are in the panel below.
        return [
            Paragraph(
                "A Tiny star chart you use as a Spellcasting Focus for your Druid spells. Roll on the Star Map table for its form, or choose one."
            ),
            Facts(
                (
                    (
                        "Spells",
                        "While holding it, you have Guidance and Guiding Bolt prepared",
                    ),
                    (
                        "Free Guiding Bolt",
                        "Cast it without a spell slot, Wisdom modifier (minimum once) times per Long Rest",
                    ),
                    (
                        "Replace it",
                        "A 1-hour ceremony during a Short or Long Rest; it destroys the old map",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You’ve created a star chart as part of your heavenly studies. It is a Tiny object, and you can use it as a Spellcasting Focus for your Druid spells. You determine its form by rolling on the Star Map table or by choosing one.\n"
            "While holding the map, you have the Guidance and Guiding Bolt spells prepared, and you can cast Guiding Bolt without expending a spell slot. You can cast it in that way a number of times equal to your Wisdom modifier (minimum of once), and you regain all expended uses when you finish a Long Rest.\n"
            "If you lose the map, you can perform a 1-hour ceremony to magically create a replacement. This ceremony can be performed during a Short or Long Rest, and it destroys the previous map."
        )
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def number_of_uses(self, character: CharacterView) -> int:
        return max(1, character.get_wisdom_modifier())


STARRY_FORM_DICE = FeatureDice(
    "Archer and Chalice",
    (
        (3, "1d8"),
        (10, "2d8"),
    ),
    CharacterClass.DRUID,
    note="+ Wisdom modifier",
)


class StarryForm(Feature):
    def __init__(self):
        super().__init__(
            name="Starry Form",
            origin="Circle of the Stars Druid Level 3",
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION,
                duration="10 Minutes or Until Dismissed/Incapacitated",
                range="10-Foot Radius",
            ),
            usage_tags=["damage", "heal", "buff"],
            dice=STARRY_FORM_DICE,
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # The Archer and Chalice dice are in the panel below.
        return [
            Paragraph(
                "Take on a luminous starry form instead of shape-shifting. You keep your game statistics."
            ),
            Facts(
                (
                    ("Cost", "One use of Wild Shape"),
                    ("Action", "Bonus Action"),
                    (
                        "Duration",
                        "10 minutes. Ends early if you dismiss it (no action required), have the Incapacitated condition, or use this feature again.",
                    ),
                    (
                        "Light",
                        "Bright Light in a 10-foot radius and Dim Light for 10 feet more",
                    ),
                    ("Constellation", "Choose one each time you take the form"),
                )
            ),
            Option(
                "Archer",
                (
                    Facts(
                        (
                            (
                                "Action",
                                "When you take the form, and as a Bonus Action on your later turns",
                            ),
                            ("Range", "60 feet"),
                            ("Target", "One creature"),
                            (
                                "Attack",
                                "Ranged spell attack (Wisdom modifier + Proficiency Bonus)",
                            ),
                            (
                                "Hit",
                                "Archer and Chalice dice (see Dice below) + Wisdom modifier Radiant damage",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Chalice",
                (
                    Facts(
                        (
                            (
                                "Trigger",
                                "You cast a spell using a spell slot that restores Hit Points to a creature",
                            ),
                            ("Range", "30 feet"),
                            ("Target", "You or another creature"),
                            (
                                "Heal",
                                "Archer and Chalice dice (see Dice below) + Wisdom modifier Hit Points",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Dragon",
                (
                    Facts(
                        (
                            (
                                "Effect",
                                "On Intelligence and Wisdom checks, and Constitution saves to maintain Concentration, treat a d20 roll of 9 or lower as a 10",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "As a Bonus Action, you can expend a use of your Wild Shape feature to take on a starry form rather than shape-shifting.\n"
            "While in your starry form, you retain your game statistics, but your body becomes luminous, your joints glimmer like stars, and glowing lines connect them as on a star chart. This form sheds Bright Light in a 10-foot radius and Dim Light for an additional 10 feet. The form lasts for 10 minutes. It ends early if you dismiss it (no action required), have the Incapacitated condition, or use this feature again.\n"
            "Whenever you assume your starry form, choose which of the following constellations glimmers on your body; your choice gives you certain benefits while in the form.\n"
            "Archer. A constellation of an archer appears on you. When you activate this form and as a Bonus Action on your subsequent turns while it lasts, you can make a ranged spell attack, hurling a luminous arrow that targets one creature within 60 feet of yourself. On a hit, the attack deals Radiant damage equal to 1d8 plus your Wisdom modifier.\n"
            "Chalice. A constellation of a life-giving goblet appears on you. Whenever you cast a spell using a spell slot that restores Hit Points to a creature, you or another creature within 30 feet of you can regain Hit Points equal to 1d8 plus your Wisdom modifier.\n"
            "Dragon. A constellation of a wise dragon appears on you. When you make an Intelligence or a Wisdom check or a Constitution saving throw to maintain Concentration, you can treat a roll of 9 or lower on the d20 as a 10.\n"
            + self._current_values(character)
        )
        return description

    @staticmethod
    def _current_values(character: CharacterView) -> str:
        """The constellations' numbers at the character's level (Twinkling
        Constellations turns the 1d8s into 2d8 and gives the Dragon flight)."""
        wisdom_modifier = character.get_wisdom_modifier()
        spell_attack = character.calculate_attack_bonus_for_ability(Ability.WISDOM)
        twinkling = character.has_feature(TwinklingConstellations)
        dice = STARRY_FORM_DICE.at(character)
        lines = [
            f"Archer right now: {spell_attack:+} to hit, {dice} + {wisdom_modifier} Radiant damage.",
            f"Chalice right now: regain {dice} + {wisdom_modifier} Hit Points.",
        ]
        if twinkling:
            lines.append("Dragon right now: also a Fly Speed of 20 feet (can hover).")
        return "\n".join(lines)


class CosmicOmen(Feature):
    def __init__(self):
        super().__init__(
            name="Cosmic Omen",
            origin="Circle of the Stars Druid Level 6",
            activation=FeatureActivation(
                action_type=ActionType.REACTION,
                duration="Until Next Long Rest",
                range="30 Feet",
            ),
            usage_tags=["buff", "control"],
            uses=FeatureUses(
                max_uses=MAX_ABILITY_MODIFIER,
                regain_all_on="long rest",
                current_formula="Current amount: equal to your Wisdom modifier.",
            ),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # Uses are in the panel below.
        return [
            Paragraph(
                "After each Long Rest, consult your Star Map and roll a die: an even roll gives you Weal, an odd roll Woe, until your next Long Rest."
            ),
            Facts(
                (
                    ("Action", "Reaction"),
                    (
                        "Trigger",
                        "A creature you can see within 30 feet is about to make a D20 Test",
                    ),
                    ("Weal (even)", "Roll 1d6 and add it to the total"),
                    ("Woe (odd)", "Roll 1d6 and subtract it from the total"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Whenever you finish a Long Rest, you can consult your Star Map for omens and roll a die. Until you finish your next Long Rest, you gain access to a special Reaction based on whether you rolled an even or an odd number on the die:\n"
            "Weal (Even). Whenever a creature you can see within 30 feet of you is about to make a D20 Test, you can take a Reaction to roll 1d6 and add the number rolled to the total.\n"
            "Woe (Odd). Whenever a creature you can see within 30 feet of you is about to make a D20 Test, you can take a Reaction to roll 1d6 and subtract the number rolled from the total.\n"
            "You can use this Reaction a number of times equal to your Wisdom modifier (minimum of once), and you regain all expended uses when you finish a Long Rest."
        )
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.CREATURE

    def number_of_uses(self, character: CharacterView) -> int:
        return max(1, character.get_wisdom_modifier())


class TwinklingConstellations(Feature):
    def __init__(self):
        super().__init__(
            name="Twinkling Constellations",
            origin="Circle of the Stars Druid Level 10",
            usage_tags=["damage", "heal", "buff", "utility"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("The constellations of your Starry Form improve."),
            Facts(
                (
                    ("Archer and Chalice", "Their 1d8 becomes 2d8"),
                    (
                        "Dragon",
                        "While it's active, you have a Fly Speed of 20 feet and can hover",
                    ),
                    (
                        "Changing",
                        "At the start of each of your turns in Starry Form, you can change which constellation glimmers on your body",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "The constellations of your Starry Form improve. The 1d8 of the Archer and the Chalice becomes 2d8, and while the Dragon is active, you have a Fly Speed of 20 feet and can hover.\n"
            "Moreover, at the start of each of your turns while in your Starry Form, you can change which constellation glimmers on your body."
        )
        return description


class FullOfStars(Feature):
    def __init__(self):
        super().__init__(
            name="Full of Stars",
            origin="Circle of the Stars Druid Level 14",
            usage_tags=["buff"],
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("While in your Starry Form, you become partially incorporeal."),
            Facts((("Resistance", "Bludgeoning, Piercing and Slashing damage"),)),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "While in your Starry Form, you become partially incorporeal, giving you Resistance to Bludgeoning, Piercing, and Slashing damage."
        return description
