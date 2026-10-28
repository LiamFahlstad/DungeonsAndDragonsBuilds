from Core.Definitions import Condition
from Model.Content.Feature import Feature, FeatureActivation, ActionType, FeatureTarget
from Model.Content.Improvements import ConditionImmunity
from Model.Ledger.LedgerWriter import LedgerWriter
from Core.Definitions import Ability
from CharacterContent.Spells.SpellLists import DivinationLevel1Spells
from Model.Spells import FeatureSpell
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Option


class KnightlyEnvoy(Feature):
    def __init__(self):
        super().__init__(
            name="Knightly Envoy",
            origin="Banneret Fighter Level 3",
            usage_tags=["utility"],
        )

    def granted_spells(self) -> list[FeatureSpell]:
        return [
            FeatureSpell(
                DivinationLevel1Spells.COMPREHEND_LANGUAGES,
                Ability.CHARISMA,
                "Ritual only",
            )
        ]

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Comprehension",
                        "Cast Comprehend Languages, but only as a Ritual; Charisma is your spellcasting ability for it",
                    ),
                    (
                        "Polyglot",
                        "Learn one language. When you finish a Long Rest, you can swap it for a language you've heard, seen signed or read in the past 24 hours.",
                    ),
                    (
                        "Well Spoken",
                        "Proficiency in Insight, Intimidation, Persuasion or Performance (your choice)",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You know how to conduct yourself with grace as a noble ambassador. You gain the following benefits.\n"
            "Comprehension. You can cast the Comprehend Languages spell but only as a Ritual. Charisma is your spellcasting ability for it.\n"
            "Polyglot. You learn one language from the language tables in the Player’s Handbook or chapter 2 of this book. When you finish a Long Rest, you can replace a language learned from this benefit with another language you have heard, seen signed, or read in the past 24 hours.\n"
            "Well Spoken. You gain proficiency in one of the following skills of your choice: Insight, Intimidation, Persuasion, or Performance."
        )
        return description


class GroupRecovery(Feature):
    def __init__(self):
        super().__init__(
            name="Group Recovery",
            origin="Banneret Fighter Level 3",
            activation=FeatureActivation(range="30-Foot Emanation"),
            usage_tags=["heal"],
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Trigger", "You use Second Wind to regain Hit Points"),
                    (
                        "Target",
                        "Allies in a 30-foot Emanation from you (60 feet from Fighter level 18), up to your Charisma modifier (minimum of one)",
                    ),
                    ("Heal", "1d4 + Fighter level Hit Points each"),
                    ("Limit", "Once per Short or Long Rest"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "When you use your Second Wind to regain Hit Points, you can choose a number of allies within a 30-foot Emanation originating from yourself, up to a number of allies equal to your Charisma modifier (minimum of one). Each of those allies regains Hit Points equal to 1d4 plus your Fighter level. Once you use this ability, you can’t use it again until you finish a Short or Long Rest."
        return description


class TeamTactics(Feature):
    def __init__(self):
        super().__init__(
            name="Team Tactics", origin="Banneret Fighter Level 7", usage_tags=["buff"]
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Trigger", "You use Group Recovery"),
                    (
                        "Effect",
                        "Each chosen ally has Advantage on D20 Tests until the start of your next turn",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "When you use Group Recovery, each chosen ally has Advantage on D20 Tests until the start of your next turn."
        return description


class RallyingSurge(Feature):
    def __init__(self):
        super().__init__(
            name="Rallying Surge",
            origin="Banneret Fighter Level 10",
            activation=FeatureActivation(range="30-Foot Emanation"),
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Trigger", "You use Action Surge"),
                    (
                        "Target",
                        "Allies in a 30-foot Emanation from you (60 feet from Fighter level 18), up to your Charisma modifier (minimum of one)",
                    ),
                    (
                        "Effect",
                        "Each can immediately take a Reaction for one option below",
                    ),
                )
            ),
            Option(
                "Options",
                (
                    Facts(
                        (
                            ("Attack", "One attack with a weapon or an Unarmed Strike"),
                            (
                                "Move",
                                "Up to half its Speed, without provoking Opportunity Attacks",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "When you use your Action Surge, you can choose allies within a 30-foot Emanation originating from yourself, up to a number of allies equal to your Charisma modifier (minimum of one). Each of those allies can immediately take a Reaction to use one of the following options.\n"
            "Attack. The ally makes one attack with a weapon or an Unarmed Strike.\n"
            "Move. The ally moves up to half its Speed without provoking Opportunity Attacks."
        )
        return description


class SharedResilience(Feature):
    def __init__(self):
        super().__init__(
            name="Shared Resilience",
            origin="Banneret Fighter Level 15",
            activation=FeatureActivation(
                action_type=ActionType.REACTION, range="60 Feet"
            ),
            usage_tags=["buff"],
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Action", "Reaction"),
                    (
                        "Trigger",
                        "An ally you can see within 60 feet fails a saving throw",
                    ),
                    ("Cost", "One use of Indomitable"),
                    (
                        "Effect",
                        "The ally rerolls with a bonus equal to your Fighter level and must use the new roll",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "When an ally you can see within 60 feet of yourself fails a saving throw, you can take a Reaction to expend a use of your Indomitable feature. The ally can immediately reroll the saving throw with a bonus equal to your Fighter level; the ally must use the new roll."
        return description


class InspiringCommander(Feature):
    def __init__(self):
        super().__init__(
            name="Inspiring Commander",
            origin="Banneret Fighter Level 18",
            passive=True,
            usage_tags=["buff"],
        )
        self._immunities = [
            ConditionImmunity(Condition.CHARMED),
            ConditionImmunity(Condition.FRIGHTENED),
        ]

    def apply(self, ledger_writer: LedgerWriter):
        for immunity in self._immunities:
            immunity.apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Bolstered Rally",
                        "Group Recovery and Rallying Surge now use a 60-foot Emanation",
                    ),
                    (
                        "Unshakable Bravery",
                        "Immunity to the Charmed and Frightened conditions",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You gain the following benefits.\n"
            "Bolstered Rally. The area of effect for both Group Recovery and Rallying Surge is now a 60-foot Emanation.\n"
            "Unshakable Bravery. You have Immunity to the Charmed and Frightened conditions."
        )
        return description
