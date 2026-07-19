from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock

ROGUE_HIT_DIE = 8


class FastHands(Feature):
    def __init__(self):
        super().__init__(name="Fast Hands", origin="Thief Rogue Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "As a Bonus Action, you can do one of the following.\n"
            "Sleight of Hand. Make a Dexterity (Sleight of Hand) check to pick a lock or disarm a trap with Thieves' Tools or to pick a pocket.\n"
            "Use an Object. Take the Utilize action, or take the Magic action to use a magic item that requires an action."
        )
        return description


class SecondStoryWork(Feature):
    def __init__(self):
        super().__init__(name="Second Story Work", origin="Thief Rogue Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You've trained to get into especially hard-to-reach places, granting you these benefits.\n"
            "Climber. You gain a Climb Speed equal to your Speed.\n"
            "Jumper. You can determine your jump distance using your Dexterity rather than your Strength."
        )
        return description


class SupremeSneak(Feature):
    def __init__(self):
        super().__init__(name="Supreme Sneak", origin="Thief Rogue Level 9")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain the following Cunning Strike option.\n"
            "Stealth Attack (Cost: 1d6). If you have the Hide action's Invisible condition, this attack doesn't end that condition on you if you end the turn behind Three-Quarters Cover or Total Cover."
        )
        return description


class UseMagicDevice(Feature):
    def __init__(self):
        super().__init__(name="Use Magic Device", origin="Thief Rogue Level 13")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You've learned how to maximize use of magic items, granting you the following benefits.\n"
            "Attunement. You can attune to up to four magic items at once.\n"
            "Charges. Whenever you use a magic item property that expends charges, roll 1d6. On a roll of 6, you use the property without expending the charges.\n"
            "Scrolls. You can use any Spell Scroll, using Intelligence as your spellcasting ability for the spell. If the spell is a cantrip or a level 1 spell, you can cast it reliably. If the scroll contains a higher-level spell, you must first succeed on an Intelligence (Arcana) check (DC 10 plus the spell's level). On a successful check, you cast the spell from the scroll. On a failed check, the scroll disintegrates."
        )
        return description


class ThiefsReflexes(Feature):
    def __init__(self):
        super().__init__(name="Thief's Reflexes", origin="Thief Rogue Level 17")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You are adept at laying ambushes and quickly escaping danger. You can take two turns during the first round of any combat. You take your first turn at your normal Initiative and your second turn at your Initiative minus 10."
        return description
