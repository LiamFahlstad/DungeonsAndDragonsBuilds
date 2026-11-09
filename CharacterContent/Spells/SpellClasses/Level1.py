"""Level 1 spells as classes (CharacterContent/Spells/SpellFactory/ClassSpell.py),
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
from Core.Definitions import Ability, CharacterClass, Condition, DamageType
from Model.Content.CombatEffect import (
    CombatCondition,
    CombatDamage,
    CombatEffect,
    CombatHitPoints,
    CombatInstances,
    EffectRoll,
    TurnEdge,
    TurnOf,
)
from Model.Content.Feature import FeatureTarget
from Model.Content.FeatureText import Block, Facts, Option, Paragraph, Table
from Model.View import CharacterView


class AbsorbElements(ClassSpell):
    rules = SpellRules(
        name="Absorb Elements",
        level=1,
        school=School.ABJURATION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.DRUID,
            CharacterClass.RANGER,
            CharacterClass.SORCERER,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(
            CastingTimeType.REACTION,
            trigger="which you take when you take acid, cold, fire, lightning, or thunder damage",
        ),
        range=Range(RangeType.SELF),
        components=Components(somatic=True),
        duration=Duration(DurationType.ROUND, 1),
        source="Xanathar's Guide to Everything",
        description=(
            "The spell captures some of the incoming energy, lessening its effect on you and storing it for your next melee attack. You have resistance to the triggering damage type until the start of your next turn. Also, the first time you hit with a melee attack on your next turn, the target takes an extra 1d6 damage of the triggering type, and the spell ends.\n"
            "At Higher Levels. When you cast this spell using a spell slot of 2nd level or higher, the extra damage increases by 1d6 for each slot level above 1st."
        ),
        usage_tags=("buff", "damage"),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "9cbde18027ea95f5")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "The spell captures some of the incoming energy, lessening its effect on you and storing it for your next melee attack.",
                    ),
                    (
                        "Trigger",
                        "You take acid, cold, fire, lightning, or thunder damage",
                    ),
                    (
                        "Resistance",
                        "To the triggering damage type until the start of your next turn",
                    ),
                    (
                        "Stored energy",
                        "The first time you hit with a melee attack on your next turn, the target takes an extra 1d6 damage of the triggering type, and the spell ends",
                    ),
                )
            ),
            Option(
                "At Higher Levels",
                (Facts((("Extra damage", "+1d6 for each slot level above 1st"),)),),
            ),
        ]

    def combat_effects(
        self, character: CharacterView | None = None
    ) -> list[CombatEffect]:
        return [
            CombatEffect(
                conditions=(CombatCondition("Absorb Elements"),),
                notes=(
                    "You have Resistance to the triggering damage type (Acid, Cold, Fire, Lightning or Thunder) until the start of your next turn.",
                    "The first time you hit with a melee attack on your next turn, the target takes an extra 1d6 damage of that type (1d6 more per slot level above 1), and the spell ends.",
                ),
            )
        ]


class Alarm(ClassSpell):
    rules = SpellRules(
        name="Alarm",
        level=1,
        school=School.ABJURATION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.RANGER,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.MINUTE, 1, ritual=True),
        range=Range(RangeType.FOOT, 30),
        components=Components(
            verbal=True, somatic=True, material="a bell and silver wire"
        ),
        duration=Duration(DurationType.HOUR, 8),
        source="Player's Handbook",
        description=(
            "You set an alarm against intrusion. Choose a door, a window, or an area within range that is no larger than a 20-foot Cube. Until the spell ends, an alarm alerts you whenever a creature touches or enters the warded area. When you cast the spell, you can designate creatures that won’t set off the alarm. You also choose whether the alarm is audible or mental:\n"
            "Audible Alarm. The alarm produces the sound of a handbell for 10 seconds within 60 feet of the warded area.\n"
            "Mental Alarm. You are alerted by a mental ping if you are within 1 mile of the warded area. This ping awakens you if you’re asleep."
        ),
        usage_tags=("control",),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "9151fbdb9c5675f3")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You set an alarm against intrusion."),
            Facts(
                (
                    (
                        "Warded area",
                        "A door, a window, or an area within range that is no larger than a 20-foot Cube",
                    ),
                    (
                        "Trigger",
                        "Until the spell ends, an alarm alerts you whenever a creature touches or enters the warded area",
                    ),
                    (
                        "Exceptions",
                        "When you cast the spell, you can designate creatures that won't set off the alarm",
                    ),
                )
            ),
            Table(
                ("Alarm (choose one)", "Effect"),
                (
                    (
                        "Audible",
                        "The sound of a handbell for 10 seconds within 60 feet of the warded area",
                    ),
                    (
                        "Mental",
                        "A mental ping alerts you if you are within 1 mile of the warded area; it awakens you if you're asleep",
                    ),
                ),
            ),
        ]

    def combat_effects(
        self, character: CharacterView | None = None
    ) -> list[CombatEffect]:
        return []


class Bless(ClassSpell):
    rules = SpellRules(
        name="Bless",
        level=1,
        school=School.ENCHANTMENT,
        classes=(CharacterClass.CLERIC, CharacterClass.PALADIN),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 30),
        components=Components(
            verbal=True, somatic=True, material="a Holy Symbol worth 5+ GP"
        ),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "You bless up to three creatures within range. Whenever a target makes an attack roll or a saving throw before the spell ends, the target adds 1d4 to the attack roll or save.\n"
            "Using a Higher-Level Spell Slot. You can target one additional creature for each spell slot level above 1."
        ),
        usage_tags=("buff",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "2a2ba528f6de6081")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Targets", "Up to three creatures within range"),
                    (
                        "Effect",
                        "Whenever a target makes an attack roll or a saving throw before the spell ends, it adds 1d4 to the roll",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (
                    Facts(
                        (("Targets", "+1 creature for each spell slot level above 1"),)
                    ),
                ),
            ),
        ]

    def combat_effects(
        self, character: CharacterView | None = None
    ) -> list[CombatEffect]:
        return [
            CombatEffect(
                conditions=(CombatCondition("Bless"),),
                notes=(
                    "Each target adds 1d4 to its attack rolls and saving throws for the duration. Up to three creatures, one more per slot level above 1.",
                ),
            )
        ]


class BurningHands(ClassSpell):
    rules = SpellRules(
        name="Burning Hands",
        level=1,
        school=School.EVOCATION,
        classes=(CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "A thin sheet of flames shoots forth from you. Each creature in a 15-foot Cone makes a Dexterity saving throw, taking 3d6 Fire damage on a failed save or half as much damage on a successful one.\n"
            "Flammable objects in the Cone that aren’t being worn or carried start burning.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 1d6 for each spell slot level above 1."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "1f0c7425a4ac2d3b")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Flavor", "A thin sheet of flames shoots forth from you."),
                    ("Area", "15-foot Cone"),
                    ("Save", "Dexterity, made by each creature in the Cone"),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (("3d6 Fire damage", "Half as much damage"),),
            ),
            Facts(
                (
                    (
                        "Objects",
                        "Flammable objects in the Cone that aren't being worn or carried start burning",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Damage", "+1d6 for each spell slot level above 1"),)),),
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
                damage=(CombatDamage("3d6", DamageType.FIRE, upcast="1d6"),),
                notes=(
                    "Each creature in a 15-foot Cone. Flammable objects in it that aren't worn or carried start burning.",
                ),
            )
        ]


class CharmPerson(ClassSpell):
    rules = SpellRules(
        name="Charm Person",
        level=1,
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
            "One Humanoid you can see within range makes a Wisdom saving throw. It does so with Advantage if you or your allies are fighting it. On a failed save, the target has the Charmed condition until the spell ends or until you or your allies damage it. The Charmed creature is Friendly to you. When the spell ends, the target knows it was Charmed by you.\n"
            "Using a Higher-Level Spell Slot. You can target one additional creature for each spell slot level above 1."
        ),
        usage_tags=("control",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "1e005ebb1b18ce52")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You try to charm a Humanoid."),
            Facts(
                (
                    ("Target", "One Humanoid you can see within range"),
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
                        (("Targets", "+1 creature for each spell slot level above 1"),)
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
                save_ability=Ability.WISDOM,
                conditions=(CombatCondition(Condition.CHARMED),),
                notes=(
                    "Humanoids only. The target has Advantage on the save if you or your allies are fighting it.",
                    "It ends early if you or your allies damage the target. One more target per slot level above 1.",
                ),
            )
        ]


class ChromaticOrb(ClassSpell):
    rules = SpellRules(
        name="Chromatic Orb",
        level=1,
        school=School.EVOCATION,
        classes=(CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 90),
        components=Components(
            verbal=True, somatic=True, material="a diamond worth 50+ GP"
        ),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "You hurl an orb of energy at a target within range. Choose Acid, Cold, Fire, Lightning, Poison, or Thunder for the type of orb you create, and then make a ranged spell attack against the target. On a hit, the target takes 3d8 damage of the chosen type.\n"
            "If you roll the same number on two or more of the d8s, the orb leaps to a different target of your choice within 30 feet of the target. Make an attack roll against the new target, and make a new damage roll. The orb can’t leap again unless you cast the spell with a level 2+ spell slot.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 1d8 for each spell slot level above 1. The orb can leap a maximum number of times equal to the level of the slot expended, and a creature can be targeted only once by each casting of this spell."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "1d05d9ae65468b22")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You hurl an orb of energy at a target, and it can leap on to others."
            ),
            Facts(
                (
                    ("Target", "A target within range"),
                    (
                        "Type",
                        "Acid, Cold, Fire, Lightning, Poison, or Thunder (choose when casting)",
                    ),
                    ("Attack", "Ranged spell attack"),
                    ("On a hit", "3d8 damage of the chosen type"),
                )
            ),
            Option(
                "Leap",
                (
                    Facts(
                        (
                            (
                                "Trigger",
                                "You roll the same number on two or more of the d8s",
                            ),
                            (
                                "New target",
                                "A different target of your choice within 30 feet of the target; make a new attack roll and a new damage roll",
                            ),
                            (
                                "Leaps",
                                "One with a level 1 slot; it can't leap again unless cast with a level 2+ slot",
                            ),
                            ("Each creature", "Can be targeted only once per casting"),
                        )
                    ),
                ),
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (
                    Facts(
                        (
                            ("Damage", "+1d8 for each spell slot level above 1"),
                            ("Leaps", "Up to the level of the slot expended"),
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
                roll=EffectRoll.ATTACK,
                damage=(
                    CombatDamage(
                        "3d8",
                        None,
                        (
                            DamageType.ACID,
                            DamageType.COLD,
                            DamageType.FIRE,
                            DamageType.LIGHTNING,
                            DamageType.POISON,
                            DamageType.THUNDER,
                        ),
                        upcast="1d8",
                    ),
                ),
                notes=(
                    "If two or more of the d8s match, the orb leaps to another target within 30 feet: a new attack and damage roll. With a level 2+ slot it can leap as many times as the slot's level, each creature once.",
                ),
            )
        ]


class Command(ClassSpell):
    rules = SpellRules(
        name="Command",
        level=1,
        school=School.ENCHANTMENT,
        classes=(CharacterClass.BARD, CharacterClass.CLERIC, CharacterClass.PALADIN),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "You speak a one-word command to a creature you can see within range. The target must succeed on a Wisdom saving throw or follow the command on its next turn. Choose the command from these options:\n"
            "Approach. The target moves toward you by the shortest and most direct route, ending its turn if it moves within 5 feet of you.\n"
            "Drop. The target drops whatever it is holding and then ends its turn.\n"
            "Flee. The target spends its turn moving away from you by the fastest available means.\n"
            "Grovel. The target has the Prone condition and then ends its turn.\n"
            "Halt. On its turn, the target doesn’t move and takes no action or Bonus Action.\n"
            "Using a Higher-Level Spell Slot. You can affect one additional creature for each spell slot level above 1."
        ),
        usage_tags=("control",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "26e44310036c791a")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You speak a one-word command to a creature, which it must obey on its next turn."
            ),
            Facts(
                (
                    ("Target", "A creature you can see within range"),
                    ("Save", "Wisdom"),
                    ("Failed save", "The target follows the command on its next turn"),
                )
            ),
            Table(
                ("Command", "On its next turn, the target..."),
                (
                    (
                        "Approach",
                        "Moves toward you by the shortest and most direct route, ending its turn if it moves within 5 feet of you",
                    ),
                    ("Drop", "Drops whatever it's holding, then ends its turn"),
                    (
                        "Flee",
                        "Spends its turn moving away from you by the fastest available means",
                    ),
                    ("Grovel", "Has the Prone condition, then ends its turn"),
                    ("Halt", "Doesn't move and takes no action or Bonus Action"),
                ),
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (
                    Facts(
                        (("Targets", "+1 creature for each spell slot level above 1"),)
                    ),
                ),
            ),
        ]

    def combat_effects(
        self, character: CharacterView | None = None
    ) -> list[CombatEffect]:
        return [
            CombatEffect(
                name="Command: Approach",
                roll=EffectRoll.SAVE,
                save_ability=Ability.WISDOM,
                conditions=(
                    CombatCondition("Command", until=(TurnEdge.END, TurnOf.TARGET)),
                ),
                notes=(
                    "On its next turn, the target moves toward you by the shortest and most direct route, ending its turn if it moves within 5 feet of you.",
                    "One more target per slot level above 1.",
                ),
            ),
            CombatEffect(
                name="Command: Drop",
                roll=EffectRoll.SAVE,
                save_ability=Ability.WISDOM,
                conditions=(
                    CombatCondition("Command", until=(TurnEdge.END, TurnOf.TARGET)),
                ),
                notes=(
                    "On its next turn, the target drops whatever it is holding and then ends its turn.",
                    "One more target per slot level above 1.",
                ),
            ),
            CombatEffect(
                name="Command: Flee",
                roll=EffectRoll.SAVE,
                save_ability=Ability.WISDOM,
                conditions=(
                    CombatCondition("Command", until=(TurnEdge.END, TurnOf.TARGET)),
                ),
                notes=(
                    "On its next turn, the target spends its turn moving away from you by the fastest available means.",
                    "One more target per slot level above 1.",
                ),
            ),
            CombatEffect(
                name="Command: Grovel",
                roll=EffectRoll.SAVE,
                save_ability=Ability.WISDOM,
                conditions=(CombatCondition(Condition.PRONE),),
                notes=(
                    "On its next turn, the target has the Prone condition and then ends its turn.",
                    "One more target per slot level above 1.",
                ),
            ),
            CombatEffect(
                name="Command: Halt",
                roll=EffectRoll.SAVE,
                save_ability=Ability.WISDOM,
                conditions=(
                    CombatCondition("Command", until=(TurnEdge.END, TurnOf.TARGET)),
                ),
                notes=(
                    "On its next turn, the target doesn't move and takes no action or Bonus Action.",
                    "One more target per slot level above 1.",
                ),
            ),
        ]


class CureWounds(ClassSpell):
    rules = SpellRules(
        name="Cure Wounds",
        level=1,
        school=School.ABJURATION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.BARD,
            CharacterClass.CLERIC,
            CharacterClass.DRUID,
            CharacterClass.PALADIN,
            CharacterClass.RANGER,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.TOUCH),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "A creature you touch regains a number of Hit Points equal to 2d8 plus your spellcasting ability modifier.\n"
            "Using a Higher-Level Spell Slot. The healing increases by 2d8 for each spell slot level above 1."
        ),
        usage_tags=("heal",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "f97882a42d50f351")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("A creature you touch regains Hit Points."),
            Facts(
                (
                    ("Target", "A creature you touch"),
                    ("Healing", "2d8 + your spellcasting ability modifier"),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Healing", "+2d8 for each spell slot level above 1"),)),),
            ),
        ]

    def combat_effects(
        self, character: CharacterView | None = None
    ) -> list[CombatEffect]:
        return [
            CombatEffect(
                healing=CombatHitPoints(dice="2d8", upcast="2d8", add_modifier=True)
            )
        ]


class DisguiseSelf(ClassSpell):
    rules = SpellRules(
        name="Disguise Self",
        level=1,
        school=School.ILLUSION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.BARD,
            CharacterClass.SORCERER,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.HOUR, 1),
        source="Player's Handbook",
        description=(
            "You make yourself - including your clothing, armor, weapons, and other belongings on your person - look different until the spell ends. You can seem 1 foot shorter or taller and can appear heavier or lighter. You must adopt a form that has the same basic arrangement of limbs as you have. Otherwise, the extent of the illusion is up to you.\n"
            "The changes wrought by this spell fail to hold up to physical inspection. For example, if you use this spell to add a hat to your outfit, objects pass through the hat, and anyone who touches it would feel nothing.\n"
            "To discern that you are disguised, a creature must take the Study action to inspect your appearance and succeed on an Intelligence (Investigation) check against your spell save DC."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "2c612f503b07b48e")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You make yourself look different, including your clothing, armor, weapons, and other belongings on your person."
            ),
            Facts(
                (
                    (
                        "Size",
                        "You can seem 1 foot shorter or taller, and heavier or lighter",
                    ),
                    (
                        "Shape",
                        "Must keep your basic arrangement of limbs; otherwise the illusion is up to you",
                    ),
                    (
                        "Touch",
                        "Fails physical inspection: if you add a hat, objects pass through it, and anyone who touches it feels nothing",
                    ),
                    (
                        "Seeing through",
                        "A creature must take the Study action to inspect your appearance and succeed on an Intelligence (Investigation) check against your spell save DC",
                    ),
                )
            ),
        ]

    def combat_effects(
        self, character: CharacterView | None = None
    ) -> list[CombatEffect]:
        return []


class DissonantWhispers(ClassSpell):
    rules = SpellRules(
        name="Dissonant Whispers",
        level=1,
        school=School.ENCHANTMENT,
        classes=(CharacterClass.BARD,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "One creature of your choice that you can see within range hears a discordant melody in its mind. The target makes a Wisdom saving throw. On a failed save, it takes 3d6 Psychic damage and must immediately use its Reaction, if available, to move as far away from you as it can, using the safest route. On a successful save, the target takes half as much damage only.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 1d6 for each spell slot level above 1."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "e82758ec42b9fbff")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "One creature of your choice that you can see within range hears a discordant melody in its mind.",
                    ),
                    (
                        "Target",
                        "One creature of your choice that you can see within range",
                    ),
                    ("Save", "Wisdom"),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (
                    (
                        "3d6 Psychic damage, and it must immediately use its Reaction, if available, to move as far away from you as it can, using the safest route",
                        "Half as much damage only",
                    ),
                ),
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Damage", "+1d6 for each spell slot level above 1"),)),),
            ),
        ]

    def combat_effects(
        self, character: CharacterView | None = None
    ) -> list[CombatEffect]:
        return [
            CombatEffect(
                roll=EffectRoll.SAVE,
                save_ability=Ability.WISDOM,
                half_on_success=True,
                damage=(CombatDamage("3d6", DamageType.PSYCHIC, upcast="1d6"),),
                notes=(
                    "On a failed save, the target must immediately use its Reaction, if available, to move as far away from you as it can by the safest route.",
                ),
            )
        ]


class DivineSmite(ClassSpell):
    rules = SpellRules(
        name="Divine Smite",
        level=1,
        school=School.EVOCATION,
        classes=(CharacterClass.PALADIN,),
        casting_time=CastingTime(
            CastingTimeType.BONUS_ACTION,
            trigger="which you take immediately after hitting a target with a Melee weapon or an Unarmed Strike",
        ),
        range=Range(RangeType.SELF),
        components=Components(verbal=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "The target takes an extra 2d8 Radiant damage from the attack. The damage increases by 1d8 if the target is a Fiend or an Undead.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 1d8 for each spell slot level above 1."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "bfdb523f95bd2d3b")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Trigger",
                        "Immediately after you hit a target with a Melee weapon or an Unarmed Strike",
                    ),
                    (
                        "Damage",
                        "The target takes an extra 2d8 Radiant damage from the attack",
                    ),
                    (
                        "Fiend or Undead",
                        "The damage increases by 1d8 if the target is a Fiend or an Undead",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Damage", "+1d8 for each spell slot level above 1"),)),),
            ),
        ]

    def combat_effects(
        self, character: CharacterView | None = None
    ) -> list[CombatEffect]:
        return [
            CombatEffect(
                damage=(
                    CombatDamage("2d8", DamageType.RADIANT, upcast="1d8"),
                    CombatDamage(
                        "1d8",
                        DamageType.RADIANT,
                        when="the target is a Fiend or an Undead",
                    ),
                ),
                notes=(
                    "Cast right after hitting a target with a Melee weapon or an Unarmed Strike: pick that target. On a critical hit, roll the dice twice.",
                ),
            )
        ]


class EnsnaringStrike(ClassSpell):
    rules = SpellRules(
        name="Ensnaring Strike",
        level=1,
        school=School.CONJURATION,
        classes=(CharacterClass.RANGER,),
        casting_time=CastingTime(
            CastingTimeType.BONUS_ACTION,
            trigger="which you take immediately after hitting a creature with a weapon",
        ),
        range=Range(RangeType.SELF),
        components=Components(verbal=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "As you hit the target, grasping vines appear on it, and it makes a Strength saving throw. A Large or larger creature has Advantage on this save. On a failed save, the target has the Restrained condition until the spell ends. On a successful save, the vines shrivel away, and the spell ends.\n"
            "While Restrained, the target takes 1d6 Piercing damage at the start of each of its turns. The target or a creature within reach of it can take an action to make a Strength (Athletics) check against your spell save DC. On a success, the spell ends.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 1d6 for each spell slot level above 1."
        ),
        usage_tags=("buff", "control", "damage"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "dbdf4c1f3f6265c3")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "As you hit the target, grasping vines appear on it, and it makes a Strength saving throw.",
                    ),
                    ("Trigger", "Immediately after you hit a creature with a weapon"),
                    ("Save", "Strength; a Large or larger creature has Advantage"),
                    ("Failed save", "Restrained until the spell ends"),
                    ("Successful save", "The vines shrivel away, and the spell ends"),
                )
            ),
            Facts(
                (
                    (
                        "While Restrained",
                        "The target takes 1d6 Piercing damage at the start of each of its turns",
                    ),
                    (
                        "Escape",
                        "The target or a creature within reach of it can take an action to make a Strength (Athletics) check against your spell save DC; on a success, the spell ends",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Damage", "+1d6 for each spell slot level above 1"),)),),
            ),
        ]

    def combat_effects(
        self, character: CharacterView | None = None
    ) -> list[CombatEffect]:
        return [
            CombatEffect(
                roll=EffectRoll.SAVE,
                save_ability=Ability.STRENGTH,
                conditions=(CombatCondition(Condition.RESTRAINED),),
                notes=(
                    "Cast right after hitting with a weapon. A Large or larger creature has Advantage on the save. On a success the spell ends.",
                    "While Restrained, the target takes 1d6 Piercing damage (1d6 more per slot level above 1) at the start of each of its turns. It or a creature within reach can take an action to make a Strength (Athletics) check against your spell save DC to end the spell.",
                ),
            )
        ]


class Entangle(ClassSpell):
    rules = SpellRules(
        name="Entangle",
        level=1,
        school=School.CONJURATION,
        classes=(CharacterClass.DRUID, CharacterClass.RANGER),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 90),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "Grasping plants sprout from the ground in a 20-foot square within range. For the duration, these plants turn the ground in the area into Difficult Terrain. They disappear when the spell ends.\n"
            "Each creature (other than you) in the area when you cast the spell must succeed on a Strength saving throw or have the Restrained condition until the spell ends. A Restrained creature can take an action to make a Strength (Athletics) check against your spell save DC. On a success, it frees itself from the grasping plants and is no longer Restrained by them."
        ),
        usage_tags=("control",),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "b85481a70449b4b3")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "Grasping plants sprout from the ground in a 20-foot square within range.",
                    ),
                    ("Area", "20-foot square within range"),
                    (
                        "Terrain",
                        "The ground in the area is Difficult Terrain for the duration; the plants disappear when the spell ends",
                    ),
                    (
                        "Save",
                        "Strength, made by each creature (other than you) in the area when you cast the spell",
                    ),
                    ("Failed save", "Restrained until the spell ends"),
                    (
                        "Escape",
                        "A Restrained creature can take an action to make a Strength (Athletics) check against your spell save DC, freeing itself on a success",
                    ),
                )
            )
        ]

    def combat_effects(
        self, character: CharacterView | None = None
    ) -> list[CombatEffect]:
        return [
            CombatEffect(
                roll=EffectRoll.SAVE,
                save_ability=Ability.STRENGTH,
                conditions=(CombatCondition(Condition.RESTRAINED),),
                notes=(
                    "Each creature other than you in the 20-foot square. The area is Difficult Terrain for the duration.",
                    "A Restrained creature can take an action to make a Strength (Athletics) check against your spell save DC to free itself.",
                ),
            )
        ]


class FaerieFire(ClassSpell):
    rules = SpellRules(
        name="Faerie Fire",
        level=1,
        school=School.EVOCATION,
        classes=(CharacterClass.ARTIFICER, CharacterClass.BARD, CharacterClass.DRUID),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "Objects in a 20-foot Cube within range are outlined in blue, green, or violet light (your choice). Each creature in the Cube is also outlined if it fails a Dexterity saving throw. For the duration, objects and affected creatures shed Dim Light in a 10-foot radius and can’t benefit from the Invisible condition.\n"
            "Attack rolls against an affected creature or object have Advantage if the attacker can see it."
        ),
        usage_tags=("control",),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "218f38789348b8e6")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "Objects and creatures in an area are outlined in light, revealing them."
            ),
            Facts(
                (
                    ("Area", "20-foot Cube within range"),
                    ("Color", "Blue, green, or violet (your choice)"),
                    ("Objects", "Every object in the Cube is outlined"),
                    (
                        "Creatures",
                        "Each creature in the Cube is outlined if it fails a Dexterity save",
                    ),
                    (
                        "Outlined",
                        "Sheds Dim Light in a 10-foot radius and can't benefit from the Invisible condition",
                    ),
                    (
                        "Attacks",
                        "Attack rolls against an outlined creature or object have Advantage if the attacker can see it",
                    ),
                )
            ),
        ]

    def combat_effects(
        self, character: CharacterView | None = None
    ) -> list[CombatEffect]:
        return [
            CombatEffect(
                roll=EffectRoll.SAVE,
                save_ability=Ability.DEXTERITY,
                conditions=(CombatCondition("Faerie Fire"),),
                notes=(
                    "An affected creature sheds Dim Light, can't benefit from the Invisible condition, and attack rolls against it have Advantage if the attacker can see it.",
                ),
            )
        ]


class FalseLife(ClassSpell):
    rules = SpellRules(
        name="False Life",
        level=1,
        school=School.NECROMANCY,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.SORCERER,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True, material="a drop of alcohol"),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "You gain 2d4 + 4 Temporary Hit Points.\n"
            "Using a Higher-Level Spell Slot. You gain 5 additional Temporary Hit Points for each spell slot level above 1."
        ),
        usage_tags=("heal",),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "41a0bb3ca2200d58")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts((("Temporary Hit Points", "You gain 2d4 + 4 Temporary Hit Points"),)),
            Option(
                "Using a Higher-Level Spell Slot",
                (
                    Facts(
                        (
                            (
                                "Temporary Hit Points",
                                "+5 for each spell slot level above 1",
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
                temp_hp=CombatHitPoints(dice="2d4 + 4", upcast="5"),
                notes=("They're the caster's: pick the caster as the target.",),
            )
        ]


class FeatherFall(ClassSpell):
    rules = SpellRules(
        name="Feather Fall",
        level=1,
        school=School.TRANSMUTATION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.BARD,
            CharacterClass.SORCERER,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(
            CastingTimeType.REACTION,
            trigger="which you take when you or a creature you can see within 60 feet of you falls",
        ),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True, material="a small feather or piece of down"),
        duration=Duration(DurationType.MINUTE, 1),
        source="Player's Handbook",
        description="Choose up to five falling creatures within range. A falling creature’s rate of descent slows to 60 feet per round until the spell ends. If a creature lands before the spell ends, the creature takes no damage from the fall, and the spell ends for that creature.",
        usage_tags=("buff",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "e5a258628a284df8")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You slow the fall of up to five creatures."),
            Facts(
                (
                    (
                        "Trigger",
                        "You or a creature you can see within 60 feet of you falls",
                    ),
                    ("Targets", "Up to five falling creatures within range"),
                    (
                        "Descent",
                        "A falling creature's rate of descent slows to 60 feet per round until the spell ends",
                    ),
                    (
                        "Landing",
                        "If a creature lands before the spell ends, it takes no damage from the fall, and the spell ends for that creature",
                    ),
                )
            ),
        ]

    def combat_effects(
        self, character: CharacterView | None = None
    ) -> list[CombatEffect]:
        return [
            CombatEffect(
                conditions=(CombatCondition("Feather Fall"),),
                notes=(
                    "Up to five falling creatures descend 60 feet per round and take no damage from the fall when they land, which ends the spell for them.",
                ),
            )
        ]


class FogCloud(ClassSpell):
    rules = SpellRules(
        name="Fog Cloud",
        level=1,
        school=School.CONJURATION,
        classes=(
            CharacterClass.DRUID,
            CharacterClass.RANGER,
            CharacterClass.SORCERER,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 120),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.HOUR, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "You create a 20-foot-radius Sphere of fog centered on a point within range. The Sphere is Heavily Obscured. It lasts for the duration or until a strong wind (such as one created by Gust of Wind) disperses it.\n"
            "Using a Higher-Level Spell Slot. The fog’s radius increases by 20 feet for each spell slot level above 1."
        ),
        usage_tags=("control",),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "b0d4e6ce3bcf2baa")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You create a Sphere of fog."),
            Facts(
                (
                    ("Area", "20-foot-radius Sphere centered on a point within range"),
                    ("Visibility", "The Sphere is Heavily Obscured"),
                    (
                        "Lasts",
                        "For the duration, or until a strong wind (such as one created by Gust of Wind) disperses it",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Radius", "+20 feet for each spell slot level above 1"),)),),
            ),
        ]

    def combat_effects(
        self, character: CharacterView | None = None
    ) -> list[CombatEffect]:
        return []


class Grease(ClassSpell):
    rules = SpellRules(
        name="Grease",
        level=1,
        school=School.CONJURATION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.SORCERER,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(
            verbal=True, somatic=True, material="a bit of pork rind or butter"
        ),
        duration=Duration(DurationType.MINUTE, 1),
        source="Player's Handbook",
        description=(
            "Nonflammable grease covers the ground in a 10-foot square centered on a point within range and turns it into Difficult Terrain for the duration.\n"
            "When the grease appears, each creature standing in its area must succeed on a Dexterity saving throw or have the Prone condition. A creature that enters the area or ends its turn there must also succeed on that save or fall Prone."
        ),
        usage_tags=("control",),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "93a54aabccf31cb9")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("Nonflammable grease covers the ground."),
            Facts(
                (
                    ("Area", "10-foot square centered on a point within range"),
                    ("Terrain", "Difficult Terrain for the duration"),
                    (
                        "Save",
                        "Dexterity, made by each creature standing in the area when the grease appears, and by a creature that enters the area or ends its turn there",
                    ),
                    ("Failed save", "The creature has the Prone condition"),
                    ("Successful save", "No effect"),
                )
            ),
        ]

    def combat_effects(
        self, character: CharacterView | None = None
    ) -> list[CombatEffect]:
        return [
            CombatEffect(
                roll=EffectRoll.SAVE,
                save_ability=Ability.DEXTERITY,
                conditions=(CombatCondition(Condition.PRONE),),
                notes=(
                    "The 10-foot square is Difficult Terrain for the duration. A creature that enters it or ends its turn there makes the save again or falls Prone.",
                ),
            )
        ]


class GuidingBolt(ClassSpell):
    rules = SpellRules(
        name="Guiding Bolt",
        level=1,
        school=School.EVOCATION,
        classes=(CharacterClass.CLERIC,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 120),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.ROUND, 1),
        source="Player's Handbook",
        description=(
            "You hurl a bolt of light toward a creature within range. Make a ranged spell attack against the target. On a hit, it takes 4d6 Radiant damage, and the next attack roll made against it before the end of your next turn has Advantage.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 1d6 for each spell slot level above 1."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "1abf69ec1fda5d19")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You hurl a bolt of light toward a creature within range.",
                    ),
                    ("Target", "A creature within range"),
                    ("Attack", "Ranged spell attack"),
                    (
                        "On a hit",
                        "4d6 Radiant damage, and the next attack roll made against it before the end of your next turn has Advantage",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Damage", "+1d6 for each spell slot level above 1"),)),),
            ),
        ]

    def combat_effects(
        self, character: CharacterView | None = None
    ) -> list[CombatEffect]:
        return [
            CombatEffect(
                roll=EffectRoll.ATTACK,
                damage=(CombatDamage("4d6", DamageType.RADIANT, upcast="1d6"),),
                notes=(
                    "On a hit, the next attack roll against the target before the end of your next turn has Advantage.",
                ),
            )
        ]


class HealingWord(ClassSpell):
    rules = SpellRules(
        name="Healing Word",
        level=1,
        school=School.ABJURATION,
        classes=(CharacterClass.BARD, CharacterClass.CLERIC, CharacterClass.DRUID),
        casting_time=CastingTime(CastingTimeType.BONUS_ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "A creature of your choice that you can see within range regains Hit Points equal to 2d4 plus your spellcasting ability modifier.\n"
            "Using a Higher-Level Spell Slot. The healing increases by 2d4 for each spell slot level above 1."
        ),
        usage_tags=("heal",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "2abc67b3481ed9f9")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("A creature you can see regains Hit Points."),
            Facts(
                (
                    (
                        "Target",
                        "A creature of your choice that you can see within range",
                    ),
                    ("Healing", "2d4 + your spellcasting ability modifier"),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Healing", "+2d4 for each spell slot level above 1"),)),),
            ),
        ]

    def combat_effects(
        self, character: CharacterView | None = None
    ) -> list[CombatEffect]:
        return [
            CombatEffect(
                healing=CombatHitPoints(dice="2d4", upcast="2d4", add_modifier=True)
            )
        ]


class HuntersMark(ClassSpell):
    rules = SpellRules(
        name="Hunter's Mark",
        level=1,
        school=School.DIVINATION,
        classes=(CharacterClass.RANGER,),
        casting_time=CastingTime(CastingTimeType.BONUS_ACTION),
        range=Range(RangeType.FOOT, 90),
        components=Components(verbal=True),
        duration=Duration(DurationType.HOUR, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "You magically mark one creature you can see within range as your quarry. Until the spell ends, you deal an extra 1d6 Force damage to the target whenever you hit it with an attack roll. You also have Advantage on any Wisdom (Perception or Survival) check you make to find it.\n"
            "If the target drops to 0 Hit Points before this spell ends, you can take a Bonus Action to move the mark to a new creature you can see within range.\n"
            "Using a Higher-Level Spell Slot. Your Concentration can last longer with a spell slot of level 3–4 (up to 8 hours) or 5+ (up to 24 hours)."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "3fba3f140f28f7a0")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You magically mark a creature as your quarry."),
            Facts(
                (
                    ("Target", "One creature you can see within range"),
                    (
                        "Extra damage",
                        "1d6 Force damage whenever you hit it with an attack roll",
                    ),
                    (
                        "Tracking",
                        "Advantage on Wisdom (Perception or Survival) checks to find it",
                    ),
                    (
                        "Move the mark",
                        "If the target drops to 0 Hit Points before the spell ends, you can take a Bonus Action to move the mark to a new creature you can see within range",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (
                    Table(
                        ("Slot level", "Concentration lasts up to"),
                        (("1-2", "1 hour"), ("3-4", "8 hours"), ("5+", "24 hours")),
                    ),
                ),
            ),
        ]

    def combat_effects(
        self, character: CharacterView | None = None
    ) -> list[CombatEffect]:
        return [
            CombatEffect(
                conditions=(CombatCondition("Hunter's Mark"),),
                notes=(
                    "You deal an extra 1d6 Force damage to the target whenever you hit it with an attack roll, and have Advantage on Wisdom (Perception or Survival) checks to find it.",
                    "If it drops to 0 Hit Points, a Bonus Action moves the mark to a new creature.",
                ),
            )
        ]


class IceKnife(ClassSpell):
    rules = SpellRules(
        name="Ice Knife",
        level=1,
        school=School.CONJURATION,
        classes=(CharacterClass.DRUID, CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(
            somatic=True, material="a drop of water or a piece of ice"
        ),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "You create a shard of ice and fling it at one creature within range. Make a ranged spell attack against the target. On a hit, the target takes 1d10 Piercing damage. Hit or miss, the shard then explodes. The target and each creature within 5 feet of it must succeed on a Dexterity saving throw or take 2d6 Cold damage.\n"
            "Using a Higher-Level Spell Slot. The Cold damage increases by 1d6 for each spell slot level above 1."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "80932f05b1ec0493")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You fling a shard of ice that explodes."),
            Facts(
                (
                    ("Target", "One creature within range"),
                    ("Attack", "Ranged spell attack"),
                    ("On a hit", "1d10 Piercing damage"),
                )
            ),
            Option(
                "Explosion",
                (
                    Facts(
                        (
                            ("When", "Hit or miss, the shard then explodes"),
                            (
                                "Targets",
                                "The target and each creature within 5 feet of it",
                            ),
                            ("Save", "Dexterity"),
                            ("Failed save", "2d6 Cold damage"),
                            ("Successful save", "No damage"),
                        )
                    ),
                ),
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Cold damage", "+1d6 for each spell slot level above 1"),)),),
            ),
        ]

    def combat_effects(
        self, character: CharacterView | None = None
    ) -> list[CombatEffect]:
        return [
            CombatEffect(
                name="Ice Knife: shard",
                roll=EffectRoll.ATTACK,
                damage=(CombatDamage("1d10", DamageType.PIERCING),),
                notes=(
                    "Hit or miss, the shard then explodes: pick Ice Knife: explosion next.",
                ),
            ),
            CombatEffect(
                name="Ice Knife: explosion",
                roll=EffectRoll.SAVE,
                save_ability=Ability.DEXTERITY,
                damage=(CombatDamage("2d6", DamageType.COLD, upcast="1d6"),),
                spends_use=False,
                notes=(
                    "The target and each creature within 5 feet of it. Part of the same casting: it spends no slot.",
                ),
            ),
        ]


class Longstrider(ClassSpell):
    rules = SpellRules(
        name="Longstrider",
        level=1,
        school=School.TRANSMUTATION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.BARD,
            CharacterClass.DRUID,
            CharacterClass.RANGER,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.TOUCH),
        components=Components(verbal=True, somatic=True, material="a pinch of dirt"),
        duration=Duration(DurationType.HOUR, 1),
        source="Player's Handbook",
        description=(
            "You touch a creature. The target’s Speed increases by 10 feet until the spell ends.\n"
            "Using a Higher-Level Spell Slot. You can target one additional creature for each spell slot level above 1."
        ),
        usage_tags=("buff",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "a1c44d0245e40ef9")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Target", "A creature you touch"),
                    ("Effect", "Its Speed increases by 10 feet until the spell ends"),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (
                    Facts(
                        (("Targets", "+1 creature for each spell slot level above 1"),)
                    ),
                ),
            ),
        ]

    def combat_effects(
        self, character: CharacterView | None = None
    ) -> list[CombatEffect]:
        return [
            CombatEffect(
                conditions=(CombatCondition("Longstrider"),),
                notes=(
                    "The target's Speed increases by 10 feet. One more target per slot level above 1.",
                ),
            )
        ]


class MagicMissile(ClassSpell):
    rules = SpellRules(
        name="Magic Missile",
        level=1,
        school=School.EVOCATION,
        classes=(CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 120),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "You create three glowing darts of magical force. Each dart strikes a creature of your choice that you can see within range. A dart deals 1d4 + 1 Force damage to its target. The darts all strike simultaneously, and you can direct them to hit one creature or several.\n"
            "Using a Higher-Level Spell Slot. The spell creates one more dart for each spell slot level above 1."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "51090f0ac39a8b23")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Flavor", "You create three glowing darts of magical force."),
                    ("Darts", "Three"),
                    (
                        "Targets",
                        "Each dart strikes a creature of your choice that you can see within range",
                    ),
                    ("Damage", "1d4 + 1 Force damage per dart"),
                    (
                        "Striking",
                        "The darts all strike simultaneously, and you can direct them to hit one creature or several",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Darts", "+1 dart for each spell slot level above 1"),)),),
            ),
        ]

    def combat_effects(
        self, character: CharacterView | None = None
    ) -> list[CombatEffect]:
        return [
            CombatEffect(
                damage=(CombatDamage("1d4 + 1", DamageType.FORCE),),
                instances=CombatInstances(3, upcast=1, noun="dart"),
                notes=(
                    "Each dart strikes a creature of your choice: lower Times and apply again to split them.",
                ),
            )
        ]


class RayOfSickness(ClassSpell):
    rules = SpellRules(
        name="Ray of Sickness",
        level=1,
        school=School.NECROMANCY,
        classes=(CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "You shoot a greenish ray at a creature within range. Make a ranged spell attack against the target. On a hit, the target takes 2d8 Poison damage and has the Poisoned condition until the end of your next turn.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 1d8 for each spell slot level above 1."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "a94ca091a84a8b18")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Flavor", "You shoot a greenish ray at a creature within range."),
                    ("Target", "A creature within range"),
                    ("Attack", "Ranged spell attack"),
                    (
                        "On a hit",
                        "2d8 Poison damage, and the target has the Poisoned condition until the end of your next turn",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Damage", "+1d8 for each spell slot level above 1"),)),),
            ),
        ]

    def combat_effects(
        self, character: CharacterView | None = None
    ) -> list[CombatEffect]:
        return [
            CombatEffect(
                roll=EffectRoll.ATTACK,
                damage=(CombatDamage("2d8", DamageType.POISON, upcast="1d8"),),
                conditions=(
                    CombatCondition(
                        Condition.POISONED, until=(TurnEdge.END, TurnOf.SOURCE)
                    ),
                ),
            )
        ]


class Shield(ClassSpell):
    rules = SpellRules(
        name="Shield",
        level=1,
        school=School.ABJURATION,
        classes=(CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(
            CastingTimeType.REACTION,
            trigger="which you take when you are hit by an attack roll or targeted by the",
        ),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.ROUND, 1),
        source="Player's Handbook",
        description="An imperceptible barrier of magical force protects you. Until the start of your next turn, you have a +5 bonus to AC, including against the triggering attack, and you take no damage from Magic Missile .",
        usage_tags=("buff", "control"),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "7f57072fb9646fc0")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "An imperceptible barrier of magical force protects you.",
                    ),
                    (
                        "Trigger",
                        "You are hit by an attack roll or targeted by the Magic Missile spell",
                    ),
                    (
                        "AC",
                        "+5 until the start of your next turn, including against the triggering attack",
                    ),
                    (
                        "Magic Missile",
                        "You take no damage from it until the start of your next turn",
                    ),
                )
            )
        ]

    def combat_effects(
        self, character: CharacterView | None = None
    ) -> list[CombatEffect]:
        return [
            CombatEffect(
                conditions=(CombatCondition("Shield"),),
                notes=(
                    "+5 to your AC until the start of your next turn, including against the triggering attack, and no damage from Magic Missile.",
                ),
            )
        ]


class ShieldOfFaith(ClassSpell):
    rules = SpellRules(
        name="Shield of Faith",
        level=1,
        school=School.ABJURATION,
        classes=(CharacterClass.CLERIC, CharacterClass.PALADIN),
        casting_time=CastingTime(CastingTimeType.BONUS_ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True, somatic=True, material="a prayer scroll"),
        duration=Duration(DurationType.MINUTE, 10, concentration=True),
        source="Player's Handbook",
        description="A shimmering field surrounds a creature of your choice within range, granting it a +2 bonus to AC for the duration.",
        usage_tags=("buff",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "1d2bb88a4a267c4f")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "A shimmering field surrounds a creature of your choice within range, granting it a +2 bonus to AC for the duration.",
                    ),
                    ("Target", "A creature of your choice within range"),
                    ("Effect", "+2 bonus to AC for the duration"),
                )
            )
        ]

    def combat_effects(
        self, character: CharacterView | None = None
    ) -> list[CombatEffect]:
        return [
            CombatEffect(
                conditions=(CombatCondition("Shield of Faith"),),
                notes=(
                    "A creature of your choice gets a +2 bonus to AC for the duration.",
                ),
            )
        ]


class Sleep(ClassSpell):
    rules = SpellRules(
        name="Sleep",
        level=1,
        school=School.ENCHANTMENT,
        classes=(CharacterClass.BARD, CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(
            verbal=True, somatic=True, material="a pinch of sand or rose petals"
        ),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "Each creature of your choice in a 5-foot-radius Sphere centered on a point within range must succeed on a Wisdom saving throw or have the Incapacitated condition until the end of its next turn, at which point it must repeat the save. If the target fails the second save, the target has the Unconscious condition for the duration. The spell ends on a target if it takes damage or someone within 5 feet of it takes an action to shake it out of the spell’s effect.\n"
            "Creatures that don’t sleep, such as elves, or that have Immunity to the Exhaustion condition automatically succeed on saves against this spell."
        ),
        usage_tags=("control",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "a38f7b26bd801179")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Area", "5-foot-radius Sphere centered on a point within range"),
                    ("Targets", "Each creature of your choice in the area"),
                    ("Save", "Wisdom"),
                    (
                        "Auto-success",
                        "Creatures that don't sleep, such as elves, or that have Immunity to the Exhaustion condition automatically succeed on saves against this spell",
                    ),
                )
            ),
            Table(
                ("Save", "If it fails"),
                (
                    (
                        "First save",
                        "Incapacitated until the end of its next turn, when it repeats the save",
                    ),
                    ("Second save", "Unconscious for the duration"),
                ),
            ),
            Facts(
                (
                    (
                        "Waking",
                        "The spell ends on a target if it takes damage, or someone within 5 feet of it takes an action to shake it out of the spell's effect",
                    ),
                )
            ),
        ]

    def combat_effects(
        self, character: CharacterView | None = None
    ) -> list[CombatEffect]:
        return [
            CombatEffect(
                roll=EffectRoll.SAVE,
                save_ability=Ability.WISDOM,
                conditions=(
                    CombatCondition(
                        Condition.INCAPACITATED, until=(TurnEdge.END, TurnOf.TARGET)
                    ),
                ),
                notes=(
                    "At the end of its next turn the target repeats the save: on a failure it has the Unconscious condition for the duration. It wakes if it takes damage or someone within 5 feet takes an action to shake it. Creatures that don't sleep, or are immune to Exhaustion, succeed automatically.",
                ),
            )
        ]


class SpeakWithAnimals(ClassSpell):
    rules = SpellRules(
        name="Speak with Animals",
        level=1,
        school=School.DIVINATION,
        classes=(
            CharacterClass.BARD,
            CharacterClass.DRUID,
            CharacterClass.RANGER,
            CharacterClass.WARLOCK,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION, ritual=True),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 10),
        source="Player's Handbook",
        description=(
            "For the duration, you can comprehend and verbally communicate with Beasts, and you can use any of the Influence action’s skill options with them.\n"
            "Most Beasts have little to say about topics that don’t pertain to survival or companionship, but at minimum, a Beast can give you information about nearby locations and monsters, including whatever it has perceived within the past day."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "fd41f790dd467891")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("For the duration, you can talk with Beasts."),
            Facts(
                (
                    (
                        "Talking",
                        "You can comprehend and verbally communicate with Beasts",
                    ),
                    (
                        "Influence",
                        "You can use any of the Influence action's skill options with them",
                    ),
                    (
                        "Topics",
                        "Most Beasts have little to say about topics that don't pertain to survival or companionship",
                    ),
                    (
                        "At minimum",
                        "A Beast can give you information about nearby locations and monsters, including whatever it has perceived within the past day",
                    ),
                )
            ),
        ]

    def combat_effects(
        self, character: CharacterView | None = None
    ) -> list[CombatEffect]:
        return []


class TashasHideousLaughter(ClassSpell):
    rules = SpellRules(
        name="Tasha's Hideous Laughter",
        level=1,
        school=School.ENCHANTMENT,
        classes=(CharacterClass.BARD, CharacterClass.WARLOCK, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 30),
        components=Components(
            verbal=True, somatic=True, material="a tart and a feather"
        ),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "One creature of your choice that you can see within range makes a Wisdom saving throw. On a failed save, it has the Prone and Incapacitated conditions for the duration. During that time, it laughs uncontrollably if it’s capable of laughter, and it can’t end the Prone condition on itself.\n"
            "At the end of each of its turns and each time it takes damage, it makes another Wisdom saving throw. The target has Advantage on the save if the save is triggered by damage. On a successful save, the spell ends.\n"
            "Using a Higher-Level Spell Slot. You can target one additional creature for each spell slot level above 1."
        ),
        usage_tags=("buff",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "2089d2e8045df39c")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Target", "One creature of your choice you can see within range"),
                    ("Save", "Wisdom"),
                    (
                        "Failed save",
                        "Prone and Incapacitated for the duration; it laughs uncontrollably if capable of laughter, and it can't end the Prone condition on itself",
                    ),
                    (
                        "Repeat save",
                        "At the end of each of its turns, and each time it takes damage (with Advantage when triggered by damage); on a success, the spell ends",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (
                    Facts(
                        (("Targets", "+1 creature for each spell slot level above 1"),)
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
                save_ability=Ability.WISDOM,
                repeat_save=True,
                conditions=(
                    CombatCondition(Condition.INCAPACITATED),
                    CombatCondition(Condition.PRONE),
                ),
                notes=(
                    "It can't end the Prone condition on itself. It also repeats the save each time it takes damage, with Advantage.",
                    "One more target per slot level above 1.",
                ),
            )
        ]


class Thunderwave(ClassSpell):
    rules = SpellRules(
        name="Thunderwave",
        level=1,
        school=School.EVOCATION,
        classes=(
            CharacterClass.BARD,
            CharacterClass.DRUID,
            CharacterClass.SORCERER,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "You unleash a wave of thunderous energy. Each creature in a 15-foot Cube originating from you makes a Constitution saving throw. On a failed save, a creature takes 2d8 Thunder damage and is pushed 10 feet away from you. On a successful save, a creature takes half as much damage only.\n"
            "In addition, unsecured objects that are entirely within the Cube are pushed 10 feet away from you, and a thunderous boom is audible within 300 feet.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 1d8 for each spell slot level above 1."
        ),
        usage_tags=("control", "damage"),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "5232861c80b1697f")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Flavor", "You unleash a wave of thunderous energy."),
                    ("Area", "15-foot Cube originating from you"),
                    ("Save", "Constitution, made by each creature in the area"),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (
                    (
                        "2d8 Thunder damage and pushed 10 feet away from you",
                        "Half as much damage only",
                    ),
                ),
            ),
            Facts(
                (
                    (
                        "Objects",
                        "Unsecured objects entirely within the Cube are pushed 10 feet away from you",
                    ),
                    ("Sound", "A thunderous boom audible within 300 feet"),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Damage", "+1d8 for each spell slot level above 1"),)),),
            ),
        ]

    def combat_effects(
        self, character: CharacterView | None = None
    ) -> list[CombatEffect]:
        return [
            CombatEffect(
                roll=EffectRoll.SAVE,
                save_ability=Ability.CONSTITUTION,
                half_on_success=True,
                damage=(CombatDamage("2d8", DamageType.THUNDER, upcast="1d8"),),
                notes=(
                    "Each creature in a 15-foot Cube from you. On a failed save it's also pushed 10 feet away from you.",
                ),
            )
        ]


class WitchBolt(ClassSpell):
    rules = SpellRules(
        name="Witch Bolt",
        level=1,
        school=School.EVOCATION,
        classes=(
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(
            verbal=True, somatic=True, material="a twig struck by lightning"
        ),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "A beam of crackling energy lances toward a creature within range, forming a sustained arc of lightning between you and the target. Make a ranged spell attack against it. On a hit, the target takes 2d12 Lightning damage.\n"
            "On each of your subsequent turns, you can take a Bonus Action to deal 1d12 Lightning damage to the target automatically, even if the first attack missed.\n"
            "The spell ends if the target is ever outside the spell’s range or if it has Total Cover from you.\n"
            "Using a Higher-Level Spell Slot. The initial damage increases by 1d12 for each spell slot level above 1."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "845972c6183692af")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "A beam of crackling energy lances toward a creature within range, forming a sustained arc of lightning between you and the target.",
                    ),
                    ("Target", "A creature within range"),
                    ("Attack", "Ranged spell attack"),
                    ("On a hit", "2d12 Lightning damage"),
                    (
                        "Later turns",
                        "On each of your subsequent turns, you can take a Bonus Action to deal 1d12 Lightning damage to the target automatically, even if the first attack missed",
                    ),
                    (
                        "Ends early",
                        "If the target is ever outside the spell's range or if it has Total Cover from you",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (
                    Facts(
                        (("Initial damage", "+1d12 for each spell slot level above 1"),)
                    ),
                ),
            ),
        ]

    def combat_effects(
        self, character: CharacterView | None = None
    ) -> list[CombatEffect]:
        return [
            CombatEffect(
                roll=EffectRoll.ATTACK,
                damage=(CombatDamage("2d12", DamageType.LIGHTNING, upcast="1d12"),),
                notes=(
                    "On each of your later turns, a Bonus Action deals 1d12 Lightning damage to the target automatically, even if the first attack missed. It ends if the target is out of range or has Total Cover from you.",
                ),
            )
        ]


SPELLS = [
    AbsorbElements,
    Alarm,
    Bless,
    BurningHands,
    CharmPerson,
    ChromaticOrb,
    Command,
    CureWounds,
    DisguiseSelf,
    DissonantWhispers,
    DivineSmite,
    EnsnaringStrike,
    Entangle,
    FaerieFire,
    FalseLife,
    FeatherFall,
    FogCloud,
    Grease,
    GuidingBolt,
    HealingWord,
    HuntersMark,
    IceKnife,
    Longstrider,
    MagicMissile,
    RayOfSickness,
    Shield,
    ShieldOfFaith,
    Sleep,
    SpeakWithAnimals,
    TashasHideousLaughter,
    Thunderwave,
    WitchBolt,
]
