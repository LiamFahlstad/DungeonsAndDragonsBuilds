import Definitions
from Definitions import Ability
from Features.BaseFeatures import TextFeature
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils

SORCERER_HIT_DIE = 6


class Spellcasting(TextFeature):
    def __init__(self):
        super().__init__(name="Spellcasting", origin="Sorcerer Level 1")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Spellcasting\n"
            "    * Replacing Cantrips: Change one when you gain a Sorcerer level.\n"
            "    * Replacing Spells: Change one whenever you gain a Sorcerer level.\n"
            "    * Regaining Spell Slots: You regain all expended spell slots when you finish a Long Rest.\n"
            "    * Spellcasting Ability: Charisma"
        )
        return description


class InnateSorcery(TextFeature):
    def __init__(self):
        super().__init__(name="Innate Sorcery", origin="Sorcerer Level 1")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "An event in your past left an indelible mark on you, infusing you with simmering magic. As a Bonus Action, you can unleash that magic for 1 minute, during which you gain the following benefits:\n"
            "The spell save DC of your Sorcerer spells increases by 1.\n"
            "You have Advantage on the attack rolls of Sorcerer spells you cast.\n"
            "You can use this feature twice, and you regain all expended uses of it when you finish a Long Rest."
        )
        return StringUtils.add_boxes(description, 2, reset="long rest")


class FontOfMagic(TextFeature):
    def __init__(self):
        super().__init__(name="Font of Magic", origin="Sorcerer Level 2")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        sorcerer_level = character_stat_block.get_class_level(
            Definitions.CharacterClass.SORCERER
        )
        sorcery_points = sorcerer_level
        description = (
            "Rules for Sorcery Points:\n"
            "    * You regain all expended Sorcery Points when you finish a Long Rest.\n"
            "    * Using Sorcery Points: You can use your Sorcery Points to fuel the options below, along with other features, such as Metamagic, that use those points.\n"
            "    * Converting Spell Slots to Sorcery Points: You can expend a spell slot to gain a number of Sorcery Points equal to the slot's level (no action required).\n"
            "    * Creating Spell Slots: As a Bonus Action, you can transform unexpended Sorcery Points into one spell slot. The Creating Spell Slots table shows the cost of creating a spell slot of a given level, and it lists the minimum Sorcerer level you must be to create a slot. Any spell slot you create with this feature vanishes when you finish a Long Rest.\n"
            "   Spell Slot Level | Sorcery Point Cost | Minimum Sorcerer Level\n"
            "   -----------------|--------------------|-----------------------\n"
            "           1        |         2          |           2           \n"
            "           2        |         3          |           3           \n"
            "           3        |         5          |           5           \n"
            "           4        |         6          |           7           \n"
            "           5        |         7          |           9           "
        )
        return StringUtils.add_boxes(description, sorcery_points, reset="long rest")


class Metamagic(TextFeature):
    def __init__(self):
        super().__init__(name="Metamagic", origin="Sorcerer Level 2")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        sorcerer_level = character_stat_block.get_class_level(
            Definitions.CharacterClass.SORCERER
        )
        if sorcerer_level < 10:
            metamaagic_options = 2
        elif sorcerer_level < 20:
            metamaagic_options = 4
        else:
            metamaagic_options = 6
        description = (
            f"Because your magic flows from within, you can alter your spells to suit your needs; You have {metamaagic_options} options to temporarily modify spells you cast. To use an option, you must spend the number of Sorcery Points that it costs.\n"
            "You can use only one Metamagic option on a spell when you cast it unless otherwise noted in one of those options.\n"
            "Whenever you gain a Sorcerer level, you can replace one of your Metamagic options with one you don't know."
        )
        return description


class SorcerousRestoration(TextFeature):
    def __init__(self):
        super().__init__(name="Sorcerous Restoration", origin="Sorcerer Level 5")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you finish a Short Rest, you can regain expended Sorcery Points, but no more than a number equal to half your Sorcerer level (round down). Once you use this feature, you can't do so again until you finish a Long Rest."
        return description


