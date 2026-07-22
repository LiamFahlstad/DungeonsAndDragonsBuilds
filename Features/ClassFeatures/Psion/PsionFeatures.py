from Core.Definitions import PSION_HIT_DIE
from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class PsionicPower(Feature):
    def __init__(self):
        super().__init__(name="Psionic Power", origin="Psion Level 1")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You harbor a wellspring of psionic energy within\n"
            "yourself. This energy is represented by your Psionic\n"
            "Energy Dice. Your Psion level determines the die\n"
            "size and number of Psionic Energy Dice you have, as\n"
            "shown in the Energy Dice column of the Psiopn table\n"
            "Your Psionic Energy Dice are used to enhance or\n"
            "fuel certain Psion features. You start with two such\n"
            "features: Telekinetic Propel and Telepathic\n"
            "Connection, each of which is detailed below. Some of\n"
            "your powers expend the Psionic Energy Dice, as\n"
            "specified in a power's description, and you can't use\n"
            "a power if it requires you to use a die when all your\n"
            "Psionic Energy Dice are expended.\n"
            "You regain one expended Psionic Energy Die when\n"
            "you finish a Short Rest, and you regain all of them\n"
            "when you finish a Long Rest.\n"
            "Some features that use Psionic Energy Dice\n"
            "require your target to make a saving throw. The save\n"
            "DC equals the spell save DC from this class's\n"
            "Spellcasting feature.\n"
            "Telekinetic Propel. As a Bonus Action, choose one\n"
            "Large or smaller creature other than you that you\n"
            "can see within 30 feet of yourself. When you do so,\n"
            "the target must succeed on a Strength saving throw\n"
            "or be moved 5 feet straight toward you or straight\n"
            "away from you. Alternatively, you can roll one\n"
            "Psionic Energy Die when you take this Bonus Action,\n"
            "and the distance moved is equal to 5 times the\n"
            "number rolled. The die is expended only if the target\n"
            "fails the saving throw.\n"
            "Telepathic Connection. You have telepathy with a\n"
            "range of 30 feet. As a Bonus Action, you can roll one\n"
            "Psionic Energy Die. For the next hour, the range of\n"
            "your telepathy increases by a number of feet equal\n"
            "to 10 times the number rolled. The first time you use\n"
            "this Bonus Action after each Long Rest, you don't\n"
            "expend the Psionic Energy Die. All other times you\n"
            "use this feature, you expend the die."
        )
        return description


class SubtleTelekinesis(Feature):
    def __init__(self):
        super().__init__(name="Subtle Telekinesis", origin="Psion Level 1")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You know the Mage Hand cantrip. You can cast it\n"
            "without Somatic components, and you can make the\n"
            "spectral hand Invisible when you cast it."
        )
        return description


class PsionicDiscipline(Feature):
    def __init__(self):
        super().__init__(name="Psionic Discipline", origin="Psion Level 2")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You learn further psionic techniques that are fueled\n"
            "by your Psionic Energy Dice. You gain two\n"
            "disciplines of your choice, such as Expanded\n"
            "Awareness and Id Insinuation. Disciplines are\n"
            "described in the “Psionic Discipline Options” section\n"
            "later in this class's description.\n"
            "You can use only one Discipline each turn and only\n"
            "once per turn unless otherwise noted in one of those\n"
            "options.\n"
            "Whenever you gain a Psion level, you can replace\n"
            "one of your Psionic Discipline options with one you\n"
            "don't know. You gain one additional option at Psion\n"
            "levels 5, 10, 13, and 17."
        )
        return description


class PsionicRestoration(Feature):
    def __init__(self):
        super().__init__(name="Psionic Restoration", origin="Psion Level 5")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can perform a meditation that focuses the mind\n"
            "for 1 minute. At the end of it, you regain expended\n"
            "Psionic Energy Dice. Once you use this feature, you\n"
            "can't do so again until you finish a Long Rest."
        )
        return description


class PsionicSurge(Feature):
    def __init__(self):
        super().__init__(name="Psionic Surge", origin="Psion Level 7")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can push your psionic powers using your life\n"
            "force. After you roll one or more Psionic Energy\n"
            "Dice, you can expend one of your Hit Point Dice and\n"
            "treat any roll of 1, 2, or 3 on those Psionic Energy\n"
            "Dice as a 4."
        )
        return description


class PsionicReserves(Feature):
    def __init__(self):
        super().__init__(name="Psionic Reserves", origin="Psion Level 18")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you roll Initiative, you regain expended uses\n"
            "of Psionic Energy Dice until you have four if you\n"
            "have fewer than that."
        )
        return description


class EpicBoon(Feature):
    def __init__(self):
        super().__init__(name="Epic Boon", origin="Psion Level 19")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain an Epic Boon feat or another feat of your\n"
            "choice for which you qualify. Boon of Energy\n"
            "Resistance is recommended."
        )
        return description


class EnkindledLifeForce(Feature):
    def __init__(self):
        super().__init__(name="Enkindled Life Force", origin="Psion Level 20")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You burn your life force to achieve greater psionics.\n"
            "Once per turn, when you roll one or more Psionic\n"
            "Energy Dice for a Psion feature or Psionic Discipline,\n"
            "you can expend one or two of your Hit Point Dice.\n"
            "For each Hit Point Die expended, roll an additional\n"
            "Psionic Energy Die and add the numbers rolled to\n"
            "the total. This roll does not expend the Psionic\n"
            "Energy Die."
        )
        return description
