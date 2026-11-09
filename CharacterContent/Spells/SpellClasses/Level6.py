"""Level 6 spells as classes (CharacterContent/Spells/SpellFactory/ClassSpell.py),
which SpellFactory uses instead of their JSON records. Written by
CharacterContent/Spells/SpellClassConverter.py; edit them by hand from
then on: each class is its spell's one source."""

from CharacterContent.Spells.SpellFactory.ClassSpell import (
    ClassSpell,
    RecordStamp,
    SpellRules,
)
from CharacterContent.Spells.SpellFactory.Enums import (
    AreaShape,
    CastingTimeType,
    DurationType,
    RangeType,
    School,
)
from CharacterContent.Spells.SpellFactory.SpellFields import (
    Area,
    CastingTime,
    Components,
    Duration,
    Range,
)
from Core.Definitions import CharacterClass
from Model.Content.Feature import FeatureTarget
from Model.Content.FeatureText import Block, Facts, Option, Paragraph, Table


class ArcaneGate(ClassSpell):
    rules = SpellRules(
        name="Arcane Gate",
        level=6,
        school=School.CONJURATION,
        classes=(
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 500),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 10, concentration=True),
        source="Player's Handbook",
        description=(
            "You create linked teleportation portals. Choose two Large, unoccupied spaces on the ground that you can see, one space within range and the other one within 10 feet of you. A circular portal opens in each of those spaces and remains for the duration.\n"
            "The portals are two-dimensional glowing rings filled with mist that blocks sight. They hover inches from the ground and are perpendicular to it.\n"
            "A portal is open on only one side (you choose which). Anything entering the open side of a portal exits from the open side of the other portal as if the two were adjacent to each other. As a Bonus Action, you can change the facing of the open sides."
        ),
        usage_tags=("buff",),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "d6b3695e3bd3ced5")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You create linked teleportation portals."),
            Facts(
                (
                    (
                        "Spaces",
                        "Choose two Large, unoccupied spaces on the ground that you can see: one space within range and the other one within 10 feet of you",
                    ),
                    (
                        "Portals",
                        "A circular portal opens in each of those spaces and remains for the duration",
                    ),
                    (
                        "Appearance",
                        "The portals are two-dimensional glowing rings filled with mist that blocks sight; they hover inches from the ground and are perpendicular to it",
                    ),
                    (
                        "Open side",
                        "A portal is open on only one side (you choose which)",
                    ),
                    (
                        "Travel",
                        "Anything entering the open side of a portal exits from the open side of the other portal as if the two were adjacent to each other",
                    ),
                    (
                        "Facing",
                        "As a Bonus Action, you can change the facing of the open sides",
                    ),
                )
            ),
        ]


class BladeBarrier(ClassSpell):
    rules = SpellRules(
        name="Blade Barrier",
        level=6,
        school=School.EVOCATION,
        classes=(CharacterClass.CLERIC,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 90),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 10, concentration=True),
        source="Player's Handbook",
        description=(
            "You create a wall of whirling blades made of magical energy. The wall appears within range and lasts for the duration. You make a straight wall up to 100 feet long, 20 feet high, and 5 feet thick, or a ringed wall up to 60 feet in diameter, 20 feet high, and 5 feet thick. The wall provides Three-Quarters Cover, and its space is Difficult Terrain.\n"
            "Any creature in the wall’s space makes a Dexterity saving throw, taking 6d10 Force damage on a failed save or half as much damage on a successful one. A creature also makes that save if it enters the wall’s space or ends it turn there. A creature makes that save only once per turn."
        ),
        usage_tags=("control",),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "b739853f9b47b24f")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You create a wall of whirling blades made of magical energy.",
                    ),
                    (
                        "Appears",
                        "The wall appears within range and lasts for the duration",
                    ),
                    (
                        "Shape",
                        "A straight wall up to 100 feet long, 20 feet high, and 5 feet thick, or a ringed wall up to 60 feet in diameter, 20 feet high, and 5 feet thick",
                    ),
                    ("Cover", "The wall provides Three-Quarters Cover"),
                    ("Terrain", "The wall's space is Difficult Terrain"),
                    ("Save", "Dexterity, made by any creature in the wall's space"),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (("6d10 Force damage", "Half as much damage"),),
            ),
            Facts(
                (
                    (
                        "Also saves",
                        "A creature also makes that save if it enters the wall's space or ends its turn there",
                    ),
                    ("Once per turn", "A creature makes that save only once per turn"),
                )
            ),
        ]


class BonesOfTheEarth(ClassSpell):
    rules = SpellRules(
        name="Bones of the Earth",
        level=6,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.DRUID,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 120),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Xanathar's Guide to Everything",
        description=(
            "You cause up to six pillars of stone to burst from places on the ground that you can see within range. Each pillar is a cylinder that has a diameter of 5 feet and a height of up to 30 feet. The ground where a pillar appears must be wide enough for its diameter, and you can target ground under a creature if that creature is Medium or smaller. Each pillar has AC 5 and 30 hit points. When reduced to 0 hit points, a pillar crumbles into rubble, which creates an area of difficult terrain with a 10-foot radius. The rubble lasts until cleared.\n"
            "If a pillar is created under a creature, that creature must succeed on a Dexterity saving throw or be lifted by the pillar. A creature can choose to fail the save.\n"
            "If a pillar is prevented from reaching its full height because of a ceiling or other obstacle, a creature on the pillar takes 6d6 bludgeoning damage and is restrained, pinched between the pillar and the obstacle. The restrained creature can use an action to make a Strength or Dexterity check (the creature's choice) against the spell's saving throw DC. On a success, the creature is no longer restrained and must either move off the pillar or fall off it.\n"
            "At Higher Levels. When you cast this spell using a spell slot of 7th level or higher, you can create two additional pillars for each slot level above 6th."
        ),
        usage_tags=("control", "damage", "utility"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "74b29439d2421af4")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Pillars",
                        "Up to six pillars of stone burst from places on the ground that you can see within range",
                    ),
                    (
                        "Shape",
                        "Each pillar is a cylinder that has a diameter of 5 feet and a height of up to 30 feet",
                    ),
                    (
                        "Ground",
                        "The ground where a pillar appears must be wide enough for its diameter, and you can target ground under a creature if that creature is Medium or smaller",
                    ),
                    ("Each pillar", "AC 5 and 30 hit points"),
                    (
                        "Rubble",
                        "When reduced to 0 hit points, a pillar crumbles into rubble, which creates an area of Difficult Terrain with a 10-foot radius",
                    ),
                    ("Cleared", "The rubble lasts until cleared"),
                )
            ),
            Option(
                "Pillar Under a Creature",
                (
                    Facts(
                        (
                            (
                                "Save",
                                "Dexterity, made by a creature under which a pillar is created",
                            ),
                            ("Failed save", "The creature is lifted by the pillar"),
                            ("Successful save", "No effect"),
                            ("Choosing", "A creature can choose to fail the save"),
                        )
                    ),
                ),
            ),
            Option(
                "Pillar Blocked From Full Height",
                (
                    Facts(
                        (
                            (
                                "Condition",
                                "A pillar is prevented from reaching its full height because of a ceiling or other obstacle",
                            ),
                            (
                                "Effect",
                                "A creature on the pillar takes 6d6 Bludgeoning damage and is Restrained, pinched between the pillar and the obstacle",
                            ),
                            (
                                "Escape",
                                "The Restrained creature can use an action to make a Strength or Dexterity check (the creature's choice) against the spell's saving throw DC",
                            ),
                            (
                                "On a success",
                                "The creature is no longer Restrained and must either move off the pillar or fall off it",
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
                                "Pillars",
                                "When you cast this spell using a spell slot of 7th level or higher, you can create two additional pillars for each slot level above 6th",
                            ),
                        )
                    ),
                ),
            ),
        ]


class ChainLightning(ClassSpell):
    rules = SpellRules(
        name="Chain Lightning",
        level=6,
        school=School.EVOCATION,
        classes=(CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 150),
        components=Components(verbal=True, somatic=True, material="three silver pins"),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "You launch a lightning bolt toward a target you can see within range. Three bolts then leap from that target to as many as three other targets of your choice, each of which must be within 30 feet of the first target. A target can be a creature or an object and can be targeted by only one of the bolts.\n"
            "Each target makes a Dexterity saving throw, taking 10d8 Lightning damage on a failed save or half as much damage on a successful one.\n"
            "Using a Higher-Level Spell Slot. One additional bolt leaps from the first target to another target for each spell slot level above 6."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "ea0b7bb667ffae1c")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "First bolt",
                        "You launch a lightning bolt toward a target you can see within range",
                    ),
                    (
                        "Other bolts",
                        "Three bolts then leap from that target to as many as three other targets of your choice, each of which must be within 30 feet of the first target",
                    ),
                    (
                        "Targets",
                        "A target can be a creature or an object and can be targeted by only one of the bolts",
                    ),
                    ("Save", "Dexterity, made by each target"),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (("10d8 Lightning damage", "Half as much damage"),),
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (
                    Facts(
                        (
                            (
                                "Bolts",
                                "One additional bolt leaps from the first target to another target for each spell slot level above 6",
                            ),
                        )
                    ),
                ),
            ),
        ]


class CircleOfDeath(ClassSpell):
    rules = SpellRules(
        name="Circle of Death",
        level=6,
        school=School.NECROMANCY,
        classes=(
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 150),
        components=Components(
            verbal=True,
            somatic=True,
            material="the powder of a crushed black pearl worth 500+ GP",
        ),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "Negative energy ripples out in a 60-foot-radius Sphere from a point you choose within range. Each creature in that area makes a Constitution saving throw, taking 8d8 Necrotic damage on a failed save or half as much damage on a successful one.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 2d8 for each spell slot level above 6."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "8c59227a86b5a64f")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Flavor", "Negative energy ripples out."),
                    (
                        "Area",
                        "60-foot-radius Sphere from a point you choose within range",
                    ),
                    ("Save", "Constitution, made by each creature in that area"),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (("8d8 Necrotic damage", "Half as much damage"),),
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Damage", "+2d8 for each spell slot level above 6"),)),),
            ),
        ]


class ConjureFey(ClassSpell):
    rules = SpellRules(
        name="Conjure Fey",
        level=6,
        school=School.CONJURATION,
        classes=(CharacterClass.DRUID,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 10, concentration=True),
        source="Player's Handbook",
        description=(
            "You conjure a Medium spirit from the Feywild in an unoccupied space you can see within range. The spirit lasts for the duration, and it looks like a Fey creature of your choice. When the spirit appears, you can make one melee spell attack against a creature within 5 feet of it. On a hit, the target takes Psychic damage equal to 3d12 plus your spellcasting ability modifier, and the target has the Frightened condition until the start of your next turn, with both you and the spirit as the source of the fear.\n"
            "As a Bonus Action on your later turns, you can teleport the spirit to an unoccupied space you can see within 30 feet of the space it left and make the attack against a creature within 5 feet of it.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 1d12 for each spell slot level above 6."
        ),
        usage_tags=("buff", "control", "damage"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "88de18b4848a8429")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Appears",
                        "A Medium spirit from the Feywild, conjured in an unoccupied space you can see within range",
                    ),
                    ("Lasts", "The spirit lasts for the duration"),
                    ("Looks like", "A Fey creature of your choice"),
                    (
                        "Attack",
                        "When the spirit appears, you can make one melee spell attack against a creature within 5 feet of it",
                    ),
                    (
                        "On a hit",
                        "The target takes Psychic damage equal to 3d12 plus your spellcasting ability modifier, and the target has the Frightened condition until the start of your next turn, with both you and the spirit as the source of the fear",
                    ),
                    (
                        "Later turns",
                        "As a Bonus Action on your later turns, you can teleport the spirit to an unoccupied space you can see within 30 feet of the space it left and make the attack against a creature within 5 feet of it",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Damage", "+1d12 for each spell slot level above 6"),)),),
            ),
        ]


class Contingency(ClassSpell):
    rules = SpellRules(
        name="Contingency",
        level=6,
        school=School.ABJURATION,
        classes=(CharacterClass.WIZARD,),
        casting_time=CastingTime(CastingTimeType.MINUTE, 10),
        range=Range(RangeType.SELF),
        components=Components(
            verbal=True,
            somatic=True,
            material="a gem-encrusted statuette of yourself worth 1,500+ GP",
        ),
        duration=Duration(DurationType.DAY, 10),
        source="Player's Handbook",
        description=(
            "Choose a spell of level 5 or lower that you can cast, that has a casting time of an action, and that can target you. You cast that spell—called the contingent spell—as part of casting Contingency, expending spell slots for both, but the contingent spell doesn’t come into effect. Instead, it takes effect when a certain trigger occurs. You describe that trigger when you cast the two spells. For example, a Contingency cast with Water Breathing might stipulate that Water Breathing comes into effect when you are engulfed in water or a similar liquid.\n"
            "The contingent spell takes effect immediately after the trigger occurs for the first time, whether or not you want it to, and then Contingency ends.\n"
            "The contingent spell takes effect only on you, even if it can normally target others. You can use only one Contingency spell at a time. If you cast this spell again, the effect of another Contingency spell on you ends. Also, Contingency ends on you if its material component is ever not on your person."
        ),
        usage_tags=("buff",),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "32a8ce3c7d329b7a")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Spell",
                        "Choose a spell of level 5 or lower that you can cast, that has a casting time of an action, and that can target you",
                    ),
                    (
                        "Casting",
                        "You cast that spell—called the contingent spell—as part of casting Contingency, expending spell slots for both, but the contingent spell doesn't come into effect",
                    ),
                    (
                        "Trigger",
                        "Instead, it takes effect when a certain trigger occurs. You describe that trigger when you cast the two spells",
                    ),
                    (
                        "Example",
                        "A Contingency cast with Water Breathing might stipulate that Water Breathing comes into effect when you are engulfed in water or a similar liquid",
                    ),
                    (
                        "Taking effect",
                        "The contingent spell takes effect immediately after the trigger occurs for the first time, whether or not you want it to, and then Contingency ends",
                    ),
                    (
                        "Only on you",
                        "The contingent spell takes effect only on you, even if it can normally target others",
                    ),
                    (
                        "One at a time",
                        "You can use only one Contingency spell at a time. If you cast this spell again, the effect of another Contingency spell on you ends",
                    ),
                    (
                        "Ends early",
                        "Contingency ends on you if its material component is ever not on your person",
                    ),
                )
            )
        ]


class CreateHomunculus(ClassSpell):
    rules = SpellRules(
        name="Create Homunculus",
        level=6,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.WIZARD,),
        casting_time=CastingTime(CastingTimeType.HOUR, 1),
        range=Range(RangeType.TOUCH),
        components=Components(
            verbal=True,
            somatic=True,
            material="clay, ash, and mandrake root, all of which the spell consumes, and a jewel-encrusted dagger worth at least 1,000 gp",
        ),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Xanathar's Guide to Everything",
        description="While speaking an intricate incantation, you cut yourself with a jewel-encrusted dagger, taking 2d4 piercing damage that can't be reduced in any way. You then drip your blood on the spell's other components and touch them, transforming them into a special construct called a homunculus. The statistics of the homunculus are in the Monster Manual. It is your faithful companion, and it dies if you die. Whenever you finish a long rest, you can spend up to half your Hit Dice if the homunculus is on the same plane of existence as you. When you do so, roll each die and add your Constitution modifier to it. Your hit point maximum is reduced by the total, and the homunculus's hit point maximum and current hit points are both increased by it. This process can reduce you to no lower than 1 hit point. and the change to your and the homunculus's hit points ends when you finish your next long rest. The reduction to your hit point maximum can't be removed by any means before then, except by the homunculus‘s death. You can have only one homunculus at a time. If you cast this spell while your homunculus lives, the spell fails.",
        usage_tags=("control", "damage", "summon"),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "ffe7107088d26e10")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Cost",
                        "While speaking an intricate incantation, you cut yourself with a jewel-encrusted dagger, taking 2d4 Piercing damage that can't be reduced in any way",
                    ),
                    (
                        "Creating",
                        "You then drip your blood on the spell's other components and touch them, transforming them into a special construct called a homunculus",
                    ),
                    (
                        "Statistics",
                        "The statistics of the homunculus are in the Monster Manual",
                    ),
                    (
                        "Companion",
                        "It is your faithful companion, and it dies if you die",
                    ),
                    (
                        "Only one",
                        "You can have only one homunculus at a time. If you cast this spell while your homunculus lives, the spell fails",
                    ),
                )
            ),
            Option(
                "Sharing Hit Points",
                (
                    Facts(
                        (
                            (
                                "When",
                                "Whenever you finish a long rest, you can spend up to half your Hit Dice if the homunculus is on the same plane of existence as you",
                            ),
                            (
                                "Roll",
                                "When you do so, roll each die and add your Constitution modifier to it",
                            ),
                            (
                                "Effect",
                                "Your hit point maximum is reduced by the total, and the homunculus's hit point maximum and current hit points are both increased by it",
                            ),
                            (
                                "Minimum",
                                "This process can reduce you to no lower than 1 hit point",
                            ),
                            (
                                "Lasts",
                                "The change to your and the homunculus's hit points ends when you finish your next long rest",
                            ),
                            (
                                "Removal",
                                "The reduction to your hit point maximum can't be removed by any means before then, except by the homunculus's death",
                            ),
                        )
                    ),
                ),
            ),
        ]


