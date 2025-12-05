from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Definitions import Ability, DiceRollCondition, Skill
from Features import Weapons, Maneuvers
from Features.BaseFeatures import CharacterFeature, TextFeature


FIGHTER_HIT_DIE = 10


class SecondWind(TextFeature):
    def __init__(self):
        super().__init__(name="Second Wind", origin="Fighter Level 1")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        uses = 2
        if character_stat_block.level >= 4:
            uses = 3
        if character_stat_block.level >= 10:
            uses = 3

        base_text = (
            f"You have a limited well of physical and mental stamina that you can draw on. "
            f"As a Bonus Action, you can use it to regain Hit Points equal to 1d10 plus your Fighter level.\n"
            f"You can use this feature {uses} time(s). You regain one expended use when you finish a Short Rest, "
            f"and you regain all expended uses when you finish a Long Rest.\n"
        )
        if character_stat_block.level >= 2:
            base_text += self.add_feature_effects(character_stat_block, TacticalMind())

        if character_stat_block.level >= 5:
            base_text += self.add_feature_effects(character_stat_block, TacticalShift())

        return base_text


class ActionSurge(TextFeature):
    def __init__(self):
        super().__init__(name="Action Surge", origin="Fighter Level 2")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "Level 2: You can take one additional action on your turn.\n"
            "You must finish a short or long rest to use this feature again.\n"
        )


class TacticalMind(TextFeature):
    def __init__(self):
        super().__init__(name="Tactical Mind", origin="Fighter Level 2")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "When you fail an ability check, you can use Second Wind to roll 1d10 and add it to the check.\n"
            "If the check still fails, the Second Wind use isn't expended.\n"
        )


class SuperiorityDice(TextFeature):
    def __init__(self):
        self.maneuvers = []
        super().__init__(name="Superiority Dice", origin="Fighter Battle Master")

    def add_maneuver(self, maneuver: Maneuvers.Maneuver):
        self.maneuvers.append(maneuver)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        if character_stat_block.level < 7:
            number_of_superiority_die = 4
        elif character_stat_block.level < 15:
            number_of_superiority_die = 5
        else:
            number_of_superiority_die = 6

        if character_stat_block.level < 10:
            superiority_die = "1d8"
        elif character_stat_block.level < 18:
            superiority_die = "1d10"
        else:
            superiority_die = "1d12"

        base_text = (
            f"These are {superiority_die}s, and you can expend them to fuel your maneuvers.\n"
            "You regain all expended superiority dice when you finish a short or long rest.\n"
            f"Number of Superiority Dice: {number_of_superiority_die}\n"
        )

        for maneuver in self.maneuvers:
            base_text += self.add_feature_effects(character_stat_block, maneuver)

        return base_text


class ExtraAttack(TextFeature):
    def __init__(self):
        super().__init__(name="Extra Attack", origin="Fighter Level 5")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "You can attack twice, instead of once, whenever you take the Attack action on your turn.\n"


class TacticalShift(TextFeature):
    def __init__(self):
        super().__init__(name="Tactical Shift", origin="Fighter Level 5")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "Whenever you activate your Second Wind with a Bonus Action, you can move up to half your Speed without provoking Opportunity Attacks.\n"
