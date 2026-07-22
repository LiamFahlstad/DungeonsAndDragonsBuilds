from Core.Definitions import ROGUE_HIT_DIE
from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class FastHands(Feature):
    def __init__(self):
        super().__init__(name="Fast Hands", origin="Thief Rogue Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can use the bonus action granted by your Cunning Action to make a Dexterity (Sleight of Hand) "
            "check, use your thieves' tools to disarm a trap or open a lock, or take the Use an Object action."
        )
        return description


class SecondStoryWork(Feature):
    def __init__(self):
        super().__init__(name="Second-Story Work", origin="Thief Rogue Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain the ability to climb faster than normal; climbing no longer costs you extra movement.\n"
            "In addition, when you make a running jump, the distance you cover increases by a number of feet "
            "equal to your Dexterity modifier."
        )
        return description


class SupremeSneak(Feature):
    def __init__(self):
        super().__init__(name="Supreme Sneak", origin="Thief Rogue Level 9")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You have advantage on a Dexterity (Stealth) check if you move no more than half your speed on the "
            "same turn."
        )
        return description


class UseMagicDevice(Feature):
    def __init__(self):
        super().__init__(name="Use Magic Device", origin="Thief Rogue Level 13")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You have learned enough about the workings of magic that you can improvise the use of items even "
            "when they are not intended for you. You ignore all class, race, and level requirements on the use "
            "of magic items."
        )
        return description


class ThiefsReflexes(Feature):
    def __init__(self):
        super().__init__(name="Thief's Reflexes", origin="Thief Rogue Level 17")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You have become adept at laying ambushes and quickly escaping danger. You can take two turns "
            "during the first round of any combat. You take your first turn at your normal initiative and your "
            "second turn at your initiative minus 10. You can't use this feature when you are surprised."
        )
        return description
