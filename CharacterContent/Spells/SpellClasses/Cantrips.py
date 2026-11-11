"""Cantrips as classes (CharacterContent/Spells/SpellFactory/ClassSpell.py),
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
    CombatInstances,
    EffectRoll,
    TurnEdge,
    TurnOf,
)
from Model.Content.Feature import FeatureTarget
from Model.Content.FeatureText import Block, Facts, Option, Paragraph, Table
from Model.View import CharacterView


class ChillTouch(ClassSpell):
    rules = SpellRules(
        name="Chill Touch",
        level=0,
        school=School.NECROMANCY,
        classes=(
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.TOUCH),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "Channeling the chill of the grave, make a melee spell attack against a target within reach. On a hit, the target takes 1d10 Necrotic damage, and it can’t regain Hit Points until the end of your next turn.\n"
            "Cantrip Upgrade. The damage increases by 1d10 when you reach levels 5 (2d10), 11 (3d10), and 17 (4d10)."
        ),
        usage_tags=("damage", "heal"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "83cd5aaddcb3f54e")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "Channeling the chill of the grave, make a melee spell attack against a target within reach.",
                    ),
                    ("Target", "A target within your reach"),
                    ("Attack", "Melee spell attack"),
                    (
                        "On a hit",
                        "1d10 Necrotic damage, and the target can't regain Hit Points until the end of your next turn",
                    ),
                )
            ),
            Option(
                "Cantrip Upgrade",
                (
                    Table(
                        ("Character level", "Damage"),
                        (("1", "1d10"), ("5", "2d10"), ("11", "3d10"), ("17", "4d10")),
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
                        "1d10",
                        DamageType.NECROTIC,
                        cantrip=((5, "2d10"), (11, "3d10"), (17, "4d10")),
                    ),
                ),
                conditions=(
                    CombatCondition("Chill Touch", until=(TurnEdge.END, TurnOf.SOURCE)),
                ),
                notes=(
                    "A melee spell attack. On a hit, the target can't regain Hit Points until the end of your next turn.",
                ),
            )
        ]


class EldritchBlast(ClassSpell):
    rules = SpellRules(
        name="Eldritch Blast",
        level=0,
        school=School.EVOCATION,
        classes=(CharacterClass.WARLOCK,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 120),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "You hurl a beam of crackling energy. Make a ranged spell attack against one creature or object in range. On a hit, the target takes 1d10 Force damage.\n"
            "Cantrip Upgrade. The spell creates two beams at level 5, three beams at level 11, and four beams at level 17. You can direct the beams at the same target or at different ones. Make a separate attack roll for each beam."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "3d2acbc38b477571")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Flavor", "You hurl a beam of crackling energy."),
                    ("Target", "One creature or object within range"),
                    ("Attack", "Ranged spell attack"),
                    ("On a hit", "1d10 Force damage"),
                )
            ),
            Option(
                "Cantrip Upgrade",
                (
                    Table(
                        ("Character level", "Beams"),
                        (("1", "1"), ("5", "2"), ("11", "3"), ("17", "4")),
                    ),
                    Facts(
                        (
                            (
                                "Beams",
                                "Direct them at the same target or different ones, with a separate attack roll for each beam",
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
                roll=EffectRoll.ATTACK,
                damage=(CombatDamage("1d10", DamageType.FORCE),),
                instances=CombatInstances(
                    1, cantrip=((5, 2), (11, 3), (17, 4)), noun="beam"
                ),
                notes=(
                    "The beams can go at one target or several: lower Times and apply again for the others.",
                ),
            )
        ]


class Friends(ClassSpell):
    rules = SpellRules(
        name="Friends",
        level=0,
        school=School.ENCHANTMENT,
        classes=(
            CharacterClass.BARD,
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 10),
        components=Components(somatic=True, material="some makeup"),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "You magically emanate a sense of friendship toward one creature you can see within range. The target must succeed on a Wisdom saving throw or have the Charmed condition for the duration. The target succeeds automatically if it isn’t a Humanoid, if you’re fighting it, or if you have cast this spell on it within the past 24 hours.\n"
            "The spell ends early if the target takes damage or if you make an attack roll, deal damage, or force anyone to make a saving throw. When the spell ends, the target knows it was Charmed by you."
        ),
        usage_tags=("control", "damage", "heal"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "ce527c2620ceb478")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You magically emanate a sense of friendship toward one creature you can see within range.",
                    ),
                    ("Target", "One creature you can see within range"),
                    ("Save", "Wisdom"),
                    ("Failed save", "Charmed for the duration"),
                    (
                        "Auto-success",
                        "The target succeeds automatically if it isn't a Humanoid, if you're fighting it, or if you have cast this spell on it within the past 24 hours",
                    ),
                    (
                        "Ends early",
                        "If the target takes damage, or if you make an attack roll, deal damage, or force anyone to make a saving throw",
                    ),
                    (
                        "Afterward",
                        "When the spell ends, the target knows it was Charmed by you",
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
                save_ability=Ability.WISDOM,
                conditions=(CombatCondition(Condition.CHARMED),),
                notes=(
                    "The target succeeds automatically if it isn't a Humanoid, if you're fighting it, or if you've cast this on it in the past 24 hours.",
                    "The spell ends early if the target takes damage or you make an attack roll, deal damage or force a saving throw.",
                ),
            )
        ]


class Guidance(ClassSpell):
    rules = SpellRules(
        name="Guidance",
        level=0,
        school=School.DIVINATION,
        classes=(CharacterClass.ARTIFICER, CharacterClass.CLERIC, CharacterClass.DRUID),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.TOUCH),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description="You touch a willing creature and choose a skill. Until the spell ends, the creature adds 1d4 to any ability check using the chosen skill.",
        usage_tags=("buff",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "5133ea0e9ab349ef")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You touch a willing creature and choose a skill."),
            Facts(
                (
                    ("Target", "A willing creature you touch"),
                    (
                        "Effect",
                        "Until the spell ends, the creature adds 1d4 to any ability check using the chosen skill",
                    ),
                )
            ),
        ]

    def combat_effects(
        self, character: CharacterView | None = None
    ) -> list[CombatEffect]:
        return [
            CombatEffect(
                conditions=(CombatCondition("Guidance"),),
                notes=(
                    "A willing creature adds 1d4 to ability checks with the skill you choose.",
                ),
            )
        ]


class Message(ClassSpell):
    rules = SpellRules(
        name="Message",
        level=0,
        school=School.TRANSMUTATION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.BARD,
            CharacterClass.DRUID,
            CharacterClass.SORCERER,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 120),
        components=Components(somatic=True, material="a copper wire"),
        duration=Duration(DurationType.ROUND, 1),
        source="Player's Handbook",
        description=(
            "You point toward a creature within range and whisper a message. The target (and only the target) hears the message and can reply in a whisper that only you can hear.\n"
            "You can cast this spell through solid objects if you are familiar with the target and know it is beyond the barrier. Magical silence; 1 foot of stone, metal, or wood; or a thin sheet of lead blocks the spell."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "cbea29bd1f741b32")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You point toward a creature within range and whisper a message."
            ),
            Facts(
                (
                    ("Target", "A creature within range"),
                    (
                        "Effect",
                        "The target (and only the target) hears the message and can reply in a whisper that only you can hear",
                    ),
                    (
                        "Through objects",
                        "You can cast it through solid objects if you are familiar with the target and know it is beyond the barrier",
                    ),
                    (
                        "Blocked by",
                        "Magical silence; 1 foot of stone, metal, or wood; or a thin sheet of lead",
                    ),
                )
            ),
        ]

    def combat_effects(
        self, character: CharacterView | None = None
    ) -> list[CombatEffect]:
        return []


class MinorIllusion(ClassSpell):
    rules = SpellRules(
        name="Minor Illusion",
        level=0,
        school=School.ILLUSION,
        classes=(
            CharacterClass.BARD,
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 30),
        components=Components(somatic=True, material="a bit of fleece"),
        duration=Duration(DurationType.MINUTE, 1),
        source="Player's Handbook",
        description=(
            "You create a sound or an image of an object within range that lasts for the duration. See the descriptions below for the effects of each. The illusion ends if you cast this spell again.\n"
            "If a creature takes a Study action to examine the sound or image, the creature can determine that it is an illusion with a successful Intelligence (Investigation) check against your spell save DC. If a creature discerns the illusion for what it is, the illusion becomes faint to the creature.\n"
            "Sound. If you create a sound, its volume can range from a whisper to a scream. It can be your voice, someone else’s voice, a lion’s roar, a beating of drums, or any other sound you choose. The sound continues unabated throughout the duration, or you can make discrete sounds at different times before the spell ends.\n"
            "Image. If you create an image of an object—such as a chair, muddy footprints, or a small chest—it must be no larger than a 5-foot Cube. The image can’t create sound, light, smell, or any other sensory effect. Physical interaction with the image reveals it to be an illusion, since things can pass through it."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "aed6bc67bb8fbc1b")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You create a sound or an image of an object within range. The illusion ends if you cast this spell again."
            ),
            Option(
                "Sound",
                (
                    Facts(
                        (
                            ("Volume", "Anything from a whisper to a scream"),
                            (
                                "Sound",
                                "Your voice, someone else's voice, a lion's roar, a beating of drums, or any other sound you choose",
                            ),
                            (
                                "Timing",
                                "Continuous for the duration, or discrete sounds at different times before the spell ends",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Image",
                (
                    Facts(
                        (
                            (
                                "Size",
                                "An object no larger than a 5-foot Cube, such as a chair, muddy footprints, or a small chest",
                            ),
                            (
                                "Senses",
                                "Visual only: no sound, light, smell, or any other sensory effect",
                            ),
                            (
                                "Touch",
                                "Physical interaction reveals it as an illusion, since things pass through it",
                            ),
                        )
                    ),
                ),
            ),
            Facts(
                (
                    (
                        "Seeing through",
                        "A creature that takes the Study action to examine the illusion can make an Intelligence (Investigation) check against your spell save DC; on a success, it determines that it is an illusion, and the illusion becomes faint to it",
                    ),
                )
            ),
        ]

    def combat_effects(
        self, character: CharacterView | None = None
    ) -> list[CombatEffect]:
        return []


class ProduceFlame(ClassSpell):
    rules = SpellRules(
        name="Produce Flame",
        level=0,
        school=School.CONJURATION,
        classes=(CharacterClass.DRUID,),
        casting_time=CastingTime(CastingTimeType.BONUS_ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 10),
        source="Player's Handbook",
        description=(
            "A flickering flame appears in your hand and remains there for the duration. While there, the flame emits no heat and ignites nothing, and it sheds Bright Light in a 20-foot radius and Dim Light for an additional 20 feet. The spell ends if you cast it again.\n"
            "Until the spell ends, you can take a Magic action to hurl fire at a creature or an object within 60 feet of you. Make a ranged spell attack. On a hit, the target takes 1d8 Fire damage.\n"
            "Cantrip Upgrade. The damage increases by 1d8 when you reach levels 5 (2d8), 11 (3d8), and 17 (4d8)."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "882e447360b11d03")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "A flickering flame appears in your hand and remains there for the duration.",
                    ),
                    ("Appears", "In your hand, where it remains for the duration"),
                    (
                        "Light",
                        "Bright Light in a 20-foot radius and Dim Light for an additional 20 feet",
                    ),
                    ("Harmless", "The flame emits no heat and ignites nothing"),
                    ("Ends early", "If you cast this spell again"),
                )
            ),
            Option(
                "Hurl Flame",
                (
                    Facts(
                        (
                            ("Action", "Magic action, until the spell ends"),
                            ("Target", "A creature or an object within 60 feet of you"),
                            ("Attack", "Ranged spell attack"),
                            ("On a hit", "1d8 Fire damage"),
                        )
                    ),
                ),
            ),
            Option(
                "Cantrip Upgrade",
                (
                    Table(
                        ("Character level", "Damage"),
                        (("1", "1d8"), ("5", "2d8"), ("11", "3d8"), ("17", "4d8")),
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
                        "1d8",
                        DamageType.FIRE,
                        cantrip=((5, "2d8"), (11, "3d8"), (17, "4d8")),
                    ),
                ),
                notes=(
                    "Casting it (a Bonus Action) makes the flame; hurling it is a Magic action, on this turn or a later one.",
                ),
            )
        ]


class Resistance(ClassSpell):
    rules = SpellRules(
        name="Resistance",
        level=0,
        school=School.ABJURATION,
        classes=(CharacterClass.ARTIFICER, CharacterClass.CLERIC, CharacterClass.DRUID),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.TOUCH),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description="You touch a willing creature and choose a damage type: Acid, Bludgeoning, Cold, Fire, Lightning, Necrotic, Piercing, Poison, Radiant, Slashing, or Thunder. When the creature takes damage of the chosen type before the spell ends, the creature reduces the total damage taken by 1d4. A creature can benefit from this spell only once per turn.",
        usage_tags=("buff",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "53254148a1bbded5")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You touch a willing creature and protect it against one type of damage."
            ),
            Facts(
                (
                    ("Target", "A willing creature you touch"),
                    (
                        "Damage type",
                        "Choose one: Acid, Bludgeoning, Cold, Fire, Lightning, Necrotic, Piercing, Poison, Radiant, Slashing, or Thunder",
                    ),
                    (
                        "Effect",
                        "When the creature takes damage of the chosen type before the spell ends, it reduces the total damage taken by 1d4",
                    ),
                    (
                        "Limit",
                        "A creature can benefit from this spell only once per turn",
                    ),
                )
            ),
        ]

    def combat_effects(
        self, character: CharacterView | None = None
    ) -> list[CombatEffect]:
        return [
            CombatEffect(
                conditions=(CombatCondition("Resistance"),),
                notes=(
                    "Choose a damage type: when the creature takes damage of that type, it reduces the total by 1d4, once per turn.",
                ),
            )
        ]


class SacredFlame(ClassSpell):
    rules = SpellRules(
        name="Sacred Flame",
        level=0,
        school=School.EVOCATION,
        classes=(CharacterClass.CLERIC,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "Flame-like radiance descends on a creature that you can see within range. The target must succeed on a Dexterity saving throw or take 1d8 Radiant damage. The target gains no benefit from Half Cover or Three-Quarters Cover for this save.\n"
            "Cantrip Upgrade. The damage increases by 1d8 when you reach levels 5 (2d8), 11 (3d8), and 17 (4d8)."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "d54c6e18def10e63")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "Flame-like radiance descends on a creature that you can see within range.",
                    ),
                    ("Target", "A creature you can see within range"),
                    ("Save", "Dexterity"),
                    ("Failed save", "1d8 Radiant damage"),
                    ("Successful save", "No damage"),
                    (
                        "Cover",
                        "The target gains no benefit from Half Cover or Three-Quarters Cover for this save",
                    ),
                )
            ),
            Option(
                "Cantrip Upgrade",
                (
                    Table(
                        ("Character level", "Damage"),
                        (("1", "1d8"), ("5", "2d8"), ("11", "3d8"), ("17", "4d8")),
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
                damage=(
                    CombatDamage(
                        "1d8",
                        DamageType.RADIANT,
                        cantrip=((5, "2d8"), (11, "3d8"), (17, "4d8")),
                    ),
                ),
                notes=(
                    "The target gains no benefit from Half Cover or Three-Quarters Cover for this save.",
                ),
            )
        ]


class SpareTheDying(ClassSpell):
    rules = SpellRules(
        name="Spare the Dying",
        level=0,
        school=School.NECROMANCY,
        classes=(CharacterClass.ARTIFICER, CharacterClass.CLERIC, CharacterClass.DRUID),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 15),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "Choose a creature within range that has 0 Hit Points and isn’t dead. The creature becomes Stable.\n"
            "Cantrip Upgrade. The range doubles when you reach levels 5 (30 feet), 11 (60 feet), and 17 (120 feet)."
        ),
        usage_tags=("heal",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "1c7718b2a5528476")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You stabilize a dying creature."),
            Facts(
                (
                    (
                        "Target",
                        "A creature within range that has 0 Hit Points and isn't dead",
                    ),
                    ("Effect", "The creature becomes Stable"),
                )
            ),
            Option(
                "Cantrip Upgrade",
                (
                    Table(
                        ("Character level", "Range"),
                        (
                            ("1", "15 feet"),
                            ("5", "30 feet"),
                            ("11", "60 feet"),
                            ("17", "120 feet"),
                        ),
                    ),
                ),
            ),
        ]

    def combat_effects(
        self, character: CharacterView | None = None
    ) -> list[CombatEffect]:
        return [
            CombatEffect(
                notes=(
                    "A creature with 0 Hit Points that isn't dead becomes Stable. Range 15 feet, doubling at character levels 5, 11 and 17.",
                )
            )
        ]


class StarryWisp(ClassSpell):
    rules = SpellRules(
        name="Starry Wisp",
        level=0,
        school=School.EVOCATION,
        classes=(CharacterClass.BARD, CharacterClass.DRUID),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "You launch a mote of light at one creature or object within range. Make a ranged spell attack against the target. On a hit, the target takes 1d8 Radiant damage, and until the end of your next turn, it emits Dim Light in a 10-foot radius and can’t benefit from the Invisible condition.\n"
            "Cantrip Upgrade. The damage increases by 1d8 when you reach levels 5 (2d8), 11 (3d8), and 17 (4d8)."
        ),
        usage_tags=("buff", "damage"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "d94178ddb3907e36")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You launch a mote of light at one creature or object within range.",
                    ),
                    ("Target", "One creature or object within range"),
                    ("Attack", "Ranged spell attack"),
                    (
                        "On a hit",
                        "1d8 Radiant damage, and until the end of your next turn, the target emits Dim Light in a 10-foot radius and can't benefit from the Invisible condition",
                    ),
                )
            ),
            Option(
                "Cantrip Upgrade",
                (
                    Table(
                        ("Character level", "Damage"),
                        (("1", "1d8"), ("5", "2d8"), ("11", "3d8"), ("17", "4d8")),
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
                        "1d8",
                        DamageType.RADIANT,
                        cantrip=((5, "2d8"), (11, "3d8"), (17, "4d8")),
                    ),
                ),
                notes=(
                    "On a hit, until the end of your next turn the target sheds Dim Light in a 10-foot radius and can't benefit from the Invisible condition.",
                ),
            )
        ]


class Thaumaturgy(ClassSpell):
    rules = SpellRules(
        name="Thaumaturgy",
        level=0,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.CLERIC,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 30),
        components=Components(verbal=True),
        duration=Duration(DurationType.MINUTE, 1, up_to=True),
        source="Player's Handbook",
        description=(
            "You manifest a minor wonder within range. You create one of the effects below within range. If you cast this spell multiple times, you can have up to three of its 1-minute effects active at a time.\n"
            "Altered Eyes. You alter the appearance of your eyes for 1 minute.\n"
            "Booming Voice. Your voice booms up to three times as loud as normal for 1 minute. For the duration, you have Advantage on Charisma (Intimidation) checks.\n"
            "Fire Play. You cause flames to flicker, brighten, dim, or change color for 1 minute.\n"
            "Invisible Hand. You instantaneously cause an unlocked door or window to fly open or slam shut.\n"
            "Phantom Sound. You create an instantaneous sound that originates from a point of your choice within range, such as a rumble of thunder, the cry of a raven, or ominous whispers.\n"
            "Tremors. You cause harmless tremors in the ground for 1 minute."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "8fd34fa3e2da3372")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts((("Flavor", "You manifest a minor wonder within range."),)),
            Paragraph("You create one of the effects below within range."),
            Facts(
                (
                    (
                        "Active effects",
                        "Up to three of its 1-minute effects at a time, from repeated castings",
                    ),
                )
            ),
            Table(
                ("Effect", "What it does", "Lasts"),
                (
                    ("Altered Eyes", "The appearance of your eyes changes", "1 minute"),
                    (
                        "Booming Voice",
                        "Your voice booms up to three times as loud as normal, and you have Advantage on Charisma (Intimidation) checks",
                        "1 minute",
                    ),
                    (
                        "Fire Play",
                        "Flames flicker, brighten, dim, or change color",
                        "1 minute",
                    ),
                    (
                        "Invisible Hand",
                        "An unlocked door or window flies open or slams shut",
                        "Instantaneous",
                    ),
                    (
                        "Phantom Sound",
                        "A sound from a point of your choice within range, such as a rumble of thunder, the cry of a raven, or ominous whispers",
                        "Instantaneous",
                    ),
                    ("Tremors", "Harmless tremors in the ground", "1 minute"),
                ),
            ),
        ]

    def combat_effects(
        self, character: CharacterView | None = None
    ) -> list[CombatEffect]:
        return []


class TollTheDead(ClassSpell):
    rules = SpellRules(
        name="Toll the Dead",
        level=0,
        school=School.NECROMANCY,
        classes=(CharacterClass.CLERIC, CharacterClass.WARLOCK, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "You point at one creature you can see within range, and the single chime of a dolorous bell is audible within 10 feet of the target. The target must succeed on a Wisdom saving throw or take 1d8 Necrotic damage. If the target is missing any of its Hit Points, it instead takes 1d12 Necrotic damage.\n"
            "Cantrip Upgrade. The damage increases by one die when you reach levels 5 (2d8 or 2d12), 11 (3d8 or 3d12), and 17 (4d8 or 4d12)."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "fbdcedbdc9fe3c57")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You point at one creature you can see within range, and the single chime of a dolorous bell is audible within 10 feet of the target.",
                    ),
                    ("Sound", "The chime is audible within 10 feet of the target"),
                    ("Target", "One creature you can see within range"),
                    ("Save", "Wisdom"),
                )
            ),
            Table(
                ("Target", "Failed save", "Successful save"),
                (
                    ("At full Hit Points", "1d8 Necrotic damage", "No damage"),
                    ("Missing any Hit Points", "1d12 Necrotic damage", "No damage"),
                ),
            ),
            Option(
                "Cantrip Upgrade",
                (
                    Table(
                        ("Character level", "Full Hit Points", "Missing Hit Points"),
                        (
                            ("1", "1d8", "1d12"),
                            ("5", "2d8", "2d12"),
                            ("11", "3d8", "3d12"),
                            ("17", "4d8", "4d12"),
                        ),
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
                damage=(
                    CombatDamage(
                        "1d8",
                        DamageType.NECROTIC,
                        cantrip=((5, "2d8"), (11, "3d8"), (17, "4d8")),
                    ),
                ),
                notes=(
                    "For a target that has all its Hit Points: pick the hurt-target row for one that's missing any.",
                ),
            ),
            CombatEffect(
                name="Toll the Dead (hurt target)",
                roll=EffectRoll.SAVE,
                save_ability=Ability.WISDOM,
                damage=(
                    CombatDamage(
                        "1d12",
                        DamageType.NECROTIC,
                        cantrip=((5, "2d12"), (11, "3d12"), (17, "4d12")),
                    ),
                ),
                notes=("For a target missing any of its Hit Points.",),
            ),
        ]


class TrueStrike(ClassSpell):
    rules = SpellRules(
        name="True Strike",
        level=0,
        school=School.DIVINATION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.BARD,
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(
            somatic=True,
            material="a weapon with which you have proficiency and that is worth 1+ CP",
        ),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "Guided by a flash of magical insight, you make one attack with the weapon used in the spell’s casting. The attack uses your spellcasting ability for the attack and damage rolls instead of using Strength or Dexterity. If the attack deals damage, it can be Radiant damage or the weapon’s normal damage type (your choice).\n"
            "Cantrip Upgrade. Whether you deal Radiant damage or the weapon’s normal damage type, the attack deals extra Radiant damage when you reach levels 5 (1d6), 11 (2d6), and 17 (3d6)."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "f6296cce3db8696c")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "Guided by a flash of magical insight, you make one attack with the weapon used in the spell's casting.",
                    ),
                    (
                        "Attack",
                        "One attack with the weapon used in the spell's casting",
                    ),
                    (
                        "Attack and damage",
                        "Use your spellcasting ability instead of Strength or Dexterity",
                    ),
                    (
                        "Damage type",
                        "If the attack deals damage, it can be Radiant damage or the weapon's normal damage type (your choice)",
                    ),
                )
            ),
            Option(
                "Cantrip Upgrade",
                (
                    Table(
                        ("Character level", "Extra Radiant damage"),
                        (("1", "None"), ("5", "1d6"), ("11", "2d6"), ("17", "3d6")),
                    ),
                    Facts(
                        (
                            (
                                "Extra damage",
                                "Always Radiant, whichever type the attack deals",
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
                roll=EffectRoll.ATTACK,
                notes=(
                    "One attack with the weapon used in the casting, using your spellcasting ability for its attack and damage rolls: give the weapon's damage. It can deal Radiant damage instead of its own type.",
                    "Extra Radiant damage: 1d6 from character level 5, 2d6 from 11, 3d6 from 17.",
                ),
            )
        ]


class ViciousMockery(ClassSpell):
    rules = SpellRules(
        name="Vicious Mockery",
        level=0,
        school=School.ENCHANTMENT,
        classes=(CharacterClass.BARD,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "You unleash a string of insults laced with subtle enchantments at one creature you can see or hear within range. The target must succeed on a Wisdom saving throw or take 1d6 Psychic damage and have Disadvantage on the next attack roll it makes before the end of its next turn.\n"
            "Cantrip Upgrade. The damage increases by 1d6 when you reach levels 5 (2d6), 11 (3d6), and 17 (4d6)."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "8d3fb1d4dfb5c03c")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You unleash a string of insults laced with subtle enchantments at one creature you can see or hear within range.",
                    ),
                    ("Target", "One creature you can see or hear within range"),
                    ("Save", "Wisdom"),
                    (
                        "Failed save",
                        "1d6 Psychic damage, and Disadvantage on the next attack roll it makes before the end of its next turn",
                    ),
                    ("Successful save", "No effect"),
                )
            ),
            Option(
                "Cantrip Upgrade",
                (
                    Table(
                        ("Character level", "Damage"),
                        (("1", "1d6"), ("5", "2d6"), ("11", "3d6"), ("17", "4d6")),
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
                damage=(
                    CombatDamage(
                        "1d6",
                        DamageType.PSYCHIC,
                        cantrip=((5, "2d6"), (11, "3d6"), (17, "4d6")),
                    ),
                ),
                notes=(
                    "On a failed save, the target also has Disadvantage on the next attack roll it makes before the end of its next turn.",
                ),
            )
        ]


class AcidSplash(ClassSpell):
    rules = SpellRules(
        name="Acid Splash",
        level=0,
        school=School.EVOCATION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.SORCERER,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "You create an acidic bubble at a point within range, where it explodes in a 5-foot-radius Sphere. Each creature in that Sphere must succeed on a Dexterity saving throw or take 1d6 Acid damage.\n"
            "Cantrip Upgrade. The damage increases by 1d6 when you reach levels 5 (2d6), 11 (3d6), and 17 (4d6)."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "a9f2cfe794b06bcc")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You create an acidic bubble at a point within range, where it explodes in a 5-foot-radius Sphere.",
                    ),
                    ("Area", "5-foot-radius Sphere centered on a point within range"),
                    ("Save", "Dexterity, made by each creature in the Sphere"),
                    ("Failed save", "1d6 Acid damage"),
                    ("Successful save", "No damage"),
                )
            ),
            Option(
                "Cantrip Upgrade",
                (
                    Table(
                        ("Character level", "Damage"),
                        (("1", "1d6"), ("5", "2d6"), ("11", "3d6"), ("17", "4d6")),
                    ),
                ),
            ),
        ]


class BladeWard(ClassSpell):
    rules = SpellRules(
        name="Blade Ward",
        level=0,
        school=School.ABJURATION,
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
        description="Whenever a creature makes an attack roll against you before the spell ends, the attacker subtracts 1d4 from the attack roll.",
        usage_tags=("buff", "control"),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "059a838bb4d8538c")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You ward yourself against attacks."),
            Facts(
                (
                    (
                        "Effect",
                        "Whenever a creature makes an attack roll against you before the spell ends, the attacker subtracts 1d4 from the attack roll",
                    ),
                )
            ),
        ]


class BoomingBlade(ClassSpell):
    rules = SpellRules(
        name="Booming Blade",
        level=0,
        school=School.EVOCATION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF, area=Area(5, AreaShape.RADIUS)),
        components=Components(
            somatic=True, material="a melee weapon worth at least 1 sp"
        ),
        duration=Duration(DurationType.ROUND, 1),
        source="Tasha's Cauldron of Everything",
        description=(
            "You brandish the weapon used in the spell's casting and make a melee attack with it against one creature within 5 feet of you. On a hit, the target suffers the weapon attack's normal effects and then becomes sheathed in booming energy until the start of your next turn. If the target willingly moves 5 feet or more before then, the target takes 1d8 thunder damage, and the spell ends.\n"
            "At Higher Levels. At 5th level, the melee attack deals an extra 1d8 thunder damage to the target on a hit, and the damage the target takes for moving increases to 2d8. Both damage rolls increase by 1d8 at 11th level (2d8 and 3d8) and again at 17th level (3d8 and 4d8)."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "a61fd60b1fc090e5")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You brandish the weapon used in the spell's casting and make a melee attack with it."
            ),
            Facts(
                (
                    ("Target", "One creature within 5 feet of you"),
                    ("Attack", "A melee attack with the weapon"),
                    (
                        "On a hit",
                        "The target suffers the weapon attack's normal effects and becomes sheathed in booming energy until the start of your next turn",
                    ),
                    (
                        "If it moves",
                        "If the target willingly moves 5 feet or more before then, it takes 1d8 Thunder damage, and the spell ends",
                    ),
                )
            ),
            Option(
                "At Higher Levels",
                (
                    Table(
                        (
                            "Character level",
                            "Extra Thunder damage on a hit",
                            "Damage for moving",
                        ),
                        (
                            ("1", "None", "1d8"),
                            ("5", "1d8", "2d8"),
                            ("11", "2d8", "3d8"),
                            ("17", "3d8", "4d8"),
                        ),
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
                conditions=(
                    CombatCondition(
                        "Booming Blade", until=(TurnEdge.START, TurnOf.SOURCE)
                    ),
                ),
                notes=(
                    "One melee attack with the weapon used in the casting, against a creature within 5 feet: give the weapon's own attack bonus and damage.",
                    "Extra Thunder damage on a hit: 1d8 from character level 5, 2d8 from 11, 3d8 from 17.",
                ),
            ),
            CombatEffect(
                name="Booming Blade: moved",
                damage=(
                    CombatDamage(
                        "1d8",
                        DamageType.THUNDER,
                        cantrip=((5, "2d8"), (11, "3d8"), (17, "4d8")),
                    ),
                ),
                spends_use=False,
                notes=(
                    "If the target willingly moves 5 feet or more before the start of your next turn. Then the spell ends: take the badge off.",
                ),
            ),
        ]


class ControlFlames(ClassSpell):
    rules = SpellRules(
        name="Control Flames",
        level=0,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.DRUID, CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(somatic=True),
        duration=Duration(
            DurationType.INSTANTANEOUS, alternative=Duration(DurationType.HOUR, 1)
        ),
        source="Xanathar's Guide to Everything",
        description=(
            "You choose nonmagical flame that you can see within range and that fits within a 5-foot cube. You affect it in one of the following ways:\n"
            "You instantaneously expand the flame 5 feet in one direction, provided that wood or other fuel is present in the new location.\n"
            "You instantaneously extinguish the flames within the cube.\n"
            "You double or halve the area of bright light and dim light cast by the flame, change its color, or both. The change lasts for 1 hour.\n"
            "You cause simple shapes—such as the vague form of a creature, an inanimate object, or a location—to appear within the flames and animate as you like. The shapes last for 1 hour.\n"
            "If you cast this spell multiple times, you can have up to three of its non-instantaneous effects active at a time, and you can dismiss such an effect as an action."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "418b4d57625fc757")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You choose nonmagical flame that you can see within range and that fits within a 5-foot Cube, and affect it in one of these ways."
            ),
            Table(
                ("Effect", "Lasts"),
                (
                    (
                        "Expand the flame 5 feet in one direction, provided that wood or other fuel is present in the new location",
                        "Instantaneous",
                    ),
                    ("Extinguish the flames within the Cube", "Instantaneous"),
                    (
                        "Double or halve the area of Bright Light and Dim Light cast by the flame, change its color, or both",
                        "1 hour",
                    ),
                    (
                        "Simple shapes, such as the vague form of a creature, an inanimate object, or a location, appear within the flames and animate as you like",
                        "1 hour",
                    ),
                ),
            ),
            Facts(
                (
                    (
                        "Active effects",
                        "Up to three of its non-instantaneous effects at a time, from multiple castings",
                    ),
                    ("Dismiss", "As an action, you can dismiss such an effect"),
                )
            ),
        ]


class CreateBonfire(ClassSpell):
    rules = SpellRules(
        name="Create Bonfire",
        level=0,
        school=School.CONJURATION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.DRUID,
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Xanathar's Guide to Everything",
        description=(
            "You create a bonfire on ground that you can see within range. Until the spell ends, the bonfire fills a 5-foot cube. Any creature in the bonfire's space when you cast the spell must succeed on a Dexterity saving throw or take 1d8 fire damage. A creature must also make the saving throw when it enters the bonfire's space for the first time on a turn or ends its turn there.\n"
            "At Higher Levels. The spell's damage increases by 1d8 when you reach 5th level (2d8), 11th level (3d8), and 17th level (4d8)."
        ),
        usage_tags=("damage", "utility"),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "2ee33dfa25d64b8b")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You create a bonfire on ground that you can see within range."),
            Facts(
                (
                    ("Area", "5-foot Cube, until the spell ends"),
                    (
                        "Save",
                        "Dexterity, made by any creature in the bonfire's space when you cast the spell, and by a creature when it enters the space for the first time on a turn or ends its turn there",
                    ),
                    ("Failed save", "1d8 Fire damage"),
                    ("Successful save", "No damage"),
                )
            ),
            Option(
                "At Higher Levels",
                (
                    Table(
                        ("Character level", "Damage"),
                        (("1", "1d8"), ("5", "2d8"), ("11", "3d8"), ("17", "4d8")),
                    ),
                ),
            ),
        ]


class DancingLights(ClassSpell):
    rules = SpellRules(
        name="Dancing Lights",
        level=0,
        school=School.ILLUSION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.BARD,
            CharacterClass.SORCERER,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 120),
        components=Components(
            verbal=True, somatic=True, material="a bit of phosphorus"
        ),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "You create up to four torch-size lights within range, making them appear as torches, lanterns, or glowing orbs that hover for the duration. Alternatively, you combine the four lights into one glowing Medium form that is vaguely humanlike. Whichever form you choose, each light sheds Dim Light in a 10-foot radius.\n"
            "As a Bonus Action, you can move the lights up to 60 feet to a space within range. A light must be within 20 feet of another light created by this spell, and a light vanishes if it exceeds the spell’s range."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "b4fc225118496670")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You create hovering lights that you can move around."),
            Facts(
                (
                    (
                        "Lights",
                        "Up to four torch-size lights within range, appearing as torches, lanterns, or glowing orbs that hover for the duration",
                    ),
                    (
                        "Or",
                        "The four lights combined into one glowing Medium form that is vaguely humanlike",
                    ),
                    (
                        "Light",
                        "Each light sheds Dim Light in a 10-foot radius, whichever form you choose",
                    ),
                    (
                        "Move",
                        "Bonus Action: move the lights up to 60 feet to a space within range",
                    ),
                    (
                        "Spacing",
                        "A light must be within 20 feet of another light created by this spell",
                    ),
                    ("Range limit", "A light vanishes if it exceeds the spell's range"),
                )
            ),
        ]


class Druidcraft(ClassSpell):
    rules = SpellRules(
        name="Druidcraft",
        level=0,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.DRUID,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 30),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "Whispering to the spirits of nature, you create one of the following effects within range.\n"
            "Weather Sensor. You create a Tiny, harmless sensory effect that predicts what the weather will be at your location for the next 24 hours. The effect might manifest as a golden orb for clear skies, a cloud for rain, falling snowflakes for snow, and so on. This effect persists for 1 round.\n"
            "Bloom. You instantly make a flower blossom, a seed pod open, or a leaf bud bloom.\n"
            "Sensory Effect. You create a harmless sensory effect, such as falling leaves, spectral dancing fairies, a gentle breeze, the sound of an animal, or the faint odor of skunk. The effect must fit in a 5-foot Cube.\n"
            "Fire Play. You light or snuff out a candle, a torch, or a campfire."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "ae5abb2563dc54f9")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "Whispering to the spirits of nature, you create one of the following effects within range.",
                    ),
                )
            ),
            Table(
                ("Effect", "What it does"),
                (
                    (
                        "Weather Sensor",
                        "A Tiny, harmless sensory effect predicts the weather at your location for the next 24 hours (a golden orb for clear skies, a cloud for rain, falling snowflakes for snow, and so on); it persists for 1 round",
                    ),
                    (
                        "Bloom",
                        "A flower blossoms, a seed pod opens, or a leaf bud blooms, instantly",
                    ),
                    (
                        "Sensory Effect",
                        "A harmless sensory effect that fits in a 5-foot Cube, such as falling leaves, spectral dancing fairies, a gentle breeze, the sound of an animal, or the faint odor of skunk",
                    ),
                    (
                        "Fire Play",
                        "Light or snuff out a candle, a torch, or a campfire",
                    ),
                ),
            ),
        ]


class Elementalism(ClassSpell):
    rules = SpellRules(
        name="Elementalism",
        level=0,
        school=School.TRANSMUTATION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.DRUID,
            CharacterClass.SORCERER,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 30),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "You exert control over the elements, creating one of the following effects within range.\n"
            "Beckon Air. You create a breeze strong enough to ripple cloth, stir dust, rustle leaves, and close open doors and shutters, all in a 5-foot Cube. Doors and shutters being held open by someone or something aren’t affected.\n"
            "Beckon Earth. You create a thin shroud of dust or sand that covers surfaces in a 5-foot-square area, or you cause a single word to appear in your handwriting in a patch of dirt or sand.\n"
            "Beckon Fire. You create a thin cloud of harmless embers and colored, scented smoke in a 5-foot Cube. You choose the color and scent, and the embers can light candles, torches, or lamps in that area. The smoke’s scent lingers for 1 minute.\n"
            "Beckon Water. You create a spray of cool mist that lightly dampens creatures and objects in a 5-foot Cube. Alternatively, you create 1 cup of clean water either in an open container or on a surface, and the water evaporates in 1 minute.\n"
            "Sculpt Element. You cause dirt, sand, fire, smoke, mist, or water that can fit in a 1-foot Cube to assume a crude shape (such as that of a creature) for 1 hour."
        ),
        usage_tags=("control",),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "b693df7d35930306")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You exert control over the elements, creating one of these effects within range."
            ),
            Table(
                ("Effect", "What it does"),
                (
                    (
                        "Beckon Air",
                        "A breeze in a 5-foot Cube ripples cloth, stirs dust, rustles leaves, and closes open doors and shutters (not ones held open by someone or something)",
                    ),
                    (
                        "Beckon Earth",
                        "A thin shroud of dust or sand covers surfaces in a 5-foot-square area, or a single word appears in your handwriting in a patch of dirt or sand",
                    ),
                    (
                        "Beckon Fire",
                        "A thin cloud of harmless embers and colored, scented smoke (you choose the color and scent) fills a 5-foot Cube; the embers can light candles, torches, or lamps there, and the scent lingers for 1 minute",
                    ),
                    (
                        "Beckon Water",
                        "A spray of cool mist lightly dampens creatures and objects in a 5-foot Cube, or 1 cup of clean water appears in an open container or on a surface and evaporates in 1 minute",
                    ),
                    (
                        "Sculpt Element",
                        "Dirt, sand, fire, smoke, mist, or water that fits in a 1-foot Cube takes a crude shape (such as a creature) for 1 hour",
                    ),
                ),
            ),
        ]

    def combat_effects(
        self, character: CharacterView | None = None
    ) -> list[CombatEffect]:
        return []


class EncodeThoughts(ClassSpell):
    rules = SpellRules(
        name="Encode Thoughts",
        level=0,
        school=School.ENCHANTMENT,
        classes=(),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(somatic=True),
        duration=Duration(DurationType.HOUR, 8),
        source="Guildmaster's Guide to Ravnica",
        description=(
            "You pull a memory, an idea, or a message from your mind and transform it into a tangible string of glowing energy called a thought strand, which persists for the duration or until you cast this spell again. The thought strand appears in an unoccupied space within 5 feet of you as a Tiny, weightless, semisolid object that can be held and carried like a ribbon. It is otherwise stationary.\n"
            "If you cast this spell while concentrating on a spell or an ability that allows you to read or manipulate the thoughts of others (such as detect thoughts or modify memory ), you can transform the thoughts or memories you read, rather than your own, into a thought strand.\n"
            "Casting this spell while holding a thought strand allows you to instantly receive whatever memory, idea, or message the thought strand contains. (Casting detect thoughts on the strand has the same effect.)"
        ),
        usage_tags=("utility",),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "673274125bee6298")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You pull a memory, an idea, or a message from your mind and transform it into a tangible string of glowing energy called a thought strand, which persists for the duration or until you cast this spell again.",
                    ),
                    (
                        "Thought strand",
                        "A Tiny, weightless, semisolid object that can be held and carried like a ribbon; it is otherwise stationary",
                    ),
                    ("Appears", "In an unoccupied space within 5 feet of you"),
                    ("Lasts", "For the duration, or until you cast this spell again"),
                    (
                        "Others' thoughts",
                        "If you cast it while concentrating on a spell or an ability that lets you read or manipulate the thoughts of others (such as Detect Thoughts or Modify Memory), you can make a strand from the thoughts or memories you read instead of your own",
                    ),
                    (
                        "Reading one",
                        "Casting this spell while holding a thought strand lets you instantly receive the memory, idea, or message it contains; casting Detect Thoughts on the strand has the same effect",
                    ),
                )
            )
        ]


class FireBolt(ClassSpell):
    rules = SpellRules(
        name="Fire Bolt",
        level=0,
        school=School.EVOCATION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.SORCERER,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 120),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "You hurl a mote of fire at a creature or an object within range. Make a ranged spell attack against the target. On a hit, the target takes 1d10 Fire damage. A flammable object hit by this spell starts burning if it isn’t being worn or carried.\n"
            "Cantrip Upgrade. The damage increases by 1d10 when you reach levels 5 (2d10), 11 (3d10), and 17 (4d10)."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "f1b21dfa8fb279b7")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You hurl a mote of fire at a creature or an object within range.",
                    ),
                    ("Target", "A creature or an object within range"),
                    ("Attack", "Ranged spell attack"),
                    ("On a hit", "1d10 Fire damage"),
                    (
                        "Objects",
                        "A flammable object hit by this spell starts burning if it isn't being worn or carried",
                    ),
                )
            ),
            Option(
                "Cantrip Upgrade",
                (
                    Table(
                        ("Character level", "Damage"),
                        (("1", "1d10"), ("5", "2d10"), ("11", "3d10"), ("17", "4d10")),
                    ),
                ),
            ),
        ]


class Frostbite(ClassSpell):
    rules = SpellRules(
        name="Frostbite",
        level=0,
        school=School.EVOCATION,
        classes=(
            CharacterClass.DRUID,
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
            CharacterClass.ARTIFICER,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Xanathar's Guide to Everything",
        description=(
            "You cause numbing frost to form on one creature that you can see within range. The target must make a Constitution saving throw. On a failed save, the target takes 1d6 cold damage, and it has disadvantage on the next weapon attack roll it makes before the end of its next turn.\n"
            "At Higher Levels. The spell's damage increases by 1d6 when you reach 5th level (2d6), 11th level (3d6), and 17th level (4d6)."
        ),
        usage_tags=("control", "damage", "utility"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "2e77dd54ed7abef2")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You cause numbing frost to form on one creature that you can see within range.",
                    ),
                    ("Target", "One creature you can see within range"),
                    ("Save", "Constitution"),
                    (
                        "Failed save",
                        "1d6 Cold damage, and Disadvantage on the next weapon attack roll it makes before the end of its next turn",
                    ),
                    ("Successful save", "No effect"),
                )
            ),
            Option(
                "At Higher Levels",
                (
                    Table(
                        ("Character level", "Damage"),
                        (("1", "1d6"), ("5", "2d6"), ("11", "3d6"), ("17", "4d6")),
                    ),
                ),
            ),
        ]


class GreenFlameBlade(ClassSpell):
    rules = SpellRules(
        name="Green-Flame Blade",
        level=0,
        school=School.EVOCATION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF, area=Area(5, AreaShape.RADIUS)),
        components=Components(
            somatic=True, material="a melee weapon worth at least 1 sp"
        ),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Tasha's Cauldron of Everything/Sword Coast Adventurer's Guide",
        description=(
            "You brandish the weapon used in the spell's casting and make a melee attack with it against one creature within 5 feet of you. On a hit, the target suffers the weapon attack's normal effects, and you can cause green fire to leap from the target to a different creature of your choice that you can see within 5 feet of it. The second creature takes fire damage equal to your spellcasting ability modifier.\n"
            "At Higher Levels. At 5th level, the melee attack deals an extra 1d8 fire damage to the target on a hit, and the fire damage to the second creature increases to 1d8 + your spellcasting ability modifier. Both damage rolls increase by 1d8 at 11th level (2d8 and 2d8) and 17th level (3d8 and 3d8)."
        ),
        usage_tags=("damage", "utility"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "884757d409fa65f8")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You brandish the weapon used in the spell's casting and make a melee attack with it, and green fire can leap to a second creature."
            ),
            Facts(
                (
                    ("Target", "One creature within 5 feet of you"),
                    ("Attack", "A melee attack with the weapon"),
                    (
                        "On a hit",
                        "The target suffers the weapon attack's normal effects",
                    ),
                    (
                        "Leap",
                        "On a hit, green fire can leap from the target to a different creature of your choice that you can see within 5 feet of it",
                    ),
                    (
                        "Second creature",
                        "Fire damage equal to your spellcasting ability modifier",
                    ),
                )
            ),
            Option(
                "At Higher Levels",
                (
                    Table(
                        (
                            "Character level",
                            "Extra Fire damage to the target on a hit",
                            "Fire damage to the second creature",
                        ),
                        (
                            ("1", "None", "Spellcasting ability modifier"),
                            ("5", "1d8", "1d8 + spellcasting ability modifier"),
                            ("11", "2d8", "2d8 + spellcasting ability modifier"),
                            ("17", "3d8", "3d8 + spellcasting ability modifier"),
                        ),
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
                notes=(
                    "One melee attack with the weapon used in the casting, against a creature within 5 feet: give the weapon's own attack bonus and damage.",
                    "Extra Fire damage on a hit: 1d8 from character level 5, 2d8 from 11, 3d8 from 17.",
                ),
            ),
            CombatEffect(
                name="Green-Flame Blade: leaping fire",
                damage=(
                    CombatDamage(
                        "0",
                        DamageType.FIRE,
                        cantrip=((5, "1d8"), (11, "2d8"), (17, "3d8")),
                        add_modifier=True,
                    ),
                ),
                spends_use=False,
                notes=(
                    "After a hit: a different creature you can see within 5 feet of the target.",
                ),
            ),
        ]


class Gust(ClassSpell):
    rules = SpellRules(
        name="Gust",
        level=0,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.DRUID, CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 30),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Xanathar's Guide to Everything",
        description=(
            "You seize the air and compel it to create one of the following effects at a point you can see within range:\n"
            "One Medium or smaller creature that you choose must succeed on a Strength saving throw or be pushed up to 5 feet away from you.\n"
            "You create a small blast of air capable of moving one object that is neither held nor carried and that weighs no more than 5 pounds. The object is pushed up to 10 feet away from you. It isn't pushed with enough force to cause damage.\n"
            "You create a harmless sensory affect using air, such as causing leaves to rustle, wind to slam shutters shut, or your clothing to ripple in a breeze."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.CREATURE,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "f211c280b53e2b08")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You seize the air and compel it to create one of the following effects at a point you can see within range.",
                    ),
                    ("Point", "A point you can see within range"),
                )
            ),
            Option(
                "Push a Creature",
                (
                    Facts(
                        (
                            (
                                "Target",
                                "One Medium or smaller creature that you choose",
                            ),
                            ("Save", "Strength"),
                            ("Failed save", "Pushed up to 5 feet away from you"),
                        )
                    ),
                ),
            ),
            Option(
                "Push an Object",
                (
                    Facts(
                        (
                            (
                                "Target",
                                "One object that is neither held nor carried and that weighs no more than 5 pounds",
                            ),
                            (
                                "Effect",
                                "A small blast of air pushes it up to 10 feet away from you, without enough force to cause damage",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Sensory Effect",
                (
                    Facts(
                        (
                            (
                                "Effect",
                                "A harmless sensory effect using air, such as causing leaves to rustle, wind to slam shutters shut, or your clothing to ripple in a breeze",
                            ),
                        )
                    ),
                ),
            ),
        ]


class Infestation(ClassSpell):
    rules = SpellRules(
        name="Infestation",
        level=0,
        school=School.CONJURATION,
        classes=(
            CharacterClass.DRUID,
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 30),
        components=Components(verbal=True, somatic=True, material="a living flea"),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Xanathar's Guide to Everything",
        description=(
            "You cause a cloud of mites, fleas, and other parasites to appear momentarily on one creature you can see within range. The target must succeed on a Constitution saving throw, or it takes 1d6 poison damage and moves 5 feet in a random direction if it can move and its speed is at least 5 feet. Roll a d4 for the direction: 1, north; 2, south; 3, east; or 4, west. This movement doesn't provoke opportunity attacks, and if the direction rolled is blocked, the target doesn't move.\n"
            "At Higher Levels. The spell's damage increases by 1d6 when you reach 5th level (2d6), 11th level (3d6), and 17th level (4d6)."
        ),
        usage_tags=("control", "damage", "utility"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "d302ca2314f9a648")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You cause a cloud of mites, fleas, and other parasites to appear momentarily on one creature you can see within range.",
                    ),
                    ("Target", "One creature you can see within range"),
                    ("Save", "Constitution"),
                    (
                        "Failed save",
                        "1d6 Poison damage, and the target moves 5 feet in a random direction if it can move and its speed is at least 5 feet",
                    ),
                    ("Successful save", "No effect"),
                )
            ),
            Table(
                ("d4", "Direction"),
                (("1", "North"), ("2", "South"), ("3", "East"), ("4", "West")),
            ),
            Facts(
                (
                    (
                        "Movement",
                        "Doesn't provoke opportunity attacks; if the direction rolled is blocked, the target doesn't move",
                    ),
                )
            ),
            Option(
                "At Higher Levels",
                (
                    Table(
                        ("Character level", "Damage"),
                        (("1", "1d6"), ("5", "2d6"), ("11", "3d6"), ("17", "4d6")),
                    ),
                ),
            ),
        ]


class Light(ClassSpell):
    rules = SpellRules(
        name="Light",
        level=0,
        school=School.EVOCATION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.BARD,
            CharacterClass.CLERIC,
            CharacterClass.SORCERER,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.TOUCH),
        components=Components(verbal=True, material="a firefly or phosphorescent moss"),
        duration=Duration(DurationType.HOUR, 1),
        source="Player's Handbook",
        description=(
            "You touch one Large or smaller object that isn’t being worn or carried by someone else. Until the spell ends, the object sheds Bright Light in a 20-foot radius and Dim Light for an additional 20 feet. The light can be colored as you like.\n"
            "Covering the object with something opaque blocks the light. The spell ends if you cast it again."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "5391e9f697226a96")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You make an object you touch shed light."),
            Facts(
                (
                    (
                        "Target",
                        "One Large or smaller object that isn't being worn or carried by someone else",
                    ),
                    (
                        "Light",
                        "Bright Light in a 20-foot radius and Dim Light for an additional 20 feet, colored as you like",
                    ),
                    (
                        "Covering",
                        "Covering the object with something opaque blocks the light",
                    ),
                    ("Ends early", "If you cast this spell again"),
                )
            ),
        ]


class LightningLure(ClassSpell):
    rules = SpellRules(
        name="Lightning Lure",
        level=0,
        school=School.EVOCATION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF, area=Area(15, AreaShape.RADIUS)),
        components=Components(verbal=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Tasha's Cauldron of Everything",
        description=(
            "You create a lash of lightning energy that strikes at one creature of your choice that you can see within 15 feet of you. The target must succeed on a Strength saving throw or be pulled up to 10 feet in a straight line toward you and then take 1d8 lightning damage if it is within 5 feet of you.\n"
            "At Higher Levels. This spell's damage increases by 1d8 when you reach 5th level (2d8), 11th level (3d8), and 17th level (4d8)."
        ),
        usage_tags=("damage", "utility"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "3faa8aad4f28f3e1")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You create a lash of lightning energy that strikes at one creature of your choice that you can see within 15 feet of you.",
                    ),
                    (
                        "Target",
                        "One creature of your choice that you can see within 15 feet of you",
                    ),
                    ("Save", "Strength"),
                    (
                        "Failed save",
                        "Pulled up to 10 feet in a straight line toward you, then takes 1d8 Lightning damage if it is within 5 feet of you",
                    ),
                    ("Successful save", "No effect"),
                )
            ),
            Option(
                "At Higher Levels",
                (
                    Table(
                        ("Character level", "Damage"),
                        (("1", "1d8"), ("5", "2d8"), ("11", "3d8"), ("17", "4d8")),
                    ),
                ),
            ),
        ]


class MageHand(ClassSpell):
    rules = SpellRules(
        name="Mage Hand",
        level=0,
        school=School.CONJURATION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.BARD,
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 30),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 1),
        source="Player's Handbook",
        description=(
            "A spectral, floating hand appears at a point you choose within range. The hand lasts for the duration. The hand vanishes if it is ever more than 30 feet away from you or if you cast this spell again.\n"
            "When you cast the spell, you can use the hand to manipulate an object, open an unlocked door or container, stow or retrieve an item from an open container, or pour the contents out of a vial.\n"
            "As a Magic action on your later turns, you can control the hand thus again. As part of that action, you can move the hand up to 30 feet.\n"
            "The hand can’t attack, activate magic items, or carry more than 10 pounds."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "44a5ba687100f651")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "A spectral, floating hand appears at a point you choose within range.",
                    ),
                    ("Appears", "At a point you choose within range"),
                    (
                        "Uses",
                        "Manipulate an object, open an unlocked door or container, stow or retrieve an item from an open container, or pour the contents out of a vial",
                    ),
                    (
                        "When",
                        "As you cast the spell, then as a Magic action on your later turns",
                    ),
                    ("Movement", "Up to 30 feet, as part of each Magic action"),
                    (
                        "Can't",
                        "Attack, activate magic items, or carry more than 10 pounds",
                    ),
                    (
                        "Vanishes",
                        "If the hand is ever more than 30 feet away from you, or if you cast this spell again",
                    ),
                )
            )
        ]

    def combat_effects(
        self, character: CharacterView | None = None
    ) -> list[CombatEffect]:
        return []


class MagicStone(ClassSpell):
    rules = SpellRules(
        name="Magic Stone",
        level=0,
        school=School.TRANSMUTATION,
        classes=(
            CharacterClass.DRUID,
            CharacterClass.WARLOCK,
            CharacterClass.ARTIFICER,
        ),
        casting_time=CastingTime(CastingTimeType.BONUS_ACTION),
        range=Range(RangeType.TOUCH),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 1),
        source="Xanathar's Guide to Everything/Elemental Evil Player's Companion",
        description=(
            "You touch one to three pebbles and imbue them with magic. You or someone else can make a ranged spell attack with one of the pebbles by throwing it or hurling it with a sling. If thrown, it has a range of 60 feet. If someone else attacks with the pebble, that attacker adds your spellcasting ability modifier, not the attacker's, to the attack roll. On a hit, the target takes bludgeoning damage equal to 1d6 + your spellcasting ability modifier. Hit or miss, the spell then ends on the stone.\n"
            "If you cast this spell again, the spell ends early on any pebbles still affected by it."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "18327c12752fe0b9")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You touch one to three pebbles and imbue them with magic."),
            Facts(
                (
                    (
                        "Who attacks",
                        "You or someone else can make a ranged spell attack with one of the pebbles, by throwing it or hurling it with a sling",
                    ),
                    ("Range", "60 feet if thrown"),
                    (
                        "Attack roll",
                        "The attacker adds your spellcasting ability modifier, not the attacker's",
                    ),
                    (
                        "On a hit",
                        "Bludgeoning damage equal to 1d6 + your spellcasting ability modifier",
                    ),
                    ("After", "Hit or miss, the spell then ends on the stone"),
                    (
                        "Ends early",
                        "If you cast this spell again, it ends on any pebbles still affected by it",
                    ),
                )
            ),
        ]


class Mending(ClassSpell):
    rules = SpellRules(
        name="Mending",
        level=0,
        school=School.TRANSMUTATION,
        classes=(
            CharacterClass.BARD,
            CharacterClass.CLERIC,
            CharacterClass.DRUID,
            CharacterClass.SORCERER,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.MINUTE, 1),
        range=Range(RangeType.TOUCH),
        components=Components(verbal=True, somatic=True, material="two lodestones"),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "This spell repairs a single break or tear in an object you touch, such as a broken chain link, two halves of a broken key, a torn cloak, or a leaking wineskin. As long as the break or tear is no larger than 1 foot in any dimension, you mend it, leaving no trace of the former damage.\n"
            "This spell can physically repair a magic item, but it can’t restore magic to such an object."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "659a1ab32c36e091")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You repair a single break or tear in an object you touch, leaving no trace of the former damage."
            ),
            Facts(
                (
                    (
                        "Size",
                        "The break or tear must be no larger than 1 foot in any dimension",
                    ),
                    (
                        "Examples",
                        "A broken chain link, two halves of a broken key, a torn cloak, or a leaking wineskin",
                    ),
                    (
                        "Magic items",
                        "It can physically repair a magic item, but it can't restore magic to such an object",
                    ),
                )
            ),
        ]


class MindSliver(ClassSpell):
    rules = SpellRules(
        name="Mind Sliver",
        level=0,
        school=School.ENCHANTMENT,
        classes=(
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True),
        duration=Duration(DurationType.ROUND, 1),
        source="Player's Handbook",
        description=(
            "You try to temporarily sliver the mind of one creature you can see within range. The target must succeed on an Intelligence saving throw or take 1d6 Psychic damage and subtract 1d4 from the next saving throw it makes before the end of your next turn.\n"
            "Cantrip Upgrade. The damage increases by 1d6 when you reach levels 5 (2d6), 11 (3d6), and 17 (4d6)."
        ),
        usage_tags=("control", "damage"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "22836d09161ff060")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You try to temporarily sliver the mind of one creature."),
            Facts(
                (
                    ("Target", "One creature you can see within range"),
                    ("Save", "Intelligence"),
                    (
                        "Failed save",
                        "1d6 Psychic damage, and the target subtracts 1d4 from the next saving throw it makes before the end of your next turn",
                    ),
                    ("Successful save", "No effect"),
                )
            ),
            Option(
                "Cantrip Upgrade",
                (
                    Table(
                        ("Character level", "Damage"),
                        (("1", "1d6"), ("5", "2d6"), ("11", "3d6"), ("17", "4d6")),
                    ),
                ),
            ),
        ]


class MoldEarth(ClassSpell):
    rules = SpellRules(
        name="Mold Earth",
        level=0,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.DRUID, CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 30),
        components=Components(somatic=True),
        duration=Duration(
            DurationType.INSTANTANEOUS, alternative=Duration(DurationType.HOUR, 1)
        ),
        source="Xanathar's Guide to Everything",
        description=(
            "You choose a portion of dirt or stone that you can see within range and that fits within a 5-foot cube. You manipulate it in one of the following ways:\n"
            "If you target an area of loose earth, you can instantaneously excavate it, move it along the ground, and deposit it up to 5 feet away. This movement doesn't have enough force to cause damage.\n"
            "You cause shapes, colors, or both to appear on the dirt or stone, spelling out words, creating images, or shaping patterns. The changes last for 1 hour.\n"
            "If the dirt or stone you target is on the ground, you cause it to become difficult terrain. Alternatively, you can cause the ground to become normal terrain if it is already difficult terrain. This change lasts for 1 hour.\n"
            "If you cast this spell multiple times, you can have no more than two of its non-instantaneous effects active at a time, and you can dismiss such an effect as an action."
        ),
        usage_tags=("control", "utility"),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "0c2177e407bf27f1")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You choose a portion of dirt or stone that you can see within range and that fits within a 5-foot Cube, and manipulate it in one of these ways."
            ),
            Table(
                ("Effect", "Lasts"),
                (
                    (
                        "Excavate an area of loose earth, move it along the ground, and deposit it up to 5 feet away; this movement doesn't have enough force to cause damage",
                        "Instantaneous",
                    ),
                    (
                        "Shapes, colors, or both appear on the dirt or stone, spelling out words, creating images, or shaping patterns",
                        "1 hour",
                    ),
                    (
                        "Dirt or stone on the ground becomes Difficult Terrain, or ground that is already Difficult Terrain becomes normal terrain",
                        "1 hour",
                    ),
                ),
            ),
            Facts(
                (
                    (
                        "Active effects",
                        "No more than two of its non-instantaneous effects at a time, from multiple castings",
                    ),
                    ("Dismiss", "As an action, you can dismiss such an effect"),
                )
            ),
        ]


class PoisonSpray(ClassSpell):
    rules = SpellRules(
        name="Poison Spray",
        level=0,
        school=School.NECROMANCY,
        classes=(
            CharacterClass.ARTIFICER,
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
            "You spray toxic mist at a creature within range. Make a ranged spell attack against the target. On a hit, the target takes 1d12 Poison damage.\n"
            "Cantrip Upgrade. The damage increases by 1d12 when you reach levels 5 (2d12), 11 (3d12), and 17 (4d12)."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "028b0ceafc9dc4e4")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Flavor", "You spray toxic mist at a creature within range."),
                    ("Target", "A creature within range"),
                    ("Attack", "Ranged spell attack"),
                    ("On a hit", "1d12 Poison damage"),
                )
            ),
            Option(
                "Cantrip Upgrade",
                (
                    Table(
                        ("Character level", "Damage"),
                        (("1", "1d12"), ("5", "2d12"), ("11", "3d12"), ("17", "4d12")),
                    ),
                ),
            ),
        ]


class Prestidigitation(ClassSpell):
    rules = SpellRules(
        name="Prestidigitation",
        level=0,
        school=School.TRANSMUTATION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.BARD,
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 10),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.HOUR, 1, up_to=True),
        source="Player's Handbook",
        description=(
            "You create a magical effect within range. Choose the effect from the options below. If you cast this spell multiple times, you can have up to three of its non-instantaneous effects active at a time.\n"
            "Sensory Effect. You create an instantaneous, harmless sensory effect, such as a shower of sparks, a puff of wind, faint musical notes, or an odd odor.\n"
            "Fire Play. You instantaneously light or snuff out a candle, a torch, or a small campfire.\n"
            "Clean or Soil. You instantaneously clean or soil an object no larger than 1 cubic foot.\n"
            "Minor Sensation. You chill, warm, or flavor up to 1 cubic foot of nonliving material for 1 hour.\n"
            "Magic Mark. You make a color, a small mark, or a symbol appear on an object or a surface for 1 hour.\n"
            "Minor Creation. You create a nonmagical trinket or an illusory image that can fit in your hand. It lasts until the end of your next turn. A trinket can deal no damage and has no monetary worth."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "6d7a4d191fe5af8c")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You create a magical effect within range, choosing one of the options below."
            ),
            Facts(
                (
                    (
                        "Active effects",
                        "Up to three of its non-instantaneous effects at a time, from repeated castings",
                    ),
                )
            ),
            Table(
                ("Effect", "What it does", "Lasts"),
                (
                    (
                        "Sensory Effect",
                        "A harmless sensory effect, such as a shower of sparks, a puff of wind, faint musical notes, or an odd odor",
                        "Instantaneous",
                    ),
                    (
                        "Fire Play",
                        "Light or snuff out a candle, a torch, or a small campfire",
                        "Instantaneous",
                    ),
                    (
                        "Clean or Soil",
                        "Clean or soil an object no larger than 1 cubic foot",
                        "Instantaneous",
                    ),
                    (
                        "Minor Sensation",
                        "Chill, warm, or flavor up to 1 cubic foot of nonliving material",
                        "1 hour",
                    ),
                    (
                        "Magic Mark",
                        "A color, a small mark, or a symbol appears on an object or a surface",
                        "1 hour",
                    ),
                    (
                        "Minor Creation",
                        "A nonmagical trinket or an illusory image that fits in your hand; a trinket deals no damage and has no monetary worth",
                        "Until the end of your next turn",
                    ),
                ),
            ),
        ]

    def combat_effects(
        self, character: CharacterView | None = None
    ) -> list[CombatEffect]:
        return []


class PrimalSavagery(ClassSpell):
    rules = SpellRules(
        name="Primal Savagery",
        level=0,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.DRUID,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Xanathar's Guide to Everything",
        description=(
            "You channel primal magic to cause your teeth or fingernails to sharpen, ready to deliver a corrosive attack. Make a melee spell attack against one creature within 5 feet of you. On a hit, the target takes 1d10 acid damage. After you make the attack, your teeth or fingernails return to normal.\n"
            "At Higher Levels. The spell's damage increases by 1d10 when you reach 5th level (2d10), 11th level (3d10), and 17th level (4d10)."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "f2230b3f1c090131")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You channel primal magic to cause your teeth or fingernails to sharpen, ready to deliver a corrosive attack.",
                    ),
                    ("Target", "One creature within 5 feet of you"),
                    ("Attack", "Melee spell attack"),
                    ("On a hit", "1d10 Acid damage"),
                    (
                        "After",
                        "Your teeth or fingernails return to normal after you make the attack",
                    ),
                )
            ),
            Option(
                "At Higher Levels",
                (
                    Table(
                        ("Character level", "Damage"),
                        (("1", "1d10"), ("5", "2d10"), ("11", "3d10"), ("17", "4d10")),
                    ),
                ),
            ),
        ]


class RayOfFrost(ClassSpell):
    rules = SpellRules(
        name="Ray of Frost",
        level=0,
        school=School.EVOCATION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.SORCERER,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "A frigid beam of blue-white light streaks toward a creature within range. Make a ranged spell attack against the target. On a hit, it takes 1d8 Cold damage, and its Speed is reduced by 10 feet until the start of your next turn.\n"
            "Cantrip Upgrade. The damage increases by 1d8 when you reach levels 5 (2d8), 11 (3d8), and 17 (4d8)."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "fe8112ada3001e0f")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "A frigid beam of blue-white light streaks toward a creature within range.",
                    ),
                    ("Target", "A creature within range"),
                    ("Attack", "Ranged spell attack"),
                    (
                        "On a hit",
                        "1d8 Cold damage, and its Speed is reduced by 10 feet until the start of your next turn",
                    ),
                )
            ),
            Option(
                "Cantrip Upgrade",
                (
                    Table(
                        ("Character level", "Damage"),
                        (("1", "1d8"), ("5", "2d8"), ("11", "3d8"), ("17", "4d8")),
                    ),
                ),
            ),
        ]


class ShapeWater(ClassSpell):
    rules = SpellRules(
        name="Shape Water",
        level=0,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.DRUID, CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 30),
        components=Components(somatic=True),
        duration=Duration(
            DurationType.INSTANTANEOUS, alternative=Duration(DurationType.HOUR, 1)
        ),
        source="Xanathar's Guide to Everything",
        description=(
            "You choose an area of water that you can see within range and that fits within a 5-foot cube. You manipulate it in one of the following ways:\n"
            "You instantaneously move or otherwise change the flow of the water as you direct, up to 5 feet in any direction. This movement doesn't have enough force to cause damage.\n"
            "You cause the water to form into simple shapes and animate at your direction. This change lasts for 1 hour.\n"
            "You change the water's color or opacity. The water must be changed in the same way throughout. This change lasts for 1 hour.\n"
            "You freeze the water, provided that there are no creatures in it. The water unfreezes in 1 hour.\n"
            "If you cast this spell multiple times, you can have no more than two of its non-instantaneous effects active at a time, and you can dismiss such an effect as an action."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "75b86714fab73a8f")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You choose an area of water that you can see within range and that fits within a 5-foot Cube, and manipulate it in one of these ways."
            ),
            Table(
                ("Effect", "Lasts"),
                (
                    (
                        "Move or otherwise change the flow of the water as you direct, up to 5 feet in any direction; this movement doesn't have enough force to cause damage",
                        "Instantaneous",
                    ),
                    (
                        "The water forms into simple shapes and animates at your direction",
                        "1 hour",
                    ),
                    (
                        "Change the water's color or opacity; it must be changed in the same way throughout",
                        "1 hour",
                    ),
                    (
                        "Freeze the water, provided that there are no creatures in it",
                        "Unfreezes in 1 hour",
                    ),
                ),
            ),
            Facts(
                (
                    (
                        "Active effects",
                        "No more than two of its non-instantaneous effects at a time, from multiple castings",
                    ),
                    ("Dismiss", "As an action, you can dismiss such an effect"),
                )
            ),
        ]


class Shillelagh(ClassSpell):
    rules = SpellRules(
        name="Shillelagh",
        level=0,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.DRUID,),
        casting_time=CastingTime(CastingTimeType.BONUS_ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True, material="mistletoe"),
        duration=Duration(DurationType.MINUTE, 1),
        source="Player's Handbook",
        description=(
            "A Club or Quarterstaff you are holding is imbued with nature’s power. For the duration, you can use your spellcasting ability instead of Strength for the attack and damage rolls of melee attacks using that weapon, and the weapon’s damage die becomes a d8. If the attack deals damage, it can be Force damage or the weapon’s normal damage type (your choice).\n"
            "The spell ends early if you cast it again or if you let go of the weapon.\n"
            "Cantrip Upgrade. The damage die changes when you reach levels 5 (d10), 11 (d12), and 17 (2d6)."
        ),
        usage_tags=("buff",),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "0ec89a21aa5f5472")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "A Club or Quarterstaff you are holding is imbued with nature's power.",
                    ),
                    ("Weapon", "A Club or Quarterstaff you are holding"),
                    (
                        "Attack and damage",
                        "Use your spellcasting ability instead of Strength for the attack and damage rolls of melee attacks using that weapon",
                    ),
                    (
                        "Damage die",
                        "The weapon's damage die becomes a d8 (see Cantrip Upgrade)",
                    ),
                    (
                        "Damage type",
                        "If the attack deals damage, it can be Force damage or the weapon's normal damage type (your choice)",
                    ),
                    (
                        "Ends early",
                        "If you cast this spell again or let go of the weapon",
                    ),
                )
            ),
            Option(
                "Cantrip Upgrade",
                (
                    Table(
                        ("Character level", "Damage die"),
                        (("1", "d8"), ("5", "d10"), ("11", "d12"), ("17", "2d6")),
                    ),
                ),
            ),
        ]


class ShockingGrasp(ClassSpell):
    rules = SpellRules(
        name="Shocking Grasp",
        level=0,
        school=School.EVOCATION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.SORCERER,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.TOUCH),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "Lightning springs from you to a creature that you try to touch. Make a melee spell attack against the target. On a hit, the target takes 1d8 Lightning damage, and it can’t make Opportunity Attacks until the start of its next turn.\n"
            "Cantrip Upgrade. The damage increases by 1d8 when you reach levels 5 (2d8), 11 (3d8), and 17 (4d8)."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "1d8aa826ca20e16a")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "Lightning springs from you to a creature that you try to touch.",
                    ),
                    ("Target", "A creature you try to touch"),
                    ("Attack", "Melee spell attack"),
                    (
                        "On a hit",
                        "1d8 Lightning damage, and the target can't make Opportunity Attacks until the start of its next turn",
                    ),
                )
            ),
            Option(
                "Cantrip Upgrade",
                (
                    Table(
                        ("Character level", "Damage"),
                        (("1", "1d8"), ("5", "2d8"), ("11", "3d8"), ("17", "4d8")),
                    ),
                ),
            ),
        ]


class SorcerousBurst(ClassSpell):
    rules = SpellRules(
        name="Sorcerous Burst",
        level=0,
        school=School.EVOCATION,
        classes=(CharacterClass.SORCERER,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 120),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "You cast sorcerous energy at one creature or object within range. Make a ranged spell attack against the target. On a hit, the target takes 1d8 damage of a type you choose: Acid, Cold, Fire, Lightning, Poison, Psychic, or Thunder.\n"
            "If you roll an 8 on a d8 for this spell, you can roll another d8, and add it to the damage. When you cast this spell, the maximum number of these d8s you can add to the spell’s damage equals your spellcasting ability modifier.\n"
            "Cantrip Upgrade. The damage increases by 1d8 when you reach levels 5 (2d8), 11 (3d8), and 17 (4d8)."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "62d82bc9a5d7a1a4")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You cast sorcerous energy at one creature or object, and its damage can keep exploding."
            ),
            Facts(
                (
                    ("Target", "One creature or object within range"),
                    ("Attack", "Ranged spell attack"),
                    (
                        "On a hit",
                        "1d8 damage of a type you choose: Acid, Cold, Fire, Lightning, Poison, Psychic, or Thunder",
                    ),
                    (
                        "Exploding 8s",
                        "If you roll an 8 on a d8 for this spell, you can roll another d8 and add it to the damage",
                    ),
                    (
                        "Extra d8s",
                        "The maximum number of these d8s you can add to the spell's damage equals your spellcasting ability modifier",
                    ),
                )
            ),
            Option(
                "Cantrip Upgrade",
                (
                    Table(
                        ("Character level", "Damage"),
                        (("1", "1d8"), ("5", "2d8"), ("11", "3d8"), ("17", "4d8")),
                    ),
                ),
            ),
        ]


class SwordBurst(ClassSpell):
    rules = SpellRules(
        name="Sword Burst",
        level=0,
        school=School.CONJURATION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF, area=Area(5, AreaShape.RADIUS)),
        components=Components(verbal=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Tasha's Cauldron of Everything",
        description=(
            "You create a momentary circle of spectral blades that sweep around you. All other creatures within 5 feet of you must succeed on a Dexterity saving throw or take 1d6 force damage.\n"
            "At Higher Levels. This spell's damage increases by 1d6 when you reach 5th level (2d6), 11th level (3d6), and 17th level (4d6)."
        ),
        usage_tags=("damage", "utility"),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "e727e4cb84c90deb")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You create a momentary circle of spectral blades that sweep around you.",
                    ),
                    ("Targets", "All other creatures within 5 feet of you"),
                    ("Save", "Dexterity"),
                    ("Failed save", "1d6 Force damage"),
                    ("Successful save", "No damage"),
                )
            ),
            Option(
                "At Higher Levels",
                (
                    Table(
                        ("Character level", "Damage"),
                        (("1", "1d6"), ("5", "2d6"), ("11", "3d6"), ("17", "4d6")),
                    ),
                ),
            ),
        ]


class ThornWhip(ClassSpell):
    rules = SpellRules(
        name="Thorn Whip",
        level=0,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.ARTIFICER, CharacterClass.DRUID),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 30),
        components=Components(
            verbal=True, somatic=True, material="the stem of a thorny plant"
        ),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "You create a vine-like whip covered in thorns that lashes out at your command toward a creature in range. Make a melee spell attack against the target. On a hit, the target takes 1d6 Piercing damage, and if it is Large or smaller, you can pull it up to 10 feet closer to you.\n"
            "Cantrip Upgrade. The damage increases by 1d6 when you reach levels 5 (2d6), 11 (3d6), and 17 (4d6)."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "8615c2ae88b3db62")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You create a vine-like whip covered in thorns that lashes out at your command toward a creature in range.",
                    ),
                    ("Target", "A creature within range"),
                    ("Attack", "Melee spell attack"),
                    ("On a hit", "1d6 Piercing damage"),
                    (
                        "Pull",
                        "If the target is Large or smaller, you can pull it up to 10 feet closer to you",
                    ),
                )
            ),
            Option(
                "Cantrip Upgrade",
                (
                    Table(
                        ("Character level", "Damage"),
                        (("1", "1d6"), ("5", "2d6"), ("11", "3d6"), ("17", "4d6")),
                    ),
                ),
            ),
        ]


class Thunderclap(ClassSpell):
    rules = SpellRules(
        name="Thunderclap",
        level=0,
        school=School.EVOCATION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.BARD,
            CharacterClass.DRUID,
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "Each creature in a 5-foot Emanation originating from you must succeed on a Constitution saving throw or take 1d6 Thunder damage. The spell’s thunderous sound can be heard up to 100 feet away.\n"
            "Cantrip Upgrade. The damage increases by 1d6 when you reach levels 5 (2d6), 11 (3d6), and 17 (4d6)."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "0b27c78bab05abeb")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Area", "5-foot Emanation originating from you"),
                    ("Save", "Constitution, made by each creature in the area"),
                    ("Failed save", "1d6 Thunder damage"),
                    ("Successful save", "No damage"),
                    ("Sound", "Can be heard up to 100 feet away"),
                )
            ),
            Option(
                "Cantrip Upgrade",
                (
                    Table(
                        ("Character level", "Damage"),
                        (("1", "1d6"), ("5", "2d6"), ("11", "3d6"), ("17", "4d6")),
                    ),
                ),
            ),
        ]


class WordOfRadiance(ClassSpell):
    rules = SpellRules(
        name="Word of Radiance",
        level=0,
        school=School.EVOCATION,
        classes=(CharacterClass.CLERIC,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, material="a sunburst token"),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "Burning radiance erupts from you in a 5-foot Emanation. Each creature of your choice that you can see in it must succeed on a Constitution saving throw or take 1d6 Radiant damage.\n"
            "Cantrip Upgrade. The damage increases by 1d6 when you reach levels 5 (2d6), 11 (3d6), and 17 (4d6)."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "402a90476c41d0a7")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "Burning radiance erupts from you in a 5-foot Emanation.",
                    ),
                    ("Area", "5-foot Emanation originating from you"),
                    (
                        "Targets",
                        "Each creature of your choice that you can see in the area",
                    ),
                    ("Save", "Constitution"),
                    ("Failed save", "1d6 Radiant damage"),
                    ("Successful save", "No damage"),
                )
            ),
            Option(
                "Cantrip Upgrade",
                (
                    Table(
                        ("Character level", "Damage"),
                        (("1", "1d6"), ("5", "2d6"), ("11", "3d6"), ("17", "4d6")),
                    ),
                ),
            ),
        ]


class SappingSting(ClassSpell):
    rules = SpellRules(
        name="Sapping Sting",
        level=0,
        school=School.NECROMANCY,
        classes=(CharacterClass.WIZARD,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 30),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Explorer's Guide to Wildemount",
        description=(
            "You sap the vitality of one creature you can see in range. The target must succeed on a Constitution saving throw or take 1d4 necrotic damage and fall prone.\n"
            "At Higher Levels. This spell's damage increases by 1d4 when you reach 5th level (2d4), 11th level (3d4), and 17th level (4d4)."
        ),
        usage_tags=("control", "damage", "utility"),
        target=FeatureTarget.ENEMY,
        school_note="Dunamancy",
    )
    converted_from = RecordStamp("spells_dnd5e.json", "2d79425c2e180943")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You sap the vitality of one creature you can see in range.",
                    ),
                    ("Target", "One creature you can see within range"),
                    ("Save", "Constitution"),
                    ("Failed save", "1d4 Necrotic damage, and the target falls Prone"),
                    ("Successful save", "No effect"),
                )
            ),
            Option(
                "At Higher Levels",
                (
                    Table(
                        ("Character level", "Damage"),
                        (("1", "1d4"), ("5", "2d4"), ("11", "3d4"), ("17", "4d4")),
                    ),
                ),
            ),
        ]


SPELLS = [
    AcidSplash,
    BladeWard,
    BoomingBlade,
    ChillTouch,
    ControlFlames,
    CreateBonfire,
    DancingLights,
    Druidcraft,
    EldritchBlast,
    Elementalism,
    EncodeThoughts,
    FireBolt,
    Friends,
    Frostbite,
    GreenFlameBlade,
    Guidance,
    Gust,
    Infestation,
    Light,
    LightningLure,
    MageHand,
    MagicStone,
    Mending,
    Message,
    MindSliver,
    MinorIllusion,
    MoldEarth,
    PoisonSpray,
    Prestidigitation,
    PrimalSavagery,
    ProduceFlame,
    RayOfFrost,
    Resistance,
    SacredFlame,
    SappingSting,
    ShapeWater,
    Shillelagh,
    ShockingGrasp,
    SorcerousBurst,
    SpareTheDying,
    StarryWisp,
    SwordBurst,
    Thaumaturgy,
    ThornWhip,
    Thunderclap,
    TollTheDead,
    TrueStrike,
    ViciousMockery,
    WordOfRadiance,
]