class CreateUndead(ClassSpell):
    rules = SpellRules(
        name="Create Undead",
        level=6,
        school=School.NECROMANCY,
        classes=(CharacterClass.CLERIC, CharacterClass.WARLOCK, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.MINUTE, 1),
        range=Range(RangeType.FOOT, 10),
        components=Components(
            verbal=True,
            somatic=True,
            material="one 150+ GP black onyx stone for each corpse",
        ),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "You can cast this spell only at night. Choose up to three corpses of Medium or Small Humanoids within range. Each one becomes a Ghoul under your control (see the Monster Manual for its stat block).\n"
            "As a Bonus Action on each of your turns, you can mentally command any creature you animated with this spell if the creature is within 120 feet of you (if you control multiple creatures, you can command any of them at the same time, issuing the same command to them). You decide what action the creature will take and where it will move on its next turn, or you can issue a general command, such as to guard a particular place. If you issue no commands, the creature takes the Dodge action and moves only to avoid harm. Once given an order, the creature continues to follow the order until its task is complete.\n"
            "The creature is under your control for 24 hours, after which it stops obeying any command you’ve given it. To maintain control of the creature for another 24 hours, you must cast this spell on the creature before the current 24-hour period ends. This use of the spell reasserts your control over up to three creatures you have animated with this spell rather than animating new ones.\n"
            "Using a Higher-Level Spell Slot. If you use a level 7 spell slot, you can animate or reassert control over four Ghouls. If you use a level 8 spell slot, you can animate or reassert control over five Ghouls or two Ghasts or Wights. If you use a level 9 spell slot, you can animate or reassert control over six Ghouls, three Ghasts or Wights, or two Mummies. See the Monster Manual for these stat blocks."
        ),
        usage_tags=("summon",),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "329c19656e1b56e7")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Casting", "You can cast this spell only at night"),
                    (
                        "Targets",
                        "Up to three corpses of Medium or Small Humanoids within range",
                    ),
                    (
                        "Effect",
                        "Each one becomes a Ghoul under your control (see the Monster Manual for its stat block)",
                    ),
                )
            ),
            Option(
                "Commanding",
                (
                    Facts(
                        (
                            (
                                "Command",
                                "As a Bonus Action on each of your turns, you can mentally command any creature you animated with this spell if the creature is within 120 feet of you",
                            ),
                            (
                                "Several",
                                "If you control multiple creatures, you can command any of them at the same time, issuing the same command to them",
                            ),
                            (
                                "Orders",
                                "You decide what action the creature will take and where it will move on its next turn, or you can issue a general command, such as to guard a particular place",
                            ),
                            (
                                "No command",
                                "If you issue no commands, the creature takes the Dodge action and moves only to avoid harm",
                            ),
                            (
                                "Following",
                                "Once given an order, the creature continues to follow the order until its task is complete",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Control",
                (
                    Facts(
                        (
                            (
                                "Lasts",
                                "The creature is under your control for 24 hours, after which it stops obeying any command you've given it",
                            ),
                            (
                                "Maintaining",
                                "To maintain control of the creature for another 24 hours, you must cast this spell on the creature before the current 24-hour period ends",
                            ),
                            (
                                "Reasserting",
                                "This use of the spell reasserts your control over up to three creatures you have animated with this spell rather than animating new ones",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (
                    Table(
                        ("Slot level", "You can animate or reassert control over"),
                        (
                            ("7", "Four Ghouls"),
                            ("8", "Five Ghouls or two Ghasts or Wights"),
                            ("9", "Six Ghouls, three Ghasts or Wights, or two Mummies"),
                        ),
                    ),
                    Facts(
                        (
                            (
                                "Stat blocks",
                                "See the Monster Manual for these stat blocks",
                            ),
                        )
                    ),
                ),
            ),
        ]


class Dirge(ClassSpell):
    rules = SpellRules(
        name="Dirge",
        level=6,
        school=School.ENCHANTMENT,
        classes=(CharacterClass.BARD, CharacterClass.CLERIC),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Forgotten Realms - Heroes of Faerun",
        description=(
            "Deathly power fills a 60-foot Emanation originating from you for the duration.\n"
            "When you cast this spell, you can designate creatures to be unaffected by it. Any other creature can’t regain Hit Points while in the Emanation. Whenever the Emanation enters a creature’s space and whenever a creature enters the Emanation or ends its turn there, the creature makes a Constitution saving throw. On a failed save, the creature takes 3d10 Necrotic damage and has the Prone condition. On a successful save, the creature takes half as much damage and its Speed is halved. A creature makes this save only once per turn.\n"
            "Casting as a Circle Spell. Casting this as a Circle spell requires a minimum of two secondary casters. If the spell is cast as a Circle spell, its duration becomes Concentration, up to 10 minutes.\n"
            "A creature that fails its save against the spell’s effect also gains 1 Exhaustion level. While the creature has Exhaustion levels, finishing a Long Rest neither restores lost Hit Points nor reduces the creature’s Exhaustion level.\n"
            "When the spell is cast, each secondary caster must expend a level 4+ spell slot; otherwise, the spell fails."
        ),
        usage_tags=("control", "damage", "heal"),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "69700a1c2ade5a3a")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Area",
                        "Deathly power fills a 60-foot Emanation originating from you for the duration",
                    ),
                    (
                        "Unaffected",
                        "When you cast this spell, you can designate creatures to be unaffected by it",
                    ),
                    (
                        "Healing",
                        "Any other creature can't regain Hit Points while in the Emanation",
                    ),
                    (
                        "Save",
                        "Constitution, made whenever the Emanation enters a creature's space and whenever a creature enters the Emanation or ends its turn there",
                    ),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (
                    (
                        "The creature takes 3d10 Necrotic damage and has the Prone condition",
                        "The creature takes half as much damage and its Speed is halved",
                    ),
                ),
            ),
            Facts(
                (("Once per turn", "A creature makes this save only once per turn"),)
            ),
            Option(
                "Casting as a Circle Spell",
                (
                    Facts(
                        (
                            (
                                "Casters",
                                "Casting this as a Circle spell requires a minimum of two secondary casters",
                            ),
                            (
                                "Duration",
                                "If the spell is cast as a Circle spell, its duration becomes Concentration, up to 10 minutes",
                            ),
                            (
                                "Exhaustion",
                                "A creature that fails its save against the spell's effect also gains 1 Exhaustion level",
                            ),
                            (
                                "Resting",
                                "While the creature has Exhaustion levels, finishing a Long Rest neither restores lost Hit Points nor reduces the creature's Exhaustion level",
                            ),
                            (
                                "Spell slots",
                                "When the spell is cast, each secondary caster must expend a level 4+ spell slot; otherwise, the spell fails",
                            ),
                        )
                    ),
                ),
            ),
        ]


class Disintegrate(ClassSpell):
    rules = SpellRules(
        name="Disintegrate",
        level=6,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(
            verbal=True, somatic=True, material="a lodestone and dust"
        ),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "You launch a green ray at a target you can see within range. The target can be a creature, a nonmagical object, or a creation of magical force, such as the wall created by Wall of Force .\n"
            "A creature targeted by this spell makes a Dexterity saving throw. On a failed save, the target takes 10d6 + 40 Force damage. If this damage reduces it to 0 Hit Points, it and everything nonmagical it is wearing and carrying are disintegrated into gray dust. The target can be revived only by a True Resurrection or a Wish spell.\n"
            "This spell automatically disintegrates a Large or smaller nonmagical object or a creation of magical force. If such a target is Huge or larger, this spell disintegrates a 10-foot-Cube portion of it.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 3d6 for each spell slot level above 6."
        ),
        usage_tags=("control", "damage", "heal"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "542082d3ba5e8236")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You launch a green ray at a target you can see within range.",
                    ),
                    (
                        "Target",
                        "A target you can see within range; it can be a creature, a nonmagical object, or a creation of magical force, such as the wall created by Wall of Force",
                    ),
                    ("Save", "Dexterity, made by a creature targeted by this spell"),
                    ("Failed save", "The target takes 10d6 + 40 Force damage"),
                    ("Successful save", "No damage"),
                    (
                        "Disintegrated",
                        "If this damage reduces it to 0 Hit Points, it and everything nonmagical it is wearing and carrying are disintegrated into gray dust",
                    ),
                    (
                        "Revival",
                        "The target can be revived only by a True Resurrection or a Wish spell",
                    ),
                    (
                        "Objects",
                        "This spell automatically disintegrates a Large or smaller nonmagical object or a creation of magical force",
                    ),
                    (
                        "Huge or larger",
                        "If such a target is Huge or larger, this spell disintegrates a 10-foot-Cube portion of it",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Damage", "+3d6 for each spell slot level above 6"),)),),
            ),
        ]


class DrawmijsInstantSummons(ClassSpell):
    rules = SpellRules(
        name="Drawmij's Instant Summons",
        level=6,
        school=School.CONJURATION,
        classes=(CharacterClass.WIZARD,),
        casting_time=CastingTime(CastingTimeType.MINUTE, 1, ritual=True),
        range=Range(RangeType.TOUCH),
        components=Components(
            verbal=True, somatic=True, material="a sapphire worth 1,000+ GP"
        ),
        duration=Duration(DurationType.UNTIL_DISPELLED),
        source="Player's Handbook",
        description=(
            "You touch the sapphire used in the casting and an object weighing 10 pounds or less whose longest dimension is 6 feet or less. The spell leaves an Invisible mark on that object and invisibly inscribes the object’s name on the sapphire. Each time you cast this spell, you must use a different sapphire.\n"
            "Thereafter, you can take a Magic action to speak the object’s name and crush the sapphire. The object instantly appears in your hand regardless of physical or planar distances, and the spell ends.\n"
            "If another creature is holding or carrying the object, crushing the sapphire doesn’t transport it, but instead you learn who that creature is and where that creature is currently located."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "508a3da2fbab5cec")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Touch",
                        "You touch the sapphire used in the casting and an object weighing 10 pounds or less whose longest dimension is 6 feet or less",
                    ),
                    (
                        "Mark",
                        "The spell leaves an Invisible mark on that object and invisibly inscribes the object's name on the sapphire",
                    ),
                    (
                        "Sapphire",
                        "Each time you cast this spell, you must use a different sapphire",
                    ),
                    (
                        "Recall",
                        "Thereafter, you can take a Magic action to speak the object's name and crush the sapphire",
                    ),
                    (
                        "Effect",
                        "The object instantly appears in your hand regardless of physical or planar distances, and the spell ends",
                    ),
                    (
                        "Held by another",
                        "If another creature is holding or carrying the object, crushing the sapphire doesn't transport it, but instead you learn who that creature is and where that creature is currently located",
                    ),
                )
            )
        ]


