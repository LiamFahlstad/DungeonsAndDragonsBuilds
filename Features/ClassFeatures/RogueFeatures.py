from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Definitions import Ability, DiceRollCondition, Skill
from Features import Weapons, Maneuvers
from Features.BaseFeatures import CharacterFeature, TextFeature


RANGER_HIT_DIE = 8


class Expertise(CharacterFeature):
    def __init__(self, skill_1: Skill, skill_2: Skill):
        self.skill_1 = skill_1
        self.skill_2 = skill_2

    def modify(self, character_stat_block: CharacterStatBlock):
        character_stat_block.skills.add_skill_expertise(self.skill_1)
        character_stat_block.skills.add_skill_expertise(self.skill_2)


class SneakAttack(TextFeature):
    def __init__(self):
        super().__init__(name="Sneak Attack", origin="Rogue Level 1")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You know how to strike subtly and exploit a foe's distraction. Once per turn you can deal an extra 1d6 damage to one creature you hit with an attack roll if you have Advantage on the roll and the attack uses a Finesse or a Ranged weapon. The extra damage's type is the same was the weapon's type.\n"
            "You don't need Advantage on the attack roll if at least one of your allies is within 5 feet of the target, the ally doesn't have the Incapacitated condition and you don't have Disadvantage on the attack roll.\n"
            "The extra damage increases as you gain Rogue levels, as shown in the Sneak Attack column of the Rogue Features table."
        )
        return description


class ThievesCant(TextFeature):
    def __init__(self):
        super().__init__(name="Thieves' Cant", origin="Rogue Level 1")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You picked up various languages in the communities where you plied your roguish talents. You know Thieves' Cant and one other language of your choice, which you choose from the language tables in Chapter 2."
        return description


class WeaponMastery(TextFeature):
    def __init__(self):
        super().__init__(name="Weapon Mastery", origin="Rogue Level 1")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your training with weapons allows you to use the mastery properties of two kinds of weapons of your choice with which you have proficiency, such as Daggers and Shortbows.\n"
            "Whenever you finish a Long Rest, you can change the kinds of weapons you chose. For example, you could switch to using the mastery properties of Scimitars and Shortswords."
        )
        return description


class CunningAction(TextFeature):
    def __init__(self):
        super().__init__(name="Cunning Action", origin="Rogue Level 2")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Your quick thinking and agility allow you to move and act quickly. On your turn, you can take one of the following actions as a Bonus Action: Dash, Disengage, or Hide."
        return description


class SteadyAim(TextFeature):
    def __init__(self):
        super().__init__(name="Steady Aim", origin="Rogue Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "As a Bonus Action, you give yourself Advantage on your next attack roll on your current turn. You can use this feature only if you haven't moved during this turn, and after you use it, your Speed is 0 until the end of the current turn."
        return description


class CunningStrike(TextFeature):
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
            " * Poison (Cost: 1d6). You add a toxin to your strike, forcing the target to make a Constitution saving throw. On a failed save, the target has the Poisoned condition for 1 minute. At the end of each of its turns, the poisoned target repeats the save, ending the effect on a success.\n"
            "   To use this effect, you must have a Poisoner's Kit on your person.\n"
            " * Trip (Cost: 1d6). If the target is Large or smaller, it must succeed on a Dexterity saving throw or have the Prone condition.\n"
            " * Withdraw (Cost: 1d6). Immediately after the attack, you move up to half your speed without provoking Opportunity Attacks."
        )
        return description


class UncannyDodge(TextFeature):
    def __init__(self):
        super().__init__(name="Uncanny Dodge", origin="Rogue Level 5")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When an attacker that you can see hits you with an attack roll, you can take a Reaction to halve the attack's damage against you (round down)."
        return description


class Evasion(TextFeature):
    def __init__(self):
        super().__init__(name="Evasion", origin="Rogue Level 7")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can nimbly dodge out of the way of certain dangers. When you're subjected to an effect that allows you to make a Dexterity saving throw to take only half damage, you instead take no damage if you succeed on the saving throw and only half damage if you fail. You can't use this feature if you have the Incapacitated condition."
        return description


