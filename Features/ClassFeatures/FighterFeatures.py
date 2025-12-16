from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Definitions import Ability, DiceRollCondition, Skill
from Features import Weapons, Maneuvers
from Features.BaseFeatures import CharacterFeature, TextFeature


FIGHTER_HIT_DIE = 10


class FightingStyle(TextFeature):
    def __init__(self):
        super().__init__(name="Fighting Style", origin="Fighter Level 1")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain a Fighting Style feat of your choice (see chapter 5). Defense is recommended.\n"
            "Whenever you gain a Fighter level, you can replace the feat you chose with a different Fighting Style feat."
        )
        return description


class SecondWind(TextFeature):
    def __init__(self):
        super().__init__(name="Second Wind", origin="Fighter Level 1")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        uses = 2
        if character_stat_block.character_level >= 4:
            uses = 3
        if character_stat_block.character_level >= 10:
            uses = 3

        base_text = (
            f"You have a limited well of physical and mental stamina that you can draw on. "
            f"As a Bonus Action, you can use it to regain Hit Points equal to 1d10 plus your Fighter level.\n"
            f"You can use this feature {uses} time(s). You regain one expended use when you finish a Short Rest, "
            f"and you regain all expended uses when you finish a Long Rest.\n"
        )
        if character_stat_block.character_level >= 2:
            base_text += self.add_feature_effects(character_stat_block, TacticalMind())

        if character_stat_block.character_level >= 5:
            base_text += self.add_feature_effects(character_stat_block, TacticalShift())

        return base_text


class WeaponMastery(TextFeature):
    def __init__(self):
        super().__init__(name="Weapon Mastery", origin="Fighter Level 1")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your training with weapons allows you to use the mastery properties of three kinds of Simple or Martial weapons of your choice. Whenever you finish a Long Rest, you can practice weapon drills and change one of those weapon choices.\n"
            "When you reach certain Fighter levels, you gain the ability to use the mastery properties of more kinds of weapons, as shown in the Weapon Mastery column of the Fighter Features table."
        )
        return description


class ActionSurge(TextFeature):
    def __init__(self):
        super().__init__(name="Action Surge", origin="Fighter Level 2")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can push yourself beyond your normal limits for a moment. On your turn, you can take one additional action, except the Magic action.\n"
            "Once you use this feature, you can’t do so again until you finish a Short or Long Rest. Starting at level 17, you can use it twice before a rest but only once on a turn."
        )
        return description


class TacticalMind(TextFeature):
    def __init__(self):
        super().__init__(name="Tactical Mind", origin="Fighter Level 2")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You have a mind for tactics on and off the battlefield. When you fail an ability check, you can expend a use of your Second Wind to push yourself toward success. Rather than regaining Hit Points, you roll 1d10 and add the number rolled to the ability check, potentially turning it into a success. If the check still fails, this use of Second Wind isn’t expended."
        return description


class SuperiorityDice(TextFeature):
    def __init__(self):
        self.maneuvers = []
        super().__init__(name="Superiority Dice", origin="Fighter Battle Master")

    def add_maneuver(self, maneuver: Maneuvers.Maneuver):
        self.maneuvers.append(maneuver)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        if character_stat_block.character_level < 7:
            number_of_superiority_die = 4
        elif character_stat_block.character_level < 15:
            number_of_superiority_die = 5
        else:
            number_of_superiority_die = 6

        if character_stat_block.character_level < 10:
            superiority_die = "1d8"
        elif character_stat_block.character_level < 18:
            superiority_die = "1d10"
        else:
            superiority_die = "1d12"

        base_text = (
            f"These are {superiority_die}s, and you can expend them to fuel your maneuvers.\n"
            "You regain all expended superiority dice when you finish a short or long rest.\n"
            f"Number of Superiority Dice: {number_of_superiority_die}\n"
        )

        for maneuver in self.maneuvers:
            base_text += self.add_feature_effects(character_stat_block, maneuver)

        return base_text


class ExtraAttack(TextFeature):
    def __init__(self):
        super().__init__(name="Extra Attack", origin="Fighter Level 5")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can attack twice instead of once whenever you take the Attack action on your turn."
        return description


class TacticalShift(TextFeature):
    def __init__(self):
        super().__init__(name="Tactical Shift", origin="Fighter Level 5")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Whenever you activate your Second Wind with a Bonus Action, you can move up to half your Speed without provoking Opportunity Attacks."
        return description


