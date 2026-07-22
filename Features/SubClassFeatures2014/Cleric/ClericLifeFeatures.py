from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class BonusProficiency(Feature):
    def __init__(self):
        super().__init__(name="Bonus Proficiency", origin="Life Domain Cleric Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You gain proficiency with heavy armor."
        return description


class DiscipleOfLife(Feature):
    def __init__(self):
        super().__init__(name="Disciple of Life", origin="Life Domain Cleric Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Your healing spells are more effective. Whenever you use a spell of 1st level or higher to restore hit points to a creature, the creature regains additional hit points equal to 2 + the spell's level."
        return description


class PreserveLifeChannelDivinity(Feature):
    def __init__(self):
        super().__init__(
            name="Channel Divinity: Preserve Life",
            origin="Life Domain Cleric Level 3",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can use your Channel Divinity to heal the badly injured.\n"
            "As an action, you present your holy symbol and evoke healing energy that can restore a number of hit points equal to five times your cleric level. Choose any creatures within 30 feet of you, and divide those hit points among them. This feature can restore a creature to no more than half of its hit point maximum. You can't use this feature on an undead or a construct."
        )
        return description


class LifeDomainSpells(Feature):
    def __init__(self):
        super().__init__(name="Life Domain Spells", origin="Life Domain Cleric Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your connection to this divine domain ensures you always have certain spells ready. When you reach a Cleric level specified in the Life Domain Spells table, you thereafter always have the listed spells prepared.\n"
            "Life Domain Spells\n"
            "Cleric Level\tSpells\n"
            "1st\tBless, Cure Wounds\n"
            "3rd\tLesser Restoration, Spiritual Weapon\n"
            "5th\tBeacon of Hope, Revivify\n"
            "7th\tDeath Ward, Guardian of Faith\n"
            "9th\tMass Cure Wounds, Raise Dead"
        )
        return description


class BlessedHealer(Feature):
    def __init__(self):
        super().__init__(name="Blessed Healer", origin="Life Domain Cleric Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "The healing spells you cast on others heal you as well. When you cast a spell of 1st level or higher that restores hit points to a creature other than you, you regain hit points equal to 2 + the spell's level."
        return description


class DivineStrike(Feature):
    def __init__(self):
        super().__init__(name="Divine Strike", origin="Life Domain Cleric Level 8")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You gain the ability to infuse your weapon strikes with divine energy. Once on each of your turns when you hit a creature with a weapon attack, you can cause the attack to deal an extra 1d8 radiant damage to the target. When you reach 14th level, the extra damage increases to 2d8."
        return description


class SupremeHealing(Feature):
    def __init__(self):
        super().__init__(name="Supreme Healing", origin="Life Domain Cleric Level 17")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you would normally roll one or more dice to restore hit points with a spell, you instead use the highest number possible for each die. For example, instead of restoring 2d6 hit points to a creature, you restore 12."
        return description