class ReliableTalent(TextFeature):
    def __init__(self):
        super().__init__(name="Reliable Talent", origin="Rogue Level 7")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Whenever you make an ability check that uses one of your skill or tool proficiencies, you can treat a d20 roll of 9 or lower as a 10."
        return description


class ImprovedCunningStrike(TextFeature):
    def __init__(self):
        super().__init__(name="Improved Cunning Strike", origin="Rogue Level 11")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can use up to two Cunning Strike effects when you deal Sneak Attack damage, paying the die cost for each effect."
        return description


class DeviousStrikes(TextFeature):
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


class SlipperyMind(TextFeature):
    def __init__(self):
        super().__init__(name="Slippery Mind", origin="Rogue Level 15")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        character_stat_block.saving_throws.add_proficiency(Ability.WISDOM)
        character_stat_block.saving_throws.add_proficiency(Ability.CHARISMA)
        description = "Your mind is exceptionally difficult to control. You gain proficiency in Wisdom and Charisma saving throws."
        return description


class Elusive(TextFeature):
    def __init__(self):
        super().__init__(name="Elusive", origin="Rogue Level 18")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You're so evasive that attackers rarely gain the upper hand against you. No attack roll can have advantage against you unless you have the Incapacitated condition."
        return description


class StrokeOfLuck(TextFeature):
    def __init__(self):
        super().__init__(name="Stroke of Luck", origin="Rogue Level 20")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You have a marvelous knack for succeeding when you need to. If you fail a d20 Test, you can turn the roll into a 20.\n"
            "Once you use this feature, you can't use it again until you finish a Short or Long Rest."
        )
        return description


### Arcane Trickster Rogue Features ###


