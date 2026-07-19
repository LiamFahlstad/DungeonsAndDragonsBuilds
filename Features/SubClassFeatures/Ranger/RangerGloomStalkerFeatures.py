
from Definitions import Ability, RANGER_HIT_DIE
from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class DreadAmbusher(Feature):
    def __init__(self):
        super().__init__(name="Dread Ambusher", origin="Gloom Stalker Ranger Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        wis_mod = character_stat_block.get_ability_modifier(Ability.WISDOM)
        uses = max(1, wis_mod)
        description = (
            "You have mastered the art of creating fearsome ambushes, granting you the following benefits.\n"
            "Ambusher's Leap. At the start of your first turn of each combat, your speed increases by 10 feet until the end of that turn.\n"
            f"Dreadful Strike. When you attack a creature and hit it with a weapon, you can deal an extra 2d6 Psychic damage. You can use this benefit only once per turn, you can use it a number of times equal to your Wisdom modifier (minimum of once) ({uses}), and you regain all expended uses when you finish a Long Rest.\n"
            "Initiative Bonus. When you roll Initiative, you can add your Wisdom modifier to the roll."
        )
        return StringUtils.add_boxes(description, uses, regain_all_on="long rest")


class GloomStalkerSpells(Feature):
    def __init__(self):
        super().__init__(
            name="Gloom Stalker Spells", origin="Gloom Stalker Ranger Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you reach a Ranger level specified in the Gloom Stalker spells table, you thereafter always have the listed spells prepared."
        return description


class UmbralSight(Feature):
    def __init__(self):
        super().__init__(name="Umbral Sight", origin="Gloom Stalker Ranger Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain Darkvision with a range of 60 feet. If you already have Darkvision when you gain this feature, its range increases by 60 feet.\n"
            "You are also adept at evading creatures that rely on Darkvision. While entirely in Darkness, you have the Invisible condition to any creature that relies on Darkvision to see you in that Darkness."
        )
        return description


class IronMind(Feature):
    def __init__(self):
        super().__init__(name="Iron Mind", origin="Gloom Stalker Ranger Level 7")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You have honed your ability to resist mind-altering powers. You gain proficiency in Wisdom saving throws. If you already have this proficiency, you instead gain proficiency in Intelligence or Charisma saving throws (your choice)."
        return description


class StalkersFlurry(Feature):
    def __init__(self):
        super().__init__(
            name="Stalker's Flurry", origin="Gloom Stalker Ranger Level 11"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "The Psychic damage of your Dreadful Strike becomes 2d8. In addition, when you use the Dreadful Strike effect of your Dread Ambusher feature, you can use one of the following additional effects.\n"
            "Sudden Strike. You can make another attack with the same weapon against a different creature that is within 5 feet of the original target and that is within the weapon's range.\n"
            "Mass Fear. The target and each creature within 10 feet of it must make a wisdom saving throw against your spell save DC. On a failed save, a creature has the Frightened condition until the start of your next turn."
        )
        return description


class ShadowyDodge(Feature):
    def __init__(self):
        super().__init__(name="Shadowy Dodge", origin="Gloom Stalker Ranger Level 15")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When a creature makes an attack roll against you, you can take a Reaction to impose Disadvantage on that roll. Whether the attack hits or misses, you can teleport up to 30 feet to an unoccupied space that you can see."
        return description
