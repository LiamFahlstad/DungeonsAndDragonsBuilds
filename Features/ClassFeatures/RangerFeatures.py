from Definitions import Ability, Skill
from Features.BaseFeatures import CharacterFeature, TextFeature
from StatBlocks.CharacterStatBlock import CharacterStatBlock

RANGER_HIT_DIE = 10


class SpellCasting(TextFeature):
    def __init__(self):
        super().__init__(name="Spell Casting", origin="Ranger Level 1")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Spellcasting:\n"
            " * Whenever you finish a Long Rest, you can replace one spell on your list with another Ranger spell for which you have spell slots.\n"
            " * You regain all expended slots when you finish a Long Rest.\n"
            " * Wisdom is your spellcasting ability for your Ranger spells."
        )
        return description


class ReplacingWeaponMasteries(TextFeature):
    def __init__(self):
        super().__init__(name="Replacing Weapon Masteries", origin="Ranger Level 1")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Whenever you finish a Long Rest, you can change the kinds of weapons you chose."
        return description


class FavoredEnemy(TextFeature):
    def __init__(self):
        super().__init__(name="Favored Enemy", origin="Ranger Level 1")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        if character_stat_block.character_level < 5:
            free_hunters_mark_uses = 2
        elif character_stat_block.character_level < 9:
            free_hunters_mark_uses = 3
        elif character_stat_block.character_level < 13:
            free_hunters_mark_uses = 4
        elif character_stat_block.character_level < 16:
            free_hunters_mark_uses = 5
        else:
            free_hunters_mark_uses = 6

        description = (
            "You always have the Hunter's Mark spell prepared.\n"
            f"You can cast it {free_hunters_mark_uses} times without expending a spell slot, and you regain all expended uses of this ability when you finish a Long Rest.\n"
        )
        return description


class DeftExplorerExpertise(CharacterFeature):
    """While studying magic, you also specialized in another field of study. Choose one of the following skills in which you have proficiency: Arcana, History, Investigation, Medicine, Nature, or Religion. You have Expertise in the chosen skill."""

    def __init__(self, skill: Skill):
        self.skill = skill

    def modify(self, character_stat_block: CharacterStatBlock):
        character_stat_block.skills.add_skill_expertise(self.skill)


class DeftExplorerLanguages(TextFeature):
    def __init__(self):
        super().__init__(name="Deft Explorer", origin="Ranger Level 2")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Languages.: You know two languages of your choice from the language tables in chapter 2."
        return description


class ExtraAttack(TextFeature):
    def __init__(self):
        super().__init__(name="Extra Attack", origin="Ranger Level 5")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can attack twice instead of once whenever you take the Attack action on your turn."
        return description


