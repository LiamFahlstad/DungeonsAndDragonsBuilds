from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock

ROGUE_HIT_DIE = 8


class Assassinate(Feature):
    def __init__(self):
        super().__init__(name="Assassinate", origin="Assassin Rogue Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You're adept at ambushing a target, granting you the following benefits.\n"
            "Initiative. You have Advantage on Initiative rolls.\n"
            "Surprising Strikes. During the first round of each combat, you have Advantage on attack rolls against any creature that hasn't taken a turn. If your Sneak Attack hits any target during that round, the target takes extra damage of the weapon's type equal to your Rogue level."
        )
        return description


class AssassinsTools(Feature):
    def __init__(self):
        super().__init__(name="Assassin's Tools", origin="Assassin Rogue Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You gain a Disguise Kit and a Poisoner's Kit, and you have proficiency with them."
        return description


class InfiltrationExpertise(Feature):
    def __init__(self):
        super().__init__(name="Infiltration Expertise", origin="Assassin Rogue Level 9")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You are an expert at the following techniques that aid your infiltrations.\n"
            "Masterful Mimicry. You can unerringly mimic another person's speech, handwriting or both if you have spent at least 1 hour studying them.\n"
            "Roving Aim. Your speed isn't reduced to 0 by using Steady Aim."
        )
        return description


class EnvenomWeapons(Feature):
    def __init__(self):
        super().__init__(name="Envenom Weapons", origin="Assassin Rogue Level 13")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you use the Poison option of your Cunning Strike, the target also takes 2d6 Poison damage whenever it fails the saving throw. This damage ignores Resistance to Poison damage."
        return description


class DeathStrike(Feature):
    def __init__(self):
        super().__init__(name="Death Strike", origin="Assassin Rogue Level 17")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you hit with your Sneak Attack on the first round of a combat, the target must succeed on a Constitution saving throw (DC 8 plus your Dexterity modifier and Proficiency Bonus), or the attack's damage is doubled against the target."
        return description
