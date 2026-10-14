import Core.Definitions as Definitions
from Model.Content.Feature import (
    Feature,
    FeatureUses,
    FeatureActivation,
    ActionType,
    RegainedOn,
    FeatureTarget,
)
from Model.Content.Improvements import (
    GrantSense,
    GrantArmorTraining,
    GrantWeaponProficiency,
)
from CharacterContent.Items.Weapons import WeaponProficiency
from Core.Definitions import ArmorType, CharacterClass
from Model.Ledger.LedgerWriter import LedgerWriter
from Utils import StringUtils
from Core.Rules import MAX_PROFICIENCY_BONUS, levels_gained, proficiency_bonus
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Option, Paragraph, Table


class BonusProficiencies(Feature):
    def __init__(self):
        super().__init__(
            name="Bonus Proficiencies", origin="Twilight Domain Cleric Level 3"
        )

    def apply(self, ledger_writer: LedgerWriter):
        # "You gain proficiency with martial weapons and heavy armor."
        GrantWeaponProficiency([WeaponProficiency.MARTIAL]).apply(ledger_writer)
        GrantArmorTraining([ArmorType.HEAVY]).apply(ledger_writer)

    def get_description(self, character: CharacterView) -> str:
        description = "You gain proficiency with martial weapons and heavy armor."
        return description


class TwilightDomainSpells(Feature):
    def __init__(self):
        super().__init__(
            name="Twilight Domain Spells", origin="Twilight Domain Cleric Level 3"
        )

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Your connection to this divine domain ensures you always have certain spells ready. When you reach a Cleric level specified in the Twilight Domain Spells table, you thereafter always have the listed spells prepared.\n"
            "Twilight Domain Spells\n"
            "Cleric Level\tSpells\n"
            "1st\tFaerie Fire, Sleep\n"
            "3rd\tMoonbeam, See Invisibility\n"
            "5th\tAura of Vitality, Leomund's Tiny Hut\n"
            "7th\tAura of Life, Greater Invisibility\n"
            "9th\tCircle of Power, Mislead"
        )
        return description


class EyesOfNight(Feature):
    def __init__(self):
        super().__init__(
            name="Eyes of Night",
            origin="Twilight Domain Cleric Level 3",
            activation=FeatureActivation(
                action_type=ActionType.ACTION, duration="1 Hour", range="10 Feet"
            ),
            usage_tags=["utility"],
        )
        # "You have darkvision out to a range of 300 feet." (sharing it is
        # the activated part)
        self._darkvision = GrantSense(Definitions.Sense.DARKVISION, 300)

    def apply(self, ledger_writer: LedgerWriter):
        self._darkvision.apply(ledger_writer)

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Darkvision",
                        "300 feet. Dim light looks like bright light and darkness like dim light.",
                    ),
                    (
                        "Share",
                        "Action: willing creatures you can see within 10 feet, up to your Wisdom modifier (minimum one), share it for 1 hour",
                    ),
                    (
                        "Recharge",
                        "Share once per long rest, or expend a spell slot of any level to share again",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You can see through the deepest gloom. You have darkvision out to a range of 300 feet. In that radius, you can see in dim light as if it were bright light and in darkness as if it were dim light.\n"
            "As an action, you can magically share the darkvision of this feature with willing creatures you can see within 10 feet of you, up to a number of creatures equal to your Wisdom modifier (minimum of one creature). The shared darkvision lasts for 1 hour. Once you share it, you can't do so again until you finish a long rest, unless you expend a spell slot of any level to share it again."
        )
        description += f"\nRight now: share with up to {max(1, character.get_wisdom_modifier())} creatures."
        return description


class VigilantBlessing(Feature):
    def __init__(self):
        super().__init__(
            name="Vigilant Blessing",
            origin="Twilight Domain Cleric Level 3",
            activation=FeatureActivation(action_type=ActionType.ACTION),
            usage_tags=["buff"],
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY

    def get_description(self, character: CharacterView) -> str:
        description = "The night has taught you to be vigilant. As an action, you give one creature you touch (including possibly yourself) advantage on the next initiative roll the creature makes. This benefit ends immediately after the roll or if you use this feature again."
        return description


class TwilightSanctuaryChannelDivinity(Feature):
    def __init__(self):
        super().__init__(
            name="Channel Divinity: Twilight Sanctuary",
            origin="Twilight Domain Cleric Level 3",
            activation=FeatureActivation(
                action_type=ActionType.ACTION,
                duration="1 Minute or Until You Are Incapacitated or Die",
                range="Self (30-Foot-Radius Sphere)",
            ),
            usage_tags=["heal", "buff"],
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.AREA

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "Use Channel Divinity to refresh your allies with soothing twilight."
            ),
            Facts(
                (
                    ("Action", "Action, presenting your holy symbol"),
                    (
                        "Area",
                        "30-foot-radius sphere of dim light centered on you; it moves with you",
                    ),
                    ("Duration", "1 minute, or until you're incapacitated or die"),
                    (
                        "Trigger",
                        "A creature (including you) ends its turn in the sphere",
                    ),
                )
            ),
            Option(
                "Grant one",
                (
                    Table(
                        ("Benefit", "Effect"),
                        (
                            ("Temporary hit points", "1d6 + Cleric level"),
                            (
                                "End charm or fear",
                                "End one effect causing it to be charmed or frightened",
                            ),
                        ),
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You can use your Channel Divinity to refresh your allies with soothing twilight.\n"
            "As an action, you present your holy symbol, and a sphere of twilight emanates from you. The sphere is centered on you, has a 30-foot radius, and is filled with dim light. The sphere moves with you, and it lasts for 1 minute or until you are incapacitated or die. Whenever a creature (including you) ends its turn in the sphere, you can grant that creature one of these benefits:\n"
            "    * You grant it temporary hit points equal to 1d6 plus your cleric level.\n"
            "    * You end one effect on it causing it to be charmed or frightened."
        )
        level = character.get_class_level(CharacterClass.CLERIC)
        description += f"\nRight now: 1d6 + {level} temporary hit points."
        return description


class StepsOfNight(Feature):
    def __init__(self):
        super().__init__(
            name="Steps of Night",
            origin="Twilight Domain Cleric Level 6",
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION, duration="1 Minute"
            ),
            usage_tags=["utility"],
            uses=FeatureUses(
                max_uses=MAX_PROFICIENCY_BONUS,
                regain_all_on="long rest",
                current_formula="Current amount: equal to your proficiency bonus.",
                gained_at=levels_gained(proficiency_bonus, from_level=6),
            ),
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF

    def get_description(self, character: CharacterView) -> str:
        description = "You can draw on the mystical power of night to rise into the air. As a bonus action when you are in dim light or darkness, you can magically give yourself a flying speed equal to your walking speed for 1 minute. You can use this bonus action a number of times equal to your proficiency bonus, and you regain all expended uses when you finish a long rest."
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def number_of_uses(self, character: CharacterView) -> int:
        return character.get_proficiency_bonus()


class TwilightShroud(Feature):
    def __init__(self):
        super().__init__(
            name="Twilight Shroud",
            origin="Twilight Domain Cleric Level 17",
            usage_tags=["buff"],
        )

    def get_description(self, character: CharacterView) -> str:
        description = "The twilight that you summon offers a protective embrace: you and your allies have half cover while in the sphere created by your Twilight Sanctuary."
        return description