class DruidGrove(ClassSpell):
    rules = SpellRules(
        name="Druid Grove",
        level=6,
        school=School.ABJURATION,
        classes=(CharacterClass.DRUID,),
        casting_time=CastingTime(CastingTimeType.MINUTE, 10),
        range=Range(RangeType.TOUCH),
        components=Components(
            verbal=True,
            somatic=True,
            material="mistletoe, which the spell consumes, that was harvested with a golden sickle under the light of a full moon",
        ),
        duration=Duration(DurationType.HOUR, 24),
        source="Xanathar's Guide to Everything",
        description=(
            "You invoke the spirits of nature to protect an area outdoors or underground. The area can be as small as a 30-foot cube or as large as a 90-foot cube. Buildings and other structures are excluded from the affected area. If you cast this spell in the same area every day for a year, the spell lasts until dispelled. The spell creates the following effects within the area. When you cast this spell, you can specify creatures as friends who are immune to the effects. You can also specify a password that, when spoken aloud, makes the speaker immune to these effects. The entire warded area radiates magic. A dispel magic cast on the area, if successful, removes only one of the following effects, not the entire area. That spell's caster chooses which effect to end. Only when all its effects are gone is this spell dispelled.\n"
            "Solid Fog. You can fill any number of 5-foot squares on the ground with thick fog, making them heavily obscured. The fog reaches 10 feet high. In addition, every foot of movement through the fog costs 2 extra feet. To a creature immune to this effect, the fog obscures nothing and looks like soft mist, with motes of green light floating in the air.\n"
            "Grasping Undergrowth. You can fill any number of 5-foot squares on the ground that aren't filled with fog with grasping weeds and vines, as if they were affected by an entangle spell. To a creature immune to this effect, the weeds and vines feel soft and reshape themselves to serve as temporary seats or beds.\n"
            "Grove Guardians. You can animate up to four trees in the area, causing them to uproot themselves from the ground. These trees have the same statistics as an awakened tree, which appears in the Monster Manual, except they can't speak, and their bark is covered with druidic symbols. If any creature not immune to this effect enters the warded area, the grove guardians fight until they have driven off or slain the intruders. The grove guardians also obey your spoken commands (no action required by you) that you issue while in the area. If you don't give them commands and no intruders are present, the grove guardians do nothing. The grove guardians can‘t leave the warded area. When the spell ends, the magic animating them disappears, and the trees take root again if possible.\n"
            "Additional Spell Effect. You can place your choice of one of the following magical effects within the warded area:\n"
            "A constant gust of wind in two locations of your choice\n"
            "Spike growth in one location of your choice\n"
            "Wind wall in two locations of your choice\n"
            "To a creature immune to this effect, the winds are a fragrant, gentle breeze, and the area of spike growth is harmless."
        ),
        usage_tags=("control", "utility"),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "ccbfe6b66ecf65a7")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You invoke the spirits of nature to protect an area outdoors or underground.",
                    ),
                    (
                        "Area",
                        "An area outdoors or underground, as small as a 30-foot cube or as large as a 90-foot cube; buildings and other structures are excluded from the affected area",
                    ),
                    (
                        "Permanent",
                        "If you cast this spell in the same area every day for a year, the spell lasts until dispelled",
                    ),
                    (
                        "Effects",
                        "The spell creates the following effects within the area",
                    ),
                    (
                        "Friends",
                        "When you cast this spell, you can specify creatures as friends who are immune to the effects",
                    ),
                    (
                        "Password",
                        "You can also specify a password that, when spoken aloud, makes the speaker immune to these effects",
                    ),
                    ("Magic", "The entire warded area radiates magic"),
                    (
                        "Dispel Magic",
                        "A dispel magic cast on the area, if successful, removes only one of the following effects, not the entire area",
                    ),
                    ("Which effect", "That spell's caster chooses which effect to end"),
                    (
                        "Dispelled",
                        "Only when all its effects are gone is this spell dispelled",
                    ),
                )
            ),
            Option(
                "Solid Fog",
                (
                    Facts(
                        (
                            (
                                "Fog",
                                "You can fill any number of 5-foot squares on the ground with thick fog, making them Heavily Obscured",
                            ),
                            ("Height", "The fog reaches 10 feet high"),
                            (
                                "Movement",
                                "Every foot of movement through the fog costs 2 extra feet",
                            ),
                            (
                                "Immune creatures",
                                "To a creature immune to this effect, the fog obscures nothing and looks like soft mist, with motes of green light floating in the air",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Grasping Undergrowth",
                (
                    Facts(
                        (
                            (
                                "Weeds",
                                "You can fill any number of 5-foot squares on the ground that aren't filled with fog with grasping weeds and vines, as if they were affected by an entangle spell",
                            ),
                            (
                                "Immune creatures",
                                "To a creature immune to this effect, the weeds and vines feel soft and reshape themselves to serve as temporary seats or beds",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Grove Guardians",
                (
                    Facts(
                        (
                            (
                                "Trees",
                                "You can animate up to four trees in the area, causing them to uproot themselves from the ground",
                            ),
                            (
                                "Statistics",
                                "These trees have the same statistics as an awakened tree, which appears in the Monster Manual, except they can't speak, and their bark is covered with druidic symbols",
                            ),
                            (
                                "Intruders",
                                "If any creature not immune to this effect enters the warded area, the grove guardians fight until they have driven off or slain the intruders",
                            ),
                            (
                                "Commands",
                                "The grove guardians also obey your spoken commands (no action required by you) that you issue while in the area",
                            ),
                            (
                                "No commands",
                                "If you don't give them commands and no intruders are present, the grove guardians do nothing",
                            ),
                            (
                                "Leaving",
                                "The grove guardians can't leave the warded area",
                            ),
                            (
                                "Ending",
                                "When the spell ends, the magic animating them disappears, and the trees take root again if possible",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Additional Spell Effect",
                (
                    Facts(
                        (
                            (
                                "Choose one",
                                "You can place your choice of one of the following magical effects within the warded area",
                            ),
                        )
                    ),
                    Table(
                        ("Effect", "Locations"),
                        (
                            ("A constant gust of wind", "Two locations of your choice"),
                            ("Spike growth", "One location of your choice"),
                            ("Wind wall", "Two locations of your choice"),
                        ),
                    ),
                    Facts(
                        (
                            (
                                "Immune creatures",
                                "To a creature immune to this effect, the winds are a fragrant, gentle breeze, and the area of spike growth is harmless",
                            ),
                        )
                    ),
                ),
            ),
        ]


class ElminstersEffulgentSpheres(ClassSpell):
    rules = SpellRules(
        name="Elminster's Effulgent Spheres",
        level=6,
        school=School.EVOCATION,
        classes=(CharacterClass.DRUID, CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(
            verbal=True, somatic=True, material="an opal worth 1,000 GP+"
        ),
        duration=Duration(DurationType.HOUR, 1),
        source="Forgotten Realms - Heroes of Faerun",
        description=(
            "Six chromatic spheres orbit you for the duration.\n"
            "While the spheres are present, you can expend spheres to create the following effects:\n"
            "Absorb Energy. When you take Acid, Cold, Fire, Lightning, or Thunder damage, you can take a Reaction to expend one sphere and give yourself Resistance to the triggering damage type until the start of your next turn.\n"
            "Energy Blast. As a Bonus Action, you send one sphere hurtling toward a target within 120 feet of yourself. Make a ranged spell attack. On a hit, the target takes 3d6 Acid, Cold, Fire, Lightning, or Thunder damage (your choice). Regardless of whether you hit, the sphere is expended.\n"
            "The spell ends early if you have no more spheres remaining.\n"
            "Using a Higher-Level Spell Slot. The number of spheres increases by 1 for every spell slot level above 6."
        ),
        usage_tags=("buff", "damage"),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "0ce1d40de02a6377")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Flavor", "Six chromatic spheres orbit you for the duration."),
                    ("Spheres", "Six"),
                    (
                        "Using",
                        "While the spheres are present, you can expend spheres to create the following effects",
                    ),
                    (
                        "Ends early",
                        "The spell ends early if you have no more spheres remaining",
                    ),
                )
            ),
            Option(
                "Absorb Energy",
                (
                    Facts(
                        (
                            (
                                "Trigger",
                                "You take Acid, Cold, Fire, Lightning, or Thunder damage",
                            ),
                            (
                                "Reaction",
                                "You can take a Reaction to expend one sphere and give yourself Resistance to the triggering damage type until the start of your next turn",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Energy Blast",
                (
                    Facts(
                        (
                            (
                                "Bonus Action",
                                "You send one sphere hurtling toward a target within 120 feet of yourself",
                            ),
                            ("Attack", "Ranged spell attack"),
                            (
                                "On a hit",
                                "The target takes 3d6 Acid, Cold, Fire, Lightning, or Thunder damage (your choice)",
                            ),
                            (
                                "Expended",
                                "Regardless of whether you hit, the sphere is expended",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Spheres", "+1 for every spell slot level above 6"),)),),
            ),
        ]


class Eyebite(ClassSpell):
    rules = SpellRules(
        name="Eyebite",
        level=6,
        school=School.NECROMANCY,
        classes=(
            CharacterClass.BARD,
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "For the duration, your eyes become an inky void. One creature of your choice within 60 feet of you that you can see must succeed on a Wisdom saving throw or be affected by one of the following effects of your choice for the duration.\n"
            "On each of your turns until the spell ends, you can take a Magic action to target another creature but can’t target a creature again if it has succeeded on a save against this casting of the spell.\n"
            "Asleep. The target has the Unconscious condition. It wakes up if it takes any damage or if another creature takes an action to shake it awake.\n"
            "Panicked. The target has the Frightened condition. On each of its turns, the Frightened target must take the Dash action and move away from you by the safest and shortest route available. If the target moves to a space at least 60 feet away from you where it can’t see you, this effect ends.\n"
            "Sickened. The target has the Poisoned condition."
        ),
        usage_tags=("control",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "ff14017af2d9d9b3")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Flavor", "For the duration, your eyes become an inky void."),
                    (
                        "Target",
                        "One creature of your choice within 60 feet of you that you can see",
                    ),
                    ("Save", "Wisdom"),
                    (
                        "Failed save",
                        "The target is affected by one of the following effects of your choice for the duration",
                    ),
                    ("Successful save", "No effect"),
                    (
                        "Each turn",
                        "On each of your turns until the spell ends, you can take a Magic action to target another creature but can't target a creature again if it has succeeded on a save against this casting of the spell",
                    ),
                )
            ),
            Table(
                ("Effect", "Description"),
                (
                    (
                        "Asleep",
                        "The target has the Unconscious condition. It wakes up if it takes any damage or if another creature takes an action to shake it awake",
                    ),
                    (
                        "Panicked",
                        "The target has the Frightened condition. On each of its turns, the Frightened target must take the Dash action and move away from you by the safest and shortest route available. If the target moves to a space at least 60 feet away from you where it can't see you, this effect ends",
                    ),
                    ("Sickened", "The target has the Poisoned condition"),
                ),
            ),
        ]


class FindThePath(ClassSpell):
    rules = SpellRules(
        name="Find the Path",
        level=6,
        school=School.DIVINATION,
        classes=(CharacterClass.BARD, CharacterClass.CLERIC, CharacterClass.DRUID),
        casting_time=CastingTime(CastingTimeType.MINUTE, 1),
        range=Range(RangeType.SELF),
        components=Components(
            verbal=True,
            somatic=True,
            material="a set of divination tools - such as cards or runes - worth 100+ GP",
        ),
        duration=Duration(DurationType.DAY, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "You magically sense the most direct physical route to a location you name. You must be familiar with the location, and the spell fails if you name a destination on another plane of existence, a moving destination (such as a mobile fortress), or an unspecific destination (such as “a green dragon’s lair”).\n"
            "For the duration, as long as you are on the same plane of existence as the destination, you know how far it is and in what direction it lies. Whenever you face a choice of paths along the way there, you know which path is the most direct."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "c00354e2a9351299")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Destination",
                        "You magically sense the most direct physical route to a location you name",
                    ),
                    ("Requirement", "You must be familiar with the location"),
                    (
                        "Fails",
                        'The spell fails if you name a destination on another plane of existence, a moving destination (such as a mobile fortress), or an unspecific destination (such as "a green dragon\'s lair")',
                    ),
                    (
                        "Knowing",
                        "For the duration, as long as you are on the same plane of existence as the destination, you know how far it is and in what direction it lies",
                    ),
                    (
                        "Paths",
                        "Whenever you face a choice of paths along the way there, you know which path is the most direct",
                    ),
                )
            )
        ]


class FizbansPlatinumShield(ClassSpell):
    rules = SpellRules(
        name="Fizban's Platinum Shield",
        level=6,
        school=School.ABJURATION,
        classes=(CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.BONUS_ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(
            verbal=True,
            somatic=True,
            material="a platinum-plated dragon scale, worth at least 500 gp",
        ),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Fizban's Treasury of Dragons",
        description=(
            "You create a field of silvery light that surrounds a creature of your choice within range (you can choose yourself). The field sheds dim light out to 5 feet. While surrounded by the field, a creature gains the following benefits:\n"
            "Cover. The creature has half cover.\n"
            "Damage Resistance. The creature has resistance to acid, cold, fire, lightning, and poison damage.\n"
            "Evasion. If the creature is subjected to an effect that allows it to make a Dexterity saving throw to take only half damage, the creature instead takes no damage if it succeeds on the saving throw, and only half damage if it fails.\n"
            "As a bonus action on subsequent turns, you can move the field to another creature within 60 feet of the field."
        ),
        usage_tags=("buff", "damage", "utility"),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "57b88d0fd7d12630")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You create a field of silvery light that surrounds a creature of your choice within range (you can choose yourself).",
                    ),
                    (
                        "Target",
                        "A creature of your choice within range (you can choose yourself)",
                    ),
                    ("Light", "The field sheds dim light out to 5 feet"),
                    (
                        "Benefits",
                        "While surrounded by the field, a creature gains the following benefits",
                    ),
                    ("Cover", "The creature has half cover"),
                    (
                        "Resistance",
                        "The creature has resistance to Acid, Cold, Fire, Lightning, and Poison damage",
                    ),
                    (
                        "Evasion",
                        "If the creature is subjected to an effect that allows it to make a Dexterity saving throw to take only half damage, the creature instead takes no damage if it succeeds on the saving throw, and only half damage if it fails",
                    ),
                    (
                        "Moving it",
                        "As a bonus action on subsequent turns, you can move the field to another creature within 60 feet of the field",
                    ),
                )
            )
        ]


class FleshToStone(ClassSpell):
    rules = SpellRules(
        name="Flesh to Stone",
        level=6,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.DRUID, CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(
            verbal=True, somatic=True, material="a cockatrice feather"
        ),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "You attempt to turn one creature that you can see within range into stone. The target makes a Constitution saving throw. On a failed save, it has the Restrained condition for the duration. On a successful save, its Speed is 0 until the start of your next turn. Constructs automatically succeed on the save.\n"
            "A Restrained target makes another Constitution saving throw at the end of each of its turns. If it successfully saves against this spell three times, the spell ends. If it fails its saves three times, it is turned to stone and has the Petrified condition for the duration. The successes and failures needn’t be consecutive; keep track of both until the target collects three of a kind.\n"
            "If you maintain your Concentration on this spell for the entire possible duration, the target is Petrified until the condition is ended by Greater Restoration or similar magic."
        ),
        usage_tags=("control", "heal"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "34415f07d9422506")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Target",
                        "One creature that you can see within range; you attempt to turn it into stone",
                    ),
                    ("Save", "Constitution"),
                    (
                        "Failed save",
                        "The target has the Restrained condition for the duration",
                    ),
                    (
                        "Successful save",
                        "The target's Speed is 0 until the start of your next turn",
                    ),
                    ("Constructs", "Constructs automatically succeed on the save"),
                    (
                        "Repeat save",
                        "Constitution, made by a Restrained target at the end of each of its turns",
                    ),
                )
            ),
            Option(
                "Three of a Kind",
                (
                    Facts(
                        (
                            (
                                "Successes",
                                "If it successfully saves against this spell three times, the spell ends",
                            ),
                            (
                                "Failures",
                                "If it fails its saves three times, it is turned to stone and has the Petrified condition for the duration",
                            ),
                            (
                                "Tracking",
                                "The successes and failures needn't be consecutive; keep track of both until the target collects three of a kind",
                            ),
                        )
                    ),
                ),
            ),
            Facts(
                (
                    (
                        "Permanent",
                        "If you maintain your Concentration on this spell for the entire possible duration, the target is Petrified until the condition is ended by Greater Restoration or similar magic",
                    ),
                )
            ),
        ]


class Forbiddance(ClassSpell):
    rules = SpellRules(
        name="Forbiddance",
        level=6,
        school=School.ABJURATION,
        classes=(CharacterClass.CLERIC,),
        casting_time=CastingTime(CastingTimeType.MINUTE, 10, ritual=True),
        range=Range(RangeType.TOUCH),
        components=Components(
            verbal=True, somatic=True, material="ruby dust worth 1,000+ GP"
        ),
        duration=Duration(DurationType.DAY, 1),
        source="Player's Handbook",
        description=(
            "You create a ward against magical travel that protects up to 40,000 square feet of floor space to a height of 30 feet above the floor. For the duration, creatures can’t teleport into the area or use portals, such as those created by the Gate spell, to enter the area. The spell proofs the area against planar travel, and therefore prevents creatures from accessing the area by way of the Astral Plane, the Ethereal Plane, the Feywild, the Shadowfell, or the Plane Shift spell.\n"
            "In addition, the spell damages types of creatures that you choose when you cast it. Choose one or more of the following: Aberrations, Celestials, Elementals, Fey, Fiends, and Undead. When a creature of a chosen type enters the spell’s area for the first time on a turn or ends its turn there, the creature takes 5d10 Radiant or Necrotic damage (your choice when you cast this spell).\n"
            "You can designate a password when you cast the spell. A creature that speaks the password as it enters the area takes no damage from the spell.\n"
            "The spell’s area can’t overlap with the area of another Forbiddance spell. If you cast Forbiddance every day for 30 days in the same location, the spell lasts until it is dispelled, and the Material components are consumed on the last casting."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "a455ec99d0607ac2")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Area",
                        "A ward against magical travel that protects up to 40,000 square feet of floor space to a height of 30 feet above the floor",
                    ),
                    (
                        "Teleporting",
                        "For the duration, creatures can't teleport into the area or use portals, such as those created by the Gate spell, to enter the area",
                    ),
                    (
                        "Planar travel",
                        "The spell proofs the area against planar travel, and therefore prevents creatures from accessing the area by way of the Astral Plane, the Ethereal Plane, the Feywild, the Shadowfell, or the Plane Shift spell",
                    ),
                    (
                        "Overlap",
                        "The spell's area can't overlap with the area of another Forbiddance spell",
                    ),
                    (
                        "Permanent",
                        "If you cast Forbiddance every day for 30 days in the same location, the spell lasts until it is dispelled, and the Material components are consumed on the last casting",
                    ),
                )
            ),
            Option(
                "Damaging Creatures",
                (
                    Facts(
                        (
                            (
                                "Types",
                                "In addition, the spell damages types of creatures that you choose when you cast it. Choose one or more of the following: Aberrations, Celestials, Elementals, Fey, Fiends, and Undead",
                            ),
                            (
                                "Trigger",
                                "A creature of a chosen type enters the spell's area for the first time on a turn or ends its turn there",
                            ),
                            (
                                "Damage",
                                "The creature takes 5d10 Radiant or Necrotic damage (your choice when you cast this spell)",
                            ),
                            (
                                "Password",
                                "You can designate a password when you cast the spell",
                            ),
                            (
                                "Speaking it",
                                "A creature that speaks the password as it enters the area takes no damage from the spell",
                            ),
                        )
                    ),
                ),
            ),
        ]


class GlobeOfInvulnerability(ClassSpell):
    rules = SpellRules(
        name="Globe of Invulnerability",
        level=6,
        school=School.ABJURATION,
        classes=(CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True, material="a glass bead"),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "An immobile, shimmering barrier appears in a 10-foot Emanation around you and remains for the duration.\n"
            "Any spell of level 5 or lower cast from outside the barrier can’t affect anything within it. Such a spell can target creatures and objects within the barrier, but the spell has no effect on them. Similarly, the area within the barrier is excluded from areas of effect created by such spells.\n"
            "Using a Higher-Level Spell Slot. The barrier blocks spells of 1 level higher for each spell slot level above 6."
        ),
        usage_tags=("buff",),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "e59062ef3d72f3d8")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Barrier",
                        "An immobile, shimmering barrier appears in a 10-foot Emanation around you and remains for the duration",
                    ),
                    (
                        "Spells",
                        "Any spell of level 5 or lower cast from outside the barrier can't affect anything within it",
                    ),
                    (
                        "Targeting",
                        "Such a spell can target creatures and objects within the barrier, but the spell has no effect on them",
                    ),
                    (
                        "Areas",
                        "Similarly, the area within the barrier is excluded from areas of effect created by such spells",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (
                    Facts(
                        (
                            (
                                "Blocked spells",
                                "The barrier blocks spells of 1 level higher for each spell slot level above 6",
                            ),
                        )
                    ),
                ),
            ),
        ]


