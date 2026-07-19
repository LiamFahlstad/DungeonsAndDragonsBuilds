from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock

SORCERER_HIT_DIE = 6


class SpellfireSpells(Feature):
    def __init__(self):
        super().__init__(name="Spellfire Spells", origin="Spellfire Sorcerer Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you reach a Sorcerer level specified in the Spellfire Spells table, you thereafter always have the listed spells prepared.\n"
            "Spellfire Spells\n"
            "Sorcerer Level	Spells\n"
            "3	Cure Wounds, Guiding Bolt, Lesser Restoration, Scorching Ray\n"
            "5	Aura of Vitality, Dispel Magic\n"
            "7	Fire Shield, Wall of Fire\n"
            "9	Greater Restoration, Flame Strike"
        )
        return description


class SpellfireBurst(Feature):
    def __init__(self):
        super().__init__(name="Spellfire Burst", origin="Spellfire Sorcerer Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you spend at least 1 Sorcery Point as part of a Magic action or a Bonus Action on your turn, you can unleash one of the following magical effects of your choice. You can do so only once per turn.\n"
            "Bolstering Flames. You or one creature you can see within 30 feet of yourself gains Temporary Hit Points equal to 1d4 plus your Charisma modifier.\n"
            "Radiant Fire. One creature you can see within 30 feet of yourself takes 1d4 Fire or Radiant damage (your choice)."
        )
        return description


class AbsorbSpells(Feature):
    def __init__(self):
        super().__init__(name="Absorb Spells", origin="Spellfire Sorcerer Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You always have Counterspell prepared.\n"
            "Additionally, whenever a target fails the saving throw against a Counterspell you cast, you regain 1d4 Sorcery Points."
        )
        return description


class HonedSpellfire(Feature):
    def __init__(self):
        super().__init__(name="Honed Spellfire", origin="Spellfire Sorcerer Level 14")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Your Spellfire Burst improves. You add your Sorcerer level to the Temporary Hit Points gained from Bolstering Flames, and the damage of your Radiant Fire increases to 1d8."
        return description


class CrownOfSpellfire(Feature):
    def __init__(self):
        super().__init__(
            name="Crown of Spellfire", origin="Spellfire Sorcerer Level 18"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you use Innate Sorcery, you can alter it and infuse yourself with the essence of spellfire, gaining the following benefits while this use of Innate Sorcery is active. Once you use this feature to alter Innate Sorcery, you can’t use it again until you finish a Long Rest unless you spend 5 Sorcery Points (no action required) to restore your use of it.\n"
            "Burning Life Force. Once per turn when you are hit by an attack roll, you can expend a number of Hit Point Dice, up to a maximum equal to your Charisma modifier (minimum of one). Roll the expended dice, and reduce the amount of damage from that attack equal to the total rolled.\n"
            "Flight. You gain a Fly Speed of 60 feet and can hover.\n"
            "Spell Avoidance. When you’re subjected to a spell or magical effect that allows you to make a saving throw to take only half damage, you instead take no damage if you succeed on the save and only half damage if you fail. You can’t use this benefit if you have the Incapacitated condition."
        )
        return description
