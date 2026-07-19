from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock

PALADIN_HIT_DIE = 10


class OathOfVengeanceSpells(Feature):
    def __init__(self):
        super().__init__(
            name="Oath of Vengeance Spells", origin="Oath of Vengeance Paladin Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "The magic of your oath ensures you always have certain spells ready; when you reach a Paladin level specified in the Oath of Vengeance Spells table, you thereafter always have the listed spells prepared.\n"
            "Oath of Vengeance Spells\n"
            "Paladin Level	Spells\n"
            "3	Bane, Hunter's Mark\n"
            "5	Hold Person, Misty Step\n"
            "9	Haste, Protection from Energy\n"
            "13	Banishment, Dimension Door\n"
            "17	Hold Monster, Scrying"
        )
        return description


class VowOfEnmity(Feature):
    def __init__(self):
        super().__init__(
            name="Vow of Enmity", origin="Oath of Vengeance Paladin Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you take the Attack action, you can expend one use of your Channel Divinity to utter a vow of enmity against a creature you can see within 30 feet of yourself. You have Advantage on attack rolls against the creature for 1 minute or until you use this feature again.\n"
            "If the creature drops to 0 Hit Points before the vow ends, you can transfer the vow to a different creature within 30 feet of yourself (no action required)."
        )
        return description


class RelentlessAvenger(Feature):
    def __init__(self):
        super().__init__(
            name="Relentless Avenger", origin="Oath of Vengeance Paladin Level 7"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Your supernatural focus helps you close off a foe's retreat. When you hit a creature with an Opportunity Attack, you can reduce the creature's Speed to 0 until the end of the current turn. You can then move up to half your Speed as part of the same Reaction. This movement doesn't provoke Opportunity Attacks."
        return description


class SoulOfVengeance(Feature):
    def __init__(self):
        super().__init__(
            name="Soul of Vengeance", origin="Oath of Vengeance Paladin Level 15"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Immediately after a creature under the effect of your Vow of Enmity hits or misses with an attack roll, you can take a Reaction to make a melee attack against that creature if it's within range."
        return description


class AvengingAngel(Feature):
    def __init__(self):
        super().__init__(
            name="Avenging Angel", origin="Oath of Vengeance Paladin Level 20"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "As a Bonus Action, you gain the benefits below for 10 minutes or until you end them (no action required). Once you use this feature, you can't use it again until you finish a Long Rest. You can also restore your use of it by expending a level 5 spell slot (no action required).\n"
            "Flight. You sprout spectral wings on your back and have a Fly Speed of 60 feet, and can hover.\n"
            "Frightful Aura. Whenever an enemy starts its turn in your Aura of Protection, that creature must succeed on a Wisdom saving throw or have the Frightened condition for 1 minute or until it takes any damage. Attack rolls against the Frightened creature have Advantage."
        )
        return description