class GuardsAndWards(ClassSpell):
    rules = SpellRules(
        name="Guards and Wards",
        level=6,
        school=School.ABJURATION,
        classes=(CharacterClass.BARD, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.HOUR, 1),
        range=Range(RangeType.TOUCH),
        components=Components(
            verbal=True, somatic=True, material="a silver rod worth 10+ GP"
        ),
        duration=Duration(DurationType.HOUR, 24),
        source="Player's Handbook",
        description=(
            "You create a ward that protects up to 2,500 square feet of floor space. The warded area can be up to 20 feet tall, and you shape it as one 50-foot square, one hundred 5-foot squares that are contiguous, or twenty-five 10-foot squares that are contiguous.\n"
            "When you cast this spell, you can specify individuals that are unaffected by the spell’s effects. You can also specify a password that, when spoken aloud within 5 feet of the warded area, makes the speaker immune to its effects.\n"
            "The spell creates the effects below within the warded area. Dispel Magic has no effect on Guards and Wards itself, but each of the following effects can be dispelled. If all four are dispelled, Guards and Wards ends. If you cast the spell every day for 365 days on the same area, the spell thereafter lasts until all its effects are dispelled.\n"
            "Corridors. Fog fills all the warded corridors, making them Heavily Obscured. In addition, at each intersection or branching passage offering a choice of direction, there is a 50 percent chance that a creature other than you believes it is going in the opposite direction from the one it chooses.\n"
            "Doors. All doors in the warded area are magically locked, as if sealed by the Arcane Lock spell. In addition, you can cover up to ten doors with an illusion to make them appear as plain sections of wall.\n"
            "Stairs. Webs fill all stairs in the warded area from top to bottom, as in the Web spell. These strands regrow in 10 minutes if they are destroyed while Guards and Wards lasts.\n"
            "Other Spell Effect. Place one of the following magical effects within the warded area:\n"
            "Dancing Lights in four corridors, with a simple program that the lights repeat as long as Guards and Wards lasts\n"
            "Magic Mouth in two locations\n"
            "Stinking Cloud in two locations (the vapors return within 10 minutes if dispersed while Guards and Wards lasts)\n"
            "Gust of Wind in one corridor or room (the wind blows continuously while the spell lasts)\n"
            "Suggestion in one 5-foot square; any creature that enters that square receives the suggestion mentally"
        ),
        usage_tags=("control",),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "713dd85dfc0c9053")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Ward",
                        "You create a ward that protects up to 2,500 square feet of floor space",
                    ),
                    ("Height", "The warded area can be up to 20 feet tall"),
                    (
                        "Shape",
                        "You shape it as one 50-foot square, one hundred 5-foot squares that are contiguous, or twenty-five 10-foot squares that are contiguous",
                    ),
                    (
                        "Unaffected",
                        "When you cast this spell, you can specify individuals that are unaffected by the spell's effects",
                    ),
                    (
                        "Password",
                        "You can also specify a password that, when spoken aloud within 5 feet of the warded area, makes the speaker immune to its effects",
                    ),
                    (
                        "Effects",
                        "The spell creates the effects below within the warded area",
                    ),
                    (
                        "Dispelling",
                        "Dispel Magic has no effect on Guards and Wards itself, but each of the following effects can be dispelled. If all four are dispelled, Guards and Wards ends",
                    ),
                    (
                        "Permanent",
                        "If you cast the spell every day for 365 days on the same area, the spell thereafter lasts until all its effects are dispelled",
                    ),
                )
            ),
            Option(
                "Corridors",
                (
                    Facts(
                        (
                            (
                                "Fog",
                                "Fog fills all the warded corridors, making them Heavily Obscured",
                            ),
                            (
                                "Intersections",
                                "In addition, at each intersection or branching passage offering a choice of direction, there is a 50 percent chance that a creature other than you believes it is going in the opposite direction from the one it chooses",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Doors",
                (
                    Facts(
                        (
                            (
                                "Locked",
                                "All doors in the warded area are magically locked, as if sealed by the Arcane Lock spell",
                            ),
                            (
                                "Disguised",
                                "In addition, you can cover up to ten doors with an illusion to make them appear as plain sections of wall",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Stairs",
                (
                    Facts(
                        (
                            (
                                "Webs",
                                "Webs fill all stairs in the warded area from top to bottom, as in the Web spell",
                            ),
                            (
                                "Regrowing",
                                "These strands regrow in 10 minutes if they are destroyed while Guards and Wards lasts",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Other Spell Effect",
                (
                    Facts(
                        (
                            (
                                "Choose one",
                                "Place one of the following magical effects within the warded area",
                            ),
                        )
                    ),
                    Table(
                        ("Effect", "Placement"),
                        (
                            (
                                "Dancing Lights",
                                "In four corridors, with a simple program that the lights repeat as long as Guards and Wards lasts",
                            ),
                            ("Magic Mouth", "In two locations"),
                            (
                                "Stinking Cloud",
                                "In two locations (the vapors return within 10 minutes if dispersed while Guards and Wards lasts)",
                            ),
                            (
                                "Gust of Wind",
                                "In one corridor or room (the wind blows continuously while the spell lasts)",
                            ),
                            (
                                "Suggestion",
                                "In one 5-foot square; any creature that enters that square receives the suggestion mentally",
                            ),
                        ),
                    ),
                ),
            ),
        ]


class Harm(ClassSpell):
    rules = SpellRules(
        name="Harm",
        level=6,
        school=School.NECROMANCY,
        classes=(CharacterClass.CLERIC,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description="You unleash virulent magic on a creature you can see within range. The target makes a Constitution saving throw. On a failed save, it takes 14d6 Necrotic damage, and its Hit Point maximum is reduced by an amount equal to the Necrotic damage it took. On a successful save, it takes half as much damage only. This spell can’t reduce a target’s Hit Point maximum below 1.",
        usage_tags=("damage",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "b5d7f8a7010205f6")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You unleash virulent magic on a creature you can see within range.",
                    ),
                    ("Target", "A creature you can see within range"),
                    ("Save", "Constitution"),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (
                    (
                        "14d6 Necrotic damage, and its Hit Point maximum is reduced by an amount equal to the Necrotic damage it took",
                        "Half as much damage only",
                    ),
                ),
            ),
            Facts(
                (
                    (
                        "Minimum",
                        "This spell can't reduce a target's Hit Point maximum below 1",
                    ),
                )
            ),
        ]


class Heal(ClassSpell):
    rules = SpellRules(
        name="Heal",
        level=6,
        school=School.ABJURATION,
        classes=(CharacterClass.CLERIC, CharacterClass.DRUID),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "Choose a creature that you can see within range. Positive energy washes through the target, restoring 70 Hit Points. This spell also ends the Blinded, Deafened, and Poisoned conditions on the target.\n"
            "Using a Higher-Level Spell Slot. The healing increases by 10 for each spell slot level above 6."
        ),
        usage_tags=("heal",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "23a06eca102842d8")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Flavor", "Positive energy washes through the target."),
                    ("Target", "A creature that you can see within range"),
                    ("Healing", "70 Hit Points"),
                    (
                        "Conditions ended",
                        "This spell also ends the Blinded, Deafened, and Poisoned conditions on the target",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Healing", "+10 for each spell slot level above 6"),)),),
            ),
        ]


class HeroesFeast(ClassSpell):
    rules = SpellRules(
        name="Heroes' Feast",
        level=6,
        school=School.CONJURATION,
        classes=(CharacterClass.BARD, CharacterClass.CLERIC, CharacterClass.DRUID),
        casting_time=CastingTime(CastingTimeType.MINUTE, 10),
        range=Range(RangeType.SELF),
        components=Components(
            verbal=True,
            somatic=True,
            material="a gem-encrusted bowl worth 1,000+ GP, which the spell consumes",
        ),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "You conjure a feast that appears on a surface in an unoccupied 10-foot Cube next to you. The feast takes 1 hour to consume and disappears at the end of that time, and the beneficial effects don’t set in until this hour is over. Up to twelve creatures can partake of the feast.\n"
            "A creature that partakes gains several benefits, which last for 24 hours. The creature has Resistance to Poison damage, and it has Immunity to the Frightened and Poisoned conditions. Its Hit Point maximum also increases by 2d10, and it gains the same number of Hit Points."
        ),
        usage_tags=("buff", "damage", "heal"),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "f3fcf9f13c46f3ba")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Feast",
                        "You conjure a feast that appears on a surface in an unoccupied 10-foot Cube next to you",
                    ),
                    (
                        "Consuming",
                        "The feast takes 1 hour to consume and disappears at the end of that time, and the beneficial effects don't set in until this hour is over",
                    ),
                    ("Partakers", "Up to twelve creatures can partake of the feast"),
                    (
                        "Benefits",
                        "A creature that partakes gains several benefits, which last for 24 hours",
                    ),
                    (
                        "Defenses",
                        "The creature has Resistance to Poison damage, and it has Immunity to the Frightened and Poisoned conditions",
                    ),
                    (
                        "Hit Points",
                        "Its Hit Point maximum also increases by 2d10, and it gains the same number of Hit Points",
                    ),
                )
            )
        ]


class InvestitureOfFlame(ClassSpell):
    rules = SpellRules(
        name="Investiture of Flame",
        level=6,
        school=School.TRANSMUTATION,
        classes=(
            CharacterClass.DRUID,
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 10, concentration=True),
        source="Xanathar's Guide to Everything",
        description=(
            "Flames race across your body, shedding bright light in a 30-foot radius and dim light for an additional 30 feet for the spell's duration. The flames don't harm you. Until the spell ends, you gain the following benefits:\n"
            "You are immune to fire damage and have resistance to cold damage.\n"
            "Any creature that moves within 5 feet of you for the first time on a turn or ends its turn there takes 1d10 fire damage.\n"
            "You can use your action to create a line of fire 15 feet long and 5 feet wide extending from you in a direction you choose. Each creature in the line must make a Dexterity saving throw. A creature takes 4d8 fire damage on a failed save, or half as much damage on a successful one."
        ),
        usage_tags=("buff", "damage", "utility"),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "fce3aa5cdfeee871")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Flavor", "Flames race across your body."),
                    (
                        "Light",
                        "The flames shed bright light in a 30-foot radius and dim light for an additional 30 feet for the spell's duration",
                    ),
                    ("Harmless", "The flames don't harm you"),
                    (
                        "Benefits",
                        "Until the spell ends, you gain the following benefits",
                    ),
                    (
                        "Resistances",
                        "You are immune to Fire damage and have resistance to Cold damage",
                    ),
                    (
                        "Aura",
                        "Any creature that moves within 5 feet of you for the first time on a turn or ends its turn there takes 1d10 Fire damage",
                    ),
                )
            ),
            Option(
                "Line of Fire",
                (
                    Facts(
                        (
                            (
                                "Use",
                                "You can use your action to create a line of fire 15 feet long and 5 feet wide extending from you in a direction you choose",
                            ),
                            ("Save", "Dexterity, made by each creature in the line"),
                        )
                    ),
                    Table(
                        ("Failed save", "Successful save"),
                        (("4d8 Fire damage", "Half as much damage"),),
                    ),
                ),
            ),
        ]


class InvestitureOfIce(ClassSpell):
    rules = SpellRules(
        name="Investiture of Ice",
        level=6,
        school=School.TRANSMUTATION,
        classes=(
            CharacterClass.DRUID,
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 10, concentration=True),
        source="Xanathar's Guide to Everything",
        description=(
            "Until the spell ends, ice rimes your body, and you gain the following benefits:\n"
            "You are immune to cold damage and have resistance to fire damage.\n"
            "You can move across difficult terrain created by ice or snow without spending extra movement.\n"
            "The ground in a 10-foot radius around you is icy and is difficult terrain for creatures other than you. The radius moves with you.\n"
            "You can use your action to create a 15-foot cone of freezing wind extending from your outstretched hand in a direction you choose. Each creature in the cone must make a Constitution saving throw. A creature takes 4d6 cold damage on a failed save, or half as much damage on a successful one. A creature that fails its save against this effect has its speed halved until the start of your next turn."
        ),
        usage_tags=("buff", "control", "damage", "utility"),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "cd5f3dba00842302")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Flavor", "Ice rimes your body."),
                    (
                        "Benefits",
                        "Until the spell ends, you gain the following benefits",
                    ),
                    (
                        "Resistances",
                        "You are immune to Cold damage and have resistance to Fire damage",
                    ),
                    (
                        "Movement",
                        "You can move across difficult terrain created by ice or snow without spending extra movement",
                    ),
                    (
                        "Ground",
                        "The ground in a 10-foot radius around you is icy and is difficult terrain for creatures other than you. The radius moves with you",
                    ),
                )
            ),
            Option(
                "Freezing Wind",
                (
                    Facts(
                        (
                            (
                                "Use",
                                "You can use your action to create a 15-foot cone of freezing wind extending from your outstretched hand in a direction you choose",
                            ),
                            ("Save", "Constitution, made by each creature in the cone"),
                        )
                    ),
                    Table(
                        ("Failed save", "Successful save"),
                        (
                            (
                                "4d6 Cold damage, and its speed is halved until the start of your next turn",
                                "Half as much damage",
                            ),
                        ),
                    ),
                ),
            ),
        ]


class InvestitureOfStone(ClassSpell):
    rules = SpellRules(
        name="Investiture of Stone",
        level=6,
        school=School.TRANSMUTATION,
        classes=(
            CharacterClass.DRUID,
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 10, concentration=True),
        source="Xanathar's Guide to Everything",
        description=(
            "Until the spell ends, bits of rock spread across your body, and you gain the following benefits:\n"
            "You have resistance to bludgeoning, piercing, and slashing damage from nonmagical weapons.\n"
            "You can use your action to create a small earthquake on the ground in a 15-foot radius centered on you. Other creatures on that ground must succeed on a Dexterity saving throw or be knocked prone.\n"
            "You can move across difficult terrain made of earth or stone without spending extra movement. You can move through solid earth or stone as if it was air and without destabilizing it, but you can't end your movement there. If you do so, you are ejected to the nearest unoccupied space, this spell ends, and you are stunned until the end of your next turn."
        ),
        usage_tags=("buff", "control", "utility"),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "c622ef44d2086ddd")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Flavor", "Bits of rock spread across your body."),
                    (
                        "Benefits",
                        "Until the spell ends, you gain the following benefits",
                    ),
                    (
                        "Resistance",
                        "You have resistance to Bludgeoning, Piercing, and Slashing damage from nonmagical weapons",
                    ),
                    (
                        "Movement",
                        "You can move across difficult terrain made of earth or stone without spending extra movement",
                    ),
                    (
                        "Burrowing",
                        "You can move through solid earth or stone as if it was air and without destabilizing it, but you can't end your movement there",
                    ),
                    (
                        "Ejected",
                        "If you do so, you are ejected to the nearest unoccupied space, this spell ends, and you are Stunned until the end of your next turn",
                    ),
                )
            ),
            Option(
                "Earthquake",
                (
                    Facts(
                        (
                            (
                                "Use",
                                "You can use your action to create a small earthquake on the ground in a 15-foot radius centered on you",
                            ),
                            ("Targets", "Other creatures on that ground"),
                            ("Save", "Dexterity"),
                            ("Failed save", "The creature is knocked Prone"),
                            ("Successful save", "No effect"),
                        )
                    ),
                ),
            ),
        ]