class SorceryIncarnate(TextFeature):
    def __init__(self):
        super().__init__(name="Sorcery Incarnate", origin="Sorcerer Level 7")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "If you have no uses of Innate Sorcery left, you can use it if you spend 2 Sorcery Points when you take the Bonus Action to activate it.\n"
            "In addition, while your Innate Sorcery feature is active, you can use up to two of your Metamagic options on each spell you cast."
        )
        return description


class ArcaneApotheosis(TextFeature):
    def __init__(self):
        super().__init__(name="Arcane Apotheosis", origin="Sorcerer Level 20")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "While your Innate Sorcery feature is active, you can use one Metamagic option on each of your turns without spending Sorcery Points on it."
        return description


### Aberrant Sorcery Features Generated Below ###


class TelepathicSpeech(TextFeature):
    def __init__(self):
        super().__init__(name="Telepathic Speech", origin="Aberrant Sorcery Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can form a telepathic connection between your mind and the mind of another. As a Bonus Action, choose one creature you can see within 30 feet of yourself. You and the chosen creature can communicate telepathically with each other while the two of you are within a number of miles of each other equal to your Charisma modifier (minimum of 1 mile). To understand each other, you each must mentally use a language the other knows.\n"
            "The telepathic connection lasts for a number of minutes equal to your Sorcerer level. It ends early if you use this ability to form a connection with a different creature."
        )
        return description


class PsionicSorcery(TextFeature):
    def __init__(self):
        super().__init__(name="Psionic Sorcery", origin="Aberrant Sorcery Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you cast any level 1+ spell from your Psionic Spells feature, you can cast it by expending a spell slot as normal or by spending a number of Sorcery Points equal to the spell’s level. If you cast the spell using Sorcery Points, it requires no Verbal or Somatic components, and it requires no Material components unless they are consumed by the spell or have a cost specified in it."
        return description


class PsychicDefenses(TextFeature):
    def __init__(self):
        super().__init__(name="Psychic Defenses", origin="Aberrant Sorcery Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You have Resistance to Psychic damage, and you have Advantage on saving throws to avoid or end the Charmed or Frightened condition."
        return description


class RevelationinFlesh(TextFeature):
    def __init__(self):
        super().__init__(name="Revelation in Flesh", origin="Aberrant Sorcery Level 14")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can unleash the aberrant truth hidden within yourself. As a Bonus Action, you can spend 1 Sorcery Point or more to magically alter your body for 10 minutes. For each Sorcery Point you spend, you gain one of the following benefits of your choice, the effects of which last until the alteration ends.\n"
            "Aquatic Adaptation. You gain a Swim Speed equal to twice your Speed, and you can breathe underwater. Gills grow from your neck or flare behind your ears, and your fingers become webbed or you grow wriggling cilia.\n"
            "Glistening Flight. You gain a Fly Speed equal to your Speed, and you can hover. As you fly, your skin glistens with mucus or otherworldly light.\n"
            "See the Invisible. You can see any Invisible creature within 60 feet of yourself that isn’t behind Total Cover. Your eyes also turn black or become writhing sensory tendrils.\n"
            "Wormlike Movement. Your body, along with any equipment you are wearing or carrying, becomes slimy and pliable. You can move through any space as narrow as 1 inch, and you can spend 5 feet of movement to escape from nonmagical restraints or the Grappled condition."
        )
        return description


class WarpingImplosion(TextFeature):
    def __init__(self):
        super().__init__(name="Warping Implosion", origin="Aberrant Sorcery Level 18")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can unleash a space-warping anomaly. As a Magic action, you teleport to an unoccupied space you can see within 120 feet of yourself. Immediately after you disappear, each creature within 30 feet of the space you left must make a Strength saving throw against your spell save DC. On a failed save, a creature takes 3d10 Force damage and is pulled straight toward the space you left, ending in an unoccupied space as close to your former space as possible. On a successful save, the creature takes half as much damage only.\n"
            "Once you use this feature, you can’t do so again until you finish a Long Rest unless you spend 5 Sorcery Points (no action required) to restore your use of it."
        )
        return description


### Clockwork Sorcery Features Generated Below ###


