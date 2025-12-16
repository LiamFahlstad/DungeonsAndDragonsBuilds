from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Definitions import Ability, DiceRollCondition, Skill
from Features.BaseFeatures import CharacterFeature, TextFeature


PALADIN_HIT_DIE = 10


class LayOnHands(TextFeature):
    def __init__(self):
        super().__init__(name="Lay on Hands", origin="Paladin Level 1")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your blessed touch can heal wounds. You have a pool of healing power that replenishes when you take a Long Rest. With that pool, you can restore a total number of Hit Points equal to five times your Paladin level.\n"
            "As a Bonus Action, you can touch a creature (which could be yourself) and draw power from the pool of healing to restore a number of Hit Points to that creature, up to the maximum amount remaining in the pool.\n"
            "You can also expend 5 Hit Points from the pool of healing power to remove the Poisoned condition from the creature; those points don't also restore Hit Points to the creature."
        )
        return description


class WeaponMastery(TextFeature):
    def __init__(self):
        super().__init__(name="Weapon Mastery", origin="Paladin Level 1")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your training with weapons allows you to use the mastery properties of two kinds of weapons of your choice with which you have proficiency, such as Longswords and Javelins.\n"
            "Whenever you finish a Long Rest, you can change the kinds of weapons you chose. For example, you could switch to using the mastery properties of Halberds and Flails."
        )
        return description


class FightingStyle(TextFeature):
    def __init__(self):
        super().__init__(name="Fighting Style", origin="Paladin Level 2")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain a Fighting Style feat of your choice. Instead of choosing one of those feats, you can choose the option below.\n"
            "Blessed Warrior. You learn two Cleric cantrips of your choice. Guidance and Sacred Flame are recommended. The chosen cantrips count as Paladin spells for you, and Charisma is your spellcasting ability for them. Whenever you gain a Paladin level, you can replace one of these cantrips with another Cleric cantrip."
        )
        return description


class PaladinsSmite(TextFeature):
    def __init__(self):
        super().__init__(name="Paladin's Smite", origin="Paladin Level 2")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You always have the Divine Smite spell prepared. In addition, you can cast it without expending a spell slot, but you must finish a Long Rest before you can cast it in this way again."
        return description


class ChannelDivinity(TextFeature):
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
        if character_stat_block.character_level >= 11:
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


class ExtraAttack(TextFeature):
    def __init__(self):
        super().__init__(name="Extra Attack", origin="Paladin Level 5")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can attack twice instead of once whenever you take the Attack action on your turn."
        return description


class FaithfulSteed(TextFeature):
    def __init__(self):
        super().__init__(name="Faithful Steed", origin="Paladin Level 5")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can call on the aid of an otherworldly steed. You always have the Find Steed spell prepared.\n"
            "You can also cast the spell once without expending a spell slot, and you regain the ability to do so when you finish a Long Rest."
        )
        return description


class AuraOfProtection(TextFeature):
    def __init__(self):
        super().__init__(name="Aura of Protection", origin="Paladin Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You radiate a protective, unseeable aura in a 10-foot Emanation that originates from you. The aura is inactive while you have the Incapacitated condition.\n"
            "You and your allies in the aura gain a bonus to saving throws equal to your Charisma modifier (minimum bonus of +1).\n"
            "If another Paladin is present, a creature can benefit from only one Aura of Protection at a time; the creature chooses which aura while in them."
        )
        return description


class AbjureFoes(TextFeature):
    def __init__(self):
        super().__init__(name="Abjure Foes", origin="Paladin Level 9")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "As a Magic action, you can expend one use of this class's Channel Divinity to overwhelm foes with awe. As you present your Holy Symbol or weapon, you can target a number of creatures equal to your Charisma modifier (minimum of one creature) that you can see within 60 feet of yourself. Each target must succeed on a Wisdom saving throw or have the Frightened condition for 1 minute or until it takes any damage. While Frightened in this way, a target can do only one of the following on its turns: move, take an action, or take a Bonus Action."
        return description


class AuraOfCourage(TextFeature):
    def __init__(self):
        super().__init__(name="Aura of Courage", origin="Paladin Level 10")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You and your allies have Immunity to the Frightened condition while in your Aura of Protection. If a Frightened ally enters the aura, that condition has no effect on that ally while there."
        return description


