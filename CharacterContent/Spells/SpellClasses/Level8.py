"""Level 8 spells as classes (CharacterContent/Spells/SpellFactory/ClassSpell.py),
which SpellFactory uses instead of their JSON records. Written by
CharacterContent/Spells/SpellClassConverter.py; edit them by hand from
then on: each class is its spell's one source."""

from CharacterContent.Spells.SpellFactory.ClassSpell import (
    ClassSpell,
    RecordStamp,
    SpellRules,
)
from CharacterContent.Spells.SpellFactory.Enums import (
    CastingTimeType,
    DurationType,
    RangeType,
    School,
)
from CharacterContent.Spells.SpellFactory.SpellFields import (
    CastingTime,
    Components,
    Duration,
    Range,
)
from Core.Definitions import CharacterClass
from Model.Content.Feature import FeatureTarget


class AbiDalzimsHorridWilting(ClassSpell):
    rules = SpellRules(
        name="Abi-Dalzim's Horrid Wilting",
        level=8,
        school=School.NECROMANCY,
        classes=(CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 150),
        components=Components(verbal=True, somatic=True, material="a bit of sponge"),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Xanathar's Guide to Everything",
        description=(
            "You draw the moisture from every creature in a 30-foot cube centered on a point you choose within range. Each creature in that area must make a Constitution saving throw. Constructs and undead aren't affected, and plants and water elementals make this saving throw with disadvantage. A creature takes 12d8 necrotic damage on a failed save, or half as much damage on a successful one.\n"
            "Nonmagical plants in the area that aren't creatures, such as trees and shrubs, wither and die instantly."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "4a63fb9fc9b15a2b")


class AnimalShapes(ClassSpell):
    rules = SpellRules(
        name="Animal Shapes",
        level=8,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.DRUID,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 30),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.HOUR, 24),
        source="Player's Handbook",
        description=(
            "Choose any number of willing creatures that you can see within range. Each target shape-shifts into a Large or smaller Beast of your choice that has a Challenge Rating of 4 or lower. You can choose a different form for each target. On later turns, you can take a Magic action to transform the targets again.\n"
            "A target’s game statistics are replaced by the chosen Beast’s statistics, but the target retains its creature type; Hit Points; Hit Point Dice; alignment; ability to communicate; and Intelligence, Wisdom, and Charisma scores. The target’s actions are limited by the Beast form’s anatomy, and it can’t cast spells. The target’s equipment melds into the new form, and the target can’t use any of that equipment while in that form.\n"
            "The target gains a number of Temporary Hit Points equal to the Hit Points of the first form into which it shape-shifts. These Temporary Hit Points vanish if any remain when the spell ends. The transformation lasts for the duration or until the target ends it as a Bonus Action."
        ),
        usage_tags=("heal",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "a493ba15f0cb53d7")


class AntimagicField(ClassSpell):
    rules = SpellRules(
        name="Antimagic Field",
        level=8,
        school=School.ABJURATION,
        classes=(CharacterClass.CLERIC, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True, material="iron filings"),
        duration=Duration(DurationType.HOUR, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "An aura of antimagic surrounds you in 10-foot Emanation. No one can cast spells, take Magic actions, or create other magical effects inside the aura, and those things can’t target or otherwise affect anything inside it. Magical properties of magic items don’t work inside the aura or on anything inside it.\n"
            "Areas of effect created by spells or other magic can’t extend into the aura, and no one can teleport into or out of it or use planar travel there. Portals close temporarily while in the aura.\n"
            "Ongoing spells, except those cast by an Artifact or a deity, are suppressed in the area. While an effect is suppressed, it doesn’t function, but the time it spends suppressed counts against its duration.\n"
            "Dispel Magic has no effect on the aura, and the auras created by different Antimagic Field spells don’t nullify each other."
        ),
        usage_tags=("buff",),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "f4803e028b0647aa")


