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
from Model.Content.CombatModifiers import (
    ArmorClass,
    ArmorClassBase,
    AtTurnStart,
    AttackKind,
    AttacksAgainst,
    ConditionImmunity,
    D20Bonus,
    D20Test,
    ExtraDamageFrom,
    ExtraDamageOnHit,
    RollMode,
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
                conditions=(
                    CombatCondition(
                        "Bless",
                        modifiers=(
                            D20Bonus(
                                (D20Test.ATTACK_ROLL, D20Test.SAVING_THROW), "1d4"
                            ),
                        ),
                    ),
                ),
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
                conditions=(
                    CombatCondition(
                        "Hunter's Mark",
                        modifiers=(ExtraDamageFrom("1d6", DamageType.FORCE),),
                    ),
                ),
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
                conditions=(
                    CombatCondition("Shield of Faith", modifiers=(ArmorClass(2),)),
                ),
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


class AnimalFriendship(ClassSpell):
    rules = SpellRules(
        name="Animal Friendship",
        level=1,
        school=School.ENCHANTMENT,
        classes=(CharacterClass.BARD, CharacterClass.DRUID, CharacterClass.RANGER),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 30),
        components=Components(verbal=True, somatic=True, material="a morsel of food"),
        duration=Duration(DurationType.HOUR, 24),
        source="Player's Handbook",
        description=(
            "Target a Beast that you can see within range. The target must succeed on a Wisdom saving throw or have the Charmed condition for the duration. If you or one of your allies deals damage to the target, the spells ends.\n"
            "Using a Higher-Level Spell Slot. You can target one additional Beast for each spell slot level above 1."
        ),
        usage_tags=("control",),
        target=FeatureTarget.CREATURE,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "1cd62343f858dc06")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You try to charm a Beast."),
            Facts(
                (
                    ("Target", "A Beast that you can see within range"),
                    ("Save", "Wisdom"),
                    ("Failed save", "Charmed for the duration"),
                    (
                        "Ends early",
                        "If you or one of your allies deals damage to the target",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Targets", "+1 Beast for each spell slot level above 1"),)),),
            ),
        ]


class ArmorOfAgathys(ClassSpell):
    rules = SpellRules(
        name="Armor of Agathys",
        level=1,
        school=School.ABJURATION,
        classes=(CharacterClass.WARLOCK,),
        casting_time=CastingTime(CastingTimeType.BONUS_ACTION),
        range=Range(RangeType.SELF),
        components=Components(
            verbal=True, somatic=True, material="a shard of blue glass"
        ),
        duration=Duration(DurationType.HOUR, 1),
        source="Player's Handbook",
        description=(
            "Protective magical frost surrounds you. You gain 5 Temporary Hit Points. If a creature hits you with a melee attack roll before the spell ends, the creature takes 5 Cold damage. The spell ends early if you have no Temporary Hit Points.\n"
            "Using a Higher-Level Spell Slot. The Temporary Hit Points and the Cold damage both increase by 5 for each spell slot level above 1."
        ),
        usage_tags=("damage", "heal"),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "d2037c1db7756c97")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Flavor", "Protective magical frost surrounds you."),
                    ("Temporary Hit Points", "You gain 5 Temporary Hit Points"),
                    (
                        "Retaliation",
                        "If a creature hits you with a melee attack roll before the spell ends, the creature takes 5 Cold damage",
                    ),
                    ("Ends early", "If you have no Temporary Hit Points"),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (
                    Facts(
                        (
                            (
                                "Increase",
                                "The Temporary Hit Points and the Cold damage both increase by 5 for each spell slot level above 1",
                            ),
                        )
                    ),
                ),
            ),
        ]


class ArmsOfHadar(ClassSpell):
    rules = SpellRules(
        name="Arms of Hadar",
        level=1,
        school=School.CONJURATION,
        classes=(CharacterClass.WARLOCK,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "Invoking Hadar, you cause tendrils to erupt from yourself. Each creature in a 10-foot Emanation originating from you makes a Strength saving throw. On a failed save, a target takes 2d6 Necrotic damage and can’t take Reactions until the start of its next turn. On a successful save, a target takes half as much damage only.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 1d6 for each spell slot level above 1."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "ffe9467d22b1e290")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "Invoking Hadar, you cause tendrils to erupt from yourself.",
                    ),
                    ("Area", "10-foot Emanation originating from you"),
                    ("Save", "Strength, made by each creature in the area"),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (
                    (
                        "2d6 Necrotic damage, and it can't take Reactions until the start of its next turn",
                        "Half as much damage only",
                    ),
                ),
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Damage", "+1d6 for each spell slot level above 1"),)),),
            ),
        ]


class Bane(ClassSpell):
    rules = SpellRules(
        name="Bane",
        level=1,
        school=School.ENCHANTMENT,
        classes=(CharacterClass.BARD, CharacterClass.CLERIC, CharacterClass.WARLOCK),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 30),
        components=Components(verbal=True, somatic=True, material="a drop of blood"),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "Up to three creatures of your choice that you can see within range must each make a Charisma saving throw. Whenever a target that fails this save makes an attack roll or a saving throw before the spell ends, the target must subtract 1d4 from the attack roll or save.\n"
            "Using a Higher-Level Spell Slot. You can target one additional creature for each spell slot level above 1."
        ),
        usage_tags=("control",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "74ef36a69ae8089e")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You hinder the attacks and saves of up to three creatures."),
            Facts(
                (
                    (
                        "Targets",
                        "Up to three creatures of your choice that you can see within range",
                    ),
                    ("Save", "Charisma, made by each target"),
                    (
                        "Failed save",
                        "Whenever the target makes an attack roll or a saving throw before the spell ends, it must subtract 1d4 from the attack roll or save",
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


class BeastBond(ClassSpell):
    rules = SpellRules(
        name="Beast Bond",
        level=1,
        school=School.DIVINATION,
        classes=(CharacterClass.DRUID, CharacterClass.RANGER),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.TOUCH),
        components=Components(
            verbal=True, somatic=True, material="a bit of fur wrapped in cloth"
        ),
        duration=Duration(DurationType.MINUTE, 10, concentration=True),
        source="Xanathar's Guide to Everything",
        description="You establish a telepathic link with one beast you touch that is friendly to you or charmed by you. The spell fails if the beast's Intelligence is 4 or higher. Until the spell ends, the link is active while you and the beast are within line of sight of each other. Through the link, the beast can understand your telepathic messages to it, and it can telepathically communicate simple emotions and concepts back to you. While the link is active, the beast gains advantage on attack rolls against any creature within 5 feet of you that you can see.",
        usage_tags=("buff", "control", "utility"),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "1c49a60c1a871d26")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You establish a telepathic link with a beast."),
            Facts(
                (
                    (
                        "Target",
                        "One beast you touch that is friendly to you or charmed by you",
                    ),
                    ("Fails if", "The beast's Intelligence is 4 or higher"),
                    (
                        "Link",
                        "Active until the spell ends, while you and the beast are within line of sight of each other",
                    ),
                    (
                        "Telepathy",
                        "The beast can understand your telepathic messages to it, and it can telepathically communicate simple emotions and concepts back to you",
                    ),
                    (
                        "Advantage",
                        "While the link is active, the beast gains Advantage on attack rolls against any creature within 5 feet of you that you can see",
                    ),
                )
            ),
        ]


class BuzzingBee(ClassSpell):
    rules = SpellRules(
        name="Buzzing Bee",
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
        components=Components(verbal=True, somatic=True, material="a dab of honey"),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="D&D Beyond Drops - May 2026",
        description=(
            "You call forth a noisy spectral bee. You target a creature that you can see within range. The bee hovers around the target, distracting it with loud buzzing. For the duration, the target has Disadvantage on Wisdom (Perception) checks, Dexterity (Stealth) checks, and Constitution saving throws made to maintain Concentration. In addition, the target cannot benefit from the Invisible condition.\n"
            "The bee moves with the target, hovering within 3 feet of it as long as the target is within 120 feet of you. The bee disappears when the spell ends or if the target moves out of range."
        ),
        usage_tags=("buff",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "580f3aaa665ca880")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You call forth a noisy spectral bee. The bee hovers around the target, distracting it with loud buzzing.",
                    ),
                    ("Target", "A creature that you can see within range"),
                    (
                        "Disadvantage",
                        "For the duration, on its Wisdom (Perception) checks, Dexterity (Stealth) checks, and Constitution saving throws made to maintain Concentration",
                    ),
                    (
                        "Invisible",
                        "The target can't benefit from the Invisible condition",
                    ),
                    (
                        "The bee",
                        "Moves with the target, hovering within 3 feet of it as long as the target is within 120 feet of you",
                    ),
                    (
                        "Ends",
                        "The bee disappears when the spell ends or if the target moves out of range",
                    ),
                )
            )
        ]


class Catapult(ClassSpell):
    rules = SpellRules(
        name="Catapult",
        level=1,
        school=School.TRANSMUTATION,
        classes=(
            CharacterClass.SORCERER,
            CharacterClass.WIZARD,
            CharacterClass.ARTIFICER,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Xanathar's Guide to Everything",
        description=(
            "Choose one object weighing 1 to 5 pounds within range that isn't being worn or carried. The object flies in a straight line up to 90 feet in a direction you choose before falling to the ground, stopping early if it impacts against a solid surface. If the object would strike a creature, that creature must make a Dexterity saving throw. On a failed save, the object strikes the target and stops moving. When the object strikes something, the object and what it strikes each take 3d8 bludgeoning damage.\n"
            "At Higher Levels. When you cast this spell using a spell slot of 2nd level or higher, the maximum weight of objects that you can target with this spell increases by 5 pounds, and the damage increases by 1d8, for each slot level above 1st."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "6fd616b0eb93da0a")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You hurl a small object through the air."),
            Facts(
                (
                    (
                        "Target",
                        "One object weighing 1 to 5 pounds within range that isn't being worn or carried",
                    ),
                    (
                        "Flight",
                        "It flies in a straight line up to 90 feet in a direction you choose before falling to the ground, stopping early if it impacts against a solid surface",
                    ),
                    (
                        "Creature in path",
                        "If the object would strike a creature, that creature makes a Dexterity saving throw; on a failed save, the object strikes it and stops moving",
                    ),
                    (
                        "Impact",
                        "When the object strikes something, the object and what it strikes each take 3d8 Bludgeoning damage",
                    ),
                )
            ),
            Option(
                "At Higher Levels",
                (
                    Facts(
                        (
                            (
                                "Maximum weight",
                                "+5 pounds for each slot level above 1st",
                            ),
                            ("Damage", "+1d8 for each slot level above 1st"),
                        )
                    ),
                ),
            ),
        ]


class CauseFear(ClassSpell):
    rules = SpellRules(
        name="Cause Fear",
        level=1,
        school=School.NECROMANCY,
        classes=(CharacterClass.WARLOCK, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Xanathar's Guide to Everything",
        description=(
            "You awaken the sense of mortality in one creature you can see within range. A construct or an undead is immune to this effect. The target must succeed on a Wisdom saving throw or become frightened of you until the spell ends. The frightened target can repeat the saving throw at the end of each of its turns, ending the effect on itself on a success.\n"
            "At Higher Levels. When you cast this spell using a spell slot of 2nd level or higher, you can target one additional creature for each slot level above 1st. The creatures must be within 30 feet of each other when you target them."
        ),
        usage_tags=("control", "utility"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "e64c5deffe440036")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You awaken the sense of mortality in one creature you can see within range.",
                    ),
                    (
                        "Target",
                        "One creature you can see within range; a construct or an undead is immune",
                    ),
                    ("Save", "Wisdom"),
                    ("Failed save", "Frightened of you until the spell ends"),
                    (
                        "Repeat save",
                        "At the end of each of its turns, ending the effect on itself on a success",
                    ),
                )
            ),
            Option(
                "At Higher Levels",
                (
                    Facts(
                        (
                            ("Targets", "+1 creature for each slot level above 1st"),
                            (
                                "Spacing",
                                "The creatures must be within 30 feet of each other when you target them",
                            ),
                        )
                    ),
                ),
            ),
        ]


