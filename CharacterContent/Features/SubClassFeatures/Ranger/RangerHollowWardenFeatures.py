from Core.Definitions import Ability, Condition
from Model.Content.Feature import (
    ActionType,
    Feature,
    FeatureActivation,
    FeatureTarget,
    FeatureUses,
)
from Model.Content.Improvements import ConditionImmunity, SavingThrowBonus
from Model.View import CharacterView
from Model.Ledger.LedgerWriter import LedgerWriter
from Model.Content.FeatureText import Block, Facts, Option, Paragraph, Table, dc_formula


class HollowWardenSpells(Feature):
    def __init__(self):
        super().__init__(
            name="Hollow Warden Spells", origin="Hollow Warden Ranger Level 3"
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "From the Ranger level shown, you always have these spells prepared."
            ),
            Table(
                ("Ranger level", "Spell"),
                (
                    ("3", "Wrathful Smite"),
                    ("5", "Alter Self"),
                    ("9", "Phantom Steed"),
                    ("13", "Dominate Beast"),
                    ("17", "Steel Wind Strike"),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "When you reach a Ranger level specified in the Hollow Warden Spells table, you thereafter always have the listed spell prepared.\n"
            "Hollow Warden Spells\n"
            "Ranger Level	Spells\n"
            "3	Wrathful Smite\n"
            "5	Alter Self\n"
            "9	Phantom Steed\n"
            "13	Dominate Beast\n"
            "17	Steel Wind Strike"
        )
        return description


class WrathOfTheWild(Feature):
    def __init__(self):
        super().__init__(
            name="Wrath of the Wild",
            origin="Hollow Warden Ranger Level 3",
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION,
                duration="1 Minute or Until Incapacitated",
                range="10-Foot Emanation",
            ),
            usage_tags=["buff", "control"],
        )

    def calculate_dc(self, character: CharacterView) -> int:
        return character.calculate_difficulty_class_for_ability(Ability.WISDOM)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "Transform into a ghastly form drawn from ancient horrors of the land."
            ),
            Facts(
                (
                    ("Cost", "One use of Favored Enemy"),
                    ("Action", "Bonus Action"),
                    (
                        "Duration",
                        "1 minute; ends early if you're Incapacitated, die, or end it (no action required)",
                    ),
                )
            ),
            Option(
                "While transformed",
                (
                    Facts(
                        (
                            ("Ancient Armor", "+1 to AC; +2 from Ranger level 11"),
                            (
                                "Prowling Retribution",
                                "Right after a creature you can see within 5 feet damages you or an ally, make an Opportunity Attack against it",
                            ),
                            (
                                "Unnerving Aura",
                                f"When you transform and at the start of each of your turns, each creature of your choice in a 10-foot Emanation makes a Wisdom save against your spell save DC ({dc_formula(Ability.WISDOM)}). Failed: Frightened until the start of your next turn.",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You draw power from the strange and ancient horrors of the land, causing you to sprout unnatural growths, such as bloody antlers or putrid fangs, or causing your shadow to lengthen or twist around you. As a Bonus Action, you can expend a use of Favored Enemy to transform into a ghastly form, gaining the following benefits for 1 minute or until you have the Incapacitated condition, die, or end the transformation (no action required).\n"
            "Ancient Armor. You gain a +1 bonus to AC, as your body is wreathed in rotten bark and beastly bristles. This bonus increases to +2 when you reach Ranger level 11.\n"
            "Prowling Retribution. Immediately after a creature you can see within 5 feet of yourself deals damage to you or one of your allies, you can make an Opportunity Attack against that creature.\n"
            "Unnerving Aura. When you transform and at the start of each of your subsequent turns, each creature of your choice in a 10-foot Emanation originating from you makes a Wisdom saving throw against your spell save DC. On a failed save, a creature has the Frightened condition until the start of your next turn."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.AREA


class HungeringMight(Feature):
    def __init__(self):
        super().__init__(
            name="Hungering Might",
            origin="Hollow Warden Ranger Level 7",
            usage_tags=["buff", "heal"],
        )

    def apply(self, ledger_writer: LedgerWriter):
        def bonus(cs: CharacterView) -> int:
            return max(1, cs.get_wisdom_modifier())

        SavingThrowBonus([Ability.CONSTITUTION], bonus).apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Constitution saves", "+ Wisdom modifier (minimum +1)"),
                    (
                        "Feeding",
                        "Once per turn, when you hit a creature with an attack roll while transformed by Wrath of the Wild and Bloodied, regain 1d10 + Wisdom modifier Hit Points",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You gain a bonus to Constitution saving throws equal to your Wisdom modifier (minimum of +1).\n"
            "In addition, once per turn when you hit a creature with an attack roll while you are transformed using Wrath of the Wild, you regain a number of Hit Points equal to 1d10 plus your Wisdom modifier, provided you are Bloodied when you hit."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class RotAndViolence(Feature):
    def __init__(self):
        super().__init__(
            name="Rot and Violence",
            origin="Hollow Warden Ranger Level 11",
            usage_tags=["control"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("While transformed with Wrath of the Wild:"),
            Facts(
                (
                    (
                        "Menacing Aura",
                        "A creature that fails its save against your Unnerving Aura also can't regain Hit Points or take Reactions until the start of your next turn",
                    ),
                    (
                        "Strangling Roots",
                        "When you hit with a weapon attack roll, use the Sap or Slow mastery property as well as a different one",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Your dedication to wild eldritch beings alters you further. When transformed using Wrath of the Wild, you gain the following additional benefits.\n"
            "Menacing Aura. When a creature fails its saving throw against your Unnerving Aura, it also can’t regain Hit Points or take Reactions until the start of your next turn.\n"
            "Strangling Roots. When you hit a creature with an attack roll using a weapon, you can activate the Sap or Slow mastery property in addition to a different mastery property you’re using with that weapon."
        )
        return description


class AncientMight(Feature):
    def __init__(self):
        super().__init__(
            name="Ancient Might",
            origin="Hollow Warden Ranger Level 15",
            usage_tags=["damage", "heal", "buff"],
            uses=FeatureUses(max_uses=1, regain_all_on="long rest"),
        )
        self._immunity = ConditionImmunity(Condition.EXHAUSTION)

    def apply(self, ledger_writer: LedgerWriter):
        self._immunity.apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # Persistent Wrath's once-per-Long-Rest box is in the panel below.
        return [
            Facts(
                (
                    (
                        "Ominous Strikes",
                        "Attacks that hit a Frightened creature deal extra damage equal to your Wisdom modifier",
                    ),
                    (
                        "Persistent Wrath",
                        "If you drop to 0 Hit Points but don't die while transformed by Wrath of the Wild, your Hit Points become 2 x Ranger level instead. Once per Long Rest; expend a level 4+ spell slot (no action required) to use it again.",
                    ),
                    ("Timeless", "Immunity to the Exhaustion condition"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You become wholly suffused with the wild’s ancient and terrible power, granting you the following benefits.\n"
            "Ominous Strikes. When you hit a creature that has the Frightened condition with an attack roll, that attack deals extra damage equal to your Wisdom modifier.\n"
            "Persistent Wrath. If you’re reduced to 0 Hit Points but not killed outright while transformed using Wrath of the Wild, you can surge with wild power. Your Hit Points instead change to a number equal to twice your Ranger level. Once you use this feature, you can’t do so again until you finish a Long Rest. You can also expend a level 4+ spell slot (no action required) to restore your use of this feature.\n"
            "Timeless. You have Immunity to the Exhaustion condition."
        )
        return description
