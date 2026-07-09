from Definitions import Ability, CharacterClass, Skill
from Features.Core.BaseFeatures import Feature
from Features.Core.SubFeatures import SavingThrowProficiencyChoice, SkillExpertiseChoice
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils

ROGUE_HIT_DIE = 8


class Expertise(Feature):
    def __init__(self, skill_1: Skill, skill_2: Skill):
        super().__init__()
        self._choice = SkillExpertiseChoice(
            [skill_1, skill_2], list(Skill), count=2, error_prefix="Rogue Expertise"
        )

    def apply(self, character_stat_block: CharacterStatBlock):
        self._choice.apply(character_stat_block)


class SneakAttack(Feature):
    def __init__(self):
        super().__init__(name="Sneak Attack", origin="Rogue Level 1")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You know how to strike subtly and exploit a foe's distraction. Once per turn you can deal an extra 1d6 damage to one creature you hit with an attack roll if you have Advantage on the roll and the attack uses a Finesse or a Ranged weapon. The extra damage's type is the same was the weapon's type.\n"
            "You don't need Advantage on the attack roll if at least one of your allies is within 5 feet of the target, the ally doesn't have the Incapacitated condition and you don't have Disadvantage on the attack roll.\n"
            "The extra damage increases as you gain Rogue levels, as shown in the Sneak Attack column of the Rogue Features table."
        )
        return description


class ThievesCant(Feature):
    def __init__(self):
        super().__init__(name="Thieves' Cant", origin="Rogue Level 1")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You picked up various languages in the communities where you plied your roguish talents. You know Thieves' Cant and one other language of your choice, which you choose from the language tables in Chapter 2."
        return description


class WeaponMastery(Feature):
    def __init__(self):
        super().__init__(name="Weapon Mastery", origin="Rogue Level 1")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your training with weapons allows you to use the mastery properties of two kinds of weapons of your choice with which you have proficiency, such as Daggers and Shortbows.\n"
            "Whenever you finish a Long Rest, you can change the kinds of weapons you chose. For example, you could switch to using the mastery properties of Scimitars and Shortswords."
        )
        return description


class CunningAction(Feature):
    def __init__(self):
        super().__init__(name="Cunning Action", origin="Rogue Level 2")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Your quick thinking and agility allow you to move and act quickly. On your turn, you can take one of the following actions as a Bonus Action: Dash, Disengage, or Hide."
        return description


