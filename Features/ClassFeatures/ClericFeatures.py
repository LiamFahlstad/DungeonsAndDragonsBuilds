from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Definitions import Ability, DiceRollCondition, Skill
from Features.BaseFeatures import CharacterFeature, TextFeature


BARBARIAN_HIT_DIE = 8


class DivineOrder(TextFeature):
    def __init__(self):
        super().__init__(name="Divine Order", origin="Cleric Level 1")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You have dedicated yourself to one of the following sacred roles of your choice.\n"
            "Protector. Trained for battle, you gain proficiency with Martial weapons and training with Heavy armor.\n"
            "Thaumaturge. You know one extra cantrip from the Cleric spell list. In addition, your mystical connection to the divine gives you a bonus to your Intelligence (Arcana or Religion) checks. The bonus equals your Wisdom modifier (minimum of +1)."
        )
        return description


class ChannelDivinity(TextFeature):
    def __init__(self):
        super().__init__(name="Channel Divinity", origin="Cleric Level 2")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can channel divine energy directly from the Outer Planes to fuel magical effects. You start with two such effects: Divine Spark and Turn Undead, each of which is described below. Each time you use this class's Channel Divinity, choose which Channel Divinity effect from this class to create. You gain additional effect options at higher Cleric levels.\n"
            "You can use this class's Channel Divinity twice. You regain one of its expended uses when you finish a Short Rest, and you regain all expended uses when you finish a Long Rest. You gain additional uses when you reach certain Cleric levels, as shown in the Channel Divinity column of the Cleric Features table.\n"
            "If a Channel Divinity effect requires a saving throw, the DC equals the spell save DC from this class's Spellcasting feature.\n"
            "Divine Spark. As a Magic action, you point your Holy Symbol at another creature you can see within 30 feet of yourself and focus divine energy at it. Roll 1d8 and add your Wisdom modifier. You either restore Hit Points to the creature equal to that total or force the creature to make a Constitution saving throw. On a failed save, the creature takes Necrotic or Radiant damage (your choice) equal to that total. On a successful save, the creature takes half as much damage (round down).\n"
            "You roll an additional d8 when you reach Cleric levels 7 (2d8), 13 (3d8), and 18 (4d8).\n"
            "Turn Undead. As a Magic action, you present your Holy Symbol and censure Undead creatures. Each Undead of your choice within 30 feet of you must make a Wisdom saving throw. If the creature fails its save, it has the Frightened and Incapacitated conditions for 1 minute. For that duration, it tries to move as far from you as it can on its turns. This effect ends early on the creature if it takes any damage, if you have the Incapacitated condition, or if you die."
        )
        return description


class SearUndead(TextFeature):
    def __init__(self):
        super().__init__(name="Sear Undead", origin="Cleric Level 5")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Whenever you use Turn Undead, you can roll a number of d8s equal to your Wisdom modifier (minimum of 1d8) and add the rolls together. Each Undead that fails its saving throw against that use of Turn Undead takes Radiant damage equal to the roll's total. This damage doesn't end the turn effect."
        return description


class BlessedStrikes(TextFeature):
    def __init__(self):
        super().__init__(name="Blessed Strikes", origin="Cleric Level 7")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Divine power infuses you in battle. You gain one of the following options of your choice (if you get either option from a Cleric subclass in an older book, use only the option you choose for this feature).\n"
            "Divine Strike. Once on each of your turns when you hit a creature with an attack roll using a weapon, you can cause the target to take an extra 1d8 Necrotic or Radiant damage (your choice).\n"
            "Potent Spellcasting. Add your Wisdom modifier to the damage you deal with any Cleric cantrip."
        )
        return description


class DivineIntervention(TextFeature):
    def __init__(self):
        super().__init__(name="Divine Intervention", origin="Cleric Level 10")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can call on your deity or pantheon to intervene on your behalf. As a Magic action, choose any Cleric spell of level 5 or lower that doesn't require a Reaction to cast. As part of the same action, you cast that spell without expending a spell slot or needing Material components. You can't use this feature again until you finish a Long Rest."
        return description


