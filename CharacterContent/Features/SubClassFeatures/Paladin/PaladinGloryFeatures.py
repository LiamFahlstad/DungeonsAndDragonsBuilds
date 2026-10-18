from Core.Definitions import PALADIN_HIT_DIE
from Model.Content.Feature import (
    Feature,
    FeatureUses,
    FeatureActivation,
    ActionType,
    RegainedOn,
    FeatureTarget,
)
from Model.Content.Improvements import SpeedBonus
from Model.Ledger.LedgerWriter import LedgerWriter
from Utils import StringUtils
from Core.Rules import MAX_ABILITY_MODIFIER
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Option, Paragraph, Table


class InspiringSmite(Feature):
    def __init__(self):
        super().__init__(
            name="Inspiring Smite",
            origin="Oath of Glory Paladin Level 3",
            activation=FeatureActivation(range="30 Feet"),
            usage_tags=["heal"],
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Trigger", "Immediately after you cast Divine Smite"),
                    ("Cost", "One use of Channel Divinity"),
                    (
                        "Target",
                        "Creatures of your choice within 30 feet, which can include you",
                    ),
                    (
                        "Effect",
                        "2d8 + Paladin level Temporary Hit Points, divided among them however you like",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "Immediately after you cast Divine Smite, you can expend one use of your Channel Divinity and distribute Temporary Hit Points to creatures of your choice within 30 feet of yourself, which can include you. The total number of Temporary Hit Points equals 2d8 plus your Paladin level, divided among the chosen creatures however you like."
        return description


class GlorySpells(Feature):
    def __init__(self):
        super().__init__(
            name="Oath of Glory Spells", origin="Oath of Glory Paladin Level 3"
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "From the Paladin level shown, you always have these spells prepared."
            ),
            Table(
                ("Paladin level", "Spells"),
                (
                    ("3", "Guiding Bolt, Heroism"),
                    ("5", "Enhance Ability, Magic Weapon"),
                    ("9", "Haste, Protection from Energy"),
                    ("13", "Compulsion, Freedom of Movement"),
                    ("17", "Legend Lore, Yolande's Regal Presence"),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "The magic of your oath ensures you always have certain spells ready; when you reach a Paladin level specified in the Oath of Glory Spells table, you thereafter always have the listed spells prepared.\n"
            "Oath of Glory Spells\n"
            "Paladin Level	Spells\n"
            "3	Guiding Bolt, Heroism\n"
            "5	Enhance Ability, Magic Weapon\n"
            "9	Haste, Protection from Energy\n"
            "13	Compulsion, Freedom of Movement\n"
            "17	Legend Lore, Yolande's Regal Presence"
        )
        return description


class PeerlessAthlete(Feature):
    def __init__(self):
        super().__init__(
            name="Peerless Athlete",
            origin="Oath of Glory Paladin Level 3",
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION, duration="1 Hour"
            ),
            usage_tags=["buff"],
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Action", "Bonus Action"),
                    ("Cost", "One use of Channel Divinity"),
                    ("Duration", "1 hour"),
                    (
                        "Checks",
                        "Advantage on Strength (Athletics) and Dexterity (Acrobatics) checks",
                    ),
                    (
                        "Jumps",
                        "Long and High Jumps go 10 feet farther (the extra distance costs movement as normal)",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "As a Bonus Action, you can expend one use of your Channel Divinity to augment your athleticism. For 1 hour, you have Advantage on Strength (Athletics) and Dexterity (Acrobatics) checks, and the distance of your Long and High Jumps increases by 10 feet (this extra distance costs movement as normal)."
        return description


class AuraOfAlacrity(Feature):
    def __init__(self):
        super().__init__(
            name="Aura of Alacrity",
            origin="Oath of Glory Paladin Level 7",
            usage_tags=["buff"],
        )

    def apply(self, ledger_writer: LedgerWriter):
        # "Your Speed increases by 10 feet." (the allies' boost is situational)
        SpeedBonus(10).apply(ledger_writer)

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Your Speed", "+10 feet"),
                    (
                        "Allies",
                        "When an ally enters your Aura of Protection for the first time on a turn or starts its turn there, its Speed increases by 10 feet until the end of its next turn",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Your Speed increases by 10 feet.\n"
            "In addition, whenever an ally enters your Aura of Protection for the first time on a turn or starts their turn there, the ally's Speed increases by 10 feet until the end of their next turn."
        )
        return description


class GloriousDefense(Feature):
    def __init__(self):
        super().__init__(
            name="Glorious Defense",
            origin="Oath of Glory Paladin Level 15",
            activation=FeatureActivation(
                action_type=ActionType.REACTION, range="10 Feet"
            ),
            usage_tags=["buff", "damage"],
            uses=FeatureUses(
                max_uses=MAX_ABILITY_MODIFIER,
                regain_all_on="long rest",
                current_formula="Current amount: equal to your Charisma modifier.",
            ),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # Uses are in the panel below.
        return [
            Paragraph("Turn defense into a sudden strike."),
            Facts(
                (
                    ("Action", "Reaction"),
                    (
                        "Trigger",
                        "You or a creature you can see within 10 feet is hit by an attack roll",
                    ),
                    (
                        "Effect",
                        "Add your Charisma modifier (minimum +1) to the target's AC against that attack",
                    ),
                    (
                        "Counter",
                        "If the attack misses, make one weapon attack against the attacker as part of this Reaction, if it's within range",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You can turn defense into a sudden strike. When you or another creature you can see within 10 feet of you is hit by an attack roll, you can take a Reaction to grant a bonus to the target's AC against that attack, potentially causing it to miss. The bonus equals your Charisma modifier (minimum of +1). If the attack misses, you can make one attack with a weapon against the attacker as part of this Reaction if the attacker is within your weapon's range.\n"
            "You can use this feature a number of times equal to your Charisma modifier (minimum of once), and you regain all expended uses when you finish a Long Rest."
        )
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY

    def number_of_uses(self, character: CharacterView) -> int:
        return max(1, character.get_charisma_modifier())


class LivingLegend(Feature):
    def __init__(self):
        super().__init__(
            name="Living Legend",
            origin="Oath of Glory Paladin Level 20",
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION, duration="10 Minutes"
            ),
            usage_tags=["buff"],
            uses=FeatureUses(max_uses=1, regain_all_on="long rest"),
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # The once-per-Long-Rest box is in the panel below.
        return [
            Paragraph("Empower yourself with the legends of your great deeds."),
            Facts(
                (
                    ("Action", "Bonus Action"),
                    ("Duration", "10 minutes"),
                    (
                        "Recharge",
                        "Once per Long Rest, or expend a level 5 spell slot (no action required) to restore it",
                    ),
                )
            ),
            Option(
                "Benefits",
                (
                    Facts(
                        (
                            ("Charismatic", "Advantage on all Charisma checks"),
                            (
                                "Saving Throw Reroll",
                                "Reaction when you fail a saving throw: reroll it and use the new roll",
                            ),
                            (
                                "Unerring Strike",
                                "Once on each of your turns, when you miss with a weapon attack roll, it hits instead",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You can empower yourself with the legends—whether true or exaggerated—of your great deeds. As a Bonus Action, you gain the following benefits for 10 minutes. Once you use this feature, you can't use it again until you finish a Long Rest. You can also restore your use of it by expending a level 5 spell slot (no action required).\n"
            "Charismatic. You are blessed with an otherworldly presence and have Advantage on all Charisma checks.\n"
            "Saving Throw Reroll. If you fail a saving throw, you can take a Reaction to reroll it. You must use this new roll.\n"
            "Unerring Strike. Once on each of your turns when you make an attack roll with a weapon and miss, you can cause that attack to hit instead."
        )
        return description