class InvestitureOfWind(ClassSpell):
    rules = SpellRules(
        name="Investiture of Wind",
        level=6,
        school=School.TRANSMUTATION,
        classes=(
            CharacterClass.DRUID,
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 10, concentration=True),
        source="Xanathar's Guide to Everything",
        description=(
            "Until the spell ends, wind whirls around you, and you gain the following benefits:\n"
            "Ranged weapon attacks made against you have disadvantage on the attack roll.\n"
            "You gain a flying speed of 60 feet. If you are still flying when the spell ends, you fall, unless you can somehow prevent it.\n"
            "You can use your action to create a 15-foot cube of swirling wind centered on a point you can see within 60 feet of you. Each creature in that area must make a Constitution saving throw. A creature takes 2d10 bludgeoning damage on a failed save, or half as much damage on a successful one. If a Large or smaller creature fails the save, that creature is also pushed up to 10 feet away from the center of the cube."
        ),
        usage_tags=("buff", "damage", "utility"),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "b016f7447b9d5604")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Flavor", "Wind whirls around you."),
                    (
                        "Benefits",
                        "Until the spell ends, you gain the following benefits",
                    ),
                    (
                        "Defense",
                        "Ranged weapon attacks made against you have Disadvantage on the attack roll",
                    ),
                    ("Flying", "You gain a flying speed of 60 feet"),
                    (
                        "Falling",
                        "If you are still flying when the spell ends, you fall, unless you can somehow prevent it",
                    ),
                )
            ),
            Option(
                "Swirling Wind",
                (
                    Facts(
                        (
                            (
                                "Use",
                                "You can use your action to create a 15-foot cube of swirling wind centered on a point you can see within 60 feet of you",
                            ),
                            (
                                "Save",
                                "Constitution, made by each creature in that area",
                            ),
                        )
                    ),
                    Table(
                        ("Failed save", "Successful save"),
                        (
                            (
                                "2d10 Bludgeoning damage, and a Large or smaller creature is also pushed up to 10 feet away from the center of the cube",
                                "Half as much damage",
                            ),
                        ),
                    ),
                ),
            ),
        ]


class LeomundsLamentableBelaborment(ClassSpell):
    rules = SpellRules(
        name="Leomund's Lamentable Belaborment",
        level=6,
        school=School.ENCHANTMENT,
        classes=(CharacterClass.BARD, CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 30),
        components=Components(verbal=True),
        duration=Duration(DurationType.MINUTE, 1),
        source="D&D Beyond Drops - May 2026",
        description=(
            "You proclaim an insightful or inflammatory statement, such as a claim about the politics of a nearby town. Each creature in a 10-foot-radius Sphere centered on a point you choose within range must succeed on an Intelligence saving throw or have the Charmed condition until the spell ends. Any creature that doesn’t share a language with you or that has an Intelligence score lower than 3 automatically succeeds on the saving throw.\n"
            "While Charmed, a target must spend its turn discussing or arguing for or against your statement. For the duration, the target has a Speed of 0 and has the Blinded and Deafened conditions with respect to everyone except you and other targets affected by this spell.\n"
            "At the end of each of its turns, the target repeats the save, ending the spell on itself on a success."
        ),
        usage_tags=("control",),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "2cd924072240323c")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You proclaim an insightful or inflammatory statement, such as a claim about the politics of a nearby town.",
                    ),
                    (
                        "Area",
                        "10-foot-radius Sphere centered on a point you choose within range",
                    ),
                    ("Save", "Intelligence, made by each creature in the Sphere"),
                    (
                        "Failed save",
                        "The creature has the Charmed condition until the spell ends",
                    ),
                    ("Successful save", "No effect"),
                    (
                        "Automatic",
                        "Any creature that doesn't share a language with you or that has an Intelligence score lower than 3 automatically succeeds on the saving throw",
                    ),
                    (
                        "While Charmed",
                        "A target must spend its turn discussing or arguing for or against your statement",
                    ),
                    (
                        "Senses",
                        "For the duration, the target has a Speed of 0 and has the Blinded and Deafened conditions with respect to everyone except you and other targets affected by this spell",
                    ),
                    (
                        "Repeat save",
                        "At the end of each of its turns, the target repeats the save, ending the spell on itself on a success",
                    ),
                )
            )
        ]