class Roving(TextFeature):
    def __init__(self):
        super().__init__(name="Roving", origin="Ranger Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Your speed increases by 10 feet while you aren't wearing Heavy Armor. You also have a Climb speed and a Swim Speed equal to your Speed."
        return description


class Expertise(CharacterFeature):
    def __init__(self, skill_1: Skill, skill_2: Skill):
        self.skill_1 = skill_1
        self.skill_2 = skill_2

    def modify(self, character_stat_block: CharacterStatBlock):
        character_stat_block.skills.add_skill_expertise(self.skill_1)
        character_stat_block.skills.add_skill_expertise(self.skill_2)


class Tireless(TextFeature):
    def __init__(self):
        super().__init__(name="Tireless", origin="Ranger Level 10")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        wis_mod = character_stat_block.get_ability_modifier(Ability.WISDOM)
        description = (
            "Primal forces now help fuel you on your journeys, granting you the following benefits.\n"
            f" * Temporary Hit Points: As a Magic Action, you can give yourself a number of Temporary Hit Points equal to 1d8 plus your Wisdom modifier (minimum of 1) ({max(1, wis_mod)}).\n"
            f"   You can use this action a number of times equal to your Wisdom modifier (minimum of once) ({max(1, wis_mod)}), and you regain all expended uses when you finish a Long Rest.\n"
            " * Decrease Exhaustion: Whenever you finish a Short Rest, your Exhaustion level, if any, decreases by 1."
        )
        return description


class RelentlessHunter(TextFeature):
    def __init__(self):
        super().__init__(name="Relentless Hunter", origin="Ranger Level 13")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Taking damage can't break your Concentration on Hunter's Mark."
        return description


class NaturesVeil(TextFeature):
    def __init__(self):
        super().__init__(name="Nature's Veil", origin="Ranger Level 14")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        wis_mod = character_stat_block.get_ability_modifier(Ability.WISDOM)
        description = (
            "You invoke spirits of nature to magically hide yourself. As a Bonus Action you can give yourself the Invisible condition until the end of your next turn.\n"
            f"You can use this feature a number of times equal to your Wisdom modifier (minimum of once) ({max(1, wis_mod)}), and you regain all expended uses when you finish a Long Rest."
        )
        return description


class PreciseHunter(TextFeature):
    def __init__(self):
        super().__init__(name="Precise Hunter", origin="Ranger Level 17")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You have Advantage on attack rolls against the creature currently marked by your Hunter's Mark."
        return description


class FeralSenses(TextFeature):
    def __init__(self):
        super().__init__(name="Feral Senses", origin="Ranger Level 18")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Your connection to the forces of nature grants you Blindsight with a range of 30 feet."
        return description


class FoeSlayer(TextFeature):
    def __init__(self):
        super().__init__(name="Foe Slayer", origin="Ranger Level 20")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "The damage die of your Hunter's Mark is a d10 rather than a d6."
        return description


### Beast Master Ranger Features ###


class PrimalCompanion(TextFeature):
    def __init__(self):
        super().__init__(name="Primal Companion", origin="Beast Master Ranger Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You magically summon a primal beast, which draws strength from your bond with nature. Choose its stat block: Beast of the Land, Beast of the Sea or Beast of the Sky. You also determine the kind of animal it is, choosing a kind appropriate for the stat block. Whatever beast you choose, it bears primal markings indicating its supernatural origin.\n"
            "The Beast in Combat. In Combat, the beast acts during your turn. It can move and use its Reaction on its own, but the only action it takes is the Dodge action unless you take a Bonus Action to command it to take an action in its stat block or some other action. You can also sacrifice one of your attacks when you take the Attack action to command the beast to take the Beast's Strike action. If you have the Incapacitated condition, the beast acts on its own and isn't limited to the dodge action.\n"
            "Restoring or Replacing the Beast. If the beast has died within the last hour, you can take a Magic action to touch it and expend a spell slot. The beast returns to life after 1 minute with all its Hit Points restored.\n"
            "Whenever you finish a Long Rest, you can summon a different primal beast, which appears in an unoccupied space within 5 feet of you. You choose its stat block and appearance. If you already have a beast from this feature, the old one vanishes when the new one appears."
        )
        return description


class ExceptionalTraining(TextFeature):
    def __init__(self):
        super().__init__(
            name="Exceptional Training", origin="Beast Master Ranger Level 7"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you take a Bonus Action to command your Primal Companion beast to take an action, you can also command it to take the Dash, Disengage, Dodge, or Help action using its Bonus Action.\n"
            "In addition, whenever it hits with an attack roll and deals damage, it can deal your choice of Force damage or its normal damage type."
        )
        return description


class BestialFury(TextFeature):
    def __init__(self):
        super().__init__(name="Bestial Fury", origin="Beast Master Ranger Level 11")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you command your Primal Companion beast to take the Beast's Strike action, the beast can use it twice.\n"
            "In addition, the first time each turn it hits a creature under the effect of your Hunter's Mark spell, the beast deals extra Force damage equal to the bonus damage of that spell."
        )
        return description