class Ceremony(ClassSpell):
    rules = SpellRules(
        name="Ceremony",
        level=1,
        school=School.ABJURATION,
        classes=(CharacterClass.CLERIC, CharacterClass.PALADIN),
        casting_time=CastingTime(CastingTimeType.HOUR, 1, ritual=True),
        range=Range(RangeType.TOUCH),
        components=Components(
            verbal=True,
            somatic=True,
            material="25 gp worth of powdered silver, which the spell consumes",
        ),
        duration=Duration(DurationType.INSTANTANEOUS, note="see below"),
        source="Xanathar's Guide to Everything",
        description=(
            "You perform one of several religious ceremonies. When you cast the spell, choose one of the following ceremonies, the target of which must be within 10 feet of you throughout the casting.\n"
            "Atonement. You touch one willing creature whose alignment has changed, and you make a DC 20 Wisdom (Insight) check. On a successful check, you restore the target to its original alignment.\n"
            "Bless Water. You touch one vial of water and cause it to become holy water.\n"
            "Coming of Age. You touch one humanoid who is a young adult. For the next 24 hours, whenever the target makes an ability check, it can roll a d4 and add the number rolled to the ability check. A creature can benefit from this rite only once.\n"
            "Dedication. You touch one humanoid who wishes to be dedicated to your god's service. For the next 24 hours, whenever the target makes a saving throw, it can roll a d4 and add the number rolled to the save. A creature can benefit from this rite only once.\n"
            "Funeral Rite. You touch one corpse, and for the next 7 days, the target can't become undead by any means short of a Wish spell.\n"
            "Wedding. You touch adult humanoids willing to be bonded together in marriage. For the next 7 days, each target gains a +2 bonus to AC while they are within 30 feet of each other. A creature can benefit from this rite again only if widowed."
        ),
        usage_tags=("buff",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "3fbb8380637165a9")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You perform one of several religious ceremonies, chosen when you cast the spell."
            ),
            Facts(
                (
                    (
                        "Range",
                        "The target must be within 10 feet of you throughout the casting",
                    ),
                )
            ),
            Table(
                ("Ceremony", "You touch", "Effect"),
                (
                    (
                        "Atonement",
                        "One willing creature whose alignment has changed",
                        "You make a DC 20 Wisdom (Insight) check; on a success, you restore the target to its original alignment",
                    ),
                    ("Bless Water", "One vial of water", "It becomes holy water"),
                    (
                        "Coming of Age",
                        "One humanoid who is a young adult",
                        "For the next 24 hours, whenever it makes an ability check, it can roll a d4 and add the number rolled; a creature can benefit from this rite only once",
                    ),
                    (
                        "Dedication",
                        "One humanoid who wishes to be dedicated to your god's service",
                        "For the next 24 hours, whenever it makes a saving throw, it can roll a d4 and add the number rolled; a creature can benefit from this rite only once",
                    ),
                    (
                        "Funeral Rite",
                        "One corpse",
                        "For the next 7 days, it can't become undead by any means short of a Wish spell",
                    ),
                    (
                        "Wedding",
                        "Adult humanoids willing to be bonded together in marriage",
                        "For the next 7 days, each gains a +2 bonus to AC while they are within 30 feet of each other; a creature can benefit from this rite again only if widowed",
                    ),
                ),
            ),
        ]

    def combat_effects(
        self, character: CharacterView | None = None
    ) -> list[CombatEffect]:
        return []


class ChaosBolt(ClassSpell):
    rules = SpellRules(
        name="Chaos Bolt",
        level=1,
        school=School.EVOCATION,
        classes=(CharacterClass.SORCERER,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 120),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Xanathar's Guide to Everything",
        description=(
            "You hurl an undulating, warbling mass of chaotic energy at one creature in range. Make a ranged spell attack against the target. On a hit, the target takes 2d8 + 1d6 damage. Choose one of the d8s. The number rolled on that die determines the attack's damage type, as shown below.\n"
            "If you roll the same number on both d8s, the chaotic energy leaps from the target to a different creature of your choice within 30 feet of it. Make a new attack roll against the new target, and make a new damage roll, which could cause the chaotic energy to leap again.\n"
            "A creature can be targeted only once by each casting of this spell.\n"
            "At Higher Levels. When you cast this spell using a spell slot of 2nd level or higher, each target takes 1d6 extra damage of the type rolled for each slot level above 1st."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "5bc8ae4ecddfd989")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You hurl an undulating, warbling mass of chaotic energy at one creature in range.",
                    ),
                    ("Target", "One creature in range"),
                    ("Attack", "Ranged spell attack"),
                    ("On a hit", "2d8 + 1d6 damage"),
                    (
                        "Damage type",
                        "Choose one of the d8s; the number rolled on that die determines the damage type",
                    ),
                )
            ),
            Table(
                ("d8", "Damage type"),
                (
                    ("1", "Acid"),
                    ("2", "Cold"),
                    ("3", "Fire"),
                    ("4", "Force"),
                    ("5", "Lightning"),
                    ("6", "Poison"),
                    ("7", "Psychic"),
                    ("8", "Thunder"),
                ),
            ),
            Option(
                "Leap",
                (
                    Facts(
                        (
                            ("Trigger", "You roll the same number on both d8s"),
                            (
                                "New target",
                                "A different creature of your choice within 30 feet of the target; make a new attack roll and a new damage roll, which could cause the chaotic energy to leap again",
                            ),
                            (
                                "Each creature",
                                "Can be targeted only once by each casting of this spell",
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
                                "Extra damage",
                                "Each target takes 1d6 extra damage of the type rolled for each slot level above 1st",
                            ),
                        )
                    ),
                ),
            ),
        ]


class ColorSpray(ClassSpell):
    rules = SpellRules(
        name="Color Spray",
        level=1,
        school=School.ILLUSION,
        classes=(CharacterClass.BARD, CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(
            verbal=True, somatic=True, material="a pinch of colorful sand"
        ),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description="You launch a dazzling array of flashing, colorful light. Each creature in a 15-foot Cone originating from you must succeed on a Constitution saving throw or have the Blinded condition until the end of your next turn.",
        usage_tags=("control",),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "2d55aeeb36e030ed")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You launch a dazzling array of flashing, colorful light.",
                    ),
                    ("Area", "15-foot Cone originating from you"),
                    ("Save", "Constitution, made by each creature in the Cone"),
                    ("Failed save", "Blinded until the end of your next turn"),
                    ("Successful save", "No effect"),
                )
            )
        ]


class CompelledDuel(ClassSpell):
    rules = SpellRules(
        name="Compelled Duel",
        level=1,
        school=School.ENCHANTMENT,
        classes=(CharacterClass.PALADIN,),
        casting_time=CastingTime(CastingTimeType.BONUS_ACTION),
        range=Range(RangeType.FOOT, 30),
        components=Components(verbal=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "You try to compel a creature into a duel. One creature that you can see within range makes a Wisdom saving throw. On a failed save, the target has Disadvantage on attack rolls against creatures other than you, and it can't willingly move to a space that is more than 30 feet away from you.\n"
            "The spell ends if you make an attack roll against a creature other than the target, if you cast a spell on an enemy other than the target, if an ally of yours damages the target, or if you end your turn more than 30 feet away from the target."
        ),
        usage_tags=("buff", "control"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "a234e4b12ae59525")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You try to compel a creature into a duel."),
            Facts(
                (
                    ("Target", "One creature that you can see within range"),
                    ("Save", "Wisdom"),
                    (
                        "Failed save",
                        "The target has Disadvantage on attack rolls against creatures other than you, and it can't willingly move to a space that is more than 30 feet away from you",
                    ),
                )
            ),
            Option(
                "The Spell Ends If",
                (
                    Facts(
                        (
                            (
                                "Your attack",
                                "You make an attack roll against a creature other than the target",
                            ),
                            (
                                "Your spell",
                                "You cast a spell on an enemy other than the target",
                            ),
                            ("An ally", "An ally of yours damages the target"),
                            (
                                "Distance",
                                "You end your turn more than 30 feet away from the target",
                            ),
                        )
                    ),
                ),
            ),
        ]


class ComprehendLanguages(ClassSpell):
    rules = SpellRules(
        name="Comprehend Languages",
        level=1,
        school=School.DIVINATION,
        classes=(
            CharacterClass.BARD,
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION, ritual=True),
        range=Range(RangeType.SELF),
        components=Components(
            verbal=True, somatic=True, material="a pinch of soot and salt"
        ),
        duration=Duration(DurationType.HOUR, 1),
        source="Player's Handbook",
        description="For the duration, you understand the literal meaning of any language that you hear or see signed. You also understand any written language that you see, but you must be touching the surface on which the words are written. It takes about 1 minute to read one page of text. This spell doesn't decode symbols or secret messages.",
        usage_tags=("utility",),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "efa2f3423f2ce520")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "For the duration, you understand languages you hear, see signed, or read."
            ),
            Facts(
                (
                    (
                        "Spoken and signed",
                        "You understand the literal meaning of any language that you hear or see signed",
                    ),
                    (
                        "Written",
                        "You understand any written language that you see, but you must be touching the surface on which the words are written",
                    ),
                    ("Reading", "It takes about 1 minute to read one page of text"),
                    ("Limit", "Doesn't decode symbols or secret messages"),
                )
            ),
        ]

    def combat_effects(
        self, character: CharacterView | None = None
    ) -> list[CombatEffect]:
        return []