class MagicJar(ClassSpell):
    rules = SpellRules(
        name="Magic Jar",
        level=6,
        school=School.NECROMANCY,
        classes=(CharacterClass.WIZARD,),
        casting_time=CastingTime(CastingTimeType.MINUTE, 1),
        range=Range(RangeType.SELF),
        components=Components(
            verbal=True,
            somatic=True,
            material="a gem, crystal, or reliquary worth 500+ GP",
        ),
        duration=Duration(DurationType.UNTIL_DISPELLED),
        source="Player's Handbook",
        description=(
            "Your body falls into a catatonic state as your soul leaves it and enters the container you used for the spell’s Material component. While your soul inhabits the container, you are aware of your surroundings as if you were in the container’s space. You can’t move or take Reactions. The only action you can take is to project your soul up to 100 feet out of the container, either returning to your living body (and ending the spell) or attempting to possess a Humanoid’s body.\n"
            "You can attempt to possess any Humanoid within 100 feet of you that you can see (creatures warded by a Protection from Evil and Good or Magic Circle spell can’t be possessed). The target makes a Charisma saving throw. On a failed save, your soul enters the target’s body, and the target’s soul becomes trapped in the container. On a successful save, the target resists your efforts to possess it, and you can’t attempt to possess it again for 24 hours.\n"
            "Once you possess a creature’s body, you control it. Your Hit Points, Hit Point Dice, Strength, Dexterity, Constitution, Speed, and senses are replaced by the creature’s. You otherwise keep your game statistics.\n"
            "Meanwhile, the possessed creature’s soul can perceive from the container using its own senses, but it can’t move and it is Incapacitated.\n"
            "While possessing a body, you can take a Magic action to return from the host body to the container if it is within 100 feet of you, returning the host creature’s soul to its body. If the host body dies while you’re in it, the creature dies, and you make a Charisma saving throw against your own spellcasting DC. On a success, you return to the container if it is within 100 feet of you. Otherwise, you die.\n"
            "If the container is destroyed or the spell ends, your soul returns to your body. If your body is more than 100 feet away from you or if your body is dead, you die. If another creature’s soul is in the container when it is destroyed, the creature’s soul returns to its body if the body is alive and within 100 feet. Otherwise, that creature dies.\n"
            "When the spell ends, the container is destroyed."
        ),
        usage_tags=("buff",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "f287cf10901f17b5")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Soul",
                        "Your body falls into a catatonic state as your soul leaves it and enters the container you used for the spell's Material component",
                    ),
                    (
                        "Aware",
                        "While your soul inhabits the container, you are aware of your surroundings as if you were in the container's space",
                    ),
                    ("Limits", "You can't move or take Reactions"),
                    (
                        "Action",
                        "The only action you can take is to project your soul up to 100 feet out of the container, either returning to your living body (and ending the spell) or attempting to possess a Humanoid's body",
                    ),
                )
            ),
            Option(
                "Possessing a Body",
                (
                    Facts(
                        (
                            (
                                "Target",
                                "You can attempt to possess any Humanoid within 100 feet of you that you can see (creatures warded by a Protection from Evil and Good or Magic Circle spell can't be possessed)",
                            ),
                            ("Save", "Charisma"),
                            (
                                "Failed save",
                                "Your soul enters the target's body, and the target's soul becomes trapped in the container",
                            ),
                            (
                                "Successful save",
                                "The target resists your efforts to possess it, and you can't attempt to possess it again for 24 hours",
                            ),
                            (
                                "Control",
                                "Once you possess a creature's body, you control it",
                            ),
                            (
                                "Statistics",
                                "Your Hit Points, Hit Point Dice, Strength, Dexterity, Constitution, Speed, and senses are replaced by the creature's. You otherwise keep your game statistics",
                            ),
                            (
                                "Its soul",
                                "Meanwhile, the possessed creature's soul can perceive from the container using its own senses, but it can't move and it is Incapacitated",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Leaving the Body",
                (
                    Facts(
                        (
                            (
                                "Returning",
                                "While possessing a body, you can take a Magic action to return from the host body to the container if it is within 100 feet of you, returning the host creature's soul to its body",
                            ),
                            (
                                "Host dies",
                                "If the host body dies while you're in it, the creature dies, and you make a Charisma saving throw against your own spellcasting DC",
                            ),
                            (
                                "Result",
                                "On a success, you return to the container if it is within 100 feet of you. Otherwise, you die",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Ending the Spell",
                (
                    Facts(
                        (
                            (
                                "Your soul",
                                "If the container is destroyed or the spell ends, your soul returns to your body. If your body is more than 100 feet away from you or if your body is dead, you die",
                            ),
                            (
                                "Another soul",
                                "If another creature's soul is in the container when it is destroyed, the creature's soul returns to its body if the body is alive and within 100 feet. Otherwise, that creature dies",
                            ),
                            (
                                "Container",
                                "When the spell ends, the container is destroyed",
                            ),
                        )
                    ),
                ),
            ),
        ]


class MassSuggestion(ClassSpell):
    rules = SpellRules(
        name="Mass Suggestion",
        level=6,
        school=School.ENCHANTMENT,
        classes=(CharacterClass.BARD, CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True, material="a snake’s tongue"),
        duration=Duration(DurationType.HOUR, 24),
        source="Player's Handbook",
        description=(
            "You suggest a course of activity—described in no more than 25 words—to twelve or fewer creatures you can see within range that can hear and understand you. The suggestion must sound achievable and not involve anything that would obviously deal damage to any of the targets or their allies. For example, you could say, “Walk to the village down that road, and help the villagers there harvest crops until sunset.” Or you could say, “Now is not the time for violence. Drop your weapons, and dance! Stop in an hour.”\n"
            "Each target must succeed on a Wisdom saving throw or have the Charmed condition for the duration or until you or your allies deal damage to the target. Each Charmed target pursues the suggestion to the best of its ability. The suggested activity can continue for the entire duration, but if the suggested activity can be completed in a shorter time, the spell ends for a target upon completing it.\n"
            "Using a Higher-Level Spell Slot. The duration is longer with a spell slot of level 7 (10 days), 8 (30 days), or 9 (366 days)."
        ),
        usage_tags=("control",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "e5e3b7890cf6ab54")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Targets",
                        "Twelve or fewer creatures you can see within range that can hear and understand you",
                    ),
                    (
                        "Suggestion",
                        "You suggest a course of activity—described in no more than 25 words",
                    ),
                    (
                        "Limits",
                        "The suggestion must sound achievable and not involve anything that would obviously deal damage to any of the targets or their allies",
                    ),
                    (
                        "Example",
                        'You could say, "Walk to the village down that road, and help the villagers there harvest crops until sunset."',
                    ),
                    (
                        "Another example",
                        'Or you could say, "Now is not the time for violence. Drop your weapons, and dance! Stop in an hour."',
                    ),
                    ("Save", "Wisdom, made by each target"),
                    (
                        "Failed save",
                        "The target has the Charmed condition for the duration or until you or your allies deal damage to the target",
                    ),
                    ("Successful save", "No effect"),
                    (
                        "Pursuit",
                        "Each Charmed target pursues the suggestion to the best of its ability",
                    ),
                    (
                        "Activity",
                        "The suggested activity can continue for the entire duration, but if the suggested activity can be completed in a shorter time, the spell ends for a target upon completing it",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (
                    Table(
                        ("Slot level", "Duration"),
                        (("7", "10 days"), ("8", "30 days"), ("9", "366 days")),
                    ),
                ),
            ),
        ]


class MentalPrison(ClassSpell):
    rules = SpellRules(
        name="Mental Prison",
        level=6,
        school=School.ILLUSION,
        classes=(
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(somatic=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Xanathar's Guide to Everything",
        description="You attempt to bind a creature within an illusory cell that only it perceives. One creature you can see within range must make an Intelligence saving throw. The target succeeds automatically if it is immune to being charmed. On a successful save, the target takes 5d10 psychic damage, and the spell ends. On a failed save, the target takes 5d10 psychic damage, and you make the area immediately around the target's space appear dangerous to it in some way. You might cause the target to perceive itself as being surrounded by fire, floating razors, or hideous maws filled with dripping teeth. Whatever form the illusion takes, the target can't see or hear anything beyond it and is restrained for the spell's duration. If the target is moved out of the illusion, makes a melee attack through it, or reaches any part of its body through it, the target takes 10d10 psychic damage, and the spell ends.",
        usage_tags=("control", "damage", "utility"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "bfd48d2bb68e387d")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You attempt to bind a creature within an illusory cell that only it perceives.",
                    ),
                    ("Target", "One creature you can see within range"),
                    ("Save", "Intelligence"),
                    (
                        "Automatic",
                        "The target succeeds automatically if it is immune to being Charmed",
                    ),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (
                    (
                        "5d10 Psychic damage, and you make the area immediately around the target's space appear dangerous to it in some way",
                        "5d10 Psychic damage, and the spell ends",
                    ),
                ),
            ),
            Option(
                "The Illusion",
                (
                    Facts(
                        (
                            (
                                "Examples",
                                "You might cause the target to perceive itself as being surrounded by fire, floating razors, or hideous maws filled with dripping teeth",
                            ),
                            (
                                "Effect",
                                "Whatever form the illusion takes, the target can't see or hear anything beyond it and is Restrained for the spell's duration",
                            ),
                            (
                                "Breaking it",
                                "If the target is moved out of the illusion, makes a melee attack through it, or reaches any part of its body through it, the target takes 10d10 Psychic damage, and the spell ends",
                            ),
                        )
                    ),
                ),
            ),
        ]


class MoveEarth(ClassSpell):
    rules = SpellRules(
        name="Move Earth",
        level=6,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.DRUID, CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 120),
        components=Components(verbal=True, somatic=True, material="a miniature shovel"),
        duration=Duration(DurationType.HOUR, 2, concentration=True),
        source="Player's Handbook",
        description=(
            "Choose an area of terrain no larger than 40 feet on a side within range. You can reshape dirt, sand, or clay in the area in any manner you choose for the duration. You can raise or lower the area’s elevation, create or fill in a trench, erect or flatten a wall, or form a pillar. The extent of any such changes can’t exceed half the area’s largest dimension. For example, if you affect a 40-foot square, you can create a pillar up to 20 feet high, raise or lower the square’s elevation by up to 20 feet, dig a trench up to 20 feet deep, and so on. It takes 10 minutes for these changes to complete. Because the terrain’s transformation occurs slowly, creatures in the area can’t usually be trapped or injured by the ground’s movement.\n"
            "At the end of every 10 minutes you spend concentrating on the spell, you can choose a new area of terrain to affect within range.\n"
            "This spell can’t manipulate natural stone or stone construction. Rocks and structures shift to accommodate the new terrain. If the way you shape the terrain would make a structure unstable, it might collapse.\n"
            "Similarly, this spell doesn’t directly affect plant growth. The moved earth carries any plants along with it."
        ),
        usage_tags=("control", "heal"),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "854e652e7fe896d7")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Area",
                        "An area of terrain no larger than 40 feet on a side within range",
                    ),
                    (
                        "Reshaping",
                        "You can reshape dirt, sand, or clay in the area in any manner you choose for the duration",
                    ),
                    (
                        "Changes",
                        "You can raise or lower the area's elevation, create or fill in a trench, erect or flatten a wall, or form a pillar",
                    ),
                    (
                        "Extent",
                        "The extent of any such changes can't exceed half the area's largest dimension",
                    ),
                    (
                        "Example",
                        "If you affect a 40-foot square, you can create a pillar up to 20 feet high, raise or lower the square's elevation by up to 20 feet, dig a trench up to 20 feet deep, and so on",
                    ),
                    ("Time", "It takes 10 minutes for these changes to complete"),
                    (
                        "Creatures",
                        "Because the terrain's transformation occurs slowly, creatures in the area can't usually be trapped or injured by the ground's movement",
                    ),
                    (
                        "New area",
                        "At the end of every 10 minutes you spend concentrating on the spell, you can choose a new area of terrain to affect within range",
                    ),
                    (
                        "Stone",
                        "This spell can't manipulate natural stone or stone construction. Rocks and structures shift to accommodate the new terrain",
                    ),
                    (
                        "Structures",
                        "If the way you shape the terrain would make a structure unstable, it might collapse",
                    ),
                    (
                        "Plants",
                        "Similarly, this spell doesn't directly affect plant growth. The moved earth carries any plants along with it",
                    ),
                )
            )
        ]


class OtilukesFreezingSphere(ClassSpell):
    rules = SpellRules(
        name="Otiluke's Freezing Sphere",
        level=6,
        school=School.EVOCATION,
        classes=(CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 300),
        components=Components(
            verbal=True, somatic=True, material="a miniature crystal sphere"
        ),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "A frigid globe streaks from you to a point of your choice within range, where it explodes in a 60-foot-radius Sphere. Each creature in that area makes a Constitution saving throw, taking 10d6 Cold damage on failed save or half as much damage on a successful one.\n"
            "If the globe strikes a body of water, it freezes the water to a depth of 6 inches over an area 30 feet square. This ice lasts for 1 minute. Creatures that were swimming on the surface of frozen water are trapped in the ice and have the Restrained condition. A trapped creature can take an action to make a Strength (Athletics) check against your spell save DC to break free.\n"
            "You can refrain from firing the globe after completing the spell’s casting. If you do so, a globe about the size of a sling bullet, cool to the touch, appears in your hand. At any time, you or a creature you give the globe to can throw the globe (to a range of 40 feet) or hurl it with a sling (to the sling’s normal range). It shatters on impact, with the same effect as a normal casting of the spell. You can also set the globe down without shattering it. After 1 minute, if the globe hasn’t already shattered, it explodes.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 1d6 for each spell slot level above 6."
        ),
        usage_tags=("control", "damage"),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "4fef1f387320853c")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "A frigid globe streaks from you to a point of your choice within range, where it explodes in a 60-foot-radius Sphere.",
                    ),
                    (
                        "Area",
                        "60-foot-radius Sphere, where the globe explodes at a point of your choice within range",
                    ),
                    ("Save", "Constitution, made by each creature in that area"),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (("10d6 Cold damage", "Half as much damage"),),
            ),
            Option(
                "Striking Water",
                (
                    Facts(
                        (
                            (
                                "Freezing",
                                "If the globe strikes a body of water, it freezes the water to a depth of 6 inches over an area 30 feet square",
                            ),
                            ("Lasts", "This ice lasts for 1 minute"),
                            (
                                "Trapped",
                                "Creatures that were swimming on the surface of frozen water are trapped in the ice and have the Restrained condition",
                            ),
                            (
                                "Escape",
                                "A trapped creature can take an action to make a Strength (Athletics) check against your spell save DC to break free",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Holding the Globe",
                (
                    Facts(
                        (
                            (
                                "Refraining",
                                "You can refrain from firing the globe after completing the spell's casting",
                            ),
                            (
                                "Globe",
                                "If you do so, a globe about the size of a sling bullet, cool to the touch, appears in your hand",
                            ),
                            (
                                "Throwing",
                                "At any time, you or a creature you give the globe to can throw the globe (to a range of 40 feet) or hurl it with a sling (to the sling's normal range)",
                            ),
                            (
                                "Shatters",
                                "It shatters on impact, with the same effect as a normal casting of the spell",
                            ),
                            (
                                "Setting down",
                                "You can also set the globe down without shattering it",
                            ),
                            (
                                "Exploding",
                                "After 1 minute, if the globe hasn't already shattered, it explodes",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Damage", "+1d6 for each spell slot level above 6"),)),),
            ),
        ]


class OttosIrresistibleDance(ClassSpell):
    rules = SpellRules(
        name="Otto's Irresistible Dance",
        level=6,
        school=School.ENCHANTMENT,
        classes=(CharacterClass.BARD, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 30),
        components=Components(verbal=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "One creature that you can see within range must make a Wisdom saving throw. On a successful save, the target dances comically until the end of its next turn, during which it must spend all its movement to dance in place.\n"
            "On a failed save, the target has the Charmed condition for the duration. While Charmed, the target dances comically, must use all its movement to dance in place, and has Disadvantage on Dexterity saving throws and attack rolls, and other creatures have Advantage on attack rolls against it. On each of its turns, the target can take an action to collect itself and repeat the save, ending the spell on itself on a success."
        ),
        usage_tags=("buff", "control"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "254ec404125c845b")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Target", "One creature that you can see within range"),
                    ("Save", "Wisdom"),
                    (
                        "Failed save",
                        "The target has the Charmed condition for the duration",
                    ),
                    (
                        "While Charmed",
                        "The target dances comically, must use all its movement to dance in place, and has Disadvantage on Dexterity saving throws and attack rolls, and other creatures have Advantage on attack rolls against it",
                    ),
                    (
                        "Repeat save",
                        "On each of its turns, the target can take an action to collect itself and repeat the save, ending the spell on itself on a success",
                    ),
                    (
                        "Successful save",
                        "The target dances comically until the end of its next turn, during which it must spend all its movement to dance in place",
                    ),
                )
            )
        ]


class PlanarAlly(ClassSpell):
    rules = SpellRules(
        name="Planar Ally",
        level=6,
        school=School.CONJURATION,
        classes=(CharacterClass.CLERIC,),
        casting_time=CastingTime(CastingTimeType.MINUTE, 10),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "You beseech an otherworldly entity for aid. The being must be known to you: a god, a demon prince, or some other being of cosmic power. That entity sends a Celestial, an Elemental, or a Fiend loyal to it to aid you, making the creature appear in an unoccupied space within range. If you know a specific creature’s name, you can speak that name when you cast this spell to request that creature, though you might get a different creature anyway (DM’s choice).\n"
            "When the creature appears, it is under no compulsion to behave a particular way. You can ask it to perform a service in exchange for payment, but it isn’t obliged to do so. The requested task could range from simple (fly us across the chasm, or help us fight a battle) to complex (spy on our enemies, or protect us during our foray into the dungeon). You must be able to communicate with the creature to bargain for its services.\n"
            "Payment can take a variety of forms. A Celestial might require a sizable donation of gold or magic items to an allied temple, while a Fiend might demand a living sacrifice or a gift of treasure. Some creatures might exchange their service for a quest undertaken by you.\n"
            "A task that can be measured in minutes requires a payment worth 100 GP per minute. A task measured in hours requires 1,000 GP per hour. And a task measured in days (up to 10 days) requires 10,000 GP per day. The DM can adjust these payments based on the circumstances under which you cast the spell. If the task is aligned with the creature’s ethos, the payment might be halved or even waived. Nonhazardous tasks typically require only half the suggested payment, while especially dangerous tasks might require a greater gift. Creatures rarely accept tasks that seem suicidal.\n"
            "After the creature completes the task, or when the agreed-upon duration of service expires, the creature returns to its home plane after reporting back to you if possible. If you are unable to agree on a price for the creature’s service, the creature immediately returns to its home plane."
        ),
        usage_tags=("summon",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "8f3bc7702945ab3a")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Entity",
                        "You beseech an otherworldly entity for aid. The being must be known to you: a god, a demon prince, or some other being of cosmic power",
                    ),
                    (
                        "Creature",
                        "That entity sends a Celestial, an Elemental, or a Fiend loyal to it to aid you, making the creature appear in an unoccupied space within range",
                    ),
                    (
                        "By name",
                        "If you know a specific creature's name, you can speak that name when you cast this spell to request that creature, though you might get a different creature anyway (DM's choice)",
                    ),
                )
            ),
            Option(
                "Bargaining",
                (
                    Facts(
                        (
                            (
                                "Behavior",
                                "When the creature appears, it is under no compulsion to behave a particular way",
                            ),
                            (
                                "Service",
                                "You can ask it to perform a service in exchange for payment, but it isn't obliged to do so",
                            ),
                            (
                                "Tasks",
                                "The requested task could range from simple (fly us across the chasm, or help us fight a battle) to complex (spy on our enemies, or protect us during our foray into the dungeon)",
                            ),
                            (
                                "Communication",
                                "You must be able to communicate with the creature to bargain for its services",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Payment",
                (
                    Facts(
                        (
                            ("Forms", "Payment can take a variety of forms"),
                            (
                                "Examples",
                                "A Celestial might require a sizable donation of gold or magic items to an allied temple, while a Fiend might demand a living sacrifice or a gift of treasure. Some creatures might exchange their service for a quest undertaken by you",
                            ),
                        )
                    ),
                    Table(
                        ("Task measured in", "Payment required"),
                        (
                            ("Minutes", "100 GP per minute"),
                            ("Hours", "1,000 GP per hour"),
                            ("Days (up to 10 days)", "10,000 GP per day"),
                        ),
                    ),
                    Facts(
                        (
                            (
                                "Adjusting",
                                "The DM can adjust these payments based on the circumstances under which you cast the spell",
                            ),
                            (
                                "Aligned tasks",
                                "If the task is aligned with the creature's ethos, the payment might be halved or even waived",
                            ),
                            (
                                "Risk",
                                "Nonhazardous tasks typically require only half the suggested payment, while especially dangerous tasks might require a greater gift",
                            ),
                            (
                                "Suicidal",
                                "Creatures rarely accept tasks that seem suicidal",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Returning",
                (
                    Facts(
                        (
                            (
                                "Done",
                                "After the creature completes the task, or when the agreed-upon duration of service expires, the creature returns to its home plane after reporting back to you if possible",
                            ),
                            (
                                "No agreement",
                                "If you are unable to agree on a price for the creature's service, the creature immediately returns to its home plane",
                            ),
                        )
                    ),
                ),
            ),
        ]


class PrimordialWard(ClassSpell):
    rules = SpellRules(
        name="Primordial Ward",
        level=6,
        school=School.ABJURATION,
        classes=(CharacterClass.DRUID,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Xanathar's Guide to Everything",
        description=(
            "You have resistance to acid, cold, fire, lightning, and thunder damage for the spell's duration.\n"
            "When you take damage of one of those types, you can use your reaction to gain immunity to that type of damage, including against the triggering damage. If you do so, the resistances end, and you have the immunity until the end of your next turn, at which time the spell ends."
        ),
        usage_tags=("buff",),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "31cfbc44f1b95b44")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Resistance",
                        "You have resistance to Acid, Cold, Fire, Lightning, and Thunder damage for the spell's duration",
                    ),
                    ("Trigger", "You take damage of one of those types"),
                    (
                        "Reaction",
                        "You can use your reaction to gain immunity to that type of damage, including against the triggering damage",
                    ),
                    (
                        "Then",
                        "If you do so, the resistances end, and you have the immunity until the end of your next turn, at which time the spell ends",
                    ),
                )
            )
        ]


class ProgrammedIllusion(ClassSpell):
    rules = SpellRules(
        name="Programmed Illusion",
        level=6,
        school=School.ILLUSION,
        classes=(CharacterClass.BARD, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 120),
        components=Components(
            verbal=True, somatic=True, material="jade dust worth 25+ GP"
        ),
        duration=Duration(DurationType.UNTIL_DISPELLED),
        source="Player's Handbook",
        description=(
            "You create an illusion of an object, a creature, or some other visible phenomenon within range that activates when a specific trigger occurs. The illusion is imperceptible until then. It must be no larger than a 30-foot Cube, and you decide when you cast the spell how the illusion behaves and what sounds it makes. This scripted performance can last up to 5 minutes.\n"
            "When the trigger you specify occurs, the illusion springs into existence and performs in the manner you described. Once the illusion finishes performing, it disappears and remains dormant for 10 minutes, after which the illusion can be activated again.\n"
            "The trigger can be as general or as detailed as you like, though it must be based on visual or audible phenomena that occur within 30 feet of the area. For example, you could create an illusion of yourself to appear and warn off others who attempt to open a trapped door.\n"
            "Physical interaction with the image reveals it to be illusory, since things can pass through it. A creature that takes the Study action to examine the image can determine that it is an illusion with a successful Intelligence (Investigation) check against your spell save DC. If a creature discerns the illusion for what it is, the creature can see through the image, and any noise it makes sounds hollow to the creature."
        ),
        usage_tags=("control",),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "849a2e5e6515b220")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Illusion",
                        "You create an illusion of an object, a creature, or some other visible phenomenon within range that activates when a specific trigger occurs",
                    ),
                    ("Hidden", "The illusion is imperceptible until then"),
                    ("Size", "It must be no larger than a 30-foot Cube"),
                    (
                        "Behavior",
                        "You decide when you cast the spell how the illusion behaves and what sounds it makes",
                    ),
                    (
                        "Performance",
                        "This scripted performance can last up to 5 minutes",
                    ),
                    (
                        "Trigger",
                        "The trigger can be as general or as detailed as you like, though it must be based on visual or audible phenomena that occur within 30 feet of the area",
                    ),
                    (
                        "Example",
                        "You could create an illusion of yourself to appear and warn off others who attempt to open a trapped door",
                    ),
                    (
                        "Activating",
                        "When the trigger you specify occurs, the illusion springs into existence and performs in the manner you described",
                    ),
                    (
                        "Dormant",
                        "Once the illusion finishes performing, it disappears and remains dormant for 10 minutes, after which the illusion can be activated again",
                    ),
                )
            ),
            Option(
                "Discerning the Illusion",
                (
                    Facts(
                        (
                            (
                                "Touching it",
                                "Physical interaction with the image reveals it to be illusory, since things can pass through it",
                            ),
                            (
                                "Studying it",
                                "A creature that takes the Study action to examine the image can determine that it is an illusion with a successful Intelligence (Investigation) check against your spell save DC",
                            ),
                            (
                                "Seeing through",
                                "If a creature discerns the illusion for what it is, the creature can see through the image, and any noise it makes sounds hollow to the creature",
                            ),
                        )
                    ),
                ),
            ),
        ]


class Scatter(ClassSpell):
    rules = SpellRules(
        name="Scatter",
        level=6,
        school=School.CONJURATION,
        classes=(
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 30),
        components=Components(verbal=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Xanathar's Guide to Everything",
        description="The air quivers around up to five creatures of your choice that you can see within range. An unwilling creature must succeed on a Wisdom saving throw to resist this spell. You teleport each affected target to an unoccupied space that you can see within 120 feet of you. That space must be on the ground or on a floor.",
        usage_tags=("utility",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "6d41b7f9fef97e18")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "The air quivers around up to five creatures of your choice that you can see within range.",
                    ),
                    (
                        "Targets",
                        "Up to five creatures of your choice that you can see within range",
                    ),
                    (
                        "Save",
                        "Wisdom, made by an unwilling creature to resist this spell",
                    ),
                    (
                        "Teleport",
                        "You teleport each affected target to an unoccupied space that you can see within 120 feet of you",
                    ),
                    ("Space", "That space must be on the ground or on a floor"),
                )
            )
        ]