class SteadyAim(Feature):
    def __init__(self):
        super().__init__(name="Steady Aim", origin="Rogue Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "As a Bonus Action, you give yourself Advantage on your next attack roll on your current turn. You can use this feature only if you haven't moved during this turn, and after you use it, your Speed is 0 until the end of the current turn."
        return description


class CunningStrike(Feature):
    def __init__(self):
        super().__init__(name="Cunning Strike", origin="Rogue Level 5")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        saving_throw = (
            8
            + character_stat_block.get_ability_modifier(Ability.DEXTERITY)
            + character_stat_block.get_proficiency_bonus()
        )
        description = (
            "You've developed cunning ways to use your Sneak Attack. When you deal Sneak Attack damage, you can add one of the following Cunning Strike effects. Each effect has a die cost, which is the number of Sneak Attack dice you must forgo to add the effect. You remove the die before rolling, and the effect occurs immediately after the attack's damage is dealt. For example, if you add the Poison effect, remove 1d6 from the Sneak Attack's damage before rolling.\n"
            f"If a Cunning Strike requires a saving throw, the DC equals 8 plus your Dexterity modifier and Proficiency Bonus ({saving_throw}).\n"
            "    * Poison (Cost: 1d6). You add a toxin to your strike, forcing the target to make a Constitution saving throw. On a failed save, the target has the Poisoned condition for 1 minute. At the end of each of its turns, the poisoned target repeats the save, ending the effect on a success.\n"
            "   To use this effect, you must have a Poisoner's Kit on your person.\n"
            "    * Trip (Cost: 1d6). If the target is Large or smaller, it must succeed on a Dexterity saving throw or have the Prone condition.\n"
            "    * Withdraw (Cost: 1d6). Immediately after the attack, you move up to half your speed without provoking Opportunity Attacks."
        )
        return description


class UncannyDodge(Feature):
    def __init__(self):
        super().__init__(name="Uncanny Dodge", origin="Rogue Level 5")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When an attacker that you can see hits you with an attack roll, you can take a Reaction to halve the attack's damage against you (round down)."
        return description


class Evasion(Feature):
    def __init__(self):
        super().__init__(name="Evasion", origin="Rogue Level 7")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can nimbly dodge out of the way of certain dangers. When you're subjected to an effect that allows you to make a Dexterity saving throw to take only half damage, you instead take no damage if you succeed on the saving throw and only half damage if you fail. You can't use this feature if you have the Incapacitated condition."
        return description


class ReliableTalent(Feature):
    def __init__(self):
        super().__init__(name="Reliable Talent", origin="Rogue Level 7")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Whenever you make an ability check that uses one of your skill or tool proficiencies, you can treat a d20 roll of 9 or lower as a 10."
        return description


class ImprovedCunningStrike(Feature):
    def __init__(self):
        super().__init__(name="Improved Cunning Strike", origin="Rogue Level 11")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can use up to two Cunning Strike effects when you deal Sneak Attack damage, paying the die cost for each effect."
        return description


class DeviousStrikes(Feature):
    def __init__(self):
        super().__init__(name="Devious Strikes", origin="Rogue Level 14")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You've practiced new ways to use your Sneak Attack deviously. The following effects are now among your Cunning Strike options.\n"
            "Daze (Cost: 2d6). The target must succeed on a Constitution saving throw, or on its next turn, it can do only one of the following: move or take an action or a Bonus Action.\n"
            "Knock Out (Cost: 6d6). The target must succeed on a Constitution saving throw, or it has the Unconscious condition for 1 minute or until it takes any damage. The Unconscious target repeats the save at the end of its turns, ending the effect on itself on a success.\n"
            "Obscure (Cost: 3d6). The target must succeed on a Dexterity saving throw, or it has the Blinded condition until the end of its next turn."
        )
        return description


class SlipperyMind(Feature):
    def __init__(self):
        super().__init__(name="Slippery Mind", origin="Rogue Level 15")
        self._choice = SavingThrowProficiencyChoice(
            [Ability.WISDOM, Ability.CHARISMA], list(Ability), count=2,
            error_prefix="Slippery Mind"
        )

    def apply(self, character_stat_block: CharacterStatBlock):
        self._choice.apply(character_stat_block)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "Your mind is exceptionally difficult to control. You gain proficiency in Wisdom and Charisma saving throws."


class Elusive(Feature):
    def __init__(self):
        super().__init__(name="Elusive", origin="Rogue Level 18")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You're so evasive that attackers rarely gain the upper hand against you. No attack roll can have advantage against you unless you have the Incapacitated condition."
        return description


class StrokeOfLuck(Feature):
    def __init__(self):
        super().__init__(name="Stroke of Luck", origin="Rogue Level 20")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You have a marvelous knack for succeeding when you need to. If you fail a d20 Test, you can turn the roll into a 20.\n"
            "Once you use this feature, you can't use it again until you finish a Short or Long Rest."
        )
        return description


### Arcane Trickster Rogue Features ###