class RadiantStrikes(TextFeature):
    def __init__(self):
        super().__init__(name="Radiant Strikes", origin="Paladin Level 11")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Your strikes now carry supernatural power. When you hit a target with an attack roll using a Melee weapon or an Unarmed Strike, the target takes an extra 1d8 Radiant damage."
        return description


class RestoringTouch(TextFeature):
    def __init__(self):
        super().__init__(name="Restoring Touch", origin="Paladin Level 14")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you use Lay On Hands on a creature, you can also remove one or more of the following conditions from the creature: Blinded, Charmed, Deafened, Frightened, Paralyzed, or Stunned. You must expend 5 Hit Points from the healing pool of Lay On Hands for each of these conditions you remove; those points don't also restore Hit Points to the creature."
        return description


class AuraExpansion(TextFeature):
    def __init__(self):
        super().__init__(name="Aura Expansion", origin="Paladin Level 18")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Your Aura of Protection is now a 30-foot Emanation."
        return description


### Oath of Devotion Paladin Features ###


class OathOfDevotionSpells(TextFeature):
    def __init__(self):
        super().__init__(
            name="Oath of Devotion Spells", origin="Oath of Devotion Paladin Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "The magic of your oath ensures you always have certain spells ready; when you reach a Paladin level specified in the Oath of Devotion Spells table, you thereafter always have the listed spells prepared.\n"
            "Oath of Devotion Spells\n"
            "Paladin Level	Spells\n"
            "3	Protection from Evil and Good, Shield of Faith\n"
            "5	Aid, Zone of Truth\n"
            "9	Beacon of Hope, Dispel Magic\n"
            "13	Freedom of Movement, Guardian of Faith\n"
            "17	Commune, Flame Strike"
        )
        return description


class SacredWeapon(TextFeature):
    def __init__(self):
        super().__init__(
            name="Sacred Weapon", origin="Oath of Devotion Paladin Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you take the Attack action, you can expend one use of your Channel Divinity to imbue one Melee weapon that you are holding with positive energy. For 10 minutes or until you use this feature again, you add your Charisma modifier to attack rolls you make with that weapon (minimum bonus of +1), and each time you hit with it, you cause it to deal its normal damage type or Radiant damage.\n"
            "The weapon also emits Bright Light in a 20-foot radius and Dim Light 20 feet beyond that.\n"
            "You can end this effect early (no action required). This effect also ends if you aren't carrying the weapon."
        )
        return description