class CreateOrDestroyWater(ClassSpell):
    rules = SpellRules(
        name="Create or Destroy Water",
        level=1,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.CLERIC, CharacterClass.DRUID),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 30),
        components=Components(
            verbal=True, somatic=True, material="a mix of water and sand"
        ),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "You do one of the following:\n"
            "Create Water. You create up to 10 gallons of clean water within range in an open container. Alternatively, the water falls as rain in a 30-foot Cube within range, extinguishing exposed flames there.\n"
            "Destroy Water. You destroy up to 10 gallons of water in an open container within range. Alternatively, you destroy fog in a 30-foot Cube within range.\n"
            "Using a Higher-Level Spell Slot. You create or destroy 10 additional gallons of water, or the size of the Cube increases by 5 feet, for each spell slot level above 1."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "7a286ba03547515d")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You create or destroy water."),
            Option(
                "Create Water",
                (
                    Facts(
                        (
                            (
                                "Water",
                                "Up to 10 gallons of clean water within range in an open container",
                            ),
                            (
                                "Or rain",
                                "The water falls as rain in a 30-foot Cube within range, extinguishing exposed flames there",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Destroy Water",
                (
                    Facts(
                        (
                            (
                                "Water",
                                "Up to 10 gallons of water in an open container within range",
                            ),
                            (
                                "Or fog",
                                "You destroy fog in a 30-foot Cube within range",
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
                                "Increase",
                                "10 additional gallons of water, or the size of the Cube increases by 5 feet, for each spell slot level above 1",
                            ),
                        )
                    ),
                ),
            ),
        ]


class DetectEvilAndGood(ClassSpell):
    rules = SpellRules(
        name="Detect Evil and Good",
        level=1,
        school=School.DIVINATION,
        classes=(CharacterClass.CLERIC, CharacterClass.PALADIN),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 10, concentration=True),
        source="Player's Handbook",
        description=(
            "For the duration, you sense the location of any Aberration, Celestial, Elemental, Fey, Fiend, or Undead within 30 feet of yourself. You also sense whether the Hallow spell is active there and, if so, where.\n"
            "The spell is blocked by 1 foot of stone, dirt, or wood; 1 inch of metal; or a thin sheet of lead."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "eade6524daa0aa47")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "For the duration, you sense otherworldly creatures and hallowed ground near you."
            ),
            Facts(
                (
                    ("Area", "Within 30 feet of yourself"),
                    (
                        "You sense",
                        "The location of any Aberration, Celestial, Elemental, Fey, Fiend, or Undead",
                    ),
                    (
                        "Hallow",
                        "Whether the Hallow spell is active there and, if so, where",
                    ),
                    (
                        "Blocked by",
                        "1 foot of stone, dirt, or wood; 1 inch of metal; or a thin sheet of lead",
                    ),
                )
            ),
        ]


class DetectMagic(ClassSpell):
    rules = SpellRules(
        name="Detect Magic",
        level=1,
        school=School.DIVINATION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.BARD,
            CharacterClass.CLERIC,
            CharacterClass.DRUID,
            CharacterClass.PALADIN,
            CharacterClass.RANGER,
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION, ritual=True),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 10, concentration=True),
        source="Player's Handbook",
        description=(
            "For the duration, you sense the presence of magical effects within 30 feet of yourself. If you sense such effects, you can take the Magic action to see a faint aura around any visible creature or object in the area that bears the magic, and if an effect was created by a spell, you learn the spell's school of magic.\n"
            "The spell is blocked by 1 foot of stone, dirt, or wood; 1 inch of metal; or a thin sheet of lead."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "917c4d72ce0985cc")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("For the duration, you sense magic near you."),
            Facts(
                (
                    ("Area", "Within 30 feet of yourself"),
                    ("You sense", "The presence of magical effects"),
                    (
                        "Auras",
                        "If you sense such effects, you can take the Magic action to see a faint aura around any visible creature or object in the area that bears the magic",
                    ),
                    (
                        "School",
                        "If an effect was created by a spell, you learn the spell's school of magic",
                    ),
                    (
                        "Blocked by",
                        "1 foot of stone, dirt, or wood; 1 inch of metal; or a thin sheet of lead",
                    ),
                )
            ),
        ]

    def combat_effects(
        self, character: CharacterView | None = None
    ) -> list[CombatEffect]:
        return []


class DetectPoisonAndDisease(ClassSpell):
    rules = SpellRules(
        name="Detect Poison and Disease",
        level=1,
        school=School.DIVINATION,
        classes=(
            CharacterClass.CLERIC,
            CharacterClass.DRUID,
            CharacterClass.PALADIN,
            CharacterClass.RANGER,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION, ritual=True),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True, material="a yew leaf"),
        duration=Duration(DurationType.MINUTE, 10, concentration=True),
        source="Player's Handbook",
        description=(
            "For the duration, you sense the location of poisons, poisonous or venomous creatures, and magical contagions within 30 feet of yourself. You sense the kind of poison, creature, or contagion in each case.\n"
            "The spell is blocked by 1 foot of stone, dirt, or wood; 1 inch of metal; or a thin sheet of lead."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "427077950f34b9bf")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("For the duration, you sense poisons and disease near you."),
            Facts(
                (
                    ("Area", "Within 30 feet of yourself"),
                    (
                        "You sense",
                        "The location of poisons, poisonous or venomous creatures, and magical contagions",
                    ),
                    (
                        "Details",
                        "You sense the kind of poison, creature, or contagion in each case",
                    ),
                    (
                        "Blocked by",
                        "1 foot of stone, dirt, or wood; 1 inch of metal; or a thin sheet of lead",
                    ),
                )
            ),
        ]


class DistortValue(ClassSpell):
    rules = SpellRules(
        name="Distort Value",
        level=1,
        school=School.ILLUSION,
        classes=(
            CharacterClass.BARD,
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.MINUTE, 1),
        range=Range(RangeType.TOUCH),
        components=Components(verbal=True),
        duration=Duration(DurationType.HOUR, 8),
        source="Acquisitions Inc.",
        description=(
            "You cast this spell on an object no more than 1 foot on a side, doubling the object's perceived value by adding illusionary flourish or reducing its perceived value by half with the help of illusionary dents and scratches. Anyone examining the object must roll an Investigation check against your spell DC.\n"
            "At Higher Levels. When you cast this spell using a higher spell slot, you increase the size of the object by 1 foot per spell slot over 1st."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "cfe0c188833cba58")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You change an object's perceived value with illusion."),
            Facts(
                (
                    ("Target", "An object no more than 1 foot on a side"),
                    (
                        "Effect",
                        "Double its perceived value by adding illusionary flourish, or halve it with illusionary dents and scratches",
                    ),
                    (
                        "Examining",
                        "Anyone examining the object must roll an Investigation check against your spell DC",
                    ),
                )
            ),
            Option(
                "At Higher Levels",
                (Facts((("Object size", "+1 foot for each spell slot over 1st"),)),),
            ),
        ]


class DivineFavor(ClassSpell):
    rules = SpellRules(
        name="Divine Favor",
        level=1,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.PALADIN,),
        casting_time=CastingTime(CastingTimeType.BONUS_ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 1),
        source="Player's Handbook",
        description="Until the spell ends, your attacks with weapons deal an extra 1d4 Radiant damage on a hit.",
        usage_tags=("damage",),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "99308df4ecbd2d50")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Effect",
                        "Until the spell ends, your attacks with weapons deal an extra 1d4 Radiant damage on a hit",
                    ),
                )
            )
        ]

    def combat_effects(
        self, character: CharacterView | None = None
    ) -> list[CombatEffect]:
        return [
            CombatEffect(
                conditions=(
                    CombatCondition(
                        "Divine Favor",
                        modifiers=(
                            ExtraDamageOnHit(
                                "1d4", DamageType.RADIANT, AttackKind.WEAPON
                            ),
                        ),
                    ),
                ),
                notes=(
                    "The caster's attacks with weapons deal an extra 1d4 Radiant damage on a hit: the badge goes on the caster.",
                ),
            )
        ]


class EarthTremor(ClassSpell):
    rules = SpellRules(
        name="Earth Tremor",
        level=1,
        school=School.EVOCATION,
        classes=(
            CharacterClass.BARD,
            CharacterClass.DRUID,
            CharacterClass.SORCERER,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF, area=Area(10, AreaShape.RADIUS)),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Xanathar's Guide to Everything/Elemental Evil Player's Companion",
        description=(
            "You cause a tremor in the ground in a 10-foot radius. Each creature other than you in that area must make a Dexterity saving throw. On a failed save, a creature takes 1d6 bludgeoning damage and is knocked prone. If the ground in that area is loose earth or stone, it becomes difficult terrain until cleared.\n"
            "At Higher Levels. When you cast this spell using a spell slot of 2nd level or higher, the damage increases by 1d6 for each slot level above 1st."
        ),
        usage_tags=("control", "damage"),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "51b04719232d3d85")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You cause a tremor in the ground around you."),
            Facts(
                (
                    ("Area", "10-foot radius"),
                    (
                        "Save",
                        "Dexterity, made by each creature other than you in the area",
                    ),
                    ("Failed save", "1d6 Bludgeoning damage, and knocked Prone"),
                    ("Successful save", "No effect"),
                    (
                        "Ground",
                        "If the ground in the area is loose earth or stone, it becomes Difficult Terrain until cleared",
                    ),
                )
            ),
            Option(
                "At Higher Levels",
                (Facts((("Damage", "+1d6 for each slot level above 1st"),)),),
            ),
        ]


class ExpeditiousRetreat(ClassSpell):
    rules = SpellRules(
        name="Expeditious Retreat",
        level=1,
        school=School.TRANSMUTATION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.BONUS_ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 10, concentration=True),
        source="Player's Handbook",
        description="You take the Dash action, and until the spell ends, you can take that action again as a Bonus Action.",
        usage_tags=("buff",),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "2563b29ccb8ab060")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("On casting", "You take the Dash action"),
                    (
                        "Later",
                        "Until the spell ends, you can take that action again as a Bonus Action",
                    ),
                )
            )
        ]