class MageHandLegerdemain(TextFeature):
    def __init__(self):
        super().__init__(
            name="Mage Hand Legerdemain", origin="Arcane Trickster Rogue Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you cast Mage Hand, you can cast it as a Bonus Action, and you can make the spectral hand Invisible. You can control the hand as a Bonus Action, and through it, you can make Dexterity (Sleight of Hand) checks."
        return description


class MagicalAmbush(TextFeature):
    def __init__(self):
        super().__init__(name="Magical Ambush", origin="Arcane Trickster Rogue Level 9")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "If you have the Invisible condition when you cast a spell on a creature, it has Disadvantage on any saving throw it makes against the spell on the same turn."
        return description


class VersatileTrickster(TextFeature):
    def __init__(self):
        super().__init__(
            name="Versatile Trickster", origin="Arcane Trickster Rogue Level 13"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You gain the ability to distract targets with your Mage Hand. When you use the Trip option of your Cunning Strike on a creature, you can also use that option on another creature within 5 feet of the spectral hand."
        return description


class SpellThief(TextFeature):
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


class Assassinate(TextFeature):
    def __init__(self):
        super().__init__(name="Assassinate", origin="Assassin Rogue Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You're adept at ambushing a target, granting you the following benefits.\n"
            "Initiative. You have Advantage on Initiative rolls.\n"
            "Surprising Strikes. During the first round of each combat, you have Advantage on attack rolls against any creature that hasn't taken a turn. If your Sneak Attack hits any target during that round, the target takes extra damage of the weapon's type equal to your Rogue level."
        )
        return description


class AssassinsTools(TextFeature):
    def __init__(self):
        super().__init__(name="Assassin's Tools", origin="Assassin Rogue Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You gain a Disguise Kit and a Poisoner's Kit, and you have proficiency with them."
        return description


class InfiltrationExpertise(TextFeature):
    def __init__(self):
        super().__init__(name="Infiltration Expertise", origin="Assassin Rogue Level 9")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You are an expert at the following techniques that aid your infiltrations.\n"
            "Masterful Mimicry. You can unerringly mimic another person's speech, handwriting or both if you have spent at least 1 hour studying them.\n"
            "Roving Aim. Your speed isn't reduced to 0 by using Steady Aim."
        )
        return description


class EnvenomWeapons(TextFeature):
    def __init__(self):
        super().__init__(name="Envenom Weapons", origin="Assassin Rogue Level 13")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you use the Poison option of your Cunning Strike, the target also takes 2d6 Poison damage whenever it fails the saving throw. This damage ignores Resistance to Poison damage."
        return description


class DeathStrike(TextFeature):
    def __init__(self):
        super().__init__(name="Death Strike", origin="Assassin Rogue Level 17")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you hit with your Sneak Attack on the first round of a combat, the target must succeed on a Constitution saving throw (DC 8 plus your Dexterity modifier and Proficiency Bonus), or the attack's damage is doubled against the target."
        return description


### Scion of the Three Rogue Features ###


class Bloodthirst(TextFeature):
    def __init__(self):
        super().__init__(name="Bloodthirst", origin="Scion of the Three Rogue Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When an enemy you can see within 30 feet of yourself takes damage and is Bloodied after taking that damage but not killed outright, you can take a Reaction and teleport to an unoccupied space you can see within 5 feet of that enemy. You can then make one melee attack. You can use this feature a number of times equal to your Intelligence modifier (minimum of once), and you regain all expended uses when you finish a Long Rest."
        return description


class DreadAllegiance(TextFeature):
    def __init__(self):
        super().__init__(
            name="Dread Allegiance", origin="Scion of the Three Rogue Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Choose one of the Dead Three: Bane, Bhaal, or Myrkul. You gain Resistance to one type of damage and the ability to cast a cantrip, as detailed in the table below; Intelligence is your spellcasting ability for this cantrip. When you finish a Long Rest, you can change your choice."
        return description


class StrikeFear(TextFeature):
    def __init__(self):
        super().__init__(name="Strike Fear", origin="Scion of the Three Rogue Level 9")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain the following Cunning Strike option.\n"
            "Terrify (Cost: 1d6). The target must succeed on a Wisdom saving throw, or it has the Frightened condition for 1 minute. While the target is Frightened in this way, you have Advantage on attack rolls against the target.\n"
            "The Frightened target repeats the save at the end of each of its turns, ending the effect on itself on a success."
        )
        return description


class AuraofMalevolence(TextFeature):
    def __init__(self):
        super().__init__(
            name="Aura of Malevolence", origin="Scion of the Three Rogue Level 13"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You radiate malignant power associated with one of the Dead Three. When you use Bloodthirst and teleport, each creature of your choice within 10 feet of either the space you left or your destination space (your choice) takes damage equal to your Intelligence modifier; the damage type is the same as the damage Resistance granted by your choice in the Dread Allegiance feature. Damage dealt by this feature ignores Resistance."
        return description


class DreadIncarnate(TextFeature):
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


class PsionicPower(TextFeature):
    def __init__(self):
        super().__init__(name="Psionic Power", origin="Soulknife Rogue Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You harbor a wellspring of psionic energy within yourself. It is represented by your Psionic Energy Dice, which fuel certain powers you have from this subclass. The Soulknife Energy Dice table shows the number of these dice you have when you reach certain Rogue levels, and the table shows the die size.\n"
            "Any features in this subclass that use a Psionic Energy Die use only the dice from this subclass. Some of your powers expend a Psionic Energy Die, as specified in the power's description, and you can't use the power if it requires you to use a die when your Psionic Energy Dice are all expended.\n"
            "You regain one of your expended Psionic Energy Dice when you finish a Short Rest, and you regain all of them when you finish a Long Rest.\n"
            "Psi-Bolstered Knack. If you fail an ability check using a skill or tool with which you have proficiency, you can roll one Psionic Energy Die and add the number rolled to the check, potentially turning failure into success. The die is expended only if the roll then succeeds.\n"
            "Psychic Whispers. You can establish telepathic communication between yourself and others. As a Magic action, choose one or more creatures you can see, up to a number of creatures equal to your Proficiency Bonus, and then roll one Psionic Energy Die. For a number of hours equal to the number rolled, the chosen creatures can speak telepathically to you, and you can speak telepathically with them. To send or receive a message (no action required), you and the other creature must be within 1 mile of each other. A creature can end the telepathic connection at any time (no action required)."
        )
        return description


class PsychicBlades(TextFeature):
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


class SoulBlades(TextFeature):
    def __init__(self):
        super().__init__(name="Soul Blades", origin="Soulknife Rogue Level 9")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can now use the following powers with your Psychic Blades.\n"
            "Homing Strikes. If you make an attack roll with your Psychic Blade and miss the target, you can roll one Psionic Energy Die and add the number rolled to the attack roll. If this causes the attack to hit, the die is expended.\n"
            "Psychic Teleportation. As a Bonus Action, you manifest a Psychic Blade, expend one Psionic Energy Die and roll it, and throw the blade at an unoccupied space you can see up to a number of feet away equal to 10 times the number rolled. You then teleport to that space, and the blade vanishes."
        )
        return description


class PsychicVeil(TextFeature):
    def __init__(self):
        super().__init__(name="Psychic Veil", origin="Soulknife Rogue Level 13")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can weave a veil of psychic static to mask yourself. As a Magic action, you gain the Invisible condition for 1 hour or until you dismiss the effect (no action required). This invisibility ends early immediately after you deal damage to a creature or you force a creature to make a saving throw.\n"
            "Once you use this feature, you can't do so again until you finish a Long Rest unless you expend a Psionic Energy Die (no action required) to restore your use of it."
        )
        return description


class RendMind(TextFeature):
    def __init__(self):
        super().__init__(name="Rend Mind", origin="Soulknife Rogue Level 17")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can sweep your Psychic Blades through a creature's mind. When you use you Psychic Blades to deal Sneak Attack damage to a creature, you can force that target to make a Wisdom saving throw (DC 8 plus your Dexterity modifier and Proficiency Bonus). If the save fails, the target has the Stunned condition for 1 minute. The Stunned target repeats the save at the end of each of its turns, ending the effect on itself with a success.\n"
            "Once you use this feature, you can't do so again until you finish a Long Rest unless you expend three Psionic Energy Dice (no action required) to restore your use of it."
        )
        return description


### Thief Rogue Features ###


class FastHands(TextFeature):
    def __init__(self):
        super().__init__(name="Fast Hands", origin="Thief Rogue Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "As a Bonus Action, you can do one of the following.\n"
            "Sleight of Hand. Make a Dexterity (Sleight of Hand) check to pick a lock or disarm a trap with Thieves' Tools or to pick a pocket.\n"
            "Use an Object. Take the Utilize action, or take the Magic action to use a magic item that requires an action."
        )
        return description


class SecondStoryWork(TextFeature):
    def __init__(self):
        super().__init__(name="Second Story Work", origin="Thief Rogue Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You've trained to get into especially hard-to-reach places, granting you these benefits.\n"
            "Climber. You gain a Climb Speed equal to your Speed.\n"
            "Jumper. You can determine your jump distance using your Dexterity rather than your Strength."
        )
        return description


class SupremeSneak(TextFeature):
    def __init__(self):
        super().__init__(name="Supreme Sneak", origin="Thief Rogue Level 9")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain the following Cunning Strike option.\n"
            "Stealth Attack (Cost: 1d6). If you have the Hide action's Invisible condition, this attack doesn't end that condition on you if you end the turn behind Three-Quarters Cover or Total Cover."
        )
        return description


class UseMagicDevice(TextFeature):
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


class ThiefsReflexes(TextFeature):
    def __init__(self):
        super().__init__(name="Thief's Reflexes", origin="Thief Rogue Level 17")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You are adept at laying ambushes and quickly escaping danger. You can take two turns during the first round of any combat. You take your first turn at your normal Initiative and your second turn at your Initiative minus 10."
        return description