class Spellcasting(Feature):
    def __init__(self):
        super().__init__(name="Spellcasting", origin="Arcane Trickster Rogue Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You have learned to cast spells. See chapter 7 for the rules on spellcasting. The information below details how you use those rules as an Arcane Trickster.\n"
            "Cantrips. You know three cantrips: Mage Hand and two other cantrips of your choice from the Wizard spell list (see that class's section for its list). Mind Sliver and Minor Illusion are recommended.\n"
            "Whenever you gain a Rogue level, you can replace one of your cantrips, except Mage Hand, with another Wizard cantrip of your choice.\n"
            "When you reach Rogue level 10, you learn another Wizard cantrip of your choice.\n"
            "Spell Slots. The Arcane Trickster Spellcasting table shows how many spell slots you have to cast your level 1+ spells. You regain all expended spell slots when you finish a Long Rest.\n"
            "Prepared Spells of Level 1+. You prepare a list of the level 1+ spells that are available for you to cast with this feature. To start, choose three level 1 Wizard spells. Charm Person, Disguise Self and Fog Cloud are recommended.\n"
            "The number of spells on your list increases as you gain Rogue levels, as shown in the Prepared Spells column of the Arcane Trickster Spellcasting table. Whenever that number increases, choose additional Wizard spells until the number of spells on your list matches the number in the Arcane Trickster Spellcasting table. The chosen spells must be of a level for which you have spell slots. For example, if you're a level 7 Rogue, your list of prepared spells can include five Wizard spells of level 1 or 2 in any combination.\n"
            "Changing Your Prepared Spells. Whenever you gain a Rogue level, you can replace one spell on your list with another Wizard spell for which you have spell slots.\n"
            "Spellcasting Ability. Intelligence is your spellcasting ability for your Wizard spells.\n"
            "Spellcasting Focus. You can use an Arcane Focus as a Spellcasting Focus for your Wizard spells.\n"
            "Restriction. Aside from Mage Hand, the spells you choose for this feature must be Enchantment or Illusion spells, unless they are among a short list of exceptions such as Alarm, Detect Magic, Feather Fall, Find Familiar and Knock.\n"
            "Arcane Trickster Spellcasting\n"
            "Rogue Level	Prepared Spells	1st	2nd	3rd	4th\n"
            "3	3	2	-	-	-\n"
            "4	4	3	-	-	-\n"
            "5	4	3	-	-	-\n"
            "6	4	3	-	-	-\n"
            "7	5	4	2	-	-\n"
            "8	6	4	2	-	-\n"
            "9	6	4	2	-	-\n"
            "10	7	4	3	-	-\n"
            "11	8	4	3	-	-\n"
            "12	8	4	3	-	-\n"
            "13	9	4	3	2	-\n"
            "14	10	4	3	2	-\n"
            "15	10	4	3	2	-\n"
            "16	11	4	3	3	-\n"
            "17	11	4	3	3	-\n"
            "18	11	4	3	3	-\n"
            "19	12	4	3	3	1\n"
            "20	13	4	3	3	1"
        )
        return description


