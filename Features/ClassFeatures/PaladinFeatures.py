from StatBlocks.CharacterStatBlock import CharacterStatBlock
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

    def get_divine_sense_description(self, character_stat_block: CharacterStatBlock):
        indent = self.indent
        return (
            f"{indent}Divine Sense:\n"
            f"{indent}Unlocked: Paladin level 3:\n"
            f"{indent}Range: 60 ft radius;\n"
            f"{indent}Casting Time: Bonus Action;\n"
            f"{indent}Duration: 10 minutes.\n"
            f"{indent}Detects Celestials, Fiends, and Undead (location and creature type), and senses consecrated/desecrated places/objects within range.\n"
        )

    def get_vow_of_enmity_description(self, character_stat_block: CharacterStatBlock):
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

    def get_sacred_weapon_description(self, character_stat_block: CharacterStatBlock):
        indent = self.indent
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

        if "Sacred Weapon" in self.spells:
            description += "\n"
            description += self.get_sacred_weapon_description(character_stat_block)

        if "Abjure Foes" in self.spells:
            description += self.add_feature_effects(character_stat_block, AbjureFoes())

        return description


class AbjureFoes(TextFeature):
    def __init__(self):
        super().__init__(name="Abjure Foes", origin="Paladin Level 9")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        charisma_mod = character_stat_block.get_ability_modifier(Ability.CHARISMA)
        spell_casting_dc = character_stat_block.calculate_spell_save_dc()
        text = f"As a Magic action, you can expend one use of this class's Channel Divinity to overwhelm foes with awe. As you present your Holy Symbol or weapon, you can target a number of creatures equal to your Charisma modifier ({charisma_mod}) (minimum of one creature) that you can see within 60 feet of yourself. Each target must succeed on a Wisdom saving throw (DC={spell_casting_dc}) or have the Frightened condition for 1 minute or until it takes any damage. While Frightened in this way, a target can do only one of the following on its turns: move, take an action, or take a Bonus Action."
        return text


class PeerlessAthlete(TextFeature):
    def __init__(self):
        super().__init__(
            name="Peerless Athlete", origin="Oath of Glory Paladin Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "As a Bonus Action, you can expend one use of your Channel Divinity to augment your athleticism. For 1 hour, you have Advantage on Strength (Athletics) and Dexterity (Acrobatics) checks, and the distance of your Long and High Jumps increases by 10 feet (this extra distance costs movement as normal)."
        return description


class InspiringSmite(TextFeature):
    def __init__(self):
        super().__init__(name="Inspiring Smite", origin="Oath of Glory Paladin Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Immediately after you cast Divine Smite, you can expend one use of your Channel Divinity and distribute Temporary Hit Points to creatures of your choice within 30 feet of yourself, which can include you. The total number of Temporary Hit Points equals 2d8 plus your Paladin level, divided among the chosen creatures however you like."
        return description


class GloriousDefense(TextFeature):
    def __init__(self):
        super().__init__(
            name="Glorious Defense", origin="Oath of Glory Paladin Level 15"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can turn defense into a sudden strike. When you or another creature you can see within 10 feet of you is hit by an attack roll, you can take a Reaction to grant a bonus to the target's AC against that attack, potentially causing it to miss. The bonus equals your Charisma modifier (minimum of +1). If the attack misses, you can make one attack with a weapon against the attacker as part of this Reaction if the attacker is within your weapon's range.\n"
            "You can use this feature a number of times equal to your Charisma modifier (minimum of once), and you regain all expended uses when you finish a Long Rest."
        )
        return description


class LivingLegend(TextFeature):
    def __init__(self):
        super().__init__(name="Living Legend", origin="Oath of Glory Paladin Level 20")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can empower yourself with the legends - whether true or exaggerated - of your great deeds. As a Bonus Action, you gain the benefits below for 10 minutes. Once you use this feature, you can't use it again until you finish a Long Rest. You can also restore your use of it by expending a level 5 spell slot (no action required).\n"
            "Charismatic. You are blessed with an otherworldly presence and have Advantage on all Charisma checks.\n"
            "Saving Throw Reroll. If you fail a saving throw, you can take a Reaction to reroll it. You must use this new roll.\n"
            "Unerring Strike. Once on each of your turns when you make an attack roll with a weapon and miss, you can cause that attack to hit instead."
        )
        return description


class AvengingAngel(TextFeature):
    def __init__(self):
        super().__init__(name="Avenging Angel", origin="Paladin Level 20")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "As a Bonus Action, you gain the benefits below for 10 minutes or until you end them (no action required). Once you use this feature, you can't use it\n"
            "again until you finish a Long Rest. You can also restore your use of it by expending a level 5 spell slot (no action required).\n"
            "Flight. You sprout spectral wings on your back, have a Fly Speed of 60 feet, and can hover.\n"
            "Frightful Aura. Whenever an enemy starts its turn in your Aura of Protection, that creature must succeed on a Wisdom saving throw or have the Frightened condition for 1 minute or until it takes any damage. Attack rolls against the Frightened creature have Advantage.\n"
        )
        return description