class AntipathySympathy(ClassSpell):
    rules = SpellRules(
        name="Antipathy/Sympathy",
        level=8,
        school=School.ENCHANTMENT,
        classes=(CharacterClass.BARD, CharacterClass.DRUID, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.HOUR, 1),
        range=Range(RangeType.FOOT, 60),
        components=Components(
            verbal=True, somatic=True, material="a mix of vinegar and honey"
        ),
        duration=Duration(DurationType.DAY, 10),
        source="Player's Handbook",
        description=(
            "As you cast the spell, choose whether it creates antipathy or sympathy, and target one creature or object that is Huge or smaller. Then specify a kind of creature, such as red dragons, goblins, or vampires. A creature of the chosen kind makes a Wisdom saving throw when it comes within 120 feet of the target. Your choice of antipathy or sympathy determines what happens to a creature when it fails that save:\n"
            "Antipathy. The creature has the Frightened condition. The Frightened creature must use its movement on its turns to get as far away as possible from the target, moving by the safest route.\n"
            "Sympathy. The creature has the Charmed condition. The Charmed creature must use its movement on its turns to get as close as possible to the target, moving by the safest route. If the creature is within 5 feet of the target, the creature can’t willingly move away. If the target damages the Charmed creature, that creature can make a Wisdom saving throw to end the effect, as described below.\n"
            "Ending the Effect. If the Frightened or Charmed creature ends its turn more than 120 feet away from the target, the creature makes a Wisdom saving throw. On a successful save, the creature is no longer affected by the target. A creature that successfully saves against this effect is immune to it for 1 minute, after which it can be affected again."
        ),
        usage_tags=("control",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "e66b37a252edc453")


class Befuddlement(ClassSpell):
    rules = SpellRules(
        name="Befuddlement",
        level=8,
        school=School.ENCHANTMENT,
        classes=(
            CharacterClass.BARD,
            CharacterClass.DRUID,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 150),
        components=Components(
            verbal=True, somatic=True, material="a key ring with no keys"
        ),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "You blast the mind of a creature that you can see within range. The target makes an Intelligence saving throw.\n"
            "On a failed save, the target takes 10d12 Psychic damage and can't cast spells or take the Magic action. At the end of every 30 days, the target repeats the save, ending the effect on a success. The effect can also be ended by the Greater Restoration , Heal , or Wish spell.\n"
            "On a successful save, the target takes half as much damage only."
        ),
        usage_tags=("control", "damage"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "c0517632abd2dcc3")


class Clone(ClassSpell):
    rules = SpellRules(
        name="Clone",
        level=8,
        school=School.NECROMANCY,
        classes=(CharacterClass.WIZARD,),
        casting_time=CastingTime(CastingTimeType.HOUR, 1),
        range=Range(RangeType.TOUCH),
        components=Components(
            verbal=True,
            somatic=True,
            material="a diamond worth 1,000+ GP, which the spell consumes, and a sealable vessel worth 2,000+ GP that is large enough to hold the creature being cloned",
        ),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "You touch a creature or at least 1 cubic inch of its flesh. An inert duplicate of that creature forms inside the vessel used in the spell’s casting and finishes growing after 120 days; you choose whether the finished clone is the same age as the creature or younger. The clone remains inert and endures indefinitely while its vessel remains undisturbed.\n"
            "If the original creature dies after the clone finishes forming, the creature’s soul transfers to the clone if the soul is free and willing to return. The clone is physically identical to the original and has the same personality, memories, and abilities, but none of the original’s equipment. The creature’s original remains, if any, become inert and can’t be revived, since the creature’s soul is elsewhere."
        ),
        usage_tags=("heal",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "6007f4030fca9985")


class ControlWeather(ClassSpell):
    rules = SpellRules(
        name="Control Weather",
        level=8,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.CLERIC, CharacterClass.DRUID, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.MINUTE, 10),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True, material="burning incense"),
        duration=Duration(DurationType.HOUR, 8, concentration=True),
        source="Player's Handbook",
        description=(
            "You take control of the weather within 5 miles of you for the duration. You must be outdoors to cast this spell, and it ends early if you go indoors.\n"
            "When you cast the spell, you change the current weather conditions, which are determined by the DM. You can change precipitation, temperature, and wind. It takes 1d4 × 10 minutes for the new conditions to take effect. Once they do so, you can change the conditions again. When the spell ends, the weather gradually returns to normal.\n"
            "When you change the weather conditions, find a current condition on the following tables and change its stage by one, up or down. When changing the wind, you can change its direction."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "a2cfd99186c81fe8")