class MageHandLegerdemain(Feature):
    def __init__(self):
        super().__init__(
            name="Mage Hand Legerdemain", origin="Arcane Trickster Rogue Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you cast Mage Hand, you can cast it as a Bonus Action, and you can make the spectral hand Invisible. You can control the hand as a Bonus Action, and through it, you can make Dexterity (Sleight of Hand) checks."
        return description


class MagicalAmbush(Feature):
    def __init__(self):
        super().__init__(name="Magical Ambush", origin="Arcane Trickster Rogue Level 9")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "If you have the Invisible condition when you cast a spell on a creature, it has Disadvantage on any saving throw it makes against the spell on the same turn."
        return description


class VersatileTrickster(Feature):
    def __init__(self):
        super().__init__(
            name="Versatile Trickster", origin="Arcane Trickster Rogue Level 13"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You gain the ability to distract targets with your Mage Hand. When you use the Trip option of your Cunning Strike on a creature, you can also use that option on another creature within 5 feet of the spectral hand."
        return description


class SpellThief(Feature):
    def __init__(self):
        super().__init__(name="Spell Thief", origin="Arcane Trickster Rogue Level 17")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain the ability to magically steal the knowledge of how to cast a spell from another spellcaster.\n"
            "Immediately after a creature casts a spell that targets you or includes you in its area of effect, you can take a Reaction to force the creature to make an Intelligence saving throw. The DC equals your spell save DC. On a failed save, you negate the spell's effect against you, and you steal the knowledge of the spell if it is at least level 1 and of a level you can cast (it doesn't need to be a Wizard spell). For the next 8 hours, you have the spell prepared. The creature can't cast it until 8 hours have passed.\n"
            "Once you steal a spell with this feature, you can't use this feature again until you finish a Long Rest."
        )
        return description


### Assassin Rogue Features ###


class Assassinate(Feature):
    def __init__(self):
        super().__init__(name="Assassinate", origin="Assassin Rogue Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You're adept at ambushing a target, granting you the following benefits.\n"
            "Initiative. You have Advantage on Initiative rolls.\n"
            "Surprising Strikes. During the first round of each combat, you have Advantage on attack rolls against any creature that hasn't taken a turn. If your Sneak Attack hits any target during that round, the target takes extra damage of the weapon's type equal to your Rogue level."
        )
        return description


class AssassinsTools(Feature):
    def __init__(self):
        super().__init__(name="Assassin's Tools", origin="Assassin Rogue Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You gain a Disguise Kit and a Poisoner's Kit, and you have proficiency with them."
        return description


class InfiltrationExpertise(Feature):
    def __init__(self):
        super().__init__(name="Infiltration Expertise", origin="Assassin Rogue Level 9")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You are an expert at the following techniques that aid your infiltrations.\n"
            "Masterful Mimicry. You can unerringly mimic another person's speech, handwriting or both if you have spent at least 1 hour studying them.\n"
            "Roving Aim. Your speed isn't reduced to 0 by using Steady Aim."
        )
        return description


class EnvenomWeapons(Feature):
    def __init__(self):
        super().__init__(name="Envenom Weapons", origin="Assassin Rogue Level 13")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you use the Poison option of your Cunning Strike, the target also takes 2d6 Poison damage whenever it fails the saving throw. This damage ignores Resistance to Poison damage."
        return description


class DeathStrike(Feature):
    def __init__(self):
        super().__init__(name="Death Strike", origin="Assassin Rogue Level 17")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you hit with your Sneak Attack on the first round of a combat, the target must succeed on a Constitution saving throw (DC 8 plus your Dexterity modifier and Proficiency Bonus), or the attack's damage is doubled against the target."
        return description


### Scion of the Three Rogue Features ###


class Bloodthirst(Feature):
    def __init__(self):
        super().__init__(name="Bloodthirst", origin="Scion of the Three Rogue Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        intelligence_modifier = character_stat_block.get_ability_modifier(
            Ability.INTELLIGENCE
        )
        uses = max(1, intelligence_modifier)
        description = "When an enemy you can see within 30 feet of yourself takes damage and is Bloodied after taking that damage but not killed outright, you can take a Reaction and teleport to an unoccupied space you can see within 5 feet of that enemy. You can then make one melee attack. You can use this feature a number of times equal to your Intelligence modifier (minimum of once), and you regain all expended uses when you finish a Long Rest."
        return StringUtils.add_boxes(description, uses, regain_all_on="long rest")


class DreadAllegiance(Feature):
    def __init__(self):
        super().__init__(
            name="Dread Allegiance", origin="Scion of the Three Rogue Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Choose one of the Dead Three: Bane, Bhaal, or Myrkul. You gain Resistance to one type of damage and the ability to cast a cantrip, as detailed in the table below; Intelligence is your spellcasting ability for this cantrip. When you finish a Long Rest, you can change your choice.\n"
            "God	Damage Resistance	Cantrip\n"
            "Bane	Psychic	Minor Illusion\n"
            "Bhaal	Poison	Blade Ward\n"
            "Myrkul	Necrotic	Chill Touch"
        )
        return description


class StrikeFear(Feature):
    def __init__(self):
        super().__init__(name="Strike Fear", origin="Scion of the Three Rogue Level 9")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain the following Cunning Strike option.\n"
            "Terrify (Cost: 1d6). The target must succeed on a Wisdom saving throw, or it has the Frightened condition for 1 minute. While the target is Frightened in this way, you have Advantage on attack rolls against the target.\n"
            "The Frightened target repeats the save at the end of each of its turns, ending the effect on itself on a success."
        )
        return description