class ImprovedBlessedStrikes(TextFeature):
    def __init__(self):
        super().__init__(name="Improved Blessed Strikes", origin="Cleric Level 14")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "The option you chose for Blessed Strikes grows more powerful.\n"
            "Divine Strike. The extra damage of your Divine Strike increases to 2d8.\n"
            "Potent Spellcasting. When you cast a Cleric cantrip and deal damage to a creature with it, you can give vitality to yourself or another creature within 60 feet of yourself, granting a number of Temporary Hit Points equal to twice your Wisdom modifier."
        )
        return description


class GreaterDivineIntervention(TextFeature):
    def __init__(self):
        super().__init__(name="Greater Divine Intervention", origin="Cleric Level 20")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can call on even more powerful divine intervention. When you use your Divine Intervention feature, you can choose Wish when you select a spell. If you do so, you can't use Divine Intervention again until you finish 2d4 Long Rests.\n"
            "class"
        )
        return description


### Knowledge Domain Cleric Features ###


class BlessingsofKnowledge(TextFeature):
    def __init__(self):
        super().__init__(
            name="Blessings of Knowledge", origin="Knowledge Domain Cleric Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You gain proficiency with one type of Artisan's Tools of your choice and in two of the following skills of your choice: Arcana, History, Nature, or Religion. You have Expertise in those two skills."
        return description


class KnowledgeDomainSpells(TextFeature):
    def __init__(self):
        super().__init__(
            name="Knowledge Domain Spells", origin="Knowledge Domain Cleric Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you reach a Cleric level specified in the Knowledge Domain Spells table, you thereafter always have the listed spells prepare"
        return description


class MindMagic(TextFeature):
    def __init__(self):
        super().__init__(name="Mind Magic", origin="Knowledge Domain Cleric Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "As a Magic action, you can expend one use of your Channel Divinity to manifest your magical knowledge. Choose one spell from the Divination school on the Knowledge Domain Spells table that you have prepared. As part of that action, you cast that spell without expending a spell slot or needing Material components."
        return description


class UnfetteredMind(TextFeature):
    def __init__(self):
        super().__init__(
            name="Unfettered Mind", origin="Knowledge Domain Cleric Level 6"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain telepathy out to 60 feet. When you use this telepathy, you can simultaneously contact a number of creatures equal to your Wisdom modifier (minimum of one).\n"
            "Additionally, you gain proficiency in Intelligence saving throws. If you already have this proficiency, you instead gain saving throw proficiency with one ability in which you lack it."
        )
        return description


class DivineForeknowledge(TextFeature):
    def __init__(self):
        super().__init__(
            name="Divine Foreknowledge", origin="Knowledge Domain Cleric Level 17"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "As a Bonus Action, you magically expand your mind to the future. For 1 hour, you have Advantage on D20 Tests. Once you use this feature, you can't use it again until you finish a Long Rest. You can also restore your use of this feature by expending a level 6+ spell slot (no action required)."
        return description


### Life Domain Cleric Features ###


class DiscipleofLife(TextFeature):
    def __init__(self):
        super().__init__(name="Disciple of Life", origin="Life Domain Cleric Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When a spell you cast with a spell slot restores Hit Points to a creature, that creature regains additional Hit Points on the turn you cast the spell. The additional Hit Points equal 2 plus the spell slot's level."
        return description


class LifeDomainSpells(TextFeature):
    def __init__(self):
        super().__init__(name="Life Domain Spells", origin="Life Domain Cleric Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Your connection to this divine domain ensures you always have certain spells ready. When you reach a Cleric level specified in the Life Domain Spells table, you thereafter always have the listed spells prepared."
        return description


class PreserveLife(TextFeature):
    def __init__(self):
        super().__init__(name="Preserve Life", origin="Life Domain Cleric Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "As a Magic action, you present your Holy Symbol and expend a use of your Channel Divinity to evoke healing energy that can restore a number of Hit Points equal to five times your Cleric level. Choose Bloodied creatures within 30 feet of yourself (which can include you), and divide those Hit Points among them. This feature can restore a creature to no more than half its Hit Point maximum."
        return description


class BlessedHealer(TextFeature):
    def __init__(self):
        super().__init__(name="Blessed Healer", origin="Life Domain Cleric Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "The healing spells you cast on others heal you as well. Immediately after you cast a spell with a spell slot that restores Hit Points to one or more creatures other than yourself, you regain Hit Points equal to 2 plus the spell slot's level."
        return description


class SupremeHealing(TextFeature):
    def __init__(self):
        super().__init__(name="Supreme Healing", origin="Life Domain Cleric Level 17")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you would normally roll one or more dice to restore Hit Points to a creature with a spell or Channel Divinity, don't roll those dice for the healing; instead use the highest number possible for each die. For example, instead of restoring 2d6 Hit Points to a creature with a spell, you restore 12."
        return description


### Light Domain Cleric Features ###


class LightDomainSpells(TextFeature):
    def __init__(self):
        super().__init__(
            name="Light Domain Spells", origin="Light Domain Cleric Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Your connection to this divine domain ensures you always have certain spells ready. When you reach a Cleric level specified in the Light Domain Spells table, you thereafter always have the listed spells prepared."
        return description


class RadianceOfTheDawn(TextFeature):
    def __init__(self):
        super().__init__(
            name="Radiance of the Dawn", origin="Light Domain Cleric Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "As a Magic action, you present your Holy Symbol and expend a use of your Channel Divinity to emit a flash of light in a 30-foot Emanation originating from yourself. Any magical Darkness—such as that created by the Darkness spell—in that area is dispelled. Additionally, each creature of your choice in that area must make a Constitution saving throw, taking Radiant damage equal to 2d10 plus your Cleric level on a failed save or half as much damage on a successful one."
        return description


class WardingFlare(TextFeature):
    def __init__(self):
        super().__init__(name="Warding Flare", origin="Light Domain Cleric Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When a creature that you can see within 30 feet of yourself makes an attack roll, you can take a Reaction to impose Disadvantage on the attack roll, causing light to flare before it hits or misses.\n"
            "You can use this feature a number of times equal to your Wisdom modifier (minimum of once). You regain all expended uses when you finish a Long Rest."
        )
        return description


class ImprovedWardingFlare(TextFeature):
    def __init__(self):
        super().__init__(
            name="Improved Warding Flare", origin="Light Domain Cleric Level 6"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You regain all expended uses of your Warding Flare when you finish a Short or Long Rest.\n"
            "In addition, whenever you use Warding Flare, you can give the target of the triggering attack a number of Temporary Hit Points equal to 2d6 plus your Wisdom modifier."
        )
        return description


class CoronaOfLight(TextFeature):
    def __init__(self):
        super().__init__(name="Corona of Light", origin="Light Domain Cleric Level 17")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "As a Magic action, you cause yourself to emit an aura of sunlight that lasts for 1 minute or until you dismiss it (no action required). You emit Bright Light in a 60-foot radius and Dim Light for an additional 30 feet. Your enemies in the Bright Light have Disadvantage on saving throws against your Radiance of the Dawn and any spell that deals Fire or Radiant damage.\n"
            "You can use this feature a number of times equal to your Wisdom modifier (minimum of once), and you regain all expended uses when you finish a Long Rest."
        )
        return description


### Trickery Domain Cleric Features ###


class BlessingOfTheTrickster(TextFeature):
    def __init__(self):
        super().__init__(
            name="Blessing of the Trickster", origin="Trickery Domain Cleric Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "As a Magic action, you can choose yourself or a willing creature within 30 feet of yourself to have Advantage on Dexterity (Stealth) checks. This blessing lasts until you finish a Long Rest or you use this feature again."
        return description


class TrickeryDomainSpells(TextFeature):
    def __init__(self):
        super().__init__(
            name="Trickery Domain Spells", origin="Trickery Domain Cleric Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Your connection to this divine domain ensures you always have certain spells ready. When you reach a Cleric level specified in the Trickery Domain Spells table, you thereafter always have the listed spells prepared."
        return description


class InvokeDuplicity(TextFeature):
    def __init__(self):
        super().__init__(
            name="Invoke Duplicity", origin="Trickery Domain Cleric Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "As a Bonus Action, you can expend one use of your Channel Divinity to create a perfect visual illusion of yourself in an unoccupied space you can see within 30 feet of yourself. The illusion is intangible and doesn't occupy its space. It lasts for 1 minute, but it ends early if you dismiss it (no action required) or have the Incapacitated condition. The illusion is animated and mimics your expressions and gestures. While it persists, you gain the following benefits.\n"
            "Cast Spells. You can cast spells as though you were in the illusion's space, but you must use your own senses.\n"
            "Distract. When both you and your illusion are within 5 feet of a creature that can see the illusion, you have Advantage on attack rolls against that creature, given how distracting the illusion is to the target.\n"
            "Move. As a Bonus Action, you can move the illusion up to 30 feet to an unoccupied space you can see that is within 120 feet of yourself."
        )
        return description


class TrickstersTransposition(TextFeature):
    def __init__(self):
        super().__init__(
            name="Trickster's Transposition", origin="Trickery Domain Cleric Level 6"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Whenever you take the Bonus Action to create or move the illusion of your Invoke Duplicity, you can teleport, swapping places with the illusion."
        return description


class ImprovedDuplicity(TextFeature):
    def __init__(self):
        super().__init__(
            name="Improved Duplicity", origin="Trickery Domain Cleric Level 17"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "The illusion of your Invoke Duplicity has grown more powerful in the following ways.\n"
            "Shared Distraction. When you and your allies make attack rolls against a creature within 5 feet of the illusion, the attack rolls have Advantage.\n"
            "Healing Illusion. When the illusion ends, you or a creature of your choice within 5 feet of it regains a number of Hit Points equal to your Cleric level."
        )
        return description


### War Domain Cleric Features ###


class GuidedStrike(TextFeature):
    def __init__(self):
        super().__init__(name="Guided Strike", origin="War Domain Cleric Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you or a creature within 30 feet of you misses with an attack roll, you can expend one use of your Channel Divinity and give that roll a +10 bonus, potentially causing it to hit. When you use this feature to benefit another creature's attack roll, you must take a Reaction to do so."
        return description


class WarDomainSpells(TextFeature):
    def __init__(self):
        super().__init__(name="War Domain Spells", origin="War Domain Cleric Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Your connection to this divine domain ensures you always have certain spells ready. When you reach a Cleric level specified in the War Domain Spells table, you thereafter always have the listed spells prepared."
        return description


class WarPriest(TextFeature):
    def __init__(self):
        super().__init__(name="War Priest", origin="War Domain Cleric Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "As a Bonus Action, you can make one attack with a weapon or an Unarmed Strike. You can use this Bonus Action a number of times equal to your Wisdom modifier (minimum of once). You regain all expended uses when you finish a Short or Long Rest."
        return description


class WarGodsBlessing(TextFeature):
    def __init__(self):
        super().__init__(name="War God's Blessing", origin="War Domain Cleric Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can expend a use of your Channel Divinity to cast Shield of Faith or Spiritual Weapon rather than expending a spell slot. When you cast either spell in this way, the spell doesn't require Concentration. Instead the spell lasts for 1 minute, but it ends early if you cast that spell again, have the Incapacitated condition, or die."
        return description


class AvatarOfBattle(TextFeature):
    def __init__(self):
        super().__init__(name="Avatar of Battle", origin="War Domain Cleric Level 17")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain Resistance to Bludgeoning, Piercing, and Slashing damage."
        )
        return description
