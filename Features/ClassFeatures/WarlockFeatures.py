from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Definitions import Ability, DiceRollCondition, Skill
from Features.BaseFeatures import CharacterFeature, TextFeature


WARLOCK_HIT_DIE = 8


class MagicalCunning(TextFeature):
    def __init__(self):
        super().__init__(name="Magical Cunning", origin="Warlock Level 2")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can perform an esoteric rite for 1 minute. At the end of it, you regain expended Pact Magic spell slots but no more than a number equal to half your maximum (round up). Once you use this feature, you can't do so again until you finish a Long Rest."
        return description


class ContactPatron(TextFeature):
    def __init__(self):
        super().__init__(name="Contact Patron", origin="Warlock Level 9")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "In the past, you usually contacted your patron through intermediaries. Now you can communicate directly; you always have the Contact Other Plane spell prepared. With this feature, you can cast the spell without expending a spell slot to contact your patron, and you automatically succeed on the spell's saving throw.\n"
            "Once you cast the spell with this feature, you can't do so in this way again until you finish a Long Rest."
        )
        return description


class MysticArcanum(TextFeature):
    def __init__(self):
        super().__init__(name="Mystic Arcanum", origin="Warlock Level 11")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your patron grants you a magical secret called an arcanum. Choose one level 6 Warlock spell as this arcanum.\n"
            "You can cast your arcanum spell once without expending a spell slot, and you must finish a Long Rest before you can cast it in this way again.\n"
            "As shown in the Warlock Features table, you gain another Warlock spell of your choice that can be cast in this way when you reach Warlock levels 13 (level 7 spell), 15 (level 8 spell), and 17 (level 9 spell). You regain all uses of your Mystic Arcanum when you finish a Long Rest.\n"
            "Whenever you gain a Warlock level, you can replace one of your arcanum spells with another Warlock spell of the same level."
        )
        return description


class EldritchMaster(TextFeature):
    def __init__(self):
        super().__init__(name="Eldritch Master", origin="Warlock Level 20")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you use your Magical Cunning feature, you regain all your expended Pact Magic spell slots."
        return description


### Archfey Patron Features ###