class Demiplane(ClassSpell):
    rules = SpellRules(
        name="Demiplane",
        level=8,
        school=School.CONJURATION,
        classes=(
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(somatic=True),
        duration=Duration(DurationType.HOUR, 1),
        source="Player's Handbook",
        description=(
            "You create a shadowy Medium door on a flat solid surface that you can see within range. This door can be opened and closed, and it leads to a demiplane that is an empty room 30 feet in each dimension, made of wood or stone (your choice).\n"
            "When the spell ends, the door vanishes, and any objects inside the demiplane remain there. Any creatures inside also remain unless they opt to be shunted through the door as it vanishes, landing with the Prone condition in the unoccupied spaces closest to the door’s former space.\n"
            "Each time you cast this spell, you can create a new demiplane or connect the shadowy door to a demiplane you created with a previous casting of this spell. Additionally, if you know the nature and contents of a demiplane created by a casting of this spell by another creature, you can connect the shadowy door to that demiplane instead."
        ),
        usage_tags=("heal",),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "a034175a77811738")


class DominateMonster(ClassSpell):
    rules = SpellRules(
        name="Dominate Monster",
        level=8,
        school=School.ENCHANTMENT,
        classes=(
            CharacterClass.BARD,
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.HOUR, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "One creature you can see within range must succeed on a Wisdom saving throw or have the Charmed condition for the duration. The target has Advantage on the save if you or your allies are fighting it. Whenever the target takes damage, it repeats the save, ending the spell on itself on a success.\n"
            "You have a telepathic link with the Charmed target while the two of you are on the same plane of existence. On your turn, you can use this link to issue commands to the target (no action required), such as “Attack that creature,” “Move over there,” or “Fetch that object.” The target does its best to obey on its turn. If it completes an order and doesn’t receive further direction from you, it acts and moves as it likes, focusing on protecting itself.\n"
            "You can command the target to take a Reaction but must take your own Reaction to do so.\n"
            "Using a Higher-Level Spell Slot. Your Concentration can last longer with a level 9 spell slot (up to 8 hours)."
        ),
        usage_tags=("buff", "control"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "581c4eacb3aea97e")


class Earthquake(ClassSpell):
    rules = SpellRules(
        name="Earthquake",
        level=8,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.CLERIC, CharacterClass.DRUID, CharacterClass.SORCERER),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 500),
        components=Components(verbal=True, somatic=True, material="a fractured rock"),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "Choose a point on the ground that you can see within range. For the duration, an intense tremor rips through the ground in a 100-foot-radius circle centered on that point. The ground there is Difficult Terrain.\n"
            "When you cast this spell and at the end of each of your turns for the duration, each creature on the ground in the area makes a Dexterity saving throw. On a failed save, a creature has the Prone condition, and its Concentration is broken.\n"
            "You can also cause the effects below.\n"
            "Fissures. A total of 1d6 fissures open in the spell’s area at the end of the turn you cast it. You choose the fissures’ locations, which can’t be under structures. Each fissure is 1d10 × 10 feet deep and 10 feet wide, and it extends from one edge of the spell’s area to another edge. A creature in the same space as a fissure must succeed on a Dexterity saving throw or fall in. A creature that successfully saves moves with the fissure’s edge as it opens.\n"
            "Structures. The tremor deals 50 Bludgeoning damage to any structure in contact with the ground in the area when you cast the spell and at the end of each of your turns until the spell ends. If a structure drops to 0 Hit Points, it collapses.\n"
            "A creature within a distance from a collapsing structure equal to half the structure’s height makes a Dexterity saving throw. On a failed save, the creature takes 12d6 Bludgeoning damage, has the Prone condition, and is buried in the rubble, requiring a DC 20 Strength (Athletics) check as an action to escape. On a successful save, the creature takes half as much damage only."
        ),
        usage_tags=("control", "damage"),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "ae1a7f756eb75dfa")


