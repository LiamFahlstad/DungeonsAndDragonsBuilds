import Core.Definitions as Definitions
from Model.Content.Feature import (
    ActionType,
    Feature,
    FeatureActivation,
    FeatureTarget,
    FeatureUses,
    RegainedOn,
)
from Utils import StringUtils
from Core.Rules import levels_gained
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Option, Paragraph, Table, dc_formula
from CharacterContent.Features.ClassFeatures.SpellcastingTable import (
    spellcasting_table,
)

# The Sorcerer Features table's Cantrips and Prepared Spells columns, levels 1-20.
SORCERER_CANTRIPS = (4, 4, 4, 5, 5, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6)
SORCERER_PREPARED_SPELLS = (
    2,
    4,
    6,
    7,
    9,
    10,
    11,
    12,
    14,
    15,
    16,
    16,
    17,
    17,
    18,
    18,
    19,
    20,
    21,
    22,
)


class Spellcasting(Feature):
    def __init__(self):
        super().__init__(name="Spellcasting", origin="Sorcerer Level 1")

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Spellcasting ability", "Charisma"),
                    ("Save DC", dc_formula(Definitions.Ability.CHARISMA)),
                    ("Spell attack", "Charisma modifier + Proficiency Bonus"),
                    (
                        "Cantrips",
                        "As many as the table below; replace one whenever you gain a Sorcerer level",
                    ),
                    (
                        "Prepared spells",
                        "As many as the table below; replace one whenever you gain a Sorcerer level",
                    ),
                    ("Spell slots", "Regain all when you finish a Long Rest"),
                )
            ),
            spellcasting_table("Sorcerer", SORCERER_PREPARED_SPELLS, SORCERER_CANTRIPS),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Spellcasting\n"
            "    * Replacing Cantrips: Change one when you gain a Sorcerer level.\n"
            "    * Replacing Spells: Change one whenever you gain a Sorcerer level.\n"
            "    * Regaining Spell Slots: You regain all expended spell slots when you finish a Long Rest.\n"
            "    * Spellcasting Ability: Charisma"
        )
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST


