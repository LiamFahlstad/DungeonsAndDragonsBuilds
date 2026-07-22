from Core.Definitions import WIZARD_HIT_DIE
from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class NecromancySavant(Feature):
    def __init__(self):
        super().__init__(name="Necromancy Savant", origin="Necromancy Wizard Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "The gold and time you must spend to copy a Necromancy spell into your spellbook is halved."
        return description


class GrimHarvest(Feature):
    def __init__(self):
        super().__init__(name="Grim Harvest", origin="Necromancy Wizard Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain the ability to reap life energy from creatures you kill with your spells. Once per turn when you kill one or more creatures with a spell of 1st level or higher, you regain hit points equal to twice the spell's level, or three times its level if the spell belongs to the School of Necromancy.\n"
            "You don't gain this benefit for killing constructs or undead."
        )
        return description


class UndeadThralls(Feature):
    def __init__(self):
        super().__init__(name="Undead Thralls", origin="Necromancy Wizard Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You add the Animate Dead spell to your spellbook if it is not there already. When you cast Animate Dead, you can target one additional corpse or pile of bones, creating another zombie or skeleton, as appropriate.\n"
            "Whenever you create an undead using a necromancy spell, it has additional benefits:\n"
            "    * The creature's hit point maximum is increased by an amount equal to your wizard level.\n"
            "    * The creature adds your proficiency bonus to its weapon damage rolls."
        )
        return description


class InuredToUndeath(Feature):
    def __init__(self):
        super().__init__(
            name="Inured to Undeath", origin="Necromancy Wizard Level 10"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You have resistance to necrotic damage, and your hit point maximum can't be reduced. You have spent so much time dealing with undead and the forces that animate them that you have become inured to some of their worst effects."
        return description


class CommandUndead(Feature):
    def __init__(self):
        super().__init__(name="Command Undead", origin="Necromancy Wizard Level 14")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can use magic to bring undead under your control, even those created by other wizards. As an action, you can choose one undead that you can see within 60 feet of you. That creature must make a Charisma saving throw against your wizard spell save DC. If it succeeds, you can't use this feature on it again. If it fails, it becomes friendly to you and obeys your commands until you use this feature again.\n"
            "Intelligent undead are harder to control in this way. If the target has an Intelligence of 8 or higher, it has advantage on the saving throw. If it fails the saving throw and has an Intelligence of 12 or higher, it can repeat the saving throw at the end of every hour until it succeeds and breaks free."
        )
        return description