class EntrancingMirrors(ClassSpell):
    rules = SpellRules(
        name="Entrancing Mirrors",
        level=8,
        school=School.ILLUSION,
        classes=(
            CharacterClass.BARD,
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 90),
        components=Components(verbal=True, somatic=True, material="a mirror shard"),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Arcana Unleashed",
        description=(
            "You create dozens of illusory mirrors to confuse up to three creatures of your choice that you can see within range.\n"
            "Each target makes an Intelligence saving throw. On a failed save, a target takes 7d6 Psychic damage and has the Stunned condition. While the target is Stunned, its Speed is halved. On a successful save, a target takes half as much damage only.\n"
            "A Stunned target repeats the Intelligence saving throw at the end of each of its turns, ending the spell on itself on a success."
        ),
        usage_tags=("control", "damage"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "7438c11cfb41167d")


class Feeblemind(ClassSpell):
    rules = SpellRules(
        name="Feeblemind",
        level=8,
        school=School.ENCHANTMENT,
        classes=(
            CharacterClass.BARD,
            CharacterClass.DRUID,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 150),
        components=Components(
            verbal=True,
            somatic=True,
            material="a handful of clay, crystal, glass, or mineral spheres",
        ),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "You blast the mind of a creature that you can see within range, attempting to shatter its intellect and personality. The target takes 4d6 psychic damage and must make an Intelligence saving throw.\n"
            "On a failed save, the creature's Intelligence and Charisma scores become 1. The creature can't cast spells, activate magic items, understand language, or communicate in any intelligible way. The creature can, however, identify its friends, follow them, and even protect them.\n"
            "At the end of every 30 days, the creature can repeat its saving throw against this spell. If it succeeds on its saving throw, the spell ends. The spell can also be ended by Greater Restoration , Heal , or Wish ."
        ),
        usage_tags=("control", "damage", "utility"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "34e9bbb1b8ef574a")


class Glibness(ClassSpell):
    rules = SpellRules(
        name="Glibness",
        level=8,
        school=School.ENCHANTMENT,
        classes=(CharacterClass.BARD, CharacterClass.WARLOCK),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True),
        duration=Duration(DurationType.HOUR, 1),
        source="Player's Handbook",
        description="Until the spell ends, when you make a Charisma check, you can replace the number you roll with a 15. Additionally, no matter what you say, magic that would determine if you are telling the truth indicates that you are being truthful.",
        usage_tags=("buff",),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "20fae216cd5afba3")


