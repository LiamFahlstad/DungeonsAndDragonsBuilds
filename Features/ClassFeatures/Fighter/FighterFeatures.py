from Definitions import FIGHTER_HIT_DIE
from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class FightingStyle(Feature):
    def __init__(self):
        super().__init__(name="Fighting Style", origin="Fighter Level 1")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain a Fighting Style feat of your choice (see chapter 5). Defense is recommended.\n"
            "Whenever you gain a Fighter level, you can replace the feat you chose with a different Fighting Style feat."
        )
        return description


class SecondWind(Feature):
    def __init__(self):
        super().__init__(name="Second Wind", origin="Fighter Level 1")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        uses = 2
        if character_stat_block.character_level >= 4:
            uses = 3
        if character_stat_block.character_level >= 10:
            uses = 4

        base_text = (
            f"You have a limited well of physical and mental stamina that you can draw on. "
            f"As a Bonus Action, you can use it to regain Hit Points equal to 1d10 plus your Fighter level.\n"
            f"You can use this feature {uses} time(s). You regain one expended use when you finish a Short Rest, "
            f"and you regain all expended uses when you finish a Long Rest.\n"
        )

        return StringUtils.add_boxes(
            base_text, uses, regain_x_on=(1, "short rest"), regain_all_on="long rest"
        )


class WeaponMastery(Feature):
    def __init__(self):
        super().__init__(name="Weapon Mastery", origin="Fighter Level 1")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your training with weapons allows you to use the mastery properties of three kinds of Simple or Martial weapons of your choice. Whenever you finish a Long Rest, you can practice weapon drills and change one of those weapon choices.\n"
            "When you reach certain Fighter levels, you gain the ability to use the mastery properties of more kinds of weapons, as shown in the Weapon Mastery column of the Fighter Features table."
        )
        return description


class ActionSurge(Feature):
    def __init__(self):
        super().__init__(name="Action Surge", origin="Fighter Level 2")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        uses = 2 if character_stat_block.character_level >= 17 else 1
        description = (
            "You can push yourself beyond your normal limits for a moment. On your turn, you can take one additional action, except the Magic action.\n"
            "Once you use this feature, you can’t do so again until you finish a Short or Long Rest. Starting at level 17, you can use it twice before a rest but only once on a turn."
        )
        return StringUtils.add_boxes(
            description, uses, regain_all_on="short or long rest"
        )


class TacticalMind(Feature):
    def __init__(self):
        super().__init__(name="Tactical Mind", origin="Fighter Level 2")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You have a mind for tactics on and off the battlefield. When you fail an ability check, you can expend a use of your Second Wind to push yourself toward success. Rather than regaining Hit Points, you roll 1d10 and add the number rolled to the ability check, potentially turning it into a success. If the check still fails, this use of Second Wind isn’t expended."
        return description


class ExtraAttack(Feature):
    def __init__(self):
        super().__init__(name="Extra Attack", origin="Fighter Level 5")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can attack twice instead of once whenever you take the Attack action on your turn."
        return description


class TacticalShift(Feature):
    def __init__(self):
        super().__init__(name="Tactical Shift", origin="Fighter Level 5")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Whenever you activate your Second Wind with a Bonus Action, you can move up to half your Speed without provoking Opportunity Attacks."
        return description


class Indomitable(Feature):
    def __init__(self):
        super().__init__(name="Indomitable", origin="Fighter Level 9")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        if character_stat_block.character_level >= 17:
            uses = 3
        elif character_stat_block.character_level >= 13:
            uses = 2
        else:
            uses = 1
        description = (
            "If you fail a saving throw, you can reroll it with a bonus equal to your Fighter level. You must use the new roll, and you can’t use this feature again until you finish a Long Rest.\n"
            "You can use this feature twice before a Long Rest starting at level 13 and three times before a Long Rest starting at level 17."
        )
        return StringUtils.add_boxes(description, uses, regain_all_on="long rest")


class TacticalMaster(Feature):
    def __init__(self):
        super().__init__(name="Tactical Master", origin="Fighter Level 9")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you attack with a weapon whose mastery property you can use, you can replace that property with the Push, Sap, or Slow property for that attack."
        return description


class TwoExtraAttacks(Feature):
    def __init__(self):
        super().__init__(name="Two Extra Attacks", origin="Fighter Level 11")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can attack three times instead of once whenever you take the Attack action on your turn."
        return description


class StudiedAttacks(Feature):
    def __init__(self):
        super().__init__(name="Studied Attacks", origin="Fighter Level 13")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You study your opponents and learn from each attack you make. If you make an attack roll against a creature and miss, you have Advantage on your next attack roll against that creature before the end of your next turn."
        return description


class EpicBoon(Feature):
    def __init__(self):
        super().__init__(name="Epic Boon", origin="Fighter Level 19")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You gain an Epic Boon feat or another feat of your choice for which you qualify. Boon of Combat Prowess is recommended."
        return description


class ThreeExtraAttacks(Feature):
    def __init__(self):
        super().__init__(name="Three Extra Attacks", origin="Fighter Level 20")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can attack four times instead of once whenever you take the Attack action on your turn."
        return description