class FeignInterest(ClassSpell):
    rules = SpellRules(
        name="Feign Interest",
        level=1,
        school=School.ILLUSION,
        classes=(CharacterClass.WIZARD,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True),
        duration=Duration(DurationType.HOUR, 1),
        source="D&D Beyond Drops - September 2026",
        description=(
            "This spell is a favorite of apprentices and students. For the duration, you appear to be fully focused and paying rapt attention. Behind the illusion, you can be napping, thinking about other things, or otherwise letting your mind wander.\n"
            "A creature that takes a Search action to evaluate your state of mind can determine that your interest is feigned with a successful Wisdom (Insight) check against your spell save DC. If a creature discerns the illusion for what it is, they see your true demeanor."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "f64ac123b1af9827")


class FindFamiliar(ClassSpell):
    rules = SpellRules(
        name="Find Familiar",
        level=1,
        school=School.CONJURATION,
        classes=(CharacterClass.WIZARD,),
        casting_time=CastingTime(CastingTimeType.HOUR, 1, ritual=True),
        range=Range(RangeType.FOOT, 10),
        components=Components(
            verbal=True,
            somatic=True,
            material="burning incense worth 10+ GP, which the spell consumes",
        ),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "You gain the service of a familiar, a spirit that takes an animal form you choose: Bat, Cat, Frog, Hawk, Lizard, Octopus, Owl, Rat, Raven, Spider, Weasel, or another Beast that has a Challenge Rating of 0. Appearing in an unoccupied space within range, the familiar has the statistics of the chosen form (see appendix B), though it is a Celestial, Fey, or Fiend (your choice) instead of a Beast. Your familiar acts independently of you, but it obeys your commands.\n"
            "Telepathic Connection. While your familiar is within 100 feet of you, you can communicate with it telepathically. Additionally, as a Bonus Action, you can see through the familiar’s eyes and hear what it hears until the start of your next turn, gaining the benefits of any special senses it has.\n"
            "Finally, when you cast a spell with a range of touch, your familiar can deliver the touch. Your familiar must be within 100 feet of you, and it must take a Reaction to deliver the touch when you cast the spell.\n"
            "Combat. The familiar is an ally to you and your allies. It rolls its own Initiative and acts on its own turn. A familiar can’t attack, but it can take other actions as normal.\n"
            "Disappearance of the Familiar. When the familiar drops to 0 Hit Points, it disappears. It reappears after you cast this spell again. As a Magic action, you can temporarily dismiss the familiar to a pocket dimension. Alternatively, you can dismiss it forever. As a Magic action while it is temporarily dismissed, you can cause it to reappear in an unoccupied space within 30 feet of you. Whenever the familiar drops to 0 Hit Points or disappears into the pocket dimension, it leaves behind in its space anything it was wearing or carrying.\n"
            "One Familiar Only. You can’t have more than one familiar at a time. If you cast this spell while you have a familiar, you instead cause it to adopt a new eligible form."
        ),
        usage_tags=("buff", "summon"),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "aa6e07ecd937ce9b")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You gain the service of a familiar, a spirit that takes an animal form you choose. It acts independently of you, but it obeys your commands."
            ),
            Facts(
                (
                    (
                        "Forms",
                        "Bat, Cat, Frog, Hawk, Lizard, Octopus, Owl, Rat, Raven, Spider, Weasel, or another Beast of Challenge Rating 0",
                    ),
                    (
                        "Statistics",
                        "Those of the chosen form, but it's a Celestial, Fey, or Fiend (your choice) instead of a Beast",
                    ),
                    ("Appears", "In an unoccupied space within range"),
                    (
                        "One only",
                        "You can't have more than one familiar; casting this spell while you have one makes it adopt a new eligible form instead",
                    ),
                )
            ),
            Option(
                "Telepathic Connection",
                (
                    Facts(
                        (
                            (
                                "Telepathy",
                                "While your familiar is within 100 feet of you, you can communicate with it telepathically",
                            ),
                            (
                                "Its senses",
                                "As a Bonus Action, you can see through the familiar's eyes and hear what it hears until the start of your next turn, gaining the benefits of any special senses it has",
                            ),
                            (
                                "Touch spells",
                                "When you cast a spell with a range of touch, your familiar can deliver the touch; it must be within 100 feet of you, and it must take a Reaction to deliver the touch when you cast the spell",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Combat",
                (
                    Facts(
                        (
                            ("Allegiance", "An ally to you and your allies"),
                            ("Initiative", "Rolls its own and acts on its own turn"),
                            (
                                "Actions",
                                "Can't attack, but can take other actions as normal",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Disappearance",
                (
                    Facts(
                        (
                            (
                                "0 Hit Points",
                                "It disappears, and reappears after you cast this spell again",
                            ),
                            (
                                "Dismiss",
                                "Magic action: dismiss it temporarily to a pocket dimension, or forever",
                            ),
                            (
                                "Recall",
                                "Magic action while it's temporarily dismissed: it reappears in an unoccupied space within 30 feet of you",
                            ),
                            (
                                "Its gear",
                                "Whenever it drops to 0 Hit Points or disappears into the pocket dimension, it leaves behind anything it was wearing or carrying",
                            ),
                        )
                    ),
                ),
            ),
        ]


class FrostFingers(ClassSpell):
    rules = SpellRules(
        name="Frost Fingers",
        level=1,
        school=School.EVOCATION,
        classes=(CharacterClass.WIZARD,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF, area=Area(15, AreaShape.CONE)),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Icewind Dale - Rime of the Frostmaiden",
        description=(
            "Freezing cold blasts from your fingertips in a 15-foot cone. Each creature in that area must make a Constitution saving throw, taking 2d8 cold damage on a failed save, or half as much damage on a successful one.\n"
            "The cold freezes nonmagical liquids in the area that aren't being worn or carried.\n"
            "At Higher Levels. When you cast this spell using a spell slot of 2nd level or higher, the damage increases by 1d8 for each slot level above 1st."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "4d26dcf6f16cdc40")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "Freezing cold blasts from your fingertips in a 15-foot cone.",
                    ),
                    ("Area", "15-foot cone"),
                    ("Save", "Constitution, made by each creature in the area"),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (("2d8 Cold damage", "Half as much damage"),),
            ),
            Facts(
                (
                    (
                        "Liquids",
                        "The cold freezes nonmagical liquids in the area that aren't being worn or carried",
                    ),
                )
            ),
            Option(
                "At Higher Levels",
                (Facts((("Damage", "+1d8 for each slot level above 1st"),)),),
            ),
        ]


class Goodberry(ClassSpell):
    rules = SpellRules(
        name="Goodberry",
        level=1,
        school=School.CONJURATION,
        classes=(CharacterClass.DRUID, CharacterClass.RANGER),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(
            verbal=True, somatic=True, material="a sprig of mistletoe"
        ),
        duration=Duration(DurationType.HOUR, 24),
        source="Player's Handbook",
        description=(
            "Ten berries appear in your hand and are infused with magic for the duration. A creature can take a Bonus Action to eat one berry. Eating a berry restores 1 Hit Point, and the berry provides enough nourishment to sustain a creature for one day.\n"
            "Uneaten berries disappear when the spell ends."
        ),
        usage_tags=("heal",),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "c2819bf387956907")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "Ten berries appear in your hand and are infused with magic for the duration."
            ),
            Facts(
                (
                    ("Eating", "A creature can take a Bonus Action to eat one berry"),
                    (
                        "Effect",
                        "Eating a berry restores 1 Hit Point, and the berry provides enough nourishment to sustain a creature for one day",
                    ),
                    ("Spell ends", "Uneaten berries disappear"),
                )
            ),
        ]


class HailOfThorns(ClassSpell):
    rules = SpellRules(
        name="Hail of Thorns",
        level=1,
        school=School.CONJURATION,
        classes=(CharacterClass.RANGER,),
        casting_time=CastingTime(
            CastingTimeType.BONUS_ACTION,
            trigger="which you take immediately after hitting a creature with a Ranged weapon",
        ),
        range=Range(RangeType.SELF),
        components=Components(verbal=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "As you hit the creature, this spell creates a rain of thorns that sprouts from your Ranged weapon or ammunition. The target of the attack and each creature within 5 feet of it make a Dexterity saving throw, taking 1d10 Piercing damage on a failed save or half as much damage on a successful one.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 1d10 for each spell slot level above 1."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "fbe5ccebb22560a1")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "As you hit the creature, this spell creates a rain of thorns that sprouts from your Ranged weapon or ammunition.",
                    ),
                    (
                        "Trigger",
                        "Immediately after you hit a creature with a Ranged weapon",
                    ),
                    (
                        "Targets",
                        "The target of the attack and each creature within 5 feet of it",
                    ),
                    ("Save", "Dexterity"),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (("1d10 Piercing damage", "Half as much damage"),),
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Damage", "+1d10 for each spell slot level above 1"),)),),
            ),
        ]


class HellishRebuke(ClassSpell):
    rules = SpellRules(
        name="Hellish Rebuke",
        level=1,
        school=School.EVOCATION,
        classes=(CharacterClass.WARLOCK,),
        casting_time=CastingTime(
            CastingTimeType.REACTION,
            trigger="which you take in response to taking damage from a creature that you can see within 60 feet of yourself",
        ),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "The creature that damaged you is momentarily surrounded by green flames. It makes a Dexterity saving throw, taking 2d10 Fire damage on a failed save or half as much damage on a successful one.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 1d10 for each spell slot level above 1."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "98015ea93c759717")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "The creature that damaged you is momentarily surrounded by green flames.",
                    ),
                    (
                        "Trigger",
                        "You take damage from a creature that you can see within 60 feet of yourself",
                    ),
                    ("Target", "The creature that damaged you"),
                    ("Save", "Dexterity"),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (("2d10 Fire damage", "Half as much damage"),),
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Damage", "+1d10 for each spell slot level above 1"),)),),
            ),
        ]


class Heroism(ClassSpell):
    rules = SpellRules(
        name="Heroism",
        level=1,
        school=School.ENCHANTMENT,
        classes=(CharacterClass.BARD, CharacterClass.PALADIN),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.TOUCH),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "A willing creature you touch is imbued with bravery. Until the spell ends, the creature is immune to the Frightened condition and gains Temporary Hit Points equal to your spellcasting ability modifier at the start of each of its turns.\n"
            "Using a Higher-Level Spell Slot. You can target one additional creature for each spell slot level above 1."
        ),
        usage_tags=("heal",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "5282ba89840f1a93")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Flavor", "A willing creature you touch is imbued with bravery."),
                    ("Target", "A willing creature you touch"),
                    (
                        "Frightened",
                        "Until the spell ends, the creature is immune to the Frightened condition",
                    ),
                    (
                        "Temporary Hit Points",
                        "Equal to your spellcasting ability modifier, gained at the start of each of its turns",
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
                conditions=(
                    CombatCondition(
                        "Heroism",
                        modifiers=(
                            ConditionImmunity((Condition.FRIGHTENED,)),
                            AtTurnStart("Heroism: Temporary Hit Points"),
                        ),
                    ),
                ),
                notes=("One more target per slot level above 1.",),
            ),
            CombatEffect(
                name="Heroism: Temporary Hit Points",
                temp_hp=CombatHitPoints(add_modifier=True),
                spends_use=False,
                notes=(
                    "Each target gains them at the start of each of its turns while it has Heroism; the simulator gives them then.",
                ),
            ),
        ]


