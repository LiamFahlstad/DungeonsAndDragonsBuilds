from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock

PALADIN_HIT_DIE = 10


class OathOfDevotionSpells(Feature):
    def __init__(self):
        super().__init__(
            name="Oath of Devotion Spells", origin="Oath of Devotion Paladin Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "The magic of your oath ensures you always have certain spells ready; when you reach a Paladin level specified in the Oath of Devotion Spells table, you thereafter always have the listed spells prepared.\n"
            "Oath of Devotion Spells\n"
            "Paladin Level	Spells\n"
            "3	Protection from Evil and Good, Shield of Faith\n"
            "5	Aid, Zone of Truth\n"
            "9	Beacon of Hope, Dispel Magic\n"
            "13	Freedom of Movement, Guardian of Faith\n"
            "17	Commune, Flame Strike"
        )
        return description


class SacredWeapon(Feature):
    def __init__(self):
        super().__init__(
            name="Sacred Weapon", origin="Oath of Devotion Paladin Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you take the Attack action, you can expend one use of your Channel Divinity to imbue one Melee weapon that you are holding with positive energy. For 10 minutes or until you use this feature again, you add your Charisma modifier to attack rolls you make with that weapon (minimum bonus of +1), and each time you hit with it, you cause it to deal its normal damage type or Radiant Damage.\n"
            "The weapon also emits Bright Light in a 20-foot radius and Dim Light 20 feet beyond that.\n"
            "You can end this effect early (no action required). This effect also ends if you aren't carrying the weapon."
        )
        return description


class AuraOfDevotion(Feature):
    def __init__(self):
        super().__init__(
            name="Aura of Devotion", origin="Oath of Devotion Paladin Level 7"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You and your allies have Immunity to the Charmed condition while in your Aura of Protection. If a Charmed ally enters the aura, that condition has no effect on that ally while there."
        return description


class SmiteOfProtection(Feature):
    def __init__(self):
        super().__init__(
            name="Smite of Protection", origin="Oath of Devotion Paladin Level 15"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Your magical smite now radiates protective energy. Whenever you cast Divine Smite, you and your allies have Half Cover while in your Aura of Protection. The aura has this benefit until the start of your next turn."
        return description


class HolyNimbus(Feature):
    def __init__(self):
        super().__init__(name="Holy Nimbus", origin="Oath of Devotion Paladin Level 20")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "As a Bonus Action, you can imbue your Aura of Protection with holy power, granting the benefits below for 10 minutes or until you end them (no action required). Once you use this feature, you can't use it again until you finish a Long Rest. You can also restore your use of it by expending a level 5 spell slot (no action required).\n"
            "Holy Ward. You have Advantage on any saving throw you are forced to make by a Fiend or an Undead.\n"
            "Radiant Damage. Whenever an enemy starts its turn in the aura, that creature takes Radiant damage equal to your Charisma modifier plus your Proficiency Bonus.\n"
            "Sunlight. The aura is filled with Bright Light that is sunlight."
        )
        return description
