from Core.Definitions import MONK_HIT_DIE
from Features.Core.BaseFeatures import Feature
from Features.Equipment.Weapons import WeaponsDamageRolls
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils

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


class KenseiWeapons(Feature):
    def __init__(self):
        super().__init__(name="Kensei Weapons", origin="Way of the Kensei Monk Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Choose two types of weapons to be your kensei weapons: one melee weapon and one ranged weapon. "
            "Each of these weapons can be any simple or martial weapon that lacks the heavy and special properties. "
            "The longbow is also a valid choice. You gain proficiency with these weapons if you don't already have it. "
            "Weapons of the chosen types are monk weapons for you. Many of this tradition's features work only with your kensei weapons. "
            "When you reach 6th, 11th, and 17th level in this class, you can choose another type of weapon – either melee or ranged – "
            "to be a kensei weapon for you, following the criteria above."
        )
        return description


class AgileParry(Feature):
    def __init__(self):
        super().__init__(name="Agile Parry", origin="Way of the Kensei Monk Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "If you make an unarmed strike as part of the Attack action on your turn and are holding a kensei weapon, "
            "you can use it to defend yourself if it is a melee weapon. You gain a +2 bonus to AC until the start of your next turn, "
            "while the weapon is in your hand and you aren't incapacitated."
        )
        return description


class KenseiShot(Feature):
    def __init__(self):
        super().__init__(name="Kensei's Shot", origin="Way of the Kensei Monk Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can use a bonus action on your turn to make your ranged attacks with a kensei weapon more deadly. "
            "When you do so, any target you hit with a ranged attack using a kensei weapon takes an extra 1d4 damage of the weapon's type. "
            "You retain this benefit until the end of the current turn."
        )
        return description


class WayOfTheBrush(Feature):
    def __init__(self):
        super().__init__(name="Way of the Brush", origin="Way of the Kensei Monk Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain proficiency with your choice of calligrapher's supplies or painter's supplies."
        )
        return description


class MagicKenseiWeapons(Feature):
    def __init__(self):
        super().__init__(name="Magic Kensei Weapons", origin="Way of the Kensei Monk Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your attacks with your kensei weapons count as magical for the purpose of overcoming resistance and immunity to nonmagical attacks and damage."
        )
        return description


class DeftStrike(Feature):
    def __init__(self):
        super().__init__(name="Deft Strike", origin="Way of the Kensei Monk Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you hit a target with a kensei weapon, you can spend 1 ki point to cause the weapon to deal extra damage to the target "
            "equal to your Martial Arts die. You can use this feature only once on each of your turns."
        )
        return StringUtils.add_boxes(description, 1, regain_all_on="turn")


class SharpenTheBlade(Feature):
    def __init__(self):
        super().__init__(name="Sharpen the Blade", origin="Way of the Kensei Monk Level 11")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "As a bonus action, you can expend up to 3 ki points to grant one kensei weapon you touch a bonus to attack and damage rolls "
            "when you attack with it. The bonus equals the number of ki points you spent. This bonus lasts for 1 minute or until you use "
            "this feature again. This feature has no effect on a magic weapon that already has a bonus to attack and damage rolls."
        )
        return description


class UnearringAccuracy(Feature):
    def __init__(self):
        super().__init__(name="Unerring Accuracy", origin="Way of the Kensei Monk Level 17")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your mastery of weapons grants you extraordinary accuracy. If you miss with an attack roll using a monk weapon on your turn, "
            "you can reroll it. You can use this feature only once on each of your turns."
        )
        return StringUtils.add_boxes(description, 1, regain_all_on="turn")
