from Features.Core.BaseFeatures import Feature
from Features.Equipment.Weapons import WeaponsDamageRolls
from StatBlocks.CharacterStatBlock import CharacterStatBlock

MONK_HIT_DIE = 8

LEVEL_TO_MARTIAL_ARTS_DIE = {
    1: WeaponsDamageRolls.D6,
    2: WeaponsDamageRolls.D6,
    3: WeaponsDamageRolls.D6,
    4: WeaponsDamageRolls.D6,
    5: WeaponsDamageRolls.D8,
    6: WeaponsDamageRolls.D8,
    7: WeaponsDamageRolls.D8,
    8: WeaponsDamageRolls.D8,
    9: WeaponsDamageRolls.D8,
    10: WeaponsDamageRolls.D8,
    11: WeaponsDamageRolls.D10,
    12: WeaponsDamageRolls.D10,
    13: WeaponsDamageRolls.D10,
    14: WeaponsDamageRolls.D10,
    15: WeaponsDamageRolls.D10,
    16: WeaponsDamageRolls.D10,
    17: WeaponsDamageRolls.D12,
    18: WeaponsDamageRolls.D12,
    19: WeaponsDamageRolls.D12,
    20: WeaponsDamageRolls.D12,
}

LEVEL_TO_FOCUS_POINTS = {
    1: 0,
    2: 2,
    3: 3,
    4: 4,
    5: 5,
    6: 6,
    7: 7,
    8: 8,
    9: 9,
    10: 10,
    11: 11,
    12: 12,
    13: 13,
    14: 14,
    15: 15,
    16: 16,
    17: 17,
    18: 18,
    19: 19,
    20: 20,
}


class MysticArtsSpellcasting(Feature):
    def __init__(self):
        super().__init__(
            name="Spellcasting", origin="Warrior of the Mystic Arts Monk Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You have learned to cast spells. See the Player's Handbook for the rules on spellcasting. The information below details how you use those rules as a Warrior of the Mystic Arts.\n"
            "Cantrips. You know two cantrips of your choice from the Sorcerer spell list. Blade Ward and Thunderclap are recommended. Whenever you gain a Monk level, you can replace one of these cantrips with another cantrip of your choice from the Sorcerer spell list.\n"
            "When you reach Monk level 10, you learn another Sorcerer cantrip of your choice.\n"
            "Prepared Spells of Level 1+. You prepare the list of level 1+ spells that are available for you to cast with this feature. To start, choose three level 1 spells from the Sorcerer spell list. Jump, Magic Missile, and Shield are recommended. The number of spells on your list increases as you gain Monk levels, as shown in the Prepared Spells column of the Warrior of the Mystic Arts Spellcasting table. Whenever that number increases, choose additional spells from the Sorcerer spell list until the number of spells on your list matches the number on the table. The chosen spells must be of a level for which you have spell slots. For example, if you're a level 7 Monk, your list of prepared spells can include five Sorcerer spells of levels 1 and 2 in any combination.\n"
            "Changing Your Prepared Spells. Whenever you gain a Monk level, you can replace one spell on your list with another Sorcerer spell for which you have spell slots.\n"
            "Spellcasting Ability. Wisdom is your spellcasting ability for your Sorcerer spells.\n"
            "Spellcasting Focus. You can use an Arcane Focus as a Spellcasting Focus for your Sorcerer spells.\n"
            "Multiclassing. If you multiclass and have the Spellcasting feature from more than one class, add one third of your Monk levels (round down) to determine your available spell slots."
        )
        return description


class MysticFightingStyle(Feature):
    def __init__(self):
        super().__init__(
            name="Mystic Fighting Style",
            origin="Warrior of the Mystic Arts Monk Level 6",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you take the Attack action on your turn, you can replace one Unarmed Strike with a casting of one of your Sorcerer cantrips that has a casting time of an action."
        return description


class MysticFocus(Feature):
    def __init__(self):
        super().__init__(
            name="Mystic Focus", origin="Warrior of the Mystic Arts Monk Level 6"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You keep your magical power and martial focus in perfect balance, allowing you to convert spell slots into Focus Points, or convert Focus Points into spell slots.\n"
            "Converting Spell Slots to Focus Points. You can expend a spell slot to regain a number of expended Focus Points equal to the slot's level (no action required).\n"
            "Recovering Spell Slots. When you finish a Short Rest or use Uncanny Metabolism, you can transform unexpended Focus Points to recover one expended spell slot. The Recovering Spell Slots table shows the cost of recovering a spell slot of a given level, and it lists the minimum Monk level you must be to recover a slot. You can recover a spell slot no higher than level 4.\n"
            "Recovering Spell Slots\n"
            "Spell Slot Level\tFocus Point Cost\tMin. Monk Level\n"
            "1\t2\t6\n"
            "2\t3\t7\n"
            "3\t5\t13\n"
            "4\t6\t19"
        )
        return description


class FocusedStrike(Feature):
    def __init__(self):
        super().__init__(
            name="Focused Strike", origin="Warrior of the Mystic Arts Monk Level 11"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you use your Stunning Strike, whether the target succeeds or fails on the saving throw, the target has Disadvantage on saving throws against your spells until the start of your next turn."
        return description


class ImprovedMysticFightingStyle(Feature):
    def __init__(self):
        super().__init__(
            name="Improved Mystic Fighting Style",
            origin="Warrior of the Mystic Arts Monk Level 17",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you use Flurry of Blows, you can replace two of the Unarmed Strikes with a casting of one of your level 1 or 2 Sorcerer spells that has a casting time of an action, and you cast it as part of the same Bonus Action you use to activate Flurry of Blows."
        return description
