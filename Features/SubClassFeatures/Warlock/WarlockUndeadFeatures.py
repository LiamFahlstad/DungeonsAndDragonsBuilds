from Core.Definitions import Ability, WARLOCK_HIT_DIE
from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class FormOfDread(Feature):
    def __init__(self):
        super().__init__(name="Form of Dread", origin="Undead Patron Warlock Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        charisma_modifier = character_stat_block.get_ability_modifier(Ability.CHARISMA)
        uses = max(1, charisma_modifier)
        description = (
            "As a Bonus Action, you transform into an avatar of your patron's dreadful power, gaining the benefits below for 1 minute, until you have the Incapacitated condition, or until you end the form (no action required). You can transform a number of times equal to your Charisma modifier (minimum of once), and you regain all expended uses when you finish a Long Rest.\n"
            "Facsimile of Life. You gain Temporary Hit Points equal to 1d10 plus your Warlock level.\n"
            "Fearless Form. You have Immunity to the Frightened condition. If you are Frightened when you transform, the condition immediately ends for you.\n"
            "Frightful Avatar. Once per turn, when you hit a creature with an attack roll, you can force it to make a Wisdom saving throw against your spell save DC. On a failed save, the target has the Frightened condition until the end of your next turn."
        )
        return StringUtils.add_boxes(description, uses, regain_all_on="long rest")


class UndeadSpells(Feature):
    def __init__(self):
        super().__init__(name="Undead Spells", origin="Undead Patron Warlock Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "The magic of your patron ensures you always have certain spells ready; when you reach a Warlock level specified in the Undead Spells table, you thereafter always have the listed spells prepared.\n"
            "Undead Spells\n"
            "Warlock Level	Spells\n"
            "3	Bane, Blindness/Deafness, Phantasmal Force, Ray of Sickness\n"
            "5	Speak with Dead, Summon Undead\n"
            "7	Greater Invisibility, Phantasmal Killer\n"
            "9	Antilife Shell, Cloudkill"
        )
        return description


class GraveTouched(Feature):
    def __init__(self):
        super().__init__(name="Grave Touched", origin="Undead Patron Warlock Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your patron's powers have a profound effect on your body and magic, granting you the following benefits.\n"
            "Arcane Necrosis. Necrotic damage from your attacks, Warlock spells, and Warlock features ignores Resistance to Necrotic damage. Once per turn when you cast a spell that deals damage, you can change that spell's damage type to Necrotic.\n"
            "Dreaded Necrosis. When you hit a creature with an attack roll and deal Necrotic damage while using your Form of Dread, you can roll one additional damage die when determining the Necrotic damage the target takes. You can use this benefit only once per turn.\n"
            "Undead Endurance. You don't gain Exhaustion levels from dehydration, malnutrition, or suffocation. In addition, you don't need to sleep, and magic can't put you to sleep."
        )
        return description


class NecroticHusk(Feature):
    def __init__(self):
        super().__init__(name="Necrotic Husk", origin="Undead Patron Warlock Level 10")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your connection to undeath saturates your body. You gain the following benefits.\n"
            "Necrotic Resilience. You have Resistance to Necrotic damage. While using your Form of Dread, you have Immunity to Necrotic damage.\n"
            "Unholy Resuscitation. If you drop to 0 Hit Points and don't die outright, you can cause your body to erupt with deathly energy. Each creature of your choice in a 30-foot Emanation originating from you makes a Constitution saving throw against your spell save DC, taking Necrotic damage equal to 2d10 plus your Charisma modifier on a failed save or half as much damage on a successful one. Your Hit Points then change to twice your Warlock level, and you gain 1 Exhaustion level.\n"
            "Once you use this benefit, you can't use it again until you finish a Short or Long Rest."
        )
        return description


class SuperiorDread(Feature):
    def __init__(self):
        super().__init__(name="Superior Dread", origin="Undead Patron Warlock Level 14")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your Form of Dread improves, granting you the following benefits while you are using it.\n"
            "Dread Resistance. You have Resistance to Bludgeoning, Piercing, and Slashing damage.\n"
            "Ghostly Flight. You have a Fly Speed equal to your Speed and can hover. You can move through creatures and objects as if they were Difficult Terrain, but you take 1d10 Force damage if you end your turn inside a creature or an object.\n"
            "Profane Casting. Whenever you cast a Warlock spell from the Conjuration or Necromancy school, you cast it without any Verbal, Somatic, or Material components, except Material components that are costly or consumed."
        )
        return description
