from Core.Definitions import PSION_HIT_DIE, Ability
from CharacterContent.Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class MindInfiltrator(Feature):
    def __init__(self):
        super().__init__(name="Mind Infiltrator", origin="Telepath Psion Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you cast Detect Thoughts, you can expend one\n"
            "Psionic Energy Die to modify the spell so that the\n"
            "spell doesn't require spell components or\n"
            "Concentration. In addition, when you use the Read\n"
            "Thoughts effect of the spell, the target doesn't know\n"
            "you're probing its mind if it fails the Wisdom saving\n"
            "throw."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Spell", "Detect Thoughts"),
            ("Cost", "1 Psionic Energy Die"),
            ("No Components", "Spell components waived"),
            ("No Concentration", "Spell doesn't require Concentration"),
            ("Stealth on Read Thoughts", "Target doesn't know you're probing (if fails save)"),
        ]


class TelepathicDistraction(Feature):
    def __init__(self):
        super().__init__(name="Telepathic Distraction", origin="Telepath Psion Level 3", action_type="reaction")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When a creature you can see within range of your\n"
            "telepathy hits with an attack roll, you can take a\n"
            "Reaction to roll one Psionic Energy Die and subtract\n"
            "the number rolled from attack roll, potentially\n"
            "causing the attack to miss. The die is expended only\n"
            "if the target misses the attack."
        )
        return description


class BulwarkMind(Feature):
    def __init__(self):
        super().__init__(name="Bulwark Mind", origin="Telepath Psion Level 6", duration="10 Minutes")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "At the start of your turn, you can expend one Psionic\n"
            "Energy Die to strengthen your mind and enter a\n"
            "fortified state. For the next 10 minutes, you have\n"
            "Resistance to Psychic damage; and whenever you\n"
            "make an Intelligence, Wisdom, or Charisma saving\n"
            "throw, you add a roll of your Psionic Energy Die to\n"
            "the save. Rolling the Psionic Energy Die doesn't\n"
            "expend it. You can't use this benefit if you have the\n"
            "Incapacitated condition."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Activation", "Start of turn"),
            ("Cost", "1 Psionic Energy Die"),
            ("Duration", "10 minutes"),
            ("Damage Resistance", "Psychic damage"),
            ("Saving Throw Bonus", "Add die roll to INT/WIS/CHA saves (die doesn't expend)"),
            ("Restriction", "Not while Incapacitated"),
        ]


class PotentThoughts(Feature):
    def __init__(self):
        super().__init__(name="Potent Thoughts", origin="Telepath Psion Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You have telepathy with a range of 60 feet. In\n"
            "addition, you add your Intelligence modifier to the\n"
            "damage you deal with any Psion cantrip."
        )
        return description


class TelepathicBolstering(Feature):
    def __init__(self):
        super().__init__(name="Telepathic Bolstering", origin="Telepath Psion Level 10", action_type="reaction")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you or a creature you can see within range of\n"
            "your telepathy fails an ability check or misses with\n"
            "an attack roll, you can take a Reaction to expend one\n"
            "Psionic Energy Die. Roll the die and add the number\n"
            "rolled to the d20, potentially turning a failed check\n"
            "into a success or a miss into a hit. The Psionic\n"
            "Energy Die is expended only if the check succeeds or\n"
            "the attack hits."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Trigger", "You or ally within telepathy range fails check or misses attack"),
            ("Action", "Reaction"),
            ("Effect", "Roll Psionic Energy Die and add to d20 roll"),
            ("Cost", "1 Psionic Energy Die (expended only if success)"),
        ]


class ScrambleMinds(Feature):
    def __init__(self):
        super().__init__(name="Scramble Minds", origin="Telepath Psion Level 14", range="30-Foot Radius")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can cast Confusion without expending a spell\n"
            "slot by instead expending four Psionic Energy Dice.\n"
            "When you cast Confusion without a spell slot using\n"
            "this feature, you can modify the spell so that the\n"
            "radius of the spell's Sphere becomes 30 feet and you\n"
            "can choose one creature you can see in the spell's\n"
            "area to automatically succeed on their saving throw\n"
            "against the spell.\n"
            "In addition, when a creature under the effect of\n"
            "the spell starts its turn, you choose their behavior\n"
            "from the table for the turn instead of the creature\n"
            "rolling to determine its behavior."
        )
        return description

    def get_concise_description(
        self, character_stat_block: CharacterStatBlock
    ) -> str:
        return (
            "Cast Confusion without slot by expending 4 Psionic Energy Dice. Spell's radius becomes 30 feet, "
            "choose one creature to auto-succeed on save, and you pick each creature's confused behavior each turn "
            "(instead of rolling)."
        )
