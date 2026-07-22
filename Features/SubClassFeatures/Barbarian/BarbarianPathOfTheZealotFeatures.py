from Core.Definitions import BARBARIAN_HIT_DIE
from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class DivineFury(Feature):
    def __init__(self):
        super().__init__(
            name="Divine Fury", origin="Path Of The Zealot Barbarian Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can channel divine power into your strikes. On each of your turns while your Rage is active, the first creature you hit with a weapon or an Unarmed Strike takes extra damage equal to 1d6 plus half your Barbarian level (round down). The extra damage is Necrotic or Radiant; you choose the type each time you deal the damage."
        return description


class WarriorOfTheGods(Feature):
    def __init__(self):
        super().__init__(
            name="Warrior of the Gods", origin="Path Of The Zealot Barbarian Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "A divine entity helps ensure you can continue the fight. You have a pool of four d12s that you can spend to heal yourself. As a Bonus Action, you can expend dice from the pool, roll them, and regain a number of Hit Points equal to the roll’s total.\n"
            "Your pool regains all expended dice when you finish a Long Rest.\n"
            "The pool's maximum number of dice increases by one when you reach Barbarian levels 6 (5 dice), 12 (6 dice), and 17 (7 dice)."
        )
        return description


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


class RageOfTheGods(Feature):
    def __init__(self):
        super().__init__(
            name="Rage of the Gods", origin="Path Of The Zealot Barbarian Level 14"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you activate your Rage, you can assume the form of a divine warrior. This form lasts for 1 minute or until you drop to 0 Hit Points. Once you use this feature, you can't do so again until you finish a Long Rest.\n"
            "While in this form, you gain the benefits below.\n"
            "Flight. You have a Fly Speed equal to your Speed and can hover.\n"
            "Resistance. You have Resistance to Necrotic, Psychic, and Radiant damage.\n"
            "Revivification. When a creature within 30 feet of you would drop to 0 Hit Points, you can take a Reaction to expend a use of your Rage to instead change the target’s Hit Points to a number equal to your Barbarian level."
        )
        return description