class RestoreBalance(TextFeature):
    def __init__(self):
        super().__init__(name="Restore Balance", origin="Clockwork Sorcery Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        charisma_modifier = character_stat_block.get_ability_modifier(Ability.CHARISMA)
        uses = max(1, charisma_modifier)
        description = (
            "Your connection to the plane of absolute order allows you to equalize chaotic moments. When a creature you can see within 60 feet of yourself is about to roll a d20 with Advantage or Disadvantage, you can take a Reaction to prevent the roll from being affected by Advantage and Disadvantage.\n"
            "You can use this feature a number of times equal to your Charisma modifier (minimum of once), and you regain all expended uses when you finish a Long Rest."
        )
        return StringUtils.add_boxes(description, uses, reset="long rest")


class BastionOfLaw(TextFeature):
    def __init__(self):
        super().__init__(name="Bastion of Law", origin="Clockwork Sorcery Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can tap into the grand equation of existence to imbue a creature with a shimmering shield of order. As a Magic action, you can expend 1 to 5 Sorcery Points to create a magical ward around yourself or another creature you can see within 30 feet of yourself. The ward is represented by a number of d8s equal to the number of Sorcery Points spent to create it. When the warded creature takes damage, it can expend a number of those dice, roll them, and reduce the damage taken by the total rolled on those dice.\n"
            "The ward lasts until you finish a Long Rest or until you use this feature again."
        )
        return description


class TranceOfOrder(TextFeature):
    def __init__(self):
        super().__init__(name="Trance of Order", origin="Clockwork Sorcery Level 14")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain the ability to align your consciousness with the endless calculations of Mechanus. As a Bonus Action, you can enter this state for 1 minute. For the duration, attack rolls against you can’t benefit from Advantage, and whenever you make a D20 Test, you can treat a roll of 9 or lower on the d20 as a 10.\n"
            "Once you use this feature, you can’t use it again until you finish a Long Rest unless you spend 5 Sorcery Points (no action required) to restore your use of it."
        )
        return description


class ClockworkCavalcade(TextFeature):
    def __init__(self):
        super().__init__(
            name="Clockwork Cavalcade", origin="Clockwork Sorcery Level 18"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You momentarily summon spirits of order to expunge disorder around you. As a Magic action, you summon the spirits in a 30-foot Cube originating from you. The spirits look like modrons or other Constructs of your choice. The spirits are intangible and invulnerable, and they create the effects below within the Cube before vanishing. Once you use this action, you can’t use it again until you finish a Long Rest unless you spend 7 Sorcery Points (no action required) to restore your use of it.\n"
            "Heal. The spirits restore up to 100 Hit Points, divided as you choose among any number of creatures of your choice in the Cube.\n"
            "Repair. Any damaged objects entirely in the Cube are repaired instantly.\n"
            "Dispel. Every spell of level 6 and lower ends on creatures and objects of your choice in the Cube."
        )
        return description


### Draconic Sorcery Features Generated Below ###


class DraconicResilience(TextFeature):
    def __init__(self):
        super().__init__(name="Draconic Resilience", origin="Draconic Sorcerer Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "The magic in your body manifests physical traits of your draconic gift. Your Hit Point maximum increases by 3, and it increases by 1 whenever you gain another Sorcerer level.\n"
            "Parts of you are also covered by dragon-like scales. While you aren’t wearing armor, your base Armor Class equals 10 plus your Dexterity and Charisma modifiers."
        )
        return description


class ElementalAffinity(TextFeature):
    def __init__(self):
        super().__init__(name="Elemental Affinity", origin="Draconic Sorcerer Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your draconic magic has an affinity with a damage type associated with dragons. Choose one of those types: Acid, Cold, Fire, Lightning, or Poison.\n"
            "You have Resistance to that damage type, and when you cast a spell that deals damage of that type, you can add your Charisma modifier to one damage roll of that spell."
        )
        return description


class DragonWings(TextFeature):
    def __init__(self):
        super().__init__(name="Dragon Wings", origin="Draconic Sorcerer Level 14")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "As a Bonus Action, you can cause draconic wings to appear on your back. The wings last for 1 hour or until you dismiss them (no action required). For the duration, you have a Fly Speed of 60 feet.\n"
            "Once you use this feature, you can’t use it again until you finish a Long Rest unless you spend 3 Sorcery Points (no action required) to restore your use of it."
        )
        return description


