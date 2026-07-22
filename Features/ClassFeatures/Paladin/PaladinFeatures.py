from Core.Definitions import PALADIN_HIT_DIE
from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class LayOnHands(Feature):
    def __init__(self):
        super().__init__(name="Lay on Hands", origin="Paladin Level 1")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your blessed touch can heal wounds. You have a pool of healing power that replenishes when you take a Long Rest. With that pool, you can restore a total number of Hit Points equal to five times your Paladin level.\n"
            "As a Bonus Action, you can touch a creature (which could be yourself) and draw power from the pool of healing to restore a number of Hit Points to that creature, up to the maximum amount remaining in the pool.\n"
            "You can also expend 5 Hit Points from the pool of healing power to remove the Poisoned condition from the creature; those points don't also restore Hit Points to the creature."
        )
        return description


class WeaponMastery(Feature):
    def __init__(self):
        super().__init__(name="Weapon Mastery", origin="Paladin Level 1")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your training with weapons allows you to use the mastery properties of two kinds of weapons of your choice with which you have proficiency, such as Longswords and Javelins.\n"
            "Whenever you finish a Long Rest, you can change the kinds of weapons you chose. For example, you could switch to using the mastery properties of Halberds and Flails."
        )
        return description


class FightingStyle(Feature):
    def __init__(self):
        super().__init__(name="Fighting Style", origin="Paladin Level 2")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain a Fighting Style feat of your choice. Instead of choosing one of those feats, you can choose the option below.\n"
            "Blessed Warrior. You learn two Cleric cantrips of your choice. Guidance and Sacred Flame are recommended. The chosen cantrips count as Paladin spells for you, and Charisma is your spellcasting ability for them. Whenever you gain a Paladin level, you can replace one of these cantrips with another Cleric cantrip."
        )
        return description


class PaladinsSmite(Feature):
    def __init__(self):
        super().__init__(name="Paladin's Smite", origin="Paladin Level 2")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You always have the Divine Smite spell prepared. In addition, you can cast it without expending a spell slot, but you must finish a Long Rest before you can cast it in this way again."
        return description


class ChannelDivinity(Feature):
    _INDENT = "    "

    def __init__(self):
        self.spells = []
        super().__init__(name="Channel Divinity", origin="Paladin Level 3")

    def add_spell(self, spell: str):
        self.spells.append(spell)

    def get_divine_sense_description(self, character_stat_block: CharacterStatBlock):
        indent = self._INDENT
        return (
            f"{indent}Divine Sense:\n"
            f"{indent}Unlocked: Paladin level 3:\n"
            f"{indent}Range: 60 ft radius;\n"
            f"{indent}Casting Time: Bonus Action;\n"
            f"{indent}Duration: 10 minutes.\n"
            f"{indent}Detects Celestials, Fiends, and Undead (location and creature type), and senses consecrated/desecrated places/objects within range.\n"
        )

    def get_vow_of_enmity_description(self, character_stat_block: CharacterStatBlock):
        indent = self._INDENT
        return (
            f"{indent}Vow of Enmity:\n"
            f"{indent}Unlocked: Oath of Vengeance Paladin level 3:\n"
            f"{indent}Range: 30 ft;\n"
            f"{indent}Casting Time: None, but requires the Attack action to use.\n"
            f"{indent}Duration: 1 minute or until you use this feature again.\n"
            f"{indent}You gain Advantage on attack rolls against targeted creature.\n"
            f"{indent}If the creature drops to 0 Hit Points before the vow ends, you can transfer the vow to a different creature within 30 feet of yourself (no action required).\n"
        )

    def get_sacred_weapon_description(self, character_stat_block: CharacterStatBlock):
        indent = self._INDENT
        return (
            f"{indent}Sacred Weapon:\n"
            f"{indent}Unlocked: Oath of Devotion Paladin level 3:\n"
            f"{indent}Range: 30 ft;\n"
            f"{indent}Casting Time: None, but requires the Attack action to use.\n"
            f"{indent}Duration: 10 minutes or until you use this feature again or turn it off (not action required) or you aren't carrying your weapon.\n"
            f"{indent}You add your Charisma modifier to attack rolls you make with that weapon (minimum bonus of +1), and each time you hit with it, you cause it to deal its normal damage type or Radiant damage.\n"
            f"{indent}The weapon also emits Bright Light in a 20-foot radius and Dim Light 20 feet beyond that.\n"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        usages = 2
        if character_stat_block.character_level >= 11:
            usages = 3

        description = (
            "Each time you use this class's Channel Divinity, you choose which effect from this class to create.\n"
            f"Usage: {usages}.\n"
            "You regain one after a Short Rest, all after a Long Rest.\n"
            "DC: class's Spellcasting feature.\n"
        )
        description = StringUtils.add_boxes(
            description,
            usages,
            regain_x_on=(1, "short rest"),
            regain_all_on="long rest",
        )

        if "Divine Sense" in self.spells:
            description += "\n"
            description += self.get_divine_sense_description(character_stat_block)

        if "Vow of Enmity" in self.spells:
            description += "\n"
            description += self.get_vow_of_enmity_description(character_stat_block)

        if "Sacred Weapon" in self.spells:
            description += "\n"
            description += self.get_sacred_weapon_description(character_stat_block)

        if "Abjure Foes" in self.spells:
            description += "\n"
            description += AbjureFoes().get_description(character_stat_block) + "\n"

        return description


class ExtraAttack(Feature):
    def __init__(self):
        super().__init__(name="Extra Attack", origin="Paladin Level 5")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can attack twice instead of once whenever you take the Attack action on your turn."
        return description


class FaithfulSteed(Feature):
    def __init__(self):
        super().__init__(name="Faithful Steed", origin="Paladin Level 5")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can call on the aid of an otherworldly steed. You always have the Find Steed spell prepared.\n"
            "You can also cast the spell once without expending a spell slot, and you regain the ability to do so when you finish a Long Rest."
        )
        return description


