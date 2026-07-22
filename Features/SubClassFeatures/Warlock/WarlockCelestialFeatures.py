from Core.Definitions import WARLOCK_HIT_DIE
from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class CelestialSpells(Feature):
    def __init__(self):
        super().__init__(
            name="Celestial Spells", origin="Celestial Patron Warlock Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "The magic of your patron ensures you always have certain spells ready; when you reach a Warlock level specified in the Celestial Spells table, you thereafter always have the listed spells prepared."
        return description


class HealingLight(Feature):
    def __init__(self):
        super().__init__(
            name="Healing Light", origin="Celestial Patron Warlock Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain the ability to channel celestial energy to heal wounds. You have a pool of d6s to fuel this healing. The number of dice in the pool equals 1 plus your Warlock level.\n"
            "As a Bonus Action, you can heal yourself or one creature you can see within 60 feet of yourself, expending dice from the pool. The maximum number of dice you can expend at once equals your Charisma modifier (minimum of one die). Roll the dice you expend, and restore a number of Hit Points equal to the roll's total. Your pool regains all expended dice when you finish a Long Rest."
        )
        return description


class RadiantSoul(Feature):
    def __init__(self):
        super().__init__(name="Radiant Soul", origin="Celestial Patron Warlock Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Your link to your patron allows you to serve as a conduit for radiant energy. You have Resistance to Radiant damage. Once per turn, when a spell you cast deals Radiant or Fire damage, you can add your Charisma modifier to that spell's damage against one of the spell's targets."
        return description


class CelestialResilience(Feature):
    def __init__(self):
        super().__init__(
            name="Celestial Resilience", origin="Celestial Patron Warlock Level 10"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You gain Temporary Hit Points whenever you use your Magical Cunning feature or finish a Short or Long Rest. These Temporary Hit Points equal your Warlock level plus your Charisma modifier. Additionally, choose up to five creatures you can see when you gain the points. Those creatures each gain Temporary Hit Points equal to half your Warlock level plus your Charisma modifier."
        return description


class SearingVengeance(Feature):
    def __init__(self):
        super().__init__(
            name="Searing Vengeance", origin="Celestial Patron Warlock Level 14"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you or an ally within 60 feet of you is about to make a Death Saving Throw, you can unleash radiant energy to save the creature. The creature regains Hit Points equal to half its Hit Point maximum and can end the Prone condition on itself. Each creature of your choice that is within 30 feet of the creature takes Radiant damage equal to 2d8 plus your Charisma modifier, and each has the Blinded condition until the end of the current turn.\n"
            "Once you use this feature, you can't use it again until you finish a Long Rest."
        )
        return description