class SoulCage(ClassSpell):
    rules = SpellRules(
        name="Soul Cage",
        level=6,
        school=School.NECROMANCY,
        classes=(CharacterClass.WARLOCK, CharacterClass.WIZARD),
        casting_time=CastingTime(
            CastingTimeType.REACTION,
            trigger="which you take when a humanoid you can see within 60 feet of you dies",
        ),
        range=Range(RangeType.FOOT, 60),
        components=Components(
            verbal=True, somatic=True, material="a tiny silver cage worth 100 gp"
        ),
        duration=Duration(DurationType.HOUR, 8),
        source="Xanathar's Guide to Everything",
        description=(
            "This spell snatches the soul of a humanoid as it dies and traps it inside the tiny cage you use for the material component. A stolen soul remains inside the cage until the spell ends or until you destroy the cage, which ends the spell. While you have a soul inside the cage, you can exploit it in any of the ways described below. You can use a trapped soul up to six times. Once you exploit a soul for the sixth time, it is released, and the spell ends. While a soul is trapped, the dead humanoid it came from can't be revived.\n"
            "Steal Life. You can use a bonus action to drain vigor from the soul and regain 2d8 hit points.\n"
            "Query Soul. You ask the soul a question (no action required) and receive a brief telepathic answer, which you can understand regardless of the language used. The soul knows only what it knew in life, but it must answer you truthfully and to the best of its ability. The answer is no more than a sentence or two and might be cryptic.\n"
            "Borrow Experience. You can use a bonus action to bolster yourself with the soul's life experience, making your next attack roll, ability check, or saving throw with advantage. If you don't use this benefit before the start of your next turn, it is lost.\n"
            "Eyes of the Dead. You can use an action to name a place the humanoid saw in life, which creates an invisible sensor somewhere in that place if it is on the plane of existence you're currently on. The sensor remains for as long as you concentrate, up to 10 minutes (as if you were concentrating on a spell). You receive visual and auditory information from the sensor as if you were in its space using your senses.\n"
            "A creature that can see the sensor (such as one using see invisibility or truesight) sees a translucent image of the tormented humanoid whose soul you caged."
        ),
        usage_tags=("heal", "utility"),
        target=FeatureTarget.CREATURE,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "ca0bd3edbe4b7d57")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Trigger", "A humanoid you can see within 60 feet of you dies"),
                    (
                        "Soul",
                        "This spell snatches the soul of a humanoid as it dies and traps it inside the tiny cage you use for the material component",
                    ),
                    (
                        "Remains",
                        "A stolen soul remains inside the cage until the spell ends or until you destroy the cage, which ends the spell",
                    ),
                    (
                        "Using it",
                        "While you have a soul inside the cage, you can exploit it in any of the ways described below",
                    ),
                    (
                        "Uses",
                        "You can use a trapped soul up to six times. Once you exploit a soul for the sixth time, it is released, and the spell ends",
                    ),
                    (
                        "Revival",
                        "While a soul is trapped, the dead humanoid it came from can't be revived",
                    ),
                )
            ),
            Option(
                "Steal Life",
                (
                    Facts(
                        (
                            (
                                "Use",
                                "You can use a bonus action to drain vigor from the soul",
                            ),
                            ("Healing", "You regain 2d8 hit points"),
                        )
                    ),
                ),
            ),
            Option(
                "Query Soul",
                (
                    Facts(
                        (
                            (
                                "Use",
                                "You ask the soul a question (no action required) and receive a brief telepathic answer, which you can understand regardless of the language used",
                            ),
                            (
                                "Truthful",
                                "The soul knows only what it knew in life, but it must answer you truthfully and to the best of its ability",
                            ),
                            (
                                "Answer",
                                "The answer is no more than a sentence or two and might be cryptic",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Borrow Experience",
                (
                    Facts(
                        (
                            (
                                "Use",
                                "You can use a bonus action to bolster yourself with the soul's life experience, making your next attack roll, ability check, or saving throw with Advantage",
                            ),
                            (
                                "Lost",
                                "If you don't use this benefit before the start of your next turn, it is lost",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Eyes of the Dead",
                (
                    Facts(
                        (
                            (
                                "Use",
                                "You can use an action to name a place the humanoid saw in life, which creates an invisible sensor somewhere in that place if it is on the plane of existence you're currently on",
                            ),
                            (
                                "Duration",
                                "The sensor remains for as long as you concentrate, up to 10 minutes (as if you were concentrating on a spell)",
                            ),
                            (
                                "Senses",
                                "You receive visual and auditory information from the sensor as if you were in its space using your senses",
                            ),
                            (
                                "Seen",
                                "A creature that can see the sensor (such as one using see invisibility or truesight) sees a translucent image of the tormented humanoid whose soul you caged",
                            ),
                        )
                    ),
                ),
            ),
        ]


class SummonDinosaur(ClassSpell):
    rules = SpellRules(
        name="Summon Dinosaur",
        level=6,
        school=School.CONJURATION,
        classes=(CharacterClass.DRUID,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 90),
        components=Components(
            verbal=True, somatic=True, material="polished scale worth 600+ GP"
        ),
        duration=Duration(DurationType.HOUR, 1, concentration=True),
        source="Arcana Unleashed",
        description=(
            "You call forth the spirit of a primeval dinosaur. It manifests in an unoccupied space that you can see within range and uses the Dinosaur Spirit stat block. When you cast the spell, choose Ankylosaur, Triceratops, or Tyrannosaur. The creature resembles a dinosaur of the chosen type, which determines certain details in its stat block. The creature disappears when it drops to 0 Hit Points or when the spell ends.\n"
            "The creature is an ally to you and your allies. In combat, the creature shares your Initiative count, but it takes its turn immediately after yours. It obeys your verbal commands (no action required by you). If you don’t issue any, the creature takes the Dodge action and uses its movement to avoid danger.\n"
            "Using a Higher-Level Spell Slot. Use the spell slot’s level for the spell’s level in the stat block."
        ),
        usage_tags=("summon",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "b887e9b6eeb357c8")


class SummonFiend(ClassSpell):
    rules = SpellRules(
        name="Summon Fiend",
        level=6,
        school=School.CONJURATION,
        classes=(CharacterClass.WARLOCK, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 90),
        components=Components(
            verbal=True, somatic=True, material="a bloody vial worth 600+ GP"
        ),
        duration=Duration(DurationType.HOUR, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "You call forth a fiendish spirit. It manifests in an unoccupied space that you can see within range and uses the Fiendish Spirit stat block. When you cast the spell, choose Demon, Devil, or Yugoloth. The creature resembles a Fiend of the chosen type, which determines certain details in its stat block. The creature disappears when it drops to 0 Hit Points or when the spell ends.\n"
            "The creature is an ally to you and your allies. In combat, the creature shares your Initiative count, but it takes its turn immediately after yours. It obeys your verbal commands (no action required by you). If you don’t issue any, it takes the Dodge action and uses its movement to avoid danger.\n"
            "Using a Higher-Level Spell Slot. Use the spell slot’s level for the spell’s level in the stat block."
        ),
        usage_tags=("summon",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "ccf10b90f726b900")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You call forth a fiendish spirit."),
            Facts(
                (
                    ("Appears", "In an unoccupied space that you can see within range"),
                    (
                        "Kind",
                        "Demon, Devil, or Yugoloth, chosen when you cast the spell; the creature resembles a Fiend of the chosen type, which determines certain details in its stat block",
                    ),
                    ("Stat block", "Fiendish Spirit (below)"),
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
                "Fiendish Spirit",
                (
                    Facts(
                        (
                            ("Type", "Large Fiend"),
                            ("AC", "12 + the spell's level"),
                            (
                                "Hit Points",
                                "50 (Demon only), 40 (Devil only), or 60 (Yugoloth only) + 15 for each spell level above 6",
                            ),
                            (
                                "Speed",
                                "40 ft., Climb 40 ft. (Demon only), Fly 60 ft. (Devil only)",
                            ),
                            (
                                "Abilities",
                                "Str 13, Dex 16, Con 15, Int 10, Wis 10, Cha 16",
                            ),
                            ("Resistances", "Fire"),
                            ("Immunities", "Poison; Poisoned"),
                            ("Senses", "Darkvision 60 ft., Passive Perception 10"),
                            ("Languages", "Abyssal, Infernal, Telepathy 60 ft"),
                            (
                                "Death Throes",
                                "Demon only. When the spirit drops to 0 Hit Points or the spell ends, the spirit explodes. Dexterity Saving Throw: DC equals your spell save DC, each creature in a 10-foot Emanation originating from the spirit. Failure: 2d10 plus this spell's level Fire damage. Success: Half damage",
                            ),
                            (
                                "Devil's Sight",
                                "Devil only. Magical Darkness doesn't impede the spirit's Darkvision",
                            ),
                            (
                                "Magic Resistance",
                                "The spirit has Advantage on saving throws against spells and other magical effects",
                            ),
                            (
                                "Multiattack",
                                "The spirit makes a number of attacks equal to half this spell's level (round down)",
                            ),
                            (
                                "Bite",
                                "Demon only. Melee Attack Roll: Bonus equals your spell attack modifier, reach 5 ft. Hit: 1d12 + 3 + the spell's level Necrotic damage",
                            ),
                            (
                                "Claws",
                                "Yugoloth only. Melee Attack Roll: Bonus equals your spell attack modifier, reach 5 ft. Hit: 1d8 + 3 + the spell's level Slashing damage. Immediately after the attack hits or misses, the spirit can teleport up to 30 feet to an unoccupied space it can see",
                            ),
                            (
                                "Fiery Strike",
                                "Devil only. Melee or Ranged Attack Roll: Bonus equals your spell attack modifier, reach 5 ft. or range 150 ft. Hit: 2d6 + 3 + the spell's level Fire damage",
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


class Sunbeam(ClassSpell):
    rules = SpellRules(
        name="Sunbeam",
        level=6,
        school=School.EVOCATION,
        classes=(
            CharacterClass.CLERIC,
            CharacterClass.DRUID,
            CharacterClass.SORCERER,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True, material="a magnifying glass"),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "You launch a sunbeam in a 5-foot-wide, 60-foot-long Line. Each creature in the Line makes a Constitution saving throw. On a failed save, a creature takes 6d8 Radiant damage and has the Blinded condition until the start of your next turn. On a successful save, it takes half as much damage only.\n"
            "Until the spell ends, you can take a Magic action to create a new Line of radiance.\n"
            "For the duration, a mote of brilliant radiance shines above you. It sheds Bright Light in a 30-foot radius and Dim Light for an additional 30 feet. This light is sunlight."
        ),
        usage_tags=("control", "damage"),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "105ee61b20440215")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Area",
                        "You launch a sunbeam in a 5-foot-wide, 60-foot-long Line",
                    ),
                    ("Save", "Constitution, made by each creature in the Line"),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (
                    (
                        "6d8 Radiant damage, and the creature has the Blinded condition until the start of your next turn",
                        "Half as much damage only",
                    ),
                ),
            ),
            Facts(
                (
                    (
                        "New Line",
                        "Until the spell ends, you can take a Magic action to create a new Line of radiance",
                    ),
                    (
                        "Mote",
                        "For the duration, a mote of brilliant radiance shines above you",
                    ),
                    (
                        "Light",
                        "It sheds Bright Light in a 30-foot radius and Dim Light for an additional 30 feet",
                    ),
                    ("Sunlight", "This light is sunlight"),
                )
            ),
        ]


class TashasBubblingCauldron(ClassSpell):
    rules = SpellRules(
        name="Tasha's Bubbling Cauldron",
        level=6,
        school=School.CONJURATION,
        classes=(CharacterClass.WARLOCK, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 5),
        components=Components(
            verbal=True, somatic=True, material="a gilded ladle worth 500+ GP"
        ),
        duration=Duration(DurationType.MINUTE, 10),
        source="Player's Handbook",
        description=(
            "You conjure a claw-footed cauldron filled with bubbling liquid. The cauldron appears in an unoccupied space on the ground within 5 feet of you and lasts for the duration. The cauldron can't be moved and disappears when the spell ends, along with the bubbling liquid inside it.\n"
            "The liquid in the cauldron duplicates the properties of a Common or an Uncommon potion of your choice (such as a Potion of Healing ). As a Bonus Action, you or an ally can reach into the cauldron and withdraw one potion of that kind. The potion is contained in a vial that disappears when the potion is consumed. The cauldron can produce a number of these potions equal to your spellcasting ability modifier (minimum 1). When the last of these potions is withdrawn from the cauldron, the cauldron disappears, and the spell ends.\n"
            "Potions obtained from the cauldron that aren't consumed disappear when you cast this spell again."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "3155e918bd47a1ba")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You conjure a claw-footed cauldron filled with bubbling liquid.",
                    ),
                    (
                        "Appears",
                        "In an unoccupied space on the ground within 5 feet of you; the cauldron lasts for the duration",
                    ),
                    (
                        "Cauldron",
                        "The cauldron can't be moved and disappears when the spell ends, along with the bubbling liquid inside it",
                    ),
                    (
                        "Liquid",
                        "The liquid in the cauldron duplicates the properties of a Common or an Uncommon potion of your choice (such as a Potion of Healing)",
                    ),
                    (
                        "Withdrawing",
                        "As a Bonus Action, you or an ally can reach into the cauldron and withdraw one potion of that kind",
                    ),
                    (
                        "Vial",
                        "The potion is contained in a vial that disappears when the potion is consumed",
                    ),
                    (
                        "Number",
                        "The cauldron can produce a number of these potions equal to your spellcasting ability modifier (minimum 1)",
                    ),
                    (
                        "Ends",
                        "When the last of these potions is withdrawn from the cauldron, the cauldron disappears, and the spell ends",
                    ),
                    (
                        "Unconsumed",
                        "Potions obtained from the cauldron that aren't consumed disappear when you cast this spell again",
                    ),
                )
            )
        ]


class TashasOtherworldlyGuise(ClassSpell):
    rules = SpellRules(
        name="Tasha's Otherworldly Guise",
        level=6,
        school=School.TRANSMUTATION,
        classes=(
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.BONUS_ACTION),
        range=Range(RangeType.SELF),
        components=Components(
            verbal=True,
            somatic=True,
            material="an object engraved with a symbol of the Outer Planes, worth at least 500 gp",
        ),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Tasha's Cauldron of Everything",
        description=(
            "Uttering an incantation, you draw on the magic of the Lower Planes or Upper Planes (your choice) to transform yourself. You gain the following benefits until the spell ends:\n"
            "You are immune to fire and poison damage (Lower Planes) or radiant and necrotic damage (Upper Planes).\n"
            "You are immune to the poisoned condition (Lower Planes) or the charmed condition (Upper Planes).\n"
            "Spectral wings appear on your back, giving you a flying speed of 40 feet.\n"
            "You have a +2 bonus to AC.\n"
            "All your weapon attacks are magical, and when you make a weapon attack, you can use your spell casting ability modifier instead of Strength or Dexterity for the attack and damage rolls.\n"
            "You can attack twice, instead of once, when you take the Attack action on your turn. You ignore this benefit if you already have a feature, like Extra Attack, that lets you attack more than once when you take the Attack action on your turn."
        ),
        usage_tags=("buff", "damage"),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "0a9cb766fa2ac867")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "Uttering an incantation, you draw on the magic of the Lower Planes or Upper Planes (your choice) to transform yourself.",
                    ),
                    ("Planes", "Lower Planes or Upper Planes (your choice)"),
                    (
                        "Benefits",
                        "You gain the following benefits until the spell ends",
                    ),
                )
            ),
            Table(
                ("Planes", "Immune to damage", "Immune to condition"),
                (
                    ("Lower Planes", "Fire and Poison", "Poisoned"),
                    ("Upper Planes", "Radiant and Necrotic", "Charmed"),
                ),
            ),
            Facts(
                (
                    (
                        "Wings",
                        "Spectral wings appear on your back, giving you a flying speed of 40 feet",
                    ),
                    ("AC", "You have a +2 bonus to AC"),
                    (
                        "Weapons",
                        "All your weapon attacks are magical, and when you make a weapon attack, you can use your spell casting ability modifier instead of Strength or Dexterity for the attack and damage rolls",
                    ),
                    (
                        "Attacks",
                        "You can attack twice, instead of once, when you take the Attack action on your turn",
                    ),
                    (
                        "Not stacking",
                        "You ignore this benefit if you already have a feature, like Extra Attack, that lets you attack more than once when you take the Attack action on your turn",
                    ),
                )
            ),
        ]


class TensersTransformation(ClassSpell):
    rules = SpellRules(
        name="Tenser's Transformation",
        level=6,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.WIZARD,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(
            verbal=True, somatic=True, material="a few hairs from a bull"
        ),
        duration=Duration(DurationType.MINUTE, 10, concentration=True),
        source="Xanathar's Guide to Everything",
        description=(
            "You endow yourself with endurance and martial prowess fueled by magic. Until the spell ends, you can't cast spells, and you gain the following benefits:\n"
            "You gain 50 temporary hit points. If any of these remain when the spell ends, they are lost.\n"
            "You have advantage on attack rolls that you make with simple and martial weapons.\n"
            "When you hit a target with a weapon attack, that target takes an extra 2d12 force damage.\n"
            "You have proficiency with all armor, shields, simple weapons, and martial weapons.\n"
            "You have proficiency in Strength and Constitution saving throws.\n"
            "You can attack twice, instead of once, when you take the Attack action on your turn. You ignore this benefit if you already have a feature, like Extra Attack, that gives you extra attacks.\n"
            "Immediately after the spell ends, you must succeed on a DC 15 Constitution saving throw or suffer one level of exhaustion."
        ),
        usage_tags=("buff", "damage", "heal"),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "31d2b49fc884e0a4")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You endow yourself with endurance and martial prowess fueled by magic.",
                    ),
                    ("Spells", "Until the spell ends, you can't cast spells"),
                    (
                        "Benefits",
                        "Until the spell ends, you gain the following benefits",
                    ),
                    ("Temp. hit points", "You gain 50 temporary hit points"),
                    (
                        "Lost",
                        "If any of these remain when the spell ends, they are lost",
                    ),
                    (
                        "Advantage",
                        "You have Advantage on attack rolls that you make with simple and martial weapons",
                    ),
                    (
                        "Extra damage",
                        "When you hit a target with a weapon attack, that target takes an extra 2d12 Force damage",
                    ),
                    (
                        "Proficiencies",
                        "You have proficiency with all armor, shields, simple weapons, and martial weapons",
                    ),
                    (
                        "Saves",
                        "You have proficiency in Strength and Constitution saving throws",
                    ),
                    (
                        "Attacks",
                        "You can attack twice, instead of once, when you take the Attack action on your turn",
                    ),
                    (
                        "Not stacking",
                        "You ignore this benefit if you already have a feature, like Extra Attack, that gives you extra attacks",
                    ),
                )
            ),
            Option(
                "When the Spell Ends",
                (
                    Facts(
                        (
                            (
                                "Save",
                                "Constitution (DC 15), made by you immediately after the spell ends",
                            ),
                            ("Failed save", "You suffer one level of Exhaustion"),
                            ("Successful save", "No effect"),
                        )
                    ),
                ),
            ),
        ]