class Hex(ClassSpell):
    rules = SpellRules(
        name="Hex",
        level=1,
        school=School.ENCHANTMENT,
        classes=(CharacterClass.WARLOCK,),
        casting_time=CastingTime(CastingTimeType.BONUS_ACTION),
        range=Range(RangeType.FOOT, 90),
        components=Components(
            verbal=True, somatic=True, material="the petrified eye of a newt"
        ),
        duration=Duration(DurationType.HOUR, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "You place a curse on a creature that you can see within range. Until the spell ends, you deal an extra 1d6 Necrotic damage to the target whenever you hit it with an attack roll. Also, choose one ability when you cast the spell. The target has Disadvantage on ability checks made with the chosen ability.\n"
            "If the target drops to 0 Hit Points before this spell ends, you can take a Bonus Action on a later turn to curse a new creature.\n"
            "Using a Higher-Level Spell Slot. Your Concentration can last longer with a spell slot of level 2 (up to 4 hours), 3–4 (up to 8 hours), or 5+ (24 hours)."
        ),
        usage_tags=("control", "damage"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "6cb2b3f703691a6b")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Target", "A creature you can see within range"),
                    (
                        "Extra damage",
                        "1d6 Necrotic damage whenever you hit it with an attack roll",
                    ),
                    (
                        "Ability checks",
                        "It has Disadvantage on checks with one ability you choose when you cast the spell",
                    ),
                    (
                        "Move the curse",
                        "If the target drops to 0 Hit Points before the spell ends, you can take a Bonus Action on a later turn to curse a new creature",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (
                    Table(
                        ("Slot level", "Concentration lasts up to"),
                        (
                            ("1", "1 hour"),
                            ("2", "4 hours"),
                            ("3-4", "8 hours"),
                            ("5+", "24 hours"),
                        ),
                    ),
                ),
            ),
        ]


class Identify(ClassSpell):
    rules = SpellRules(
        name="Identify",
        level=1,
        school=School.DIVINATION,
        classes=(CharacterClass.ARTIFICER, CharacterClass.BARD, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.MINUTE, 1, ritual=True),
        range=Range(RangeType.TOUCH),
        components=Components(
            verbal=True, somatic=True, material="a pearl worth 100+ GP"
        ),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "You touch an object throughout the spell’s casting. If the object is a magic item or some other magical object, you learn its properties and how to use them, whether it requires Attunement, and how many charges it has, if any. You learn whether any ongoing spells are affecting the item and what they are. If the item was created by a spell, you learn that spell’s name.\n"
            "If you instead touch a creature throughout the casting, you learn which ongoing spells, if any, are currently affecting it."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "8861144782ba2770")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You touch an object or a creature throughout the spell's casting."
            ),
            Option(
                "An Object",
                (
                    Facts(
                        (
                            (
                                "If magical",
                                "If it is a magic item or some other magical object, you learn its properties and how to use them, whether it requires Attunement, and how many charges it has, if any",
                            ),
                            (
                                "Spells on it",
                                "You learn whether any ongoing spells are affecting the item and what they are",
                            ),
                            (
                                "Made by a spell",
                                "If the item was created by a spell, you learn that spell's name",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "A Creature",
                (
                    Facts(
                        (
                            (
                                "You learn",
                                "Which ongoing spells, if any, are currently affecting it",
                            ),
                        )
                    ),
                ),
            ),
        ]


class IllusoryScript(ClassSpell):
    rules = SpellRules(
        name="Illusory Script",
        level=1,
        school=School.ILLUSION,
        classes=(CharacterClass.BARD, CharacterClass.WARLOCK, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.MINUTE, 1, ritual=True),
        range=Range(RangeType.TOUCH),
        components=Components(
            somatic=True, material="ink worth 10+ GP, which the spell consumes"
        ),
        duration=Duration(DurationType.DAY, 10),
        source="Player's Handbook",
        description=(
            "You write on parchment, paper, or another suitable material and imbue it with an illusion that lasts for the duration. To you and any creatures you designate when you cast the spell, the writing appears normal, seems to be written in your hand, and conveys whatever meaning you intended when you wrote the text. To all others, the writing appears as if it were written in an unknown or magical script that is unintelligible. Alternatively, the illusion can alter the meaning, handwriting, and language of the text, though the language must be one you know.\n"
            "If the spell is dispelled, the original script and the illusion both disappear.\n"
            "A creature that has Truesight can read the hidden message."
        ),
        usage_tags=("buff",),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "dbf061e26763abeb")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You write on parchment, paper, or another suitable material and imbue it with an illusion that lasts for the duration."
            ),
            Facts(
                (
                    (
                        "You and chosen",
                        "To you and any creatures you designate when you cast the spell, the writing appears normal, seems to be written in your hand, and conveys whatever meaning you intended when you wrote the text",
                    ),
                    (
                        "All others",
                        "The writing appears as if it were written in an unknown or magical script that is unintelligible",
                    ),
                    (
                        "Alternatively",
                        "The illusion can alter the meaning, handwriting, and language of the text, though the language must be one you know",
                    ),
                    (
                        "Dispelled",
                        "The original script and the illusion both disappear",
                    ),
                    (
                        "Truesight",
                        "A creature that has Truesight can read the hidden message",
                    ),
                )
            ),
        ]


class InflictWounds(ClassSpell):
    rules = SpellRules(
        name="Inflict Wounds",
        level=1,
        school=School.NECROMANCY,
        classes=(CharacterClass.CLERIC,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.TOUCH),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "A creature you touch makes a Constitution saving throw, taking 2d10 Necrotic damage on a failed save or half as much damage on a successful one.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 1d10 for each spell slot level above 1."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "552ba398ea638703")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts((("Target", "A creature you touch"), ("Save", "Constitution"))),
            Table(
                ("Failed save", "Successful save"),
                (("2d10 Necrotic damage", "Half as much damage"),),
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Damage", "+1d10 for each spell slot level above 1"),)),),
            ),
        ]


class InsidiousRhythm(ClassSpell):
    rules = SpellRules(
        name="Insidious Rhythm",
        level=1,
        school=School.ENCHANTMENT,
        classes=(CharacterClass.BARD,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 120),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="D&D Beyond Drops - May 2026",
        description=(
            "One creature of your choice that you can see within range hears a haunting yet catchy tune that continuously repeats in its mind. The target must succeed on a Wisdom saving throw, or it has Disadvantage on Intelligence checks and on Constitution saving throws made to maintain Concentration. At the end of each of its turns, the target repeats the save, ending the spell on itself on a success.\n"
            "Using a Higher-Level Spell Slot. You can target one additional creature for each spell slot level above 1."
        ),
        usage_tags=("control",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "3917827fdc8fd5ed")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "One creature of your choice that you can see within range hears a haunting yet catchy tune that continuously repeats in its mind.",
                    ),
                    (
                        "Target",
                        "One creature of your choice that you can see within range",
                    ),
                    ("Save", "Wisdom"),
                    (
                        "Failed save",
                        "Disadvantage on Intelligence checks and on Constitution saving throws made to maintain Concentration",
                    ),
                    (
                        "Repeat save",
                        "At the end of each of its turns, ending the spell on itself on a success",
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


class JimsMagicMissile(ClassSpell):
    rules = SpellRules(
        name="Jim's Magic Missile",
        level=1,
        school=School.EVOCATION,
        classes=(CharacterClass.WIZARD,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 120),
        components=Components(
            verbal=True,
            somatic=True,
            material="1 gold coin, which is consumed as tax for using the spell",
        ),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Acquisitions Inc.",
        description=(
            "You create three twisting, whistling, hypoallergenic, gluten-free darts of magical force. Each dart can target a creature of your choice that you can see within range. Make a ranged spell attack for each missile. On a hit, the missile does 2d4 force damage.\n"
            "If the attack roll scores a critical, the missile does 5d4 force damage instead of the 4d4 force that you would normally get on a critical. If any of the attack roll is a natural one, all missiles turn around and hit the caster for 1 force damage per missile.\n"
            "At Higher Levels. When you cast this spell using a spell slot of 2nd level or higher, the spell creates one more dart for each slot level above 1st. This also increases the tax by 1 gp per spell slot over 1st."
        ),
        usage_tags=("damage", "utility"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "189e56ea45430ea9")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You create three twisting, whistling, hypoallergenic, gluten-free darts of magical force.",
                    ),
                    ("Darts", "Three"),
                    (
                        "Targets",
                        "Each dart can target a creature of your choice that you can see within range",
                    ),
                    ("Attack", "A ranged spell attack for each missile"),
                    ("On a hit", "2d4 Force damage"),
                    (
                        "Critical hit",
                        "5d4 Force damage, instead of the 4d4 you would normally get on a critical",
                    ),
                    (
                        "Natural 1",
                        "If any of the attack rolls is a natural 1, all missiles turn around and hit the caster for 1 Force damage per missile",
                    ),
                )
            ),
            Option(
                "At Higher Levels",
                (
                    Facts(
                        (
                            ("Darts", "+1 dart for each slot level above 1st"),
                            ("Tax", "+1 gp for each spell slot over 1st"),
                        )
                    ),
                ),
            ),
        ]


class Jump(ClassSpell):
    rules = SpellRules(
        name="Jump",
        level=1,
        school=School.TRANSMUTATION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.DRUID,
            CharacterClass.RANGER,
            CharacterClass.SORCERER,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.BONUS_ACTION),
        range=Range(RangeType.TOUCH),
        components=Components(
            verbal=True, somatic=True, material="a grasshopper’s hind leg"
        ),
        duration=Duration(DurationType.MINUTE, 1),
        source="Player's Handbook",
        description=(
            "You touch a willing creature. Once on each of its turns until the spell ends, that creature can jump up to 30 feet by spending 10 feet of movement.\n"
            "Using a Higher-Level Spell Slot. You can target one additional creature for each spell slot level above 1."
        ),
        usage_tags=("buff",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "a1faf62e2a45cb98")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Target", "A willing creature you touch"),
                    (
                        "Effect",
                        "Once on each of its turns until the spell ends, that creature can jump up to 30 feet by spending 10 feet of movement",
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


class MageArmor(ClassSpell):
    rules = SpellRules(
        name="Mage Armor",
        level=1,
        school=School.ABJURATION,
        classes=(CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.TOUCH),
        components=Components(
            verbal=True, somatic=True, material="a piece of cured leather"
        ),
        duration=Duration(DurationType.HOUR, 8),
        source="Player's Handbook",
        description="You touch a willing creature who isn’t wearing armor. Until the spell ends, the target’s base AC becomes 13 plus its Dexterity modifier. The spell ends early if the target dons armor.",
        usage_tags=("buff",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "d5acb9eea1dd98fc")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Target", "A willing creature who isn't wearing armor"),
                    ("Base AC", "13 + its Dexterity modifier, until the spell ends"),
                    ("Ends early", "If the target dons armor"),
                )
            )
        ]

    def combat_effects(
        self, character: CharacterView | None = None
    ) -> list[CombatEffect]:
        return [
            CombatEffect(
                conditions=(
                    CombatCondition(
                        "Mage Armor",
                        modifiers=(ArmorClassBase(13, (Ability.DEXTERITY,)),),
                    ),
                ),
                notes=(
                    "Pick a creature who isn't wearing armor; it ends if the target dons armor.",
                ),
            ),
        ]


