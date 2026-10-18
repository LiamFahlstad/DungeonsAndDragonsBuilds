from Core.Definitions import PALADIN_HIT_DIE
from Model.Content.Feature import (
    ActionType,
    Feature,
    FeatureActivation,
    FeatureTarget,
    FeatureUses,
    RegainedOn,
)
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Option, Paragraph, Table, dc_formula
from Core.Definitions import Ability


class NaturesWrath(Feature):
    def __init__(self):
        super().__init__(
            name="Nature's Wrath",
            origin="Oath of the Ancients Paladin Level 3",
            activation=FeatureActivation(
                action_type=ActionType.ACTION, duration="1 Minute", range="15 Feet"
            ),
            usage_tags=["control"],
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Conjure spectral vines around nearby creatures."),
            Facts(
                (
                    ("Action", "Magic action"),
                    ("Cost", "One use of Channel Divinity"),
                    (
                        "Target",
                        "Each creature of your choice you can see within 15 feet",
                    ),
                    (
                        "Save",
                        f"Strength save against your Paladin spell save DC ({dc_formula(Ability.CHARISMA)})",
                    ),
                    ("Failed", "Restrained for 1 minute"),
                    (
                        "Repeat save",
                        "At the end of each of its turns, ending the effect on a success",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "As a Magic action, you can expend one use of your Channel Divinity to conjure spectral vines around nearby creatures. Each creature of your choice that you can see within 15 feet of yourself must succeed on a Strength saving throw or have the Restrained condition for 1 minute. A Restrained creature repeats the save at the end of each of its turns, ending the effect on a success."
        return description


class OathOfTheAncientsSpells(Feature):
    def __init__(self):
        super().__init__(
            name="Oath of the Ancients Spells",
            origin="Oath of the Ancients Paladin Level 3",
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "From the Paladin level shown, you always have these spells prepared."
            ),
            Table(
                ("Paladin level", "Spells"),
                (
                    ("3", "Ensnaring Strike, Speak with Animals"),
                    ("5", "Misty Step, Moonbeam"),
                    ("9", "Plant Growth, Protection from Energy"),
                    ("13", "Ice Storm, Stoneskin"),
                    ("17", "Commune with Nature, Tree Stride"),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "The magic of your oath ensures you always have certain spells ready; when you reach a Paladin level specified in the Oath of the Ancients Spells table, you thereafter always have the listed spells prepared.\n"
            "Oath of the Ancients Spells\n"
            "Paladin Level	Spells\n"
            "3	Ensnaring Strike, Speak with Animals\n"
            "5	Misty Step, Moonbeam\n"
            "9	Plant Growth, Protection from Energy\n"
            "13	Ice Storm, Stoneskin\n"
            "17	Commune with Nature, Tree Stride"
        )
        return description


class AuraOfWarding(Feature):
    def __init__(self):
        super().__init__(
            name="Aura of Warding",
            origin="Oath of the Ancients Paladin Level 7",
            usage_tags=["buff"],
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("An eldritch ward blunts energy from beyond the Material Plane."),
            Facts(
                (
                    ("Area", "Your Aura of Protection"),
                    (
                        "Effect",
                        "You and your allies have Resistance to Necrotic, Psychic and Radiant damage",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "Ancient magic lies so heavily upon you that it forms an eldritch ward, blunting energy from beyond the Material Plane; you and your allies have Resistance to Necrotic, Psychic, and Radiant damage while in your Aura of Protection."
        return description


class UndyingSentinel(Feature):
    def __init__(self):
        super().__init__(
            name="Undying Sentinel",
            origin="Oath of the Ancients Paladin Level 15",
            usage_tags=["heal"],
            uses=FeatureUses(max_uses=1, regain_all_on="long rest"),
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Option(
                "Undying",
                (
                    Facts(
                        (
                            (
                                "Trigger",
                                "You're reduced to 0 Hit Points and not killed outright",
                            ),
                            (
                                "Effect",
                                "Drop to 1 Hit Point instead, then regain three times your Paladin level in Hit Points",
                            ),
                            ("Limit", "Once per Long Rest (box below)"),
                        )
                    ),
                ),
            ),
            Option(
                "Ageless",
                (
                    Facts(
                        (
                            (
                                "Effect",
                                "You can't be aged magically, and you cease visibly aging",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "When you are reduced to 0 Hit Points and not killed outright, you can drop to 1 Hit Point instead, and you regain a number of Hit Points equal to three times your Paladin level. Once you use this feature, you can't do so again until you finish a Long Rest.\n"
            "Additionally, you can't be aged magically, and you cease visibly aging."
        )
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST


class ElderChampion(Feature):
    def __init__(self):
        super().__init__(
            name="Elder Champion",
            origin="Oath of the Ancients Paladin Level 20",
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION, duration="1 Minute or Until Ended"
            ),
            usage_tags=["heal", "control"],
            uses=FeatureUses(max_uses=1, regain_all_on="long rest"),
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # The once-per-Long-Rest box is in the panel below.
        return [
            Paragraph("Imbue your Aura of Protection with primal power."),
            Facts(
                (
                    ("Action", "Bonus Action"),
                    ("Duration", "1 minute, or until you end it (no action required)"),
                    (
                        "Recharge",
                        "Once per Long Rest, or expend a level 5 spell slot (no action required) to restore it",
                    ),
                    (
                        "Diminish Defiance",
                        "Enemies in the aura have Disadvantage on saves against your spells and Channel Divinity options",
                    ),
                    (
                        "Regeneration",
                        "Regain 10 Hit Points at the start of each of your turns",
                    ),
                    (
                        "Swift Spells",
                        "Cast a spell with a casting time of an action as a Bonus Action instead",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "As a Bonus Action, you can imbue your Aura of Protection with primal power, granting the following benefits for 1 minute or until you end them (no action required). Once you use this feature, you can't use it again until you finish a Long Rest. You can also restore your use of it by expending a level 5 spell slot (no action required).\n"
            "Diminish Defiance. Enemies in the aura have Disadvantage on saving throws against your spells and Channel Divinity options.\n"
            "Regeneration. At the start of each of your turns, you regain 10 Hit Points.\n"
            "Swift Spells. Whenever you cast a spell that has a casting time of an action, you can cast it using a Bonus Action instead."
        )
        return description