class ShareSpells(TextFeature):
    def __init__(self):
        super().__init__(name="Share Spells", origin="Beast Master Ranger Level 15")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you cast a spell targeting yourself, you can also affect your Primal Companion beast with the spell if the beast is within 30 feet of you."
        return description


### Fey Wanderer Ranger Features ###


class DreadfulStrikes(TextFeature):
    def __init__(self):
        super().__init__(name="Dreadful Strikes", origin="Fey Wanderer Ranger Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can augment your weapon strikes with mind-scarring magic drawn from the murky hollows of the Feywild. When you hit a creature with a weapon, you can deal an extra 1d4 Psychic damage to the target, which can take this extra damage only once per turn. The extra damage increases to 1d6 when you reach Ranger level 11."
        return description


class FeyWandererSpells(TextFeature):
    def __init__(self):
        super().__init__(
            name="Fey Wanderer Spells", origin="Fey Wanderer Ranger Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you reach a Ranger level specified in the Fey Wanderer spells table, you thereafter always have the listed spells prepared."
        return description


class OtherworldlyGlamour(TextFeature):
    def __init__(self):
        super().__init__(
            name="Otherworldly Glamour.", origin="Fey Wanderer Ranger Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Whenever you make a Charisma check, you gain a bonus to the check equal to your Wisdom modifier (Minimum of +1).\n"
            "You also gain proficiency in one of these skills of your choice: Deception, Performance, or Persuasion."
        )
        return description


class BeguilingTwist(TextFeature):
    def __init__(self):
        super().__init__(name="Beguiling Twist", origin="Fey Wanderer Ranger Level 7")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "The magic of the Feywild guards your mind. You have advantage on saving throws to avoid or end the Charmed or Frightened condition.\n"
            "In addition, whenever you or a creature you can see within 120 feet of you succeeds on a saving throw to avoid or end the Charmed or Frightened condition, you can take a Reaction to force a different creature you can see within 120 feet of yourself to make a Wisdom save against your spell save DC. On a failed save, the target is charmed or frightened (your choice) for 1 minute. The target repeats the save at the end of each of its turns, ending the effect on itself on a success."
        )
        return description


class FeyReinforcements(TextFeature):
    def __init__(self):
        super().__init__(
            name="Fey Reinforcements", origin="Fey Wanderer Ranger Level 11"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can cast Summon Fey without a Material component. You can also cast it once without a spell slot, and you regain the ability to cast it in this way when you finish a Long Rest.\n"
            "Whenever you start casting the spell, you can modify it so that it doesn't require Concentration. If you do so, the spell's duration becomes 1 minute for the casting."
        )
        return description


class MistyWanderer(TextFeature):
    def __init__(self):
        super().__init__(name="Misty Wanderer", origin="Fey Wanderer Ranger Level 15")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can cast Misty Step without expending a spell slot. You can do so a number of times equal to your Wisdom modifier (minimum of once), and you regain all expended uses when you finish a Long Rest.\n"
            "In addition, whenever you cast Misty Step, you can bring along one willing creature you can see within 5 feet of yourself. That creature teleports to an unoccupied space of your choice within 5 feet of your destination space."
        )
        return description


### Gloom Stalker Ranger Features ###


class DreadAmbusher(TextFeature):
    def __init__(self):
        super().__init__(name="Dread Ambusher", origin="Gloom Stalker Ranger Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You have mastered the art of creating fearsome ambushes, granting you the following benefits.\n"
            "Ambusher's Leap. At the start of your first turn of each combat, your speed increases by 10 feet until the end of that turn.\n"
            "Dreadful Strike. When you attack a creature and hit it with a weapon, you can deal an extra 2d6 Psychic damage. You can use this benefit only once per turn, you can use it a number of times equal to your Wisdom modifier (minimum of once), and you regain all expended uses when you finish a Long Rest.\n"
            "Initiative Bonus. When you roll Initiative, you can add your Wisdom modifier to the roll."
        )
        return description