class AuraOfDevotion(TextFeature):
    def __init__(self):
        super().__init__(
            name="Aura of Devotion", origin="Oath of Devotion Paladin Level 7"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You and your allies have Immunity to the Charmed condition while in your Aura of Protection. If a Charmed ally enters the aura, that condition has no effect on that ally while there."
        return description


class SmiteOfProtection(TextFeature):
    def __init__(self):
        super().__init__(
            name="Smite of Protection", origin="Oath of Devotion Paladin Level 15"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Your magical smite now radiates protective energy. Whenever you cast Divine Smite, you and your allies have Half Cover while in your Aura of Protection. The aura has this benefit until the start of your next turn."
        return description


class HolyNimbus(TextFeature):
    def __init__(self):
        super().__init__(name="Holy Nimbus", origin="Oath of Devotion Paladin Level 20")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "As a Bonus Action, you can imbue your Aura of Protection with holy power, granting the benefits below for 10 minutes or until you end them (no action required). Once you use this feature, you can't use it again until you finish a Long Rest. You can also restore your use of it by expending a level 5 spell slot (no action required).\n"
            "Holy Ward. You have Advantage on any saving throw you are forced to make by a Fiend or an Undead.\n"
            "Radiant Damage. Whenever an enemy starts its turn in the aura, that creature takes Radiant damage equal to your Charisma modifier plus your Proficiency Bonus.\n"
            "Sunlight. The aura is filled with Bright Light that is sunlight."
        )
        return description


### Oath of Glory Paladin Features ###


class InspiringSmite(TextFeature):
    def __init__(self):
        super().__init__(name="Inspiring Smite", origin="Oath of Glory Paladin Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Immediately after you cast Divine Smite, you can expend one use of your Channel Divinity and distribute Temporary Hit Points to creatures of your choice within 30 feet of yourself, which can include you. The total number of Temporary Hit Points equals 2d8 plus your Paladin level, divided among the chosen creatures however you like."
        return description


class OathOfGlorySpells(TextFeature):
    def __init__(self):
        super().__init__(
            name="Oath of Glory Spells", origin="Oath of Glory Paladin Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "The magic of your oath ensures you always have certain spells ready; when you reach a Paladin level specified in the Oath of Glory Spells table, you thereafter always have the listed spells prepared.\n"
            "Oath of Glory Spells\n"
            "Paladin Level	Spells\n"
            "3	Guiding Bolt, Heroism\n"
            "5	Enhance Ability, Magic Weapon\n"
            "9	Haste, Protection from Energy\n"
            "13	Compulsion, Freedom of Movement\n"
            "17	Legend Lore, Yolande's Regal Presence"
        )
        return description


class PeerlessAthlete(TextFeature):
    def __init__(self):
        super().__init__(
            name="Peerless Athlete", origin="Oath of Glory Paladin Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "As a Bonus Action, you can expend one use of your Channel Divinity to augment your athleticism. For 1 hour, you have Advantage on Strength (Athletics) and Dexterity (Acrobatics) checks, and the distance of your Long and High jumps increases by 10 feet (this extra distance costs movement as normal)."
        return description


class AuraOfAlacrity(TextFeature):
    def __init__(self):
        super().__init__(
            name="Aura of Alacrity", origin="Oath of Glory Paladin Level 7"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your Speed increases by 10 feet.\n"
            "In addition, whenever an ally enters your Aura of Protection for the first time on a turn or starts their turn here, the ally's Speed increases by 10 feet until the end of their next turn."
        )
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
            "You can empower yourself with the legends—whether true or exaggerated—of your great deeds. As a Bonus Action, you gain the following benefits for 1 minute. Once you use this feature, you can't use it again until you finish a Long Rest. You can also restore your use of it by expending a level 5 spell slot (no action required).\n"
            "Charismatic. You are blessed with an otherworldly presence and have Advantage on all Charisma checks.\n"
            "Saving Throw Reroll. If you fail a saving throw, you can take a Reaction to reroll it. You must use this new roll.\n"
            "Unerring Strike. Once on each of your turns when you make an attack roll with a weapon and miss, you can cause that attack to hit instead."
        )
        return description


### Oath of the Ancients Paladin Features ###


class NaturesWrath(TextFeature):
    def __init__(self):
        super().__init__(
            name="Nature's Wrath", origin="Oath of the Ancients Paladin Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "As a Magic action, you can expend one use of your Channel Divinity to conjure spectral vines around nearby creatures. Each creature of your choice that you can see within 15 feet of yourself must succeed on a Strength saving throw or have the Restrained condition for 1 minute. A Restrained creature repeats the saving throw at the end of each of its turns, ending the effect on itself on a success."
        return description


class OathOfTheAncientsSpells(TextFeature):
    def __init__(self):
        super().__init__(
            name="Oath of the Ancients Spells",
            origin="Oath of the Ancients Paladin Level 3",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "The magic of your oath ensures you always have certain spells ready; when you reach a Paladin level specified in the Oath of the Ancients Spells table, you thereafter always have the listed spells prepared.\n"
            "Oath of the Ancients Spells\n"
            "Paladin Level	Spells\n"
            "3	Ensnaring Strike, Speak with Animals\n"
            "5	Misty Step, Moonbeam\n"
            "9	Plant Growth, Protection from Energy\n"
            "13	Ice Storm, Stoneskin\n"
            "17	Commune with Nature, Tree Stride"
        )
        return description


class AuraOfWarding(TextFeature):
    def __init__(self):
        super().__init__(
            name="Aura of Warding", origin="Oath of the Ancients Paladin Level 7"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Ancient magic lies so heavily upon you that it forms an eldritch ward, blunting energy from beyond the Material Plane; you and your allies have Resistance to Necrotic, Psychic, and Radiant damage while in your Aura of Protection."
        return description


class UndyingSentinel(TextFeature):
    def __init__(self):
        super().__init__(
            name="Undying Sentinel", origin="Oath of the Ancients Paladin Level 15"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you are reduced to 0 Hit Points and not killed outright, you can drop to 1 Hit Point instead, and you regain a number of Hit Points equal to three times your Paladin level. Once you use this feature, you can't do so again until you finish a Long Rest.\n"
            "Additionally, you can't be aged magically, and you cease visibly aging."
        )
        return description


class ElderChampion(TextFeature):
    def __init__(self):
        super().__init__(
            name="Elder Champion", origin="Oath of the Ancients Paladin Level 20"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "As a Bonus Action, you can imbue your Aura of Protection with primal power, granting the following benefits for 1 minute or until you end them (no action required). Once you use this feature, you can't use it again until you finish a Long Rest. You can also restore your use of it by expending a level 5 spell slot (no action required).\n"
            "Diminish Defiance. Enemies in the aura have Disadvantage on saving throws against your spells and Channel Divinity options.\n"
            "Regeneration. At the start of each of your turns, you regain 10 Hit Points.\n"
            "Swift Spells. Whenever you cast a spell that has a casting time of an action, you can cast it using a Bonus Action instead."
        )
        return description


### Oath of Vengeance Paladin Features ###


class OathOfVengeanceSpells(TextFeature):
    def __init__(self):
        super().__init__(
            name="Oath of Vengeance Spells", origin="Oath of Vengeance Paladin Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "The magic of your oath ensures you always have certain spells ready; when you reach a Paladin level specified in the Oath of Vengeance Spells table, you thereafter always have the listed spells prepared.\n"
            "Oath of Vengeance Spells\n"
            "Paladin Level	Spells\n"
            "3	Bane, Hunter's Mark\n"
            "5	Hold Person, Misty Step\n"
            "9	Haste, Protection from Energy\n"
            "13	Banishment, Dimension Door\n"
            "17	Hold Monster, Scrying"
        )
        return description


class VowOfEnmity(TextFeature):
    def __init__(self):
        super().__init__(
            name="Vow of Enmity", origin="Oath of Vengeance Paladin Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you take the Attack action, you can expend one use of your Channel Divinity to utter a vow of enmity against a creature you can see within 30 feet of yourself. You gain Advantage on attack rolls against the creature for 1 minute or until you use this feature again.\n"
            "If the creature drops to 0 Hit Points before the vow ends, you can transfer the vow to a different creature within 30 feet of yourself (no action required)."
        )
        return description


class RelentlessAvenger(TextFeature):
    def __init__(self):
        super().__init__(
            name="Relentless Avenger", origin="Oath of Vengeance Paladin Level 7"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Your supernatural focus helps you close off a foe's retreat. When you hit a creature with an Opportunity Attack, you can reduce the creature's Speed to 0 until the end of the current turn. You can then move up to half your Speed as part of the same Reaction. This movement doesn't provoke Opportunity Attacks."
        return description


class SoulOfVengeance(TextFeature):
    def __init__(self):
        super().__init__(
            name="Soul of Vengeance", origin="Oath of Vengeance Paladin Level 15"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Immediately after a creature under the effect of your Vow of Enmity hits or misses with an attack roll, you can take a Reaction to make a melee attack against that creature if it's within range."
        return description


class AvengingAngel(TextFeature):
    def __init__(self):
        super().__init__(
            name="Avenging Angel", origin="Oath of Vengeance Paladin Level 20"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "As a Bonus Action, you gain the benefits below for 10 minutes or until you end them (no action required). Once you use this feature, you can't use it\n"
            "again until you finish a Long Rest. You can also restore your use of it by expending a level 5 spell slot (no action required).\n"
            "Flight. You sprout spectral wings on your back, have a Fly Speed of 60 feet, and can hover.\n"
            "Frightful Aura. Whenever an enemy starts its turn in your Aura of Protection, that creature must succeed on a Wisdom saving throw or have the Frightened condition for 1 minute or until it takes any damage. Attack rolls against the Frightened creature have Advantage."
        )
        return description


### Oath of the Noble Genies Paladin Features ###


class ElementalSmite(TextFeature):
    def __init__(self):
        super().__init__(
            name="Elemental Smite", origin="Oath of the Noble Genies Paladin Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Immediately after you cast Divine Smite, you can expend one use of your Channel Divinity and invoke one of the following effects.\n"
            "Dao's Crush. Earth rises up around the target of your Divine Smite. The target has the Grappled condition (escape DC equal to your spell save DC). While Grappled, the target has the Restrained condition.\n"
            "Djinni's Escape. You teleport to an unoccupied space you can see within 30 feet of yourself and take on a semi-incorporeal form, which lasts until the end of your next turn. While in this form, you have Resistance to Bludgeoning, Piercing, and Slashing damage, and you have Immunity to the Grappled, Prone, and Restrained conditions.\n"
            "Efreeti's Fury. The target of your Divine Smite takes an extra 2d4 Fire damage, and fire jumps from the target to another creature you can see within 30 feet of yourself. The second creature also takes 2d4 Fire damage.\n"
            "Marid's Surge. The target of your Divine Smite and each creature of your choice in a 10-foot Emanation originating from you make a Strength saving throw against your spell save DC. On a failed save, a creature is pushed 15 feet straight away from you and has the Prone condition."
        )
        return description


class GenieSpells(TextFeature):
    def __init__(self):
        super().__init__(
            name="Genie Spells", origin="Oath of the Noble Genies Paladin Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you reach a Paladin level specified in the Genie Spells table, you thereafter always have the listed spells prepared\n"
            "Genie Spells\n"
            "Paladin Level	Spells\n"
            "3	Chromatic Orb, Elementalism, Thunderous Smite\n"
            "5	Mirror Image, Phantasmal Force\n"
            "9	Fly, Gaseous Form\n"
            "13	Conjure Minor Elementals, Summon Elemental\n"
            "17	Banishing Smite, Contact Other Plane"
        )
        return description


class GeniesSplendor(TextFeature):
    def __init__(self):
        super().__init__(
            name="Genie's Splendor", origin="Oath of the Noble Genies Paladin Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you aren't wearing any armor, your base Armor Class equals 10 plus your Dexterity and Charisma modifiers. You can use a Shield and still gain this benefit.\n"
            "You also gain proficiency in one of the following skills of your choice: Acrobatics, Intimidation, Performance, or Persuasion."
        )
        return description


class AuraOfElementalShielding(TextFeature):
    def __init__(self):
        super().__init__(
            name="Aura of Elemental Shielding",
            origin="Oath of the Noble Genies Paladin Level 7",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Choose one of the following damage types: Acid, Cold, Fire, Lightning, or Thunder. You and your allies have Resistance to that damage type while in your Aura of Protection.\n"
            "At the start of each of your turns, you can change the damage type affected by this feature to one of the other listed options (no action required)."
        )
        return description


class ElementalRebuke(TextFeature):
    def __init__(self):
        super().__init__(
            name="Elemental Rebuke", origin="Oath of the Noble Genies Paladin Level 15"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you are hit by an attack roll, you can take a Reaction to halve the attack's damage against yourself (round down) and force the attacker to make a Dexterity saving throw against your spell save DC. On a failed save, the attacker takes damage equal to 2d10 plus your Charisma modifier of one of the following types (your choice): Acid, Cold, Fire, Lightning, or Thunder. On a successful save, the attacker takes half as much damage.\n"
            "You can use this feature a number of times equal to your Charisma modifier (minimum of once), and you regain all expended uses when you finish a Long Rest."
        )
        return description


class NobleScion(TextFeature):
    def __init__(self):
        super().__init__(
            name="Noble Scion", origin="Oath of the Noble Genies Paladin Level 20"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "As a Bonus Action, you gain the benefits below for 10 minutes or until you end them (no action required). Once you use this feature, you can't use it again until you finish a Long Rest. You can also restore your use of it by expending a level 5 spell slot (no action required).\n"
            "Flight. You have a Fly Speed of 60 feet and can hover.\n"
            "Minor Wish. When you or an ally in your Aura of Protection fails a D20 Test, you can take a Reaction to make you or that ally succeed instead."
        )
        return description