class SoulOfVengeance(TextFeature):
    def __init__(self):
        super().__init__(name="Soul of Vengeance", origin="Paladin Level 15")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "Immediately after a creature under the effect of your Vow of Enmity hits or misses with an attack roll, you can take a Reaction to make a melee attack against that creature if it's within range."


class AuraOfAlacrity(TextFeature):
    def __init__(self):
        super().__init__(
            name="Aura of Alacrity", origin="Oath of Glory Paladin Level 7"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "In addition, whenever an ally enters your Aura of Protection for the first time on a turn or starts their turn there, the ally's Speed increases by 10 feet until the end of their next turn."


class RelentlessAvenger(TextFeature):
    def __init__(self):
        super().__init__(name="Relentless Avenger", origin="Paladin Level 7")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "Your supernatural focus helps you close off a foe's retreat. When you hit a creature with an Opportunity Attack, you can reduce the creature's Speed to 0 until the end of the current turn. You can then move up to half your Speed as part of the same Reaction. This movement doesn't provoke Opportunity Attacks."


class PaladinsSmite(TextFeature):
    def __init__(self):
        super().__init__(name="Paladin's Smite", origin="Paladin Level 2")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "Level 2: Divine Smite is always prepared and can be cast once per Long Rest without a spell slot.\n"


class LayOnHands(TextFeature):
    def __init__(self):
        self.additional_features = []
        super().__init__(name="Lay on Hands", origin="Paladin Level 1")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
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

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "Level 5: Extra Attack\n"
            "You can attack twice instead of once whenever you take the Attack action on your turn.\n"
        )


class FaithfulSteed(TextFeature):
    def __init__(self):
        super().__init__(name="Faithful Steed", origin="Paladin Level 5")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "Level 5: Faithful Steed\n"
            "You can call on the aid of an otherworldly steed. You always have the Find Steed spell prepared.\n"
            "You can also cast the spell once without expending a spell slot, and you regain the ability to do so when you finish a Long Rest.\n"
        )


class AuraOfProtection(TextFeature):
    def __init__(self):
        super().__init__(name="Aura of Protection", origin="Paladin Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        charisma_mod = character_stat_block.get_ability_modifier(Ability.CHARISMA)

        return (
            "Level 6: Aura of Protection\n"
            "You radiate a protective, unseeable aura in a 10-foot Emanation that originates from you. The aura is inactive while you have the Incapacitated condition.\n"
            f"You and your allies in the aura gain a bonus to saving throws equal to your Charisma modifier (+{charisma_mod}).\n"
            "(Doesn't stack choose which one if multiple).\n"
        )


class AuraOfDevotion(TextFeature):
    def __init__(self):
        super().__init__(
            name="Aura of Devotion", origin="Oath of Devotion Paladin Level 7"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "You and your allies have Immunity to the Charmed condition while in your Aura of Protection.\nIf a Charmed ally enters the aura, that condition has no effect on that ally while there."


class AuraOfCourage(TextFeature):
    def __init__(self):
        super().__init__(name="Aura of Courage", origin="Paladin Level 10")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "You and your allies have Immunity to the Frightened condition while in your Aura of Protection. If a Frightened ally enters the aura, that condition has no effect on that ally while there."


class RadiantStrikes(TextFeature):
    def __init__(self):
        super().__init__(name="Radiant Strikes", origin="Paladin Level 10")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "Your strikes now carry supernatural power. When you hit a target with an attack roll using a Melee weapon or an Unarmed Strike, the target takes an extra 1d8 Radiant damage."


class RestoringTouch(TextFeature):
    def __init__(self):
        super().__init__(name="Restoring Touch", origin="Paladin Level 14")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "When you use Lay On Hands on a creature, you can also remove one or more of the following conditions from the creature: Blinded, Charmed, Deafened, Frightened, Paralyzed, or Stunned. You must expend 5 Hit Points from the healing pool of Lay On Hands for each of these conditions you remove; those points don't also restore Hit Points to the creature."


class AuraOfExpansion(TextFeature):
    def __init__(self):
        super().__init__(name="Aura of Expansion", origin="Paladin Level 18")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "Your Aura of Protection is now a 30-foot Emanation."


class SmiteOfProtection(TextFeature):
    def __init__(self):
        super().__init__(
            name="Smite of Protection", origin="Oath of Devotion Paladin Level 15"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "Your magical smite now radiates protective energy. Whenever you cast Divine Smite, you and your allies have Half Cover while in your Aura of Protection. The aura has this benefit until the start of your next turn."


class HolyNimbus(TextFeature):
    def __init__(self):
        super().__init__(name="Holy Nimbus", origin="Oath of Devotion Paladin Level 20")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        text = (
            "As a Bonus Action, you can imbue your Aura of Protection with holy power, granting the benefits below for 10 minutes or until you end them (no action required). Once you use this feature, you can't use it again until you finish a Long Rest. You can also restore your use of it by expending a level 5 spell slot (no action required).\n"
            "Holy Ward. You have Advantage on any saving throw you are forced to make by a Fiend or an Undead.\n"
            "Radiant Damage. Whenever an enemy starts its turn in the aura, that creature takes Radiant damage equal to your Charisma modifier plus your Proficiency Bonus.\n"
            "Sunlight. The aura is filled with Bright Light that is sunlight.\n"
        )

        return text
