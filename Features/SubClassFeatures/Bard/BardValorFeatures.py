from Core.Definitions import BARD_HIT_DIE
from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class CombatInspiration(Feature):
    def __init__(self):
        super().__init__(
            name="Combat Inspiration", origin="College of Valor Bard Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can use your wit to turn the tide of battle. A creature that has a Bardic Inspiration die from you can use it for one of the following effects.\n"
            "Defense. When the creature is hit by an attack roll, that creature can use its Reaction to roll the Bardic Inspiration die and add the number rolled to its AC against that attack, potentially causing the attack to miss.\n"
            "Offense. Immediately after the creature hits a target with an attack roll, the creature can roll the Bardic Inspiration die and add the number rolled to the attack's damage against the target."
        )
        return description


class MartialTraining(Feature):
    def __init__(self):
        super().__init__(
            name="Martial Training", origin="College of Valor Bard Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain proficiency with Martial weapons and training with Medium armor and Shields.\n"
            "In addition, you can use a Simple or Martial weapon as a Spellcasting Focus to cast spells from your Bard spell list."
        )
        return description


class ExtraAttack(Feature):
    def __init__(self):
        super().__init__(name="Extra Attack", origin="College of Valor Bard Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can attack twice instead of once whenever you take the Attack action on your turn.\n"
            "In addition, you can cast one of your cantrips that has a casting time of an action in place of one of those attacks."
        )
        return description


class BattleMagic(Feature):
    def __init__(self):
        super().__init__(name="Battle Magic", origin="College of Valor Bard Level 14")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "After you cast a spell that has a casting time of an action, you can make one attack with a weapon as a Bonus Action."
        return description
