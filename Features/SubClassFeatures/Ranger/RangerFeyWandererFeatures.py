
from Definitions import Ability, RANGER_HIT_DIE
from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class DreadfulStrikes(Feature):
    def __init__(self):
        super().__init__(name="Dreadful Strikes", origin="Fey Wanderer Ranger Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can augment your weapon strikes with mind-scarring magic drawn from the murky hollows of the Feywild. When you hit a creature with a weapon, you can deal an extra 1d4 Psychic damage to the target, which can take this extra damage only once per turn. The extra damage increases to 1d6 when you reach Ranger level 11."
        return description


class FeyWandererSpells(Feature):
    def __init__(self):
        super().__init__(
            name="Fey Wanderer Spells", origin="Fey Wanderer Ranger Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you reach a Ranger level specified in the Fey Wanderer spells table, you thereafter always have the listed spells prepared.\n"
            "Fey Wanderer Spells\n"
            "Ranger Level	Spell\n"
            "3	Charm Person\n"
            "5	Misty Step\n"
            "9	Summon Fey\n"
            "13	Dimension Door\n"
            "17	Mislead\n"
            "You also possess a fey blessing. Choose it from the Feywild Gifts table or determine it randomly:\n"
            "1d6	Gift\n"
            "1	Illusory butterflies flutter around you while you take a Short or Long Rest.\n"
            "2	Flowers bloom from your hair each dawn.\n"
            "3	You faintly smell of cinnamon, lavender, nutmeg, or another comforting herb or spice.\n"
            "4	Your shadow dances while no one is looking directly at it.\n"
            "5	Horns or antlers sprout from your head.\n"
            "6	Your skin and hair change color each dawn."
        )
        return description


class OtherworldlyGlamour(Feature):
    def __init__(self):
        super().__init__(
            name="Otherworldly Glamour", origin="Fey Wanderer Ranger Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Whenever you make a Charisma check, you gain a bonus to the check equal to your Wisdom modifier (Minimum of +1).\n"
            "You also gain proficiency in one of these skills of your choice: Deception, Performance, or Persuasion."
        )
        return description


class BeguilingTwist(Feature):
    def __init__(self):
        super().__init__(name="Beguiling Twist", origin="Fey Wanderer Ranger Level 7")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "The magic of the Feywild guards your mind. You have advantage on saving throws to avoid or end the Charmed or Frightened condition.\n"
            "In addition, whenever you or a creature you can see within 120 feet of you succeeds on a saving throw to avoid or end the Charmed or Frightened condition, you can take a Reaction to force a different creature you can see within 120 feet of yourself to make a Wisdom save against your spell save DC. On a failed save, the target is charmed or frightened (your choice) for 1 minute. The target repeats the save at the end of each of its turns, ending the effect on itself on a success."
        )
        return description


class FeyReinforcements(Feature):
    def __init__(self):
        super().__init__(
            name="Fey Reinforcements", origin="Fey Wanderer Ranger Level 11"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can cast Summon Fey without a Material component. You can also cast it once without a spell slot, and you regain the ability to cast it in this way when you finish a Long Rest.\n"
            "Whenever you start casting the spell, you can modify it so that it doesn't require Concentration. If you do so, the spell's duration becomes 1 minute for the casting."
        )
        return description


class MistyWanderer(Feature):
    def __init__(self):
        super().__init__(name="Misty Wanderer", origin="Fey Wanderer Ranger Level 15")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        wis_mod = character_stat_block.get_ability_modifier(Ability.WISDOM)
        uses = max(1, wis_mod)
        description = (
            "You can cast Misty Step without expending a spell slot. You can do so a number of times equal to your Wisdom modifier (minimum of once), and you regain all expended uses when you finish a Long Rest.\n"
            "In addition, whenever you cast Misty Step, you can bring along one willing creature you can see within 5 feet of yourself. That creature teleports to an unoccupied space of your choice within 5 feet of your destination space."
        )
        return StringUtils.add_boxes(description, uses, regain_all_on="long rest")
