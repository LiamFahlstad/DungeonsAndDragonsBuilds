from Core.Definitions import PALADIN_HIT_DIE
from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class VengeanceSpells(Feature):
    def __init__(self):
        super().__init__(name="Oath of Vengeance Spells", origin="Oath of Vengeance Paladin Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain oath spells at the Paladin levels listed. When you reach a Paladin level specified in the Oath of Vengeance Spells table, you thereafter always have the listed spells prepared.\n"
            "Oath of Vengeance Spells\n"
            "Paladin Level	Spells\n"
            "3	Bane, Hunter's Mark\n"
            "5	Hold Person, Misty Step\n"
            "9	Haste, Protection from Energy\n"
            "13	Banishment, Dimension Door\n"
            "17	Hold Monster, Scrying"
        )
        return description


class AbjureEnemy(Feature):
    def __init__(self):
        super().__init__(name="Abjure Enemy", origin="Oath of Vengeance Paladin Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "As an action, you present your holy symbol and speak a prayer of denunciation, using your Channel Divinity. Choose one creature within 60 feet of you that you can see. That creature must make a Wisdom saving throw, unless it is immune to being frightened. Fiends and undead have disadvantage on this saving throw.\n"
            "On a failed save, the creature is frightened for 1 minute or until it takes any damage. While frightened, the creature's speed is 0, and it can't benefit from any bonus to its speed.\n"
            "On a successful save, the creature's speed is halved for 1 minute or until the creature takes any damage."
        )
        return description


class VowOfEnmity(Feature):
    def __init__(self):
        super().__init__(name="Vow of Enmity", origin="Oath of Vengeance Paladin Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "As a bonus action, you can utter a vow of enmity against a creature you can see within 10 feet of you, using your Channel Divinity. You gain advantage on attack rolls against the creature for 1 minute or until it drops to 0 hit points or falls unconscious."
        )
        return description


class RelentlessAvenger(Feature):
    def __init__(self):
        super().__init__(name="Relentless Avenger", origin="Oath of Vengeance Paladin Level 7")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your supernatural focus helps you close off a foe's retreat. When you hit a creature with an opportunity attack, you can move up to half your speed immediately after the attack and as part of the same reaction. This movement doesn't provoke opportunity attacks."
        )
        return description


class SoulOfVengeance(Feature):
    def __init__(self):
        super().__init__(name="Soul of Vengeance", origin="Oath of Vengeance Paladin Level 15")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "The authority with which you speak your Vow of Enmity gives you greater power over your foe. When a creature under the effect of your Vow of Enmity makes an attack, you can use your reaction to make a melee weapon attack against that creature if it is within range."
        )
        return description


class AvengingAngel(Feature):
    def __init__(self):
        super().__init__(name="Avenging Angel", origin="Oath of Vengeance Paladin Level 20")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Using your action, you undergo a transformation. For 1 hour, you gain the following benefits:\n"
            "    * Wings sprout from your back and grant you a flying speed of 60 feet.\n"
            "    * You emanate an aura of menace in a 30-foot radius. The first time any enemy creature enters the aura or starts its turn there during a battle, the creature must succeed on a Wisdom saving throw or become frightened of you for 1 minute or until it takes any damage. Attack rolls against the frightened creature have advantage.\n"
            "Once you use this feature, you can't use it again until you finish a long rest."
        )
        return StringUtils.add_boxes(description, 1, regain_all_on="long rest")