class AuraofMalevolence(Feature):
    def __init__(self):
        super().__init__(
            name="Aura of Malevolence", origin="Scion of the Three Rogue Level 13"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You radiate malignant power associated with one of the Dead Three. When you use Bloodthirst and teleport, each creature of your choice within 10 feet of either the space you left or your destination space (your choice) takes damage equal to your Intelligence modifier; the damage type is the same as the damage Resistance granted by your choice in the Dread Allegiance feature. Damage dealt by this feature ignores Resistance."
        return description


class DreadIncarnate(Feature):
    def __init__(self):
        super().__init__(
            name="Dread Incarnate", origin="Scion of the Three Rogue Level 17"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain the following benefits.\n"
            "Cutthroat. You regain one expended use of Bloodthirst when you finish a Short Rest.\n"
            "Murderous Intent. When you roll for your Sneak Attack damage, you can treat a roll of a 1 or 2 on the die as a 3."
        )
        return description


### Soulknife Rogue Features ###


class PsionicPower(Feature):
    def __init__(self):
        super().__init__(name="Psionic Power", origin="Soulknife Rogue Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        rogue_level = character_stat_block.get_class_level(CharacterClass.ROGUE)

        if rogue_level < 5:
            die_size, number_of_dice = 6, 4
        elif rogue_level < 9:
            die_size, number_of_dice = 8, 6
        elif rogue_level < 11:
            die_size, number_of_dice = 8, 8
        elif rogue_level < 13:
            die_size, number_of_dice = 10, 8
        elif rogue_level < 17:
            die_size, number_of_dice = 10, 10
        else:
            die_size, number_of_dice = 12, 12

        description = (
            f"You harbor a wellspring of psionic energy within yourself. It is represented by your Psionic Energy Dice (currently d{die_size}s), which fuel certain powers you have from this subclass. The Soulknife Energy Dice table shows the number of these dice you have when you reach certain Rogue levels, and the table shows the die size.\n"
            "Soulknife Energy Dice\n"
            "Rogue Level	Die Size	Number\n"
            "3	D6	4\n"
            "5	D8	6\n"
            "9	D8	8\n"
            "11	D10	8\n"
            "13	D10	10\n"
            "17	D12	12\n"
            "Any features in this subclass that use a Psionic Energy Die use only the dice from this subclass. Some of your powers expend a Psionic Energy Die, as specified in the power's description, and you can't use the power if it requires you to use a die when your Psionic Energy Dice are all expended.\n"
            "You regain one of your expended Psionic Energy Dice when you finish a Short Rest, and you regain all of them when you finish a Long Rest.\n"
            "Psi-Bolstered Knack. If you fail an ability check using a skill or tool with which you have proficiency, you can roll one Psionic Energy Die and add the number rolled to the check, potentially turning failure into success. The die is expended only if the roll then succeeds.\n"
            "Psychic Whispers. You can establish telepathic communication between yourself and others. As a Magic action, choose one or more creatures you can see, up to a number of creatures equal to your Proficiency Bonus, and then roll one Psionic Energy Die. For a number of hours equal to the number rolled, the chosen creatures can speak telepathically to you, and you can speak telepathically with them. To send or receive a message (no action required), you and the other creature must be within 1 mile of each other. A creature can end the telepathic connection at any time (no action required)."
        )
        return StringUtils.add_boxes(
            description,
            number_of_dice,
            regain_x_on=(1, "short rest"),
            regain_all_on="long rest",
        )


class PsychicBlades(Feature):
    def __init__(self):
        super().__init__(name="Psychic Blades", origin="Soulknife Rogue Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can manifest shimmering blades of psychic energy. Whenever you take the Attack action or make an Opportunity Attack, you can manifest a Psychic Blade in your free hand and make the attack with that blade. The magic blade has the following traits:\n"
            "Weapon Category: Simple Melee\n"
            "Damage on a Hit: 1d6 Psychic plus the ability modifier used for the attack roll\n"
            "Properties: Finesse, Thrown (range 60/120 feet)\n"
            "Mastery: Vex (you can use this property, and it doesn't count against the number of properties you can use with Weapon Mastery)\n"
            "The blade vanishes immediately after it hits or misses its target, and it leaves no mark if it deals damage.\n"
            "After you attack with the blade on your turn, you can make a melee or ranged attack with a second psychic blade as a Bonus Action on the same turn if your other hand is free to create it. The damage die of this bonus attack is 1d4 instead of 1d6."
        )
        return description


class SoulBlades(Feature):
    def __init__(self):
        super().__init__(name="Soul Blades", origin="Soulknife Rogue Level 9")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can now use the following powers with your Psychic Blades.\n"
            "Homing Strikes. If you make an attack roll with your Psychic Blade and miss the target, you can roll one Psionic Energy Die and add the number rolled to the attack roll. If this causes the attack to hit, the die is expended.\n"
            "Psychic Teleportation. As a Bonus Action, you manifest a Psychic Blade, expend one Psionic Energy Die and roll it, and throw the blade at an unoccupied space you can see up to a number of feet away equal to 10 times the number rolled. You then teleport to that space, and the blade vanishes."
        )
        return description


class PsychicVeil(Feature):
    def __init__(self):
        super().__init__(name="Psychic Veil", origin="Soulknife Rogue Level 13")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can weave a veil of psychic static to mask yourself. As a Magic action, you gain the Invisible condition for 1 hour or until you dismiss the effect (no action required). This invisibility ends early immediately after you deal damage to a creature or you force a creature to make a saving throw.\n"
            "Once you use this feature, you can't do so again until you finish a Long Rest unless you expend a Psionic Energy Die (no action required) to restore your use of it."
        )
        return description


