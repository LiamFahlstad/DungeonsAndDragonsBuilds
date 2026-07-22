from Definitions import PALADIN_HIT_DIE
from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class DevotionSpells(Feature):
    def __init__(self):
        super().__init__(name="Oath of Devotion Spells", origin="Oath of Devotion Paladin Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain oath spells at the Paladin levels listed. When you reach a Paladin level specified in the Oath of Devotion Spells table, you thereafter always have the listed spells prepared.\n"
            "Oath of Devotion Spells\n"
            "Paladin Level	Spells\n"
            "3	Protection from Evil and Good, Sanctuary\n"
            "5	Lesser Restoration, Zone of Truth\n"
            "9	Beacon of Hope, Dispel Magic\n"
            "13	Freedom of Movement, Guardian of Faith\n"
            "17	Commune, Flame Strike"
        )
        return description


class SacredWeapon(Feature):
    def __init__(self):
        super().__init__(name="Sacred Weapon", origin="Oath of Devotion Paladin Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "As an action, you can imbue one weapon that you are holding with positive energy, using your Channel Divinity. For 1 minute, you add your Charisma modifier to attack rolls made with that weapon (with a minimum bonus of +1). The weapon also emits bright light in a 20-foot radius and dim light 20 feet beyond that. If the weapon is not already magical, it becomes magical for the duration.\n"
            "You can end this effect on your turn as part of any other action. If you are no longer holding or carrying this weapon, or if you fall unconscious, this effect ends."
        )
        return description


class TurnTheUnholy(Feature):
    def __init__(self):
        super().__init__(name="Turn the Unholy", origin="Oath of Devotion Paladin Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "As an action, you present your holy symbol and speak a prayer censuring fiends and undead, using your Channel Divinity. Each fiend or undead that can see or hear you within 30 feet of you must make a Wisdom saving throw. If the creature fails its saving throw, it is turned for 1 minute or until it takes damage.\n"
            "A turned creature must spend its turns trying to move as far away from you as it can, and it can't willingly move to a space within 30 feet of you. It also can't take reactions. For its action, it can use only the Dash action or try to escape from an effect that prevents it from moving. If there's nowhere to move, the creature can use the Dodge action."
        )
        return description


class AuraOfDevotion(Feature):
    def __init__(self):
        super().__init__(name="Aura of Devotion", origin="Oath of Devotion Paladin Level 7")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You and friendly creatures within 10 feet of you can't be charmed while you are conscious."
        return description


class AuraOfDevotionExpansion(Feature):
    def __init__(self):
        super().__init__(
            name="Aura of Devotion Expansion", origin="Oath of Devotion Paladin Level 18"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "The range of your Aura of Devotion increases to 30 feet."
        return description


class PurityOfSpirit(Feature):
    def __init__(self):
        super().__init__(name="Purity of Spirit", origin="Oath of Devotion Paladin Level 15")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You are always under the effects of a Protection from Evil and Good spell."
        return description


class HolyNimbus(Feature):
    def __init__(self):
        super().__init__(name="Holy Nimbus", origin="Oath of Devotion Paladin Level 20")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "As an action, you can emanate an aura of sunlight. For 1 minute, bright light shines from you in a 30-foot radius, and dim light shines 30 feet beyond that.\n"
            "Whenever an enemy creature starts its turn in the bright light, the creature takes 10 radiant damage.\n"
            "In addition, for the duration, you have advantage on saving throws against spells cast by fiends or undead.\n"
            "Once you use this feature, you can't use it again until you finish a long rest."
        )
        return StringUtils.add_boxes(description, 1, regain_all_on="long rest")