class Indomitable(TextFeature):
    def __init__(self):
        super().__init__(name="Indomitable", origin="Fighter Level 9")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "If you fail a saving throw, you can reroll it with a bonus equal to your Fighter level. You must use the new roll, and you can’t use this feature again until you finish a Long Rest.\n"
            "You can use this feature twice before a Long Rest starting at level 13 and three times before a Long Rest starting at level 17."
        )
        return description


class TacticalMaster(TextFeature):
    def __init__(self):
        super().__init__(name="Tactical Master", origin="Fighter Level 9")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you attack with a weapon whose mastery property you can use, you can replace that property with the Push, Sap, or Slow property for that attack."
        return description


class TwoExtraAttacks(TextFeature):
    def __init__(self):
        super().__init__(name="Two Extra Attacks", origin="Fighter Level 11")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can attack three times instead of once whenever you take the Attack action on your turn."
        return description


class StudiedAttacks(TextFeature):
    def __init__(self):
        super().__init__(name="Studied Attacks", origin="Fighter Level 13")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You study your opponents and learn from each attack you make. If you make an attack roll against a creature and miss, you have Advantage on your next attack roll against that creature before the end of your next turn."
        return description


class EpicBoon(TextFeature):
    def __init__(self):
        super().__init__(name="Epic Boon", origin="Fighter Level 19")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You gain an Epic Boon feat or another feat of your choice for which you qualify. Boon of Combat Prowess is recommended."
        return description


class ThreeExtraAttacks(TextFeature):
    def __init__(self):
        super().__init__(name="Three Extra Attacks", origin="Fighter Level 20")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can attack four times instead of once whenever you take the Attack action on your turn."
        return description


### Banneret Fighter Features ###


class KnightlyEnvoy(TextFeature):
    def __init__(self):
        super().__init__(name="Knightly Envoy", origin="Banneret Fighter Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You know how to conduct yourself with grace as a noble ambassador. You gain the following benefits.\n"
            "Comprehension. You can cast the Comprehend Languages spell but only as a Ritual. Charisma is your spellcasting ability for it.\n"
            "Polyglot. You learn one language from the language tables in the Player’s Handbook or chapter 2 of this book. When you finish a Long Rest, you can replace a language learned from this benefit with another language you have heard, seen signed, or read in the past 24 hours.\n"
            "Well Spoken. You gain proficiency in one of the following skills of your choice: Insight, Intimidation, Persuasion, or Performance."
        )
        return description


class GroupRecovery(TextFeature):
    def __init__(self):
        super().__init__(name="Group Recovery", origin="Banneret Fighter Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you use your Second Wind to regain Hit Points, you can choose a number of allies within a 30-foot Emanation originating from yourself, up to a number of allies equal to your Charisma modifier (minimum of one). Each of those allies regains Hit Points equal to 1d4 plus your Fighter level. Once you use this ability, you can’t use it again until you finish a Short or Long Rest."
        return description


class TeamTactics(TextFeature):
    def __init__(self):
        super().__init__(name="Team Tactics", origin="Banneret Fighter Level 7")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you use Group Recovery, each chosen ally has Advantage on D20 Tests until the start of your next turn."
        return description


class RallyingSurge(TextFeature):
    def __init__(self):
        super().__init__(name="Rallying Surge", origin="Banneret Fighter Level 10")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you use your Action Surge, you can choose allies within a 30-foot Emanation originating from yourself, up to a number of allies equal to your Charisma modifier (minimum of one). Each of those allies can immediately take a Reaction to use one of the following options.\n"
            "Attack. The ally makes one attack with a weapon or an Unarmed Strike.\n"
            "Move. The ally moves up to half its Speed without provoking Opportunity Attacks."
        )
        return description


class SharedResilience(TextFeature):
    def __init__(self):
        super().__init__(name="Shared Resilience", origin="Banneret Fighter Level 15")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When an ally you can see within 60 feet of yourself fails a saving throw, you can take a Reaction to expend a use of your Indomitable feature. The ally can immediately reroll the saving throw with a bonus equal to your Fighter level; the ally must use the new roll."
        return description


class InspiringCommander(TextFeature):
    def __init__(self):
        super().__init__(name="Inspiring Commander", origin="Banneret Fighter Level 18")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain the following benefits.\n"
            "Bolstered Rally. The area of effect for both Group Recovery and Rallying Surge is now a 60-foot Emanation.\n"
            "Unshakable Bravery. You have Immunity to the Charmed and Frightened conditions."
        )
        return description


### Battle Master Fighter Features ###