class InnateSorcery(Feature):
    def __init__(self):
        super().__init__(
            name="Innate Sorcery",
            origin="Sorcerer Level 1",
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION, duration="1 Minute"
            ),
            usage_tags=["buff"],
            uses=FeatureUses(max_uses=2, regain_all_on="long rest"),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # Uses are in the panel below.
        return [
            Paragraph("Unleash the magic an event in your past left in you."),
            Facts(
                (
                    ("Action", "Bonus Action"),
                    ("Duration", "1 minute"),
                    ("Spell DC", "+1 to the spell save DC of your Sorcerer spells"),
                    (
                        "Spell attacks",
                        "Advantage on the attack rolls of Sorcerer spells you cast",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "An event in your past left an indelible mark on you, infusing you with simmering magic. As a Bonus Action, you can unleash that magic for 1 minute, during which you gain the following benefits:\n"
            "The spell save DC of your Sorcerer spells increases by 1.\n"
            "You have Advantage on the attack rolls of Sorcerer spells you cast.\n"
            "You can use this feature twice, and you regain all expended uses of it when you finish a Long Rest."
        )
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class FontOfMagic(Feature):
    def __init__(self):
        super().__init__(
            name="Font of Magic",
            origin="Sorcerer Level 2",
            uses=FeatureUses(
                max_uses=20,
                regain_all_on="long rest",
                current_formula="Current amount: equal to your Sorcerer level.",
                gained_at=levels_gained(lambda level: level, from_level=2),
            ),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # The Sorcery Point boxes are in the panel below.
        return [
            Paragraph(
                "Sorcery Points fuel Metamagic and other features, and convert to and from spell slots."
            ),
            Facts(
                (
                    (
                        "Sorcery Points",
                        "Equal to your Sorcerer level, which is also the most you can have",
                    ),
                    ("Recharge", "All on a Long Rest"),
                )
            ),
            Option(
                "Spell slot into points",
                (
                    Facts(
                        (
                            ("Action", "No action required"),
                            (
                                "Gain",
                                "Sorcery Points equal to the expended slot's level",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Points into a spell slot",
                (
                    Facts(
                        (
                            ("Action", "Bonus Action"),
                            (
                                "Create",
                                "One spell slot, no higher than level 5, from unexpended Sorcery Points",
                            ),
                            ("Lasts", "Until you finish a Long Rest"),
                        )
                    ),
                    Table(
                        ("Slot level", "Sorcery Point cost", "Minimum Sorcerer level"),
                        (
                            ("1", "2", "2"),
                            ("2", "3", "3"),
                            ("3", "5", "5"),
                            ("4", "6", "7"),
                            ("5", "7", "9"),
                        ),
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Rules for Sorcery Points:\n"
            "    * You have Sorcery Points equal to your Sorcerer level, and you can't have more than that. You regain all expended Sorcery Points when you finish a Long Rest.\n"
            "    * Using Sorcery Points: You can use your Sorcery Points to fuel the options below, along with other features, such as Metamagic, that use those points.\n"
            "    * Converting Spell Slots to Sorcery Points: You can expend a spell slot to gain a number of Sorcery Points equal to the slot's level (no action required).\n"
            "    * Creating Spell Slots: As a Bonus Action, you can transform unexpended Sorcery Points into one spell slot. The Creating Spell Slots table shows the cost of creating a spell slot of a given level, and it lists the minimum Sorcerer level you must be to create a slot. Any spell slot you create with this feature vanishes when you finish a Long Rest.\n"
            "   Spell Slot Level | Sorcery Point Cost | Minimum Sorcerer Level\n"
            "   -----------------|--------------------|-----------------------\n"
            "           1        |         2          |           2           \n"
            "           2        |         3          |           3           \n"
            "           3        |         5          |           5           \n"
            "           4        |         6          |           7           \n"
            "           5        |         7          |           9           "
        )
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def number_of_uses(self, character: CharacterView) -> int:
        return character.get_class_level(Definitions.CharacterClass.SORCERER)


class Metamagic(Feature):
    def __init__(self):
        super().__init__(name="Metamagic", origin="Sorcerer Level 2")

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Use",
                        "Spend the option's Sorcery Point cost as you cast a spell; one option per spell unless an option says otherwise",
                    ),
                    (
                        "Options known",
                        "Two; two more at Sorcerer level 10 and two more at 17",
                    ),
                    (
                        "Swap",
                        "Whenever you gain a Sorcerer level, replace one option with one you don't know",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Because your magic flows from within, you can alter your spells to suit your needs; You have Metamagic options to temporarily modify spells you cast. To use an option, you must spend the number of Sorcery Points that it costs.\n"
            "You can use only one Metamagic option on a spell when you cast it unless otherwise noted in one of those options.\n"
            "Whenever you gain a Sorcerer level, you can replace one of your Metamagic options with one you don't know. You gain two more options at Sorcerer level 10 and two more at Sorcerer level 17."
        )
        return description

    def get_resource_tiles(
        self, character: CharacterView
    ) -> list[tuple[str, list[tuple[str, str]]]]:
        options_by_level = {}
        for level in range(2, 21):
            if level < 10:
                options_by_level[level] = 2
            elif level < 17:
                options_by_level[level] = 4
            else:
                options_by_level[level] = 6
        steps = [
            (f"Lv {level_range}", str(value))
            for level_range, value in StringUtils.compress_level_progression(
                options_by_level
            )
        ]
        return [("Metamagic Options Known", steps)]


class SorcerousRestoration(Feature):
    def __init__(self):
        super().__init__(
            name="Sorcerous Restoration",
            origin="Sorcerer Level 5",
            uses=FeatureUses(max_uses=1, regain_all_on="long rest"),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # The once-per-Long-Rest box is in the panel below.
        return [
            Facts(
                (
                    ("Trigger", "You finish a Short Rest"),
                    (
                        "Effect",
                        "Regain expended Sorcery Points, up to half your Sorcerer level (round down)",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "When you finish a Short Rest, you can regain expended Sorcery Points, but no more than a number equal to half your Sorcerer level (round down). Once you use this feature, you can't do so again until you finish a Long Rest."
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST


class SorceryIncarnate(Feature):
    def __init__(self):
        super().__init__(
            name="Sorcery Incarnate", origin="Sorcerer Level 7", usage_tags=["buff"]
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Extra Innate Sorcery",
                        "With no uses of Innate Sorcery left, spend 2 Sorcery Points when you take the Bonus Action to activate it",
                    ),
                    (
                        "Metamagic",
                        "While Innate Sorcery is active, use up to two Metamagic options on each spell you cast",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "If you have no uses of Innate Sorcery left, you can use it if you spend 2 Sorcery Points when you take the Bonus Action to activate it.\n"
            "In addition, while your Innate Sorcery feature is active, you can use up to two of your Metamagic options on each spell you cast."
        )
        return description


class ArcaneApotheosis(Feature):
    def __init__(self):
        super().__init__(
            name="Arcane Apotheosis", origin="Sorcerer Level 20", usage_tags=["buff"]
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Requirement", "Your Innate Sorcery is active"),
                    (
                        "Effect",
                        "Use one Metamagic option on each of your turns without spending Sorcery Points on it",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "While your Innate Sorcery feature is active, you can use one Metamagic option on each of your turns without spending Sorcery Points on it."
        return description
