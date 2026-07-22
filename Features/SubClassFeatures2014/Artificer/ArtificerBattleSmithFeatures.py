from Definitions import ARTIFICER_HIT_DIE, Ability
from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class BattleSmithToolsOfTheTrade(Feature):
    def __init__(self):
        super().__init__(name="Tool Proficiency", origin="Battle Smith Artificer Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you adopt this specialization at 3rd level, you gain proficiency with smith's tools. If you already have this proficiency, you gain proficiency with one other type of artisan's tools of your choice."
        return description


class BattleSmithSpells(Feature):
    def __init__(self):
        super().__init__(name="Battle Smith Spells", origin="Battle Smith Artificer Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Starting at 3rd level, you always have certain spells prepared after you reach particular levels in this class, as shown in the Battle Smith Spells table. These spells count as artificer spells for you, but they don't count against the number of artificer spells you prepare.\n"
            "Battle Smith Spells\n"
            "Artificer Level	Battle Smith Spells\n"
            "3rd	Heroism, Shield\n"
            "5th	Branding Smite, Warding Bond\n"
            "9th	Aura of Vitality, Conjure Barrage\n"
            "13th	Aura of Purity, Fire Shield\n"
            "17th	Banishing Smite, Mass Cure Wounds"
        )
        return description


class BattleReady(Feature):
    def __init__(self):
        super().__init__(name="Battle Ready", origin="Battle Smith Artificer Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you reach 3rd level, your combat training and your experiments with magic have paid off in two ways.\n"
            "You gain proficiency with martial weapons.\n"
            "When you attack with a magic weapon, you can use your Intelligence modifier, instead of Strength or Dexterity modifier, for the attack and damage rolls."
        )
        return description


class SteelDefender(Feature):
    def __init__(self):
        super().__init__(name="Steel Defender", origin="Battle Smith Artificer Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "By 3rd level, your tinkering has borne you a faithful companion, a steel defender. It's friendly to you and your companions, and it obeys your commands. See its game statistics in the Steel Defender stat block, which uses your proficiency bonus (PB) in several places. You determine the creature's appearance and whether it has two legs or four; your choice has no effect on its game statistics.\n"
            "In combat, the defender shares your initiative count, but it takes its turn immediately after yours. It can move and use its reaction on its own, but the only action it takes on its turn is the Dodge action, unless you take a bonus action on your turn to command it to take another action. That action can be one in its stat block or some other action. If you are incapacitated, the defender can take any action of its choice, not just Dodge.\n"
            "If the Mending spell is cast on it, it regains 2d6 hit points. If it has died within the last hour, you can use your smith's tools as an action to revive it, provided you are within 5 feet of it and you expend a spell slot of 1st level or higher. The steel defender returns to life after 1 minute with all its hit points restored.\n"
            "At the end of a long rest, you can create a new steel defender if you have smith's tools with you. If you already have a defender from this feature, the first one immediately perishes. The defender also perishes if you die.\n"
            "Steel Defender\n"
            "Medium construct\n"
            "Armor Class: 15 (natural armor)\n"
            "Hit Points: 2 + your Intelligence modifier + 5 times your artificer level (the defender has a number of Hit Dice [d8s] equal to your artificer level)\n"
            "Speed: 40 ft.\n"
            "STR	DEX	CON	INT	WIS	CHA\n"
            "14 (+2)	12 (+1)	14 (+2)	4 (−3)	10 (+0)	6 (−2)\n"
            "Saving Throws: Dex +1 plus PB, Con +2 plus PB\n"
            "Skills: Athletics +2 plus PB, Perception +0 plus PB x 2\n"
            "Damage Immunities: poison\n"
            "Condition Immunities: charmed, exhaustion, poisoned\n"
            "Senses: darkvision 60 ft., passive Perception 10 + (PB x 2)\n"
            "Languages: understands the languages you speak\n"
            "Challenge: —\n"
            "Proficiency Bonus (PB): equals your bonus\n"
            "Vigilant. The defender can't be surprised.\n"
            "Actions\n"
            "Force-Empowered Rend. Melee Weapon Attack: your spell attack modifier to hit, reach 5 ft., one target you can see. Hit: 1d8 + PB force damage.\n"
            "Repair (3/Day). The magical mechanisms inside the defender restore 2d8 + PB hit points to itself or to one construct or object within 5 feet of it.\n"
            "Reactions\n"
            "Deflect Attack. The defender imposes disadvantage on the attack roll of one creature it can see that is within 5 feet of it, provided the attack roll is against a creature other than the defender."
        )
        return description


class BattleSmithExtraAttack(Feature):
    def __init__(self):
        super().__init__(name="Extra Attack", origin="Battle Smith Artificer Level 5")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Starting at 5th level, you can attack twice, rather than once, whenever you take the Attack action on your turn."
        return description


class ArcaneJolt(Feature):
    def __init__(self):
        super().__init__(name="Arcane Jolt", origin="Battle Smith Artificer Level 9")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        intelligence_modifier = character_stat_block.get_ability_modifier(Ability.INTELLIGENCE)
        uses = max(1, intelligence_modifier)
        description = (
            "At 9th level, you've learned new ways to channel arcane energy to harm or heal. When either you hit a target with a magic weapon attack or your steel defender hits a target, you can channel magical energy through the strike to create one of the following effects.\n"
            "The target takes an extra 2d6 force damage.\n"
            "Choose one creature or object you can see within 30 feet of the target. Healing energy flows into the chosen recipient, restoring 2d6 hit points to it.\n"
            "You can use this energy a number of times equal to your Intelligence modifier (minimum of once), but you can do so no more than once on a turn. You regain all expended uses when you finish a long rest."
        )
        return StringUtils.add_boxes(description, uses, regain_all_on="long rest")


class ImprovedDefender(Feature):
    def __init__(self):
        super().__init__(name="Improved Defender", origin="Battle Smith Artificer Level 15")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "At 15th level, your Arcane Jolt and steel defender become more powerful.\n"
            "The extra damage and the healing of your Arcane Jolt both increase to 4d6.\n"
            "Your steel defender gains a +2 bonus to Armor Class.\n"
            "Whenever your steel defender uses its Deflect Attack, the attacker takes force damage equal to 1d4 + your Intelligence modifier."
        )
        return description
