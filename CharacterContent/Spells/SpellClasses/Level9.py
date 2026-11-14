"""Level 9 spells as classes (CharacterContent/Spells/SpellFactory/ClassSpell.py),
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


class AstralProjection(ClassSpell):
    rules = SpellRules(
        name="Astral Projection",
        level=9,
        school=School.NECROMANCY,
        classes=(CharacterClass.CLERIC, CharacterClass.WARLOCK, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.HOUR, 1),
        range=Range(RangeType.FOOT, 10),
        components=Components(
            verbal=True,
            somatic=True,
            material="for each of the spell's targets, one jacinth worth 1,000+ GP and one silver bar worth 100+ GP, all of which the spell consumes",
        ),
        duration=Duration(DurationType.UNTIL_DISPELLED),
        source="Player's Handbook",
        description=(
            "You and up to eight willing creatures within range project your astral bodies into the Astral Plane (the spell ends instantly if you are already on that plane). Each target's body is left behind in a state of suspended animation; it has the Unconscious condition, doesn't need food or air, and doesn't age.\n"
            "A target's astral form resembles its body in almost every way, replicating it's game statistics and possessions. The principal difference is the addition of a silvery cord that trails from between the shoulderblades of the astral form. The cord fades from view after 1 foot. If the cord is cut - which happens only when an effect states that it does so - the target's body and astral form both die.\n"
            "A target's astral form can travel through the Astral Plane. The moment an astral form leaves that plane, the target's body and possessions travel along the silver cord, causing the target to re-enter its body on the new plane.\n"
            "Any damage or other effects that apply to an astral form have no effect on the target's body and vice versa. If a target's body or astral form drops to 0 Hit Points, the spell ends for that target. The spell ends for all the targets if you take a Magic action to dismiss it.\n"
            "When the spell ends for a target who isn't dead, the target reappears in its body and exits the state of suspended animation."
        ),
        usage_tags=("heal",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "df64a05e75bb7d82")


class BladeOfDisaster(ClassSpell):
    rules = SpellRules(
        name="Blade of Disaster",
        level=9,
        school=School.CONJURATION,
        classes=(
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.BONUS_ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Forgotten Realms - Heroes of Faerun",
        description=(
            "You create a 3-foot-long blade-shaped planar rift that lasts for the duration. The rift appears within range in a space of your choice, and you can immediately make up to two melee spell attacks, each one against a creature or object within 5 feet of the rift. On a hit, the target takes 10d6 Force damage. This attack scores a Critical Hit if the number on the d20 is 18 or higher.\n"
            "As a Bonus Action on your later turns, you can move the rift up to 60 feet and repeat the two attacks against a creature or an object within 5 feet of it. You can direct the attacks at the same target or at different ones.\n"
            "The blade can harmlessly pass through any barrier, including ones created by spells like Wall of Force ."
        ),
        usage_tags=("control", "damage"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "f0b9a33a9c686b66")


class Detonate(ClassSpell):
    rules = SpellRules(
        name="Detonate",
        level=9,
        school=School.EVOCATION,
        classes=(
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 500),
        components=Components(verbal=True, somatic=True, material="a piece of tinder"),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Arcana Unleashed",
        description=(
            "You create a magical, explosive seed inside a creature you can see within range. The target makes a Constitution saving throw, taking 10d10 Fire damage on a failed save or half as much damage on a successful one.\n"
            "An explosion then originates from the target. Each creature in a 60-foot Emanation originating from the target (not including the target) makes a Dexterity saving throw, with Disadvantage if this spell reduced the target to 0 Hit Points. A creature takes 10d10 Fire damage on a failed save or half as much damage on a successful one.\n"
            "A nonmagical object that isn’t being worn or carried also takes the damage if it’s in the Emanation, and the object starts burning if it’s flammable."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "521fc927bb4d88da")


class Foresight(ClassSpell):
    rules = SpellRules(
        name="Foresight",
        level=9,
        school=School.DIVINATION,
        classes=(
            CharacterClass.BARD,
            CharacterClass.DRUID,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.MINUTE, 1),
        range=Range(RangeType.TOUCH),
        components=Components(
            verbal=True, somatic=True, material="a hummingbird feather"
        ),
        duration=Duration(DurationType.HOUR, 8),
        source="Player's Handbook",
        description="You touch a willing creature and bestow a limited ability to see into the immediate future. For the duration, the target has Advantage on D20 Tests, and other creatures have Disadvantage on attack rolls against it. The spell ends early if you cast it again.",
        usage_tags=("buff", "control"),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "2cb3cb9c75b2ddbb")


class Gate(ClassSpell):
    rules = SpellRules(
        name="Gate",
        level=9,
        school=School.CONJURATION,
        classes=(
            CharacterClass.CLERIC,
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(
            verbal=True, somatic=True, material="a diamond worth 5,000+ GP"
        ),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "You conjure a portal linking an unoccupied space you can see within range to a precise location on a different plane of existence. The portal is a circular opening, which you can make 5 to 20 feet in diameter. You can orient the portal in any direction you choose. The portal lasts for the duration, and the portal's destination is visible through it.\n"
            "The portal has a front and a back on each plane where it appears. Travel through the portal is possible only by moving through its front. Anything that does so is instantly transported to the other plane, appearing in the unoccupied space nearest to the portal.\n"
            "Deities and other planar rulers can prevent portals created by this spell from opening in their presence or anywhere within their domains.\n"
            "When you cast this spell, you can speak the name of a specific creature (a pseudonym, title, or nickname doesn't work). If that creature is on a plane other than the one you are on, the portal opens next to the named creature and transports it to the nearest unoccupied space on your side of the portal. You gain no special power over the creature, and it is free to act as the DM deems appropriate. It might leave, attack you, or help you."
        ),
        usage_tags=("control",),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "4fd67cb33a068f74")


class Hindsight(ClassSpell):
    rules = SpellRules(
        name="Hindsight",
        level=9,
        school=School.DIVINATION,
        classes=(CharacterClass.WIZARD,),
        casting_time=CastingTime(CastingTimeType.MINUTE, 10),
        range=Range(RangeType.FOOT, 500),
        components=Components(
            verbal=True,
            somatic=True,
            material="a tiny hourglass worth 500+ GP, which the spell consumes",
        ),
        duration=Duration(DurationType.HOUR, 1, concentration=True),
        source="Arcana Unleashed",
        description="You peer backward through the fabric of time. You see visions of events that occurred within range throughout the past 10 years, racing by at approximately 1 day per second. Throughout the spell’s duration, you can freely slow down, pause, rewind, or fast-forward through these visions.",
        usage_tags=("utility",),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "94cd3a34efe95987")


class Imprisonment(ClassSpell):
    rules = SpellRules(
        name="Imprisonment",
        level=9,
        school=School.ABJURATION,
        classes=(CharacterClass.WARLOCK, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.MINUTE, 1),
        range=Range(RangeType.FOOT, 30),
        components=Components(
            verbal=True,
            somatic=True,
            material="a statuette of the target worth 5,000+ GP",
        ),
        duration=Duration(DurationType.UNTIL_DISPELLED),
        source="Player's Handbook",
        description=(
            "You create a magical restraint to hold a creature that you can see within range. The target must make a Wisdom saving throw. On a successful save, the target is unaffected, and it is immune to this spell for the next 24 hours. On a failed save, the target is imprisoned. While imprisoned, the target doesn't need to breathe, eat, or drink, and it doesn't age. Divination spells can't locate or perceive the imprisoned target, and the target can't teleport.\n"
            "Until the spell ends, the target is also affected by one of the following effects of your choice:\n"
            "Burial. The target is entombed beneath the earth in a hollow globe of magical force that is just large enough to contain the target. Nothing can pass into or out of the globe.\n"
            "Chaining. Chains firmly rooted in the ground hold the target in place. The target has the Restrained condition and can't be moved by any means.\n"
            "Hedged Prison. The target is trapped in a demiplane that is warded against teleportation and planar travel. The demiplane is your choice of a labyrinth, a cage, a tower, or the like.\n"
            "Minimus Containment. The target becomes 1 inch tall and is trapped inside an indestructible gemstone or a similar object. Light can pass through the gemstone (allowing the target to see out and other creatures to see in), but nothing else can pass through by any means.\n"
            "Slumber. The target has the Unconscious condition and can't be awoken.\n"
            "Ending the Spell. When you cast the spell, specify a trigger that will end it. The trigger can be as simple or as elaborate as you choose, but the DM must agree that it has a high likelihood of happening within the next decade. The trigger must be an observable action, such as someone making a particular offering at the temple of your god, saving your true love, or defeating a specific monster.\n"
            "A Dispel Magic spell can end the spell only if it is cast with a level 9 spell slot, targeting either the prison or the component used to create it."
        ),
        usage_tags=("buff", "control"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "ba3d7dd4fe979d3e")


class Invulnerability(ClassSpell):
    rules = SpellRules(
        name="Invulnerability",
        level=9,
        school=School.ABJURATION,
        classes=(CharacterClass.WIZARD,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(
            verbal=True,
            somatic=True,
            material="a piece of adamantine worth 500+ GP, which the spell consumes",
        ),
        duration=Duration(DurationType.MINUTE, 10, concentration=True),
        source="Arcana Unleashed",
        description="You have Immunity to all damage until the spell ends.",
        usage_tags=("buff",),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "de5e942a40e7b7a0")


class MassHeal(ClassSpell):
    rules = SpellRules(
        name="Mass Heal",
        level=9,
        school=School.ABJURATION,
        classes=(CharacterClass.CLERIC,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description="A flood of healing energy flows from you into creatures around you. You restore up to 700 Hit Points, divided as you choose among any number of creatures that you can see within range. Creatures healed by this spell also have the Blinded, Deafened, and Poisoned conditions removed from them.",
        usage_tags=("heal",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "dc970f400daf246a")


class MassPolymorph(ClassSpell):
    rules = SpellRules(
        name="Mass Polymorph",
        level=9,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.BARD, CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 120),
        components=Components(
            verbal=True, somatic=True, material="a caterpillar cocoon"
        ),
        duration=Duration(DurationType.HOUR, 1, concentration=True),
        source="Xanathar's Guide to Everything",
        description=(
            "You transform up to ten creatures of your choice that you can see within range. An unwilling target must succeed on a Wisdom saving throw to resist the transformation. An unwilling shapechanger automatically succeeds on the save.\n"
            "Each target assumes a beast form of your choice, and you can choose the same form or different ones for each target. The new form can be any beast you have seen whose challenge rating is equal to or less than the target's (or half the target's level, if the target doesn't have a challenge rating). The target's game statistics, including mental ability scores, are replaced by the statistics of the chosen beast, but the target retains its hit points, alignment, and personality.\n"
            "Each target gains a number of temporary hit points equal to the hit points of its new form. These temporary hit points can't be replaced by temporary hit points from another source. A target reverts to its normal form when it has no more temporary hit points or it dies. If the spell ends before then, the creature loses all its temporary hit points and reverts to its normal form.\n"
            "The creature is limited in the actions it can perform by the nature of its new form. It can't speak, cast spells, or do anything else that requires hands or speech. The target's gear melds into the new form.\n"
            "The target can't activate, use, wield, or otherwise benefit from any of its equipment."
        ),
        usage_tags=("control", "heal", "utility"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "85ff71d5d51ce106")


class MeteorSwarm(ClassSpell):
    rules = SpellRules(
        name="Meteor Swarm",
        level=9,
        school=School.EVOCATION,
        classes=(CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.MILE, 1),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "Blazing orbs of fire plummet to the ground at four different points you can see within range. Each creature in a 40-foot-radius Sphere centered on each of those points makes a Dexterity saving throw. A creature takes 20d6 Fire damage and 20d6 Bludgeoning damage on a failed save or half as much damage on a successful one. A creature in the area of more than one fiery Sphere is affected only once.\n"
            "A nonmagical object that isn't being worn or carried also takes the damage if it's in the spell's area, and the object starts burning if it's flammable."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "c7fa120f397fc636")


class PowerWordHeal(ClassSpell):
    rules = SpellRules(
        name="Power Word Heal",
        level=9,
        school=School.ENCHANTMENT,
        classes=(CharacterClass.BARD, CharacterClass.CLERIC),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description="A wave of healing energy washes over one creature you can see within range. The target regains all its Hit Points. If the creature has the Charmed, Frightened, Paralyzed, Poisoned, or Stunned condition, the condition ends. If the creature has the Prone condition, it can use its Reaction to stand up.",
        usage_tags=("control", "heal"),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "df45ab6884129a5c")


class PowerWordKill(ClassSpell):
    rules = SpellRules(
        name="Power Word Kill",
        level=9,
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
        description="You compel one creature you can see within range to die. If the target has 100 Hit Points or fewer, it dies. Otherwise, it takes 12d12 Psychic damage.",
        usage_tags=("damage",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "96f37e1ef88fd248")


class PrismaticWall(ClassSpell):
    rules = SpellRules(
        name="Prismatic Wall",
        level=9,
        school=School.ABJURATION,
        classes=(CharacterClass.BARD, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 10),
        source="Player's Handbook",
        description=(
            "A shimmering, multicolored plane of light forms a vertical opaque wall—up to 90 feet long, 30 feet high, and 1 inch thick - centered on a point within range. Alternatively, you shape the wall into a globe up to 30 feet in diameter centered on a point within range. The wall lasts for the duration. If you position the wall in a space occupied by a creature, the spell ends instantly without effect.\n"
            "The wall sheds Bright Light within 100 feet and Dim Light for an additional 100 feet. You and creatures you designate when you cast the spell can pass through and be near the wall without harm. If another creature that can see the wall moves within 20 feet of it or starts its turn there, the creature must succeed on a Constitution saving throw or have the Blinded condition for 1 minute.\n"
            "The wall consists of seven layers, each with a different color. When a creature reaches into or passes through the wall, it does so one layer at a time through all the layers. Each layer forces the creature to make a Dexterity saving throw or be affected by that layer’s properties as described in the Prismatic Layers table.\n"
            "The wall, which has AC 10, can be destroyed one layer at a time, in order from red to violet, by means specific to each layer. If a layer is destroyed, it is gone for the duration. Antimagic Field has no effect on the wall, and Dispel Magic can affect only the violet layer."
        ),
        usage_tags=("control",),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "fb29a547dc3db2f4")


class PsychicScream(ClassSpell):
    rules = SpellRules(
        name="Psychic Scream",
        level=9,
        school=School.ENCHANTMENT,
        classes=(
            CharacterClass.BARD,
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 90),
        components=Components(somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Xanathar's Guide to Everything",
        description=(
            "You unleash the power of your mind to blast the intellect of up to ten creatures of your choice that you can see within range. Creatures that have an Intelligence score of 2 or lower are unaffected. Each target must make an Intelligence saving throw. On a failed save, a target takes 14d6 psychic damage and is stunned. On a successful save, a target takes half as much damage and isn't stunned. If a target is killed by this damage, its head explodes, assuming it has one.\n"
            "A stunned target can make an Intelligence saving throw at the end of each of its turns. On a successful save, the stunning effect ends."
        ),
        usage_tags=("control", "damage", "utility"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "6bc8519c9687b3df")


class Shapechange(ClassSpell):
    rules = SpellRules(
        name="Shapechange",
        level=9,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.DRUID, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(
            verbal=True, somatic=True, material="a jade circlet worth 1,500+ GP"
        ),
        duration=Duration(DurationType.HOUR, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "You shape-shift into another creature for the duration or until you take a Magic action to shape-shift into a different eligible form. The new form must be of a creature that has a Challenge Rating no higher than your level or Challenge Rating. You must have seen the sort of creature before, and it can't be a Construct or an Undead.\n"
            "When you cast the spell, you gain a number of Temporary Hit Points equal to the Hit Points of the first form into which you shape-shift. These Temporary Hit Points vanish if any remain when the spell ends.\n"
            "Your game statistics are replaced by the stat block of the chosen form, but you retain your creature type; alignment; personality; Intelligence, Wisdom, and Charisma scores; Hit Points; Hit Point Dice; proficiencies; and ability to communicate. If you have the Spellcasting feature, you retain it too.\n"
            "Upon shape-shifting, you determine whether your equipment drops to the ground or changes in size and shape to fit the new form while you're in it."
        ),
        usage_tags=("heal",),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "21eff7823dbc7dd1")


class StormOfVengeance(ClassSpell):
    rules = SpellRules(
        name="Storm of Vengeance",
        level=9,
        school=School.CONJURATION,
        classes=(CharacterClass.DRUID,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.MILE, 1),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "A churning storm cloud forms for the duration, centered on a point within range and spreading to a radius of 300 feet. Each creature under the cloud when it appears must succeed on a Constitution saving throw or take 2d6 Thunder damage and have the Deafened condition for the duration.\n"
            "At the start of each of your later turns, the storm produces different effects, as detailed below.\n"
            "Turn 2. Acidic rain falls. Each creature and object under the cloud takes 4d6 Acid damage.\n"
            "Turn 3. You call six bolts of lightning from the cloud to strike six different creatures or objects beneath it. Each target makes a Dexterity saving throw, taking 10d6 Lightning damage on a failed save or half as much damage on a successful one.\n"
            "Turn 4. Hailstones rain down. Each creature under the cloud takes 2d6 Bludgeoning damage.\n"
            "Turns 5-10. Gusts and freezing rain assail the area under the cloud. Each creature there takes 1d6 Cold damage. Until the spell ends, the area is Difficult Terrain and Heavily Obscured, ranged attacks with weapons are impossible there, and strong wind blows through the area."
        ),
        usage_tags=("control", "damage"),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "5509424a394c4ce5")


class TimeStop(ClassSpell):
    rules = SpellRules(
        name="Time Stop",
        level=9,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "You briefly stop the flow of time for everyone but yourself. No time passes for other creatures, while you take 1d4 + 1 turns in a row, during which you can use actions and move as normal.\n"
            "This spell ends if one of the actions you use during this period, or any effects that you create during it, affects a creature other than you or an object being worn or carried by someone other than you. In addition, the spell ends if you move to a place more than 1,000 feet from the location where you cast it."
        ),
        usage_tags=("buff",),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "895d6983827a2a19")


class TruePolymorph(ClassSpell):
    rules = SpellRules(
        name="True Polymorph",
        level=9,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.BARD, CharacterClass.WARLOCK, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 30),
        components=Components(
            verbal=True,
            somatic=True,
            material="a drop of mercury, a dollop of gum arabic, and a wisp of smoke",
        ),
        duration=Duration(DurationType.HOUR, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "Choose one creature or nonmagical object that you can see within range. The creature shape-shifts into a different creature or a nonmagical object, or the object shape-shifts into a creature (the object must be neither worn nor carried). The transformation lasts for the duration or until the target dies or is destroyed, but if you maintain Concentration on this spell for the full duration, the spell lasts until dispelled.\n"
            "An unwilling creature can make a Wisdom saving throw, and if it succeeds, it isn't affected by this spell.\n"
            "Creature into Creature. If you turn a creature into another kind of creature, the new form can be any kind you choose that has a Challenge Rating equal to or less than the target’s Challenge Rating or level. The target's game statistics are replaced by the stat block of the new form, but it retains its Hit Points, Hit Point Dice, alignment, and personality.\n"
            "The target gains a number of Temporary Hit Points equal to the Hit Points of the new form. These Temporary Hit Points vanish if any remain when the spell ends.\n"
            "The target is limited in the actions it can perform by the anatomy of its new form, and it can't speak or cast spells.\n"
            "The target's gear melds into the new form. The creature can't use or otherwise benefit from any of that equipment.\n"
            "Object into Creature. You can turn an object into any kind of creature, as long as the creature's size is no larger than the object's size and the creature has a Challenge Rating of 9 or lower. The creature is Friendly to you and your allies. In combat, it takes its turns immediately after yours, and it obeys your commands.\n"
            "If the spell lasts more than an hour, you no longer control the creature. It might remain Friendly to you, depending on how you have treated it.\n"
            "Creature into Object. If you turn a creature into an object, it transforms along with whatever it is wearing and carrying into that form, as long as the object's size is no larger than the creature's size. The creature's statistics become those of the object, and the creature has no memory of time spent in this form after the spell ends and it returns to normal."
        ),
        usage_tags=("heal", "summon"),
        target=FeatureTarget.CREATURE,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "95d79661e619d56c")


class TrueResurrection(ClassSpell):
    rules = SpellRules(
        name="True Resurrection",
        level=9,
        school=School.NECROMANCY,
        classes=(CharacterClass.CLERIC, CharacterClass.DRUID),
        casting_time=CastingTime(CastingTimeType.HOUR, 1),
        range=Range(RangeType.TOUCH),
        components=Components(
            verbal=True,
            somatic=True,
            material="diamonds worth 25,000+ GP, which the spell consumes",
        ),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "You touch a creature that has been dead for no longer than 200 years and that died for any reason except old age. The creature is revived with all its Hit Points.\n"
            "This spell closes all wounds, neutralizes any poison, cures all magical contagions, and lifts any curses affecting the creature when it died. The spell replaces damaged or missing organs and limbs. If the creature was Undead, it is restored to its non-Undead form.\n"
            "The spell can provide a new body if the original no longer exists, in which case you must speak the creature's name. The creature then appears in an unoccupied space you choose within 10 feet of you."
        ),
        usage_tags=("heal",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "adf7449907324edc")


class VisionOfElapsingEons(ClassSpell):
    rules = SpellRules(
        name="Vision of Elapsing Eons",
        level=9,
        school=School.ILLUSION,
        classes=(
            CharacterClass.BARD,
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 120),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 1),
        source="Arcana Unleashed",
        description=(
            "You trick a creature you can see within range into believing it is watching itself and its surroundings crumble away, as if eons were passing in moments. The target must succeed on an Intelligence saving throw or take 10d12 Psychic damage and have the Paralyzed condition for the duration.\n"
            "While Paralyzed, the target repeats the save at the end of each of its turns. On a failed save, it gains 1 Exhaustion level. On a successful save, the spell ends. The spell ends early if someone within 5 feet of the target takes an action to shake it free from the illusion."
        ),
        usage_tags=("control", "damage"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "2abc8ee3d01eae7c")


class WailOfTheBanshee(ClassSpell):
    rules = SpellRules(
        name="Wail of the Banshee",
        level=9,
        school=School.NECROMANCY,
        classes=(
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Arcana Unleashed",
        description="You emit a terrible scream that can kill those who hear it. Choose up to ten creatures within range. Each target with 50 Hit Points or fewer dies. Targets with more than 50 Hit Points make a Constitution saving throw. On a failed save, a target takes 12d10 Psychic damage and has the Deafened condition for 1 hour. On a successful save, a target takes half as much damage only. A target is unaffected by the spell if it can’t hear you.",
        usage_tags=("control", "damage"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "20e7fec386e039f8")


class Weird(ClassSpell):
    rules = SpellRules(
        name="Weird",
        level=9,
        school=School.ILLUSION,
        classes=(CharacterClass.WARLOCK, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 120),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "You try to create illusory terrors in others' minds. Each creature of your choice in a 30-foot-radius Sphere centered on a point within range makes a Wisdom saving throw. On a failed save, a target takes 10d10 Psychic damage and has the Frightened condition for the duration. On a successful save, a target takes half as much damage only.\n"
            "A Frightened target makes a Wisdom saving throw at the end of each of its turns. On a failed save, it takes 5d10 Psychic damage. On a successful save, the spell ends on that target."
        ),
        usage_tags=("control", "damage"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "56d10de5d1bc12da")


class Wish(ClassSpell):
    rules = SpellRules(
        name="Wish",
        level=9,
        school=School.CONJURATION,
        classes=(CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "Wish is the mightiest spell a mortal can cast. By simply speaking aloud, you can alter reality itself.\n"
            "The basic use of this spell is to duplicate any other spell of level 8 or lower. If you use it this way, you don't need to meet any requirements to cast that spell, including costly components. The spell simply takes effect.\n"
            "Alternatively, you can create one of the following effects of your choice:\n"
            "Object Creation. You create one object of up to 25,000 GP in value that isn't a magic item. The object can be no more than 300 feet in any dimension, and it appears in an unoccupied space that you can see on the ground.\n"
            "Instant Health. You allow yourself and up to twenty creatures that you can see to regain all Hit Points, and you end all effects on them listed in the Greater Restoration spell.\n"
            "Resistance. You grant up to ten creatures that you can see Resistance to one damage type that you choose. This Resistance is permanent.\n"
            "Spell Immunity. You grant up to ten creatures you can see immunity to a single spell or other magical effect for 8 hours.\n"
            "Sudden Learning. You replace one of your feats with another feat for which you are eligible. You lose all the benefits of the old feat and gain the benefits of the new one. You can't replace a feat that is a prerequisite for any of your other feats or features.\n"
            "Roll Redo. You undo a single recent event by forcing a reroll of any die roll made within the last round (including your last turn). Reality reshapes itself to accommodate the new result. For example, a Wish spell could undo an ally’s failed saving throw or a foe's Critical Hit. You can force the reroll to be made with Advantage or Disadvantage, and you choose whether to use the reroll or the original roll.\n"
            "Reshape Reality. You may wish for something not included in any of the other effects. To do so, state your wish to the DM as precisely as possible. The DM has great latitude in ruling what occurs in such an instance; the greater the wish, the greater the likelihood that something goes wrong. This spell might simply fail, the effect you desire might be achieved only in part, or you might suffer an unforeseen consequence as a result of how you worded the wish. For example, wishing that a villain were dead might propel you forward in time to a period when that villain is no longer alive, effectively removing you from the game. Similarly, wishing for a Legendary magic item or an Artifact might instantly transport you to the presence of the item’s current owner. If your wish is granted and its effects have consequences for a whole community, region, or world, you are likely to attract powerful foes. If your wish would affect a god, the god’s divine servants might instantly intervene to prevent it or to encourage you to craft the wish in a particular way. If your wish would undo the multiverse itself, threaten the City of Sigil, or affect the Lady of Pain in any way, you see an image of her in your mind for a moment; she shakes her head, and your wish fails.\n"
            "The stress of casting Wish to produce any effect other than duplicating another spell weakens you. After enduring that stress, each time you cast a spell until you finish a Long Rest, you take 1d10 Necrotic damage per level of that spell. This damage can't be reduced or prevented in any way. In addition, your Strength score becomes 3 for 2d4 days. For each of those days that you spend resting and doing nothing more than light activity, your remaining recovery time decreases by 2 days. Finally, there is a 33 percent chance that you are unable to cast Wish ever again if you suffer this stress."
        ),
        usage_tags=("buff", "heal"),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "31db16e8cc39b3bf")


class RavenousVoid(ClassSpell):
    rules = SpellRules(
        name="Ravenous Void",
        level=9,
        school=School.EVOCATION,
        classes=(CharacterClass.WIZARD,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 1000),
        components=Components(
            verbal=True,
            somatic=True,
            material="a small, nine-pointed star made of iron",
        ),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Explorer's Guide to Wildemount",
        description=(
            "You create a 20-foot-radius sphere of destructive gravitation force centered on a point you can see within range. For the spell's duration, the sphere and any space within 100 feet of it are difficult terrain, and nonmagical objects fully inside the sphere are destroyed if they aren't being worn or carried.\n"
            "When the sphere appears and at the start of each of your turns until the spell ends, unsecured objects within 100 feet of the sphere are pulled toward the sphere's center, ending in an unoccupied space as close to the center as possible.\n"
            "A creature that starts its turn within 100 feet of the sphere must succeed on a Strength saving throw or be pulled straight toward the sphere's center, ending in an unoccupied space as close to the center as possible. A creature that enters the sphere for the first time on a turn or starts its turn there takes 5d10 force damage and is restrained until it is no longer in the sphere. If the sphere is in the air, the restrained creature hovers inside the sphere. A creature can use its action to make a Strength check against your spell save DC, ending this restrained condition on itself or another creature in the sphere that it can reach. A creature reduced to 0 hit points by this spell is annihilated, along with any nonmagical items it is wearing or carrying."
        ),
        usage_tags=("control", "damage", "utility"),
        target=FeatureTarget.AREA,
        school_note="Dunamancy:Graviturgy",
    )
    converted_from = RecordStamp("spells_dnd5e.json", "d7dc0f46a7b36e4f")


class TimeRavage(ClassSpell):
    rules = SpellRules(
        name="Time Ravage",
        level=9,
        school=School.NECROMANCY,
        classes=(CharacterClass.WIZARD,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 90),
        components=Components(
            verbal=True,
            somatic=True,
            material="an hourglass filled with diamond dust worth at least 5,000 gp, which the spell consumes",
        ),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Explorer's Guide to Wildemount",
        description="You target a creature you can see within range, putting its physical form through the devastation of rapid aging. The target must make a Constitution saving throw, taking 10d12 necrotic damage on a failed save, or half as much damage on a successful one. If the save fails, the target also ages to the point where it has only 30 days left before it dies of old age. In this aged state, the target has disadvantage on attack rolls, ability checks, and saving throws, and its walking speed is halved. Only the Wish spell or the Greater Restoration spell cast with a 9th-level spell slot can end these effects and restore the target to its previous age.",
        usage_tags=("control", "damage", "utility"),
        target=FeatureTarget.ENEMY,
        school_note="Dunamancy:Chronurgy",
    )
    converted_from = RecordStamp("spells_dnd5e.json", "70ccd38babd3f058")


class Apotheosis(ClassSpell):
    rules = SpellRules(
        name="Apotheosis",
        level=9,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.CLERIC,),
        casting_time=CastingTime(CastingTimeType.BONUS_ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True),
        duration=Duration(DurationType.MINUTE, 1),
        source="World of Warcraft",
        description=(
            "You transform into a spectral, angelic form that grants you the following benefits.\n"
            "Angelic Wings. You have a Fly Speed of 90 feet.\n"
            "Spectral Form. You have Resistance to Bludgeoning, Piercing, Radiant, and Slashing damage.\n"
            "Holy Empowerment. Whenever you cast a spell using a spell slot that restores Hit Points to one or more creatures or deals Radiant damage, determine the spell’s effects as if you had used a spell slot 2 levels higher than the spell slot you used to cast it (maximum of level 9)."
        ),
        usage_tags=("buff",),
    )
    converted_from = RecordStamp("spells_dnd2024.json", "304c125da325d86f")


SPELLS = [
    Apotheosis,
    AstralProjection,
    BladeOfDisaster,
    Detonate,
    Foresight,
    Gate,
    Hindsight,
    Imprisonment,
    Invulnerability,
    MassHeal,
    MassPolymorph,
    MeteorSwarm,
    PowerWordHeal,
    PowerWordKill,
    PrismaticWall,
    PsychicScream,
    RavenousVoid,
    Shapechange,
    StormOfVengeance,
    TimeRavage,
    TimeStop,
    TruePolymorph,
    TrueResurrection,
    VisionOfElapsingEons,
    WailOfTheBanshee,
    Weird,
    Wish,
]
