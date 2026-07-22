from Core.Definitions import ARTIFICER_HIT_DIE, Ability
from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class BattleSmithToolsOfTheTrade(Feature):
    def __init__(self):
        super().__init__(
            name="Tools of the Trade", origin="Battle Smith Artificer Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain the following benefits.\n"
            "Tool Proficiency. You gain proficiency with Smith's Tools. If you already have this proficiency, you gain proficiency with one other type of Artisan's Tools of your choice.\n"
            "Weapon Crafting. When you craft a nonmagical or magic weapon, the amount of time required to craft it is halved."
        )
        return description


class BattleSmithSpells(Feature):
    def __init__(self):
        super().__init__(
            name="Battle Smith spells", origin="Battle Smith Artificer Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you reach an Artificer level specified in the Battle Smith Spells table, you thereafter always have the listed spells prepared.\n"
            "Battle Smith Spells\n"
            "Artificer Level	Spells\n"
            "3	Heroism, Shield\n"
            "5	Shining Smite, Warding Bond\n"
            "9	Aura of Vitality, Conjure Barrage\n"
            "13	Aura of Purity, Fire Shield\n"
            "17	Banishing Smite, Mass Cure Wounds"
        )
        return description


class BattleReady(Feature):
    def __init__(self):
        super().__init__(name="Battle Ready", origin="Battle Smith Artificer Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your combat training and your experiments with magic have paid off in two ways.\n"
            "Arcane Empowerment. When you attack with a magic weapon, you can use your Intelligence modifier, instead of your Strength or Dexterity modifier, for the attack and damage rolls.\n"
            "Weapon Knowledge. You gain proficiency with Martial weapons. You can use a weapon with which you have proficiency as a Spellcasting Focus for your Artificer spells."
        )
        return description


class SteelDefender(Feature):
    def __init__(self):
        super().__init__(name="Steel Defender", origin="Battle Smith Artificer Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your tinkering has borne you a companion, a Steel Defender (see the stat block). You determine the defender's appearance and whether it has two legs or four; your choices don't affect the defender's game statistics.\n"
            "The defender is Friendly to you and your allies and obeys you. It vanishes if you die.\n"
            "The Defender in Combat. In combat, the defender acts during your turn. It can move and take its Reaction on its own, but the only action it takes is the Dodge action unless you take a Bonus Action to command it to take an action. If you have the Incapacitated condition, the defender acts on its own and isn't limited to the Dodge action.\n"
            "Restoring or Replacing the Defender. If the defender has died within the last hour, you can take a Magic action to touch it and expend a spell slot. The defender returns to life after 1 minute with all its Hit Points restored.\n"
            "Whenever you finish a Long Rest, you can create a new defender if you have Smith's Tools in hand. If you already have a defender from this feature, the first one vanishes.\n"
            "Steel Defender\n"
            "Medium Construct\n"
            "Armor Class: 12 + your Intelligence modifier\n"
            "Hit Points: HP 5 + five times your Artificer level (the defender has a number of Hit Dice [d8s] equal to your Artificer level)\n"
            "Speed: Speed 40 ft.\n"
            "STR (Mod/Save)	DEX (Mod/Save)	CON (Mod/Save)	INT (Mod/Save)	WIS (Mod/Save)	CHA (Mod/Save)\n"
            "14 (+2/+2)	12 (+1/+1)	14 (+2/+2)	4 (−3/-3)	10 (+0/+0)	6 (-2/-2)\n"
            "Immunities: Poison; Charmed, Exhaustion, Poisoned\n"
            "Senses: Darkvision 60 ft., Passive Perception 10\n"
            "Languages: Understands the languages you know\n"
            "Challenge Rating: None (XP 0; PB equals your Proficiency Bonus)\n"
            "Traits\n"
            "Steel Bond. Add your Proficiency Bonus to any ability check or saving throw the Steel Defender makes.\n"
            "Actions\n"
            "Force-Empowered Rend. Melee Attack Roll: Bonus equals your spell attack modifier, reach 5 ft. Hit: 1d8 + 2 plus your Intelligence modifier Force damage.\n"
            "Repair (3/Day). The defender, or one Construct or object it can see within 5 feet of it, regains a number of Hit Points equal to 2d8 plus your Intelligence modifier.\n"
            "Reactions\n"
            "Deflect Attack. Trigger: A creature the defender can see within 5 feet of it makes an attack roll targeting a different creature. Response: The triggering creature makes the attack roll with Disadvantage."
        )
        return description


class BattleSmithExtraAttack(Feature):
    def __init__(self):
        super().__init__(name="Extra Attack", origin="Battle Smith Artificer Level 5")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can attack twice instead of once whenever you take the Attack action on your turn. You can forgo one of your attacks when you take the Attack action to command your Steel Defender to take the Force-Empowered Rend action."
        return description


class ArcaneJolt(Feature):
    def __init__(self):
        super().__init__(name="Arcane Jolt", origin="Battle Smith Artificer Level 9")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        intelligence_modifier = character_stat_block.get_ability_modifier(Ability.INTELLIGENCE)
        uses = max(1, intelligence_modifier)
        description = (
            "When either you hit a target with an attack roll using a magic weapon or your Steel Defender hits a target, you can channel magical energy through the strike to create one of the following effects:\n"
            "Destructive Energy. The target takes an extra 2d6 Force damage.\n"
            "Restorative Energy. Choose one creature or object you can see within 30 feet of the target. Healing energy flows into the chosen recipient, restoring 2d6 Hit Points to it.\n"
            "You can use this energy a number of times equal to your Intelligence modifier (minimum of once), but you can do so no more than once per turn. You regain all expended uses when you finish a Long Rest."
        )
        return StringUtils.add_boxes(description, uses, regain_all_on="long rest")


class ImprovedDefender(Feature):
    def __init__(self):
        super().__init__(
            name="Improved Defender", origin="Battle Smith Artificer Level 15"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your Arcane Jolt and Steel Defender have become more powerful, granting these benefits.\n"
            "Improved Jolt. The extra damage and healing of your Arcane Jolt both increase to 4d6.\n"
            "Improved Deflection. Whenever your Steel Defender uses its Deflect Attack, the attacker takes Force damage equal to 1d4 plus your Intelligence modifier."
        )
        return description