class TransportViaPlants(ClassSpell):
    rules = SpellRules(
        name="Transport via Plants",
        level=6,
        school=School.CONJURATION,
        classes=(CharacterClass.DRUID,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 10),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 1),
        source="Player's Handbook",
        description="This spell creates a magical link between a Large or larger inanimate plant within range and another plant, at any distance, on the same plane of existence. You must have seen or touched the destination plant at least once before. For the duration, any creature can step into the target plant and exit from the destination plant by using 5 feet of movement.",
        usage_tags=("utility",),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "194b9a277510baea")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Link",
                        "This spell creates a magical link between a Large or larger inanimate plant within range and another plant, at any distance, on the same plane of existence",
                    ),
                    (
                        "Requirement",
                        "You must have seen or touched the destination plant at least once before",
                    ),
                    (
                        "Travel",
                        "For the duration, any creature can step into the target plant and exit from the destination plant by using 5 feet of movement",
                    ),
                )
            )
        ]


class TrueSeeing(ClassSpell):
    rules = SpellRules(
        name="True Seeing",
        level=6,
        school=School.DIVINATION,
        classes=(
            CharacterClass.BARD,
            CharacterClass.CLERIC,
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.TOUCH),
        components=Components(
            verbal=True,
            somatic=True,
            material="mushroom powder worth 25+ GP, which the spell consumes",
        ),
        duration=Duration(DurationType.HOUR, 1),
        source="Player's Handbook",
        description="For the duration, the willing creature you touch has Truesight with a range of 120 feet.",
        usage_tags=("buff",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "cf682e9e4af05788")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Target", "A willing creature you touch"),
                    (
                        "Truesight",
                        "For the duration, the willing creature you touch has Truesight with a range of 120 feet",
                    ),
                )
            )
        ]


class WallOfIce(ClassSpell):
    rules = SpellRules(
        name="Wall of Ice",
        level=6,
        school=School.EVOCATION,
        classes=(CharacterClass.WIZARD,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 120),
        components=Components(verbal=True, somatic=True, material="a piece of quartz"),
        duration=Duration(DurationType.MINUTE, 10, concentration=True),
        source="Player's Handbook",
        description=(
            "You create a wall of ice on a solid surface within range. You can form it into a hemispherical dome or a globe with a radius of up to 10 feet, or you can shape a flat surface made up of ten 10-foot-square panels. Each panel must be contiguous with another panel. In any form, the wall is 1 foot thick and lasts for the duration.\n"
            "If the wall cuts through a creature’s space when it appears, the creature is pushed to one side of the wall (you choose which side) and makes a Dexterity saving throw, taking 10d6 Cold damage on a failed save or half as much damage on a successful one.\n"
            "The wall is an object that can be damaged and thus breached. It has AC 12 and 30 Hit Points per 10-foot section, and it has Immunity to Cold, Poison, and Psychic damage and Vulnerability to Fire damage. Reducing a 10-foot section of wall to 0 Hit Points destroys it and leaves behind a sheet of frigid air in the space the wall occupied.\n"
            "A creature moving through the sheet of frigid air for the first time on a turn makes a Constitution saving throw, taking 5d6 Cold damage on a failed save or half as much damage on a successful one.\n"
            "Using a Higher-Level Spell Slot. The damage the wall deals when it appears increases by 2d6 and the damage from passing through the sheet of frigid air increases by 1d6 for each spell slot level above 6."
        ),
        usage_tags=("control", "damage"),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "182502bea5890462")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Appears", "A wall of ice on a solid surface within range"),
                    (
                        "Shape",
                        "You can form it into a hemispherical dome or a globe with a radius of up to 10 feet, or you can shape a flat surface made up of ten 10-foot-square panels",
                    ),
                    ("Panels", "Each panel must be contiguous with another panel"),
                    (
                        "Thickness",
                        "In any form, the wall is 1 foot thick and lasts for the duration",
                    ),
                )
            ),
            Option(
                "Cutting Through a Creature",
                (
                    Facts(
                        (
                            (
                                "Creature",
                                "If the wall cuts through a creature's space when it appears, the creature is pushed to one side of the wall (you choose which side)",
                            ),
                            ("Save", "Dexterity, made by that creature"),
                        )
                    ),
                    Table(
                        ("Failed save", "Successful save"),
                        (("10d6 Cold damage", "Half as much damage"),),
                    ),
                ),
            ),
            Option(
                "The Wall as an Object",
                (
                    Facts(
                        (
                            (
                                "Object",
                                "The wall is an object that can be damaged and thus breached",
                            ),
                            (
                                "Each section",
                                "AC 12 and 30 Hit Points per 10-foot section, and it has Immunity to Cold, Poison, and Psychic damage and Vulnerability to Fire damage",
                            ),
                            (
                                "Destroyed",
                                "Reducing a 10-foot section of wall to 0 Hit Points destroys it and leaves behind a sheet of frigid air in the space the wall occupied",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Sheet of Frigid Air",
                (
                    Facts(
                        (
                            (
                                "Save",
                                "Constitution, made by a creature moving through the sheet of frigid air for the first time on a turn",
                            ),
                        )
                    ),
                    Table(
                        ("Failed save", "Successful save"),
                        (("5d6 Cold damage", "Half as much damage"),),
                    ),
                ),
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (
                    Facts(
                        (
                            (
                                "Wall appears",
                                "The damage the wall deals when it appears increases by 2d6 for each spell slot level above 6",
                            ),
                            (
                                "Frigid air",
                                "The damage from passing through the sheet of frigid air increases by 1d6 for each spell slot level above 6",
                            ),
                        )
                    ),
                ),
            ),
        ]


class WallOfThorns(ClassSpell):
    rules = SpellRules(
        name="Wall of Thorns",
        level=6,
        school=School.CONJURATION,
        classes=(CharacterClass.DRUID,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 120),
        components=Components(
            verbal=True, somatic=True, material="a handful of thorns"
        ),
        duration=Duration(DurationType.MINUTE, 10, concentration=True),
        source="Player's Handbook",
        description=(
            "You create a wall of tangled brush bristling with needle-sharp thorns. The wall appears within range on a solid surface and lasts for the duration. You choose to make the wall up to 60 feet long, 10 feet high, and 5 feet thick or a circle that has a 20-foot diameter and is up to 20 feet high and 5 feet thick. The wall blocks line of sight.\n"
            "When the wall appears, each creature in its area makes a Dexterity saving throw, taking 7d8 Piercing damage on a failed save or half as much damage on a successful one.\n"
            "A creature can move through the wall, albeit slowly and painfully. For every 1 foot a creature moves through the wall, it must spend 4 feet of movement. Furthermore, the first time a creature enters a space in the wall on a turn or ends its turn there, the creature makes a Dexterity saving throw, taking 7d8 Slashing damage on a failed save or half as much damage on a successful one. A creature makes this save only once per turn.\n"
            "Using a Higher-Level Spell Slot. Both types of damage increase by 1d8 for each spell slot level above 6."
        ),
        usage_tags=("buff", "control", "damage"),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "885e1cb3fbfd3136")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You create a wall of tangled brush bristling with needle-sharp thorns.",
                    ),
                    (
                        "Appears",
                        "The wall appears within range on a solid surface and lasts for the duration",
                    ),
                    (
                        "Shape",
                        "You choose to make the wall up to 60 feet long, 10 feet high, and 5 feet thick or a circle that has a 20-foot diameter and is up to 20 feet high and 5 feet thick",
                    ),
                    ("Sight", "The wall blocks line of sight"),
                )
            ),
            Option(
                "When the Wall Appears",
                (
                    Facts((("Save", "Dexterity, made by each creature in its area"),)),
                    Table(
                        ("Failed save", "Successful save"),
                        (("7d8 Piercing damage", "Half as much damage"),),
                    ),
                ),
            ),
            Option(
                "Moving Through the Wall",
                (
                    Facts(
                        (
                            (
                                "Movement",
                                "A creature can move through the wall, albeit slowly and painfully. For every 1 foot a creature moves through the wall, it must spend 4 feet of movement",
                            ),
                            (
                                "Save",
                                "Dexterity, made the first time a creature enters a space in the wall on a turn or ends its turn there",
                            ),
                        )
                    ),
                    Table(
                        ("Failed save", "Successful save"),
                        (("7d8 Slashing damage", "Half as much damage"),),
                    ),
                    Facts(
                        (
                            (
                                "Once per turn",
                                "A creature makes this save only once per turn",
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
                                "Damage",
                                "Both types of damage increase by 1d8 for each spell slot level above 6",
                            ),
                        )
                    ),
                ),
            ),
        ]


class WindWalk(ClassSpell):
    rules = SpellRules(
        name="Wind Walk",
        level=6,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.DRUID,),
        casting_time=CastingTime(CastingTimeType.MINUTE, 1),
        range=Range(RangeType.FOOT, 30),
        components=Components(verbal=True, somatic=True, material="a candle"),
        duration=Duration(DurationType.HOUR, 8),
        source="Player's Handbook",
        description=(
            "You and up to ten willing creatures of your choice within range assume gaseous forms for the duration, appearing as wisps of cloud. While in this cloud form, a target has a Fly Speed of 300 feet and can hover; it has Immunity to the Prone condition; and it has Resistance to Bludgeoning, Piercing, and Slashing damage. The only actions a target can take in this form are the Dash action or a Magic action to begin reverting to its normal form. Reverting takes 1 minute, during which the target has the Stunned condition. Until the spell ends, the target can revert to cloud form, which also requires a Magic action followed by a 1-minute transformation.\n"
            "If a target is in cloud form and flying when the effect ends, the target descends 60 feet per round for 1 minute until it lands, which it does safely. If it can’t land after 1 minute, it falls the remaining distance."
        ),
        usage_tags=("buff", "control"),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "79573218516db9ac")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Targets",
                        "You and up to ten willing creatures of your choice within range assume gaseous forms for the duration, appearing as wisps of cloud",
                    ),
                    (
                        "Benefits",
                        "While in this cloud form, a target has a Fly Speed of 300 feet and can hover; it has Immunity to the Prone condition; and it has Resistance to Bludgeoning, Piercing, and Slashing damage",
                    ),
                    (
                        "Actions",
                        "The only actions a target can take in this form are the Dash action or a Magic action to begin reverting to its normal form",
                    ),
                    (
                        "Reverting",
                        "Reverting takes 1 minute, during which the target has the Stunned condition",
                    ),
                    (
                        "Again",
                        "Until the spell ends, the target can revert to cloud form, which also requires a Magic action followed by a 1-minute transformation",
                    ),
                    (
                        "Ending",
                        "If a target is in cloud form and flying when the effect ends, the target descends 60 feet per round for 1 minute until it lands, which it does safely",
                    ),
                    (
                        "Can't land",
                        "If it can't land after 1 minute, it falls the remaining distance",
                    ),
                )
            )
        ]


class WordOfRecall(ClassSpell):
    rules = SpellRules(
        name="Word of Recall",
        level=6,
        school=School.CONJURATION,
        classes=(CharacterClass.CLERIC,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 5),
        components=Components(verbal=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "You and up to five willing creatures within 5 feet of you instantly teleport to a previously designated sanctuary. You and any creatures that teleport with you appear in the nearest unoccupied space to the spot you designated when you prepared your sanctuary (see below). If you cast this spell without first preparing a sanctuary, the spell has no effect.\n"
            "You must designate a location, such as a temple, as a sanctuary by casting this spell there."
        ),
        usage_tags=("buff",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "920d24e6211265b4")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Effect",
                        "You and up to five willing creatures within 5 feet of you instantly teleport to a previously designated sanctuary",
                    ),
                    (
                        "Arrival",
                        "You and any creatures that teleport with you appear in the nearest unoccupied space to the spot you designated when you prepared your sanctuary (see below)",
                    ),
                    (
                        "No sanctuary",
                        "If you cast this spell without first preparing a sanctuary, the spell has no effect",
                    ),
                    (
                        "Designating",
                        "You must designate a location, such as a temple, as a sanctuary by casting this spell there",
                    ),
                )
            )
        ]


class GravityFissure(ClassSpell):
    rules = SpellRules(
        name="Gravity Fissure",
        level=6,
        school=School.EVOCATION,
        classes=(CharacterClass.WIZARD,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF, area=Area(100, AreaShape.LINE)),
        components=Components(
            verbal=True, somatic=True, material="a fistful of iron filings"
        ),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Explorer's Guide to Wildemount",
        description=(
            "You manifest a ravine of gravitational energy in a line originating from you that is 100 feet long and 5 feet wide. Each creature in that line must make a Constitution saving throw, taking 8d8 force damage on a failed save, or half as much damage on a successful one.\n"
            "Each creature within 10 feet of the line but not in it must succeed on a Constitution saving throw or take 8d8 force damage and be pulled toward the line until the creature is in its area.\n"
            "At Higher Levels. When you cast this spell using a spell slot of 7th level or higher, the damage increases by 1d8 for each slot level above 6th."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.AREA,
        school_note="Dunamancy:Graviturgy",
    )
    converted_from = RecordStamp("spells_dnd5e.json", "d61683569d02ac66")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Area",
                        "You manifest a ravine of gravitational energy in a line originating from you that is 100 feet long and 5 feet wide",
                    ),
                )
            ),
            Option(
                "Creatures in the Line",
                (
                    Facts(
                        (("Save", "Constitution, made by each creature in that line"),)
                    ),
                    Table(
                        ("Failed save", "Successful save"),
                        (("8d8 Force damage", "Half as much damage"),),
                    ),
                ),
            ),
            Option(
                "Creatures Near the Line",
                (
                    Facts(
                        (
                            (
                                "Targets",
                                "Each creature within 10 feet of the line but not in it",
                            ),
                            ("Save", "Constitution"),
                            (
                                "Failed save",
                                "The creature takes 8d8 Force damage and is pulled toward the line until the creature is in its area",
                            ),
                            ("Successful save", "No effect"),
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
                                "When you cast this spell using a spell slot of 7th level or higher, the damage increases by 1d8 for each slot level above 6th",
                            ),
                        )
                    ),
                ),
            ),
        ]


SPELLS = [
    ArcaneGate,
    BladeBarrier,
    BonesOfTheEarth,
    ChainLightning,
    CircleOfDeath,
    ConjureFey,
    Contingency,
    CreateHomunculus,
    CreateUndead,
    Dirge,
    Disintegrate,
    DrawmijsInstantSummons,
    DruidGrove,
    ElminstersEffulgentSpheres,
    Eyebite,
    FindThePath,
    FizbansPlatinumShield,
    FleshToStone,
    Forbiddance,
    GlobeOfInvulnerability,
    GravityFissure,
    GuardsAndWards,
    Harm,
    Heal,
    HeroesFeast,
    InvestitureOfFlame,
    InvestitureOfIce,
    InvestitureOfStone,
    InvestitureOfWind,
    LeomundsLamentableBelaborment,
    MagicJar,
    MassSuggestion,
    MentalPrison,
    MoveEarth,
    OtilukesFreezingSphere,
    OttosIrresistibleDance,
    PlanarAlly,
    PrimordialWard,
    ProgrammedIllusion,
    Scatter,
    SoulCage,
    SummonDinosaur,
    SummonFiend,
    Sunbeam,
    TashasBubblingCauldron,
    TashasOtherworldlyGuise,
    TensersTransformation,
    TransportViaPlants,
    TrueSeeing,
    WallOfIce,
    WallOfThorns,
    WindWalk,
    WordOfRecall,
]