class AuraOfProtection(Feature):
    def __init__(self):
        super().__init__(name="Aura of Protection", origin="Paladin Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You radiate a protective, unseeable aura in a 10-foot Emanation that originates from you. The aura is inactive while you have the Incapacitated condition.\n"
            "You and your allies in the aura gain a bonus to saving throws equal to your Charisma modifier (minimum bonus of +1).\n"
            "If another Paladin is present, a creature can benefit from only one Aura of Protection at a time; the creature chooses which aura while in them."
        )
        return description


class AbjureFoes(Feature):
    def __init__(self):
        super().__init__(name="Abjure Foes", origin="Paladin Level 9")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "As a Magic action, you can expend one use of this class's Channel Divinity to overwhelm foes with awe. As you present your Holy Symbol or weapon, you can target a number of creatures equal to your Charisma modifier (minimum of one creature) that you can see within 60 feet of yourself. Each target must succeed on a Wisdom saving throw or have the Frightened condition for 1 minute or until it takes any damage. While Frightened in this way, a target can do only one of the following on its turns: move, take an action, or take a Bonus Action."
        return description


class AuraOfCourage(Feature):
    def __init__(self):
        super().__init__(name="Aura of Courage", origin="Paladin Level 10")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You and your allies have Immunity to the Frightened condition while in your Aura of Protection. If a Frightened ally enters the aura, that condition has no effect on that ally while there."
        return description


class RadiantStrikes(Feature):
    def __init__(self):
        super().__init__(name="Radiant Strikes", origin="Paladin Level 11")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Your strikes now carry supernatural power. When you hit a target with an attack roll using a Melee weapon or an Unarmed Strike, the target takes an extra 1d8 Radiant damage."
        return description


class RestoringTouch(Feature):
    def __init__(self):
        super().__init__(name="Restoring Touch", origin="Paladin Level 14")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you use Lay On Hands on a creature, you can also remove one or more of the following conditions from the creature: Blinded, Charmed, Deafened, Frightened, Paralyzed, or Stunned. You must expend 5 Hit Points from the healing pool of Lay On Hands for each of these conditions you remove; those points don't also restore Hit Points to the creature."
        return description


class AuraExpansion(Feature):
    def __init__(self):
        super().__init__(name="Aura Expansion", origin="Paladin Level 18")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Your Aura of Protection is now a 30-foot Emanation."
        return description