class GloomStalkerSpells(TextFeature):
    def __init__(self):
        super().__init__(
            name="Gloom Stalker Spells", origin="Gloom Stalker Ranger Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you reach a Ranger level specified in the Gloom Stalker spells table, you thereafter always have the listed spells prepared."
        return description


class UmbralSight(TextFeature):
    def __init__(self):
        super().__init__(name="Umbral Sight", origin="Gloom Stalker Ranger Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain Darkvision with a range of 60 feet. If you already have Darkvision when you gain this feature, its range increases by 60 feet.\n"
            "You are also adept at evading creatures that rely on Darkvision. While entirely in Darkness, you have the Invisible condition to any creature that relies on Darkvision to see you in that Darkness."
        )
        return description


class IronMind(TextFeature):
    def __init__(self):
        super().__init__(name="Iron Mind", origin="Gloom Stalker Ranger Level 7")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You have honed your ability to resist mind-altering powers. You gain proficiency in Wisdom saving throws. If you already have this proficiency, you instead gain proficiency in Intelligence or Charisma saving throws (your choice)."
        return description


class StalkersFlurry(TextFeature):
    def __init__(self):
        super().__init__(
            name="Stalker's Flurry", origin="Gloom Stalker Ranger Level 11"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "The Psychic damage of your Dreadful Strike becomes 2d8. In addition, when you use the Dreadful Strike effect of your Dread Ambusher feature, you can use one of the following additional effects.\n"
            "Sudden Strike. You can make another attack with the same weapon against a different creature that is within 5 feet of the original target and that is within the weapon's range.\n"
            "Mass Fear. The target and each creature within 10 feet of it must make a wisdom saving throw against your spell save DC. On a failed save, a creature has the Frightened condition until the start of your next turn."
        )
        return description


class ShadowyDodge(TextFeature):
    def __init__(self):
        super().__init__(name="Shadowy Dodge", origin="Gloom Stalker Ranger Level 15")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When a creature makes an attack roll against you, you can take a Reaction to impose Disadvantage on that roll. Whether the attack hits or misses, you can teleport up to 30 feet to an unoccupied space that you can see."
        return description


### Hunter Ranger Features ###


class HuntersLore(TextFeature):
    def __init__(self):
        super().__init__(name="Hunter's Lore", origin="Hunter Ranger Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can call upon the forces of nature to reveal certain strengths and weaknesses of your prey. While a creature is marked by your Hunter's Mark, you know whether the creature has any Immunities, Resistances, or Vulnerabilities, and if the creature has any, you know what they are."
        return description


class HuntersPrey(TextFeature):
    def __init__(self):
        super().__init__(name="Hunter's Prey", origin="Hunter Ranger Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain one of the following feature options of your choice. Whenever you finish a Short or Long Rest, you can replace the chosen option with the other one.\n"
            " * Colossus Slayer: Your tenacity can wear down even the most resilient foes. When you hit a creature with a weapon, the weapon deals an extra 1d8 damage to the target if it's missing any of its Hit Points. You can deal this extra damage only once per turn.\n"
            " * Horde Breaker: Once on each of your turns when you make an attack with a weapon, you can make another attack with the same weapon against a different creature that is within 5 feet of the original target, that is within the weapon's range, and that you haven't attacked this turn."
        )
        return description


class DefensiveTactics(TextFeature):
    def __init__(self):
        super().__init__(name="Defensive Tactics", origin="Hunter Ranger Level 7")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain one of the following feature options of your choice. Whenever you finish a Short or Long Rest, you can replace the chosen option with the other one.\n"
            "Escape the Horde. Opportunity Attacks have Disadvantage against you.\n"
            "Multiattack Defense. When a creature hits you with an attack roll, that creature has Disadvantage on all other attack rolls against you this turn."
        )
        return description


class SuperiorHuntersPrey(TextFeature):
    def __init__(self):
        super().__init__(name="Superior Hunter's Prey", origin="Hunter Ranger Level 11")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Once per turn when you deal damage to a creature marked by your Hunter's Mark, you can also deal that spell's extra damage to a different creature that you can see within 30 feet of the first creature."
        return description


class SuperiorHuntersDefense(TextFeature):
    def __init__(self):
        super().__init__(
            name="Superior Hunter's Defense", origin="Hunter Ranger Level 15"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you take damage, you can take a Reaction to give yourself Resistance to that damage and any other damage of the same type until the end of the current turn."
        return description


### Winter Walker Ranger Features ###


class FrigidExplorer(TextFeature):
    def __init__(self):
        super().__init__(name="Frigid Explorer", origin="Winter Walker Ranger Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain the following benefits.\n"
            "Biting Cold. Damage from your weapon attacks, Ranger spells, and Ranger features ignores Resistance to Cold damage.\n"
            "Frost Resistance. You have Resistance to Cold damage.\n"
            "Polar Strikes. When you hit a creature with an attack roll using a weapon, you can deal an extra 1d4 Cold damage to the target, which can take this extra damage only once per turn. When you reach Ranger level 11, this extra damage increases to 1d6."
        )
        return description


class HuntersRime(TextFeature):
    def __init__(self):
        super().__init__(name="Hunter's Rime", origin="Winter Walker Ranger Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Ice rimes you and your prey, protecting you and hindering them. When you cast Hunter's Mark, you gain Temporary Hit Points equal to 1d10 plus your Ranger level.\n"
            "Additionally, while a creature is marked by your Hunter's Mark, it can't take the Disengage action."
        )
        return description


class WinterWalkerSpells(TextFeature):
    def __init__(self):
        super().__init__(
            name="Winter Walker Spells", origin="Winter Walker Ranger Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you reach a Ranger level specified in the Winter Walker Spells table, you thereafter always have the listed spells prepared."
        return description


class FortifyingSoul(TextFeature):
    def __init__(self):
        super().__init__(name="Fortifying Soul", origin="Winter Walker Ranger Level 7")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your experience surviving harrowing environments allows you to bolster your allies in addition to yourself. As a Magic action, choose a number of creatures you can see equal to your Wisdom modifier (minimum of one). Each chosen creature regains Hit Points equal to 1d10 plus your Ranger level and has Advantage on saving throws to avoid or end the Frightened condition for 1 hour.\n"
            "Once you use this feature, you can't use it again until you finish a Long Rest."
        )
        return description


class ChillingRetribution(TextFeature):
    def __init__(self):
        super().__init__(
            name="Chilling Retribution", origin="Winter Walker Ranger Level 11"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When a creature hits you with an attack roll, you can take a Reaction to force the creature to make a Wisdom saving throw against your spell save DC. On a failed save, the target has the Stunned condition until the end of your next turn. While the target is Stunned, its Speed is reduced to 0 feet.\n"
            "You can use this feature a number of times equal to your Wisdom modifier (minimum of once), and you regain all expended uses when you finish a Long Rest."
        )
        return description


class FrozenHaunt(TextFeature):
    def __init__(self):
        super().__init__(name="Frozen Haunt", origin="Winter Walker Ranger Level 15")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you cast Hunter's Mark, you can adopt a ghostly, snowy form. This form lasts until the spell ends, and while you are in this form, you gain the following benefits. Once you use this feature, you can't use it again until you finish a Long Rest unless you expend a level 4+ spell slot (no action required).\n"
            "Frozen Soul. You have Immunity to Cold damage. When you first adopt this form and at the start of each of your subsequent turns, each creature of your choice in a 15-foot Emanation originating from you takes 2d4 Cold damage.\n"
            "Partially Incorporeal. You have Immunity to the Grappled, Prone, and Restrained conditions. You can move through creatures and objects as if they were Difficult Terrain, but you take 1d10 Force damage if you end your turn inside a creature or an object. If the form ends while you are inside a creature or an object, you are shunted to the nearest unoccupied space."
        )
        return description
