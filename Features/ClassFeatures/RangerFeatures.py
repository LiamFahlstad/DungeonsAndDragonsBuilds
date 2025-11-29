from CharacterStatBlock import CharacterStatBlock
from Definitions import Ability, DiceRollCondition, Skill
from Features import Weapons, Maneuvers
from Features.BaseFeatures import CharacterFeature, TextFeature


RANGER_HIT_DIE = 10


class SpellSlots(CharacterFeature):

    def modify(self, character_stat_block: CharacterStatBlock):

        level_1_spell_slots = 0
        level_2_spell_slots = 0
        level_3_spell_slots = 0
        level_4_spell_slots = 0
        level_5_spell_slots = 0

        if character_stat_block.level >= 1:
            level_1_spell_slots = 2

        if character_stat_block.level >= 3:
            level_1_spell_slots = 3

        if character_stat_block.level >= 5:
            level_1_spell_slots = 4
            level_2_spell_slots = 2

        if character_stat_block.level >= 7:
            level_2_spell_slots = 3

        if character_stat_block.level >= 9:
            level_3_spell_slots = 2

        if character_stat_block.level >= 11:
            level_3_spell_slots = 3

        if character_stat_block.level >= 13:
            level_4_spell_slots = 1

        if character_stat_block.level >= 15:
            level_4_spell_slots = 2

        if character_stat_block.level >= 17:
            level_4_spell_slots = 3
            level_5_spell_slots = 1

        if character_stat_block.level >= 19:
            level_5_spell_slots = 2

        character_stat_block.spell_slots = {
            1: level_1_spell_slots,
            2: level_2_spell_slots,
            3: level_3_spell_slots,
            4: level_4_spell_slots,
            5: level_5_spell_slots,
        }


class FavoredEnemy(TextFeature):
    def __init__(self):
        super().__init__(name="Favored Enemy", origin="Ranger Level 1")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        free_hunters_mark = 0
        if character_stat_block.level >= 1:
            free_hunters_mark = 2
        if character_stat_block.level >= 3:
            free_hunters_mark = 3
        if character_stat_block.level >= 5:
            free_hunters_mark = 4
        return (
            f"You always have the Hunter's Mark spell prepared.\n"
            f"You can cast {free_hunters_mark} times without expending a spell slot,\n"
            "and you regain all expended uses of this ability when you finish a Long Rest."
        )


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

    def add_maneuver(self, maneuver: Maneuvers):
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