class ArchfeySpells(TextFeature):
    def __init__(self):
        super().__init__(name="Archfey Spells", origin="Archfey Patron Warlock Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "The magic of your patron ensures you always have certain spells ready; when you reach a Warlock level specified in the Archfey Spells table, you thereafter always have the listed spells prepared."
        return description


class StepsOfTheFey(TextFeature):
    def __init__(self):
        super().__init__(
            name="Steps of the Fey", origin="Archfey Patron Warlock Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your patron grants you the ability to move between the boundaries of the planes. You can cast Misty Step without expending a spell slot a number of times equal to your Charisma modifier (minimum of once), and you regain all expended uses when you finish a Long Rest.\n"
            "In addition, whenever you cast that spell, you can choose one of the following additional effects.\n"
            "Refreshing Step. Immediately after you teleport, you or one creature you can see within 10 feet of yourself gains 1d10 Temporary Hit Points.\n"
            "Taunting Step. Creatures within 5 feet of the space you left must succeed on a Wisdom saving throw against your spell save DC or have Disadvantage on attack rolls against creatures other than you until the start of your next turn."
        )
        return description


class MistyEscape(TextFeature):
    def __init__(self):
        super().__init__(name="Misty Escape", origin="Archfey Patron Warlock Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can cast Misty Step as a Reaction in response to taking damage.\n"
            "In addition, the following effects are now among your Steps of the Fey options.\n"
            "Disappearing Step. You have the Invisible condition until the start of your next turn or until immediately after you make an attack roll, deal damage, or cast a spell.\n"
            "Dreadful Step. Creatures within 5 feet of the space you left or the space you appear in (your choice) must succeed on a Wisdom saving throw against your spell save DC or take 2d10 Psychic damage."
        )
        return description


class BeguilingDefenses(TextFeature):
    def __init__(self):
        super().__init__(
            name="Beguiling Defenses", origin="Archfey Patron Warlock Level 10"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your patron teaches you how to guard your mind and body. You are immune to the Charmed condition.\n"
            "In addition, immediately after a creature you can see hits you with an attack roll, you can take a Reaction to reduce the damage you take by half (round down), and you can force the attacker to make a Wisdom saving throw against your spell save DC. On a failed save, the attacker takes Psychic damage equal to the damage you take. Once you use this Reaction, you can't use it again until you finish a Long Rest unless you expend a Pact Magic spell slot (no action required) to restore your use of it."
        )
        return description


class BewitchingMagic(TextFeature):
    def __init__(self):
        super().__init__(
            name="Bewitching Magic", origin="Archfey Patron Warlock Level 14"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Your patron grants you the ability to weave your magic with teleportation. Immediately after you cast an Enchantment or Illusion spell using an action and a spell slot, you can cast Misty Step as part of the same action and without expending a spell slot."
        return description


### Celestial Patron Features ###


class HealingLight(TextFeature):
    def __init__(self):
        super().__init__(
            name="Healing Light", origin="Celestial Patron Warlock Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain the ability to channel celestial energy to heal wounds. You have a pool of d6s to fuel this healing. The number of dice in the pool equals 1 plus your Warlock level.\n"
            "As a Bonus Action, you can heal yourself or one creature you can see within 60 feet of yourself, expending dice from the pool. The maximum number of dice you can expend at once equals your Charisma modifier (minimum of one die). Roll the dice you expend, and restore a number of Hit Points equal to the roll's total. Your pool regains all expended dice when you finish a Long Rest."
        )
        return description


class RadiantSoul(TextFeature):
    def __init__(self):
        super().__init__(name="Radiant Soul", origin="Celestial Patron Warlock Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Your link to your patron allows you to serve as a conduit for radiant energy. You have Resistance to Radiant damage. Once per turn, when a spell you cast deals Radiant or Fire damage, you can add your Charisma modifier to that spell's damage against one of the spell's targets."
        return description


class CelestialResilience(TextFeature):
    def __init__(self):
        super().__init__(
            name="Celestial Resilience", origin="Celestial Patron Warlock Level 10"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You gain Temporary Hit Points whenever you use your Magical Cunning feature or finish a Short or Long Rest. These Temporary Hit Points equal your Warlock level plus your Charisma modifier. Additionally, choose up to five creatures you can see when you gain the points. Those creatures each gain Temporary Hit Points equal to half your Warlock level plus your Charisma modifier."
        return description


class SearingVengeance(TextFeature):
    def __init__(self):
        super().__init__(
            name="Searing Vengeance", origin="Celestial Patron Warlock Level 14"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you or an ally within 60 feet of you is about to make a Death Saving Throw, you can unleash radiant energy to save the creature. The creature regains Hit Points equal to half its Hit Point maximum and can end the Prone condition on itself. Each creature of your choice that is within 30 feet of the creature takes Radiant damage equal to 2d8 plus your Charisma modifier, and each has the Blinded condition until the end of the current turn.\n"
            "Once you use this feature, you can't use it again until you finish a Long Rest."
        )
        return description


### Fiend Patron Features ###


class DarkOnesBlessing(TextFeature):
    def __init__(self):
        super().__init__(
            name="Dark One's Blessing", origin="Fiend Patron Warlock Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you reduce an enemy to 0 Hit Points, you gain Temporary Hit Points equal to your Charisma modifier plus your Warlock level (minimum of 1 Temporary Hit Point). You also gain this benefit if someone else reduces an enemy within 10 feet of you to 0 Hit Points."
        return description


class DarkOnesOwnLuck(TextFeature):
    def __init__(self):
        super().__init__(
            name="Dark One's Own Luck", origin="Fiend Patron Warlock Level 6"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can call on your fiendish patron to alter fate in your favor. When you make an ability check or a saving throw, you can use this feature to add 1d10 to your roll. You can do so after seeing the roll but before any of the roll's effects occur.\n"
            "You can use this feature a number of times equal to your Charisma modifier (minimum of once), but you can use it no more than once per roll. You regain all expended uses when you finish a Long Rest."
        )
        return description


class FiendishResilience(TextFeature):
    def __init__(self):
        super().__init__(
            name="Fiendish Resilience", origin="Fiend Patron Warlock Level 10"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Choose one damage type, other than Force, whenever you finish a Short or Long Rest. You have Resistance to that damage type until you choose a different one with this feature."
        return description


class HurlThroughHell(TextFeature):
    def __init__(self):
        super().__init__(
            name="Hurl Through Hell", origin="Fiend Patron Warlock Level 14"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Once per turn when you hit a creature with an attack roll, you can try to instantly transport the target through the Lower Planes. The target must succeed on a Charisma saving throw against your spell save DC, or the target disappears and hurtles through a nightmare landscape. The target takes 8d10 Psychic damage if it isn't a Fiend, and it has the Incapacitated condition until the end of your next turn, when it returns to the space it previously occupied or the nearest unoccupied space.\n"
            "Once you use this feature, you can't use it again until you finish a Long Rest unless you expend a Pact Magic spell slot (no action required) to restore your use of it."
        )
        return description


### Great Old One Patron Features ###


class AwakenedMind(TextFeature):
    def __init__(self):
        super().__init__(
            name="Awakened Mind", origin="Great Old One Patron Warlock Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can form a telepathic connection between your mind and the mind of another. As a Bonus Action, choose one creature you can see within 30 feet of yourself. You and the chosen creature can communicate telepathically with each other while the two of you are within a number of miles of each other equal to your Charisma modifier (minimum of 1 mile). To understand each other, you each must mentally use a language the other knows.\n"
            "The telepathic connection lasts for a number of minutes equal to your Warlock level. It ends early if you use this feature to connect with a different creature."
        )
        return description


class PsychicSpells(TextFeature):
    def __init__(self):
        super().__init__(
            name="Psychic Spells", origin="Great Old One Patron Warlock Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you cast a Warlock spell that deals damage, you can change its damage type to Psychic. In addition, when you cast a Warlock spell that is an Enchantment or Illusion, you can do so without Verbal or Somatic components."
        return description


class ClairvoyantCombatant(TextFeature):
    def __init__(self):
        super().__init__(
            name="Clairvoyant Combatant", origin="Great Old One Patron Warlock Level 6"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you form a telepathic bond with a creature using your Awakened Mind, you can force that creature to make a Wisdom saving throw against your spell save DC. On a failed save, the creature has Disadvantage on attack rolls against you, and you have Advantage on attack rolls against that creature for the duration of the bond.\n"
            "Once you use this feature, you can't use it again until you finish a Short or Long Rest unless you expend a Pact Magic spell slot (no action required) to restore your use of it."
        )
        return description


class EldritchHex(TextFeature):
    def __init__(self):
        super().__init__(
            name="Eldritch Hex", origin="Great Old One Patron Warlock Level 10"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Your alien patron grants you a powerful curse. You always have the Hex spell prepared. When you cast Hex and choose an ability, the target also has Disadvantage on saving throws of the chosen ability for the duration of the spell."
        return description


class ThoughtShield(TextFeature):
    def __init__(self):
        super().__init__(
            name="Thought Shield", origin="Great Old One Patron Warlock Level 10"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Your thoughts can't be read by telepathy or other means unless you allow it. You also have Resistance to Psychic damage, and whenever a creature deals Psychic damage to you, that creature takes the same amount of damage that you take."
        return description


class CreateThrall(TextFeature):
    def __init__(self):
        super().__init__(
            name="Create Thrall", origin="Great Old One Patron Warlock Level 14"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you cast Summon Aberration, you can modify it so that it doesn't require Concentration. If you do so, the spell's duration becomes 1 minute for that casting, and when summoned, the Aberration has a number of Temporary Hit Points equal to your Warlock level plus your Charisma modifier.\n"
            "In addition, the first time each turn the Aberration hits a creature under the effect of your Hex, the Aberration deals extra Psychic damage to the target equal to the bonus damage of that spell."
        )
        return description