class RendMind(Feature):
    def __init__(self):
        super().__init__(name="Rend Mind", origin="Soulknife Rogue Level 17")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can sweep your Psychic Blades through a creature's mind. When you use you Psychic Blades to deal Sneak Attack damage to a creature, you can force that target to make a Wisdom saving throw (DC 8 plus your Dexterity modifier and Proficiency Bonus). If the save fails, the target has the Stunned condition for 1 minute. The Stunned target repeats the save at the end of each of its turns, ending the effect on itself with a success.\n"
            "Once you use this feature, you can't do so again until you finish a Long Rest unless you expend three Psionic Energy Dice (no action required) to restore your use of it."
        )
        return description


### Thief Rogue Features ###


class FastHands(Feature):
    def __init__(self):
        super().__init__(name="Fast Hands", origin="Thief Rogue Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "As a Bonus Action, you can do one of the following.\n"
            "Sleight of Hand. Make a Dexterity (Sleight of Hand) check to pick a lock or disarm a trap with Thieves' Tools or to pick a pocket.\n"
            "Use an Object. Take the Utilize action, or take the Magic action to use a magic item that requires an action."
        )
        return description


class SecondStoryWork(Feature):
    def __init__(self):
        super().__init__(name="Second Story Work", origin="Thief Rogue Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You've trained to get into especially hard-to-reach places, granting you these benefits.\n"
            "Climber. You gain a Climb Speed equal to your Speed.\n"
            "Jumper. You can determine your jump distance using your Dexterity rather than your Strength."
        )
        return description


class SupremeSneak(Feature):
    def __init__(self):
        super().__init__(name="Supreme Sneak", origin="Thief Rogue Level 9")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain the following Cunning Strike option.\n"
            "Stealth Attack (Cost: 1d6). If you have the Hide action's Invisible condition, this attack doesn't end that condition on you if you end the turn behind Three-Quarters Cover or Total Cover."
        )
        return description


class UseMagicDevice(Feature):
    def __init__(self):
        super().__init__(name="Use Magic Device", origin="Thief Rogue Level 13")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You've learned how to maximize use of magic items, granting you the following benefits.\n"
            "Attunement. You can attune to up to four magic items at once.\n"
            "Charges. Whenever you use a magic item property that expends charges, roll 1d6. On a roll of 6, you use the property without expending the charges.\n"
            "Scrolls. You can use any Spell Scroll, using Intelligence as your spellcasting ability for the spell. If the spell is a cantrip or a level 1 spell, you can cast it reliably. If the scroll contains a higher-level spell, you must first succeed on an Intelligence (Arcana) check (DC 10 plus the spell's level). On a successful check, you cast the spell from the scroll. On a failed check, the scroll disintegrates."
        )
        return description


class ThiefsReflexes(Feature):
    def __init__(self):
        super().__init__(name="Thief's Reflexes", origin="Thief Rogue Level 17")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You are adept at laying ambushes and quickly escaping danger. You can take two turns during the first round of any combat. You take your first turn at your normal Initiative and your second turn at your Initiative minus 10."
        return description


### Phantom Rogue Features ###


class WailsFromTheGrave(Feature):
    def __init__(self):
        super().__init__(name="Wails from the Grave", origin="Phantom Rogue Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        dexterity_modifier = character_stat_block.get_ability_modifier(
            Ability.DEXTERITY
        )
        uses = max(1, dexterity_modifier)
        description = (
            "Immediately after you deal Sneak Attack damage to a creature on your turn, you can target a second creature that you can see within 30 feet of the first creature. Roll half the number of Sneak Attack damage dice for your level (round up), and the second creature takes Necrotic damage equal to the roll's total as wails of the dead sound around it.\n"
            "You can use this feature a number of times equal to your Dexterity modifier (minimum of once), and you regain all expended uses when you finish a Long Rest."
        )
        return StringUtils.add_boxes(description, uses, regain_all_on="long rest")