class ProtectionFromEvilAndGood(ClassSpell):
    rules = SpellRules(
        name="Protection from Evil and Good",
        level=1,
        school=School.ABJURATION,
        classes=(
            CharacterClass.CLERIC,
            CharacterClass.DRUID,
            CharacterClass.PALADIN,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.TOUCH),
        components=Components(
            verbal=True,
            somatic=True,
            material="a flask of Holy Water worth 25+ GP, which the spell consumes",
        ),
        duration=Duration(DurationType.MINUTE, 10, concentration=True),
        source="Player's Handbook",
        description="Until the spell ends, one willing creature you touch is protected against creatures that are Aberrations, Celestials, Elementals, Fey, Fiends, or Undead. The protection grants several benefits. Creatures of those types have Disadvantage on attack rolls against the target. The target also can’t be possessed by or gain the Charmed or Frightened conditions from them. If the target is already possessed, Charmed, or Frightened by such a creature, the target has Advantage on any new saving throw against the relevant effect.",
        usage_tags=("buff", "control", "heal"),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "ecc1079de06bf5b9")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "One willing creature you touch is protected against otherworldly creatures until the spell ends."
            ),
            Facts(
                (
                    ("Target", "One willing creature you touch"),
                    (
                        "Protects from",
                        "Aberrations, Celestials, Elementals, Fey, Fiends, and Undead",
                    ),
                    ("Their attacks", "Have Disadvantage against the target"),
                    (
                        "Protection",
                        "The target can't be possessed by them or gain the Charmed or Frightened conditions from them",
                    ),
                    (
                        "Already affected",
                        "If already possessed, Charmed, or Frightened by such a creature, the target has Advantage on any new save against that effect",
                    ),
                )
            ),
        ]

    def combat_effects(
        self, character: CharacterView | None = None
    ) -> list[CombatEffect]:
        return [
            CombatEffect(
                conditions=(
                    CombatCondition(
                        "Protection from Evil and Good",
                        modifiers=(
                            AttacksAgainst(
                                RollMode.DISADVANTAGE,
                                when="the attacker is an Aberration, Celestial,"
                                " Elemental, Fey, Fiend or Undead",
                            ),
                        ),
                    ),
                ),
                notes=(
                    "One willing creature you touch.",
                    "It can't be possessed by, or gain the Charmed or Frightened"
                    " condition from, an Aberration, Celestial, Elemental, Fey,"
                    " Fiend or Undead; if one already has, it has Advantage on any"
                    " new save against that effect.",
                ),
            )
        ]


class PurifyFoodAndDrink(ClassSpell):
    rules = SpellRules(
        name="Purify Food and Drink",
        level=1,
        school=School.TRANSMUTATION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.CLERIC,
            CharacterClass.DRUID,
            CharacterClass.PALADIN,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION, ritual=True),
        range=Range(RangeType.FOOT, 10),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description="You remove poison and rot from nonmagical food and drink in a 5-foot-radius Sphere centered on a point within range.",
        usage_tags=("heal",),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "e4d56cab404ed8a0")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You remove poison and rot from food and drink."),
            Facts(
                (
                    ("Area", "5-foot-radius Sphere centered on a point within range"),
                    (
                        "Effect",
                        "Removes poison and rot from nonmagical food and drink in the area",
                    ),
                )
            ),
        ]


class QuickClothier(ClassSpell):
    rules = SpellRules(
        name="Quick Clothier",
        level=1,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.ARTIFICER, CharacterClass.BARD, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.TOUCH),
        components=Components(verbal=True, somatic=True, material="a set of clothing"),
        duration=Duration(DurationType.HOUR, 24),
        source="D&D Beyond Drops - September 2026",
        description="You alter the appearance of a set of nonmagical clothing that isn’t being worn by someone else. You determine the color, styling, decoration, and form the clothing takes, though you can’t generate clothes worth more than 15 GP. For example, you could transform a tattered Robe into Fine Clothes, or vice versa. At the end of the spell’s duration, the altered clothing returns to its original form.",
        usage_tags=("utility",),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "eaca3ebfd2ed4de1")


class Sanctuary(ClassSpell):
    rules = SpellRules(
        name="Sanctuary",
        level=1,
        school=School.ABJURATION,
        classes=(CharacterClass.ARTIFICER, CharacterClass.CLERIC),
        casting_time=CastingTime(CastingTimeType.BONUS_ACTION),
        range=Range(RangeType.FOOT, 30),
        components=Components(
            verbal=True, somatic=True, material="a shard of glass from a mirror"
        ),
        duration=Duration(DurationType.MINUTE, 1),
        source="Player's Handbook",
        description=(
            "You ward a creature within range. Until the spell ends, any creature who targets the warded creature with an attack roll or a damaging spell must succeed on a Wisdom saving throw or either choose a new target or lose the attack or spell. This spell doesn’t protect the warded creature from areas of effect.\n"
            "The spell ends if the warded creature makes an attack roll, casts a spell, or deals damage."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "5b622bd5322b7466")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You ward a creature against attacks and damaging spells."),
            Facts(
                (
                    ("Target", "A creature within range"),
                    (
                        "Attacker's save",
                        "Wisdom, made until the spell ends by any creature who targets the warded creature with an attack roll or a damaging spell",
                    ),
                    (
                        "Failed save",
                        "The attacker must either choose a new target or lose the attack or spell",
                    ),
                    (
                        "Areas",
                        "Doesn't protect the warded creature from areas of effect",
                    ),
                    (
                        "Ends early",
                        "If the warded creature makes an attack roll, casts a spell, or deals damage",
                    ),
                )
            ),
        ]


class SearingSmite(ClassSpell):
    rules = SpellRules(
        name="Searing Smite",
        level=1,
        school=School.EVOCATION,
        classes=(CharacterClass.PALADIN,),
        casting_time=CastingTime(
            CastingTimeType.BONUS_ACTION,
            trigger="which you take immediately after hitting a target with a Melee weapon or an Unarmed Strike",
        ),
        range=Range(RangeType.SELF),
        components=Components(verbal=True),
        duration=Duration(DurationType.MINUTE, 1),
        source="Player's Handbook",
        description=(
            "As you hit the target, it takes an extra 1d6 Fire damage from the attack. At the start of each of its turns until the spell ends, the target takes 1d6 Fire damage and then makes a Constitution saving throw. On a failed save, the spell continues. On a successful save, the spell ends.\n"
            "Using a Higher-Level Spell Slot. All the damage increases by 1d6 for each spell slot level above 1."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "4e70ab50828aae88")

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
                        "On the hit",
                        "The target takes an extra 1d6 Fire damage from the attack",
                    ),
                    (
                        "Each turn",
                        "At the start of each of its turns until the spell ends, the target takes 1d6 Fire damage and then makes a Constitution saving throw",
                    ),
                    ("Failed save", "The spell continues"),
                    ("Successful save", "The spell ends"),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("All damage", "+1d6 for each spell slot level above 1"),)),),
            ),
        ]


class SilentImage(ClassSpell):
    rules = SpellRules(
        name="Silent Image",
        level=1,
        school=School.ILLUSION,
        classes=(CharacterClass.BARD, CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True, somatic=True, material="a bit of fleece"),
        duration=Duration(DurationType.MINUTE, 10, concentration=True),
        source="Player's Handbook",
        description=(
            "You create the image of an object, a creature, or some other visible phenomenon that is no larger than a 15-foot Cube. The image appears at a spot within range and lasts for the duration. The image is purely visual; it isn’t accompanied by sound, smell, or other sensory effects.\n"
            "As a Magic action, you can cause the image to move to any spot within range. As the image changes location, you can alter its appearance so that its movements appear natural for the image. For example, if you create an image of a creature and move it, you can alter the image so that it appears to be walking.\n"
            "Physical interaction with the image reveals it to be an illusion, since things can pass through it. A creature that takes a Study action to examine the image can determine that it is an illusion with a successful Intelligence (Investigation) check against your spell save DC. If a creature discerns the illusion for what it is, the creature can see through the image."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "fe531cc89a3c70d3")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You create a purely visual image of an object, a creature, or some other visible phenomenon."
            ),
            Facts(
                (
                    ("Size", "No larger than a 15-foot Cube, at a spot within range"),
                    (
                        "Senses",
                        "Visual only: no sound, smell, or other sensory effects",
                    ),
                    (
                        "Move",
                        "As a Magic action, you can move the image to any spot within range; as it moves, you can alter its appearance so its movements appear natural (a creature can appear to be walking)",
                    ),
                    (
                        "Touch",
                        "Physical interaction reveals it as an illusion, since things pass through it",
                    ),
                    (
                        "Seeing through",
                        "A creature that takes the Study action to examine it can make an Intelligence (Investigation) check against your spell save DC; on a success, it can see through the image",
                    ),
                )
            ),
        ]

    def combat_effects(
        self, character: CharacterView | None = None
    ) -> list[CombatEffect]:
        return []


class SilveryBarbs(ClassSpell):
    rules = SpellRules(
        name="Silvery Barbs",
        level=1,
        school=School.ENCHANTMENT,
        classes=(CharacterClass.BARD, CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(
            CastingTimeType.REACTION,
            trigger="which you take when a creature you can see within 60 feet of yourself succeeds on an attack roll, an ability check, or a saving throw",
        ),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Strixhaven: A Curriculum of Chaos",
        description=(
            "You magically distract the triggering creature and turn its momentary uncertainty into encouragement for another creature. The triggering creature must reroll the d20 and use the lower roll.\n"
            "You can then choose a different creature you can see within range (you can choose yourself). The chosen creature has advantage on the next attack roll, ability check, or saving throw it makes within 1 minute. A creature can be empowered by only one use of this spell at a time."
        ),
        usage_tags=("buff", "control", "utility"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "3bf0b2457547fc67")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You magically distract the triggering creature and turn its momentary uncertainty into encouragement for another creature.",
                    ),
                    (
                        "Trigger",
                        "A creature you can see within 60 feet of yourself succeeds on an attack roll, an ability check, or a saving throw",
                    ),
                    (
                        "Reroll",
                        "The triggering creature must reroll the d20 and use the lower roll",
                    ),
                    (
                        "Encourage",
                        "You can then choose a different creature you can see within range (you can choose yourself); it has Advantage on the next attack roll, ability check, or saving throw it makes within 1 minute",
                    ),
                    (
                        "Limit",
                        "A creature can be empowered by only one use of this spell at a time",
                    ),
                )
            )
        ]


