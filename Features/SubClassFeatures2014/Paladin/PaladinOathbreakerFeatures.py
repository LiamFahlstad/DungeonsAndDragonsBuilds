from Core.Definitions import PALADIN_HIT_DIE
from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class OathbreakerSpells(Feature):
    def __init__(self):
        super().__init__(
            name="Oathbreaker Spells", origin="Oathbreaker Paladin Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain oath spells at the Paladin levels listed. When you reach a Paladin level specified in the Oathbreaker Spells table, you thereafter always have the listed spells prepared.\n"
            "Oathbreaker Spells\n"
            "Paladin Level	Spells\n"
            "3	Hellish Rebuke, Inflict Wounds\n"
            "5	Crown of Madness, Darkness\n"
            "9	Animate Dead, Bestow Curse\n"
            "13	Blight, Confusion\n"
            "17	Contagion, Dominate Person"
        )
        return description


class ControlUndead(Feature):
    def __init__(self):
        super().__init__(name="Control Undead", origin="Oathbreaker Paladin Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "As an action, you can expend one use of your Channel Divinity to target one undead creature you can see within 30 feet of you.\n"
            "The target must make a Wisdom saving throw. On a failed save, the target must obey your commands for the next 24 hours, or until you use this Channel Divinity option again. An undead whose challenge rating is equal to or greater than your Paladin level is immune to this effect."
        )
        return description


class DreadfulAspect(Feature):
    def __init__(self):
        super().__init__(name="Dreadful Aspect", origin="Oathbreaker Paladin Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "As an action, you can expend one use of your Channel Divinity to channel the darkest emotions and focus them into a burst of magical menace.\n"
            "Each creature of your choice within 30 feet of you must make a Wisdom saving throw if it can see you. On a failed save, the target is frightened of you for 1 minute. If a creature frightened by this effect ends its turn more than 30 feet away from you, it can attempt another Wisdom saving throw to end the effect on it."
        )
        return description


class AuraOfHate(Feature):
    def __init__(self):
        super().__init__(name="Aura of Hate", origin="Oathbreaker Paladin Level 7")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You, as well as any fiends and undead within 10 feet of you, gain a bonus to melee weapon damage rolls equal to your Charisma modifier (minimum of +1).\n"
            "A creature can benefit from this feature from only one Paladin at a time."
        )
        return description


class AuraOfHateExpansion(Feature):
    def __init__(self):
        super().__init__(
            name="Aura of Hate Expansion", origin="Oathbreaker Paladin Level 18"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "The range of your Aura of Hate increases to 30 feet."
        return description


class SupernaturalResistance(Feature):
    def __init__(self):
        super().__init__(
            name="Supernatural Resistance", origin="Oathbreaker Paladin Level 15"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You gain resistance to bludgeoning, piercing, and slashing damage from nonmagical weapons."
        return description


class DreadLord(Feature):
    def __init__(self):
        super().__init__(name="Dread Lord", origin="Oathbreaker Paladin Level 20")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "As an action, you can surround yourself with an aura of gloom that lasts for 1 minute. The aura reduces any bright light in a 30-foot radius around you to dim light.\n"
            "Whenever an enemy that is frightened by you starts its turn in the aura, it takes 4d10 psychic damage. Additionally, you and any creatures of your choosing in the aura are draped in deeper shadow. Creatures that rely on sight have disadvantage on attack rolls against creatures draped in this shadow.\n"
            "While the aura lasts, you can use a bonus action on your turn to cause the shadows in the aura to attack one creature. Make a melee spell attack against the target. If the attack hits, the target takes necrotic damage equal to 3d10 + your Charisma modifier.\n"
            "After activating the aura, you can't do so again until you finish a long rest."
        )
        return StringUtils.add_boxes(description, 1, regain_all_on="long rest")
