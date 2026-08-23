from Core.Definitions import MONK_HIT_DIE
from CharacterContent.Features.Core.BaseFeatures import Feature
from CharacterContent.Items.Weapons import WeaponDamageRolls
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils

LEVEL_TO_MARTIAL_ARTS_DIE = {
    1: WeaponDamageRolls.D6,
    2: WeaponDamageRolls.D6,
    3: WeaponDamageRolls.D6,
    4: WeaponDamageRolls.D6,
    5: WeaponDamageRolls.D8,
    6: WeaponDamageRolls.D8,
    7: WeaponDamageRolls.D8,
    8: WeaponDamageRolls.D8,
    9: WeaponDamageRolls.D8,
    10: WeaponDamageRolls.D8,
    11: WeaponDamageRolls.D10,
    12: WeaponDamageRolls.D10,
    13: WeaponDamageRolls.D10,
    14: WeaponDamageRolls.D10,
    15: WeaponDamageRolls.D10,
    16: WeaponDamageRolls.D10,
    17: WeaponDamageRolls.D12,
    18: WeaponDamageRolls.D12,
    19: WeaponDamageRolls.D12,
    20: WeaponDamageRolls.D12,
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
        super().__init__(name="Agile Parry", origin="Way of the Kensei Monk Level 3", duration="Until Start of Next Turn", usage_tags=["buff"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "If you make an unarmed strike as part of the Attack action on your turn and are holding a kensei weapon, "
            "you can use it to defend yourself if it is a melee weapon. You gain a +2 bonus to AC until the start of your next turn, "
            "while the weapon is in your hand and you aren't incapacitated."
        )
        return description


class KenseiShot(Feature):
    def __init__(self):
        super().__init__(name="Kensei's Shot", origin="Way of the Kensei Monk Level 3", action_type="bonus_action", duration="Until End of Current Turn", usage_tags=["damage"])

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
        super().__init__(name="Magic Kensei Weapons", origin="Way of the Kensei Monk Level 6", usage_tags=["buff"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your attacks with your kensei weapons count as magical for the purpose of overcoming resistance and immunity to nonmagical attacks and damage."
        )
        return description


class DeftStrike(Feature):
    def __init__(self):
        super().__init__(name="Deft Strike", origin="Way of the Kensei Monk Level 6", usage_tags=["damage"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you hit a target with a kensei weapon, you can spend 1 ki point to cause the weapon to deal extra damage to the target "
            "equal to your Martial Arts die. You can use this feature only once on each of your turns."
        )
        return StringUtils.add_boxes(description, 1, regain_all_on="turn")


class SharpenTheBlade(Feature):
    def __init__(self):
        super().__init__(name="Sharpen the Blade", origin="Way of the Kensei Monk Level 11", action_type="bonus_action", duration="1 Minute or Until Feature Used Again", range="Touch", usage_tags=["buff"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "As a bonus action, you can expend up to 3 ki points to grant one kensei weapon you touch a bonus to attack and damage rolls "
            "when you attack with it. The bonus equals the number of ki points you spent. This bonus lasts for 1 minute or until you use "
            "this feature again. This feature has no effect on a magic weapon that already has a bonus to attack and damage rolls."
        )
        return description

    def get_table_description(self, character_stat_block: CharacterStatBlock) -> list[tuple[str, str]]:
        return [
            ("Action", "Bonus action"),
            ("Cost", "1-3 ki points"),
            ("Target", "One kensei weapon you touch"),
            ("Bonus", "Equal to ki points spent (to attack and damage rolls)"),
            ("Duration", "1 minute or until you use this feature again"),
            ("Restriction", "No effect on magic weapons with existing bonuses"),
        ]


class UnearringAccuracy(Feature):
    def __init__(self):
        super().__init__(name="Unerring Accuracy", origin="Way of the Kensei Monk Level 17", usage_tags=["buff"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your mastery of weapons grants you extraordinary accuracy. If you miss with an attack roll using a monk weapon on your turn, "
            "you can reroll it. You can use this feature only once on each of your turns."
        )
        return StringUtils.add_boxes(description, 1, regain_all_on="turn")