class CombatSuperiority(TextFeature):
    def __init__(self):
        super().__init__(
            name="Combat Superiority", origin="Battle Master Fighter Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your experience on the battlefield has refined your fighting techniques. You learn maneuvers that are fueled by special dice called Superiority Dice.\n"
            "Maneuvers. You learn three maneuvers of your choice from the “Maneuver Options” section later in this subclass’s description. Many maneuvers enhance an attack in some way. You can use only one maneuver per attack.\n"
            "You learn two additional maneuvers of your choice when you reach Fighter levels 7, 10, and 15. Each time you learn new maneuvers, you can also replace one maneuver you know with a different one.\n"
            "Superiority Dice. You have four Superiority Dice, which are d8s. A Superiority Die is expended when you use it. You regain all expended Superiority Dice when you finish a Short or Long Rest.\n"
            "You gain an additional Superiority Die when you reach Fighter levels 7 (five dice total) and 15 (six dice total).\n"
            "Saving Throws. If a maneuver requires a saving throw, the DC equals 8 plus your Strength or Dexterity modifier (your choice) and Proficiency Bonus."
        )
        return description


class StudentofWar(TextFeature):
    def __init__(self):
        super().__init__(name="Student of War", origin="Battle Master Fighter Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You gain proficiency with one type of Artisan’s Tools of your choice, and you gain proficiency in one skill of your choice from the skills available to Fighters at level 1."
        return description


class KnowYourEnemy(TextFeature):
    def __init__(self):
        super().__init__(name="Know Your Enemy", origin="Battle Master Fighter Level 7")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "As a Bonus Action, you can discern certain strengths and weaknesses of a creature you can see within 30 feet of yourself; you know whether that creature has any Immunities, Resistances, or Vulnerabilities, and if the creature has any, you know what they are.\n"
            "Once you use this feature, you can’t do so again until you finish a Long Rest. You can also restore a use of the feature by expending one Superiority Die (no action required)."
        )
        return description