class HolyAura(ClassSpell):
    rules = SpellRules(
        name="Holy Aura",
        level=8,
        school=School.ABJURATION,
        classes=(CharacterClass.CLERIC,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(
            verbal=True, somatic=True, material="a reliquary worth 1,000+ GP"
        ),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description="For the duration, you emit an aura in a 30-foot Emanation. While in the aura, creatures of your choice have Advantage on all saving throws, and other creatures have Disadvantage on attack rolls against them. In addition, when a Fiend or an Undead hits an affected creature with a melee attack roll, the attacker must succeed on a Constitution saving throw or have the Blinded condition until the end of its next turn.",
        usage_tags=("buff", "control", "damage"),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "36102c80463cc3fc")


class HolyStarOfMystra(ClassSpell):
    rules = SpellRules(
        name="Holy Star of Mystra",
        level=8,
        school=School.EVOCATION,
        classes=(CharacterClass.CLERIC, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.BONUS_ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Forgotten Realms - Heroes of Faerun",
        description=(
            "You create a glowing mote of energy that hovers above you for the duration. The mote sheds Bright Light in a 5-foot radius and Dim Light for an additional 5 feet.\n"
            "When you cast this spell and as a Bonus Action on later turns, you can unleash a shining bolt from the mote, targeting one creature within 120 feet of yourself. Make a ranged spell attack. On a hit, the target takes Force or Radiant damage (your choice) equal to 4d10 plus your spellcasting ability modifier.\n"
            "In addition, while the mote is present, you have Three-Quarters Cover, and if you succeed on a saving throw against a spell of level 7 or lower that targeted only you and didn’t create an area of effect, you can take a Reaction to deflect that spell back at the spell’s caster; the caster makes a saving throw against that spell using that caster’s own spell save DC."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "7eeff603ed08606d")


class IllusoryDragon(ClassSpell):
    rules = SpellRules(
        name="Illusory Dragon",
        level=8,
        school=School.ILLUSION,
        classes=(CharacterClass.WIZARD,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 120),
        components=Components(somatic=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Arcana Unleashed",
        description=(
            "By gathering threads of shadow material from the Shadowfell, you create a Huge shadowy dragon in an unoccupied space that you can see within range. The illusion lasts for the spell’s duration and occupies its space as if it were a creature. The illusion is tangible because of the shadow material used to create it but has Immunity to all damage and conditions.\n"
            "When the illusion appears, any enemy that can see it makes a Wisdom saving throw. On a failed save, the creature drops whatever it’s holding and has the Frightened condition for the duration. If a creature Frightened in this way ends its turn in a space where it doesn’t have line of sight to the illusion, the creature repeats the saving throw, ending the condition on itself on a success.\n"
            "As a Bonus Action, you can move the illusion up to 60 feet. At any point during its movement, you can cause the shadowy dragon to exhale a blast of energy in a 60-foot Cone. Each creature in the Cone makes an Intelligence saving throw, taking 6d6 Acid, Cold, Fire, Lightning, Necrotic, or Poison damage (your choice when you create the dragon) on a failed save or half as much damage on a successful one.\n"
            "A creature that takes a Study action to examine the dragon can determine that it is an illusion with a successful Intelligence (Investigation) check against your spell save DC. If a creature discerns the illusion for what it is, the creature can see through the image and has Advantage on saving throws to end the Frightened condition it caused and to resist its exhalation."
        ),
        usage_tags=("control", "damage"),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "c0db74d15671dc42")


class IncendiaryCloud(ClassSpell):
    rules = SpellRules(
        name="Incendiary Cloud",
        level=8,
        school=School.CONJURATION,
        classes=(CharacterClass.DRUID, CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 150),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "A swirling cloud of embers and smoke fills a 20-foot-radius Sphere centered on a point within range. The cloud’s area is Heavily Obscured. It lasts for the duration or until a strong wind (like that created by Gust of Wind ) disperses it.\n"
            "When the cloud appears, each creature in it makes a Dexterity saving throw, taking 10d8 Fire damage on a failed save or half as much damage on a successful one. A creature must also make this save when the Sphere moves into its space and when it enters the Sphere or ends its turn there. A creature makes this save only once per turn.\n"
            "The cloud moves 10 feet away from you in a direction you choose at the start of each of your turns."
        ),
        usage_tags=("control", "damage"),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "cb8ce875d34e048a")


class IronBody(ClassSpell):
    rules = SpellRules(
        name="Iron Body",
        level=8,
        school=School.TRANSMUTATION,
        classes=(
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.TOUCH),
        components=Components(
            verbal=True,
            somatic=True,
            material="diamond dust worth 250+ GP, which the spell consumes",
        ),
        duration=Duration(DurationType.HOUR, 1, concentration=True),
        source="Arcana Unleashed",
        description="One willing creature you touch transforms into living metal. Until the spell ends, the target’s Exhaustion level can’t increase; the target has Resistance to Bludgeoning, Fire, Piercing, and Slashing damage; and it has Immunity to Poison damage and the Paralyzed, Petrified, and Poisoned conditions. If the target is Paralyzed, Petrified, or Poisoned when you cast the spell, those conditions immediately end for the target.",
        usage_tags=("buff", "heal"),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "ffb2d922c07045b9")


class LightningRing(ClassSpell):
    rules = SpellRules(
        name="Lightning Ring",
        level=8,
        school=School.EVOCATION,
        classes=(
            CharacterClass.DRUID,
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.BONUS_ACTION),
        range=Range(RangeType.SELF),
        components=Components(
            verbal=True, somatic=True, material="a bit of fur and a glass ring"
        ),
        duration=Duration(DurationType.MINUTE, 10, concentration=True),
        source="Arcana Unleashed",
        description=(
            "A ring of crackling electricity fills a 10-foot Emanation originating from you. Whenever the Emanation enters a creature’s space and whenever a creature enters the Emanation or ends its turn there, you can force that creature to make a Constitution saving throw. On a failed save, the creature takes 3d6 Lightning damage plus 3d6 Thunder damage, and it has the Deafened condition for 1 minute. On a successful save, the creature takes half as much damage only.\n"
            "As a Magic action while the spell is active, you can emit a 60-foot-long, 5-foot-wide Line out from you in a direction you choose. Each creature in the Line makes a Dexterity saving throw, taking 6d6 Lightning damage on a failed save or half as much damage on a successful one."
        ),
        usage_tags=("control", "damage"),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "b7b8c05f30af7d3d")


class MaddeningDarkness(ClassSpell):
    rules = SpellRules(
        name="Maddening Darkness",
        level=8,
        school=School.EVOCATION,
        classes=(CharacterClass.WARLOCK, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 150),
        components=Components(
            verbal=True, material="a drop of pitch mixed with a drop of mercury"
        ),
        duration=Duration(DurationType.MINUTE, 10, concentration=True),
        source="Xanathar's Guide to Everything",
        description="Magical darkness spreads from a point you choose within range to fill a 60-foot-radius sphere until the spell ends. The darkness spreads around corners. A creature with darkvision can't see through this darkness. Nonmagical light, as well as light created by spells of 8th level or lower, can't illuminate the area. Shrieks, gibbering, and mad laughter can be heard within the sphere. Whenever a creature starts its turn in the sphere, it must make a Wisdom saving throw, taking 8d8 psychic damage on a failed save, or half as much damage on a successful one.",
        usage_tags=("damage", "utility"),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "abed6933b216d8a7")


class Maze(ClassSpell):
    rules = SpellRules(
        name="Maze",
        level=8,
        school=School.CONJURATION,
        classes=(CharacterClass.WIZARD,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 10, concentration=True),
        source="Player's Handbook",
        description=(
            "You banish a creature that you can see within range into a labyrinthine demiplane. The target remains there for the duration or until it escapes the maze.\n"
            "The target can take a Study action to try to escape. When it does so, it makes a DC 20 Intelligence (Investigation) check. If it succeeds, it escapes, and the spell ends.\n"
            "When the spell ends, the target reappears in the space it left or, if that space is occupied, in the nearest unoccupied space."
        ),
        usage_tags=("control",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "476d7497c0c35410")


class MightyFortress(ClassSpell):
    rules = SpellRules(
        name="Mighty Fortress",
        level=8,
        school=School.CONJURATION,
        classes=(CharacterClass.WIZARD,),
        casting_time=CastingTime(CastingTimeType.MINUTE, 1),
        range=Range(RangeType.MILE, 1),
        components=Components(
            verbal=True,
            somatic=True,
            material="a diamond worth at least 500 gp, which the spell consumes",
        ),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Xanathar's Guide to Everything",
        description=(
            "A fortress of stone erupts from a square area of ground of your choice that you can see within range. The area is 120 feet on each side, and it must not have any buildings or other structures on it. Any creatures in the area are harmlessly lifted up as the fortress rises.\n"
            "The fortress has four turrets with square bases, each one 20 feet on a side and 30 feet tall, with one turret on each corner. The turrets are connected to each other by stone walls that are each 80 feet long, creating an enclosed area. Each wall is 1 foot thick and is composed of panels that are 10 feet wide and 20 feet tall. Each panel is contiguous with two other panels or one other panel and a turret. You can place up to four stone doors in the fortress's outer wall.\n"
            "A small keep stands inside the enclosed area. The keep has a square base that is 50 feet on each side, and it has three floors with 10-foot-high ceilings. Each of the floors can be divided into as many rooms as you like, provided each room is at least 5 feet on each side. The floors of the keep are connected by stone staircases, its walls are 6 inches thick, and interior rooms can have stone doors or open archways as you choose. The keep is furnished and decorated however you like, and it contains sufficient food to serve a nine-course banquet for up to 100 people each day. Furnishings, food, and other objects created by this spell crumble to dust if removed from the fortress.\n"
            "A staff of one hundred invisible servants obeys any command given to them by creatures you designate when you cast the spell. Each servant functions as if created by the unseen servant spell.\n"
            "The walls, turrets, and keep are all made of stone that can be damaged. Each 10-foot by 10-foot section of stone has AC 15 and 30 hit points per inch of thickness. It is immune to poison and psychic damage. Reducing a section of stone to 0 hit points destroys it and might cause connected sections to buckle and collapse at the DM's discretion.\n"
            "After 7 days or when you cast this spell somewhere else, the fortress harmlessly crumbles and sinks back into the ground, leaving any creatures that were inside it safely on the ground.\n"
            "Casting this spell on the same spot once every 7 days for a year makes the fortress permanent."
        ),
        usage_tags=("utility", "summon"),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "b6435932e5373772")


class MindBlank(ClassSpell):
    rules = SpellRules(
        name="Mind Blank",
        level=8,
        school=School.ABJURATION,
        classes=(CharacterClass.BARD, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.TOUCH),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.HOUR, 24),
        source="Player's Handbook",
        description="Until the spell ends, one willing creature you touch has Immunity to Psychic damage and the Charmed condition. The target is also unaffected by anything that would sense its emotions or alignment, read its thoughts, or magically detect its location, and no spell - not even Wish - can gather information about the target, observe it remotely, or control its mind.",
        usage_tags=("heal",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "4122cdb97b5582c0")


class MomentOfPrescience(ClassSpell):
    rules = SpellRules(
        name="Moment of Prescience",
        level=8,
        school=School.DIVINATION,
        classes=(CharacterClass.WIZARD,),
        casting_time=CastingTime(
            CastingTimeType.REACTION,
            trigger="which you take when you fail a D20 Test or when a creature hits you with an attack roll",
        ),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Arcana Unleashed",
        description="You have a powerful sixth sense that guides you at just the right time. Turn the roll of your failed D20 Test into a 20, or turn the roll of the triggering attack roll into a 1.",
        usage_tags=("buff",),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "efa0d70de3c9a0bc")


class PowerWordStun(ClassSpell):
    rules = SpellRules(
        name="Power Word Stun",
        level=8,
        school=School.ENCHANTMENT,
        classes=(
            CharacterClass.BARD,
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "You overwhelm the mind of one creature you can see within range. If the target has 150 Hit Points or fewer, it has the Stunned condition. Otherwise, its Speed is 0 until the start of your next turn.\n"
            "The Stunned target makes a Constitution saving throw at the end of each of its turns, ending the condition on itself on a success."
        ),
        usage_tags=("control",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "b027caf26f8bf35e")


class Sunburst(ClassSpell):
    rules = SpellRules(
        name="Sunburst",
        level=8,
        school=School.EVOCATION,
        classes=(
            CharacterClass.CLERIC,
            CharacterClass.DRUID,
            CharacterClass.SORCERER,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 150),
        components=Components(
            verbal=True, somatic=True, material="a piece of sunstone"
        ),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "Brilliant sunlight flashes in a 60-foot-radius Sphere centered on a point you choose within range. Each creature in the Sphere makes a Constitution saving throw. On a failed save, a creature takes 12d6 Radiant damage and has the Blinded condition for 1 minute. On a successful save, it takes half as much damage only.\n"
            "A creature Blinded by this spell makes another Constitution saving throw at the end of each of its turns, ending the effect on itself on a success.\n"
            "This spell dispels Darkness in its area that was created by any spell."
        ),
        usage_tags=("control", "damage"),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "e846020f7270959e")


class Telepathy(ClassSpell):
    rules = SpellRules(
        name="Telepathy",
        level=8,
        school=School.DIVINATION,
        classes=(CharacterClass.WIZARD,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.UNLIMITED),
        components=Components(
            verbal=True, somatic=True, material="a pair of linked silver rings"
        ),
        duration=Duration(DurationType.HOUR, 24),
        source="Player's Handbook",
        description=(
            "You create a telepathic link between yourself and a willing creature with which you are familiar. The creature can be anywhere on the same plane of existence as you. The spell ends if you or the target are no longer on the same plane.\n"
            "Until the spell ends, you and the target can instantly share words, images, sounds, and other sensory messages with each other through the link, and the target recognizes you as the creature it is communicating with. The spell enables a creature to understand the meaning of your words and any sensory messages you send to it."
        ),
        usage_tags=("buff",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "eae05be35c591d0f")


class Tsunami(ClassSpell):
    rules = SpellRules(
        name="Tsunami",
        level=8,
        school=School.CONJURATION,
        classes=(CharacterClass.DRUID,),
        casting_time=CastingTime(CastingTimeType.MINUTE, 1),
        range=Range(RangeType.MILE, 1),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.ROUND, 6, concentration=True),
        source="Player's Handbook",
        description=(
            "A wall of water springs into existence at a point you choose within range. You can make the wall up to 300 feet long, 300 feet high, and 50 feet thick. The wall lasts for the duration.\n"
            "When the wall appears, each creature in its area makes a Strength saving throw, taking 6d10 Bludgeoning damage on a failed save or half as much damage on a successful one.\n"
            "At the start of each of your turns after the wall appears, the wall, along with any creatures in it, moves 50 feet away from you. Any Huge or smaller creature inside the wall or whose space the wall enters when it moves must succeed on a Strength saving throw or take 5d10 Bludgeoning damage. A creature can take this damage only once per round. At the end of the turn, the wall’s height is reduced by 50 feet, and the damage the wall deals on later rounds is reduced by 1d10. When the wall reaches 0 feet in height, the spell ends.\n"
            "A creature caught in the wall can move by swimming. Because of the wave’s force, though, the creature must succeed on a Strength (Athletics) check against your spell save DC to move at all. If it fails the check, it can’t move. A creature that moves out of the wall falls to the ground."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "d36fd76542b48c5a")


class DarkStar(ClassSpell):
    rules = SpellRules(
        name="Dark Star",
        level=8,
        school=School.EVOCATION,
        classes=(CharacterClass.WIZARD,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 150),
        components=Components(
            verbal=True,
            somatic=True,
            material="a shard of onyx and a drop of the caster's blood, both of which the spell consumes",
        ),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Explorer's Guide to Wildemount",
        description=(
            "This spell creates a sphere centered on a point you choose within range. The sphere can have a radius of up to 40 feet. The area within this sphere is filled with magical darkness and crushing gravitational force.\n"
            "For the duration, the spell's area is difficult terrain. A creature with darkvision can't see through the magical darkness, and nonmagical light can't illuminate it. No sound can be created within or pass through the area. Any creature or object entirely inside the sphere is immune to thunder damage, and creatures are deafened while entirely inside it. Casting a spell that includes a verbal component is impossible there.\n"
            "Any creature that enters the spell's area for the first time on a turn or starts its turn there must make a Constitution saving throw. The creature takes 8d10 force damage on a failed save or half as much damage on a successful save. A creature reduced to 0 hit points by this damage is disintegrated. A disintegrated creature and everything it is wearing and carrying, except magic items, are reduced to a pile of fine gray dust."
        ),
        usage_tags=("control", "damage", "utility"),
        target=FeatureTarget.AREA,
        school_note="Dunamancy:Graviturgy",
    )
    converted_from = RecordStamp("spells_dnd5e.json", "e52476bb36c1baf2")


class RealityBreak(ClassSpell):
    rules = SpellRules(
        name="Reality Break",
        level=8,
        school=School.CONJURATION,
        classes=(CharacterClass.WIZARD,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True, somatic=True, material="a crystal prism"),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Explorer's Guide to Wildemount",
        description=(
            "You shatter the barriers between realities and timelines, thrusting a creature into turmoil and madness. The target must succeed on a Wisdom saving throw, or it can't take reactions until the spell ends. The affected target must also roll a d10 at the start of each of its turns; the number rolled determines what happens to the target as shown on the Reality Break Effects table.\n"
            "At the end of each of its turns, the affected target can repeat the Wisdom saving throw, ending the spell on itself on a success\n"
            "Reality Break Effects"
        ),
        usage_tags=("control",),
        target=FeatureTarget.ENEMY,
        school_note="Dunamancy:Chronurgy",
    )
    converted_from = RecordStamp("spells_dnd5e.json", "bf4e7c9cefd9654e")


class TreeOfLife(ClassSpell):
    rules = SpellRules(
        name="Tree of Life",
        level=8,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.DRUID,),
        casting_time=CastingTime(CastingTimeType.BONUS_ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 1),
        source="World of Warcraft",
        description=(
            "You shape-shift into a Tree of Life form that resembles a treant. In this form, you gain the following benefits.\n"
            "Tree Form. You become Large. Your Speed becomes 10 feet and can’t be reduced, and Difficult Terrain doesn’t cost you extra movement.\n"
            "Bark Skin. You gain a +2 bonus to Armor Class and 10 Temporary Hit Points.\n"
            "Condition Immunity. You gain Immunity to the Paralyzed and Restrained conditions. You can’t be shape-shifted against your will.\n"
            "Source of Life. When a spell you cast with a spell slot restores Hit Points to a creature, that creature regains an additional 1d8 Hit Points on the turn you cast the spell.\n"
            "Spells Enhanced. The spell save DC of your Druid spells increases by 1, and you have Advantage on the attack rolls of Druid spells you cast."
        ),
        usage_tags=("buff", "heal"),
    )
    converted_from = RecordStamp("spells_dnd2024.json", "ae4a3e7b39173b99")


SPELLS = [
    AbiDalzimsHorridWilting,
    AnimalShapes,
    AntimagicField,
    AntipathySympathy,
    Befuddlement,
    Clone,
    ControlWeather,
    DarkStar,
    Demiplane,
    DominateMonster,
    Earthquake,
    EntrancingMirrors,
    Feeblemind,
    Glibness,
    HolyAura,
    HolyStarOfMystra,
    IllusoryDragon,
    IncendiaryCloud,
    IronBody,
    LightningRing,
    MaddeningDarkness,
    Maze,
    MightyFortress,
    MindBlank,
    MomentOfPrescience,
    PowerWordStun,
    RealityBreak,
    Sunburst,
    Telepathy,
    TreeOfLife,
    Tsunami,
]
