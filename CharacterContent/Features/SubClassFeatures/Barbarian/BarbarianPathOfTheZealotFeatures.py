import Core.Definitions as Definitions
from Core.Definitions import BARBARIAN_HIT_DIE
from CharacterContent.Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class DivineFury(Feature):
    def __init__(self):
        super().__init__(
            name="Divine Fury", origin="Path Of The Zealot Barbarian Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can channel divine power into your strikes. On each of your turns while your Rage is active, the first creature you hit with a weapon or an Unarmed Strike takes extra damage equal to 1d6 plus half your Barbarian level (round down). The extra damage is Necrotic or Radiant; you choose the type each time you deal the damage."
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        barbarian_level = character_stat_block.get_class_level(
            Definitions.CharacterClass.BARBARIAN
        )
        half_level = barbarian_level // 2
        return [
            ("Trigger", "First hit per turn while Rage active"),
            ("Extra Damage", f"1d6 + {half_level}"),
            ("Damage Type", "Necrotic or Radiant (your choice)"),
            ("Requirement", "Weapon or Unarmed Strike"),
        ]


class WarriorOfTheGods(Feature):
    def __init__(self):
        super().__init__(
            name="Warrior of the Gods", origin="Path Of The Zealot Barbarian Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "A divine entity helps ensure you can continue the fight. You have a pool of four d12s that you can spend to heal yourself. As a Bonus Action, you can expend dice from the pool, roll them, and regain a number of Hit Points equal to the roll’s total.\n"
            "Your pool regains all expended dice when you finish a Long Rest.\n"
            "The pool’s maximum number of dice increases by one when you reach Barbarian levels 6 (5 dice), 12 (6 dice), and 17 (7 dice)."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        barbarian_level = character_stat_block.get_class_level(
            Definitions.CharacterClass.BARBARIAN
        )
        if barbarian_level < 6:
            pool_size = 4
        elif barbarian_level < 12:
            pool_size = 5
        elif barbarian_level < 17:
            pool_size = 6
        else:
            pool_size = 7
        return [
            ("Action", "Bonus Action"),
            ("Pool Size", f"{pool_size} d12s (level {barbarian_level})"),
            ("Effect", "Expend dice, roll, regain HP"),
            ("Recharge", "Long Rest"),
        ]


class FanaticalFocus(Feature):
    def __init__(self):
        super().__init__(
            name="Fanatical Focus", origin="Path Of The Zealot Barbarian Level 6"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Once per active Rage, if you fail a saving throw, you can reroll it with a bonus equal to your Rage Damage bonus, and you must use the new roll."
        return description


class ZealousPresence(Feature):
    def __init__(self):
        super().__init__(
            name="Zealous Presence", origin="Path Of The Zealot Barbarian Level 10"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "As a Bonus Action, you unleash a battle cry infused with divine energy. Up to ten other creatures of your choice within 60 feet of you gain Advantage on attack rolls and saving throws until the start of your next turn.\n"
            "Once you use this feature, you can’t use it again until you finish a Long Rest unless you expend a use of your Rage (no action required) to restore your use of it."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Action", "Bonus Action"),
            ("Range", "60 feet"),
            ("Affected Creatures", "Up to 10 others"),
            ("Effect", "Advantage on attacks and saves"),
            ("Duration", "Until start of next turn"),
            ("Recharge", "Long Rest or expend Rage use"),
        ]


class RageOfTheGods(Feature):
    def __init__(self):
        super().__init__(
            name="Rage of the Gods", origin="Path Of The Zealot Barbarian Level 14"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you activate your Rage, you can assume the form of a divine warrior. This form lasts for 1 minute or until you drop to 0 Hit Points. Once you use this feature, you can’t do so again until you finish a Long Rest.\n"
            "While in this form, you gain the benefits below.\n"
            "Flight. You have a Fly Speed equal to your Speed and can hover.\n"
            "Resistance. You have Resistance to Necrotic, Psychic, and Radiant damage.\n"
            "Revivification. When a creature within 30 feet of you would drop to 0 Hit Points, you can take a Reaction to expend a use of your Rage to instead change the target’s Hit Points to a number equal to your Barbarian level."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        barbarian_level = character_stat_block.get_class_level(
            Definitions.CharacterClass.BARBARIAN
        )
        return [
            ("Activation", "When you activate your Rage"),
            ("Duration", "1 minute (or until you drop to 0 HP)"),
            ("Recharge", "Long Rest"),
            ("Flight", "Fly Speed equal to your Speed, can hover"),
            ("Resistance", "Necrotic, Psychic, and Radiant damage"),
            ("Revivification", f"Reaction within 30 ft, expend Rage use: restore HP to {barbarian_level}"),
        ]
