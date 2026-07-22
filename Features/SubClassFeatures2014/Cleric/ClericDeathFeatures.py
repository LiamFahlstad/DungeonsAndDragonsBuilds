import Core.Definitions as Definitions
from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class BonusProficiency(Feature):
    def __init__(self):
        super().__init__(name="Bonus Proficiency", origin="Death Domain Cleric Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You gain proficiency with martial weapons."
        return description


class Reaper(Feature):
    def __init__(self):
        super().__init__(name="Reaper", origin="Death Domain Cleric Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You learn one necromancy cantrip of your choice from any spell list. When you cast a necromancy cantrip that normally targets only one creature, the spell can instead target two creatures within range and within 5 feet of each other."
        return description


class DeathDomainSpells(Feature):
    def __init__(self):
        super().__init__(name="Death Domain Spells", origin="Death Domain Cleric Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your connection to this divine domain ensures you always have certain spells ready. When you reach a Cleric level specified in the Death Domain Spells table, you thereafter always have the listed spells prepared.\n"
            "Death Domain Spells\n"
            "Cleric Level\tSpells\n"
            "1st\tFalse Life, Ray of Sickness\n"
            "3rd\tBlindness/Deafness, Ray of Enfeeblement\n"
            "5th\tAnimate Dead, Vampiric Touch\n"
            "7th\tBlight, Death Ward\n"
            "9th\tAntilife Shell, Cloudkill"
        )
        return description


class TouchOfDeathChannelDivinity(Feature):
    def __init__(self):
        super().__init__(
            name="Channel Divinity: Touch of Death",
            origin="Death Domain Cleric Level 3",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        cleric_level = character_stat_block.get_class_level(
            Definitions.CharacterClass.CLERIC
        )
        damage = 5 + 2 * cleric_level
        description = f"You can use Channel Divinity to destroy another creature's life force by touch. When you hit a creature with a melee attack, you can use Channel Divinity to deal extra necrotic damage to the target. The damage equals 5 + twice your cleric level ({damage})."
        return description


class InescapableDestruction(Feature):
    def __init__(self):
        super().__init__(
            name="Inescapable Destruction", origin="Death Domain Cleric Level 6"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Your ability to channel negative energy becomes more potent. Necrotic damage dealt by your cleric spells and Channel Divinity options ignores resistance to necrotic damage."
        return description


class DivineStrike(Feature):
    def __init__(self):
        super().__init__(name="Divine Strike", origin="Death Domain Cleric Level 8")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You gain the ability to infuse your weapon strikes with necrotic energy. Once on each of your turns when you hit a creature with a weapon attack, you can cause the attack to deal an extra 1d8 necrotic damage to the target. When you reach 14th level, the extra damage increases to 2d8."
        return description


class ImprovedReaper(Feature):
    def __init__(self):
        super().__init__(name="Improved Reaper", origin="Death Domain Cleric Level 17")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you cast a necromancy spell of 1st through 5th level that targets only one creature, the spell can instead target two creatures within range and within 5 feet of each other. If the spell consumes its material components, you must provide them for each target."
        return description
