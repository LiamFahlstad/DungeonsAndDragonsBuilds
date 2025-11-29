from Character import Character
from Definitions import Ability, DiceRollCondition, Skill
from Features.BaseFeatures import CharacterFeature, TextFeature


PALADIN_HIT_DIE = 10


class ChannelDivinityFeature(TextFeature):
    """Paladin Level 3: Channel Divinity"""

    def __init__(self):
        self.spells = []
        super().__init__(name="Channel Divinity", origin="Paladin Level 3")

    @property
    def indent(self):
        return "    "

    def add_spell(self, spell: str):
        self.spells.append(spell)

    def get_divine_sense_description(self, character_stat_block: Character):
        indent = self.indent
        return (
            f"{indent}Divine Sense:\n"
            f"{indent}Unlocked: Paladin level 3:\n"
            f"{indent}Range: 60 ft radius;\n"
            f"{indent}Casting Time: Bonus Action;\n"
            f"{indent}Duration: 10 minutes.\n"
            f"{indent}Detects Celestials, Fiends, and Undead (location and creature type), and senses consecrated/desecrated places/objects within range.\n"
        )

    def get_vow_of_enmity_description(self, character_stat_block: Character):
        indent = self.indent
        return (
            f"{indent}Vow of Enmity:\n"
            f"{indent}Unlocked: Oath of Vengeance Paladin level 3:\n"
            f"{indent}Range: 30 ft;\n"
            f"{indent}Casting Time: None, but requires the Attack action to use.\n"
            f"{indent}Duration: 1 minute or until you use this feature again.\n"
            f"{indent}You gain Advantage on attack rolls against targeted creature.\n"
            f"{indent}If the creature drops to 0 Hit Points before the vow ends, you can transfer the vow to a different creature within 30 feet of yourself (no action required).\n"
        )

    def get_description(self, character_stat_block: Character) -> str:
        usages = 2
        if character_stat_block.level >= 11:
            usages = 3

        description = (
            "Each time you use this class's Channel Divinity, you choose which effect from this class to create.\n"
            f"Usage: {usages}.\n"
            "You regain one after a Short Rest, all after a Long Rest.\n"
            "DC: class's Spellcasting feature.\n"
        )

        if "Divine Sense" in self.spells:
            description += "\n"
            description += self.get_divine_sense_description(character_stat_block)

        if "Vow of Enmity" in self.spells:
            description += "\n"
            description += self.get_vow_of_enmity_description(character_stat_block)

        return description


class PaladinsSmite(TextFeature):
    def __init__(self):
        super().__init__(name="Paladin's Smite", origin="Paladin Level 2")

    def get_description(self, character_stat_block: Character) -> str:
        return "Level 2: Divine Smite is always prepared and can be cast once per Long Rest without a spell slot.\n"


class LayOnHands(TextFeature):
    def __init__(self):
        super().__init__(name="Lay on Hands", origin="Paladin Level 1")

    def get_description(self, character_stat_block: Character) -> str:
        return (
            "You have a pool of healing power.\n"
            f"Power in pool: 5 x Paladin level (5 x {character_stat_block.level} = {5 * character_stat_block.level}) Hit Points.\n"
            "You can also expend 5 Hit Points from the pool of healing power to remove the Poisoned condition from the creature; those points don't also restore Hit Points to the creature."
            "Replenishes on Long Rest.\n"
            "Casting time: Bonus Action.\n"
            "Range: Touch.\n"
        )


class ExtraAttack(TextFeature):
    def __init__(self):
        super().__init__(name="Extra Attack", origin="Paladin Level 5")

    def get_description(self, character_stat_block: Character) -> str:
        return (
            "Level 5: Extra Attack\n"
            "You can attack twice instead of once whenever you take the Attack action on your turn.\n"
        )


class FaithfulSteed(TextFeature):
    def __init__(self):
        super().__init__(name="Faithful Steed", origin="Paladin Level 5")

    def get_description(self, character_stat_block: Character) -> str:
        return (
            "Level 5: Faithful Steed\n"
            "You can call on the aid of an otherworldly steed. You always have the Find Steed spell prepared.\n"
            "You can also cast the spell once without expending a spell slot, and you regain the ability to do so when you finish a Long Rest.\n"
        )


class AuraOfProtection(TextFeature):
    def __init__(self):
        super().__init__(name="Aura of Protection", origin="Paladin Level 6")

    def get_description(self, character_stat_block: Character) -> str:
        charisma_mod = character_stat_block.get_ability_modifier(Ability.CHARISMA)
        return (
            "Level 6: Aura of Protection\n"
            "You radiate a protective, unseeable aura in a 10-foot Emanation that originates from you. The aura is inactive while you have the Incapacitated condition.\n"
            f"You and your allies in the aura gain a bonus to saving throws equal to your Charisma modifier (+{charisma_mod}).\n"
            "(Doesn't stack choose which one if multiple).\n"
        )


class SpellSlots(CharacterFeature):

    def modify(self, character_stat_block: Character):

        level_1_spell_slots = 0
        level_2_spell_slots = 0
        level_3_spell_slots = 0
        level_4_spell_slots = 0
        level_5_spell_slots = 0

        if character_stat_block.level >= 1:
            level_1_spell_slots += 2

        if character_stat_block.level >= 3:
            level_1_spell_slots += 1

        if character_stat_block.level >= 5:
            level_1_spell_slots += 1
            level_2_spell_slots += 2

        if character_stat_block.level >= 7:
            level_2_spell_slots += 1

        if character_stat_block.level >= 9:
            level_3_spell_slots += 2

        if character_stat_block.level >= 11:
            level_3_spell_slots += 1

        if character_stat_block.level >= 13:
            level_4_spell_slots += 1

        if character_stat_block.level >= 15:
            level_4_spell_slots += 1

        if character_stat_block.level >= 17:
            level_4_spell_slots += 1
            level_5_spell_slots += 1

        if character_stat_block.level >= 19:
            level_5_spell_slots += 1

        character_stat_block.spell_slots = {
            1: level_1_spell_slots,
            2: level_2_spell_slots,
            3: level_3_spell_slots,
            4: level_4_spell_slots,
            5: level_5_spell_slots,
        }
