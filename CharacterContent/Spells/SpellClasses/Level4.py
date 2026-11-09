"""Level 4 spells as classes (CharacterContent/Spells/SpellFactory/ClassSpell.py),
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
from Core.Definitions import Ability, CharacterClass, DamageType
from Model.Content.CombatEffect import CombatDamage, CombatEffect, EffectRoll
from Model.Content.Feature import FeatureTarget
from Model.Content.FeatureText import Block, Facts, Option, Paragraph, Table
from Model.View import CharacterView


class IceStorm(ClassSpell):
    rules = SpellRules(
        name="Ice Storm",
        level=4,
        school=School.EVOCATION,
        classes=(CharacterClass.DRUID, CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 300),
        components=Components(verbal=True, somatic=True, material="a mitten"),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "Hail falls in a 20-foot-radius, 40-foot-high Cylinder centered on a point within range. Each creature in the Cylinder makes a Dexterity saving throw. A creature takes 2d10 Bludgeoning damage and 4d6 Cold damage on a failed save or half as much damage on a successful one.\n"
            "Hailstones turn ground in the Cylinder into Difficult Terrain until the end of your next turn.\n"
            "Using a Higher-Level Spell Slot. The Bludgeoning damage increases by 1d10 for each spell slot level above 4."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "6520a2bfa5cb77f9")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("Hail falls in an area."),
            Facts(
                (
                    (
                        "Area",
                        "20-foot-radius, 40-foot-high Cylinder centered on a point within range",
                    ),
                    ("Save", "Dexterity, made by each creature in the Cylinder"),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (
                    (
                        "2d10 Bludgeoning damage and 4d6 Cold damage",
                        "Half as much damage",
                    ),
                ),
            ),
            Facts(
                (
                    (
                        "Terrain",
                        "Hailstones turn ground in the Cylinder into Difficult Terrain until the end of your next turn",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (
                    Facts(
                        (
                            (
                                "Bludgeoning damage",
                                "+1d10 for each spell slot level above 4",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def combat_effects(
        self, character: CharacterView | None = None
    ) -> list[CombatEffect]:
        return [
            CombatEffect(
                roll=EffectRoll.SAVE,
                save_ability=Ability.DEXTERITY,
                half_on_success=True,
                damage=(
                    CombatDamage("2d10", DamageType.BLUDGEONING, upcast="1d10"),
                    CombatDamage("4d6", DamageType.COLD),
                ),
                notes=(
                    "The ground in the Cylinder is Difficult Terrain until the end of your next turn.",
                ),
            )
        ]


class ArcaneEye(ClassSpell):
    rules = SpellRules(
        name="Arcane Eye",
        level=4,
        school=School.DIVINATION,
        classes=(CharacterClass.ARTIFICER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 30),
        components=Components(verbal=True, somatic=True, material="a bit of bat fur"),
        duration=Duration(DurationType.HOUR, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "You create an Invisible, invulnerable eye within range that hovers for the duration. You mentally receive visual information from the eye, which can see in every direction. It also has Darkvision with a range of 30 feet.\n"
            "As a Bonus Action, you can move the eye up to 30 feet in any direction. A solid barrier blocks the eye’s movement, but the eye can pass through an opening as small as 1 inch in diameter."
        ),
        usage_tags=("buff",),
    )
    converted_from = RecordStamp("spells_dnd2024.json", "2b7fabb0f3bc97d0")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You create an Invisible, invulnerable eye within range that hovers for the duration."
            ),
            Facts(
                (
                    (
                        "Vision",
                        "You mentally receive visual information from the eye, which can see in every direction",
                    ),
                    ("Darkvision", "The eye has Darkvision with a range of 30 feet"),
                    (
                        "Moving",
                        "As a Bonus Action, you can move the eye up to 30 feet in any direction",
                    ),
                    (
                        "Barriers",
                        "A solid barrier blocks the eye's movement, but the eye can pass through an opening as small as 1 inch in diameter",
                    ),
                )
            ),
        ]


class AuraOfLife(ClassSpell):
    rules = SpellRules(
        name="Aura of Life",
        level=4,
        school=School.ABJURATION,
        classes=(CharacterClass.CLERIC, CharacterClass.PALADIN),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True),
        duration=Duration(DurationType.MINUTE, 10, concentration=True),
        source="Player's Handbook",
        description="An aura radiates from you in a 30-foot Emanation for the duration. While in the aura, you and your allies have Resistance to Necrotic damage, and your Hit Point maximums can’t be reduced. If an ally with 0 Hit Points starts its turn in the aura, that ally regains 1 Hit Point.",
        usage_tags=("buff", "heal"),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "80c6ac7ed3e6ed01")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Area", "30-foot Emanation"),
                    (
                        "Resistance",
                        "While in the aura, you and your allies have Resistance to Necrotic damage",
                    ),
                    (
                        "Hit Point maximum",
                        "While in the aura, your and your allies' Hit Point maximums can't be reduced",
                    ),
                    (
                        "0 Hit Points",
                        "If an ally with 0 Hit Points starts its turn in the aura, that ally regains 1 Hit Point",
                    ),
                )
            )
        ]


class AuraOfPurity(ClassSpell):
    rules = SpellRules(
        name="Aura of Purity",
        level=4,
        school=School.ABJURATION,
        classes=(CharacterClass.CLERIC, CharacterClass.PALADIN),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True),
        duration=Duration(DurationType.MINUTE, 10, concentration=True),
        source="Player's Handbook",
        description="An aura radiates from you in a 30-foot Emanation for the duration. While in the aura, you and your allies have Resistance to Poison damage and Advantage on saving throws to avoid or end effects that include the Blinded, Charmed, Deafened, Frightened, Paralyzed, Poisoned, or Stunned condition.",
        usage_tags=("buff",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "ed814672a87ce28b")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Area", "30-foot Emanation"),
                    (
                        "Resistance",
                        "While in the aura, you and your allies have Resistance to Poison damage",
                    ),
                    (
                        "Saves",
                        "While in the aura, you and your allies have Advantage on saving throws to avoid or end effects that include the Blinded, Charmed, Deafened, Frightened, Paralyzed, Poisoned, or Stunned condition",
                    ),
                )
            )
        ]


class Backlash(ClassSpell):
    rules = SpellRules(
        name="Backlash",
        level=4,
        school=School.ABJURATION,
        classes=(
            CharacterClass.BARD,
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(
            CastingTimeType.REACTION,
            trigger="which you take in response to taking damage",
        ),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Forgotten Realms - Heroes of Faerun",
        description=(
            "You ward yourself against destructive energy, reducing the damage taken by 4d6 plus your spellcasting ability modifier.\n"
            "If the triggering damage was from a creature within range, you can force the creature to make a Constitution saving throw. The creature takes 4d6 Force damage on a failed save or half as much damage on a successful one.\n"
            "Using a Higher-Level Spell Slot. The damage reduction and Force damage from this spell both increase by 1d6 for every spell slot level above 4."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "cc4626f89031ead9")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Flavor", "You ward yourself against destructive energy."),
                    ("Trigger", "You take damage"),
                    (
                        "Reduction",
                        "You reduce the damage taken by 4d6 + your spellcasting ability modifier",
                    ),
                    (
                        "Retaliation",
                        "If the triggering damage was from a creature within range, you can force the creature to make a Constitution saving throw",
                    ),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (("4d6 Force damage", "Half as much damage"),),
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (
                    Facts(
                        (
                            (
                                "Increase",
                                "The damage reduction and Force damage both increase by 1d6 for every spell slot level above 4",
                            ),
                        )
                    ),
                ),
            ),
        ]


class Banishment(ClassSpell):
    rules = SpellRules(
        name="Banishment",
        level=4,
        school=School.ABJURATION,
        classes=(
            CharacterClass.CLERIC,
            CharacterClass.PALADIN,
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 30),
        components=Components(verbal=True, somatic=True, material="a pentacle"),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "One creature that you can see within range must succeed on a Charisma saving throw or be transported to a harmless demiplane for the duration. While there, the target has the Incapacitated condition. When the spell ends, the target reappears in the space it left or in the nearest unoccupied space if that space is occupied.\n"
            "If the target is an Aberration, a Celestial, an Elemental, a Fey, or a Fiend, the target doesn't return if the spell lasts for 1 minute. The target is instead transported to a random location on a plane (DM’s choice) associated with its creature type.\n"
            "Using a Higher-Level Spell Slot. You can target one additional creature for each spell slot level above 4."
        ),
        usage_tags=("control",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "92f5631b792c8d2c")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You try to send a creature to a harmless demiplane."),
            Facts(
                (
                    ("Target", "One creature that you can see within range"),
                    ("Save", "Charisma"),
                    (
                        "Failed save",
                        "Transported to a harmless demiplane for the duration; while there, the target has the Incapacitated condition",
                    ),
                    (
                        "Spell ends",
                        "The target reappears in the space it left, or in the nearest unoccupied space if that space is occupied",
                    ),
                    (
                        "Otherworldly",
                        "If the target is an Aberration, a Celestial, an Elemental, a Fey, or a Fiend, it doesn't return if the spell lasts for 1 minute; it is instead transported to a random location on a plane (DM's choice) associated with its creature type",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (
                    Facts(
                        (("Targets", "+1 creature for each spell slot level above 4"),)
                    ),
                ),
            ),
        ]


class Blight(ClassSpell):
    rules = SpellRules(
        name="Blight",
        level=4,
        school=School.NECROMANCY,
        classes=(
            CharacterClass.DRUID,
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 30),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "A creature that you can see within range makes a Constitution saving throw, taking 8d8 Necrotic damage on a failed save or half as much damage on a successful one. A Plant creature automatically fails the save.\n"
            "Alternatively, target a nonmagical plant that isn’t a creature, such as a tree or shrub. It doesn’t make a save; it simply withers and dies.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 1d8 for each spell slot level above 4."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "118e267dc12925e0")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Target", "A creature that you can see within range"),
                    ("Save", "Constitution; a Plant creature automatically fails"),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (("8d8 Necrotic damage", "Half as much damage"),),
            ),
            Facts(
                (
                    (
                        "Plants",
                        "Alternatively, target a nonmagical plant that isn't a creature, such as a tree or shrub; it doesn't make a save, and simply withers and dies",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Damage", "+1d8 for each spell slot level above 4"),)),),
            ),
        ]


class CharmMonster(ClassSpell):
    rules = SpellRules(
        name="Charm Monster",
        level=4,
        school=School.ENCHANTMENT,
        classes=(
            CharacterClass.BARD,
            CharacterClass.DRUID,
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 30),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.HOUR, 1),
        source="Player's Handbook",
        description=(
            "One creature you can see within range makes a Wisdom saving throw. It does so with Advantage if you or your allies are fighting it. On a failed save, the target has the Charmed condition until the spell ends or until you or your allies damage it. The Charmed creature is Friendly to you. When the spell ends, the target knows it was Charmed by you.\n"
            "Using a Higher-Level Spell Slot. You can target one additional creature for each spell slot level above 4."
        ),
        usage_tags=("control",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "1f0b8aa79ff06c1b")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You try to charm a creature."),
            Facts(
                (
                    ("Target", "One creature you can see within range"),
                    (
                        "Save",
                        "Wisdom, with Advantage if you or your allies are fighting it",
                    ),
                    (
                        "Failed save",
                        "Charmed until the spell ends or until you or your allies damage it",
                    ),
                    ("Charmed", "The Charmed creature is Friendly to you"),
                    (
                        "Afterward",
                        "When the spell ends, the target knows it was Charmed by you",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (
                    Facts(
                        (("Targets", "+1 creature for each spell slot level above 4"),)
                    ),
                ),
            ),
        ]


class Compulsion(ClassSpell):
    rules = SpellRules(
        name="Compulsion",
        level=4,
        school=School.ENCHANTMENT,
        classes=(CharacterClass.BARD,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 30),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "Each creature of your choice that you can see within range must succeed on a Wisdom saving throw or have the Charmed condition until the spell ends.\n"
            "For the duration, you can take a Bonus Action to designate a direction that is horizontal to you. Each Charmed target must use as much of its movement as possible to move in that direction on its next turn, taking the safest route. After moving in this way, a target repeats the save, ending the spell on itself on a success."
        ),
        usage_tags=("control",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "47c1cf408f497180")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You compel creatures to move in a direction you choose."),
            Facts(
                (
                    (
                        "Targets",
                        "Each creature of your choice that you can see within range",
                    ),
                    ("Save", "Wisdom"),
                    ("Failed save", "Charmed until the spell ends"),
                    (
                        "Direction",
                        "For the duration, you can take a Bonus Action to designate a direction that is horizontal to you",
                    ),
                    (
                        "Movement",
                        "Each Charmed target must use as much of its movement as possible to move in that direction on its next turn, taking the safest route",
                    ),
                    (
                        "Repeat save",
                        "After moving in this way, a target repeats the save, ending the spell on itself on a success",
                    ),
                )
            ),
        ]


class Confusion(ClassSpell):
    rules = SpellRules(
        name="Confusion",
        level=4,
        school=School.ENCHANTMENT,
        classes=(
            CharacterClass.BARD,
            CharacterClass.DRUID,
            CharacterClass.SORCERER,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 90),
        components=Components(verbal=True, somatic=True, material="three nut shells"),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "Each creature in a 10-foot-radius Sphere centered on a point you choose within range must succeed on a Wisdom saving throw, or that target can’t take Bonus Actions or Reactions and must roll 1d10 at the start of each of its turns to determine its behavior for that turn, consulting the table below.\n"
            "At the end of each of its turns, an affected target repeats the save, ending the spell on itself on a success.\n"
            "Using a Higher-Level Spell Slot. The Sphere’s radius increases by 5 feet for each spell slot level above 4."
        ),
        usage_tags=("control",),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "64d2185f65f57d15")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Area",
                        "10-foot-radius Sphere centered on a point you choose within range",
                    ),
                    ("Save", "Wisdom, made by each creature in the Sphere"),
                    (
                        "Failed save",
                        "The target can't take Bonus Actions or Reactions, and it must roll 1d10 at the start of each of its turns to determine its behavior for that turn (below)",
                    ),
                    (
                        "Repeat save",
                        "At the end of each of its turns, ending the spell on itself on a success",
                    ),
                )
            ),
            Table(
                ("1d10", "Behavior for the turn"),
                (
                    (
                        "1",
                        "The target doesn't take an action, and it uses all its movement to move; roll 1d4 for the direction: 1, north; 2, east; 3, south; or 4, west",
                    ),
                    ("2-6", "The target doesn't move or take actions"),
                    (
                        "7-8",
                        "The target doesn't move, and it takes the Attack action to make one melee attack against a random creature within reach; if none are within reach, the target takes no action",
                    ),
                    ("9-10", "The target chooses its behavior"),
                ),
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Radius", "+5 feet for each spell slot level above 4"),)),),
            ),
        ]


class ConjureMinorElementals(ClassSpell):
    rules = SpellRules(
        name="Conjure Minor Elementals",
        level=4,
        school=School.CONJURATION,
        classes=(CharacterClass.DRUID, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 10, concentration=True),
        source="Player's Handbook",
        description=(
            "You conjure spirits from the Elemental Planes that flit around you in a 15-foot Emanation for the duration. Until the spell ends, any attack you make deals an extra 2d8 damage when you hit a creature in the Emanation. This damage is Acid, Cold, Fire, or Lightning (your choice when you make the attack).\n"
            "In addition, the ground in the Emanation is Difficult Terrain for your enemies.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 1d8 for each spell slot level above 4."
        ),
        usage_tags=("control",),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "441e741d912c26a2")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You conjure spirits from the Elemental Planes that flit around you in a 15-foot Emanation for the duration.",
                    ),
                    ("Area", "15-foot Emanation"),
                    (
                        "Extra damage",
                        "Until the spell ends, any attack you make deals an extra 2d8 damage when you hit a creature in the Emanation",
                    ),
                    (
                        "Damage type",
                        "Acid, Cold, Fire, or Lightning (your choice when you make the attack)",
                    ),
                    (
                        "Terrain",
                        "The ground in the Emanation is Difficult Terrain for your enemies",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Damage", "+1d8 for each spell slot level above 4"),)),),
            ),
        ]


class ConjureWoodlandBeings(ClassSpell):
    rules = SpellRules(
        name="Conjure Woodland Beings",
        level=4,
        school=School.CONJURATION,
        classes=(CharacterClass.DRUID, CharacterClass.RANGER),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 10, concentration=True),
        source="Player's Handbook",
        description=(
            "You conjure nature spirits that flit around you in a 10-foot Emanation for the duration. Whenever the Emanation enters the space of a creature you can see and whenever a creature you can see enters the Emanation or ends its turn there, you can force that creature to make a Wisdom saving throw. The creature takes 5d8 Force damage on a failed save or half as much damage on a successful one. A creature makes this save only once per turn.\n"
            "In addition, you can take the Disengage action as a Bonus Action for the spell’s duration.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 1d8 for each spell slot level above 4."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "f8d2737c05251924")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You conjure nature spirits that flit around you in a 10-foot Emanation for the duration.",
                    ),
                    ("Area", "10-foot Emanation"),
                    (
                        "Trigger",
                        "Whenever the Emanation enters the space of a creature you can see, and whenever a creature you can see enters the Emanation or ends its turn there, you can force that creature to make a Wisdom saving throw",
                    ),
                    ("Limit", "A creature makes this save only once per turn"),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (("5d8 Force damage", "Half as much damage"),),
            ),
            Facts(
                (
                    (
                        "Disengage",
                        "You can take the Disengage action as a Bonus Action for the spell's duration",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Damage", "+1d8 for each spell slot level above 4"),)),),
            ),
        ]


class ControlWater(ClassSpell):
    rules = SpellRules(
        name="Control Water",
        level=4,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.CLERIC, CharacterClass.DRUID, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 300),
        components=Components(
            verbal=True, somatic=True, material="a mixture of water and dust"
        ),
        duration=Duration(DurationType.MINUTE, 10, concentration=True),
        source="Player's Handbook",
        description=(
            "Until the spell ends, you control any water inside an area you choose that is a Cube up to 100 feet on a side, using one of the following effects. As a Magic action on your later turns, you can repeat the same effect or choose a different one.\n"
            "Flood. You cause the water level of all standing water in the area to rise by as much as 20 feet. If you choose an area in a large body of water, you instead create a 20-foot tall wave that travels from one side of the area to the other and then crashes. Any Huge or smaller vehicles in the wave’s path are carried with it to the other side. Any Huge or smaller vehicles struck by the wave have a 25 percent chance of capsizing.\n"
            "The water level remains elevated until the spell ends or you choose a different effect. If this effect produced a wave, the wave repeats on the start of your next turn while the flood effect lasts.\n"
            "Part Water. You part water in the area and create a trench. The trench extends across the spell’s area, and the separated water forms a wall to either side. The trench remains until the spell ends or you choose a different effect. The water then slowly fills in the trench over the course of the next round until the normal water level is restored.\n"
            "Redirect Flow. You cause flowing water in the area to move in a direction you choose, even if the water has to flow over obstacles, up walls, or in other unlikely directions. The water in the area moves as you direct it, but once it moves beyond the spell’s area, it resumes its flow based on the terrain. The water continues to move in the direction you chose until the spell ends or you choose a different effect.\n"
            "Whirlpool. You cause a whirlpool to form in the center of the area, which must be at least 50 feet square and 25 feet deep. The whirlpool lasts until you choose a different effect or the spell ends. The whirlpool is 5 feet wide at the base, up to 50 feet wide at the top, and 25 feet tall. Any creature in the water and within 25 feet of the whirlpool is pulled 10 feet toward it. When a creature enters the whirlpool for the first time on a turn or ends its turn there, it makes a Strength saving throw. On a failed save, the creature takes 2d8 Bludgeoning damage. On a successful save, the creature takes half as much damage. A creature can swim away from the whirlpool only if it first takes an action to pull away and succeeds on a Strength (Athletics) check against your spell save DC."
        ),
        usage_tags=("control", "damage"),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "b5ee63f3c459a277")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "Until the spell ends, you control any water inside an area you choose that is a Cube up to 100 feet on a side, using one of the effects below."
            ),
            Facts(
                (
                    (
                        "Changing",
                        "As a Magic action on your later turns, you can repeat the same effect or choose a different one",
                    ),
                )
            ),
            Option(
                "Flood",
                (
                    Facts(
                        (
                            (
                                "Water level",
                                "All standing water in the area rises by as much as 20 feet",
                            ),
                            (
                                "Large body",
                                "If you choose an area in a large body of water, you instead create a 20-foot-tall wave that travels from one side of the area to the other and then crashes",
                            ),
                            (
                                "Vehicles",
                                "Any Huge or smaller vehicles in the wave's path are carried with it to the other side; any Huge or smaller vehicles struck by the wave have a 25 percent chance of capsizing",
                            ),
                            (
                                "Lasts",
                                "The water level remains elevated until the spell ends or you choose a different effect; if this effect produced a wave, the wave repeats on the start of your next turn while the flood effect lasts",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Part Water",
                (
                    Facts(
                        (
                            (
                                "Trench",
                                "You part water in the area and create a trench that extends across the spell's area; the separated water forms a wall to either side",
                            ),
                            (
                                "Lasts",
                                "Until the spell ends or you choose a different effect; the water then slowly fills in the trench over the course of the next round until the normal water level is restored",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Redirect Flow",
                (
                    Facts(
                        (
                            (
                                "Effect",
                                "Flowing water in the area moves in a direction you choose, even if the water has to flow over obstacles, up walls, or in other unlikely directions",
                            ),
                            (
                                "Beyond the area",
                                "Once it moves beyond the spell's area, it resumes its flow based on the terrain",
                            ),
                            (
                                "Lasts",
                                "Until the spell ends or you choose a different effect",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Whirlpool",
                (
                    Facts(
                        (
                            (
                                "Requirement",
                                "The area must be at least 50 feet square and 25 feet deep",
                            ),
                            (
                                "Size",
                                "In the center of the area: 5 feet wide at the base, up to 50 feet wide at the top, and 25 feet tall",
                            ),
                            (
                                "Lasts",
                                "Until you choose a different effect or the spell ends",
                            ),
                            (
                                "Pull",
                                "Any creature in the water and within 25 feet of the whirlpool is pulled 10 feet toward it",
                            ),
                            (
                                "Save",
                                "Strength, when a creature enters the whirlpool for the first time on a turn or ends its turn there",
                            ),
                            ("Failed save", "2d8 Bludgeoning damage"),
                            ("Successful save", "Half as much damage"),
                            (
                                "Swimming away",
                                "A creature can swim away from the whirlpool only if it first takes an action to pull away and succeeds on a Strength (Athletics) check against your spell save DC",
                            ),
                        )
                    ),
                ),
            ),
        ]


class DeathWard(ClassSpell):
    rules = SpellRules(
        name="Death Ward",
        level=4,
        school=School.ABJURATION,
        classes=(CharacterClass.CLERIC, CharacterClass.PALADIN),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.TOUCH),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.HOUR, 8),
        source="Player's Handbook",
        description=(
            "You touch a creature and grant it a measure of protection from death. The first time the target would drop to 0 Hit Points before the spell ends, the target instead drops to 1 Hit Point, and the spell ends.\n"
            "If the spell is still in effect when the target is subjected to an effect that would kill it instantly without dealing damage, that effect is negated against the target, and the spell ends."
        ),
        usage_tags=("buff",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "915349d61f2f8c6c")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You touch a creature and grant it a measure of protection from death."
            ),
            Facts(
                (
                    (
                        "At 0 Hit Points",
                        "The first time the target would drop to 0 Hit Points before the spell ends, the target instead drops to 1 Hit Point, and the spell ends",
                    ),
                    (
                        "Instant death",
                        "If the spell is still in effect when the target is subjected to an effect that would kill it instantly without dealing damage, that effect is negated against the target, and the spell ends",
                    ),
                )
            ),
        ]


class DimensionDoor(ClassSpell):
    rules = SpellRules(
        name="Dimension Door",
        level=4,
        school=School.CONJURATION,
        classes=(
            CharacterClass.BARD,
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 500),
        components=Components(verbal=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "You teleport to a location within range. You arrive at exactly the spot desired. It can be a place you can see, one you can visualize, or one you can describe by stating distance and direction, such as “200 feet straight downward” or “300 feet upward to the northwest at a 45-degree angle.”\n"
            "You can also teleport one willing creature. The creature must be within 5 feet of you when you teleport, and it teleports to a space within 5 feet of your destination space.\n"
            "If you, the other creature, or both would arrive in a space occupied by a creature or completely filled by one or more objects, you and any creature traveling with you each take 4d6 Force damage, and the teleportation fails."
        ),
        usage_tags=("buff",),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "e06689a55aaadedf")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You teleport to a location within range, arriving at exactly the spot desired."
            ),
            Facts(
                (
                    (
                        "Destination",
                        'A place you can see, one you can visualize, or one you can describe by stating distance and direction, such as "200 feet straight downward" or "300 feet upward to the northwest at a 45-degree angle"',
                    ),
                    (
                        "Passenger",
                        "You can also teleport one willing creature; it must be within 5 feet of you when you teleport, and it teleports to a space within 5 feet of your destination space",
                    ),
                    (
                        "Blocked",
                        "If you, the other creature, or both would arrive in a space occupied by a creature or completely filled by one or more objects, you and any creature traveling with you each take 4d6 Force damage, and the teleportation fails",
                    ),
                )
            ),
        ]


class DistortedDistance(ClassSpell):
    rules = SpellRules(
        name="Distorted Distance",
        level=4,
        school=School.ILLUSION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.BARD,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 120),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 10, concentration=True),
        source="Arcana Unleashed",
        description=(
            "You create an illusory spatial dilation that fills a 60-foot-radius Sphere centered on a point within range. For each creature you can see in the Sphere, you can choose one of the following effects for it:\n"
            "Dizzying Elongation. The creature makes an Intelligence saving throw. On a failed save, the creature takes 2d10 Psychic damage, and the Sphere is Difficult Terrain for it until the end of its turn.\n"
            "Shortened Space. The creature’s Speed increases by 20 feet until the end of its next turn.\n"
            "Until the spell ends, whenever a creature enters the Sphere or ends its turn there, you can choose for it to receive one of these effects. A creature can be affected by this spell only once per turn."
        ),
        usage_tags=("buff", "control", "damage"),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "b4cf78869efcdc59")


class Divination(ClassSpell):
    rules = SpellRules(
        name="Divination",
        level=4,
        school=School.DIVINATION,
        classes=(CharacterClass.CLERIC, CharacterClass.DRUID, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION, ritual=True),
        range=Range(RangeType.SELF),
        components=Components(
            verbal=True,
            somatic=True,
            material="incense worth 25+ GP, which the spell consumes",
        ),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "This spell puts you in contact with a god or a god’s servants. You ask one question about a specific goal, event, or activity to occur within 7 days. The DM offers a truthful reply, which might be a short phrase or cryptic rhyme. The spell doesn’t account for circumstances that might change the answer, such as the casting of other spells.\n"
            "If you cast the spell more than once before finishing a Long Rest, there is a cumulative 25 percent chance for each casting after the first that you get no answer."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "342888e9ca33ada9")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "This spell puts you in contact with a god or a god's servants.",
                    ),
                    (
                        "Question",
                        "One question about a specific goal, event, or activity to occur within 7 days",
                    ),
                    (
                        "Answer",
                        "The DM offers a truthful reply, which might be a short phrase or cryptic rhyme",
                    ),
                    (
                        "Limit",
                        "The spell doesn't account for circumstances that might change the answer, such as the casting of other spells",
                    ),
                    (
                        "Recasting",
                        "If you cast the spell more than once before finishing a Long Rest, there is a cumulative 25 percent chance for each casting after the first that you get no answer",
                    ),
                )
            )
        ]


class DominateBeast(ClassSpell):
    rules = SpellRules(
        name="Dominate Beast",
        level=4,
        school=School.ENCHANTMENT,
        classes=(CharacterClass.DRUID, CharacterClass.RANGER, CharacterClass.SORCERER),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "One Beast you can see within range must succeed on a Wisdom saving throw or have the Charmed condition for the duration. The target has Advantage on the save if you or your allies are fighting it. Whenever the target takes damage, it repeats the save, ending the spell on itself on a success.\n"
            "You have a telepathic link with the Charmed target while the two of you are on the same plane of existence. On your turn, you can use this link to issue commands to the target (no action required), such as “Attack that creature,” “Move over there,” or “Fetch that object.” The target does its best to obey on its turn. If it completes an order and doesn’t receive further direction from you, it acts and moves as it likes, focusing on protecting itself.\n"
            "You can command the target to take a Reaction but must take your own Reaction to do so.\n"
            "Using a Higher-Level Spell Slot. Your Concentration can last longer with a spell slot of level 5 (up to 10 minutes), 6 (up to 1 hour), or 7+ (up to 8 hours)."
        ),
        usage_tags=("buff", "control"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "4fdeb48067877e1e")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You take control of a Beast."),
            Facts(
                (
                    ("Target", "One Beast you can see within range"),
                    (
                        "Save",
                        "Wisdom, with Advantage if you or your allies are fighting it",
                    ),
                    ("Failed save", "Charmed for the duration"),
                    (
                        "Repeat save",
                        "Whenever the target takes damage, it repeats the save, ending the spell on itself on a success",
                    ),
                )
            ),
            Option(
                "Control",
                (
                    Facts(
                        (
                            (
                                "Telepathic link",
                                "You have a telepathic link with the Charmed target while the two of you are on the same plane of existence",
                            ),
                            (
                                "Commands",
                                'On your turn, you can use this link to issue commands to the target (no action required), such as "Attack that creature," "Move over there," or "Fetch that object"',
                            ),
                            (
                                "Obeying",
                                "The target does its best to obey on its turn; if it completes an order and doesn't receive further direction from you, it acts and moves as it likes, focusing on protecting itself",
                            ),
                            (
                                "Reactions",
                                "You can command the target to take a Reaction but must take your own Reaction to do so",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (
                    Table(
                        ("Slot level", "Concentration lasts up to"),
                        (
                            ("4", "1 minute"),
                            ("5", "10 minutes"),
                            ("6", "1 hour"),
                            ("7+", "8 hours"),
                        ),
                    ),
                ),
            ),
        ]


class Doomtide(ClassSpell):
    rules = SpellRules(
        name="Doomtide",
        level=4,
        school=School.CONJURATION,
        classes=(CharacterClass.BARD, CharacterClass.CLERIC, CharacterClass.WARLOCK),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 120),
        components=Components(
            verbal=True, somatic=True, material="soot and a dried eel"
        ),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Forgotten Realms - Heroes of Faerun",
        description=(
            "You create a 20-foot-radius Sphere of inky fog within range. The fog is magical Darkness and lasts for the duration or until a strong wind (such as the one created by the Gust of Wind spell) disperses it, ending the spell.\n"
            "Each creature in the Sphere when it appears makes a Wisdom saving throw. On a failed save, a creature takes 5d6 Psychic damage and subtracts 1d6 from its saving throws until the end of its next turn. On a successful save, a creature takes half as much damage only. A creature also makes this save when the Sphere moves into its space, when it enters the Sphere, or when it ends its turn inside the Sphere. A creature makes this save only once per turn.\n"
            "The Sphere moves 10 feet away from you at the start of each of your turns.\n"
            "Casting as a Circle Spell. Casting this as a Circle spell requires a minimum of five secondary casters. In addition to the spell’s usual components, you must provide a special component (a string of three black pearls from Pandemonium), which the spell consumes. The spell’s range increases to 1 mile, and its duration increases to until dispelled (no Concentration required). The spell ends early if any caster who participated in this casting contributes to another casting of Doomtide as a Circle spell.\n"
            "When the spell is cast, each secondary caster must expend a level 3+ spell slot; otherwise, the spell fails."
        ),
        usage_tags=("buff", "control", "damage"),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "9d2026570d38e7d4")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You create a 20-foot-radius Sphere of inky fog within range.",
                    ),
                    ("Area", "20-foot-radius Sphere within range"),
                    (
                        "Darkness",
                        "The fog is magical Darkness and lasts for the duration, or until a strong wind (such as the one created by the Gust of Wind spell) disperses it, ending the spell",
                    ),
                    (
                        "Moving",
                        "The Sphere moves 10 feet away from you at the start of each of your turns",
                    ),
                    (
                        "Save",
                        "Wisdom, made by each creature in the Sphere when it appears, and by a creature when the Sphere moves into its space, when it enters the Sphere, or when it ends its turn inside the Sphere; a creature makes this save only once per turn",
                    ),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (
                    (
                        "5d6 Psychic damage, and it subtracts 1d6 from its saving throws until the end of its next turn",
                        "Half as much damage only",
                    ),
                ),
            ),
            Option(
                "Casting as a Circle Spell",
                (
                    Facts(
                        (
                            (
                                "Secondary casters",
                                "A minimum of five; when the spell is cast, each must expend a level 3+ spell slot, otherwise the spell fails",
                            ),
                            (
                                "Component",
                                "In addition to the spell's usual components, a string of three black pearls from Pandemonium, which the spell consumes",
                            ),
                            ("Range", "Increases to 1 mile"),
                            (
                                "Duration",
                                "Increases to until dispelled (no Concentration required)",
                            ),
                            (
                                "Ends early",
                                "If any caster who participated in this casting contributes to another casting of Doomtide as a Circle spell",
                            ),
                        )
                    ),
                ),
            ),
        ]


class ElementalBane(ClassSpell):
    rules = SpellRules(
        name="Elemental Bane",
        level=4,
        school=School.TRANSMUTATION,
        classes=(
            CharacterClass.DRUID,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
            CharacterClass.ARTIFICER,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 90),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Xanathar's Guide to Everything",
        description=(
            "Choose one creature you can see within range, and choose one of the following damage types: acid, cold, fire, lightning, or thunder. The target must succeed on a Constitution saving throw or be affected by the spell for its duration. The first time each turn the affected target takes damage of the chosen type, the target takes an extra 2d6 damage of that type. Moreover, the target loses any resistance to that damage type until the spell ends.\n"
            "At Higher Levels. When you cast this spell using a spell slot of 5th level or higher, you can target one additional creature for each slot level above 4th. The creatures must be within 30 feet of each other when you target them."
        ),
        usage_tags=("buff", "damage", "utility"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "14de32d762175af9")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Target", "One creature you can see within range"),
                    (
                        "Damage type",
                        "Acid, cold, fire, lightning, or thunder (your choice)",
                    ),
                    ("Save", "Constitution"),
                    ("Failed save", "Affected by the spell for its duration"),
                    (
                        "Extra damage",
                        "The first time each turn the affected target takes damage of the chosen type, it takes an extra 2d6 damage of that type",
                    ),
                    (
                        "Resistance",
                        "The target loses any resistance to that damage type until the spell ends",
                    ),
                )
            ),
            Option(
                "At Higher Levels",
                (
                    Facts(
                        (
                            ("Targets", "+1 creature for each slot level above 4th"),
                            (
                                "Spacing",
                                "The creatures must be within 30 feet of each other when you target them",
                            ),
                        )
                    ),
                ),
            ),
        ]


class EvardsBlackTentacles(ClassSpell):
    rules = SpellRules(
        name="Evard's Black Tentacles",
        level=4,
        school=School.CONJURATION,
        classes=(CharacterClass.WIZARD,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 90),
        components=Components(verbal=True, somatic=True, material="a tentacle"),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "Squirming, ebony tentacles fill a 20-foot square on ground that you can see within range. For the duration, these tentacles turn the ground in that area into Difficult Terrain.\n"
            "Each creature in that area makes a Strength saving throw. On a failed save, it takes 3d6 Bludgeoning damage, and it has the Restrained condition until the spell ends. A creature also makes that save if it enters the area or ends it turn there. A creature makes that save only once per turn.\n"
            "A Restrained creature can take an action to make a Strength (Athletics) check against your spell save DC, ending the condition on itself on a success."
        ),
        usage_tags=("control", "damage"),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "e37398b370b05b09")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "Squirming, ebony tentacles fill a 20-foot square on ground that you can see within range.",
                    ),
                    ("Area", "20-foot square on ground that you can see within range"),
                    (
                        "Terrain",
                        "For the duration, the tentacles turn the ground in the area into Difficult Terrain",
                    ),
                    (
                        "Save",
                        "Strength, made by each creature in the area, and by a creature that enters the area or ends its turn there; a creature makes that save only once per turn",
                    ),
                    (
                        "Failed save",
                        "3d6 Bludgeoning damage, and Restrained until the spell ends",
                    ),
                    ("Successful save", "No effect"),
                    (
                        "Escape",
                        "A Restrained creature can take an action to make a Strength (Athletics) check against your spell save DC, ending the condition on itself on a success",
                    ),
                )
            )
        ]


class Fabricate(ClassSpell):
    rules = SpellRules(
        name="Fabricate",
        level=4,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.ARTIFICER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.MINUTE, 10),
        range=Range(RangeType.FOOT, 120),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "You convert raw materials into products of the same material. For example, you can fabricate a wooden bridge from a clump of trees, a rope from a patch of hemp, or clothes from flax or wool.\n"
            "Choose raw materials that you can see within range. You can fabricate a Large or smaller object (contained within a 10-foot Cube or eight connected 5-foot Cubes) given a sufficient quantity of material. If you’re working with metal, stone, or another mineral substance, however, the fabricated object can be no larger than Medium (contained within a 5-foot Cube). The quality of any fabricated objects is based on the quality of the raw materials.\n"
            "Creatures and magic items can’t be created by this spell. You also can’t use it to create items that require a high degree of skill - such as weapons and armor - unless you have proficiency with the type of Artisan’s Tools used to craft such objects."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "faddbb672c946e00")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You convert raw materials that you can see within range into products of the same material."
            ),
            Facts(
                (
                    (
                        "Examples",
                        "A wooden bridge from a clump of trees, a rope from a patch of hemp, or clothes from flax or wool",
                    ),
                    (
                        "Size",
                        "A Large or smaller object (contained within a 10-foot Cube or eight connected 5-foot Cubes), given a sufficient quantity of material",
                    ),
                    (
                        "Mineral",
                        "If you're working with metal, stone, or another mineral substance, the object can be no larger than Medium (contained within a 5-foot Cube)",
                    ),
                    ("Quality", "Based on the quality of the raw materials"),
                    ("Can't create", "Creatures or magic items"),
                    (
                        "Skilled items",
                        "You can't create items that require a high degree of skill, such as weapons and armor, unless you have proficiency with the type of Artisan's Tools used to craft such objects",
                    ),
                )
            ),
        ]


class FesteringBlast(ClassSpell):
    rules = SpellRules(
        name="Festering Blast",
        level=4,
        school=School.NECROMANCY,
        classes=(
            CharacterClass.DRUID,
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 1),
        source="Arcana Unleashed",
        description=(
            "A 60-foot-long, 10-foot-wide Line of miasma blasts from you in a direction you choose. Each creature in the Line must make a Constitution saving throw. On a failed save, a target takes 4d10 Necrotic damage and has the Poisoned condition for the duration.\n"
            "A creature Poisoned by this spell takes 2d10 Poison damage at the start of each of its turns. At the end of each of its turns, a Poisoned target repeats the save, ending the spell on itself on a success.\n"
            "Using a Higher-Level Spell Slot. The initial damage increases by 1d10 for each spell slot level above 4."
        ),
        usage_tags=("control", "damage"),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "a57ee220612740c4")


class FindGreaterSteed(ClassSpell):
    rules = SpellRules(
        name="Find Greater Steed",
        level=4,
        school=School.CONJURATION,
        classes=(CharacterClass.PALADIN,),
        casting_time=CastingTime(CastingTimeType.MINUTE, 10),
        range=Range(RangeType.FOOT, 30),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Xanathar's Guide to Everything",
        description="You summon a spirit that assumes the form of a loyal, majestic mount. Appearing in an unoccupied space within range, the spirit takes on a form you choose: a griffon, a pegasus, a peryton, a dire wolf, a rhinoceros, or a saber-toothed tiger. The creature has the statistics provided in the Monster Manual for the chosen form, though it is a celestial, a fey, or a fiend (your choice) instead of its normal creature type. Additionally, if it has an Intelligence score of 5 or lower, its Intelligence becomes 6, and it gains the ability to understand one language of your choice that you speak. You control the mount in combat. While the mount is within 1 mile of you, you can communicate with it telepathically. While mounted on it, you can make any spell you cast that targets only you also target the mount. The mount disappears temporarily when it drops to 0 hit points or when you dismiss it as an action. Casting this spell again re-summons the bonded mount, with all its hit points restored and any conditions removed. You can't have more than one mount bonded by this spell or find steed at the same time. As an action, you can release a mount from its bond, causing it to disappear permanently. Whenever the mount disappears, it leaves behind any objects it was wearing or carrying.",
        usage_tags=("buff", "control", "heal", "utility", "summon"),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "ad953c053d2b4ff0")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You summon a spirit that assumes the form of a loyal, majestic mount.",
                    ),
                    ("Appears", "In an unoccupied space within range"),
                    (
                        "Forms",
                        "A griffon, a pegasus, a peryton, a dire wolf, a rhinoceros, or a saber-toothed tiger",
                    ),
                    (
                        "Statistics",
                        "Those provided in the Monster Manual for the chosen form, though it is a celestial, a fey, or a fiend (your choice) instead of its normal creature type",
                    ),
                    (
                        "Intelligence",
                        "If it has an Intelligence score of 5 or lower, its Intelligence becomes 6, and it gains the ability to understand one language of your choice that you speak",
                    ),
                    ("Control", "You control the mount in combat"),
                    (
                        "Telepathy",
                        "While the mount is within 1 mile of you, you can communicate with it telepathically",
                    ),
                    (
                        "Shared spells",
                        "While mounted on it, you can make any spell you cast that targets only you also target the mount",
                    ),
                    (
                        "One mount",
                        "You can't have more than one mount bonded by this spell or find steed at the same time",
                    ),
                )
            ),
            Option(
                "Disappearance",
                (
                    Facts(
                        (
                            (
                                "Temporarily",
                                "The mount disappears temporarily when it drops to 0 hit points or when you dismiss it as an action",
                            ),
                            (
                                "Re-summoning",
                                "Casting this spell again re-summons the bonded mount, with all its hit points restored and any conditions removed",
                            ),
                            (
                                "Releasing",
                                "As an action, you can release a mount from its bond, causing it to disappear permanently",
                            ),
                            (
                                "Its gear",
                                "Whenever the mount disappears, it leaves behind any objects it was wearing or carrying",
                            ),
                        )
                    ),
                ),
            ),
        ]


class FireShield(ClassSpell):
    rules = SpellRules(
        name="Fire Shield",
        level=4,
        school=School.EVOCATION,
        classes=(CharacterClass.DRUID, CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(
            verbal=True, somatic=True, material="a bit of phosphorus or a firefly"
        ),
        duration=Duration(DurationType.MINUTE, 10),
        source="Player's Handbook",
        description=(
            "Wispy flames wreathe your body for the duration, shedding Bright Light in a 10-foot radius and Dim Light for an additional 10 feet.\n"
            "The flames provide you with a warm shield or a chill shield, as you choose. The warm shield grants you Resistance to Cold damage, and the chill shield grants you Resistance to Fire damage.\n"
            "In addition, whenever a creature within 5 feet of you hits you with a melee attack roll, the shield erupts with flame. The attacker takes 2d8 Fire damage from a warm shield or 2d8 Cold damage from a chill shield."
        ),
        usage_tags=("buff", "damage"),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "3cd59034631a0589")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Flavor", "Wispy flames wreathe your body for the duration."),
                    (
                        "Light",
                        "Bright Light in a 10-foot radius and Dim Light for an additional 10 feet",
                    ),
                )
            ),
            Table(
                (
                    "Shield",
                    "Resistance",
                    "When a creature within 5 feet of you hits you with a melee attack roll",
                ),
                (
                    (
                        "Warm",
                        "Cold damage",
                        "The shield erupts with flame; the attacker takes 2d8 Fire damage",
                    ),
                    (
                        "Chill",
                        "Fire damage",
                        "The shield erupts with flame; the attacker takes 2d8 Cold damage",
                    ),
                ),
            ),
        ]


class FountOfMoonlight(ClassSpell):
    rules = SpellRules(
        name="Fount of Moonlight",
        level=4,
        school=School.EVOCATION,
        classes=(CharacterClass.BARD, CharacterClass.DRUID),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 10, concentration=True),
        source="Player's Handbook",
        description=(
            "A cool light wreathes your body for the duration, emitting Bright Light in a 20-foot radius and Dim Light for an additional 20 feet.\n"
            "Until the spell ends, you have Resistance to Radiant damage, and your melee attacks deal an extra 2d6 Radiant damage on a hit.\n"
            "In addition, immediately after you take damage from a creature you can see within 60 feet of yourself, you can take a Reaction to force the creature to make a Constitution saving throw. On a failed save, the creature has the Blinded condition until the end of your next turn."
        ),
        usage_tags=("buff", "control", "damage"),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "a41a0e93525b6ae5")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Flavor", "A cool light wreathes your body for the duration."),
                    (
                        "Light",
                        "Bright Light in a 20-foot radius and Dim Light for an additional 20 feet",
                    ),
                    (
                        "Resistance",
                        "Until the spell ends, you have Resistance to Radiant damage",
                    ),
                    (
                        "Melee attacks",
                        "Your melee attacks deal an extra 2d6 Radiant damage on a hit",
                    ),
                )
            ),
            Option(
                "Blinding Reaction",
                (
                    Facts(
                        (
                            (
                                "Trigger",
                                "Immediately after you take damage from a creature you can see within 60 feet of yourself",
                            ),
                            (
                                "Reaction",
                                "You can take a Reaction to force the creature to make a Constitution saving throw",
                            ),
                            ("Failed save", "Blinded until the end of your next turn"),
                        )
                    ),
                ),
            ),
        ]


class FreedomOfMovement(ClassSpell):
    rules = SpellRules(
        name="Freedom of Movement",
        level=4,
        school=School.ABJURATION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.BARD,
            CharacterClass.CLERIC,
            CharacterClass.DRUID,
            CharacterClass.RANGER,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.TOUCH),
        components=Components(verbal=True, somatic=True, material="a leather strap"),
        duration=Duration(DurationType.HOUR, 1),
        source="Player's Handbook",
        description=(
            "You touch a willing creature. For the duration, the target’s movement is unaffected by Difficult Terrain, and spells and other magical effects can neither reduce the target’s Speed nor cause the target to have the Paralyzed or Restrained conditions. The target also has a Swim Speed equal to its Speed.\n"
            "In addition, the target can spend 5 feet of movement to automatically escape from nonmagical restraints, such as manacles or a creature imposing the Grappled condition on it.\n"
            "Using a Higher-Level Spell Slot. You can target one additional creature for each spell slot level above 4."
        ),
        usage_tags=("buff", "control"),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "1627ee140c4a8ce8")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Target", "A willing creature you touch"),
                    (
                        "Terrain",
                        "The target's movement is unaffected by Difficult Terrain",
                    ),
                    (
                        "Magic",
                        "Spells and other magical effects can neither reduce the target's Speed nor cause it to have the Paralyzed or Restrained conditions",
                    ),
                    ("Swim Speed", "Equal to its Speed"),
                    (
                        "Escape",
                        "The target can spend 5 feet of movement to automatically escape from nonmagical restraints, such as manacles or a creature imposing the Grappled condition on it",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (
                    Facts(
                        (("Targets", "+1 creature for each spell slot level above 4"),)
                    ),
                ),
            ),
        ]


class GaldersSpeedyCourier(ClassSpell):
    rules = SpellRules(
        name="Galder's Speedy Courier",
        level=4,
        school=School.CONJURATION,
        classes=(CharacterClass.WARLOCK, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 10),
        components=Components(
            verbal=True,
            somatic=True,
            material="25 gold pieces, or mineral goods of equivalent value, which the spell consumes",
        ),
        duration=Duration(DurationType.MINUTE, 10),
        source="Lost Laboratory of Kwalish",
        description=(
            "You summon a Small air elemental to a spot within range. The air elemental is formless, nearly transparent, immune to all damage, and cannot interact with other creatures or objects. It carries an open, empty chest whose interior dimensions are 3 feet on each side. While the spell lasts, you can deposit as many items inside the chest as will fit. You can then name a living creature you have met and seen at least once before, or any creature for which you possess a body part, lock of hair, clipping from a nail, or similar portion of the creature's body.\n"
            "As soon as the lid of the chest is closed, the elemental and the chest disappear, then reappear adjacent to the target creature. If the target creature is on another plane, or if it is proofed against magical detection or location, the contents of the chest reappear on the ground at your feet.\n"
            "The target creature is made aware of the chest's contents before it chooses whether or not to open it, and knows how much of the spell's duration remains in which it can retrieve them. No other creature can open the chest and retrieve its contents. When the spell expires or when all the contents of the chest have been removed, the elemental and the chest disappear. The elemental also disappears if the target creature orders it to return the items to you. When the elemental disappears, any items not taken from the chest reappear on the ground at your feet.\n"
            "At Higher Levels. When you cast this spell using an 8th-level spell slot, you can send the chest to a creature on a different plane of existence from you."
        ),
        usage_tags=("control", "utility", "summon"),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "93b65a48e58d759a")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You summon a Small air elemental carrying a chest, which delivers its contents to a creature you name."
            ),
            Facts(
                (
                    (
                        "Elemental",
                        "It appears at a spot within range; it is formless, nearly transparent, immune to all damage, and can't interact with other creatures or objects",
                    ),
                    (
                        "Chest",
                        "Open and empty, with interior dimensions of 3 feet on each side; while the spell lasts, you can deposit as many items inside as will fit",
                    ),
                    (
                        "Recipient",
                        "A living creature you have met and seen at least once before, or any creature for which you possess a body part, lock of hair, clipping from a nail, or similar portion of its body",
                    ),
                )
            ),
            Option(
                "Delivery",
                (
                    Facts(
                        (
                            (
                                "Sending",
                                "As soon as the lid of the chest is closed, the elemental and the chest disappear, then reappear adjacent to the target creature",
                            ),
                            (
                                "Can't reach",
                                "If the target creature is on another plane, or if it is proofed against magical detection or location, the contents of the chest reappear on the ground at your feet",
                            ),
                            (
                                "Recipient knows",
                                "The target creature is made aware of the chest's contents before it chooses whether or not to open it, and knows how much of the spell's duration remains in which it can retrieve them",
                            ),
                            (
                                "Only the recipient",
                                "No other creature can open the chest and retrieve its contents",
                            ),
                            (
                                "Ends",
                                "When the spell expires or when all the contents of the chest have been removed, the elemental and the chest disappear; the elemental also disappears if the target creature orders it to return the items to you",
                            ),
                            (
                                "Leftovers",
                                "When the elemental disappears, any items not taken from the chest reappear on the ground at your feet",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "At Higher Levels",
                (
                    Facts(
                        (
                            (
                                "8th-level slot",
                                "You can send the chest to a creature on a different plane of existence from you",
                            ),
                        )
                    ),
                ),
            ),
        ]


class GiantInsect(ClassSpell):
    rules = SpellRules(
        name="Giant Insect",
        level=4,
        school=School.CONJURATION,
        classes=(CharacterClass.DRUID,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 10, concentration=True),
        source="Player's Handbook",
        description=(
            "You summon a giant centipede, spider, or wasp (chosen when you cast the spell). It manifests in an unoccupied space you can see within range and uses the Giant Insect stat block. The form you choose determines certain details in its stat block. The creature disappears when it drops to 0 Hit Points or when the spell ends.\n"
            "The creature is an ally to you and your allies. In combat, the creature shares your Initiative count, but it takes its turn immediately after yours. It obeys your verbal commands (no action required by you). If you don’t issue any, it takes the Dodge action and uses its movement to avoid danger.\n"
            "Using a Higher-Level Spell Slot. Use the spell slot’s level for the spell’s level in the stat block."
        ),
        usage_tags=("summon",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "f5b1133656a210b4")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You summon a giant centipede, spider, or wasp."),
            Facts(
                (
                    ("Appears", "In an unoccupied space you can see within range"),
                    (
                        "Form",
                        "Centipede, spider, or wasp, chosen when you cast the spell; the form determines certain details in its stat block",
                    ),
                    ("Stat block", "Giant Insect (below)"),
                    (
                        "Disappears",
                        "When it drops to 0 Hit Points or when the spell ends",
                    ),
                )
            ),
            Option(
                "Combat",
                (
                    Facts(
                        (
                            ("Allegiance", "An ally to you and your allies"),
                            (
                                "Initiative",
                                "It shares your Initiative count, but it takes its turn immediately after yours",
                            ),
                            (
                                "Commands",
                                "It obeys your verbal commands (no action required by you); if you don't issue any, it takes the Dodge action and uses its movement to avoid danger",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Giant Insect",
                (
                    Facts(
                        (
                            ("Type", "Large Beast"),
                            ("AC", "11 + the spell's level"),
                            ("Hit Points", "30 + 10 for each spell level above 4"),
                            ("Speed", "40 ft., Climb 40 ft., Fly 40 ft. (Wasp only)"),
                            (
                                "Abilities",
                                "Str 17, Dex 13, Con 15, Int 4, Wis 14, Cha 3",
                            ),
                            ("Senses", "Darkvision 60 ft., Passive Perception 12"),
                            ("Languages", "Understands the languages you know"),
                            (
                                "Spider Climb",
                                "The insect can climb difficult surfaces, including along ceilings, without needing to make an ability check",
                            ),
                            (
                                "Multiattack",
                                "The insect makes a number of attacks equal to half this spell's level (round down)",
                            ),
                            (
                                "Poison Jab",
                                "Melee Attack Roll: Bonus equals your spell attack modifier, reach 10 ft. Hit: 1d6 + 3 + the spell's level Piercing damage plus 1d4 Poison damage",
                            ),
                            (
                                "Web Bolt",
                                "Spider only. Ranged Attack Roll: Bonus equals your spell attack modifier, range 60 ft. Hit: 1d10 + 3 + the spell's level Bludgeoning damage, and the target's Speed is reduced to 0 until the start of the insect's next turn",
                            ),
                            (
                                "Venomous Spew",
                                "Bonus Action (Centipede only). Constitution saving throw against your spell save DC, one creature the insect can see within 10 feet. Failure: The target has the Poisoned condition until the start of the insect's next turn",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (
                    Facts(
                        (
                            (
                                "Stat block",
                                "Use the spell slot's level for the spell's level in the stat block",
                            ),
                        )
                    ),
                ),
            ),
        ]


class GraspingVine(ClassSpell):
    rules = SpellRules(
        name="Grasping Vine",
        level=4,
        school=School.CONJURATION,
        classes=(CharacterClass.DRUID, CharacterClass.RANGER),
        casting_time=CastingTime(CastingTimeType.BONUS_ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "You conjure a vine that sprouts from a surface in an unoccupied space that you can see within range. The vine lasts for the duration.\n"
            "Make a melee spell attack against a creature within 30 feet of the vine. On a hit, the target takes 4d8 Bludgeoning damage and is pulled up to 30 feet toward the vine; if the target is Huge or smaller, it has the Grappled condition (escape DC equal to your spell save DC). The vine can grapple only one creature at a time, and you can cause the vine to release a Grappled creature (no action required).\n"
            "As a Bonus Action on your later turns, you can repeat the attack against a creature within 30 feet of the vine.\n"
            "Using a Higher-Level Spell Slot. The number of creatures the vine can grapple increases by one for each spell slot level above 4."
        ),
        usage_tags=("control", "damage"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "7756a05c69ac4069")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You conjure a vine that sprouts from a surface in an unoccupied space that you can see within range; it lasts for the duration."
            ),
            Facts(
                (
                    (
                        "Attack",
                        "Melee spell attack against a creature within 30 feet of the vine",
                    ),
                    (
                        "On a hit",
                        "4d8 Bludgeoning damage, and the target is pulled up to 30 feet toward the vine",
                    ),
                    (
                        "Grappled",
                        "If the target is Huge or smaller, it has the Grappled condition (escape DC equal to your spell save DC)",
                    ),
                    ("Limit", "The vine can grapple only one creature at a time"),
                    (
                        "Release",
                        "You can cause the vine to release a Grappled creature (no action required)",
                    ),
                    (
                        "Later turns",
                        "As a Bonus Action on your later turns, you can repeat the attack against a creature within 30 feet of the vine",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (
                    Facts(
                        (
                            (
                                "Grapples",
                                "The number of creatures the vine can grapple increases by one for each spell slot level above 4",
                            ),
                        )
                    ),
                ),
            ),
        ]


class GreaterInvisibility(ClassSpell):
    rules = SpellRules(
        name="Greater Invisibility",
        level=4,
        school=School.ILLUSION,
        classes=(CharacterClass.BARD, CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.TOUCH),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description="A creature you touch has the Invisible condition until the spell ends.",
        usage_tags=("buff",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "d934fd335b7ab5c7")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("A creature you touch turns invisible."),
            Facts((("Effect", "The Invisible condition until the spell ends"),)),
        ]


class GuardianOfFaith(ClassSpell):
    rules = SpellRules(
        name="Guardian of Faith",
        level=4,
        school=School.CONJURATION,
        classes=(CharacterClass.CLERIC,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 30),
        components=Components(verbal=True),
        duration=Duration(DurationType.HOUR, 8),
        source="Player's Handbook",
        description=(
            "A Large spectral guardian appears and hovers for the duration in an unoccupied space that you can see within range. The guardian occupies that space and is invulnerable, and it appears in a form appropriate for your deity or pantheon.\n"
            "Any enemy that moves to a space within 10 feet of the guardian for the first time on a turn or starts its turn there makes a Dexterity saving throw, taking 20 Radiant damage on a failed save or half as much damage on a successful one. The guardian vanishes when it has dealt a total of 60 damage."
        ),
        usage_tags=("damage", "control"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "c10dd8ebfb53da62")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("A Large spectral guardian appears and hovers for the duration."),
            Facts(
                (
                    (
                        "Appears",
                        "In an unoccupied space that you can see within range, in a form appropriate for your deity or pantheon",
                    ),
                    ("Guardian", "It occupies that space and is invulnerable"),
                    (
                        "Save",
                        "Dexterity, made by any enemy that moves to a space within 10 feet of the guardian for the first time on a turn or starts its turn there",
                    ),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (("20 Radiant damage", "Half as much damage"),),
            ),
            Facts((("Vanishes", "When it has dealt a total of 60 damage"),)),
        ]


class GuardianOfNature(ClassSpell):
    rules = SpellRules(
        name="Guardian of Nature",
        level=4,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.DRUID, CharacterClass.RANGER),
        casting_time=CastingTime(CastingTimeType.BONUS_ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Xanathar's Guide to Everything",
        description=(
            "A nature spirit answers your call and transforms you into a powerful guardian. The transformation lasts until the spell ends. You choose one of the following forms to assume: Primal Beast or Great Tree.\n"
            "Primal Beast. Bestial fur covers your body, your facial features become feral, and you gain the following benefits:\n"
            "Your walking speed increases by 10 feet.\n"
            "You gain darkvision with a range of 120 feet.\n"
            "You make Strength-based attack rolls with advantage.\n"
            "Your melee weapon attacks deal an extra 1d6 force damage on a hit.\n"
            "Great Tree. Your skin appears barky, leaves sprout from your hair, and you gain the following benefits:\n"
            "You gain 10 temporary hit points.\n"
            "You make Constitution saving throws with advantage.\n"
            "You make Dexterity and Wisdom-based attack rolls with advantage.\n"
            "While you are on the ground, the ground within 15 feet of you is difficult terrain for your enemies."
        ),
        usage_tags=("buff", "control", "damage", "heal"),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "230d4c290d4a0994")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "A nature spirit answers your call and transforms you into a powerful guardian.",
                    ),
                )
            ),
            Paragraph(
                "The transformation lasts until the spell ends. Choose one of the forms below."
            ),
            Option(
                "Primal Beast",
                (
                    Facts(
                        (
                            (
                                "Appearance",
                                "Bestial fur covers your body, and your facial features become feral",
                            ),
                            ("Speed", "Your walking speed increases by 10 feet"),
                            (
                                "Darkvision",
                                "You gain darkvision with a range of 120 feet",
                            ),
                            (
                                "Strength attacks",
                                "You make Strength-based attack rolls with Advantage",
                            ),
                            (
                                "Melee",
                                "Your melee weapon attacks deal an extra 1d6 Force damage on a hit",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Great Tree",
                (
                    Facts(
                        (
                            (
                                "Appearance",
                                "Your skin appears barky, and leaves sprout from your hair",
                            ),
                            (
                                "Temporary hit points",
                                "You gain 10 temporary hit points",
                            ),
                            (
                                "Constitution saves",
                                "You make Constitution saving throws with Advantage",
                            ),
                            (
                                "Dex and Wis attacks",
                                "You make Dexterity and Wisdom-based attack rolls with Advantage",
                            ),
                            (
                                "Terrain",
                                "While you are on the ground, the ground within 15 feet of you is Difficult Terrain for your enemies",
                            ),
                        )
                    ),
                ),
            ),
        ]


class HallucinatoryTerrain(ClassSpell):
    rules = SpellRules(
        name="Hallucinatory Terrain",
        level=4,
        school=School.ILLUSION,
        classes=(
            CharacterClass.BARD,
            CharacterClass.DRUID,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.MINUTE, 10),
        range=Range(RangeType.FOOT, 300),
        components=Components(verbal=True, somatic=True, material="a mushroom"),
        duration=Duration(DurationType.HOUR, 24),
        source="Player's Handbook",
        description=(
            "You make natural terrain in a 150-foot Cube in range look, sound, and smell like another sort of natural terrain. Thus, open fields or a road can be made to resemble a swamp, hill, crevasse, or some other difficult or impassable terrain. A pond can be made to seem like a grassy meadow, a precipice like a gentle slope, or a rock-strewn gully like a wide and smooth road. Manufactured structures, equipment, and creatures within the area aren’t changed.\n"
            "The tactile characteristics of the terrain are unchanged, so creatures entering the area are likely to notice the illusion. If the difference isn’t obvious by touch, a creature examining the illusion can take the Study action to make an Intelligence (Investigation) check against your spell save DC to disbelieve it. If a creature discerns that the terrain is illusory, the creature sees a vague image superimposed on the real terrain."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "a8ae8dba6150d426")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You make natural terrain in a 150-foot Cube in range look, sound, and smell like another sort of natural terrain."
            ),
            Facts(
                (
                    (
                        "Examples",
                        "Open fields or a road can be made to resemble a swamp, hill, crevasse, or some other difficult or impassable terrain; a pond can seem like a grassy meadow, a precipice like a gentle slope, or a rock-strewn gully like a wide and smooth road",
                    ),
                    (
                        "Unchanged",
                        "Manufactured structures, equipment, and creatures within the area aren't changed",
                    ),
                    (
                        "Touch",
                        "The tactile characteristics of the terrain are unchanged, so creatures entering the area are likely to notice the illusion",
                    ),
                    (
                        "Disbelieving",
                        "If the difference isn't obvious by touch, a creature examining the illusion can take the Study action to make an Intelligence (Investigation) check against your spell save DC to disbelieve it",
                    ),
                    (
                        "Once discerned",
                        "A creature that discerns that the terrain is illusory sees a vague image superimposed on the real terrain",
                    ),
                )
            ),
        ]


class LeomundsSecretChest(ClassSpell):
    rules = SpellRules(
        name="Leomund's Secret Chest",
        level=4,
        school=School.CONJURATION,
        classes=(CharacterClass.ARTIFICER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.TOUCH),
        components=Components(
            verbal=True,
            somatic=True,
            material="a chest, 3 feet by 2 feet by 2 feet, constructed from rare materials worth 5,000+ GP, and a Tiny replica of the chest made from the same materials worth 50+ GP",
        ),
        duration=Duration(DurationType.UNTIL_DISPELLED),
        source="Player's Handbook",
        description=(
            "You hide a chest and all its contents on the Ethereal Plane. You must touch the chest and the miniature replica that serve as Material components for the spell. The chest can contain up to 12 cubic feet of nonliving material (3 feet by 2 feet by 2 feet).\n"
            "While the chest remains on the Ethereal Plane, you can take a Magic action and touch the replica to recall the chest. It appears in an unoccupied space on the ground within 5 feet of you. You can send the chest back to the Ethereal Plane by taking a Magic action to touch the chest and the replica.\n"
            "After 60 days, there is a cumulative 5 percent chance at the end of each day that the spell ends. The spell also ends if you cast this spell again or if the Tiny replica chest is destroyed. If the spell ends and the larger chest is on the Ethereal Plane, the chest remains there for you or someone else to find."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "4a4bff29623a61e0")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You hide a chest and all its contents on the Ethereal Plane."),
            Facts(
                (
                    (
                        "Components",
                        "You must touch the chest and the miniature replica that serve as Material components for the spell",
                    ),
                    (
                        "Capacity",
                        "Up to 12 cubic feet of nonliving material (3 feet by 2 feet by 2 feet)",
                    ),
                    (
                        "Recall",
                        "While the chest remains on the Ethereal Plane, you can take a Magic action and touch the replica to recall the chest; it appears in an unoccupied space on the ground within 5 feet of you",
                    ),
                    (
                        "Send back",
                        "You can send the chest back to the Ethereal Plane by taking a Magic action to touch the chest and the replica",
                    ),
                    (
                        "After 60 days",
                        "There is a cumulative 5 percent chance at the end of each day that the spell ends",
                    ),
                    (
                        "Ends early",
                        "If you cast this spell again or if the Tiny replica chest is destroyed",
                    ),
                    (
                        "Lost chest",
                        "If the spell ends and the larger chest is on the Ethereal Plane, the chest remains there for you or someone else to find",
                    ),
                )
            ),
        ]


class LocateCreature(ClassSpell):
    rules = SpellRules(
        name="Locate Creature",
        level=4,
        school=School.DIVINATION,
        classes=(
            CharacterClass.BARD,
            CharacterClass.CLERIC,
            CharacterClass.DRUID,
            CharacterClass.PALADIN,
            CharacterClass.RANGER,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(
            verbal=True, somatic=True, material="fur from a bloodhound"
        ),
        duration=Duration(DurationType.HOUR, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "Describe or name a creature that is familiar to you. You sense the direction to the creature’s location if that creature is within 1,000 feet of you. If the creature is moving, you know the direction of its movement.\n"
            "The spell can locate a specific creature known to you or the nearest creature of a specific kind (such as a human or a unicorn) if you have seen such a creature up close—within 30 feet—at least once. If the creature you described or named is in a different form, such as under the effects of a Flesh to Stone or Polymorph spell, this spell doesn’t locate the creature.\n"
            "This spell can’t locate a creature if any thickness of lead blocks a direct path between you and the creature."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "cfbbfced034fb329")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You sense the direction to a creature familiar to you."),
            Facts(
                (
                    ("Choose", "Describe or name a creature that is familiar to you"),
                    (
                        "You sense",
                        "The direction to the creature's location, if it is within 1,000 feet of you; if it is moving, you know the direction of its movement",
                    ),
                    (
                        "Requirement",
                        "The spell can locate a specific creature known to you, or the nearest creature of a specific kind (such as a human or a unicorn), if you have seen such a creature up close (within 30 feet) at least once",
                    ),
                    (
                        "Other forms",
                        "If the creature you described or named is in a different form, such as under the effects of a Flesh to Stone or Polymorph spell, this spell doesn't locate it",
                    ),
                    (
                        "Blocked by",
                        "Any thickness of lead blocking a direct path between you and the creature",
                    ),
                )
            ),
        ]


class MordenkainensFaithfulHound(ClassSpell):
    rules = SpellRules(
        name="Mordenkainen's Faithful Hound",
        level=4,
        school=School.CONJURATION,
        classes=(CharacterClass.ARTIFICER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 30),
        components=Components(verbal=True, somatic=True, material="a silver whistle"),
        duration=Duration(DurationType.HOUR, 8),
        source="Player's Handbook",
        description=(
            "You conjure a phantom watchdog in an unoccupied space that you can see within range. The hound remains for the duration or until the two of you are more than 300 feet apart from each other.\n"
            "No one but you can see the hound, and it is intangible and invulnerable. When a Small or larger creature comes within 30 feet of it without first speaking the password that you specify when you cast this spell, the hound starts barking loudly. The hound has Truesight with a range of 30 feet.\n"
            "At the start of each of your turns, the hound attempts to bite one enemy within 5 feet of it. That enemy must succeed on a Dexterity saving throw or take 4d8 Force damage.\n"
            "On your later turns, you can take a Magic action to move the hound up to 30 feet."
        ),
        usage_tags=("buff", "damage"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "c401cf3a81ff3af2")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You conjure a phantom watchdog in an unoccupied space that you can see within range."
            ),
            Facts(
                (
                    (
                        "Lasts",
                        "For the duration, or until the two of you are more than 300 feet apart from each other",
                    ),
                    (
                        "The hound",
                        "No one but you can see it, and it is intangible and invulnerable; it has Truesight with a range of 30 feet",
                    ),
                    (
                        "Alarm",
                        "When a Small or larger creature comes within 30 feet of it without first speaking the password that you specify when you cast this spell, the hound starts barking loudly",
                    ),
                    (
                        "Moving",
                        "On your later turns, you can take a Magic action to move the hound up to 30 feet",
                    ),
                )
            ),
            Option(
                "Bite",
                (
                    Facts(
                        (
                            (
                                "When",
                                "At the start of each of your turns, the hound attempts to bite one enemy within 5 feet of it",
                            ),
                            ("Save", "Dexterity"),
                            ("Failed save", "4d8 Force damage"),
                            ("Successful save", "No damage"),
                        )
                    ),
                ),
            ),
        ]


class MordenkainensPrivateSanctum(ClassSpell):
    rules = SpellRules(
        name="Mordenkainen's Private Sanctum",
        level=4,
        school=School.ABJURATION,
        classes=(CharacterClass.ARTIFICER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.MINUTE, 10),
        range=Range(RangeType.FOOT, 120),
        components=Components(
            verbal=True, somatic=True, material="a thin sheet of lead"
        ),
        duration=Duration(DurationType.HOUR, 24),
        source="Player's Handbook",
        description=(
            "You make an area within range magically secure. The area is a Cube that can be as small as 5 feet to as large as 100 feet on each side. The spell lasts for the duration.\n"
            "When you cast the spell, you decide what sort of security the spell provides, choosing any of the following properties:\n"
            "Sound can’t pass through the barrier at the edge of the warded area.\n"
            "The barrier of the warded area appears dark and foggy, preventing vision (including Darkvision) through it.\n"
            "Sensors created by Divination spells can’t appear inside the protected area or pass through the barrier at its perimeter.\n"
            "Creatures in the area can’t be targeted by Divination spells.\n"
            "Nothing can teleport into or out of the warded area.\n"
            "Planar travel is blocked within the warded area.\n"
            "Casting this spell on the same spot every day for 365 days makes the spell last until dispelled.\n"
            "Using a Higher-Level Spell Slot. You can increase the size of the Cube by 100 feet for each spell slot level above 4."
        ),
        usage_tags=("buff", "control"),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "1a5842f88533ce3f")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You make an area within range magically secure for the duration."
            ),
            Facts(
                (
                    (
                        "Area",
                        "A Cube that can be as small as 5 feet to as large as 100 feet on each side",
                    ),
                    (
                        "Security",
                        "When you cast the spell, you choose any of the properties below",
                    ),
                    (
                        "Permanent",
                        "Casting this spell on the same spot every day for 365 days makes the spell last until dispelled",
                    ),
                )
            ),
            Table(
                ("Property", "Effect"),
                (
                    (
                        "Sound",
                        "Sound can't pass through the barrier at the edge of the warded area",
                    ),
                    (
                        "Vision",
                        "The barrier appears dark and foggy, preventing vision (including Darkvision) through it",
                    ),
                    (
                        "Scrying sensors",
                        "Sensors created by Divination spells can't appear inside the protected area or pass through the barrier at its perimeter",
                    ),
                    (
                        "Divination",
                        "Creatures in the area can't be targeted by Divination spells",
                    ),
                    (
                        "Teleportation",
                        "Nothing can teleport into or out of the warded area",
                    ),
                    (
                        "Planar travel",
                        "Planar travel is blocked within the warded area",
                    ),
                ),
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (
                    Facts(
                        (
                            (
                                "Cube size",
                                "You can increase the size of the Cube by 100 feet for each spell slot level above 4",
                            ),
                        )
                    ),
                ),
            ),
        ]


class OtilukesResilientSphere(ClassSpell):
    rules = SpellRules(
        name="Otiluke's Resilient Sphere",
        level=4,
        school=School.ABJURATION,
        classes=(CharacterClass.ARTIFICER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 30),
        components=Components(verbal=True, somatic=True, material="a glass sphere"),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "A shimmering sphere encloses a Large or smaller creature or object within range. An unwilling creature must succeed on a Dexterity saving throw or be enclosed for the duration.\n"
            "Nothing—not physical objects, energy, or other spell effects—can pass through the barrier, in or out, though a creature in the sphere can breathe there. The sphere is immune to all damage, and a creature or object inside can’t be damaged by attacks or effects originating from outside, nor can a creature inside the sphere damage anything outside it.\n"
            "The sphere is weightless and just large enough to contain the creature or object inside. An enclosed creature can take an action to push against the sphere’s walls and thus roll the sphere at up to half the creature’s Speed. Similarly, the globe can be picked up and moved by other creatures.\n"
            "A Disintegrate spell targeting the globe destroys it without harming anything inside."
        ),
        usage_tags=("buff", "control"),
        target=FeatureTarget.CREATURE,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "34e751ccf0036ae4")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "A shimmering sphere encloses a Large or smaller creature or object within range."
            ),
            Facts(
                (
                    (
                        "Unwilling",
                        "An unwilling creature must succeed on a Dexterity saving throw or be enclosed for the duration",
                    ),
                    (
                        "Barrier",
                        "Nothing (not physical objects, energy, or other spell effects) can pass through the barrier, in or out, though a creature in the sphere can breathe there",
                    ),
                    (
                        "Damage",
                        "The sphere is immune to all damage; a creature or object inside can't be damaged by attacks or effects originating from outside, nor can a creature inside the sphere damage anything outside it",
                    ),
                    (
                        "Size",
                        "Weightless and just large enough to contain the creature or object inside",
                    ),
                    (
                        "Rolling",
                        "An enclosed creature can take an action to push against the sphere's walls and thus roll the sphere at up to half the creature's Speed",
                    ),
                    (
                        "Carrying",
                        "The globe can be picked up and moved by other creatures",
                    ),
                    (
                        "Disintegrate",
                        "A Disintegrate spell targeting the globe destroys it without harming anything inside",
                    ),
                )
            ),
        ]


class PhantasmalKiller(ClassSpell):
    rules = SpellRules(
        name="Phantasmal Killer",
        level=4,
        school=School.ILLUSION,
        classes=(CharacterClass.BARD, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 120),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "You tap into the nightmares of a creature you can see within range and create an illusion of its deepest fears, visible only to that creature. The target makes a Wisdom saving throw. On a failed save, the target takes 4d10 Psychic damage and has Disadvantage on ability checks and attack rolls for the duration. On a successful save, the target takes half as much damage, and the spell ends.\n"
            "For the duration, the target makes a Wisdom saving throw at the end of each of its turns. On a failed save, it takes the Psychic damage again. On a successful save, the spell ends.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 1d10 for each spell slot level above 4."
        ),
        usage_tags=("control", "damage"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "ef70ab0d40ac7973")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You tap into the nightmares of a creature you can see within range and create an illusion of its deepest fears, visible only to that creature.",
                    ),
                    ("Target", "A creature you can see within range"),
                    ("Save", "Wisdom"),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (
                    (
                        "4d10 Psychic damage, and Disadvantage on ability checks and attack rolls for the duration",
                        "Half as much damage, and the spell ends",
                    ),
                ),
            ),
            Facts(
                (
                    (
                        "Each turn",
                        "For the duration, the target makes a Wisdom saving throw at the end of each of its turns; on a failed save, it takes the Psychic damage again, and on a successful save, the spell ends",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Damage", "+1d10 for each spell slot level above 4"),)),),
            ),
        ]


class Polymorph(ClassSpell):
    rules = SpellRules(
        name="Polymorph",
        level=4,
        school=School.TRANSMUTATION,
        classes=(
            CharacterClass.BARD,
            CharacterClass.DRUID,
            CharacterClass.SORCERER,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(
            verbal=True, somatic=True, material="a caterpillar cocoon"
        ),
        duration=Duration(DurationType.HOUR, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "You attempt to transform a creature that you can see within range into a Beast. The target must succeed on a Wisdom saving throw or shape-shift into a Beast form for the duration. That form can be any Beast you choose that has a Challenge Rating equal to or less than the target's (or the target's level if it doesn't have a Challenge Rating). The target's game statistics are replaced by the stat block of the chosen Beast, but the target retains its alignment, personality, creature type, Hit Points, and Hit Point Dice. See appendix B for a sample of Beast stat blocks.\n"
            "The target gains a number of Temporary Hit Points equal to the Hit Points of the Beast form. These Temporary Hit Points vanish if any remain when the spell ends. The spell ends early on the target if it has no Temporary Hit Points left. The target is limited in the actions it can perform by the anatomy of its new form, and it can’t speak or cast spells.\n"
            "The target's gear melds into the new form. The creature can't use or otherwise benefit from any of that equipment."
        ),
        usage_tags=("heal",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "92d62771d3155d15")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You attempt to transform a creature that you can see within range into a Beast."
            ),
            Facts(
                (
                    ("Save", "Wisdom"),
                    (
                        "Failed save",
                        "The target shape-shifts into a Beast form for the duration",
                    ),
                    (
                        "Form",
                        "Any Beast you choose that has a Challenge Rating equal to or less than the target's (or the target's level if it doesn't have a Challenge Rating); see appendix B for a sample of Beast stat blocks",
                    ),
                    (
                        "Statistics",
                        "Replaced by the stat block of the chosen Beast, but the target retains its alignment, personality, creature type, Hit Points, and Hit Point Dice",
                    ),
                    (
                        "Temporary Hit Points",
                        "The target gains a number equal to the Hit Points of the Beast form; any that remain vanish when the spell ends",
                    ),
                    (
                        "Ends early",
                        "On the target if it has no Temporary Hit Points left",
                    ),
                    (
                        "Limits",
                        "The target is limited in the actions it can perform by the anatomy of its new form, and it can't speak or cast spells",
                    ),
                    (
                        "Gear",
                        "The target's gear melds into the new form; the creature can't use or otherwise benefit from any of that equipment",
                    ),
                )
            ),
        ]


class RaulothimsPsychicLance(ClassSpell):
    rules = SpellRules(
        name="Raulothim's Psychic Lance",
        level=4,
        school=School.ENCHANTMENT,
        classes=(
            CharacterClass.BARD,
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 120),
        components=Components(verbal=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Fizban's Treasury of Dragons",
        description=(
            "You unleash a shimmering lance of psychic power from your forehead at a creature that you can see within range. Alternatively, you can utter a creature's name. If the named target is within range, it becomes the spell's target even if you can't see it. If the named target isn't within range, the lance dissipates without effect.\n"
            "The target must make an Intelligence saving throw. On a failed save, the target takes 7d6 psychic damage and is incapacitated until the start of your next turn. On a successful save, the creature takes half as much damage and isn't incapacitated.\n"
            "At Higher Levels. When you cast this spell using a spell slot of 5th level or higher, the damage increases by 1d6 for each slot level above 4th."
        ),
        usage_tags=("damage", "utility"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "a2818a45cae4b4b8")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You unleash a shimmering lance of psychic power from your forehead at a creature that you can see within range.",
                    ),
                    ("Target", "A creature that you can see within range"),
                    (
                        "By name",
                        "Alternatively, you can utter a creature's name; if the named target is within range, it becomes the spell's target even if you can't see it, and if it isn't within range, the lance dissipates without effect",
                    ),
                    ("Save", "Intelligence"),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (
                    (
                        "7d6 Psychic damage, and incapacitated until the start of your next turn",
                        "Half as much damage, and not incapacitated",
                    ),
                ),
            ),
            Option(
                "At Higher Levels",
                (Facts((("Damage", "+1d6 for each slot level above 4th"),)),),
            ),
        ]


class ShadowOfMoil(ClassSpell):
    rules = SpellRules(
        name="Shadow of Moil",
        level=4,
        school=School.NECROMANCY,
        classes=(CharacterClass.WARLOCK,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(
            verbal=True,
            somatic=True,
            material="an undead eyeball encased in a gem worth at least 150 gp",
        ),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Xanathar's Guide to Everything",
        description=(
            "Flame-like shadows wreathe your body until the spell ends, causing you to become heavily obscured to others. The shadows turn dim light within 10 feet of you into darkness, and bright light in the same area to dim light.\n"
            "Until the spell ends, you have resistance to radiant damage. In addition, whenever a creature within 10 feet of you hits you with an attack, the shadows lash out at that creature, dealing it 2d8 necrotic damage."
        ),
        usage_tags=("buff", "damage"),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "99e299beed2df2e4")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "Flame-like shadows wreathe your body until the spell ends.",
                    ),
                    ("Obscured", "You are heavily obscured to others"),
                    (
                        "Light",
                        "The shadows turn dim light within 10 feet of you into darkness, and bright light in the same area to dim light",
                    ),
                    (
                        "Resistance",
                        "Until the spell ends, you have resistance to Radiant damage",
                    ),
                    (
                        "Lashing",
                        "Whenever a creature within 10 feet of you hits you with an attack, the shadows lash out at that creature, dealing it 2d8 Necrotic damage",
                    ),
                )
            )
        ]


class SickeningRadiance(ClassSpell):
    rules = SpellRules(
        name="Sickening Radiance",
        level=4,
        school=School.EVOCATION,
        classes=(
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 120),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 10, concentration=True),
        source="Xanathar's Guide to Everything",
        description=(
            "Dim, greenish light spreads within a 30-foot-radius sphere centered on a point you choose within range. The light spreads around corners, and it lasts until the spell ends.\n"
            "When a creature moves into the spell's area for the first time on a turn or starts its turn there, that creature must succeed on a Constitution saving throw or take 4d10 radiant damage, and it suffers one level of exhaustion and emits a dim, greenish light in a 5-foot radius. This light makes it impossible for the creature to benefit from being invisible. The light and any levels of exhaustion caused by this spell go away when the spell ends."
        ),
        usage_tags=("control", "damage"),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "dd413a59dc27fcef")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "Dim, greenish light spreads within a 30-foot-radius sphere centered on a point you choose within range.",
                    ),
                    (
                        "Area",
                        "30-foot-radius sphere centered on a point you choose within range; the light spreads around corners and lasts until the spell ends",
                    ),
                    (
                        "Save",
                        "Constitution, when a creature moves into the spell's area for the first time on a turn or starts its turn there",
                    ),
                    (
                        "Failed save",
                        "4d10 Radiant damage; the creature suffers one level of exhaustion and emits a dim, greenish light in a 5-foot radius",
                    ),
                    ("Successful save", "No effect"),
                    (
                        "Glowing",
                        "This light makes it impossible for the creature to benefit from being invisible",
                    ),
                    (
                        "Spell ends",
                        "The light and any levels of exhaustion caused by this spell go away",
                    ),
                )
            )
        ]


class SpellfireStorm(ClassSpell):
    rules = SpellRules(
        name="Spellfire Storm",
        level=4,
        school=School.EVOCATION,
        classes=(CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Forgotten Realms - Heroes of Faerun",
        description=(
            "You conjure a pillar of spellfire in a 20-foot-radius, 20-foot-high Cylinder centered on a point within range. The area of the Cylinder is Bright Light, and each creature in it when it appears makes a Constitution saving throw, taking 4d10 Radiant damage on a failed save or half as much damage on a successful one. A creature also makes this save when it enters the spell’s area for the first time on a turn or ends its turn there. A creature makes this save only once per turn.\n"
            "In addition, whenever a creature in the Cylinder casts a spell, that creature makes a Constitution saving throw. On a failed save, the spell dissipates with no effect, and the action, Bonus Action, or Reaction used to cast it is wasted. If that spell was cast with a spell slot, the slot isn’t expended.\n"
            "When you cast this spell, you can designate creatures to be unaffected by it.\n"
            "Casting as a Circle Spell. In addition to the spell’s usual components, you must provide a special component (a blue star sapphire worth 25,000+ GP), which the spell consumes. The spell’s range increases to 1 mile, and it no longer requires Concentration. When the spell is cast, each secondary caster must expend a level 3+ spell slot; otherwise, the spell fails.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 1d10 for every spell slot level above 4.\n"
            "The number of secondary casters determines the spell’s area of effect and duration, as shown in the table below. The spell ends early if any caster who participated in this casting contributes to another casting of Spellfire Storm as a Circle spell."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "45e3a14b646a3289")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You conjure a pillar of spellfire in a 20-foot-radius, 20-foot-high Cylinder centered on a point within range."
            ),
            Facts(
                (
                    ("Light", "The area of the Cylinder is Bright Light"),
                    (
                        "Unaffected",
                        "When you cast this spell, you can designate creatures to be unaffected by it",
                    ),
                    (
                        "Save",
                        "Constitution, made by each creature in it when it appears, and by a creature when it enters the spell's area for the first time on a turn or ends its turn there; a creature makes this save only once per turn",
                    ),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (("4d10 Radiant damage", "Half as much damage"),),
            ),
            Option(
                "Spellcasting in the Cylinder",
                (
                    Facts(
                        (
                            (
                                "Trigger",
                                "Whenever a creature in the Cylinder casts a spell, that creature makes a Constitution saving throw",
                            ),
                            (
                                "Failed save",
                                "The spell dissipates with no effect, and the action, Bonus Action, or Reaction used to cast it is wasted",
                            ),
                            (
                                "Spell slot",
                                "If that spell was cast with a spell slot, the slot isn't expended",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Casting as a Circle Spell",
                (
                    Facts(
                        (
                            (
                                "Component",
                                "In addition to the spell's usual components, a blue star sapphire worth 25,000+ GP, which the spell consumes",
                            ),
                            ("Range", "Increases to 1 mile"),
                            ("Concentration", "No longer required"),
                            (
                                "Secondary casters",
                                "When the spell is cast, each must expend a level 3+ spell slot, otherwise the spell fails",
                            ),
                            (
                                "Area and duration",
                                "Determined by the number of secondary casters, as shown in a table that isn't included in this spell's data",
                            ),
                            (
                                "Ends early",
                                "If any caster who participated in this casting contributes to another casting of Spellfire Storm as a Circle spell",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Damage", "+1d10 for every spell slot level above 4"),)),),
            ),
        ]


class SpiritOfDeath(ClassSpell):
    rules = SpellRules(
        name="Spirit of Death",
        level=4,
        school=School.NECROMANCY,
        classes=(
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(
            verbal=True,
            somatic=True,
            material="a gilded playing card worth at least 400 gp and depicting an avatar of death",
        ),
        duration=Duration(DurationType.HOUR, 1, concentration=True),
        source="The Book of Many Things",
        description=(
            "You call forth a spirit that embodies death. The spirit manifests in an unoccupied space you can see within range and uses the reaper spirit stat block. The spirit disappears when it is reduced to 0 hit points or when the spell ends.\n"
            "The spirit is an ally to you and your companions. In combat, the spirit shares your initiative count and takes its turn immediately after yours. It obeys your verbal commands (no action required by you). If you don't issue the spirit any commands, it takes the Dodge action and uses its movement to avoid danger.\n"
            "At Higher Levels. When you cast this spell using a spell slot of 5th level or higher, use the higher level wherever the spell's level appears in the reaper spirit stat block."
        ),
        usage_tags=("utility", "summon"),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "6eb0c4c0a46531d6")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Flavor", "You call forth a spirit that embodies death."),
                    ("Appears", "In an unoccupied space you can see within range"),
                    ("Stat block", "Reaper spirit (not included in this spell's data)"),
                    (
                        "Disappears",
                        "When it is reduced to 0 hit points or when the spell ends",
                    ),
                )
            ),
            Option(
                "Combat",
                (
                    Facts(
                        (
                            ("Allegiance", "An ally to you and your companions"),
                            (
                                "Initiative",
                                "It shares your initiative count and takes its turn immediately after yours",
                            ),
                            (
                                "Commands",
                                "It obeys your verbal commands (no action required by you); if you don't issue it any commands, it takes the Dodge action and uses its movement to avoid danger",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "At Higher Levels",
                (
                    Facts(
                        (
                            (
                                "Stat block",
                                "Use the higher level wherever the spell's level appears in the reaper spirit stat block",
                            ),
                        )
                    ),
                ),
            ),
        ]


class StaggeringSmite(ClassSpell):
    rules = SpellRules(
        name="Staggering Smite",
        level=4,
        school=School.ENCHANTMENT,
        classes=(CharacterClass.PALADIN,),
        casting_time=CastingTime(
            CastingTimeType.BONUS_ACTION,
            trigger="which you take immediately after hitting a creature with a Melee weapon or an Unarmed Strike",
        ),
        range=Range(RangeType.SELF),
        components=Components(verbal=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "The target takes an extra 4d6 Psychic damage from the attack, and the target must succeed on a Wisdom saving throw or have the Stunned condition until the end of your next turn.\n"
            "Using a Higher-Level Spell Slot. The extra damage increases by 1d6 for each spell slot level above 4."
        ),
        usage_tags=("control", "damage"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "63785625aba07762")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Trigger",
                        "Immediately after you hit a creature with a Melee weapon or an Unarmed Strike",
                    ),
                    (
                        "Damage",
                        "The target takes an extra 4d6 Psychic damage from the attack",
                    ),
                    ("Save", "Wisdom"),
                    ("Failed save", "Stunned until the end of your next turn"),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Extra damage", "+1d6 for each spell slot level above 4"),)),),
            ),
        ]


class SticksToSnakes(ClassSpell):
    rules = SpellRules(
        name="Sticks to Snakes",
        level=4,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.CLERIC, CharacterClass.DRUID, CharacterClass.RANGER),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 90),
        components=Components(
            verbal=True,
            somatic=True,
            material="a small piece of bark and several snake scales",
        ),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="D&D Beyond Drops - May 2026",
        description=(
            "You can choose up to four nonmagical sticks no longer than a Quarterstaff (or similar pieces of nonmagical wood, such as Torches, Spears, etc.) that you can see within range to shape-shift into snakes. Creatures that are holding a targeted object can make a Charisma saving throw, preventing the target from shape-shifting on a success. Each shape-shifted target uses the Venomous Snake stat block.\n"
            "Each of these snakes is Friendly to you and your allies. In combat, it shares your Initiative count and takes its turn immediately after yours.\n"
            "Until the spell ends, you can take a Bonus Action to mentally command any creature you made with this spell if the creature is within 500 feet of you (if you control multiple creatures, you can command any of them at the same time, issuing the same command to each one). If you issue no commands, the creature takes the Dodge action and moves only to avoid harm. When the creature drops to 0 Hit Points, it reverts to its object form, and any remaining damage carries over to that form.\n"
            "Using a Higher-Level Spell Slot. You can target two additional objects for each spell slot level above 4."
        ),
        usage_tags=("summon",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "2ba28f4ea75eadb7")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Missing text",
                        "The opening of this spell's text (which objects become snakes, and their statistics) isn't included in this spell's data",
                    ),
                    (
                        "Allegiance",
                        "Each of these snakes is Friendly to you and your allies",
                    ),
                    (
                        "Initiative",
                        "In combat, it shares your Initiative count and takes its turn immediately after yours",
                    ),
                    (
                        "Commands",
                        "Until the spell ends, you can take a Bonus Action to mentally command any creature you made with this spell if the creature is within 500 feet of you; if you control multiple creatures, you can command any of them at the same time, issuing the same command to each one",
                    ),
                    (
                        "No command",
                        "The creature takes the Dodge action and moves only to avoid harm",
                    ),
                    (
                        "0 Hit Points",
                        "It reverts to its object form, and any remaining damage carries over to that form",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (
                    Facts(
                        (
                            (
                                "Objects",
                                "You can target two additional objects for each spell slot level above 4",
                            ),
                        )
                    ),
                ),
            ),
        ]


class StoneShape(ClassSpell):
    rules = SpellRules(
        name="Stone Shape",
        level=4,
        school=School.TRANSMUTATION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.CLERIC,
            CharacterClass.DRUID,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.TOUCH),
        components=Components(verbal=True, somatic=True, material="soft clay"),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description="You touch a stone object of Medium size or smaller or a section of stone no more than 5 feet in any dimension and form it into any shape you like. For example, you could shape a large rock into a weapon, statue, or coffer, or you could make a small passage through a wall that is 5 feet thick. You could also shape a stone door or its frame to seal the door shut. The object you create can have up to two hinges and a latch, but finer mechanical detail isn’t possible.",
        usage_tags=("utility",),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "d404e9a5ca77396d")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You touch stone and form it into any shape you like."),
            Facts(
                (
                    (
                        "Target",
                        "A stone object of Medium size or smaller, or a section of stone no more than 5 feet in any dimension",
                    ),
                    (
                        "Examples",
                        "Shape a large rock into a weapon, statue, or coffer; make a small passage through a wall that is 5 feet thick; or shape a stone door or its frame to seal the door shut",
                    ),
                    (
                        "Detail",
                        "The object you create can have up to two hinges and a latch, but finer mechanical detail isn't possible",
                    ),
                )
            ),
        ]


class Stoneskin(ClassSpell):
    rules = SpellRules(
        name="Stoneskin",
        level=4,
        school=School.TRANSMUTATION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.DRUID,
            CharacterClass.RANGER,
            CharacterClass.SORCERER,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.TOUCH),
        components=Components(
            verbal=True,
            somatic=True,
            material="diamond dust worth 100+ GP, which the spell consumes",
        ),
        duration=Duration(DurationType.HOUR, 1, concentration=True),
        source="Player's Handbook",
        description="Until the spell ends, one willing creature you touch has Resistance to Bludgeoning, Piercing, and Slashing damage.",
        usage_tags=("buff",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "6a3424b5d5d8b245")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Target", "One willing creature you touch"),
                    (
                        "Effect",
                        "Until the spell ends, Resistance to Bludgeoning, Piercing, and Slashing damage",
                    ),
                )
            )
        ]


class StormSphere(ClassSpell):
    rules = SpellRules(
        name="Storm Sphere",
        level=4,
        school=School.EVOCATION,
        classes=(CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 150),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Xanathar's Guide to Everything",
        description=(
            "A 20-foot-radius sphere of whirling air springs into existence centered on a point you choose within range. The sphere remains for the spell's duration. Each creature in the sphere when it appears or that ends its turn there must succeed on a Strength saving throw or take 2d6 bludgeoning damage. The sphere's space is difficult terrain.\n"
            "Until the spell ends, you can use a bonus action on each of your turns to cause a bolt of lightning to leap from the center of the sphere toward one creature you choose within 60 feet of the center. Make a ranged spell attack. You have advantage on the attack roll if the target is in the sphere. On a hit, the target takes 4d6 lightning damage.\n"
            "Creatures within 30 feet of the sphere have disadvantage on Wisdom (Perception) checks made to listen.\n"
            "At Higher Levels. When you cast this spell using a spell slot of 5th level or higher, the damage increases for each of its effects by 1d6 for each slot level above 4th."
        ),
        usage_tags=("buff", "control", "damage"),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "a21c2257957051ae")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "A 20-foot-radius sphere of whirling air springs into existence centered on a point you choose within range, and remains for the spell's duration."
            ),
            Facts(
                (
                    ("Terrain", "The sphere's space is Difficult Terrain"),
                    (
                        "Save",
                        "Strength, made by each creature in the sphere when it appears or that ends its turn there",
                    ),
                    ("Failed save", "2d6 Bludgeoning damage"),
                    ("Successful save", "No damage"),
                    (
                        "Hearing",
                        "Creatures within 30 feet of the sphere have Disadvantage on Wisdom (Perception) checks made to listen",
                    ),
                )
            ),
            Option(
                "Lightning Bolt",
                (
                    Facts(
                        (
                            (
                                "Action",
                                "Until the spell ends, you can use a bonus action on each of your turns to cause a bolt of lightning to leap from the center of the sphere toward one creature you choose within 60 feet of the center",
                            ),
                            (
                                "Attack",
                                "Ranged spell attack, with Advantage if the target is in the sphere",
                            ),
                            ("On a hit", "4d6 Lightning damage"),
                        )
                    ),
                ),
            ),
            Option(
                "At Higher Levels",
                (
                    Facts(
                        (
                            (
                                "Damage",
                                "The damage for each of its effects increases by 1d6 for each slot level above 4th",
                            ),
                        )
                    ),
                ),
            ),
        ]


class SummonAberration(ClassSpell):
    rules = SpellRules(
        name="Summon Aberration",
        level=4,
        school=School.CONJURATION,
        classes=(CharacterClass.WARLOCK, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 90),
        components=Components(
            verbal=True,
            somatic=True,
            material="a pickled tentacle and an eyeball in a platinum-inlaid vial worth 400+ GP",
        ),
        duration=Duration(DurationType.HOUR, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "You call forth an aberrant spirit. It manifests in an unoccupied space that you can see within range and uses the Aberrant Spirit stat block. When you cast the spell, choose Beholderkin, Mind Flayer, or Slaad. The creature resembles an Aberration of that kind, which determines certain details in its stat block. The creature disappears when it drops to 0 Hit Points or when the spell ends.\n"
            "The creature is an ally to you and your allies. In combat, it shares your Initiative count, but it takes its turn immediately after yours. It obeys your verbal commands (no action required by you). If you don’t issue any, it takes the Dodge action and uses its movement to avoid danger.\n"
            "Using a Higher-Level Spell Slot. Use the spell slot’s level for the spell’s level in the stat block."
        ),
        usage_tags=("summon",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "382702cafa0f8ba7")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You call forth an aberrant spirit."),
            Facts(
                (
                    ("Appears", "In an unoccupied space that you can see within range"),
                    (
                        "Kind",
                        "Beholderkin, Mind Flayer, or Slaad, chosen when you cast the spell; the creature resembles an Aberration of that kind, which determines certain details in its stat block",
                    ),
                    ("Stat block", "Aberrant Spirit (below)"),
                    (
                        "Disappears",
                        "When it drops to 0 Hit Points or when the spell ends",
                    ),
                )
            ),
            Option(
                "Combat",
                (
                    Facts(
                        (
                            ("Allegiance", "An ally to you and your allies"),
                            (
                                "Initiative",
                                "It shares your Initiative count, but it takes its turn immediately after yours",
                            ),
                            (
                                "Commands",
                                "It obeys your verbal commands (no action required by you); if you don't issue any, it takes the Dodge action and uses its movement to avoid danger",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Aberrant Spirit",
                (
                    Facts(
                        (
                            ("Type", "Medium Aberration"),
                            ("AC", "11 + the spell's level"),
                            ("Hit Points", "40 + 10 for each spell level above 4"),
                            ("Speed", "30 ft., Fly 30 ft. (hover; Beholderkin only)"),
                            (
                                "Abilities",
                                "Str 16, Dex 10, Con 15, Int 16, Wis 10, Cha 6",
                            ),
                            ("Immunities", "Psychic"),
                            ("Senses", "Darkvision 60 ft., Passive Perception 10"),
                            (
                                "Languages",
                                "Deep Speech, understands the languages you know",
                            ),
                            (
                                "Regeneration",
                                "Slaad only. The spirit regains 5 Hit Points at the start of its turn if it has at least 1 Hit Point",
                            ),
                            (
                                "Whispering Aura",
                                "Mind Flayer only. At the start of each of the spirit's turns, the spirit emits psionic energy if it doesn't have the Incapacitated condition. Wisdom saving throw against your spell save DC, each creature (other than you) within 5 feet of the spirit. Failure: 2d6 Psychic damage",
                            ),
                            (
                                "Multiattack",
                                "The spirit makes a number of attacks equal to half this spell's level (round down)",
                            ),
                            (
                                "Claw",
                                "Slaad only. Melee Attack Roll: Bonus equals your spell attack modifier, reach 5 ft. Hit: 1d10 + 3 + the spell's level Slashing damage, and the target can't regain Hit Points until the start of the spirit's next turn",
                            ),
                            (
                                "Eye Ray",
                                "Beholderkin only. Ranged Attack Roll: Bonus equals your spell attack modifier, range 150 ft. Hit: 1d8 + 3 + the spell's level Psychic damage",
                            ),
                            (
                                "Psychic Slam",
                                "Mind Flayer only. Melee Attack Roll: Bonus equals your spell attack modifier, reach 5 ft. Hit: 1d8 + 3 + the spell's level Psychic damage",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (
                    Facts(
                        (
                            (
                                "Stat block",
                                "Use the spell slot's level for the spell's level in the stat block",
                            ),
                        )
                    ),
                ),
            ),
        ]


class SummonConstruct(ClassSpell):
    rules = SpellRules(
        name="Summon Construct",
        level=4,
        school=School.CONJURATION,
        classes=(CharacterClass.ARTIFICER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 90),
        components=Components(
            verbal=True, somatic=True, material="a lockbox worth 400+ GP"
        ),
        duration=Duration(DurationType.HOUR, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "You call forth the spirit of a Construct. It manifests in an unoccupied space that you can see within range and uses the Construct Spirit stat block. When you cast the spell, choose a material: Clay, Metal, or Stone. The creature resembles an animate statue (you determine the appearance) made of the chosen material, which determines certain details in its stat block. The creature disappears when it drops to 0 Hit Points or when the spell ends.\n"
            "The creature is an ally to you and your allies. In combat, the creature shares your Initiative count, but it takes its turn immediately after yours. It obeys your verbal commands (no action required by you). If you don’t issue any, it takes the Dodge action and uses its movement to avoid danger.\n"
            "Using a Higher-Level Spell Slot. Use the spell slot’s level for the spell’s level in the stat block."
        ),
        usage_tags=("summon",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "a07f102c67508d57")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You call forth the spirit of a Construct."),
            Facts(
                (
                    ("Appears", "In an unoccupied space that you can see within range"),
                    (
                        "Material",
                        "Clay, Metal, or Stone, chosen when you cast the spell; the creature resembles an animate statue (you determine the appearance) made of that material, which determines certain details in its stat block",
                    ),
                    ("Stat block", "Construct Spirit (below)"),
                    (
                        "Disappears",
                        "When it drops to 0 Hit Points or when the spell ends",
                    ),
                )
            ),
            Option(
                "Combat",
                (
                    Facts(
                        (
                            ("Allegiance", "An ally to you and your allies"),
                            (
                                "Initiative",
                                "It shares your Initiative count, but it takes its turn immediately after yours",
                            ),
                            (
                                "Commands",
                                "It obeys your verbal commands (no action required by you); if you don't issue any, it takes the Dodge action and uses its movement to avoid danger",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Construct Spirit",
                (
                    Facts(
                        (
                            ("Type", "Medium Construct"),
                            ("AC", "13 + the spell's level"),
                            ("Hit Points", "40 + 15 for each spell level above 4"),
                            ("Speed", "30 ft."),
                            (
                                "Abilities",
                                "Str 18, Dex 10, Con 18, Int 14, Wis 11, Cha 5",
                            ),
                            ("Resistances", "Poison"),
                            (
                                "Immunities",
                                "Charmed, Exhaustion, Frightened, Paralyzed, Poisoned",
                            ),
                            ("Senses", "Darkvision 60 ft., Passive Perception 10"),
                            ("Languages", "Understands the languages you know"),
                            (
                                "Heated Body",
                                "Metal only. A creature that hits the spirit with a melee attack or that starts its turn in a grapple with the spirit takes 1d10 Fire damage",
                            ),
                            (
                                "Stony Lethargy",
                                "Stone only. When a creature starts its turn within 10 feet of the spirit, the spirit can target it with magical energy if the spirit can see it. Wisdom saving throw against your spell save DC, the target. Failure: Until the start of its next turn, the target can't make Opportunity Attacks, and its Speed is halved",
                            ),
                            (
                                "Multiattack",
                                "The spirit makes a number of Slam attacks equal to half this spell's level (round down)",
                            ),
                            (
                                "Slam",
                                "Melee Attack Roll: Bonus equals your spell attack modifier, reach 5 ft. Hit: 1d8 + 4 + the spell's level Bludgeoning damage",
                            ),
                            (
                                "Berserk Lashing",
                                "Reaction (Clay only). Trigger: The spirit takes damage from a creature. Response: The spirit makes a Slam attack against that creature if possible, or the spirit moves up to half its Speed toward that creature without provoking Opportunity Attacks",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (
                    Facts(
                        (
                            (
                                "Stat block",
                                "Use the spell slot's level for the spell's level in the stat block",
                            ),
                        )
                    ),
                ),
            ),
        ]


class SummonElemental(ClassSpell):
    rules = SpellRules(
        name="Summon Elemental",
        level=4,
        school=School.CONJURATION,
        classes=(CharacterClass.DRUID, CharacterClass.RANGER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 90),
        components=Components(
            verbal=True,
            somatic=True,
            material="air, a pebble, ash, and water inside a gold-inlaid vial worth 400+ GP",
        ),
        duration=Duration(DurationType.HOUR, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "You call forth an Elemental spirit. It manifests in an unoccupied space that you can see within range and uses the Elemental Spirit stat block. When you cast the spell, choose an element: Air, Earth, Fire, or Water. The creature resembles a bipedal form wreathed in the chosen element, which determines certain details in its stat block. The creature disappears when it drops to 0 Hit Points or when the spell ends.\n"
            "The creature is an ally to you and your allies. In combat, the creature shares your Initiative count, but it takes its turn immediately after yours. It obeys your verbal commands (no action required by you). If you don’t issue any, it takes the Dodge action and uses its movement to avoid danger.\n"
            "Using a Higher-Level Spell Slot. Use the spell slot’s level for the spell’s level in the stat block."
        ),
        usage_tags=("summon",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "5cd468056e7bfa44")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You call forth an Elemental spirit."),
            Facts(
                (
                    ("Appears", "In an unoccupied space that you can see within range"),
                    (
                        "Element",
                        "Air, Earth, Fire, or Water, chosen when you cast the spell; the creature resembles a bipedal form wreathed in that element, which determines certain details in its stat block",
                    ),
                    ("Stat block", "Elemental Spirit (below)"),
                    (
                        "Disappears",
                        "When it drops to 0 Hit Points or when the spell ends",
                    ),
                )
            ),
            Option(
                "Combat",
                (
                    Facts(
                        (
                            ("Allegiance", "An ally to you and your allies"),
                            (
                                "Initiative",
                                "It shares your Initiative count, but it takes its turn immediately after yours",
                            ),
                            (
                                "Commands",
                                "It obeys your verbal commands (no action required by you); if you don't issue any, it takes the Dodge action and uses its movement to avoid danger",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Elemental Spirit",
                (
                    Facts(
                        (
                            ("Type", "Medium Elemental"),
                            ("AC", "11 + the spell's level"),
                            ("Hit Points", "50 + 10 for each spell level above 4"),
                            (
                                "Speed",
                                "40 ft., Burrow 40 ft. (Earth only), Fly 40 ft. (hover; Air only), Swim 40 ft. (Water only)",
                            ),
                            (
                                "Abilities",
                                "Str 18, Dex 15, Con 17, Int 4, Wis 10, Cha 16",
                            ),
                            (
                                "Resistances",
                                "Acid (Water only); Lightning and Thunder (Air only); Piercing and Slashing (Earth only)",
                            ),
                            (
                                "Immunities",
                                "Fire (Fire only), Poison; Exhaustion, Paralyzed, Petrified, Poisoned",
                            ),
                            ("Senses", "Darkvision 60 ft., Passive Perception 10"),
                            (
                                "Languages",
                                "Primordial, understands the languages you know",
                            ),
                            (
                                "Amorphous Form",
                                "Air, Fire, and Water only. The spirit can move through a space as narrow as 1 inch wide without it counting as Difficult Terrain",
                            ),
                            (
                                "Multiattack",
                                "The spirit makes a number of Slam attacks equal to half this spell's level (round down)",
                            ),
                            (
                                "Slam",
                                "Melee Attack Roll: Bonus equals your spell attack modifier, reach 5 ft. Hit: 1d10 + 4 + the spell's level Bludgeoning (Earth only), Cold (Water only), Lightning (Air only), or Fire (Fire only) damage",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (
                    Facts(
                        (
                            (
                                "Stat block",
                                "Use the spell slot's level for the spell's level in the stat block",
                            ),
                        )
                    ),
                ),
            ),
        ]


class SummonGreaterDemon(ClassSpell):
    rules = SpellRules(
        name="Summon Greater Demon",
        level=4,
        school=School.CONJURATION,
        classes=(CharacterClass.WARLOCK, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(
            verbal=True,
            somatic=True,
            material="a vial of blood from a humanoid killed within the past 24 hours",
        ),
        duration=Duration(DurationType.HOUR, 1, concentration=True),
        source="Xanathar's Guide to Everything",
        description=(
            "You utter foul words, summoning one demon from the chaos of the Abyss. You choose the demon's type, which must be one of challenge rating 5 or lower, such as a shadow demon or a barlgura. The demon appears in an unoccupied space you can see within range, and the demon disappears when it drops to 0 hit points or when the spell ends.\n"
            "Roll initiative for the demon, which has its own turns. When you summon it and on each of your turns thereafter, you can issue a verbal command to it (requiring no action on your part), telling it what it must do on its next turn. If you issue no command, it spends its turn attacking any creature within reach that has attacked it.\n"
            "At the end of each of the demon's turns, it makes a Charisma saving throw. The demon has disadvantage on this saving throw if you say its true name. On a failed save, the demon continues to obey you. On a successful save, your control of the demon ends for the rest of the duration, and the demon spends its turns pursuing and attacking the nearest non-demons to the best of its ability. If you stop concentrating on the spell before it reaches its full duration, an uncontrolled demon doesn't disappear for 1d6 rounds if it still has hit points.\n"
            "As part of casting the spell, you can form a circle on the ground with the blood used as a material component. The circle is large enough to encompass your space. While the spell lasts, the summoned demon can't cross the circle or harm it, and it can't target anyone within it. Using the material component in this manner consumes it when the spell ends.\n"
            "At Higher Levels. When you cast this spell using a spell slot of 5th level or higher, the challenge rating increases by 1 for each slot level above 4th."
        ),
        usage_tags=("control", "utility", "summon"),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "394fc5ac66de0772")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You utter foul words, summoning one demon from the chaos of the Abyss.",
                    ),
                    (
                        "Demon",
                        "You choose the demon's type, which must be one of challenge rating 5 or lower, such as a shadow demon or a barlgura",
                    ),
                    ("Appears", "In an unoccupied space you can see within range"),
                    (
                        "Disappears",
                        "When it drops to 0 hit points or when the spell ends",
                    ),
                    (
                        "Initiative",
                        "Roll initiative for the demon, which has its own turns",
                    ),
                    (
                        "Commands",
                        "When you summon it and on each of your turns thereafter, you can issue a verbal command to it (requiring no action on your part), telling it what it must do on its next turn",
                    ),
                    (
                        "No command",
                        "It spends its turn attacking any creature within reach that has attacked it",
                    ),
                )
            ),
            Option(
                "Keeping Control",
                (
                    Facts(
                        (
                            (
                                "Save",
                                "At the end of each of the demon's turns, it makes a Charisma saving throw, with Disadvantage if you say its true name",
                            ),
                            ("Failed save", "The demon continues to obey you"),
                            (
                                "Successful save",
                                "Your control of the demon ends for the rest of the duration, and it spends its turns pursuing and attacking the nearest non-demons to the best of its ability",
                            ),
                            (
                                "Concentration",
                                "If you stop concentrating on the spell before it reaches its full duration, an uncontrolled demon doesn't disappear for 1d6 rounds if it still has hit points",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Blood Circle",
                (
                    Facts(
                        (
                            (
                                "Circle",
                                "As part of casting the spell, you can form a circle on the ground with the blood used as a material component, large enough to encompass your space",
                            ),
                            (
                                "Protection",
                                "While the spell lasts, the summoned demon can't cross the circle or harm it, and it can't target anyone within it",
                            ),
                            (
                                "Component",
                                "Using the material component in this manner consumes it when the spell ends",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "At Higher Levels",
                (Facts((("Challenge rating", "+1 for each slot level above 4th"),)),),
            ),
        ]


class VitriolicSphere(ClassSpell):
    rules = SpellRules(
        name="Vitriolic Sphere",
        level=4,
        school=School.EVOCATION,
        classes=(CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 150),
        components=Components(verbal=True, somatic=True, material="a drop of bile"),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "You point at a location within range, and a glowing, 1-foot-diameter ball of acid streaks there and explodes in a 20-foot-radius Sphere. Each creature in that area makes a Dexterity saving throw. On a failed save, a creature takes 10d4 Acid damage and another 5d4 Acid damage at the end of its next turn. On a successful save, a creature takes half the initial damage only.\n"
            "Using a Higher-Level Spell Slot. The initial damage increases by 2d4 for each spell slot level above 4."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "fbd162601f048d72")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You point at a location within range, and a glowing, 1-foot-diameter ball of acid streaks there and explodes in a 20-foot-radius Sphere.",
                    ),
                    (
                        "Area",
                        "20-foot-radius Sphere at a location you point at within range",
                    ),
                    ("Save", "Dexterity, made by each creature in the area"),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (
                    (
                        "10d4 Acid damage, and another 5d4 Acid damage at the end of its next turn",
                        "Half the initial damage only",
                    ),
                ),
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (
                    Facts(
                        (("Initial damage", "+2d4 for each spell slot level above 4"),)
                    ),
                ),
            ),
        ]


class WallOfFire(ClassSpell):
    rules = SpellRules(
        name="Wall of Fire",
        level=4,
        school=School.EVOCATION,
        classes=(CharacterClass.DRUID, CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 120),
        components=Components(
            verbal=True, somatic=True, material="a piece of charcoal"
        ),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "You create a wall of fire on a solid surface within range. You can make the wall up to 60 feet long, 20 feet high, and 1 foot thick, or a ringed wall up to 20 feet in diameter, 20 feet high, and 1 foot thick. The wall is opaque and lasts for the duration.\n"
            "When the wall appears, each creature in its area makes a Dexterity saving throw, taking 5d8 Fire damage on a failed save or half as much damage on a successful one.\n"
            "One side of the wall, selected by you when you cast this spell, deals 5d8 Fire damage to each creature that ends its turn within 10 feet of that side or inside the wall. A creature takes the same damage when it enters the wall for the first time on a turn or ends its turn there. The other side of the wall deals no damage.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 1d8 for each spell slot level above 4."
        ),
        usage_tags=("control", "damage"),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "2b05be8222f8ff37")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You create a wall of fire on a solid surface within range."),
            Facts(
                (
                    (
                        "Shape",
                        "A wall up to 60 feet long, 20 feet high, and 1 foot thick, or a ringed wall up to 20 feet in diameter, 20 feet high, and 1 foot thick",
                    ),
                    ("Opaque", "The wall is opaque and lasts for the duration"),
                    (
                        "Save",
                        "Dexterity, made by each creature in its area when the wall appears",
                    ),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (("5d8 Fire damage", "Half as much damage"),),
            ),
            Option(
                "The Damaging Side",
                (
                    Facts(
                        (
                            (
                                "Side",
                                "One side of the wall, selected by you when you cast this spell; the other side of the wall deals no damage",
                            ),
                            (
                                "Damage",
                                "5d8 Fire damage to each creature that ends its turn within 10 feet of that side or inside the wall",
                            ),
                            (
                                "Entering",
                                "A creature takes the same damage when it enters the wall for the first time on a turn or ends its turn there",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Damage", "+1d8 for each spell slot level above 4"),)),),
            ),
        ]


class WaterySphere(ClassSpell):
    rules = SpellRules(
        name="Watery Sphere",
        level=4,
        school=School.CONJURATION,
        classes=(CharacterClass.DRUID, CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 90),
        components=Components(verbal=True, somatic=True, material="a droplet of water"),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Xanathar's Guide to Everything",
        description=(
            "You conjure up a sphere of water with a 5-foot radius on a point you can see within range. The sphere can hover in the air, but no more than 10 feet off the ground. The sphere remains for the spell's duration.\n"
            "Any creature in the sphere's space must make a Strength saving throw. On a successful save, a creature is ejected from that space to the nearest unoccupied space outside it. A Huge or larger creature succeeds on the saving throw automatically. On a failed save, a creature is restrained by the sphere and is engulfed by the water. At the end of each of its turns, a restrained target can repeat the saving throw.\n"
            "The sphere can restrain a maximum of four Medium or smaller creatures or one Large creature. If the sphere restrains a creature in excess of these numbers, a random creature that was already restrained by the sphere falls out of it and lands prone in a space within 5 feet of it.\n"
            "As an action, you can move the sphere up to 30 feet in a straight line. If it moves over a pit, cliff, or other drop, it safely descends until it is hovering 10 feet over ground. Any creature restrained by the sphere moves with it. You can ram the sphere into creatures, forcing them to make the saving throw, but no more than once per turn.\n"
            "When the spell ends, the sphere falls to the ground and extinguishes all normal flames within 30 feet of it. Any creature restrained by the sphere is knocked prone in the space where it falls."
        ),
        usage_tags=("control", "utility"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "0618b70717f3dc3f")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You conjure up a sphere of water with a 5-foot radius on a point you can see within range, and it remains for the spell's duration."
            ),
            Facts(
                (
                    (
                        "Hovering",
                        "The sphere can hover in the air, but no more than 10 feet off the ground",
                    ),
                    (
                        "Save",
                        "Strength, made by any creature in the sphere's space; a Huge or larger creature succeeds automatically",
                    ),
                    (
                        "Failed save",
                        "The creature is restrained by the sphere and engulfed by the water",
                    ),
                    (
                        "Successful save",
                        "The creature is ejected from that space to the nearest unoccupied space outside it",
                    ),
                    (
                        "Repeat save",
                        "At the end of each of its turns, a restrained target can repeat the saving throw",
                    ),
                    (
                        "Capacity",
                        "A maximum of four Medium or smaller creatures or one Large creature",
                    ),
                    (
                        "Overflow",
                        "If the sphere restrains a creature in excess of these numbers, a random creature that was already restrained by the sphere falls out of it and lands Prone in a space within 5 feet of it",
                    ),
                )
            ),
            Option(
                "Moving the Sphere",
                (
                    Facts(
                        (
                            (
                                "Action",
                                "As an action, you can move the sphere up to 30 feet in a straight line",
                            ),
                            (
                                "Drops",
                                "If it moves over a pit, cliff, or other drop, it safely descends until it is hovering 10 feet over ground",
                            ),
                            (
                                "Passengers",
                                "Any creature restrained by the sphere moves with it",
                            ),
                            (
                                "Ramming",
                                "You can ram the sphere into creatures, forcing them to make the saving throw, but no more than once per turn",
                            ),
                        )
                    ),
                ),
            ),
            Facts(
                (
                    (
                        "Spell ends",
                        "The sphere falls to the ground and extinguishes all normal flames within 30 feet of it; any creature restrained by the sphere is knocked Prone in the space where it falls",
                    ),
                )
            ),
        ]


class ZoneOfAmicability(ClassSpell):
    rules = SpellRules(
        name="Zone of Amicability",
        level=4,
        school=School.ENCHANTMENT,
        classes=(CharacterClass.BARD, CharacterClass.WARLOCK),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 10),
        source="Arcana Unleashed",
        description="A magical zone of amicability radiates from you in a 60-foot Emanation for the duration. When you make an ability check to influence a creature in that area, you can treat a d20 roll of 9 or lower as a 10.",
        usage_tags=("buff",),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "ffa4bfc51dba91e8")


class GravitySinkhole(ClassSpell):
    rules = SpellRules(
        name="Gravity Sinkhole",
        level=4,
        school=School.EVOCATION,
        classes=(CharacterClass.WIZARD,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 120),
        components=Components(verbal=True, somatic=True, material="a black marble"),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Explorer's Guide to Wildemount",
        description=(
            "A 20-foot-radius sphere of crushing force forms at a point you can see within range and tugs at the creatures there. Each creature in the sphere must make a Constitution saving throw. On a failed save, the creature takes 5d10 force damage, and is pulled in a straight line toward the center of the sphere, ending in an unoccupied space as close to the center as possible (even if that space is in the air). On a successful save, the creature takes half as much damage and isn't pulled.\n"
            "At Higher Levels. When you cast this spell using a spell slot of 5th level or higher, the damage increases by 1d10 for each slot level above 4th."
        ),
        usage_tags=("damage", "utility"),
        target=FeatureTarget.AREA,
        school_note="Dunamancy:Graviturgy",
    )
    converted_from = RecordStamp("spells_dnd5e.json", "9d80f9c6f920c671")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "A 20-foot-radius sphere of crushing force forms at a point you can see within range and tugs at the creatures there.",
                    ),
                    (
                        "Area",
                        "20-foot-radius sphere at a point you can see within range",
                    ),
                    ("Save", "Constitution, made by each creature in the sphere"),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (
                    (
                        "5d10 Force damage, and pulled in a straight line toward the center of the sphere, ending in an unoccupied space as close to the center as possible (even if that space is in the air)",
                        "Half as much damage, and not pulled",
                    ),
                ),
            ),
            Option(
                "At Higher Levels",
                (Facts((("Damage", "+1d10 for each slot level above 4th"),)),),
            ),
        ]


class GateSeal(ClassSpell):
    rules = SpellRules(
        name="Gate Seal",
        level=4,
        school=School.ABJURATION,
        classes=(
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.MINUTE, 1),
        range=Range(RangeType.FOOT, 60),
        components=Components(
            verbal=True,
            somatic=True,
            material="a broken portal key, which the spell consumes",
        ),
        duration=Duration(DurationType.HOUR, 24),
        source="Planescape - Adventures in the Multiverse",
        description="You fortify the fabric of the planes within a 30-foot cube you can see within range. Within that area, portals close and can't be opened for the duration. Spells and other effects that allow planar travel or open portals such as gate or plane shift, fail if used to enter or leave the area. The cube is stationary. At Higher Levels . When you cast this spell using a spell slot of 6th level or higher, the spell lasts until dispelled.",
        usage_tags=("control", "utility"),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "a16f09f3e1252fb4")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You fortify the fabric of the planes within a 30-foot cube you can see within range.",
                    ),
                    (
                        "Area",
                        "A 30-foot cube you can see within range; the cube is stationary",
                    ),
                    (
                        "Portals",
                        "Within that area, portals close and can't be opened for the duration",
                    ),
                    (
                        "Planar travel",
                        "Spells and other effects that allow planar travel or open portals, such as gate or plane shift, fail if used to enter or leave the area",
                    ),
                )
            ),
            Option(
                "At Higher Levels",
                (Facts((("6th level or higher", "The spell lasts until dispelled"),)),),
            ),
        ]


SPELLS = [
    ArcaneEye,
    AuraOfLife,
    AuraOfPurity,
    Backlash,
    Banishment,
    Blight,
    CharmMonster,
    Compulsion,
    Confusion,
    ConjureMinorElementals,
    ConjureWoodlandBeings,
    ControlWater,
    DeathWard,
    DimensionDoor,
    DistortedDistance,
    Divination,
    DominateBeast,
    Doomtide,
    ElementalBane,
    EvardsBlackTentacles,
    Fabricate,
    FesteringBlast,
    FindGreaterSteed,
    FireShield,
    FountOfMoonlight,
    FreedomOfMovement,
    GaldersSpeedyCourier,
    GateSeal,
    GiantInsect,
    GraspingVine,
    GravitySinkhole,
    GreaterInvisibility,
    GuardianOfFaith,
    GuardianOfNature,
    HallucinatoryTerrain,
    IceStorm,
    LeomundsSecretChest,
    LocateCreature,
    MordenkainensFaithfulHound,
    MordenkainensPrivateSanctum,
    OtilukesResilientSphere,
    PhantasmalKiller,
    Polymorph,
    RaulothimsPsychicLance,
    ShadowOfMoil,
    SickeningRadiance,
    SpellfireStorm,
    SpiritOfDeath,
    StaggeringSmite,
    SticksToSnakes,
    StoneShape,
    Stoneskin,
    StormSphere,
    SummonAberration,
    SummonConstruct,
    SummonElemental,
    SummonGreaterDemon,
    VitriolicSphere,
    WallOfFire,
    WaterySphere,
    ZoneOfAmicability,
]
