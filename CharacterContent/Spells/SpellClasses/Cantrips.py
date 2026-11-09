"""Cantrips as classes (CharacterContent/Spells/SpellFactory/ClassSpell.py),
which SpellFactory uses instead of their JSON records. Written by
CharacterContent/Spells/SpellClassConverter.py; edit them by hand from
then on: each class is its spell's one source."""

from CharacterContent.Spells.SpellFactory.ClassSpell import ClassSpell, SpellRules
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
    CombatInstances,
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
                roll="attack",
                damage=(
                    CombatDamage(
                        "1d10",
                        DamageType.NECROTIC,
                        cantrip=((5, "2d10"), (11, "3d10"), (17, "4d10")),
                    ),
                ),
                conditions=(CombatCondition("Chill Touch", until=("end", "source")),),
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
                roll="attack",
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
                roll="save",
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
                roll="attack",
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
                roll="save",
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
                roll="attack",
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
                roll="save",
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
                roll="save",
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
                roll="attack",
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
                roll="save",
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


SPELLS = [
    ChillTouch,
    EldritchBlast,
    Friends,
    Guidance,
    Message,
    MinorIllusion,
    ProduceFlame,
    Resistance,
    SacredFlame,
    SpareTheDying,
    StarryWisp,
    Thaumaturgy,
    TollTheDead,
    TrueStrike,
    ViciousMockery,
]