class DragonCompanion(TextFeature):
    def __init__(self):
        super().__init__(name="Dragon Companion", origin="Draconic Sorcerer Level 18")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can cast Summon Dragon without a Material component. You can also cast it once without a spell slot, and you regain the ability to cast it in this way when you finish a Long Rest.\n"
            "Whenever you start casting the spell, you can modify it so that it doesn’t require Concentration. If you do so, the spell’s duration becomes 1 minute for that casting."
        )
        return description


### Spellfire Sorcerer Features Generated Below ###


class SpellfireBurst(TextFeature):
    def __init__(self):
        super().__init__(name="Spellfire Burst", origin="Spellfire Sorcerer Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you spend at least 1 Sorcery Point as part of a Magic action or a Bonus Action on your turn, you can unleash one of the following magical effects of your choice. You can do so only once per turn.\n"
            "Bolstering Flames. You or one creature you can see within 30 feet of yourself gains Temporary Hit Points equal to 1d4 plus your Charisma modifier.\n"
            "Radiant Fire. One creature you can see within 30 feet of yourself takes 1d4 Fire or Radiant damage (your choice)."
        )
        return description


class AbsorbSpells(TextFeature):
    def __init__(self):
        super().__init__(name="Absorb Spells", origin="Spellfire Sorcerer Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You always have Counterspell prepared.\n"
            "Additionally, whenever a target fails the saving throw against a Counterspell you cast, you regain 1d4 Sorcery Points."
        )
        return description


class HonedSpellfire(TextFeature):
    def __init__(self):
        super().__init__(name="Honed Spellfire", origin="Spellfire Sorcerer Level 14")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Your Spellfire Burst improves. You add your Sorcerer level to the Temporary Hit Points gained from Bolstering Flames, and the damage of your Radiant Fire increases to 1d8."
        return description


class CrownOfSpellfire(TextFeature):
    def __init__(self):
        super().__init__(
            name="Crown of Spellfire", origin="Spellfire Sorcerer Level 18"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you use Innate Sorcery, you can alter it and infuse yourself with the essence of spellfire, gaining the following benefits while this use of Innate Sorcery is active. Once you use this feature to alter Innate Sorcery, you can’t use it again until you finish a Long Rest unless you spend 5 Sorcery Points (no action required) to restore your use of it.\n"
            "Burning Life Force. Once per turn when you are hit by an attack roll, you can expend a number of Hit Point Dice, up to a maximum equal to your Charisma modifier (minimum of one). Roll the expended dice, and reduce the amount of damage from that attack equal to the total rolled.\n"
            "Flight. You gain a Fly Speed of 60 feet and can hover.\n"
            "Spell Avoidance. When you’re subjected to a spell or magical effect that allows you to make a saving throw to take only half damage, you instead take no damage if you succeed on the save and only half damage if you fail. You can’t use this benefit if you have the Incapacitated condition."
        )
        return description


### Wild Magic Sorcerer Features Generated Below ###


class WildMagicSurge(TextFeature):
    def __init__(self):
        super().__init__(name="Wild Magic Surge", origin="Wild Magic Sorcerer Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your spellcasting can unleash surges of untamed magic. Once per turn, you can roll 1d20 immediately after you cast a Sorcerer spell with a spell slot. If you roll a 20, roll on the Wild Magic Surge table to create a magical effect.\n"
            "If the magical effect is a spell, it is too wild to be affected by your Metamagic."
        )
        return description


class TidesOfChaos(TextFeature):
    def __init__(self):
        super().__init__(name="Tides of Chaos", origin="Wild Magic Sorcerer Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can manipulate chaos itself to give yourself Advantage on one D20 Test before you roll the d20. Once you do so, you must cast a Sorcerer spell with a spell slot or finish a Long Rest before you can use this feature again.\n"
            "If you do cast a Sorcerer spell with a spell slot before you finish a Long Rest, you automatically roll on the Wild Magic Surge table."
        )
        return description