class WhispersOfTheDead(Feature):
    def __init__(self):
        super().__init__(name="Whispers of the Dead", origin="Phantom Rogue Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Whenever you finish a Short or Long Rest, you can choose one skill or tool proficiency that you lack and gain it, as a ghostly presence shares its knowledge with you. You lose this proficiency when you use this benefit again to choose a different proficiency."
        return description


class TokensOfTheDeparted(Feature):
    def __init__(self):
        super().__init__(name="Tokens of the Departed", origin="Phantom Rogue Level 9")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "The spirits of the dead are drawn to you, and echoes of their past lives magically manifest as strange curios with resonant power.\n"
            "You gain two soul trinkets. A soul trinket is a Tiny object (the DM determines the trinket's form or has you roll on the Trinkets table in the Player's Handbook to generate it). If you move more than 30 feet from a trinket, the trinket immediately teleports to you, appearing somewhere on your person.\n"
            "Using Soul Trinkets. You can use soul trinkets in the following ways:\n"
            "Death's Knell. When you deal Sneak Attack damage on your turn, you can destroy one soul trinket and immediately use Wails from the Grave without expending a use of that feature.\n"
            "Life Essence. While you have at least one soul trinket, you have Advantage on Death Saving Throws and Constitution saving throws.\n"
            "Spirit Query. You can take a Magic action to destroy one soul trinket and immediately cast the Augury spell, requiring no spell components and using Constitution as the spellcasting modifier. If you know the creature with which the trinket is associated, you can ask the creature's spirit one question instead of casting the spell. In this case, the spirit appears to you and answers as concisely as possible in a language it knew in life.\n"
            "Gaining Additional Soul Trinkets. When a creature you can see within 30 feet of you dies, you can take a Reaction to gain another soul trinket, claiming a sliver of that creature's departing spirit. The new trinket appears somewhere on your person.\n"
            "You can have a maximum of two soul trinkets at a time. If you try to gain a soul trinket while at your maximum, one of your existing trinkets is immediately destroyed and replaced by the new trinket. The maximum number of soul trinkets you can have increases when you reach Rogue levels 13 (three trinkets) and 17 (four trinkets).\n"
            "Whenever you finish a Long Rest with fewer than two soul trinkets, you gain soul trinkets until you have two."
        )
        return description


class VoiceOfDeath(Feature):
    def __init__(self):
        super().__init__(name="Voice of Death", origin="Phantom Rogue Level 9")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can cast Speak with Dead once without a spell slot, requiring no spell components and using Dexterity as the spellcasting modifier. You regain the ability to cast it this way when you finish a Short or Long Rest.\n"
            "When you cast the spell, you can target one of your soul trinkets from Tokens of the Departed instead of a corpse, allowing the spirit of the creature associated with the trinket to answer."
        )
        return description


class GhostWalk(Feature):
    def __init__(self):
        super().__init__(name="Ghost Walk", origin="Phantom Rogue Level 13")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "As a Bonus Action, you assume a spectral form, gaining the benefits below for 10 minutes or until you end them (no action required). Once you use this feature, you can't use it again until you finish a Long Rest unless you destroy one of your soul trinkets from Tokens of the Departed (no action required) to restore your use of it.\n"
            "Flight. You gain a Fly Speed of 10 feet and can hover.\n"
            "Hazy Form. Attack rolls have Disadvantage against you.\n"
            "Incorporeal Movement. You can move through creatures and objects as if they were Difficult Terrain, but you take 1d10 Force damage if you end your turn inside a creature or an object."
        )
        return description


class DeathsFriend(Feature):
    def __init__(self):
        super().__init__(name="Death's Friend", origin="Phantom Rogue Level 17")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your association with death has become so close that you gain the following benefits.\n"
            "Death's Lament. When you use Wails from the Grave, you can deal the feature's Necrotic damage to both the first and the second creature.\n"
            "Draw of Death. When you roll Initiative, you gain one soul trinket for your Tokens of the Departed if you have none remaining."
        )
        return description
