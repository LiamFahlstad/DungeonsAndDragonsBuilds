from CharacterContent.Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class BonusProficiencies(Feature):
    def __init__(self):
        super().__init__(name="Bonus Proficiencies", origin="Way of the Drunken Master Monk Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain proficiency in the Performance skill if you don't already have it. Your martial arts technique mixes combat training with the precision of a dancer and the antics of a jester. You also gain proficiency with brewer's supplies if you don't already have it."
        )
        return description


class DrunkenTechnique(Feature):
    def __init__(self):
        super().__init__(name="Drunken Technique", origin="Way of the Drunken Master Monk Level 3", duration="Until End of Current Turn", usage_tags=["buff"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You learn how to twist and turn quickly as part of your Flurry of Blows. Whenever you use Flurry of Blows, you gain the benefit of the Disengage action, and your walking speed increases by 10 feet until the end of the current turn."
        )
        return description


class TipsySway(Feature):
    def __init__(self):
        super().__init__(name="Tipsy Sway", origin="Way of the Drunken Master Monk Level 6", action_type="reaction", range="5 Feet", usage_tags=["control"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can move in sudden, swaying ways. You gain the following benefits.\n"
            "    * Leap to Your Feet. When you're prone, you can stand up by spending 5 feet of movement, rather than half your speed.\n"
            "    * Redirect Attack. When a creature misses you with a melee attack roll, you can spend 1 ki point as a reaction to cause that attack to hit one creature of your choice, other than the attacker, that you can see within 5 feet of you."
        )
        return description


class DrunkardsLuck(Feature):
    def __init__(self):
        super().__init__(name="Drunkard's Luck", origin="Way of the Drunken Master Monk Level 11", usage_tags=["buff"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You always seem to get a lucky bounce at the right moment. When you make an ability check, an attack roll, or a saving throw and have disadvantage, you can spend 2 ki points to cancel the disadvantage for that roll."
        )
        return description


class IntoxicatedFrenzy(Feature):
    def __init__(self):
        super().__init__(name="Intoxicated Frenzy", origin="Way of the Drunken Master Monk Level 17", usage_tags=["buff"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain the ability to make an overwhelming number of attacks against a group of enemies. When you use your Flurry of Blows, you can make up to three additional attacks with it (up to a total of five Flurry of Blows attacks), provided that each Flurry of Blows attack targets a different creature this turn."
        )
        return description