class BendLuck(TextFeature):
    def __init__(self):
        super().__init__(name="Bend Luck", origin="Wild Magic Sorcerer Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You have the ability to twist fate using your wild magic. Immediately after another creature you can see rolls the d20 for a D20 Test, you can take a Reaction and spend 1 Sorcery Point to roll 1d4 and apply the number rolled as a bonus or penalty (your choice) to the d20 roll."
        return description


class ControlledChaos(TextFeature):
    def __init__(self):
        super().__init__(name="Controlled Chaos", origin="Wild Magic Sorcerer Level 14")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You gain a modicum of control over the surges of your wild magic. Whenever you roll on the Wild Magic Surge table, you can roll twice and use either number."
        return description


class TamedSurge(TextFeature):
    def __init__(self):
        super().__init__(name="Tamed Surge", origin="Wild Magic Sorcerer Level 18")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Immediately after you cast a Sorcerer spell with a spell slot, you can create an effect of your choice from the Wild Magic Surge table instead of rolling on that table. You can choose any effect in the table except for the final row, and if the chosen effect involves a roll, you must make it.\n"
            "Once you use this feature, you can’t do so again until you finish a Long Rest."
        )
        return description


### Shadow Sorcerer Features Generated Below ###


class ShadowSpells(TextFeature):
    def __init__(self):
        super().__init__(name="Shadow Spells", origin="Shadow Sorcerer Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you reach a Sorcerer level specified in the Shadow Spells table, you thereafter always have the listed spells prepared.\n"
            "Shadow Spells\n"
            "Sorcerer Level	Spells\n"
            "3	Bane, Darkness, Inflict Wounds, Pass Without Trace\n"
            "5	Hunger of Hadar, Nondetection\n"
            "7	Greater Invisibility, Phantasmal Killer\n"
            "9	Contagion, Creation"
        )
        return description


class PowerOfShadow(TextFeature):
    def __init__(self):
        super().__init__(name="Power of Shadow", origin="Shadow Sorcerer Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain the following benefits.\n"
            "Eyes of the Dark. You have Darkvision with a range of 120 feet and Blindsight with a range of 10 feet. In addition, if a spell you cast creates an area of Darkness, you can see normally through that spell’s Darkness.\n"
            "Strength of the Grave. If you would drop to 0 Hit Points and not die outright, you can make a Charisma saving throw (DC 5 plus the damage taken). On a successful save, your Hit Points instead change to a number equal to your Charisma modifier plus your Sorcerer level. After you succeed on this save, you can’t use this benefit again until you finish a Long Rest."
        )
        return description


class BeastsOfIllOmen(TextFeature):
    def __init__(self):
        super().__init__(name="Beasts of Ill Omen", origin="Shadow Sorcerer Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can call forth a howling creature of shadow to hound your foes. You can spend 3 Sorcery Points to cast Summon Beast as a Bonus Action without expending a spell slot, without preparing the spell, and without Material components. The summoned creature appears as a beast made of shadow, and enemies within 5 feet of the summoned creature have Disadvantage on saving throws against spells you cast.\n"
            "Whenever you cast the spell, you can modify it so that it doesn’t require Concentration. If you do so, the spell’s duration becomes 1 minute for that casting, and the spell ends early if you cast the spell again."
        )
        return description


class ShadowWalk(TextFeature):
    def __init__(self):
        super().__init__(name="Shadow Walk", origin="Shadow Sorcerer Level 14")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "While you are in Dim Light or Darkness, you can take a Bonus Action to teleport up to 120 feet to an unoccupied space you can see that is also in Dim Light or Darkness."
        return description


class UmbralForm(TextFeature):
    def __init__(self):
        super().__init__(name="Umbral Form", origin="Shadow Sorcerer Level 18")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you use Innate Sorcery, you can adopt a shadowy form, gaining the benefits below while your Innate Sorcery is active or until you end the form (no action required). Once you use this feature, you can’t use it again until you finish a Long Rest unless you spend 6 Sorcery Points (no action required) to restore your use of it.\n"
            "Incorporeal Movement. You can move through creatures and objects as if they were Difficult Terrain, but you take 1d10 Force damage if you end your turn inside a creature or an object.\n"
            "Shadow Resilience. You have Resistance to all damage except Force and Radiant damage."
        )
        return description
