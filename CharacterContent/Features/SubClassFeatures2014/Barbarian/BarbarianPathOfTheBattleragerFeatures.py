from CharacterContent.Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class BattleragerArmor(Feature):
    def __init__(self):
        super().__init__(name="Battlerager Armor", origin="Path Of The Battlerager Barbarian Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Restriction: Only dwarves can follow the Path of the Battlerager.\n"
            "\n"
            "When you choose this path at 3rd level, you gain the ability to use spiked armor as a weapon.\n"
            "\n"
            "While you are wearing spiked armor and are raging, you can use a bonus action to make one melee weapon attack with your armor spikes against a target within 5 feet of you. If the attack hits, the spikes deal 1d4 piercing damage. You use your Strength modifier for the attack and damage rolls.\n"
            "\n"
            "Additionally, when you use the Attack action to grapple a creature, the target takes 3 piercing damage if your grapple check succeeds."
        )
        return description


class RecklessAbandon(Feature):
    def __init__(self):
        super().__init__(name="Reckless Abandon", origin="Path Of The Battlerager Barbarian Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Beginning at 6th level, when you use Reckless Attack while raging, you also gain temporary hit points equal to your Constitution modifier (minimum of 1). They vanish if any of them are left when your rage ends."
        )
        return description


class BattleragerCharge(Feature):
    def __init__(self):
        super().__init__(name="Battlerager Charge", origin="Path Of The Battlerager Barbarian Level 10")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Beginning at 10th level, you can take the Dash action as a bonus action while you are raging."
        )
        return description


class SpikedRetribution(Feature):
    def __init__(self):
        super().__init__(name="Spiked Retribution", origin="Path Of The Battlerager Barbarian Level 14")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Starting at 14th level, when a creature within 5 feet of you hits you with a melee attack, the attacker takes 3 piercing damage if you are raging, aren't incapacitated, and are wearing spiked armor."
        )
        return description
