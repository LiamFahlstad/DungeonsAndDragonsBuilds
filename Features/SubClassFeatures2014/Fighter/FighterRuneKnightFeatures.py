from Definitions import Ability
from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class BonusProficiencies(Feature):
    def __init__(self):
        super().__init__(
            name="Bonus Proficiencies",
            origin="Rune Knight Fighter Level 3",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You gain proficiency with smith's tools, and you learn to speak, read, and write Giant."
        return description


class RuneCarver(Feature):
    def __init__(self):
        super().__init__(
            name="Rune Carver",
            origin="Rune Knight Fighter Level 3",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        proficiency_bonus = character_stat_block.get_proficiency_bonus()
        constitution_modifier = character_stat_block.get_ability_modifier(Ability.CONSTITUTION)
        rune_magic_save_dc = 8 + proficiency_bonus + constitution_modifier

        description = (
            "You can use magic runes to enhance your gear. You learn two runes of your choice, from among the runes described below, and each time you gain a level in this class, you can replace one rune you know with a different one from this feature. When you reach certain levels in this class, you learn additional runes, as shown in the Runes Known table.\n"
            "\n"
            "Runes Known\n"
            "Fighter Level\tNumber of Runes\n"
            "3rd\t2\n"
            "7th\t3\n"
            "10th\t4\n"
            "15th\t5\n"
            "\n"
            "Whenever you finish a long rest, you can touch a number of objects equal to the number of runes you know, and you inscribe a different rune onto each of the objects. To be eligible, an object must be a weapon, a suit of armor, a shield, a piece of jewelry, or something else you can wear or hold in a hand. Your rune remains on an object until you finish a long rest, and an object can bear only one of your runes at a time.\n"
            "\n"
            f"The following runes are available to you when you learn a rune. If a rune has a level requirement, you must be at least that level in this class to learn the rune. If a rune requires a saving throw, your Rune Magic save DC equals {rune_magic_save_dc}.\n"
            "\n"
            "Cloud Rune. This rune emulates the deceptive magic used by some cloud giants. While wearing or carrying an object inscribed with this rune, you have advantage on Dexterity (Sleight of Hand) checks and Charisma (Deception) checks.\n"
            "    In addition, when you or a creature you can see within 30 feet of you is hit by an attack roll, you can use your reaction to invoke the rune and choose a different creature within 30 feet of you, other than the attacker. The chosen creature becomes the target of the attack, using the same roll. This magic can transfer the attack's effects regardless of the attack's range. Once you invoke this rune, you can't do so again until you finish a short or long rest.\n"
            "\n"
            "Fire Rune. This rune's magic channels the masterful craftsmanship of great smiths. While wearing or carrying an object inscribed with this rune, your proficiency bonus is doubled for any ability check you make that uses your proficiency with a tool.\n"
            "    In addition, when you hit a creature with an attack using a weapon, you can invoke the rune to summon fiery shackles: the target takes an extra 2d6 fire damage, and it must succeed on a Strength saving throw or be restrained for 1 minute. While restrained by the shackles, the target takes 2d6 fire damage at the start of each of its turns. The target can repeat the saving throw at the end of each of its turns, banishing the shackles on a success. Once you invoke this rune, you can't do so again until you finish a short or long rest.\n"
            "\n"
            "Frost Rune. This rune's magic evokes the might of those who survive in the wintry wilderness, such as frost giants. While wearing or carrying an object inscribed with this rune, you have advantage on Wisdom (Animal Handling) checks and Charisma (Intimidation) checks.\n"
            "    In addition, you can invoke the rune as a bonus action to increase your sturdiness. For 10 minutes, you gain a +2 bonus to all ability checks and saving throws that use Strength or Constitution. Once you invoke this rune, you can't do so again until you finish a short or long rest.\n"
            "\n"
            "Stone Rune. This rune's magic channels the judiciousness associated with stone giants. While wearing or carrying an object inscribed with this rune, you have advantage on Wisdom (Insight) checks, and you have darkvision out to a range of 120 feet.\n"
            "    In addition, when a creature you can see ends its turn within 30 feet of you, you can use your reaction to invoke the rune and force the creature to make a Wisdom saving throw. Unless the save succeeds, the creature is charmed by you for 1 minute. While charmed in this way, the creature has a speed of 0 and is incapacitated, descending into a dreamy stupor. The creature repeats the saving throw at the end of each of its turns, ending the effect on a success. Once you invoke this rune, you can't do so again until you finish a short or long rest.\n"
            "\n"
            "Hill Rune (7th Level or Higher). This rune's magic bestows a resilience reminiscent of a hill giant. While wearing or carrying an object that bears this rune, you have advantage on saving throws against being poisoned, and you have resistance against poison damage.\n"
            "    In addition, you can invoke the rune as a bonus action, gaining resistance to bludgeoning, piercing, and slashing damage for 1 minute. Once you invoke this rune, you can't do so again until you finish a short or long rest.\n"
            "\n"
            "Storm Rune (7th Level or Higher). Using this rune, you can glimpse the future like a storm giant seer. While wearing or carrying an object inscribed with this rune, you have advantage on Intelligence (Arcana) checks, and you can't be surprised as long as you aren't incapacitated.\n"
            "    In addition, you can invoke the rune as a bonus action to enter a prophetic state for 1 minute or until you're incapacitated. Until the state ends, when you or another creature you can see within 60 feet of you makes an attack roll, a saving throw, or an ability check, you can use your reaction to cause the roll to have advantage or disadvantage. Once you invoke this rune, you can't do so again until you finish a short or long rest."
        )
        return description


class GiantsMight(Feature):
    def __init__(self):
        super().__init__(
            name="Giant's Might",
            origin="Rune Knight Fighter Level 3",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        proficiency_bonus = character_stat_block.get_proficiency_bonus()
        description = (
            "You have learned how to imbue yourself with the might of giants. As a bonus action, you magically gain the following benefits, which last for 1 minute:\n"
            "    * If you are smaller than Large, you become Large, along with anything you are wearing. If you lack the room to become Large, your size doesn't change.\n"
            "    * You have advantage on Strength checks and Strength saving throws.\n"
            "    * Once on each of your turns, one of your attacks with a weapon or an unarmed strike can deal an extra 1d6 damage to a target on a hit.\n"
            "\n"
            f"You can use this feature {proficiency_bonus} times, and you regain all expended uses when you finish a long rest."
        )
        return StringUtils.add_boxes(description, proficiency_bonus, regain_all_on="long rest")


class RunicShield(Feature):
    def __init__(self):
        super().__init__(
            name="Runic Shield",
            origin="Rune Knight Fighter Level 7",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        proficiency_bonus = character_stat_block.get_proficiency_bonus()
        description = (
            "You learn to invoke your rune magic to protect your allies. When another creature you can see within 60 feet of you is hit by an attack roll, you can use your reaction to force the attacker to reroll the d20 and use the new roll.\n"
            "\n"
            f"You can use this feature {proficiency_bonus} times, and you regain all expended uses when you finish a long rest."
        )
        return StringUtils.add_boxes(description, proficiency_bonus, regain_all_on="long rest")


class GreatStature(Feature):
    def __init__(self):
        super().__init__(
            name="Great Stature",
            origin="Rune Knight Fighter Level 10",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "The magic of your runes permanently alters you. When you gain this feature, roll 3d4. You grow a number of inches in height equal to the roll (determine the exact result as you wish).\n"
            "\n"
            "Moreover, the extra damage you deal with your Giant's Might feature increases to 1d8."
        )
        return description


class MasterOfRunes(Feature):
    def __init__(self):
        super().__init__(
            name="Master of Runes",
            origin="Rune Knight Fighter Level 15",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can invoke each rune you know from your Rune Carver feature twice, rather than once, and you regain all expended uses when you finish a short or long rest."
        return description


class RunicJuggernaut(Feature):
    def __init__(self):
        super().__init__(
            name="Runic Juggernaut",
            origin="Rune Knight Fighter Level 18",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You learn how to amplify your rune-powered transformation. As a result, the extra damage you deal with the Giant's Might feature increases to 1d10. Moreover, when you use that feature, your size can increase to Huge, and while you are that size, your reach increases by 5 feet."
        )
        return description
