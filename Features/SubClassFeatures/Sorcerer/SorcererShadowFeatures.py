from Core.Definitions import SORCERER_HIT_DIE
from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class ShadowSpells(Feature):
    def __init__(self):
        super().__init__(name="Shadow Spells", origin="Shadow Sorcerer Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you reach a Sorcerer level specified in the Shadow Spells table, you thereafter always have the listed spells prepared.\n"
            "Shadow Spells\n"
            "Sorcerer Level	Spells\n"
            "3	Bane, Darkness, Inflict Wounds, Pass Without Trace\n"
            "5	Hunger of Hadar, Nondetection\n"
            "7	Greater Invisibility, Phantasmal Killer\n"
            "9	Contagion, Creation"
        )
        return description


class PowerOfShadow(Feature):
    def __init__(self):
        super().__init__(name="Power of Shadow", origin="Shadow Sorcerer Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain the following benefits.\n"
            "Eyes of the Dark. You have Darkvision with a range of 120 feet and Blindsight with a range of 10 feet. In addition, if a spell you cast creates an area of Darkness, you can see normally through that spell’s Darkness.\n"
            "Strength of the Grave. If you would drop to 0 Hit Points and not die outright, you can make a Charisma saving throw (DC 5 plus the damage taken). On a successful save, your Hit Points instead change to a number equal to your Charisma modifier plus your Sorcerer level. After you succeed on this save, you can’t use this benefit again until you finish a Long Rest."
        )
        return description


class BeastsOfIllOmen(Feature):
    def __init__(self):
        super().__init__(name="Beasts of Ill Omen", origin="Shadow Sorcerer Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can call forth a howling creature of shadow to hound your foes. You can spend 3 Sorcery Points to cast Summon Beast as a Bonus Action without expending a spell slot, without preparing the spell, and without Material components. The summoned creature appears as a beast made of shadow, and enemies within 5 feet of the summoned creature have Disadvantage on saving throws against spells you cast.\n"
            "Whenever you cast the spell, you can modify it so that it doesn’t require Concentration. If you do so, the spell’s duration becomes 1 minute for that casting, and the spell ends early if you cast the spell again."
        )
        return description


class ShadowWalk(Feature):
    def __init__(self):
        super().__init__(name="Shadow Walk", origin="Shadow Sorcerer Level 14")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "While you are in Dim Light or Darkness, you can take a Bonus Action to teleport up to 120 feet to an unoccupied space you can see that is also in Dim Light or Darkness."
        return description


class UmbralForm(Feature):
    def __init__(self):
        super().__init__(name="Umbral Form", origin="Shadow Sorcerer Level 18")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you use Innate Sorcery, you can adopt a shadowy form, gaining the benefits below while your Innate Sorcery is active or until you end the form (no action required). Once you use this feature, you can’t use it again until you finish a Long Rest unless you spend 6 Sorcery Points (no action required) to restore your use of it.\n"
            "Incorporeal Movement. You can move through creatures and objects as if they were Difficult Terrain, but you take 1d10 Force damage if you end your turn inside a creature or an object.\n"
            "Shadow Resilience. You have Resistance to all damage except Force and Radiant damage."
        )
        return description
