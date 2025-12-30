from Features.BaseFeatures import TextFeature
from StatBlocks.CharacterStatBlock import CharacterStatBlock

BARD_HIT_DIE = 8


class BardicInspiration(TextFeature):
    def __init__(self):
        super().__init__(name="Bardic Inspiration", origin="Bard Level 1")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can supernaturally inspire others through words, music, or dance. This inspiration is represented by your Bardic Inspiration die, which is a d6.\n"
            "Using Bardic Inspiration. As a Bonus Action, you can inspire another creature within 60 feet of yourself who can see or hear you. That creature gains one of your Bardic Inspiration dice. A creature can have only one Bardic Inspiration die at a time.\n"
            "Once within the next hour when the creature fails a D20 Test, the creature can roll the Bardic Inspiration die and add the number rolled to the d20, potentially turning the failure into a success. A Bardic Inspiration die is expended when it's rolled.\n"
            "Number of Uses. You can confer a Bardic Inspiration die a number of times equal to your Charisma modifier (minimum of once), and you regain all expended uses when you finish a Long Rest.\n"
            "At Higher Levels. Your Bardic Inspiration die changes when you reach certain Bard levels, as shown in the Bardic Die column of the Bard Features table. The die becomes a d8 at level 5, a d10 at level 10, and a d12 at level 15."
        )
        return description


class Expertise(TextFeature):
    def __init__(self):
        super().__init__(name="Expertise", origin="Bard Level 2")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain Expertise (see the rules glossary) in two of your skill proficiencies of your choice. Performance and Persuasion are recommended if you have proficiency in them.\n"
            "At Bard level 9, you gain Expertise in two more of your skill proficiencies of your choice."
        )
        return description


class JackofallTrades(TextFeature):
    def __init__(self):
        super().__init__(name="Jack of all Trades", origin="Bard Level 2")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can add half your Proficiency Bonus (round down) to any ability check you make that uses a skill proficiency you lack and that doesn't otherwise use your Proficiency Bonus.\n"
            "For example, if you make a Strength (Athletics) check and lack Athletics proficiency, you can add half your Proficiency Bonus to the check."
        )
        return description


class FontofInspiration(TextFeature):
    def __init__(self):
        super().__init__(name="Font of Inspiration", origin="Bard Level 5")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You now regain all your expended uses of Bardic Inspiration when you finish a Short or Long Rest.\n"
            "In addition, you can expend a spell slot (no action required) to regain one expended use of Bardic Inspiration."
        )
        return description


class Countercharm(TextFeature):
    def __init__(self):
        super().__init__(name="Countercharm", origin="Bard Level 7")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can use musical notes or words of power to disrupt mind-influencing effects. If you or a creature within 30 feet of you fails a saving throw against an effect that applies the Charmed or Frightened condition, you can take a Reaction to cause the save to be rerolled, and the new roll has Advantage."
        return description


class MagicalSecrets(TextFeature):
    def __init__(self):
        super().__init__(name="Magical Secrets", origin="Bard Level 10")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You've learned secrets from various magical traditions. Whenever you reach a Bard level (including this level) and the Prepared Spells number in the Bard Features table increases, you can choose any of your new prepared spells from the Bard, Cleric, Druid, and Wizard spell lists, and the chosen spells count as Bard spells for you (see a class's section for its spell list). In addition, whenever you replace a spell prepared for this class, you can replace it with a spell from those lists."
        return description


class SuperiorInspiration(TextFeature):
    def __init__(self):
        super().__init__(name="Superior Inspiration", origin="Bard Level 18")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you roll Initiative, you regain expended uses of Bardic Inspiration until you have two if you have fewer than that."
        return description


class WordsofCreation(TextFeature):
    def __init__(self):
        super().__init__(name="Words of Creation", origin="Bard Level 20")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You have mastered two of the Words of Creation: the words of life and death. You therefore always have the Power Word: Heal and Power Word: Kill spells prepared. When you cast either spell, you can target a second creature with it if that creature is within 10 feet of the first target."
        return description


### College of Dance Bard Features ###


class DazzlingFootwork(TextFeature):
    def __init__(self):
        super().__init__(
            name="Dazzling Footwork", origin="College of Dance Bard Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "While you aren't wearing armor or wielding a Shield, you gain the following benefits.\n"
            "Dance Virtuoso. You have Advantage on any Charisma (Performance) check you make that involves you dancing.\n"
            "Unarmored Defense. Your base Armor Class equals 10 plus your Dexterity and Charisma modifiers.\n"
            "Agile Strikes. When you expend a use of your Bardic Inspiration as part of an action, a Bonus Action, or a Reaction, you can make one Unarmed Strike as part of that action, Bonus Action, or Reaction.\n"
            "Bardic Damage. You can use Dexterity instead of Strength for the attack rolls of your Unarmed Strikes. When you deal damage with an Unarmed Strike, you can deal Bludgeoning damage equal to a roll of your Bardic Inspiration die plus your Dexterity modifier, instead of the strike's normal damage. This roll doesn't expend the die."
        )
        return description