class Snare(ClassSpell):
    rules = SpellRules(
        name="Snare",
        level=1,
        school=School.ABJURATION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.DRUID,
            CharacterClass.RANGER,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.MINUTE, 1),
        range=Range(RangeType.TOUCH),
        components=Components(
            somatic=True, material="25 feet of rope, which the spell consumes"
        ),
        duration=Duration(DurationType.HOUR, 8),
        source="Xanathar's Guide to Everything",
        description=(
            "As you cast this spell, you use the rope to create a circle with a 5-foot radius on the ground or the floor. When you finish casting, the rope disappears and the circle becomes a magic trap.\n"
            "This trap is nearly invisible, requiring a successful Intelligence (Investigation) check against your spell save DC to be discerned.\n"
            "The trap triggers when a Small, Medium, or Large creature moves onto the ground or the floor in the spell's radius. That creature must succeed on a Dexterity saving throw or be magically hoisted into the air, leaving it hanging upside down 3 feet above the ground or the floor. The creature is restrained there until the spell ends.\n"
            "A restrained creature can make a Dexterity saving throw at the end of each of its turns, ending the effect on itself on a success. Alternatively, the creature or someone else who can reach it can use an action to make an Intelligence (Arcana) check against your spell save DC. On a success, the restrained effect ends.\n"
            "After the trap is triggered, the spell ends when no creature is restrained by it."
        ),
        usage_tags=("control", "utility"),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "4d3180354c897535")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You use the rope to create a circle with a 5-foot radius on the ground or the floor. When you finish casting, the rope disappears and the circle becomes a magic trap."
            ),
            Facts(
                (
                    (
                        "Spotting it",
                        "The trap is nearly invisible, requiring a successful Intelligence (Investigation) check against your spell save DC to be discerned",
                    ),
                    (
                        "Trigger",
                        "A Small, Medium, or Large creature moves onto the ground or the floor in the spell's radius",
                    ),
                    ("Save", "Dexterity"),
                    (
                        "Failed save",
                        "The creature is magically hoisted into the air, left hanging upside down 3 feet above the ground or the floor, and is Restrained there until the spell ends",
                    ),
                )
            ),
            Facts(
                (
                    (
                        "Repeat save",
                        "A Restrained creature can make a Dexterity saving throw at the end of each of its turns, ending the effect on itself on a success",
                    ),
                    (
                        "Freeing it",
                        "The creature or someone else who can reach it can use an action to make an Intelligence (Arcana) check against your spell save DC; on a success, the Restrained effect ends",
                    ),
                    (
                        "Ends",
                        "After the trap is triggered, the spell ends when no creature is Restrained by it",
                    ),
                )
            ),
        ]


class SpellfireFlare(ClassSpell):
    rules = SpellRules(
        name="Spellfire Flare",
        level=1,
        school=School.EVOCATION,
        classes=(CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Forgotten Realms - Heroes of Faerun",
        description=(
            "You unleash a blast of brilliant fire. Make a ranged spell attack against a target within range; a target gains no benefit from Half Cover or Three-Quarters Cover for this attack roll. On a hit, the target takes 2d10 Radiant damage.\n"
            "Using a Higher-Level Spell Slot. You create an additional blast for each spell slot level above 1. You can direct the blasts at the same target or at different ones. Make a separate attack roll for each blast."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "0cbdaeedf9d49cb4")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Flavor", "You unleash a blast of brilliant fire."),
                    ("Target", "A target within range"),
                    ("Attack", "Ranged spell attack"),
                    (
                        "Cover",
                        "The target gains no benefit from Half Cover or Three-Quarters Cover for this attack roll",
                    ),
                    ("On a hit", "2d10 Radiant damage"),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (
                    Facts(
                        (
                            ("Blasts", "+1 blast for each spell slot level above 1"),
                            (
                                "Directing",
                                "You can direct the blasts at the same target or at different ones; make a separate attack roll for each blast",
                            ),
                        )
                    ),
                ),
            ),
        ]


class TashasCausticBrew(ClassSpell):
    rules = SpellRules(
        name="Tasha's Caustic Brew",
        level=1,
        school=School.EVOCATION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.SORCERER,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF, area=Area(30, AreaShape.LINE)),
        components=Components(
            verbal=True, somatic=True, material="a bit of rotten food"
        ),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Tasha's Cauldron of Everything",
        description=(
            "A stream of acid emanates from you in a line 30 feet long and 5 feet wide in a direction you choose. Each creature in the line must succeed on a Dexterity saving throw or be covered in acid for the spell's duration or until a creature uses its action to scrape or wash the acid off itself or another creature. A creature covered in the acid takes 2d4 acid damage at the start of each of its turns.\n"
            "At Higher Levels. When you cast this spell using a spell slot 2nd level or higher, the damage increases by 2d4 for each slot level above 1st."
        ),
        usage_tags=("control", "damage"),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "e9247773458cc48c")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "A stream of acid emanates from you in a line 30 feet long and 5 feet wide in a direction you choose.",
                    ),
                    (
                        "Area",
                        "A line 30 feet long and 5 feet wide, in a direction you choose",
                    ),
                    ("Save", "Dexterity, made by each creature in the line"),
                    (
                        "Failed save",
                        "Covered in acid for the spell's duration, or until a creature uses its action to scrape or wash the acid off itself or another creature",
                    ),
                    (
                        "Covered",
                        "A creature covered in the acid takes 2d4 Acid damage at the start of each of its turns",
                    ),
                )
            ),
            Option(
                "At Higher Levels",
                (Facts((("Damage", "+2d4 for each slot level above 1st"),)),),
            ),
        ]


class TensersFloatingDisk(ClassSpell):
    rules = SpellRules(
        name="Tenser's Floating Disk",
        level=1,
        school=School.CONJURATION,
        classes=(CharacterClass.WIZARD,),
        casting_time=CastingTime(CastingTimeType.ACTION, ritual=True),
        range=Range(RangeType.FOOT, 30),
        components=Components(verbal=True, somatic=True, material="a drop of mercury"),
        duration=Duration(DurationType.HOUR, 1),
        source="Player's Handbook",
        description=(
            "This spell creates a circular, horizontal plane of force, 3 feet in diameter and 1 inch thick, that floats 3 feet above the ground in an unoccupied space of your choice that you can see within range. The disk remains for the duration and can hold up to 500 pounds. If more weight is placed on it, the spell ends, and everything on the disk falls to the ground.\n"
            "The disk is immobile while you are within 20 feet of it. If you move more than 20 feet away from it, the disk follows you so that it remains within 20 feet of you. It can move across uneven terrain, up or down stairs, slopes and the like, but it can’t cross an elevation change of 10 feet or more. For example, the disk can’t move across a 10-foot-deep pit, nor could it leave such a pit if it was created at the bottom.\n"
            "If you move more than 100 feet from the disk (typically because it can’t move around an obstacle to follow you), the spell ends."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "aabc58073ae7e36d")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You create a floating disk that carries a load and follows you."
            ),
            Facts(
                (
                    (
                        "Disk",
                        "A circular, horizontal plane of force, 3 feet in diameter and 1 inch thick, that floats 3 feet above the ground",
                    ),
                    (
                        "Appears",
                        "In an unoccupied space of your choice that you can see within range, and remains for the duration",
                    ),
                    (
                        "Capacity",
                        "Up to 500 pounds; if more weight is placed on it, the spell ends, and everything on the disk falls to the ground",
                    ),
                )
            ),
            Option(
                "Movement",
                (
                    Facts(
                        (
                            (
                                "Within 20 feet",
                                "The disk is immobile while you are within 20 feet of it",
                            ),
                            (
                                "Following",
                                "If you move more than 20 feet away from it, the disk follows you so that it remains within 20 feet of you",
                            ),
                            (
                                "Terrain",
                                "It can move across uneven terrain, up or down stairs, slopes, and the like",
                            ),
                            (
                                "Elevation",
                                "It can't cross an elevation change of 10 feet or more: it can't move across a 10-foot-deep pit, nor could it leave such a pit if it was created at the bottom",
                            ),
                            (
                                "Too far",
                                "If you move more than 100 feet from the disk (typically because it can't move around an obstacle to follow you), the spell ends",
                            ),
                        )
                    ),
                ),
            ),
        ]


class ThunderousSmite(ClassSpell):
    rules = SpellRules(
        name="Thunderous Smite",
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
            "Your strike rings with thunder that is audible within 300 feet of you, and the target takes an extra 2d6 Thunder damage from the attack. Additionally, if the target is a creature, it must succeed on a Strength saving throw or be pushed 10 feet away from you and have the Prone condition.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 1d6 for each spell slot level above 1."
        ),
        usage_tags=("control", "damage"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "3782b8c3bfa6686a")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "Your strike rings with thunder that is audible within 300 feet of you.",
                    ),
                    (
                        "Sound",
                        "Your strike rings with thunder that is audible within 300 feet of you",
                    ),
                    (
                        "Trigger",
                        "Immediately after you hit a target with a Melee weapon or an Unarmed Strike",
                    ),
                    (
                        "Damage",
                        "The target takes an extra 2d6 Thunder damage from the attack",
                    ),
                    ("Save", "Strength, if the target is a creature"),
                    (
                        "Failed save",
                        "Pushed 10 feet away from you and has the Prone condition",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Damage", "+1d6 for each spell slot level above 1"),)),),
            ),
        ]


