from Core.Definitions import Ability, PSION_HIT_DIE
from Model.Content.Feature import (
    ActionType,
    Feature,
    FeatureActivation,
    FeatureUses,
    RegainedOn,
)
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Option, Paragraph, dc_formula


class PsionicPower(Feature):
    def __init__(self):
        super().__init__(
            name="Psionic Power",
            origin="Psion Level 1",
            activation=FeatureActivation(range="30 Feet"),
            usage_tags=["control", "buff", "utility"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "A wellspring of psionic energy, measured in Psionic Energy Dice (number and size set by the Energy Dice column of the Psion table). They fuel your Psion powers; a power that needs a die can't be used when all are expended."
            ),
            Facts(
                (
                    ("Regain", "One die on a Short Rest; all on a Long Rest"),
                    (
                        "Save DC",
                        f"Your Psion spell save DC ({dc_formula(Ability.INTELLIGENCE)})",
                    ),
                )
            ),
            Option(
                "Telekinetic Propel",
                (
                    Facts(
                        (
                            ("Action", "Bonus Action"),
                            ("Range", "30 feet"),
                            (
                                "Target",
                                "One Large or smaller creature other than you that you can see",
                            ),
                            (
                                "Save",
                                "Strength. Failed: moved 5 feet straight toward or away from you.",
                            ),
                            (
                                "Empowered",
                                "Roll a Psionic Energy Die: the distance becomes 5 x the roll. The die is expended only if the target fails.",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Telepathic Connection",
                (
                    Facts(
                        (
                            ("Telepathy", "30 feet"),
                            (
                                "Extend",
                                "Bonus Action: roll a Psionic Energy Die; for 1 hour the range grows by 10 x the roll in feet",
                            ),
                            (
                                "Cost",
                                "The first use after each Long Rest is free; after that, the die is expended",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You harbor a wellspring of psionic energy within "
            "yourself. This energy is represented by your Psionic "
            "Energy Dice. Your Psion level determines the die "
            "size and number of Psionic Energy Dice you have, as "
            "shown in the Energy Dice column of the Psion table. "
            "Your Psionic Energy Dice are used to enhance or "
            "fuel certain Psion features. You start with two such "
            "features: Telekinetic Propel and Telepathic "
            "Connection, each of which is detailed below. Some of "
            "your powers expend the Psionic Energy Dice, as "
            "specified in a power's description, and you can't use "
            "a power if it requires you to use a die when all your "
            "Psionic Energy Dice are expended.\n"
            "You regain one expended Psionic Energy Die when "
            "you finish a Short Rest, and you regain all of them "
            "when you finish a Long Rest.\n"
            "Some features that use Psionic Energy Dice "
            "require your target to make a saving throw. The save "
            "DC equals the spell save DC from this class's "
            "Spellcasting feature.\n"
            "Telekinetic Propel. As a Bonus Action, choose one "
            "Large or smaller creature other than you that you "
            "can see within 30 feet of yourself. When you do so, "
            "the target must succeed on a Strength saving throw "
            "or be moved 5 feet straight toward you or straight "
            "away from you. Alternatively, you can roll one "
            "Psionic Energy Die when you take this Bonus Action, "
            "and the distance moved is equal to 5 times the "
            "number rolled. The die is expended only if the target "
            "fails the saving throw.\n"
            "Telepathic Connection. You have telepathy with a "
            "range of 30 feet. As a Bonus Action, you can roll one "
            "Psionic Energy Die. For the next hour, the range of "
            "your telepathy increases by a number of feet equal "
            "to 10 times the number rolled. The first time you use "
            "this Bonus Action after each Long Rest, you don't "
            "expend the Psionic Energy Die. All other times you "
            "use this feature, you expend the die."
        )
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.SHORT_OR_LONG_REST


class SubtleTelekinesis(Feature):
    def __init__(self):
        super().__init__(name="Subtle Telekinesis", origin="Psion Level 1")

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You know the Mage Hand cantrip. You can cast it "
            "without Somatic components, and you can make the "
            "spectral hand Invisible when you cast it."
        )
        return description


class PsionicDiscipline(Feature):
    def __init__(self):
        super().__init__(name="Psionic Discipline", origin="Psion Level 2")

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Disciplines",
                        "Two of your choice (such as Expanded Awareness and Id Insinuation); one more at Psion levels 5, 10, 13 and 17",
                    ),
                    ("Fuel", "Psionic Energy Dice"),
                    (
                        "Limit",
                        "One Discipline per turn, once per turn, unless an option says otherwise",
                    ),
                    (
                        "Swap",
                        "Whenever you gain a Psion level, replace one with one you don't know",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You learn further psionic techniques that are fueled "
            "by your Psionic Energy Dice. You gain two "
            "disciplines of your choice, such as Expanded "
            "Awareness and Id Insinuation. Disciplines are "
            "described in the “Psionic Discipline Options” section "
            "later in this class's description.\n"
            "You can use only one Discipline each turn and only "
            "once per turn unless otherwise noted in one of those "
            "options.\n"
            "Whenever you gain a Psion level, you can replace "
            "one of your Psionic Discipline options with one you "
            "don't know. You gain one additional option at Psion "
            "levels 5, 10, 13, and 17."
        )
        return description


class PsionicRestoration(Feature):
    def __init__(self):
        super().__init__(
            name="Psionic Restoration",
            origin="Psion Level 5",
            activation=FeatureActivation(action_type=ActionType.ACTION),
            uses=FeatureUses(max_uses=1, regain_all_on="long rest"),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # The once-per-Long-Rest box is in the panel below.
        return [
            Facts(
                (
                    ("Time", "1 minute of meditation"),
                    ("Effect", "At the end of it, regain expended Psionic Energy Dice"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You can perform a meditation that focuses the mind "
            "for 1 minute. At the end of it, you regain expended "
            "Psionic Energy Dice. Once you use this feature, you "
            "can't do so again until you finish a Long Rest."
        )
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST


class PsionicSurge(Feature):
    def __init__(self):
        super().__init__(
            name="Psionic Surge", origin="Psion Level 7", usage_tags=["buff"]
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Push your psionic powers with your life force."),
            Facts(
                (
                    ("Trigger", "You roll one or more Psionic Energy Dice"),
                    ("Cost", "One of your Hit Point Dice"),
                    ("Effect", "Treat any 1, 2 or 3 on those dice as a 4"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You can push your psionic powers using your life "
            "force. After you roll one or more Psionic Energy "
            "Dice, you can expend one of your Hit Point Dice and "
            "treat any roll of 1, 2, or 3 on those Psionic Energy "
            "Dice as a 4."
        )
        return description


class PsionicReserves(Feature):
    def __init__(self):
        super().__init__(
            name="Psionic Reserves", origin="Psion Level 18", usage_tags=["buff"]
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Trigger", "You roll Initiative"),
                    (
                        "Effect",
                        "If you have fewer than four Psionic Energy Dice, regain expended ones until you have four",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "When you roll Initiative, you regain expended uses "
            "of Psionic Energy Dice until you have four if you "
            "have fewer than that."
        )
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.INITIATIVE_ROLL


class EpicBoon(Feature):
    def __init__(self):
        super().__init__(name="Epic Boon", origin="Psion Level 19")

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You gain an Epic Boon feat or another feat of your "
            "choice for which you qualify. Boon of Energy "
            "Resistance is recommended."
        )
        return description


class EnkindledLifeForce(Feature):
    def __init__(self):
        super().__init__(
            name="Enkindled Life Force", origin="Psion Level 20", usage_tags=["buff"]
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Burn your life force to achieve greater psionics."),
            Facts(
                (
                    (
                        "Trigger",
                        "Once per turn, you roll one or more Psionic Energy Dice for a Psion feature or Psionic Discipline",
                    ),
                    ("Cost", "One or two of your Hit Point Dice"),
                    (
                        "Effect",
                        "Roll one extra Psionic Energy Die per Hit Point Die and add it to the total. These rolls don't expend Psionic Energy Dice.",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You burn your life force to achieve greater psionics. "
            "Once per turn, when you roll one or more Psionic "
            "Energy Dice for a Psion feature or Psionic Discipline, "
            "you can expend one or two of your Hit Point Dice. "
            "For each Hit Point Die expended, roll an additional "
            "Psionic Energy Die and add the numbers rolled to "
            "the total. This roll does not expend the Psionic "
            "Energy Die."
        )
        return description
