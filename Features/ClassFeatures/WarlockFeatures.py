from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Definitions import Ability, DiceRollCondition, Skill
from Features.BaseFeatures import CharacterFeature, TextFeature


WARLOCK_HIT_DIE = 8


class MagicalCunning(TextFeature):
    def __init__(self):
        super().__init__(name="Magical Cunning", origin="Warlock Level 2")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "You can perform an esoteric rite for 1 minute.\n"
            "At the end of it, you regain expended Pact Magic spell slots but no more than a number equal to half your maximum (round up).\n"
            "Once you use this feature, you can't do so again until you finish a Long Rest.\n"
        )


class StepsOfTheFey(TextFeature):
    def __init__(self):
        super().__init__(name="Steps of the Fey", origin="Warlock Archfey Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        charisma_mod = character_stat_block.get_ability_modifier(Ability.CHARISMA)
        return (
            f"You can cast Misty Step without expending a spell slot."
            f"Uses: {max(1, charisma_mod)}\n (Charisma Modifier)\n"
            "Regain: All on Long Rest.\n"
            " * Refreshing Step: Immediately after you teleport, you or one creature you can see within 10 feet of yourself gains 1d10 Temporary Hit Points.\n\n"
            " * Taunting Step: Creatures within 5 feet of the space you left must succeed on a Wisdom saving throw against your spell save DC or have Disadvantage on attack rolls against creatures other than you until the start of your next turn.\n"
        )


class SpellSlots(CharacterFeature):

    def modify(self, character_stat_block: CharacterStatBlock):

        spell_slot_level = 0
        num_spell_slots = 0

        if character_stat_block.level >= 1:
            spell_slot_level = 1
            num_spell_slots = 1

        if character_stat_block.level >= 2:
            num_spell_slots = 2

        if character_stat_block.level >= 3:
            spell_slot_level = 2

        if character_stat_block.level >= 5:
            spell_slot_level = 3

        if character_stat_block.level >= 7:
            spell_slot_level = 4

        if character_stat_block.level >= 9:
            spell_slot_level = 5

        if character_stat_block.level >= 11:
            num_spell_slots = 3

        if character_stat_block.level >= 17:
            num_spell_slots = 4

        character_stat_block.spell_slots = {
            spell_slot_level: num_spell_slots,
        }