class ImprovedCombatSuperiority(TextFeature):
    def __init__(self):
        super().__init__(
            name="Improved Combat Superiority", origin="Battle Master Fighter Level 10"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Your Superiority Die becomes a d10."
        return description


class Relentless(TextFeature):
    def __init__(self):
        super().__init__(name="Relentless", origin="Battle Master Fighter Level 15")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Once per turn, when you use a maneuver, you can roll 1d8 and use the number rolled instead of expending a Superiority Die."
        return description


class UltimateCombatSuperiority(TextFeature):
    def __init__(self):
        super().__init__(
            name="Ultimate Combat Superiority", origin="Battle Master Fighter Level 18"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Your Superiority Die becomes a d12."
        return description


### Champion Fighter Features ###


class ImprovedCritical(TextFeature):
    def __init__(self):
        super().__init__(name="Improved Critical", origin="Champion Fighter Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Your attack rolls with weapons and Unarmed Strikes can score a Critical Hit on a roll of 19 or 20 on the d20."
        return description


class RemarkableAthlete(TextFeature):
    def __init__(self):
        super().__init__(name="Remarkable Athlete", origin="Champion Fighter Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Thanks to your athleticism, you have Advantage on Initiative rolls and Strength (Athletics) checks.\n"
            "In addition, immediately after you score a Critical Hit, you can move up to half your Speed without provoking Opportunity Attacks."
        )
        return description


class AdditionalFightingStyle(TextFeature):
    def __init__(self):
        super().__init__(
            name="Additional Fighting Style", origin="Champion Fighter Level 7"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You gain another Fighting Style feat of your choice."
        return description


class HeroicWarrior(TextFeature):
    def __init__(self):
        super().__init__(name="Heroic Warrior", origin="Champion Fighter Level 10")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "The thrill of battle drives you toward victory. During combat, you can give yourself Heroic Inspiration whenever you start your turn without it."
        return description


class SuperiorCritical(TextFeature):
    def __init__(self):
        super().__init__(name="Superior Critical", origin="Champion Fighter Level 15")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Your attack rolls with weapons and Unarmed Strikes can now score a Critical Hit on a roll of 18-20 on the d20."
        return description


class Survivor(TextFeature):
    def __init__(self):
        super().__init__(name="Survivor", origin="Champion Fighter Level 18")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You attain the pinnacle of resilience in battle, giving you these benefits.\n"
            "Defy Death. You have Advantage on Death Saving Throws. Moreover, when you roll 18-20 on a Death Saving Throw, you gain the benefit of rolling a 20 on it.\n"
            "Heroic Rally. At the start of each of your turns, you regain Hit Points equal to 5 plus your Constitution modifier if you are Bloodied and have at least 1 Hit Point."
        )
        return description


### Eldritch Knight Fighter Features ###


class Spellcasting(TextFeature):
    def __init__(self):
        super().__init__(name="Spellcasting", origin="Eldritch Knight Fighter Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You have learned to cast spells. See chapter 7 for the rules on spellcasting. The information below details how you use those rules as an Eldritch Knight.\n"
            "Cantrips. You know two cantrips of your choice from the Wizard spell list (see that class’s section for its list). Ray of Frost and Shocking Grasp are recommended. Whenever you gain a Fighter level, you can replace one of these cantrips with another cantrip of your choice from the Wizard spell list.\n"
            "When you reach Fighter level 10, you learn another Wizard cantrip of your choice.\n"
            "Spell Slots. The Eldritch Knight Spellcasting table shows how many spell slots you have to cast your level 1+ spells. You regain all expended slots when you finish a Long Rest.\n"
            "Prepared Spells of Level 1+. You prepare the list of level 1+ spells that are available for you to cast with this feature. To start, choose three level 1 spells from the Wizard spell list. Burning Hands, Jump, and Shield are recommended.\n"
            "The number of spells on your list increases as you gain Fighter levels, as shown in the Prepared Spells column of the Eldritch Knight Spellcasting table. Whenever that number increases, choose additional spells from the Wizard spell list until the number of spells on your list matches the number on the table. The chosen spells must be of a level for which you have spell slots. For example, if you’re a level 7 Fighter, your list of prepared spells can include five Wizard spells of levels 1 and 2 in any combination.\n"
            "Changing Your Prepared Spells. Whenever you gain a Fighter level, you can replace one spell on your list with another Wizard spell for which you have spell slots.\n"
            "Spellcasting Ability. Intelligence is your spellcasting ability for your Wizard spells.\n"
            "Spellcasting Focus. You can use an Arcane Focus as a Spellcasting Focus for your Wizard spells.\n"
            "Eldritch Knight Spellcasting\n"
            "Fighter Level	Prepared Spells	1st	2nd	3rd	4th\n"
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


class WarBond(TextFeature):
    def __init__(self):
        super().__init__(name="War Bond", origin="Eldritch Knight Fighter Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You learn a ritual that creates a magical bond between yourself and one weapon. You perform the ritual over the course of 1 hour, which can be done during a Short Rest. The weapon must be within your reach throughout the ritual, at the conclusion of which you touch the weapon and forge the bond. The bond fails if another Fighter is bonded to the weapon or if the weapon is a magic item to which someone else is attuned.\n"
            "Once you have bonded a weapon to yourself, you can’t be disarmed of that weapon unless you have the Incapacitated condition. If it is on the same plane of existence, you can summon that weapon as a Bonus Action, causing it to teleport instantly to your hand.\n"
            "You can have up to two bonded weapons, but you can summon only one at a time with a Bonus Action. If you attempt to bond with a third weapon, you must break the bond with one of the other two."
        )
        return description


class WarMagic(TextFeature):
    def __init__(self):
        super().__init__(name="War Magic", origin="Eldritch Knight Fighter Level 7")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you take the Attack action on your turn, you can replace one of the attacks with a casting of one of your Wizard cantrips that has a casting time of an action."
        return description


class EldritchStrike(TextFeature):
    def __init__(self):
        super().__init__(
            name="Eldritch Strike", origin="Eldritch Knight Fighter Level 10"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You learn how to make your weapon strikes undercut a creature’s ability to withstand your spells. When you hit a creature with an attack using a weapon, that creature has Disadvantage on the next saving throw it makes against a spell you cast before the end of your next turn."
        return description


class ArcaneCharge(TextFeature):
    def __init__(self):
        super().__init__(
            name="Arcane Charge", origin="Eldritch Knight Fighter Level 15"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you use your Action Surge, you can teleport up to 30 feet to an unoccupied space you can see. You can teleport before or after the additional action."
        return description


class ImprovedWarMagic(TextFeature):
    def __init__(self):
        super().__init__(
            name="Improved War Magic", origin="Eldritch Knight Fighter Level 18"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you take the Attack action on your turn, you can replace two of the attacks with a casting of one of your level 1 or level 2 Wizard spells that has a casting time of an action."
        return description


### Psi Warrior Fighter Features ###


class PsionicPower(TextFeature):
    def __init__(self):
        super().__init__(name="Psionic Power", origin="Psi Warrior Fighter Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You harbor a wellspring of psionic energy within yourself. It is represented by your Psionic Energy Dice, which fuel powers you have from this subclass. The Psi Warrior Energy Dice table shows the die size and number of these dice you have when you reach certain Fighter levels.\n"
            "Psi Warrior Energy Dice\n"
            "Fighter Level	Die Size	Number\n"
            "3	D6	4\n"
            "5	D8	6\n"
            "9	D8	8\n"
            "11	D10	8\n"
            "13	D10	10\n"
            "17	D12	12\n"
            "Any features in this subclass that use a Psionic Energy Die use only the dice from this subclass. Some of your powers expend the Psionic Energy Die, as specified in a power’s description, and you can’t use a power if it requires you to use a die when all your Psionic Energy Dice are expended.\n"
            "You regain one of your expended Psionic Energy Dice when you finish a Short Rest, and you regain all of them when you finish a Long Rest.\n"
            "Protective Field. When you or another creature you can see within 30 feet of you takes damage, you can take a Reaction to expend one Psionic Energy Die, roll the die, and reduce the damage taken by the number rolled plus your Intelligence modifier (minimum reduction of 1), as you create a momentary shield of telekinetic force.\n"
            "Psionic Strike. You can propel your weapons with psionic force. Once on each of your turns, immediately after you hit a target within 30 feet of yourself with an attack and deal damage to it with a weapon, you can expend one Psionic Energy Die, rolling it and dealing Force damage to the target equal to the number rolled plus your Intelligence modifier.\n"
            "Telekinetic Movement. You can move an object or a creature with your mind. As a Magic action, choose one target you can see within 30 feet of yourself; the target must be a loose object that is Large or smaller or one willing creature other than you. You transport the target up to 30 feet to an unoccupied space you can see. Alternatively, if the target is a Tiny object, you can transport it to or from your hand.\n"
            "Once you take this action, you can’t do so again until you finish a Short or Long Rest unless you expend a Psionic Energy Die (no action required) to restore your use of it."
        )
        return description


class TelekineticAdept(TextFeature):
    def __init__(self):
        super().__init__(name="Telekinetic Adept", origin="Psi Warrior Fighter Level 7")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You have mastered new ways to use your telekinetic abilities, detailed below.\n"
            "Psi-Powered Leap. As a Bonus Action, you gain a Fly Speed equal to twice your Speed until the end of the current turn. Once you take this Bonus Action, you can’t do so again until you finish a Short or Long Rest unless you expend a Psionic Energy Die (no action required) to restore your use of it.\n"
            "Telekinetic Thrust. When you deal damage to a target with your Psionic Strike, you can force the target to make a Strength saving throw (DC 8 plus your Intelligence modifier and Proficiency Bonus). On a failed save, you can give the target the Prone condition or transport it up to 10 feet horizontally."
        )
        return description


class GuardedMind(TextFeature):
    def __init__(self):
        super().__init__(name="Guarded Mind", origin="Psi Warrior Fighter Level 10")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You have Resistance to Psychic damage. Moreover, if you start your turn with the Charmed or Frightened condition, you can expend a Psionic Energy Die (no action required) and end every effect on yourself giving you those conditions."
        return description


class BulwarkofForce(TextFeature):
    def __init__(self):
        super().__init__(name="Bulwark of Force", origin="Psi Warrior Fighter Level 15")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can shield yourself and others with telekinetic force. As a Bonus Action, you can choose creatures, including yourself, within 30 feet of yourself, up to a number of creatures equal to your Intelligence modifier (minimum of one creature). Each of the chosen creatures has Half Cover for 1 minute or until you have the Incapacitated condition.\n"
            "Once you use this feature, you can’t do so again until you finish a Long Rest unless you expend a Psionic Energy Die (no action required) to restore your use of it."
        )
        return description


class TelekineticMaster(TextFeature):
    def __init__(self):
        super().__init__(
            name="Telekinetic Master", origin="Psi Warrior Fighter Level 18"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You always have the telekinesis spell prepared. With this feature, you can cast it without a spell slot or components, and your spellcasting ability for it is Intelligence. On each of your turns while you maintain Concentration on it, including the turn when you cast it, you can make one attack with a weapon as a Bonus Action.\n"
            "Once you cast the spell with this feature, you can’t do so in this way again until you finish a Long Rest unless you expend a Psionic Energy Die (no action required) to restore your use of it."
        )
        return description
