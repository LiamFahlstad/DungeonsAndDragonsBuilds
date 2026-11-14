"""Level 7 spells as classes (CharacterContent/Spells/SpellFactory/ClassSpell.py),
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
from Model.Content.FeatureText import Block, Facts, Option, Table


class AuraOfEvasion(ClassSpell):
    rules = SpellRules(
        name="Aura of Evasion",
        level=7,
        school=School.ABJURATION,
        classes=(
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Arcana Unleashed",
        description="An aura of alacrity radiates from you in a 30-foot Emanation for the duration. While in the aura, you and your allies have Advantage on Dexterity saving throws. When an affected creature is subjected to an effect that allows it to make a Dexterity saving throw to take only half damage, it takes no damage if it succeeds on the save and only half damage if it fails. A creature with the Incapacitated condition doesn’t gain any benefit from being in the aura.",
        usage_tags=("buff",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "e355e5f53bdb4d13")


class ConjureCelestial(ClassSpell):
    rules = SpellRules(
        name="Conjure Celestial",
        level=7,
        school=School.CONJURATION,
        classes=(CharacterClass.CLERIC,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 90),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 10, concentration=True),
        source="Player's Handbook",
        description=(
            "You conjure a spirit from the Upper Planes, which manifests as a pillar of light in a 10-foot-radius, 40-foot-high Cylinder centered on a point within range. For each creature you can see in the Cylinder, choose which of these lights shines on it:\n"
            "Healing Light. The target regains Hit Points equal to 4d12 plus your spellcasting ability modifier.\n"
            "Searing Light. The target makes a Dexterity saving throw, taking 6d12 Radiant damage on a failed save or half as much damage on a successful one.\n"
            "Until the spell ends, Bright Light fills the Cylinder, and when you move on your turn, you can also move the Cylinder up to 30 feet.\n"
            "Whenever the Cylinder moves into the space of a creature you can see and whenever a creature you can see enters the Cylinder or ends its turn there, you can bathe it in one of the lights. A creature can be affected by this spell only once per turn.\n"
            "Using a Higher-Level Spell Slot. The healing and damage increase by 1d12 for each spell slot level above 7."
        ),
        usage_tags=("heal",),
        target=FeatureTarget.CREATURE,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "a8f09205a54b122c")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You conjure a spirit from the Upper Planes, which manifests as a pillar of light.",
                    ),
                    (
                        "Area",
                        "10-foot-radius, 40-foot-high Cylinder centered on a point within range",
                    ),
                    (
                        "Choose",
                        "For each creature you can see in the Cylinder, choose which of these lights shines on it",
                    ),
                )
            ),
            Option(
                "Healing Light",
                (
                    Facts(
                        (
                            (
                                "Healing",
                                "The target regains Hit Points equal to 4d12 plus your spellcasting ability modifier",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Searing Light",
                (
                    Facts((("Save", "Dexterity, made by the target"),)),
                    Table(
                        ("Failed save", "Successful save"),
                        (("6d12 Radiant damage", "Half as much damage"),),
                    ),
                ),
            ),
            Facts(
                (
                    ("Light", "Until the spell ends, Bright Light fills the Cylinder"),
                    (
                        "Moving",
                        "Until the spell ends, when you move on your turn, you can also move the Cylinder up to 30 feet",
                    ),
                    (
                        "Bathing",
                        "Whenever the Cylinder moves into the space of a creature you can see and whenever a creature you can see enters the Cylinder or ends its turn there, you can bathe it in one of the lights",
                    ),
                    (
                        "Once per turn",
                        "A creature can be affected by this spell only once per turn",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (
                    Facts(
                        (
                            (
                                "Healing and damage",
                                "Increase by 1d12 for each spell slot level above 7",
                            ),
                        )
                    ),
                ),
            ),
        ]


class CreateMagen(ClassSpell):
    rules = SpellRules(
        name="Create Magen",
        level=7,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.WIZARD,),
        casting_time=CastingTime(CastingTimeType.HOUR, 1),
        range=Range(RangeType.TOUCH),
        components=Components(
            verbal=True,
            somatic=True,
            material="a vial of quicksilver worth 500 gp and a life-sized human doll, both of which the spell consumes, and an intricate crystal rod worth at least 1,500 gp that is not consumed",
        ),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Icewind Dale - Rime of the Frostmaiden",
        description=(
            "While casting the spell, you place a vial of quicksilver in the chest of a life-sized human doll stuffed with ash or dust. You then stitch up the doll and drip your blood on it. At the end of the casting, you tap the doll with a crystal rod, transforming it into a magen clothed in whatever the doll was wearing. The type of magen is chosen by you during the casting of the spell.\n"
            "When the magen appears, your hit point maximum decreases by an amount equal to the magen's challenge rating (minimum reduction of 1). Only a Wish spell can undo this reduction to your hit point maximum.\n"
            "Any magen you create with this spell obeys your commands without question."
        ),
        usage_tags=("utility", "summon"),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "c4d8fcb73e6cde99")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Casting",
                        "While casting the spell, you place a vial of quicksilver in the chest of a life-sized human doll stuffed with ash or dust",
                    ),
                    (
                        "Stitching",
                        "You then stitch up the doll and drip your blood on it",
                    ),
                    (
                        "Transforming",
                        "At the end of the casting, you tap the doll with a crystal rod, transforming it into a magen clothed in whatever the doll was wearing",
                    ),
                    (
                        "Type",
                        "The type of magen is chosen by you during the casting of the spell",
                    ),
                    (
                        "Cost",
                        "When the magen appears, your hit point maximum decreases by an amount equal to the magen's challenge rating (minimum reduction of 1)",
                    ),
                    (
                        "Undoing",
                        "Only a Wish spell can undo this reduction to your hit point maximum",
                    ),
                    (
                        "Obedience",
                        "Any magen you create with this spell obeys your commands without question",
                    ),
                )
            )
        ]


class CrownOfStars(ClassSpell):
    rules = SpellRules(
        name="Crown of Stars",
        level=7,
        school=School.EVOCATION,
        classes=(
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.HOUR, 1),
        source="Xanathar's Guide to Everything",
        description=(
            "Seven star-like motes of light appear and orbit your head until the spell ends. You can use a bonus action to send one of the motes streaking toward one creature or object within 120 feet of you. When you do so, make a ranged spell attack. On a hit, the target takes 4d12 radiant damage. Whether you hit or miss, the mote is expended. The spell ends early if you expend the last mote. If you have four or more motes remaining, they shed bright light in a 30-foot radius and dim light for an additional 30 feet. If you have one to three motes remaining, they shed dim light in a 30-foot radius.\n"
            "At Higher Levels. When you cast this spell using a spell slot of 8th level or higher, the number of motes created increases by two for each slot level above 7th."
        ),
        usage_tags=("buff", "damage", "utility"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "68a76b7d7182a270")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "Seven star-like motes of light appear and orbit your head until the spell ends.",
                    ),
                    ("Motes", "Seven, which orbit your head until the spell ends"),
                    (
                        "Sending one",
                        "You can use a bonus action to send one of the motes streaking toward one creature or object within 120 feet of you",
                    ),
                    ("Attack", "When you do so, make a ranged spell attack"),
                    ("On a hit", "The target takes 4d12 radiant damage"),
                    ("Expended", "Whether you hit or miss, the mote is expended"),
                    ("Ends early", "The spell ends early if you expend the last mote"),
                )
            ),
            Table(
                ("Motes remaining", "Light"),
                (
                    (
                        "Four or more",
                        "Bright light in a 30-foot radius and dim light for an additional 30 feet",
                    ),
                    ("One to three", "Dim light in a 30-foot radius"),
                ),
            ),
            Option(
                "At Higher Levels",
                (
                    Facts(
                        (
                            (
                                "Slot",
                                "When you cast this spell using a spell slot of 8th level or higher",
                            ),
                            (
                                "Motes",
                                "The number of motes created increases by two for each slot level above 7th",
                            ),
                        )
                    ),
                ),
            ),
        ]


class DelayedBlastFireball(ClassSpell):
    rules = SpellRules(
        name="Delayed Blast Fireball",
        level=7,
        school=School.EVOCATION,
        classes=(CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 150),
        components=Components(
            verbal=True, somatic=True, material="a ball of bat guano and sulfur"
        ),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "A beam of yellow light flashes from you, then condenses at a chosen point within range as a glowing bead for the duration. When the spell ends, the bead explodes, and each creature in a 20-foot-radius Sphere centered on that point makes a Dexterity saving throw. A creature takes Fire damage equal to the total accumulated damage on a failed save or half as much damage on a successful one.\n"
            "The spell’s base damage is 12d6, and the damage increases by 1d6 whenever your turn ends and the spell hasn’t ended.\n"
            "If a creature touches the glowing bead before the spell ends, that creature makes a Dexterity saving throw. On a failed save, the spell ends, causing the bead to explode. On a successful save, the creature can throw the bead up to 40 feet. If the thrown bead enters a creature’s space or collides with a solid object, the spell ends, and the bead explodes.\n"
            "When the bead explodes, flammable objects in the explosion that aren’t being worn or carried start burning.\n"
            "Using a Higher-Level Spell Slot. The base damage increases by 1d6 for each spell slot level above 7."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "f0d99b03a0e1eb4f")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "A beam of yellow light flashes from you, then condenses at a chosen point within range as a glowing bead for the duration.",
                    ),
                    (
                        "Bead",
                        "Condenses at a chosen point within range as a glowing bead for the duration",
                    ),
                    ("Explosion", "When the spell ends, the bead explodes"),
                    ("Area", "20-foot-radius Sphere centered on that point"),
                    ("Save", "Dexterity, made by each creature in the Sphere"),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (
                    (
                        "Fire damage equal to the total accumulated damage",
                        "Half as much damage",
                    ),
                ),
            ),
            Facts(
                (
                    (
                        "Damage",
                        "The spell's base damage is 12d6, and the damage increases by 1d6 whenever your turn ends and the spell hasn't ended",
                    ),
                )
            ),
            Option(
                "Touching the Bead",
                (
                    Facts(
                        (
                            (
                                "Trigger",
                                "A creature touches the glowing bead before the spell ends",
                            ),
                            ("Save", "Dexterity, made by that creature"),
                            (
                                "Failed save",
                                "The spell ends, causing the bead to explode",
                            ),
                            (
                                "Successful save",
                                "The creature can throw the bead up to 40 feet",
                            ),
                            (
                                "Thrown",
                                "If the thrown bead enters a creature's space or collides with a solid object, the spell ends, and the bead explodes",
                            ),
                        )
                    ),
                ),
            ),
            Facts(
                (
                    (
                        "Burning",
                        "When the bead explodes, flammable objects in the explosion that aren't being worn or carried start burning",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (
                    Facts(
                        (
                            (
                                "Base damage",
                                "Increases by 1d6 for each spell slot level above 7",
                            ),
                        )
                    ),
                ),
            ),
        ]


class DivineWord(ClassSpell):
    rules = SpellRules(
        name="Divine Word",
        level=7,
        school=School.EVOCATION,
        classes=(CharacterClass.CLERIC,),
        casting_time=CastingTime(CastingTimeType.BONUS_ACTION),
        range=Range(RangeType.FOOT, 30),
        components=Components(verbal=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description="You utter a word imbued with power from the Upper Planes. Each creature of your choice in range makes a Charisma saving throw. On a failed save, a target that has 50 Hit Points or fewer suffers an effect based on its current Hit Points, as shown in the Divine Word Effects table. Regardless of its Hit Points, a Celestial, an Elemental, a Fey, or a Fiend target that fails its save is forced back to its plane of origin (if it isn’t there already) and can’t return to the current plane for 24 hours by any means short of a Wish spell.",
        usage_tags=("damage", "control"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "b8e78c5971227534")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You utter a word imbued with power from the Upper Planes.",
                    ),
                    ("Targets", "Each creature of your choice in range"),
                    ("Save", "Charisma"),
                    (
                        "Failed save",
                        "A target that has 50 Hit Points or fewer suffers an effect based on its current Hit Points, as shown in the Divine Word Effects table",
                    ),
                    ("Successful save", "No effect"),
                )
            ),
            Table(
                ("Hit Points", "Effect"),
                (
                    ("0–20", "The target dies"),
                    (
                        "21–30",
                        "The target has the Blinded, Deafened, and Stunned conditions for 1 hour",
                    ),
                    (
                        "31–40",
                        "The target has the Blinded and Deafened conditions for 10 minutes",
                    ),
                    ("41–50", "The target has the Deafened condition for 1 minute"),
                ),
            ),
            Facts(
                (
                    (
                        "Banished",
                        "Regardless of its Hit Points, a Celestial, an Elemental, a Fey, or a Fiend target that fails its save is forced back to its plane of origin (if it isn't there already)",
                    ),
                    (
                        "Can't return",
                        "It can't return to the current plane for 24 hours by any means short of a Wish spell",
                    ),
                )
            ),
        ]


class DraconicTransformation(ClassSpell):
    rules = SpellRules(
        name="Draconic Transformation",
        level=7,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.DRUID, CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.BONUS_ACTION),
        range=Range(RangeType.SELF),
        components=Components(
            verbal=True,
            somatic=True,
            material="a statuette of a dragon, worth at least 500 gp",
        ),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Fizban's Treasury of Dragons",
        description=(
            "With a roar, you draw on the magic of dragons to transform yourself, taking on draconic features. You gain the following benefits until the spell ends:\n"
            "Blindsight. You have blindsight with a range of 30 feet. Within that range, you can effectively see anything that isn't behind total cover, even if you're blinded or in darkness. Moreover, you can see an invisible creature, unless the creature successfully hides from you.\n"
            "Breath Weapon. When you cast this spell, and as a bonus action on subsequent turns for the duration, you can exhale shimmering energy in a 60-foot cone. Each creature in that area must make a Dexterity saving throw, taking 6d8 force damage on a failed save, or half as much damage on a successful one.\n"
            "Wings. Incorporeal wings sprout from your back, giving you a flying speed of 60 feet."
        ),
        usage_tags=("damage", "utility"),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "7705d2e4530820f1")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "With a roar, you draw on the magic of dragons to transform yourself, taking on draconic features.",
                    ),
                    (
                        "Benefits",
                        "You gain the following benefits until the spell ends",
                    ),
                )
            ),
            Option(
                "Blindsight",
                (
                    Facts(
                        (
                            (
                                "Blindsight",
                                "You have blindsight with a range of 30 feet",
                            ),
                            (
                                "Within range",
                                "Within that range, you can effectively see anything that isn't behind total cover, even if you're blinded or in darkness",
                            ),
                            (
                                "Invisible",
                                "Moreover, you can see an invisible creature, unless the creature successfully hides from you",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Breath Weapon",
                (
                    Facts(
                        (
                            (
                                "When",
                                "When you cast this spell, and as a bonus action on subsequent turns for the duration, you can exhale shimmering energy in a 60-foot cone",
                            ),
                            ("Save", "Dexterity, made by each creature in that area"),
                        )
                    ),
                    Table(
                        ("Failed save", "Successful save"),
                        (("6d8 force damage", "Half as much damage"),),
                    ),
                ),
            ),
            Option(
                "Wings",
                (
                    Facts(
                        (
                            (
                                "Wings",
                                "Incorporeal wings sprout from your back, giving you a flying speed of 60 feet",
                            ),
                        )
                    ),
                ),
            ),
        ]


class DreamOfTheBlueVeil(ClassSpell):
    rules = SpellRules(
        name="Dream of the Blue Veil",
        level=7,
        school=School.CONJURATION,
        classes=(
            CharacterClass.BARD,
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.MINUTE, 10),
        range=Range(RangeType.FOOT, 20),
        components=Components(
            verbal=True,
            somatic=True,
            material="a magic item or a willing creature from the destination world",
        ),
        duration=Duration(DurationType.HOUR, 6),
        source="Tasha's Cauldron of Everything",
        description=(
            "You and up to eight willing creatures within range fall unconscious for the spell's duration and experience visions of another world on the Material Plane, such as Oerth, Toril, Krynn, or Eberron. If the spell reaches its full duration, the visions conclude with each of you encountering and pulling back a mysterious blue curtain. The spell then ends with you mentally and physically transported to the world that was in the visions.\n"
            "To cast this spell, you must have a magic item that originated on the world you wish to reach, and you must be aware of the world's existence, even if you don't know the world's name. Your destination in the other world is a safe location within 1 mile of where the magic item was created. Alternatively, you can cast the spell if one of the affected creatures was born on the other world, which causes your destination to be a safe location within 1 mile of where that creature was born.\n"
            "The spell ends early on a creature if that creature takes any damage, and the creature isn't transported. If you take any damage, the spell ends for you and all other creatures, with none of you being transported."
        ),
        usage_tags=("control", "damage", "utility"),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "06a37546274e4acb")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "The visions conclude with each of you encountering and pulling back a mysterious blue curtain.",
                    ),
                    ("Targets", "You and up to eight willing creatures within range"),
                    (
                        "Effect",
                        "All of you fall unconscious for the spell's duration and experience visions of another world on the Material Plane, such as Oerth, Toril, Krynn, or Eberron",
                    ),
                    (
                        "Full duration",
                        "If the spell reaches its full duration, the spell then ends with you mentally and physically transported to the world that was in the visions",
                    ),
                    (
                        "Requirement",
                        "To cast this spell, you must have a magic item that originated on the world you wish to reach, and you must be aware of the world's existence, even if you don't know the world's name",
                    ),
                    (
                        "Destination",
                        "Your destination in the other world is a safe location within 1 mile of where the magic item was created",
                    ),
                    (
                        "Alternatively",
                        "You can cast the spell if one of the affected creatures was born on the other world, which causes your destination to be a safe location within 1 mile of where that creature was born",
                    ),
                )
            ),
            Option(
                "Damage Ends the Spell",
                (
                    Facts(
                        (
                            (
                                "A creature",
                                "The spell ends early on a creature if that creature takes any damage, and the creature isn't transported",
                            ),
                            (
                                "You",
                                "If you take any damage, the spell ends for you and all other creatures, with none of you being transported",
                            ),
                        )
                    ),
                ),
            ),
        ]


class Etherealness(ClassSpell):
    rules = SpellRules(
        name="Etherealness",
        level=7,
        school=School.CONJURATION,
        classes=(
            CharacterClass.BARD,
            CharacterClass.CLERIC,
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.HOUR, 8, up_to=True),
        source="Player's Handbook",
        description=(
            "You step into the border regions of the Ethereal Plane, where it overlaps with your current plane. You remain in the Border Ethereal for the duration. During this time, you can move in any direction. If you move up or down, every foot of movement costs an extra foot. You can perceive the plane you left, which looks gray, and you can’t see anything there more than 60 feet away.\n"
            "While on the Ethereal Plane, you can affect and be affected only by creatures, objects, and effects on that plane. Creatures that aren’t on the Ethereal Plane can’t perceive or interact with you unless a feature gives them the ability to do so.\n"
            "When the spell ends, you return to the plane you left in the spot that corresponds to your space in the Border Ethereal. If you appear in an occupied space, you are shunted to the nearest unoccupied space and take Force damage equal to twice the number of feet you are moved.\n"
            "This spell ends instantly if you cast it while you are on the Ethereal Plane or a plane that doesn’t border it, such as one of the Outer Planes.\n"
            "Using a Higher-Level Spell Slot. You can target up to three willing creatures (including yourself) for each spell slot level above 7. The creatures must be within 10 feet of you when you cast the spell."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "6034381aabfc9795")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You step into the border regions of the Ethereal Plane, where it overlaps with your current plane.",
                    ),
                    ("Plane", "You remain in the Border Ethereal for the duration"),
                    (
                        "Movement",
                        "During this time, you can move in any direction. If you move up or down, every foot of movement costs an extra foot",
                    ),
                    (
                        "Perceiving",
                        "You can perceive the plane you left, which looks gray, and you can't see anything there more than 60 feet away",
                    ),
                    (
                        "Affecting",
                        "While on the Ethereal Plane, you can affect and be affected only by creatures, objects, and effects on that plane",
                    ),
                    (
                        "Others",
                        "Creatures that aren't on the Ethereal Plane can't perceive or interact with you unless a feature gives them the ability to do so",
                    ),
                )
            ),
            Option(
                "When the Spell Ends",
                (
                    Facts(
                        (
                            (
                                "Returning",
                                "You return to the plane you left in the spot that corresponds to your space in the Border Ethereal",
                            ),
                            (
                                "Occupied space",
                                "If you appear in an occupied space, you are shunted to the nearest unoccupied space and take Force damage equal to twice the number of feet you are moved",
                            ),
                        )
                    ),
                ),
            ),
            Facts(
                (
                    (
                        "Ends early",
                        "This spell ends instantly if you cast it while you are on the Ethereal Plane or a plane that doesn't border it, such as one of the Outer Planes",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (
                    Facts(
                        (
                            (
                                "Targets",
                                "You can target up to three willing creatures (including yourself) for each spell slot level above 7",
                            ),
                            (
                                "Distance",
                                "The creatures must be within 10 feet of you when you cast the spell",
                            ),
                        )
                    ),
                ),
            ),
        ]


class FingerOfDeath(ClassSpell):
    rules = SpellRules(
        name="Finger of Death",
        level=7,
        school=School.NECROMANCY,
        classes=(
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "You unleash negative energy toward a creature you can see within range. The target makes a Constitution saving throw, taking 7d8 + 30 Necrotic damage on a failed save or half as much damage on a successful one.\n"
            "A Humanoid killed by this spell rises at the start of your next turn as a Zombie (see appendix B) that follows your verbal orders."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "1e6ff89435c4c5fb")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You unleash negative energy toward a creature you can see within range.",
                    ),
                    ("Target", "A creature you can see within range"),
                    ("Save", "Constitution"),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (("7d8 + 30 Necrotic damage", "Half as much damage"),),
            ),
            Facts(
                (
                    (
                        "Zombie",
                        "A Humanoid killed by this spell rises at the start of your next turn as a Zombie (see appendix B) that follows your verbal orders",
                    ),
                )
            ),
        ]


class FireStorm(ClassSpell):
    rules = SpellRules(
        name="Fire Storm",
        level=7,
        school=School.EVOCATION,
        classes=(CharacterClass.CLERIC, CharacterClass.DRUID, CharacterClass.SORCERER),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 150),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "A storm of fire appears within range. The area of the storm consists of up to ten 10-foot Cubes, which you arrange as you like. Each Cube must be contiguous with at least one other Cube. Each creature in the area makes a Dexterity saving throw, taking 7d10 Fire damage on a failed save or half as much damage on a successful one.\n"
            "Flammable objects in the area that aren’t being worn or carried start burning."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "b80ad9c169442982")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Flavor", "A storm of fire appears within range."),
                    ("Area", "Up to ten 10-foot Cubes, which you arrange as you like"),
                    (
                        "Contiguous",
                        "Each Cube must be contiguous with at least one other Cube",
                    ),
                    ("Save", "Dexterity, made by each creature in the area"),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (("7d10 Fire damage", "Half as much damage"),),
            ),
            Facts(
                (
                    (
                        "Burning",
                        "Flammable objects in the area that aren't being worn or carried start burning",
                    ),
                )
            ),
        ]


class Forcecage(ClassSpell):
    rules = SpellRules(
        name="Forcecage",
        level=7,
        school=School.EVOCATION,
        classes=(CharacterClass.BARD, CharacterClass.WARLOCK, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 100),
        components=Components(
            verbal=True,
            somatic=True,
            material="ruby dust worth 1,500+ GP, which the spell consumes",
        ),
        duration=Duration(DurationType.HOUR, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "An immobile, Invisible, Cube-shaped prison composed of magical force springs into existence around an area you choose within range. The prison can be a cage or a solid box, as you choose.\n"
            "A prison in the shape of a cage can be up to 20 feet on a side and is made from 1/2-inch diameter bars spaced 1/2 inch apart. A prison in the shape of a box can be up to 10 feet on a side, creating a solid barrier that prevents any matter from passing through it and blocking any spells cast into or out from the area.\n"
            "When you cast the spell, any creature that is completely inside the cage’s area is trapped. Creatures only partially within the area, or those too large to fit inside it, are pushed away from the center of the area until they are completely outside it.\n"
            "A creature inside the cage can’t leave it by nonmagical means. If the creature tries to use teleportation or interplanar travel to leave, it must first make a Charisma saving throw. On a successful save, the creature can use that magic to exit the cage. On a failed save, the creature doesn’t exit the cage and wastes the spell or effect. The cage also extends into the Ethereal Plane, blocking ethereal travel.\n"
            "This spell can’t be dispelled by Dispel Magic ."
        ),
        usage_tags=("buff", "control"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "99975183a5e0ba69")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Prison",
                        "An immobile, Invisible, Cube-shaped prison composed of magical force springs into existence around an area you choose within range",
                    ),
                    (
                        "Choice",
                        "The prison can be a cage or a solid box, as you choose",
                    ),
                )
            ),
            Option(
                "Cage",
                (
                    Facts(
                        (
                            (
                                "Size",
                                "A prison in the shape of a cage can be up to 20 feet on a side",
                            ),
                            (
                                "Bars",
                                "It is made from 1/2-inch diameter bars spaced 1/2 inch apart",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Box",
                (
                    Facts(
                        (
                            (
                                "Size",
                                "A prison in the shape of a box can be up to 10 feet on a side",
                            ),
                            (
                                "Barrier",
                                "Creating a solid barrier that prevents any matter from passing through it and blocking any spells cast into or out from the area",
                            ),
                        )
                    ),
                ),
            ),
            Facts(
                (
                    (
                        "Trapped",
                        "When you cast the spell, any creature that is completely inside the cage's area is trapped",
                    ),
                    (
                        "Pushed away",
                        "Creatures only partially within the area, or those too large to fit inside it, are pushed away from the center of the area until they are completely outside it",
                    ),
                    (
                        "Leaving",
                        "A creature inside the cage can't leave it by nonmagical means",
                    ),
                    (
                        "Trigger",
                        "A creature inside the cage tries to use teleportation or interplanar travel to leave",
                    ),
                    ("Save", "Charisma, which the creature must first make"),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (
                    (
                        "The creature doesn't exit the cage and wastes the spell or effect",
                        "The creature can use that magic to exit the cage",
                    ),
                ),
            ),
            Facts(
                (
                    (
                        "Ethereal Plane",
                        "The cage also extends into the Ethereal Plane, blocking ethereal travel",
                    ),
                    ("Dispelling", "This spell can't be dispelled by Dispel Magic"),
                )
            ),
        ]


class FracturedAwareness(ClassSpell):
    rules = SpellRules(
        name="Fractured Awareness",
        level=7,
        school=School.DIVINATION,
        classes=(
            CharacterClass.BARD,
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 120),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Arcana Unleashed",
        description=(
            "You cause a creature to receive conflicting visions of multiple possible futures. Choose a creature you can see within range. The target makes an Intelligence saving throw. On a failed save, the target takes 12d10 Psychic damage and has Disadvantage on D20 Tests for the duration. On a successful save, the target takes half as much damage only, and the spell ends.\n"
            "At the end of each of its turns, an affected target repeats the save, ending the spell on a success."
        ),
        usage_tags=("control", "damage"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "e3c6479fead31151")


class MirageArcane(ClassSpell):
    rules = SpellRules(
        name="Mirage Arcane",
        level=7,
        school=School.ILLUSION,
        classes=(CharacterClass.BARD, CharacterClass.DRUID, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.MINUTE, 10),
        range=Range(RangeType.SIGHT),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.DAY, 10),
        source="Player's Handbook",
        description=(
            "You make terrain in an area up to 1 mile square look, sound, smell, and even feel like some other sort of terrain. Open fields or a road could be made to resemble a swamp, hill, crevasse, or some other rough or impassable terrain. A pond can be made to seem like a grassy meadow, a precipice like a gentle slope, or a rock-strewn gully like a wide and smooth road.\n"
            "Similarly, you can alter the appearance of structures or add them where none are present. The spell doesn’t disguise, conceal, or add creatures.\n"
            "The illusion includes audible, visual, tactile, and olfactory elements, so it can turn clear ground into Difficult Terrain (or vice versa) or otherwise impede movement through the area. Any piece of the illusory terrain (such as a rock or stick) that is removed from the spell’s area disappears immediately.\n"
            "Creatures with Truesight can see through the illusion to the terrain’s true form; however, all other elements of the illusion remain, so while the creature is aware of the illusion’s presence, the creature can still physically interact with the illusion."
        ),
        usage_tags=("buff", "control"),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "c04c2330d7ba935d")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You make terrain in an area up to 1 mile square look, sound, smell, and even feel like some other sort of terrain.",
                    ),
                    ("Area", "Terrain in an area up to 1 mile square"),
                    (
                        "Examples",
                        "Open fields or a road could be made to resemble a swamp, hill, crevasse, or some other rough or impassable terrain",
                    ),
                    (
                        "More examples",
                        "A pond can be made to seem like a grassy meadow, a precipice like a gentle slope, or a rock-strewn gully like a wide and smooth road",
                    ),
                    (
                        "Structures",
                        "Similarly, you can alter the appearance of structures or add them where none are present",
                    ),
                    (
                        "Creatures",
                        "The spell doesn't disguise, conceal, or add creatures",
                    ),
                    (
                        "Senses",
                        "The illusion includes audible, visual, tactile, and olfactory elements, so it can turn clear ground into Difficult Terrain (or vice versa) or otherwise impede movement through the area",
                    ),
                    (
                        "Removed pieces",
                        "Any piece of the illusory terrain (such as a rock or stick) that is removed from the spell's area disappears immediately",
                    ),
                    (
                        "Truesight",
                        "Creatures with Truesight can see through the illusion to the terrain's true form",
                    ),
                    (
                        "Still there",
                        "However, all other elements of the illusion remain, so while the creature is aware of the illusion's presence, the creature can still physically interact with the illusion",
                    ),
                )
            )
        ]


class MordenkainensMagnificentMansion(ClassSpell):
    rules = SpellRules(
        name="Mordenkainen's Magnificent Mansion",
        level=7,
        school=School.CONJURATION,
        classes=(CharacterClass.BARD, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.MINUTE, 1),
        range=Range(RangeType.FOOT, 300),
        components=Components(
            verbal=True, somatic=True, material="a miniature door worth 15+ GP"
        ),
        duration=Duration(DurationType.HOUR, 24),
        source="Player's Handbook",
        description=(
            "You conjure a shimmering door in range that lasts for the duration. The door leads to an extradimensional dwelling and is 5 feet wide and 10 feet tall. You and any creature you designate when you cast the spell can enter the extradimensional dwelling as long as the door remains open. You can open or close it (no action required) if you are within 30 feet of it. While closed, the door is imperceptible.\n"
            "Beyond the door is a magnificent foyer with numerous chambers beyond. The dwelling’s atmosphere is clean, fresh, and warm.\n"
            "You can create any floor plan you like for the dwelling, but it can’t exceed 50 contiguous 10-foot Cubes. The place is furnished and decorated as you choose. It contains sufficient food to serve a nine-course banquet for up to 100 people. Furnishings and other objects created by this spell dissipate into smoke if removed from it.\n"
            "A staff of 100 near-transparent servants attends all who enter. You determine the appearance of these servants and their attire. They are invulnerable and obey your commands. Each servant can perform tasks that a human could perform, but they can’t attack or take any action that would directly harm another creature. Thus the servants can fetch things, clean, mend, fold clothes, light fires, serve food, pour wine, and so on. The servants can’t leave the dwelling.\n"
            "When the spell ends, any creatures or objects left inside the extradimensional space are expelled into the unoccupied spaces nearest to the entrance."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "61a20e23489198fe")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You conjure a shimmering door in range that lasts for the duration.",
                    ),
                    (
                        "Door",
                        "The door leads to an extradimensional dwelling and is 5 feet wide and 10 feet tall",
                    ),
                    (
                        "Entering",
                        "You and any creature you designate when you cast the spell can enter the extradimensional dwelling as long as the door remains open",
                    ),
                    (
                        "Open or close",
                        "You can open or close it (no action required) if you are within 30 feet of it",
                    ),
                    ("Closed", "While closed, the door is imperceptible"),
                )
            ),
            Option(
                "The Dwelling",
                (
                    Facts(
                        (
                            (
                                "Foyer",
                                "Beyond the door is a magnificent foyer with numerous chambers beyond",
                            ),
                            (
                                "Atmosphere",
                                "The dwelling's atmosphere is clean, fresh, and warm",
                            ),
                            (
                                "Floor plan",
                                "You can create any floor plan you like for the dwelling, but it can't exceed 50 contiguous 10-foot Cubes",
                            ),
                            (
                                "Furnishings",
                                "The place is furnished and decorated as you choose",
                            ),
                            (
                                "Food",
                                "It contains sufficient food to serve a nine-course banquet for up to 100 people",
                            ),
                            (
                                "Removed",
                                "Furnishings and other objects created by this spell dissipate into smoke if removed from it",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Servants",
                (
                    Facts(
                        (
                            (
                                "Staff",
                                "A staff of 100 near-transparent servants attends all who enter",
                            ),
                            (
                                "Appearance",
                                "You determine the appearance of these servants and their attire",
                            ),
                            ("Nature", "They are invulnerable and obey your commands"),
                            (
                                "Tasks",
                                "Each servant can perform tasks that a human could perform, but they can't attack or take any action that would directly harm another creature",
                            ),
                            (
                                "Examples",
                                "Thus the servants can fetch things, clean, mend, fold clothes, light fires, serve food, pour wine, and so on",
                            ),
                            ("Limit", "The servants can't leave the dwelling"),
                        )
                    ),
                ),
            ),
            Facts(
                (
                    (
                        "Spell ends",
                        "When the spell ends, any creatures or objects left inside the extradimensional space are expelled into the unoccupied spaces nearest to the entrance",
                    ),
                )
            ),
        ]


class MordenkainensSword(ClassSpell):
    rules = SpellRules(
        name="Mordenkainen's Sword",
        level=7,
        school=School.EVOCATION,
        classes=(CharacterClass.BARD, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 90),
        components=Components(
            verbal=True, somatic=True, material="a miniature sword worth 250+ GP"
        ),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "You create a spectral sword that hovers within range. It lasts for the duration.\n"
            "When the sword appears, you make a melee spell attack against a target within 5 feet of the sword. On a hit, the target takes Force damage equal to 4d12 plus your spellcasting ability modifier.\n"
            "On your later turns, you can take a Bonus Action to move the sword up to 30 feet to a spot you can see and repeat the attack against the same target or a different one."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "61bd2190a717d82b")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Flavor", "You create a spectral sword that hovers within range."),
                    (
                        "Attack",
                        "When the sword appears, you make a melee spell attack against a target within 5 feet of the sword",
                    ),
                    (
                        "On a hit",
                        "The target takes Force damage equal to 4d12 plus your spellcasting ability modifier",
                    ),
                    (
                        "Later turns",
                        "On your later turns, you can take a Bonus Action to move the sword up to 30 feet to a spot you can see and repeat the attack against the same target or a different one",
                    ),
                )
            )
        ]


class PlaneShift(ClassSpell):
    rules = SpellRules(
        name="Plane Shift",
        level=7,
        school=School.CONJURATION,
        classes=(
            CharacterClass.CLERIC,
            CharacterClass.DRUID,
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.TOUCH),
        components=Components(
            verbal=True,
            somatic=True,
            material="a forked, metal rod worth 250+ GP and attuned to a plane of existence",
        ),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "You and up to eight willing creatures who link hands in a circle are transported to a different plane of existence. You can specify a target destination in general terms, such as the City of Brass on the Elemental Plane of Fire or the palace of Dispater on the second level of the Nine Hells, and you appear in or near that destination, as determined by the DM.\n"
            "Alternatively, if you know the sigil sequence of a teleportation circle on another plane of existence, this spell can take you to that circle. If the teleportation circle is too small to hold all the creatures you transported, they appear in the closest unoccupied spaces next to the circle."
        ),
        usage_tags=("buff", "control"),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "460e3180bed16588")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Targets",
                        "You and up to eight willing creatures who link hands in a circle",
                    ),
                    (
                        "Effect",
                        "The targets are transported to a different plane of existence",
                    ),
                    (
                        "Destination",
                        "You can specify a target destination in general terms, such as the City of Brass on the Elemental Plane of Fire or the palace of Dispater on the second level of the Nine Hells",
                    ),
                    (
                        "Arrival",
                        "You appear in or near that destination, as determined by the DM",
                    ),
                    (
                        "Alternatively",
                        "If you know the sigil sequence of a teleportation circle on another plane of existence, this spell can take you to that circle",
                    ),
                    (
                        "Too small",
                        "If the teleportation circle is too small to hold all the creatures you transported, they appear in the closest unoccupied spaces next to the circle",
                    ),
                )
            )
        ]


class PowerWordFortify(ClassSpell):
    rules = SpellRules(
        name="Power Word Fortify",
        level=7,
        school=School.ENCHANTMENT,
        classes=(CharacterClass.BARD, CharacterClass.CLERIC),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description="You fortify up to six creatures you can see within range. The spell bestows 120 Temporary Hit Points, which you divide among the spell’s recipients.",
        usage_tags=("heal",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "fb0f7ecaad3e0bf4")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Targets", "Up to six creatures you can see within range"),
                    (
                        "Temporary HP",
                        "The spell bestows 120 Temporary Hit Points, which you divide among the spell's recipients",
                    ),
                )
            )
        ]


class PowerWordPain(ClassSpell):
    rules = SpellRules(
        name="Power Word Pain",
        level=7,
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
        duration=Duration(DurationType.MINUTE, 1),
        source="Arcana Unleashed",
        description=(
            "You speak a word of power that causes waves of intense pain to assail one creature you can see within range. If the target has 100 Hit Points or fewer, it takes 6d8 Force damage and has the Charmed condition for the duration. Otherwise, it takes 6d8 Force damage only.\n"
            "While the target is Charmed, its Speed can be no more than 10 feet, and it has Disadvantage on D20 Tests except Constitution saving throws. In addition, when the target tries to cast a spell, it must first succeed on a Constitution saving throw, or the spell dissipates with no effect, and the action, Bonus Action, or Reaction used to cast it is wasted. If that spell was cast with a spell slot, the slot isn’t expended.\n"
            "At the end of each of its turns, the Charmed target makes a Constitution saving throw, ending the spell on itself on a successful save."
        ),
        usage_tags=("control", "damage"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "b28a8129750011a1")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You speak a word of power that causes waves of intense pain to assail one creature you can see within range.",
                    ),
                    ("Target", "One creature you can see within range"),
                    (
                        "100 HP or fewer",
                        "The target takes 6d8 Force damage and has the Charmed condition for the duration",
                    ),
                    ("More than 100 HP", "Otherwise, it takes 6d8 Force damage only"),
                    (
                        "Repeat save",
                        "At the end of each of its turns, the Charmed target makes a Constitution saving throw, ending the spell on itself on a successful save",
                    ),
                )
            ),
            Option(
                "While the Target Is Charmed",
                (
                    Facts(
                        (
                            ("Speed", "Its Speed can be no more than 10 feet"),
                            (
                                "D20 Tests",
                                "It has Disadvantage on D20 Tests except Constitution saving throws",
                            ),
                            (
                                "Casting",
                                "When the target tries to cast a spell, it must first succeed on a Constitution saving throw, or the spell dissipates with no effect, and the action, Bonus Action, or Reaction used to cast it is wasted",
                            ),
                            (
                                "Spell slot",
                                "If that spell was cast with a spell slot, the slot isn’t expended",
                            ),
                        )
                    ),
                ),
            ),
        ]


class PrismaticSpray(ClassSpell):
    rules = SpellRules(
        name="Prismatic Spray",
        level=7,
        school=School.EVOCATION,
        classes=(CharacterClass.BARD, CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description="Eight rays of light flash from you in a 60-foot Cone. Each creature in the Cone makes a Dexterity saving throw. For each target, roll 1d8 to determine which color ray affects it, consulting the Prismatic Rays table.",
        usage_tags=("damage", "control"),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "90a5f51c81ed5be0")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Area", "Eight rays of light flash from you in a 60-foot Cone"),
                    ("Save", "Dexterity, made by each creature in the Cone"),
                    (
                        "Ray",
                        "For each target, roll 1d8 to determine which color ray affects it, consulting the Prismatic Rays table",
                    ),
                )
            ),
            Table(
                ("1d8", "Ray", "Failed save", "Successful save"),
                (
                    ("1", "Red", "12d6 Fire damage", "Half as much damage"),
                    ("2", "Orange", "12d6 Acid damage", "Half as much damage"),
                    ("3", "Yellow", "12d6 Lightning damage", "Half as much damage"),
                    ("4", "Green", "12d6 Poison damage", "Half as much damage"),
                    ("5", "Blue", "12d6 Cold damage", "Half as much damage"),
                ),
            ),
            Option(
                "6: Indigo",
                (
                    Facts(
                        (
                            (
                                "Failed save",
                                "The target has the Restrained condition and makes a Constitution saving throw at the end of each of its turns",
                            ),
                            (
                                "Three successes",
                                "If it successfully saves three times, the condition ends",
                            ),
                            (
                                "Three failures",
                                "If it fails three times, it has the Petrified condition until it is freed by an effect like the Greater Restoration spell",
                            ),
                            (
                                "Tracking",
                                "The successes and failures needn't be consecutive; keep track of both until the target collects three of a kind",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "7: Violet",
                (
                    Facts(
                        (
                            (
                                "Failed save",
                                "The target has the Blinded condition and makes a Wisdom saving throw at the start of your next turn",
                            ),
                            (
                                "Repeat success",
                                "On a Successful Save, the condition ends",
                            ),
                            (
                                "Repeat failure",
                                "On a Failed Save, the condition ends, and the creature teleports to another plane of existence (DM's choice)",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "8: Special",
                (
                    Facts(
                        (
                            (
                                "Two rays",
                                "The target is struck by two rays. Roll twice, rerolling any 8",
                            ),
                        )
                    ),
                ),
            ),
        ]


class ProjectImage(ClassSpell):
    rules = SpellRules(
        name="Project Image",
        level=7,
        school=School.ILLUSION,
        classes=(CharacterClass.BARD, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.MILE, 500),
        components=Components(
            verbal=True, somatic=True, material="a statuette of yourself worth 5+ GP"
        ),
        duration=Duration(DurationType.DAY, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "You create an illusory copy of yourself that lasts for the duration. The copy can appear at any location within range that you have seen before, regardless of intervening obstacles. The illusion looks and sounds like you, but it is intangible. If the illusion takes any damage, it disappears, and the spell ends.\n"
            "You can see through the illusion’s eyes and hear through its ears as if you were in its space. As a Magic action, you can move it up to 60 feet and make it gesture, speak, and behave in whatever way you choose. It mimics your mannerisms perfectly.\n"
            "Physical interaction with the image reveals it to be illusory, since things can pass through it. A creature that takes the Study action to examine the image can determine that it is an illusion with a successful Intelligence (Investigation) check against your spell save DC. If a creature discerns the illusion for what it is, the creature can see through the image, and any noise it makes sounds hollow to the creature."
        ),
        usage_tags=("buff", "control"),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "a8db51d8015beb52")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Illusion",
                        "You create an illusory copy of yourself that lasts for the duration",
                    ),
                    (
                        "Appears",
                        "The copy can appear at any location within range that you have seen before, regardless of intervening obstacles",
                    ),
                    (
                        "Looks like you",
                        "The illusion looks and sounds like you, but it is intangible",
                    ),
                    (
                        "Ends early",
                        "If the illusion takes any damage, it disappears, and the spell ends",
                    ),
                    (
                        "Senses",
                        "You can see through the illusion's eyes and hear through its ears as if you were in its space",
                    ),
                    (
                        "Controlling",
                        "As a Magic action, you can move it up to 60 feet and make it gesture, speak, and behave in whatever way you choose",
                    ),
                    ("Mannerisms", "It mimics your mannerisms perfectly"),
                    (
                        "Touching it",
                        "Physical interaction with the image reveals it to be illusory, since things can pass through it",
                    ),
                    (
                        "Studying it",
                        "A creature that takes the Study action to examine the image can determine that it is an illusion with a successful Intelligence (Investigation) check against your spell save DC",
                    ),
                    (
                        "Discerned",
                        "If a creature discerns the illusion for what it is, the creature can see through the image, and any noise it makes sounds hollow to the creature",
                    ),
                )
            )
        ]


class Regenerate(ClassSpell):
    rules = SpellRules(
        name="Regenerate",
        level=7,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.BARD, CharacterClass.CLERIC, CharacterClass.DRUID),
        casting_time=CastingTime(CastingTimeType.MINUTE, 1),
        range=Range(RangeType.TOUCH),
        components=Components(verbal=True, somatic=True, material="a prayer wheel"),
        duration=Duration(DurationType.HOUR, 1),
        source="Player's Handbook",
        description="A creature you touch regains 4d8 + 15 Hit Points. For the duration, the target regains 1 Hit Point at the start of each of its turns, and any severed body parts regrow after 2 minutes.",
        usage_tags=("heal",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "790af32415a36968")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Target", "A creature you touch"),
                    ("Healing", "The target regains 4d8 + 15 Hit Points"),
                    (
                        "Each turn",
                        "For the duration, the target regains 1 Hit Point at the start of each of its turns",
                    ),
                    ("Severed parts", "Any severed body parts regrow after 2 minutes"),
                )
            )
        ]


class Resurrection(ClassSpell):
    rules = SpellRules(
        name="Resurrection",
        level=7,
        school=School.NECROMANCY,
        classes=(CharacterClass.BARD, CharacterClass.CLERIC),
        casting_time=CastingTime(CastingTimeType.HOUR, 1),
        range=Range(RangeType.TOUCH),
        components=Components(
            verbal=True,
            somatic=True,
            material="a diamond worth 1,000+ GP, which the spell consumes",
        ),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "With a touch, you revive a dead creature that has been dead for no more than a century, didn’t die of old age, and wasn’t Undead when it died.\n"
            "The creature returns to life with all its Hit Points. This spell also neutralizes any poisons that affected the creature at the time of death. This spell closes all mortal wounds and restores any missing body parts.\n"
            "Coming back from the dead is an ordeal. The target takes a −4 penalty to D20 Tests. Every time the target finishes a Long Rest, the penalty is reduced by 1 until it becomes 0.\n"
            "Casting this spell to revive a creature that has been dead for 365 days or longer taxes you. Until you finish a Long Rest, you can’t cast spells again, and you have Disadvantage on D20 Tests."
        ),
        usage_tags=("buff", "heal"),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "d9ac49fca3e31dd2")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Target",
                        "A dead creature you touch that has been dead for no more than a century, didn't die of old age, and wasn't Undead when it died",
                    ),
                    ("Returns", "The creature returns to life with all its Hit Points"),
                    (
                        "Poisons",
                        "This spell also neutralizes any poisons that affected the creature at the time of death",
                    ),
                    (
                        "Wounds",
                        "This spell closes all mortal wounds and restores any missing body parts",
                    ),
                )
            ),
            Option(
                "An Ordeal",
                (
                    Facts(
                        (
                            (
                                "Penalty",
                                "Coming back from the dead is an ordeal. The target takes a −4 penalty to D20 Tests",
                            ),
                            (
                                "Recovery",
                                "Every time the target finishes a Long Rest, the penalty is reduced by 1 until it becomes 0",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Taxing the Caster",
                (
                    Facts(
                        (
                            (
                                "When",
                                "Casting this spell to revive a creature that has been dead for 365 days or longer taxes you",
                            ),
                            (
                                "Cost",
                                "Until you finish a Long Rest, you can't cast spells again, and you have Disadvantage on D20 Tests",
                            ),
                        )
                    ),
                ),
            ),
        ]


class ReverseGravity(ClassSpell):
    rules = SpellRules(
        name="Reverse Gravity",
        level=7,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.DRUID, CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 100),
        components=Components(
            verbal=True, somatic=True, material="a lodestone and iron filings"
        ),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "This spell reverses gravity in a 50-foot-radius, 100-foot high Cylinder centered on a point within range. All creatures and objects in that area that aren’t anchored to the ground fall upward and reach the top of the Cylinder. A creature can make a Dexterity saving throw to grab a fixed object it can reach, thus avoiding the fall upward.\n"
            "If a ceiling or an anchored object is encountered in this upward fall, creatures and objects strike it just as they would during a downward fall. If an affected creature or object reaches the Cylinder’s top without striking anything, it hovers there for the duration. When the spell ends, affected objects and creatures fall downward."
        ),
        usage_tags=("damage", "control"),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "4f070af71d52bc03")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Area",
                        "50-foot-radius, 100-foot high Cylinder centered on a point within range",
                    ),
                    ("Effect", "This spell reverses gravity in that area"),
                    (
                        "Falling",
                        "All creatures and objects in that area that aren't anchored to the ground fall upward and reach the top of the Cylinder",
                    ),
                    (
                        "Save",
                        "Dexterity, which a creature can make to grab a fixed object it can reach, thus avoiding the fall upward",
                    ),
                    (
                        "Ceiling",
                        "If a ceiling or an anchored object is encountered in this upward fall, creatures and objects strike it just as they would during a downward fall",
                    ),
                    (
                        "Top",
                        "If an affected creature or object reaches the Cylinder's top without striking anything, it hovers there for the duration",
                    ),
                    (
                        "Spell ends",
                        "When the spell ends, affected objects and creatures fall downward",
                    ),
                )
            )
        ]


class ReweaveFate(ClassSpell):
    rules = SpellRules(
        name="Reweave Fate",
        level=7,
        school=School.DIVINATION,
        classes=(
            CharacterClass.BARD,
            CharacterClass.CLERIC,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(
            CastingTimeType.REACTION,
            trigger="which you take when a creature you can see within 60 feet of you fails a D20 Test",
        ),
        range=Range(RangeType.FOOT, 60),
        components=Components(somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Arcana Unleashed",
        description="You untangle a single thread of fate to encourage a different result. The creature that failed the D20 Test can reroll it with Advantage, and the creature must use the new roll. If the D20 Test is successful, the creature gains 6d10 Temporary Hit Points from its strengthened fate.",
        usage_tags=("buff", "heal"),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "1192a2111b4d904d")


class Sequester(ClassSpell):
    rules = SpellRules(
        name="Sequester",
        level=7,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.WIZARD,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.TOUCH),
        components=Components(
            verbal=True,
            somatic=True,
            material="gem dust worth 5,000+ GP, which the spell consumes",
        ),
        duration=Duration(DurationType.UNTIL_DISPELLED),
        source="Player's Handbook",
        description=(
            "With a touch, you magically sequester an object or a willing creature. For the duration, the target has the Invisible condition and can’t be targeted by Divination spells, detected by magic, or viewed remotely with magic.\n"
            "If the target is a creature, it enters a state of suspended animation; it has the Unconscious condition, doesn’t age, and doesn’t need food, water, or air.\n"
            "You can set a condition for the spell to end early. The condition can be anything you choose, but it must occur or be visible within 1 mile of the target. Examples include “after 1,000 years” or “when the tarrasque awakens.” This spell also ends if the target takes any damage."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "14e6f8b50f89c4fe")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Target", "An object or a willing creature you touch"),
                    (
                        "Hidden",
                        "For the duration, the target has the Invisible condition and can't be targeted by Divination spells, detected by magic, or viewed remotely with magic",
                    ),
                    (
                        "Creature",
                        "If the target is a creature, it enters a state of suspended animation; it has the Unconscious condition, doesn't age, and doesn't need food, water, or air",
                    ),
                    (
                        "Set a condition",
                        "You can set a condition for the spell to end early. The condition can be anything you choose, but it must occur or be visible within 1 mile of the target",
                    ),
                    (
                        "Examples",
                        "Examples include “after 1,000 years” or “when the tarrasque awakens.”",
                    ),
                    (
                        "Ends early",
                        "This spell also ends if the target takes any damage",
                    ),
                )
            )
        ]


class SimbulsSynostodweomer(ClassSpell):
    rules = SpellRules(
        name="Simbul's Synostodweomer",
        level=7,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.TOUCH),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.HOUR, 1),
        source="Forgotten Realms - Heroes of Faerun",
        description="You imbue one creature you touch with magical healing energy for the duration. Whenever the target casts a spell using a spell slot, the target can immediately roll a number of unexpended Hit Point Dice equal to the spell slot’s level and regain Hit Points equal to the roll’s total plus your spellcasting ability modifier; those dice are then expended.",
        usage_tags=("heal",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "7d6ee4fee80cdfd7")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Target",
                        "One creature you touch, imbued with magical healing energy for the duration",
                    ),
                    ("Trigger", "Whenever the target casts a spell using a spell slot"),
                    (
                        "Healing",
                        "The target can immediately roll a number of unexpended Hit Point Dice equal to the spell slot's level and regain Hit Points equal to the roll's total plus your spellcasting ability modifier; those dice are then expended",
                    ),
                )
            )
        ]


class Simulacrum(ClassSpell):
    rules = SpellRules(
        name="Simulacrum",
        level=7,
        school=School.ILLUSION,
        classes=(CharacterClass.WIZARD,),
        casting_time=CastingTime(CastingTimeType.HOUR, 12),
        range=Range(RangeType.TOUCH),
        components=Components(
            verbal=True,
            somatic=True,
            material="powdered ruby worth 1,500+ GP, which the spell consumes",
        ),
        duration=Duration(DurationType.UNTIL_DISPELLED),
        source="Player's Handbook",
        description=(
            "You create a simulacrum of one Beast or Humanoid that is within 10 feet of you for the entire casting of the spell. You finish the casting by touching both the creature and a pile of ice or snow that is the same size as that creature, and the pile turns into the simulacrum, which is a creature. It uses the game statistics of the original creature at the time of casting, except it is a Construct, its Hit Point maximum is half as much, and it can’t cast this spell.\n"
            "The simulacrum is Friendly to you and creatures you designate. It obeys your commands and acts on your turn in combat. The simulacrum can’t gain levels, and it can’t take Short or Long Rests.\n"
            "If the simulacrum takes damage, the only way to restore its Hit Points is to repair it as you take a Long Rest, during which you expend components worth 100 GP per Hit Point restored. The simulacrum must stay within 5 feet of you for the repair.\n"
            "The simulacrum lasts until it drops to 0 Hit Points, at which point it reverts to snow and melts away. If you cast this spell again, any simulacrum you created with this spell is instantly destroyed."
        ),
        usage_tags=("heal", "summon"),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "14b4ed921b171b1f")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Target",
                        "One Beast or Humanoid that is within 10 feet of you for the entire casting of the spell",
                    ),
                    (
                        "Finishing",
                        "You finish the casting by touching both the creature and a pile of ice or snow that is the same size as that creature, and the pile turns into the simulacrum, which is a creature",
                    ),
                    (
                        "Statistics",
                        "It uses the game statistics of the original creature at the time of casting, except it is a Construct, its Hit Point maximum is half as much, and it can't cast this spell",
                    ),
                )
            ),
            Option(
                "The Simulacrum",
                (
                    Facts(
                        (
                            (
                                "Attitude",
                                "The simulacrum is Friendly to you and creatures you designate",
                            ),
                            (
                                "Commands",
                                "It obeys your commands and acts on your turn in combat",
                            ),
                            (
                                "Limits",
                                "The simulacrum can't gain levels, and it can't take Short or Long Rests",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Repairing It",
                (
                    Facts(
                        (
                            (
                                "Restoring",
                                "If the simulacrum takes damage, the only way to restore its Hit Points is to repair it as you take a Long Rest, during which you expend components worth 100 GP per Hit Point restored",
                            ),
                            (
                                "Nearby",
                                "The simulacrum must stay within 5 feet of you for the repair",
                            ),
                        )
                    ),
                ),
            ),
            Facts(
                (
                    (
                        "Lasts",
                        "The simulacrum lasts until it drops to 0 Hit Points, at which point it reverts to snow and melts away",
                    ),
                    (
                        "Casting again",
                        "If you cast this spell again, any simulacrum you created with this spell is instantly destroyed",
                    ),
                )
            ),
        ]


class Symbol(ClassSpell):
    rules = SpellRules(
        name="Symbol",
        level=7,
        school=School.ABJURATION,
        classes=(
            CharacterClass.BARD,
            CharacterClass.CLERIC,
            CharacterClass.DRUID,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.MINUTE, 1),
        range=Range(RangeType.TOUCH),
        components=Components(
            verbal=True,
            somatic=True,
            material="powdered diamond worth 1,000+ GP, which the spell consumes",
        ),
        duration=Duration(DurationType.UNTIL_DISPELLED_OR_TRIGGERED),
        source="Player's Handbook",
        description=(
            "You inscribe a harmful glyph either on a surface (such as a section of floor or wall) or within an object that can be closed (such as a book or chest). The glyph can cover an area no larger than 10 feet in diameter. If you choose an object, it must remain in place; if it is moved more than 10 feet from where you cast this spell, the glyph is broken, and the spell ends without being triggered.\n"
            "The glyph is nearly imperceptible and requires a successful Wisdom (Perception) check against your spell save DC to notice.\n"
            "When you inscribe the glyph, you set its trigger and choose which effect the symbol bears: Death, Discord, Fear, Pain, Sleep, or Stunning. Each one is explained below.\n"
            "Set the Trigger. You decide what triggers the glyph when you cast the spell. For glyphs inscribed on a surface, common triggers include touching or stepping on the glyph, removing another object covering it, or approaching within a certain distance of it. For glyphs inscribed within an object, common triggers include opening that object or seeing the glyph.\n"
            "You can refine the trigger so that only creatures of certain types activate it (for example, the glyph could be set to affect Aberrations). You can also set conditions for creatures that don’t trigger the glyph, such as those who say a certain password.\n"
            "Once triggered, the glyph glows, filling a 60-foot-radius Sphere with Dim Light for 10 minutes, after which time the spell ends. Each creature in the Sphere when the glyph activates is targeted by its effect, as is a creature that enters the Sphere for the first time on a turn or ends its turn there. A creature is targeted only once per turn.\n"
            "Death. Each target makes a Constitution saving throw, taking 10d10 Necrotic damage on a failed save or half as much damage on a successful save.\n"
            "Discord. Each target makes a Wisdom saving throw. On a failed save, a target argues with other creatures for 1 minute. During this time, it is incapable of meaningful communication and has Disadvantage on attack rolls and ability checks.\n"
            "Fear. Each target must succeed on a Wisdom saving throw or have the Frightened condition for 1 minute. While Frightened, the target must move at least 30 feet away from the glyph on each of its turns, if able.\n"
            "Pain. Each target must succeed on a Constitution saving throw or have the Incapacitated condition for 1 minute.\n"
            "Sleep. Each target must succeed on a Wisdom saving throw or have the Unconscious condition for 10 minutes. A creature awakens if it takes damage or if someone takes an action to shake it awake.\n"
            "Stunning. Each target must succeed on a Wisdom saving throw or have the Stunned condition for 1 minute."
        ),
        usage_tags=("buff", "control"),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "805a573823a5c3a3")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Glyph",
                        "You inscribe a harmful glyph either on a surface (such as a section of floor or wall) or within an object that can be closed (such as a book or chest)",
                    ),
                    (
                        "Size",
                        "The glyph can cover an area no larger than 10 feet in diameter",
                    ),
                    (
                        "Object",
                        "If you choose an object, it must remain in place; if it is moved more than 10 feet from where you cast this spell, the glyph is broken, and the spell ends without being triggered",
                    ),
                    (
                        "Noticing it",
                        "The glyph is nearly imperceptible and requires a successful Wisdom (Perception) check against your spell save DC to notice",
                    ),
                    (
                        "Effect",
                        "When you inscribe the glyph, you set its trigger and choose which effect the symbol bears: Death, Discord, Fear, Pain, Sleep, or Stunning",
                    ),
                )
            ),
            Option(
                "Set the Trigger",
                (
                    Facts(
                        (
                            (
                                "Trigger",
                                "You decide what triggers the glyph when you cast the spell",
                            ),
                            (
                                "On a surface",
                                "For glyphs inscribed on a surface, common triggers include touching or stepping on the glyph, removing another object covering it, or approaching within a certain distance of it",
                            ),
                            (
                                "In an object",
                                "For glyphs inscribed within an object, common triggers include opening that object or seeing the glyph",
                            ),
                            (
                                "Refining",
                                "You can refine the trigger so that only creatures of certain types activate it (for example, the glyph could be set to affect Aberrations)",
                            ),
                            (
                                "Exceptions",
                                "You can also set conditions for creatures that don't trigger the glyph, such as those who say a certain password",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "When Triggered",
                (
                    Facts(
                        (
                            (
                                "Glows",
                                "Once triggered, the glyph glows, filling a 60-foot-radius Sphere with Dim Light for 10 minutes, after which time the spell ends",
                            ),
                            (
                                "Targeted",
                                "Each creature in the Sphere when the glyph activates is targeted by its effect, as is a creature that enters the Sphere for the first time on a turn or ends its turn there",
                            ),
                            (
                                "Once per turn",
                                "A creature is targeted only once per turn",
                            ),
                        )
                    ),
                ),
            ),
            Table(
                ("Effect", "Save", "Failed save", "Successful save"),
                (
                    (
                        "Death",
                        "Constitution",
                        "10d10 Necrotic damage",
                        "Half as much damage",
                    ),
                    (
                        "Discord",
                        "Wisdom",
                        "The target argues with other creatures for 1 minute. During this time, it is incapable of meaningful communication and has Disadvantage on attack rolls and ability checks",
                        "No effect",
                    ),
                    (
                        "Fear",
                        "Wisdom",
                        "The target has the Frightened condition for 1 minute. While Frightened, the target must move at least 30 feet away from the glyph on each of its turns, if able",
                        "No effect",
                    ),
                    (
                        "Pain",
                        "Constitution",
                        "The target has the Incapacitated condition for 1 minute",
                        "No effect",
                    ),
                    (
                        "Sleep",
                        "Wisdom",
                        "The target has the Unconscious condition for 10 minutes. A creature awakens if it takes damage or if someone takes an action to shake it awake",
                        "No effect",
                    ),
                    (
                        "Stunning",
                        "Wisdom",
                        "The target has the Stunned condition for 1 minute",
                        "No effect",
                    ),
                ),
            ),
        ]


class Teleport(ClassSpell):
    rules = SpellRules(
        name="Teleport",
        level=7,
        school=School.CONJURATION,
        classes=(CharacterClass.BARD, CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 10),
        components=Components(verbal=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "This spell instantly transports you and up to eight willing creatures that you can see within range, or a single object that you can see within range, to a destination you select. If you target an object, it must be Large or smaller, and it can’t be held or carried by an unwilling creature.\n"
            "The destination you choose must be known to you, and it must be on the same plane of existence as you. Your familiarity with the destination determines whether you arrive there successfully. The DM rolls 1d100 and consults the Teleportation Outcome table and the explanations after it.\n"
            "Familiarity. Here are the meanings of the terms in the table’s Familiarity column:\n"
            "“Permanent circle” means a permanent teleportation circle whose sigil sequence you know.\n"
            "“Linked object” means you possess an object taken from the desired destination within the last six months, such as a book from a wizard’s library.\n"
            "“Very familiar” is a place you have visited often, a place you have carefully studied, or a place you can see when you cast the spell.\n"
            "“Seen casually” is a place you have seen more than once but with which you aren’t very familiar.\n"
            "“Viewed once or described” is a place you have seen once, possibly using magic, or a place you know through someone else’s description, perhaps from a map.\n"
            "“False destination” is a place that doesn’t exist. Perhaps you tried to scry an enemy’s sanctum but instead viewed an illusion, or you are attempting to teleport to a location that no longer exists.\n"
            "Mishap. The spell’s unpredictable magic results in a difficult journey. Each teleporting creature (or the target object) takes 3d10 Force damage, and the DM rerolls on the table to see where you wind up (multiple mishaps can occur, dealing damage each time).\n"
            "Similar Area. You and your group (or the target object) appear in a different area that’s visually or thematically similar to the target area. You appear in the closest similar place. If you are heading for your home laboratory, for example, you might appear in another person’s laboratory in the same city.\n"
            "Off Target. You and your group (or the target object) appear 2d12 miles away from the destination in a random direction. Roll 1d8 for the direction: 1 , east; 2 , southeast; 3 , south; 4 , southwest; 5 , west; 6 , northwest; 7 , north; or 8 , northeast.\n"
            "On Target. You and your group (or the target object) appear where you intended."
        ),
        usage_tags=("buff", "damage"),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "55153e05cc06a69e")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Targets",
                        "You and up to eight willing creatures that you can see within range, or a single object that you can see within range",
                    ),
                    (
                        "Effect",
                        "This spell instantly transports the targets to a destination you select",
                    ),
                    (
                        "Object",
                        "If you target an object, it must be Large or smaller, and it can't be held or carried by an unwilling creature",
                    ),
                    (
                        "Destination",
                        "The destination you choose must be known to you, and it must be on the same plane of existence as you",
                    ),
                    (
                        "Familiarity",
                        "Your familiarity with the destination determines whether you arrive there successfully",
                    ),
                    (
                        "Roll",
                        "The DM rolls 1d100 and consults the Teleportation Outcome table and the explanations after it",
                    ),
                )
            ),
            Table(
                ("Familiarity", "Mishap", "Similar Area", "Off Target", "On Target"),
                (
                    ("Permanent circle", "—", "—", "—", "01–00"),
                    ("Linked object", "—", "—", "—", "01–00"),
                    ("Very familiar", "01–05", "06–13", "14–24", "25–00"),
                    ("Seen casually", "01–33", "34–43", "44–53", "54–00"),
                    ("Viewed once or described", "01–43", "44–53", "54–73", "74–00"),
                    ("False destination", "01–50", "51–00", "—", "—"),
                ),
            ),
            Option(
                "Familiarity",
                (
                    Facts(
                        (
                            (
                                "Meanings",
                                "Here are the meanings of the terms in the table's Familiarity column",
                            ),
                        )
                    ),
                    Table(
                        ("Term", "Meaning"),
                        (
                            (
                                "Permanent circle",
                                "A permanent teleportation circle whose sigil sequence you know",
                            ),
                            (
                                "Linked object",
                                "You possess an object taken from the desired destination within the last six months, such as a book from a wizard's library",
                            ),
                            (
                                "Very familiar",
                                "A place you have visited often, a place you have carefully studied, or a place you can see when you cast the spell",
                            ),
                            (
                                "Seen casually",
                                "A place you have seen more than once but with which you aren't very familiar",
                            ),
                            (
                                "Viewed once or described",
                                "A place you have seen once, possibly using magic, or a place you know through someone else's description, perhaps from a map",
                            ),
                            (
                                "False destination",
                                "A place that doesn't exist. Perhaps you tried to scry an enemy's sanctum but instead viewed an illusion, or you are attempting to teleport to a location that no longer exists",
                            ),
                        ),
                    ),
                ),
            ),
            Option(
                "Mishap",
                (
                    Facts(
                        (
                            (
                                "Journey",
                                "The spell's unpredictable magic results in a difficult journey",
                            ),
                            (
                                "Damage",
                                "Each teleporting creature (or the target object) takes 3d10 Force damage",
                            ),
                            (
                                "Reroll",
                                "The DM rerolls on the table to see where you wind up (multiple mishaps can occur, dealing damage each time)",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Similar Area",
                (
                    Facts(
                        (
                            (
                                "Arrive",
                                "You and your group (or the target object) appear in a different area that's visually or thematically similar to the target area",
                            ),
                            ("Closest", "You appear in the closest similar place"),
                            (
                                "Example",
                                "If you are heading for your home laboratory, for example, you might appear in another person's laboratory in the same city",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Off Target",
                (
                    Facts(
                        (
                            (
                                "Arrive",
                                "You and your group (or the target object) appear 2d12 miles away from the destination in a random direction",
                            ),
                            (
                                "Direction",
                                "Roll 1d8 for the direction: 1, east; 2, southeast; 3, south; 4, southwest; 5, west; 6, northwest; 7, north; or 8, northeast",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "On Target",
                (
                    Facts(
                        (
                            (
                                "Arrive",
                                "You and your group (or the target object) appear where you intended",
                            ),
                        )
                    ),
                ),
            ),
        ]


class TempleOfTheGods(ClassSpell):
    rules = SpellRules(
        name="Temple of the Gods",
        level=7,
        school=School.CONJURATION,
        classes=(CharacterClass.CLERIC,),
        casting_time=CastingTime(CastingTimeType.HOUR, 1),
        range=Range(RangeType.FOOT, 120),
        components=Components(
            verbal=True, somatic=True, material="a holy symbol worth at least 5 gp"
        ),
        duration=Duration(DurationType.HOUR, 24),
        source="Xanathar's Guide to Everything",
        description=(
            "You cause a temple to shimmer into existence on ground you can see within range. The temple must fit within an unoccupied cube of space, up to 120 feet on each side. The temple remains until the spell ends. It is dedicated to whatever god, pantheon, or philosophy is represented by the holy symbol used in the casting.\n"
            "You make all decisions about the temple's appearance. The interior is enclosed by a floor, walls, and a roof, with one door granting access to the interior and as many windows as you wish. Only you and any creatures you designate when you cast the spell can open or close the door.\n"
            "The temple's interior is an open space with an idol or altar at one end. You decide whether the temple is illuminated and whether that illumination is bright light or dim light. The smell of burning incense fills the air within, and the temperature is mild.\n"
            "The temple opposes types of creatures you choose when you cast this spell. Choose one or more of the following: celestials, elementals, fey, fiends, or undead. If a creature of the chosen type attempts to enter the temple, that creature must make a Charisma saving throw. On a failed save, it can't enter the temple for 24 hours. Even if the creature can enter the temple, the magic there hinders it; whenever it makes an attack roll, an ability check, or a saving throw inside the temple, it must roll a d4 and subtract the number rolled from the d20 roll.\n"
            "In addition, the sensors created by divination spells can't appear inside the temple, and creatures within can't be targeted by divination spells.\n"
            "Finally, whenever any creature in the temple regains hit points from a spell of 1st level or higher, the creature regains additional hit points equal to your Wisdom modifier (minimum 1 hit point).\n"
            "The temple is made from opaque magical force that extends into the Ethereal Plane, thus blocking ethereal travel into the temple's interior. Nothing can physically pass through the temple's exterior. It can't be dispelled by dispel magic, and antimagic field has no effect on it. A disintegrate spell destroys the temple instantly. Casting this spell on the same spot every day for a year makes this effect permanent."
        ),
        usage_tags=("control", "heal", "utility"),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "9bdb238eafbfad19")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You cause a temple to shimmer into existence on ground you can see within range.",
                    ),
                    ("Placement", "On ground you can see within range"),
                    ("Duration", "The temple remains until the spell ends"),
                    (
                        "Size",
                        "The temple must fit within an unoccupied cube of space, up to 120 feet on each side",
                    ),
                    (
                        "Dedication",
                        "It is dedicated to whatever god, pantheon, or philosophy is represented by the holy symbol used in the casting",
                    ),
                    (
                        "Appearance",
                        "You make all decisions about the temple's appearance",
                    ),
                    (
                        "Enclosure",
                        "The interior is enclosed by a floor, walls, and a roof, with one door granting access to the interior and as many windows as you wish",
                    ),
                    (
                        "Door",
                        "Only you and any creatures you designate when you cast the spell can open or close the door",
                    ),
                    (
                        "Interior",
                        "The temple's interior is an open space with an idol or altar at one end",
                    ),
                    (
                        "Light",
                        "You decide whether the temple is illuminated and whether that illumination is bright light or dim light",
                    ),
                    (
                        "Air",
                        "The smell of burning incense fills the air within, and the temperature is mild",
                    ),
                )
            ),
            Option(
                "Opposed Creatures",
                (
                    Facts(
                        (
                            (
                                "Opposes",
                                "The temple opposes types of creatures you choose when you cast this spell. Choose one or more of the following: celestials, elementals, fey, fiends, or undead",
                            ),
                            (
                                "Entering",
                                "If a creature of the chosen type attempts to enter the temple, that creature must make a Charisma saving throw",
                            ),
                            ("Failed save", "It can't enter the temple for 24 hours"),
                            (
                                "Hindered",
                                "Even if the creature can enter the temple, the magic there hinders it; whenever it makes an attack roll, an ability check, or a saving throw inside the temple, it must roll a d4 and subtract the number rolled from the d20 roll",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Divination",
                (
                    Facts(
                        (
                            (
                                "Sensors",
                                "The sensors created by divination spells can't appear inside the temple",
                            ),
                            (
                                "Targets",
                                "Creatures within can't be targeted by divination spells",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Healing",
                (
                    Facts(
                        (
                            (
                                "Extra healing",
                                "Whenever any creature in the temple regains hit points from a spell of 1st level or higher, the creature regains additional hit points equal to your Wisdom modifier (minimum 1 hit point)",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "The Temple's Walls",
                (
                    Facts(
                        (
                            (
                                "Made of",
                                "The temple is made from opaque magical force that extends into the Ethereal Plane, thus blocking ethereal travel into the temple's interior",
                            ),
                            (
                                "Exterior",
                                "Nothing can physically pass through the temple's exterior",
                            ),
                            (
                                "Immune",
                                "It can't be dispelled by dispel magic, and antimagic field has no effect on it",
                            ),
                            (
                                "Destroyed",
                                "A disintegrate spell destroys the temple instantly",
                            ),
                            (
                                "Permanent",
                                "Casting this spell on the same spot every day for a year makes this effect permanent",
                            ),
                        )
                    ),
                ),
            ),
        ]


class Transfix(ClassSpell):
    rules = SpellRules(
        name="Transfix",
        level=7,
        school=School.ENCHANTMENT,
        classes=(CharacterClass.BARD, CharacterClass.WARLOCK, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Arcana Unleashed",
        description=(
            "For the duration, your appearance becomes otherworldly and alluring. One creature of your choice that you can see within 60 feet of you must succeed on a Charisma saving throw or have the Charmed condition for the duration.\n"
            "While Charmed, the target has the Incapacitated condition, and if the target is more than 5 feet away from you, it moves on its turn toward you by the most direct route, trying to get within 5 feet of you. If the Charmed creature ends its turn within 5 feet of you, it takes 4d8 Psychic damage.\n"
            "The target doesn’t avoid Opportunity Attacks when moving toward you, but before moving into damaging terrain (such as lava or a pit), the target repeats the save, ending the spell on itself on a success.\n"
            "Until the spell ends, you can take a Magic action on subsequent turns to target another creature, but you can’t target a creature again if it has succeeded on a save against this casting of the spell.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 1d8 for each spell slot level above 7."
        ),
        usage_tags=("control", "damage"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "12155d1456f72c83")


class VoidStar(ClassSpell):
    rules = SpellRules(
        name="Void Star",
        level=7,
        school=School.NECROMANCY,
        classes=(CharacterClass.WARLOCK, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 120),
        components=Components(
            verbal=True, somatic=True, material="a fragment of a meteor"
        ),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="D&D Beyond Drops - June 2026",
        description=(
            "You conjure forth a fragment of a dark star and launch it at one creature that you can see within range. Make a ranged spell attack against the target. On a hit, the target takes 6d12 Necrotic damage. Hit or miss, the target takes 3d12 Necrotic damage at the end of its next turn, and you regain Hit Points equal to that damage.\n"
            "Using a Higher-Level Spell Slot. The damage (both initial and later) increases by 1d12 for each spell slot level above 7."
        ),
        usage_tags=("damage", "heal"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "3f1e1ee56f11fe96")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You conjure forth a fragment of a dark star and launch it at one creature that you can see within range.",
                    ),
                    ("Target", "One creature that you can see within range"),
                    ("Attack", "Ranged spell attack"),
                    ("On a hit", "The target takes 6d12 Necrotic damage"),
                    (
                        "Next turn",
                        "At the end of the target's next turn, it takes 3d12 Necrotic damage, and you regain Hit Points equal to the amount of Necrotic damage dealt",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (
                    Facts(
                        (
                            (
                                "Damage",
                                "The damage (both initial and later) increases by 1d12 for each spell slot level above 7",
                            ),
                        )
                    ),
                ),
            ),
        ]


class Whirlwind(ClassSpell):
    rules = SpellRules(
        name="Whirlwind",
        level=7,
        school=School.EVOCATION,
        classes=(CharacterClass.DRUID, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 300),
        components=Components(verbal=True, material="a piece of straw"),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Xanathar's Guide to Everything",
        description=(
            "A whirlwind howls down to a point on the ground you specify. The whirlwind is a 10-foot-radius, 30-foot-high cylinder centered on that point. Until the spell ends, you can use your action to move the whirlwind up to 30 feet in any direction along the ground. The whirlwind sucks up any Medium or smaller objects that aren't secured to anything and that aren't worn or carried by anyone.\n"
            "A creature must make a Dexterity saving throw the first time on a turn that it enters the whirlwind or that the whirlwind enters its space, including when the whirlwind first appears. A creature takes 10d6 bludgeoning damage on a failed save, or half as much damage on a successful one. In addition, a Large or smaller creature that fails the save must succeed on a Strength saving throw or become restrained in the whirlwind until the spell ends.\n"
            "When a creature starts its turn restrained by the whirlwind, the creature is pulled 5 feet higher inside it, unless the creature is at the top. A restrained creature moves with the whirlwind and falls when the spell ends, unless the creature has some means to stay aloft.\n"
            "A restrained creature can use an action to make a Strength or Dexterity check against your spell save DC. If successful, the creature is no longer restrained by the whirlwind and is hurled 3d6 × 10 feet away from it in a random direction."
        ),
        usage_tags=("control", "damage"),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "c7f7456194237b01")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "A whirlwind howls down to a point on the ground you specify.",
                    ),
                    ("Point", "A point on the ground you specify"),
                    (
                        "Area",
                        "10-foot-radius, 30-foot-high cylinder centered on that point",
                    ),
                    (
                        "Moving",
                        "Until the spell ends, you can use your action to move the whirlwind up to 30 feet in any direction along the ground",
                    ),
                    (
                        "Objects",
                        "The whirlwind sucks up any Medium or smaller objects that aren't secured to anything and that aren't worn or carried by anyone",
                    ),
                    (
                        "Save",
                        "Dexterity, made by a creature the first time on a turn that it enters the whirlwind or that the whirlwind enters its space, including when the whirlwind first appears",
                    ),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (("10d6 bludgeoning damage", "Half as much damage"),),
            ),
            Option(
                "Restrained in the Whirlwind",
                (
                    Facts(
                        (
                            (
                                "Who",
                                "A Large or smaller creature that fails the Dexterity save",
                            ),
                            ("Save", "Strength"),
                            (
                                "Failed save",
                                "The creature becomes restrained in the whirlwind until the spell ends",
                            ),
                            ("Successful save", "Not restrained"),
                            (
                                "Rising",
                                "When a creature starts its turn restrained by the whirlwind, the creature is pulled 5 feet higher inside it, unless the creature is at the top",
                            ),
                            (
                                "Falling",
                                "A restrained creature moves with the whirlwind and falls when the spell ends, unless the creature has some means to stay aloft",
                            ),
                            (
                                "Escape",
                                "A restrained creature can use an action to make a Strength or Dexterity check against your spell save DC",
                            ),
                            (
                                "If successful",
                                "The creature is no longer restrained by the whirlwind and is hurled 3d6 × 10 feet away from it in a random direction",
                            ),
                        )
                    ),
                ),
            ),
        ]


class TetherEssence(ClassSpell):
    rules = SpellRules(
        name="Tether Essence",
        level=7,
        school=School.NECROMANCY,
        classes=(CharacterClass.WIZARD,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(
            verbal=True,
            somatic=True,
            material="a spool of platinum cord worth at least 250 gp, which the spell consumes",
        ),
        duration=Duration(DurationType.HOUR, 1, concentration=True),
        source="Explorer's Guide to Wildemount",
        description="Two creatures you can see within range must make a Constitution saving throw, with disadvantage if they are within 30 feet of each other. Either creature can willingly fail the save. If either save succeeds, the spell has no effect. If both saves fail, the creatures are magically linked for the duration, regardless of the distance between them. When damage is dealt to one of them, the same damage is dealt to the other one. If hit points are restored to one of them, the same number of hit points are restored to the other one. If either of the tethered creatures is reduced to 0 hit points, the spell ends on both. If the spell ends on one creature, it ends on both.",
        usage_tags=("damage", "heal", "utility"),
        target=FeatureTarget.CREATURE,
        school_note="Dunamancy",
    )
    converted_from = RecordStamp("spells_dnd5e.json", "fba9d16d553fddd1")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Targets", "Two creatures you can see within range"),
                    (
                        "Save",
                        "Constitution, made by both creatures, with disadvantage if they are within 30 feet of each other",
                    ),
                    ("Willingly", "Either creature can willingly fail the save"),
                    (
                        "Successful save",
                        "If either save succeeds, the spell has no effect",
                    ),
                    (
                        "Both fail",
                        "If both saves fail, the creatures are magically linked for the duration, regardless of the distance between them",
                    ),
                    (
                        "Damage",
                        "When damage is dealt to one of them, the same damage is dealt to the other one",
                    ),
                    (
                        "Healing",
                        "If hit points are restored to one of them, the same number of hit points are restored to the other one",
                    ),
                    (
                        "Ends early",
                        "If either of the tethered creatures is reduced to 0 hit points, the spell ends on both",
                    ),
                    (
                        "Ends on one",
                        "If the spell ends on one creature, it ends on both",
                    ),
                )
            )
        ]


class LayWaste(ClassSpell):
    rules = SpellRules(
        name="Lay Waste",
        level=7,
        school=School.EVOCATION,
        classes=(CharacterClass.SORCERER,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="World of Warcraft",
        description=(
            "You draw a deep breath and spew molten cinders along a 120-foot-long, 10-foot-wide Line originating from you in a direction you choose. Each creature in the Line makes a Dexterity saving throw, taking 12d6 Fire damage on a failed save or half as much damage on a successful one.\n"
            "You then teleport to an unoccupied space within 5 feet of the end of the Line."
        ),
        usage_tags=("buff", "damage"),
    )
    converted_from = RecordStamp("spells_dnd2024.json", "2743a2935ccce2ca")


SPELLS = [
    AuraOfEvasion,
    ConjureCelestial,
    CreateMagen,
    CrownOfStars,
    DelayedBlastFireball,
    DivineWord,
    DraconicTransformation,
    DreamOfTheBlueVeil,
    Etherealness,
    FingerOfDeath,
    FireStorm,
    Forcecage,
    FracturedAwareness,
    LayWaste,
    MirageArcane,
    MordenkainensMagnificentMansion,
    MordenkainensSword,
    PlaneShift,
    PowerWordFortify,
    PowerWordPain,
    PrismaticSpray,
    ProjectImage,
    Regenerate,
    Resurrection,
    ReverseGravity,
    ReweaveFate,
    Sequester,
    SimbulsSynostodweomer,
    Simulacrum,
    Symbol,
    Teleport,
    TempleOfTheGods,
    TetherEssence,
    Transfix,
    VoidStar,
    Whirlwind,
]