class UnseenServant(ClassSpell):
    rules = SpellRules(
        name="Unseen Servant",
        level=1,
        school=School.CONJURATION,
        classes=(CharacterClass.BARD, CharacterClass.WARLOCK, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION, ritual=True),
        range=Range(RangeType.FOOT, 60),
        components=Components(
            verbal=True, somatic=True, material="a bit of string and of wood"
        ),
        duration=Duration(DurationType.HOUR, 1),
        source="Player's Handbook",
        description=(
            "This spell creates an Invisible, mindless, shapeless, Medium force that performs simple tasks at your command until the spell ends. The servant springs into existence in an unoccupied space on the ground within range. It has AC 10, 1 Hit Point, and a Strength of 2, and it can’t attack. If it drops to 0 Hit Points, the spell ends.\n"
            "Once on each of your turns as a Bonus Action, you can mentally command the servant to move up to 15 feet and interact with an object. The servant can perform simple tasks that a human could do, such as fetching things, cleaning, mending, folding clothes, lighting fires, serving food, and pouring drinks. Once you give the command, the servant performs the task to the best of its ability until it completes the task, then waits for your next command.\n"
            "If you command the servant to perform a task that would move it more than 60 feet away from you, the spell ends."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "12122804b4a9ec51")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You create an Invisible, mindless, shapeless, Medium force that performs simple tasks at your command until the spell ends."
            ),
            Facts(
                (
                    ("Appears", "In an unoccupied space on the ground within range"),
                    (
                        "Statistics",
                        "AC 10, 1 Hit Point, and a Strength of 2; it can't attack",
                    ),
                    ("0 Hit Points", "If it drops to 0 Hit Points, the spell ends"),
                )
            ),
            Option(
                "Commanding It",
                (
                    Facts(
                        (
                            (
                                "Command",
                                "Once on each of your turns as a Bonus Action, you can mentally command it to move up to 15 feet and interact with an object",
                            ),
                            (
                                "Tasks",
                                "Simple tasks that a human could do, such as fetching things, cleaning, mending, folding clothes, lighting fires, serving food, and pouring drinks",
                            ),
                            (
                                "Carrying out",
                                "It performs the task to the best of its ability until it completes the task, then waits for your next command",
                            ),
                            (
                                "Range limit",
                                "If you command it to perform a task that would move it more than 60 feet away from you, the spell ends",
                            ),
                        )
                    ),
                ),
            ),
        ]


class Wardaway(ClassSpell):
    rules = SpellRules(
        name="Wardaway",
        level=1,
        school=School.ABJURATION,
        classes=(
            CharacterClass.BARD,
            CharacterClass.CLERIC,
            CharacterClass.PALADIN,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(
            verbal=True, somatic=True, material="a miniature clay hand"
        ),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Forgotten Realms - Heroes of Faerun",
        description=(
            "You hurl a disorienting magical force toward one creature within range. The target makes a Constitution saving throw; Constructs and Undead automatically succeed on this save.\n"
            "On a failed save, the target takes 2d4 Force damage, its Speed is halved until the start of your next turn, and on its next turn, it can take only an action or a Bonus Action (but not both). On a successful save, the target takes half as much damage only.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 2d4 for every spell slot level above 1."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "438ee629b6e538c4")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You hurl a disorienting magical force toward one creature within range.",
                    ),
                    ("Target", "One creature within range"),
                    (
                        "Save",
                        "Constitution; Constructs and Undead automatically succeed",
                    ),
                )
            ),
            Option(
                "Failed Save",
                (
                    Facts(
                        (
                            ("Damage", "2d4 Force damage"),
                            ("Speed", "Halved until the start of your next turn"),
                            (
                                "Its next turn",
                                "It can take only an action or a Bonus Action (but not both)",
                            ),
                        )
                    ),
                ),
            ),
            Facts((("Successful save", "Half as much damage only"),)),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Damage", "+2d4 for each spell slot level above 1"),)),),
            ),
        ]


class WrathfulSmite(ClassSpell):
    rules = SpellRules(
        name="Wrathful Smite",
        level=1,
        school=School.NECROMANCY,
        classes=(CharacterClass.PALADIN,),
        casting_time=CastingTime(
            CastingTimeType.BONUS_ACTION,
            trigger="which you take immediately after hitting a creature with a Melee weapon or an Unarmed Strike",
        ),
        range=Range(RangeType.SELF),
        components=Components(verbal=True),
        duration=Duration(DurationType.MINUTE, 1),
        source="Player's Handbook",
        description=(
            "The target takes an extra 1d6 Necrotic damage from the attack, and it must succeed on a Wisdom saving throw or have the Frightened condition until the spell ends. At the end of each of its turns, the Frightened target repeats the save, ending the spell on itself on a success.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 1d6 for each spell slot level above 1."
        ),
        usage_tags=("control", "damage"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "5dad9c0970453328")

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
                        "The target takes an extra 1d6 Necrotic damage from the attack",
                    ),
                    ("Save", "Wisdom"),
                    ("Failed save", "Frightened until the spell ends"),
                    (
                        "Repeat save",
                        "At the end of each of its turns, ending the spell on itself on a success",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Damage", "+1d6 for each spell slot level above 1"),)),),
            ),
        ]


class ZephyrStrike(ClassSpell):
    rules = SpellRules(
        name="Zephyr Strike",
        level=1,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.RANGER,),
        casting_time=CastingTime(CastingTimeType.BONUS_ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Xanathar's Guide to Everything",
        description=(
            "You move like the wind. For the duration, your movement doesn't provoke opportunity attacks.\n"
            "Once before the spell ends, you can give yourself advantage on one weapon attack roll on your turn. That attack deals an extra 1d8 force damage on a hit. Whether you hit or miss, your walking speed increases by 30 feet until the end of that turn."
        ),
        usage_tags=("buff", "damage"),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "ee4e1ff0e48bef93")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Flavor", "You move like the wind."),
                    (
                        "Movement",
                        "For the duration, your movement doesn't provoke opportunity attacks",
                    ),
                )
            ),
            Option(
                "Once Before the Spell Ends",
                (
                    Facts(
                        (
                            (
                                "Advantage",
                                "You can give yourself Advantage on one weapon attack roll on your turn",
                            ),
                            ("On a hit", "That attack deals an extra 1d8 Force damage"),
                            (
                                "Hit or miss",
                                "Your walking speed increases by 30 feet until the end of that turn",
                            ),
                        )
                    ),
                ),
            ),
        ]


class GiftOfAlacrity(ClassSpell):
    rules = SpellRules(
        name="Gift of Alacrity",
        level=1,
        school=School.DIVINATION,
        classes=(CharacterClass.WIZARD,),
        casting_time=CastingTime(CastingTimeType.MINUTE, 1),
        range=Range(RangeType.TOUCH),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.HOUR, 8),
        source="Explorer's Guide to Wildemount",
        description="You touch a willing creature. For the duration, the target can add 1d8 to its initiative rolls.",
        usage_tags=("buff",),
        target=FeatureTarget.ALLY,
        school_note="Dunamancy:Chronurgy",
    )
    converted_from = RecordStamp("spells_dnd5e.json", "b041de1795ec83e8")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Target", "A willing creature you touch"),
                    (
                        "Effect",
                        "For the duration, it can add 1d8 to its initiative rolls",
                    ),
                )
            )
        ]


class MagnifyGravity(ClassSpell):
    rules = SpellRules(
        name="Magnify Gravity",
        level=1,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.WIZARD,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.ROUND, 1),
        source="Explorer's Guide to Wildemount",
        description=(
            "The gravity in a 10-foot-radius sphere centered on a point you can see within range increases for a moment. Each creature in the sphere on the turn when you cast the spell must make a Constitution saving throw. On a failed save, a creature takes 2d8 force damage, and its speed is halved until the end of its next turn. On a successful save, a creature takes half as much damage and suffers no reduction to its speed.\n"
            "Until the start of your next turn, any object that isn't being worn or carried in the sphere requires a successful Strength check against your spell save DC to pick up or move.\n"
            "At Higher Levels. When you cast this spell using a spell slot of 2nd level or higher, the damage increases by 1d8 for each slot level above 1st."
        ),
        usage_tags=("damage", "utility"),
        target=FeatureTarget.AREA,
        school_note="Dunamancy:Graviturgy",
    )
    converted_from = RecordStamp("spells_dnd5e.json", "3b8332b67998db4a")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "The gravity in a 10-foot-radius sphere centered on a point you can see within range increases for a moment.",
                    ),
                    (
                        "Area",
                        "10-foot-radius sphere centered on a point you can see within range",
                    ),
                    (
                        "Save",
                        "Constitution, made by each creature in the sphere on the turn when you cast the spell",
                    ),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (
                    (
                        "2d8 Force damage, and its speed is halved until the end of its next turn",
                        "Half as much damage, and no reduction to its speed",
                    ),
                ),
            ),
            Facts(
                (
                    (
                        "Objects",
                        "Until the start of your next turn, any object in the sphere that isn't being worn or carried requires a successful Strength check against your spell save DC to pick up or move",
                    ),
                )
            ),
            Option(
                "At Higher Levels",
                (Facts((("Damage", "+1d8 for each slot level above 1st"),)),),
            ),
        ]


SPELLS = [
    AbsorbElements,
    Alarm,
    AnimalFriendship,
    ArmorOfAgathys,
    ArmsOfHadar,
    Bane,
    BeastBond,
    Bless,
    BurningHands,
    BuzzingBee,
    Catapult,
    CauseFear,
    Ceremony,
    ChaosBolt,
    CharmPerson,
    ChromaticOrb,
    ColorSpray,
    Command,
    CompelledDuel,
    ComprehendLanguages,
    CreateOrDestroyWater,
    CureWounds,
    DetectEvilAndGood,
    DetectMagic,
    DetectPoisonAndDisease,
    DisguiseSelf,
    DissonantWhispers,
    DistortValue,
    DivineFavor,
    DivineSmite,
    EarthTremor,
    EnsnaringStrike,
    Entangle,
    ExpeditiousRetreat,
    FaerieFire,
    FalseLife,
    FeatherFall,
    FeignInterest,
    FindFamiliar,
    FogCloud,
    FrostFingers,
    GiftOfAlacrity,
    Goodberry,
    Grease,
    GuidingBolt,
    HailOfThorns,
    HealingWord,
    HellishRebuke,
    Heroism,
    Hex,
    HuntersMark,
    IceKnife,
    Identify,
    IllusoryScript,
    InflictWounds,
    InsidiousRhythm,
    JimsMagicMissile,
    Jump,
    Longstrider,
    MageArmor,
    MagicMissile,
    MagnifyGravity,
    ProtectionFromEvilAndGood,
    PurifyFoodAndDrink,
    QuickClothier,
    RayOfSickness,
    Sanctuary,
    SearingSmite,
    Shield,
    ShieldOfFaith,
    SilentImage,
    SilveryBarbs,
    Sleep,
    Snare,
    SpeakWithAnimals,
    SpellfireFlare,
    TashasCausticBrew,
    TashasHideousLaughter,
    TensersFloatingDisk,
    ThunderousSmite,
    Thunderwave,
    UnseenServant,
    Wardaway,
    WitchBolt,
    WrathfulSmite,
    ZephyrStrike,
]
