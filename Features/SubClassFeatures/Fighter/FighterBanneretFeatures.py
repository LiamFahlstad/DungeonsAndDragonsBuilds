from Core.Definitions import FIGHTER_HIT_DIE
from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class KnightlyEnvoy(Feature):
    def __init__(self):
        super().__init__(name="Knightly Envoy", origin="Banneret Fighter Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You know how to conduct yourself with grace as a noble ambassador. You gain the following benefits.\n"
            "Comprehension. You can cast the Comprehend Languages spell but only as a Ritual. Charisma is your spellcasting ability for it.\n"
            "Polyglot. You learn one language from the language tables in the Player’s Handbook or chapter 2 of this book. When you finish a Long Rest, you can replace a language learned from this benefit with another language you have heard, seen signed, or read in the past 24 hours.\n"
            "Well Spoken. You gain proficiency in one of the following skills of your choice: Insight, Intimidation, Persuasion, or Performance."
        )
        return description


class GroupRecovery(Feature):
    def __init__(self):
        super().__init__(name="Group Recovery", origin="Banneret Fighter Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you use your Second Wind to regain Hit Points, you can choose a number of allies within a 30-foot Emanation originating from yourself, up to a number of allies equal to your Charisma modifier (minimum of one). Each of those allies regains Hit Points equal to 1d4 plus your Fighter level. Once you use this ability, you can’t use it again until you finish a Short or Long Rest."
        return description


class TeamTactics(Feature):
    def __init__(self):
        super().__init__(name="Team Tactics", origin="Banneret Fighter Level 7")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you use Group Recovery, each chosen ally has Advantage on D20 Tests until the start of your next turn."
        return description


class RallyingSurge(Feature):
    def __init__(self):
        super().__init__(name="Rallying Surge", origin="Banneret Fighter Level 10")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you use your Action Surge, you can choose allies within a 30-foot Emanation originating from yourself, up to a number of allies equal to your Charisma modifier (minimum of one). Each of those allies can immediately take a Reaction to use one of the following options.\n"
            "Attack. The ally makes one attack with a weapon or an Unarmed Strike.\n"
            "Move. The ally moves up to half its Speed without provoking Opportunity Attacks."
        )
        return description


class SharedResilience(Feature):
    def __init__(self):
        super().__init__(name="Shared Resilience", origin="Banneret Fighter Level 15")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When an ally you can see within 60 feet of yourself fails a saving throw, you can take a Reaction to expend a use of your Indomitable feature. The ally can immediately reroll the saving throw with a bonus equal to your Fighter level; the ally must use the new roll."
        return description


class InspiringCommander(Feature):
    def __init__(self):
        super().__init__(name="Inspiring Commander", origin="Banneret Fighter Level 18")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain the following benefits.\n"
            "Bolstered Rally. The area of effect for both Group Recovery and Rallying Surge is now a 60-foot Emanation.\n"
            "Unshakable Bravery. You have Immunity to the Charmed and Frightened conditions."
        )
        return description