class InspiringMovement(TextFeature):
    def __init__(self):
        super().__init__(
            name="Inspiring Movement", origin="College of Dance Bard Level 6"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When an enemy you can see ends its turn within 5 feet of you, you can take a Reaction and expend one use of your Bardic Inspiration to move up to half your Speed. Then one ally of your choice within 30 feet of you can also move up to half their Speed using their Reaction.\n"
            "None of this feature's movement provokes Opportunity Attacks."
        )
        return description


class TandemFootwork(TextFeature):
    def __init__(self):
        super().__init__(name="Tandem Footwork", origin="College of Dance Bard Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you roll Initiative, you can expend one use of your Bardic Inspiration if you don't have the Incapacitated condition. When you do so, roll your Bardic Inspiration die; you and each ally within 30 feet of you who can see or hear you gains a bonus to Initiative equal to the number rolled."
        return description


class LeadingEvasion(TextFeature):
    def __init__(self):
        super().__init__(
            name="Leading Evasion", origin="College of Dance Bard Level 14"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you are subjected to an effect that allows you to make a Dexterity saving throw to take only half damage, you instead take no damage if you succeed on the saving throw and only half damage if you fail. If any creatures within 5 feet of you are making the same Dexterity saving throw, you can share this benefit with them for that save.\n"
            "You can't use this feature if you have the Incapacitated condition."
        )
        return description


### College of Glamour Bard Features ###


class BeguilingMagic(TextFeature):
    def __init__(self):
        super().__init__(
            name="Beguiling Magic", origin="College of Glamour Bard Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You always have the Charm Person and Mirror Image spells prepared.\n"
            "In addition, immediately after you cast an Enchantment or Illusion spell using a spell slot, you can cause a creature you can see within 60 feet of yourself to make a Wisdom saving throw against your spell save DC. On a failed save, the target has the Charmed or Frightened condition (your choice) for 1 minute. The target repeats the save at the end of each of its turns, ending the effect on itself on a success.\n"
            "Once you use this benefit, you can't use it again until you finish a Long Rest. You can also restore your use of it by expending one use of your Bardic Inspiration (no action required)."
        )
        return description


class MantleofInspiration(TextFeature):
    def __init__(self):
        super().__init__(
            name="Mantle of Inspiration", origin="College of Glamour Bard Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can weave fey magic into a song or dance to fill others with vigor. As a Bonus Action, you can expend a use of Bardic Inspiration, rolling a Bardic Inspiration die. When you do so, choose a number of other creatures within 60 feet of yourself, up to a number equal to your Charisma modifier (minimum of one creature). Each of those creatures gains a number of Temporary Hit Points equal to two times the number rolled on the Bardic Inspiration die, and then each can use its Reaction to move up to its Speed without provoking Opportunity Attacks."
        return description


class MantleofMajesty(TextFeature):
    def __init__(self):
        super().__init__(
            name="Mantle of Majesty", origin="College of Glamour Bard Level 6"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You always have the Command spell prepared.\n"
            "As a Bonus Action, you cast Command without expending a spell slot, and you take on an unearthly appearance for 1 minute or until your Concentration ends. During this time, you can cast Command as a Bonus Action without expending a spell slot,\n"
            "Any creature Charmed by you automatically fails its saving throw against the Command you cast with this feature.\n"
            "Once you use this feature, you can't use it again until you finish a Long Rest. You can also restore your use of it by expending a level 3+ spell slot (no action required)."
        )
        return description


class UnbreakableMajesty(TextFeature):
    def __init__(self):
        super().__init__(
            name="Unbreakable Majesty", origin="College of Glamour Bard Level 14"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "As a Bonus Action, you can assume a magically majestic presence for 1 minute or until you have the Incapacitated condition. For the duration, whenever any creature hits you with an attack roll for the first time on a turn, the attacker must succeed on a Charisma saving throw against your spell save DC, or the attack misses instead, as the creature recoils from your majesty.\n"
            "Once you assume this majestic presence, you can't do so again until you finish a Short or Long Rest."
        )
        return description


### College of Lore Bard Features ###


class BonusProficiencies(TextFeature):
    def __init__(self):
        super().__init__(
            name="Bonus Proficiencies", origin="College of Lore Bard Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You gain proficiency with three skills of your choice."
        return description


class CuttingWords(TextFeature):
    def __init__(self):
        super().__init__(name="Cutting Words", origin="College of Lore Bard Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You learn to use your wit to supernaturally distract, confuse, and otherwise sap the confidence and competence of others. When a creature that you can see within 60 feet of yourself makes a damage roll or succeeds on an ability check or attack roll, you can take a Reaction to expend one use of your Bardic Inspiration; roll your Bardic Inspiration die, and subtract the number rolled from the creature's roll, reducing the damage or potentially turning the success into a failure."
        return description


class MagicalDiscoveries(TextFeature):
    def __init__(self):
        super().__init__(
            name="Magical Discoveries", origin="College of Lore Bard Level 6"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You learn two spells of your choice. These spells can come from the Cleric, Druid, or Wizard spell list or any combination thereof (see a class's section for its spell list). A spell you choose must be a cantrip or a spell for which you have spell slots, as shown in the Bard Features table.\n"
            "You always have the chosen spells prepared, and whenever you gain a Bard level, you can replace one of the spells with another spell that meets these requirements."
        )
        return description


class PeerlessSkill(TextFeature):
    def __init__(self):
        super().__init__(name="Peerless Skill", origin="College of Lore Bard Level 14")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you make an ability check or attack roll and fail, you can expend one use of Bardic Inspiration; roll the Bardic Inspiration die, and add the number rolled to the d20, potentially turning a failure into a success. On a failure, the Bardic Inspiration isn't expended"
        return description


### College of the Moon Bard Features ###


class MoonsInspiration(TextFeature):
    def __init__(self):
        super().__init__(
            name="Moon's Inspiration", origin="College of the Moon Bard Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "The primal and ever-changing power of the moon flows through you, granting you the following benefits.\n"
            "Inspired Eclipse. When you take a Bonus Action to give a creature a Bardic Inspiration die, you can have the Invisible condition and teleport up to 30 feet to an unoccupied space you can see as part of that Bonus Action. This invisibility lasts until the start of your next turn and ends early immediately after you make an attack roll, deal damage, or cast a spell.\n"
            "Lunar Vitality. Once per turn when you restore Hit Points to a creature with a spell, you can expend a Bardic Inspiration die and increase the amount of Hit Points restored by a number equal to a roll of the Bardic Inspiration die. The creature's Speed also increases by 10 feet until the end of its next turn."
        )
        return description


class PrimalLore(TextFeature):
    def __init__(self):
        super().__init__(name="Primal Lore", origin="College of the Moon Bard Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You learn Druidic and one cantrip from the Druid spell list. It counts as a Bard spell for you but doesn't count against the number of cantrips you know. Whenever you gain a Bard level, you can replace this cantrip with another cantrip of your choice from the Druid spell list.\n"
            "Additionally, choose one of the following skills: Animal Handling, Insight, Medicine, Nature, Perception, or Survival. You have proficiency in that skill."
        )
        return description


class BlessingofMoonlight(TextFeature):
    def __init__(self):
        super().__init__(
            name="Blessing of Moonlight", origin="College of the Moon Bard Level 6"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You always have the Moonbeam spell prepared.\n"
            "When you cast Moonbeam, you can modify the spell so that you glow faintly while the spell is active. While glowing, you shed Dim Light out to 5 feet, and whenever a creature fails its saving throw against the effects of this Moonbeam, another creature of your choice that you can see within 60 feet of yourself regains 2d4 Hit Points.\n"
            "Once you use this feature to modify a casting of Moonbeam, you can't use it again until you finish a Long Rest."
        )
        return description


class EventidesSplendor(TextFeature):
    def __init__(self):
        super().__init__(
            name="Eventide's Splendor", origin="College of the Moon Bard Level 14"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You become suffused with the might of the moon, improving your Moon's Inspiration in the following ways.\n"
            "Shadow of the New Moon. When you use Inspired Eclipse, the creature who received the Bardic Inspiration die can also have the Invisible condition and immediately take a Reaction to teleport up to 30 feet to an unoccupied space it can see. The creature remains Invisible until the start of its next turn.\n"
            "Vibrance of the Full Moon. When you use Lunar Vitality, you can roll 1d6 and use the number rolled in place of expending a Bardic Inspiration die."
        )
        return description


### College of Valor Bard Features ###


class CombatInspiration(TextFeature):
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


class MartialTraining(TextFeature):
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


class ExtraAttack(TextFeature):
    def __init__(self):
        super().__init__(name="Extra Attack", origin="College of Valor Bard Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can attack twice instead of once whenever you take the Attack action on your turn.\n"
            "In addition, you can cast one of your cantrips that has a casting time of an action in place of one of those attacks."
        )
        return description


class BattleMagic(TextFeature):
    def __init__(self):
        super().__init__(name="Battle Magic", origin="College of Valor Bard Level 14")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "After you cast a spell that has a casting time of an action, you can make one attack with a weapon as a Bonus Action."
        return description
