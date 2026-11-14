"""Level 2 spells as classes (CharacterContent/Spells/SpellFactory/ClassSpell.py),
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
    CombatTargets,
    EffectRoll,
)
from Model.Content.CombatModifiers import (
    ArmorClassMinimum,
    D20Mode,
    D20Test,
    DamageImmunity,
    HitPointMaximum,
    Note,
    RollMode,
    Size,
)
from Model.Content.Feature import FeatureTarget
from Model.Content.FeatureText import Block, Facts, Option, Paragraph, Table
from Model.View import CharacterView


class HoldPerson(ClassSpell):
    rules = SpellRules(
        name="Hold Person",
        level=2,
        school=School.ENCHANTMENT,
        classes=(
            CharacterClass.BARD,
            CharacterClass.CLERIC,
            CharacterClass.DRUID,
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(
            verbal=True, somatic=True, material="a straight piece of iron"
        ),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "Choose a Humanoid that you can see within range. The target must succeed on a Wisdom saving throw or have the Paralyzed condition for the duration. At the end of each of its turns, the target repeats the save, ending the spell on itself on a success.\n"
            "Using a Higher-Level Spell Slot. You can target one additional Humanoid for each spell slot level above 2."
        ),
        usage_tags=("control",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "2ddd49f1a2af4f63")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You paralyze a Humanoid you can see."),
            Facts(
                (
                    ("Target", "A Humanoid you can see within range"),
                    ("Save", "Wisdom"),
                    (
                        "Failed save",
                        "The target has the Paralyzed condition for the duration",
                    ),
                    (
                        "Repeat save",
                        "At the end of each of its turns; on a success, the spell ends on the target",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (
                    Facts(
                        (("Targets", "+1 Humanoid for each spell slot level above 2"),)
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
                conditions=(CombatCondition(Condition.PARALYZED),),
                targets=CombatTargets(1, upcast=1),
                notes=("Humanoids only.",),
            )
        ]


class Invisibility(ClassSpell):
    rules = SpellRules(
        name="Invisibility",
        level=2,
        school=School.ILLUSION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.BARD,
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.TOUCH),
        components=Components(
            verbal=True, somatic=True, material="an eyelash in gum arabic"
        ),
        duration=Duration(DurationType.HOUR, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "A creature you touch has the Invisible condition until the spell ends. The spell ends early immediately after the target makes an attack roll, deals damage, or casts a spell.\n"
            "Using a Higher-Level Spell Slot. You can target one additional creature for each spell slot level above 2."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "f21388fe94bcf6a4")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("A creature you touch turns invisible."),
            Facts(
                (
                    ("Target", "A creature you touch"),
                    ("Effect", "The Invisible condition until the spell ends"),
                    (
                        "Ends early",
                        "Immediately after the target makes an attack roll, deals damage, or casts a spell",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (
                    Facts(
                        (("Targets", "+1 creature for each spell slot level above 2"),)
                    ),
                ),
            ),
        ]

    def combat_effects(
        self, character: CharacterView | None = None
    ) -> list[CombatEffect]:
        return [
            CombatEffect(
                conditions=(CombatCondition(Condition.INVISIBLE),),
                targets=CombatTargets(1, upcast=1),
                notes=(
                    "It ends right after the target makes an attack roll, deals damage or casts a spell.",
                ),
            )
        ]


class Moonbeam(ClassSpell):
    rules = SpellRules(
        name="Moonbeam",
        level=2,
        school=School.EVOCATION,
        classes=(CharacterClass.DRUID,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 120),
        components=Components(verbal=True, somatic=True, material="a moonseed leaf"),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "A silvery beam of pale light shines down in a 5-foot-radius, 40-foot-high Cylinder centered on a point within range. Until the spell ends, Dim Light fills the Cylinder, and you can take a Magic action on later turns to move the Cylinder up to 60 feet.\n"
            "When the Cylinder appears, each creature in it makes a Constitution saving throw. On a failed save, a creature takes 2d10 Radiant damage, and if the creature is shape-shifted (as a result of the Polymorph spell, for example), it reverts to its true form and can’t shape-shift until it leaves the Cylinder. On a successful save, a creature takes half as much damage only. A creature also makes this save when the spell’s area moves into its space and when it enters the spell’s area or ends its turn there. A creature makes this save only once per turn.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 1d10 for each spell slot level above 2."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "bf4a8c6b9fcf2844")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "A silvery beam of pale light shines down in a 5-foot-radius, 40-foot-high Cylinder centered on a point within range.",
                    ),
                    (
                        "Area",
                        "5-foot-radius, 40-foot-high Cylinder centered on a point within range, filled with Dim Light",
                    ),
                    (
                        "Move",
                        "You can take a Magic action on later turns to move the Cylinder up to 60 feet",
                    ),
                    (
                        "Save",
                        "Constitution, when the Cylinder appears, when it moves into a creature's space, and when a creature enters it or ends its turn there; a creature makes this save only once per turn",
                    ),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (
                    (
                        "2d10 Radiant damage; a shape-shifted creature (from Polymorph, for example) reverts to its true form and can't shape-shift until it leaves the Cylinder",
                        "Half as much damage only",
                    ),
                ),
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Damage", "+1d10 for each spell slot level above 2"),)),),
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
                damage=(CombatDamage("2d10", DamageType.RADIANT, upcast="1d10"),),
                notes=(
                    "A shape-shifted creature that fails reverts to its true form. A creature also saves when the Cylinder moves into its space, and when it enters or ends its turn there (once per turn). A Magic action moves the Cylinder up to 60 feet.",
                ),
            )
        ]


class ScorchingRay(ClassSpell):
    rules = SpellRules(
        name="Scorching Ray",
        level=2,
        school=School.EVOCATION,
        classes=(CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 120),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "You hurl three fiery rays. You can hurl them at one target within range or at several. Make a ranged spell attack for each ray. On a hit, the target takes 2d6 Fire damage.\n"
            "Using a Higher-Level Spell Slot. You create one additional ray for each spell slot level above 2."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "40f09486be8aebd8")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Flavor", "You hurl three fiery rays."),
                    ("Rays", "Three"),
                    ("Targets", "One target within range, or several"),
                    ("Attack", "A ranged spell attack for each ray"),
                    ("On a hit", "2d6 Fire damage"),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Rays", "+1 ray for each spell slot level above 2"),)),),
            ),
        ]

    def combat_effects(
        self, character: CharacterView | None = None
    ) -> list[CombatEffect]:
        return [
            CombatEffect(
                roll=EffectRoll.ATTACK,
                damage=(CombatDamage("2d6", DamageType.FIRE),),
                instances=CombatInstances(3, upcast=1, noun="ray"),
                notes=(
                    "The rays can go at one target or several: lower Times and apply again for the others.",
                ),
            )
        ]


class Shatter(ClassSpell):
    rules = SpellRules(
        name="Shatter",
        level=2,
        school=School.EVOCATION,
        classes=(CharacterClass.BARD, CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True, somatic=True, material="a chip of mica"),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "A loud noise erupts from a point of your choice within range. Each creature in a 10-foot-radius Sphere centered there makes a Constitution saving throw, taking 3d8 Thunder damage on a failed save or half as much damage on a successful one. A Construct has Disadvantage on the save.\n"
            "A nonmagical object that isn’t being worn or carried also takes the damage if it’s in the spell’s area.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 1d8 for each spell slot level above 2."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "16af3f49d3981c24")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "A loud noise erupts from a point of your choice within range.",
                    ),
                    (
                        "Area",
                        "10-foot-radius Sphere centered on a point of your choice within range",
                    ),
                    (
                        "Save",
                        "Constitution, made by each creature in the area; a Construct has Disadvantage",
                    ),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (("3d8 Thunder damage", "Half as much damage"),),
            ),
            Facts(
                (
                    (
                        "Objects",
                        "A nonmagical object in the area that isn't being worn or carried also takes the damage",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Damage", "+1d8 for each spell slot level above 2"),)),),
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
                damage=(CombatDamage("3d8", DamageType.THUNDER, upcast="1d8"),),
                notes=("A Construct has Disadvantage on the save.",),
            )
        ]


class SpikeGrowth(ClassSpell):
    rules = SpellRules(
        name="Spike Growth",
        level=2,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.DRUID, CharacterClass.RANGER),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 150),
        components=Components(verbal=True, somatic=True, material="seven thorns"),
        duration=Duration(DurationType.MINUTE, 10, concentration=True),
        source="Player's Handbook",
        description=(
            "The ground in a 20-foot-radius Sphere centered on a point within range sprouts hard spikes and thorns. The area becomes Difficult Terrain for the duration. When a creature moves into or within the area, it takes 2d4 Piercing damage for every 5 feet it travels.\n"
            "The transformation of the ground is camouflaged to look natural. Any creature that can’t see the area when the spell is cast must take a Search action and succeed on a Wisdom (Perception or Survival) check against your spell save DC to recognize the terrain as hazardous before entering it."
        ),
        usage_tags=("control", "damage"),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "9299701c05a229b5")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "The ground in a 20-foot-radius Sphere centered on a point within range sprouts hard spikes and thorns.",
                    ),
                    ("Area", "20-foot-radius Sphere centered on a point within range"),
                    ("Terrain", "Difficult Terrain for the duration"),
                    (
                        "Damage",
                        "When a creature moves into or within the area, it takes 2d4 Piercing damage for every 5 feet it travels",
                    ),
                    (
                        "Camouflage",
                        "The transformation of the ground is camouflaged to look natural",
                    ),
                    (
                        "Spotting it",
                        "Any creature that can't see the area when the spell is cast must take a Search action and succeed on a Wisdom (Perception or Survival) check against your spell save DC to recognize the terrain as hazardous before entering it",
                    ),
                )
            )
        ]

    def combat_effects(
        self, character: CharacterView | None = None
    ) -> list[CombatEffect]:
        return [
            CombatEffect(
                notes=(
                    "The 20-foot-radius area is Difficult Terrain. A creature takes 2d4 Piercing damage for every 5 feet it moves into or within it.",
                    "A creature that can't see the area when it's cast needs a Search action and a Wisdom (Perception or Survival) check against your spell save DC to spot the danger.",
                )
            )
        ]


class SpiritualWeapon(ClassSpell):
    rules = SpellRules(
        name="Spiritual Weapon",
        level=2,
        school=School.EVOCATION,
        classes=(CharacterClass.CLERIC,),
        casting_time=CastingTime(CastingTimeType.BONUS_ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "You create a floating, spectral force that resembles a weapon of your choice and lasts for the duration. The force appears within range in a space of your choice, and you can immediately make one melee spell attack against one creature within 5 feet of the force. On a hit, the target takes Force damage equal to 1d8 plus your spellcasting ability modifier.\n"
            "As a Bonus Action on your later turns, you can move the force up to 20 feet and repeat the attack against a creature within 5 feet of it.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 1d8 for every slot level above 2."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "341a82403032b1ec")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You create a floating, spectral force that resembles a weapon of your choice and lasts for the duration.",
                    ),
                    ("Appears", "In a space of your choice within range"),
                    (
                        "Attack",
                        "When you cast the spell, you can immediately make one melee spell attack against one creature within 5 feet of the force",
                    ),
                    (
                        "On a hit",
                        "1d8 + your spellcasting ability modifier Force damage",
                    ),
                    (
                        "Later turns",
                        "As a Bonus Action on your later turns, you can move the force up to 20 feet and repeat the attack against a creature within 5 feet of it",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Damage", "+1d8 for each spell slot level above 2"),)),),
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
                        "1d8", DamageType.FORCE, upcast="1d8", add_modifier=True
                    ),
                ),
                notes=(
                    "On later turns, a Bonus Action moves the force up to 20 feet and repeats the attack.",
                ),
            )
        ]


class Suggestion(ClassSpell):
    rules = SpellRules(
        name="Suggestion",
        level=2,
        school=School.ENCHANTMENT,
        classes=(
            CharacterClass.BARD,
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 30),
        components=Components(verbal=True, material="a drop of honey"),
        duration=Duration(DurationType.HOUR, 8, concentration=True),
        source="Player's Handbook",
        description=(
            "You suggest a course of activity—described in no more than 25 words—to one creature you can see within range that can hear and understand you. The suggestion must sound achievable and not involve anything that would obviously deal damage to the target or its allies. For example, you could say, “Fetch the key to the cult’s treasure vault, and give the key to me.” Or you could say, “Stop fighting, leave this library peacefully, and don’t return.”\n"
            "The target must succeed on a Wisdom saving throw or have the Charmed condition for the duration or until you or your allies deal damage to the target. The Charmed target pursues the suggestion to the best of its ability. The suggested activity can continue for the entire duration, but if the suggested activity can be completed in a shorter time, the spell ends for the target upon completing it."
        ),
        usage_tags=("control",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "dcc44381b017c7b3")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You suggest a course of activity to a creature, which it pursues while Charmed."
            ),
            Facts(
                (
                    (
                        "Target",
                        "One creature you can see within range that can hear and understand you",
                    ),
                    (
                        "Suggestion",
                        "No more than 25 words; it must sound achievable and not involve anything that would obviously deal damage to the target or its allies",
                    ),
                    ("Save", "Wisdom"),
                    (
                        "Failed save",
                        "Charmed for the duration, or until you or your allies deal damage to it; it pursues the suggestion to the best of its ability",
                    ),
                    (
                        "Done early",
                        "If the activity can be completed sooner, the spell ends for the target when it completes it",
                    ),
                    (
                        "Examples",
                        '"Fetch the key to the cult\'s treasure vault, and give the key to me." "Stop fighting, leave this library peacefully, and don\'t return."',
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
                conditions=(CombatCondition(Condition.CHARMED),),
                notes=(
                    "The target must be able to hear and understand you. It ends early if you or your allies damage it, or when the suggested activity is done.",
                ),
            )
        ]


class AganazzarsScorcher(ClassSpell):
    rules = SpellRules(
        name="Aganazzar's Scorcher",
        level=2,
        school=School.EVOCATION,
        classes=(CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 30),
        components=Components(
            verbal=True, somatic=True, material="a red dragon’s scale"
        ),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Xanathar's Guide to Everything",
        description=(
            "A line of roaring flame 30 feet long and 5 feet wide emanates from you in a direction you choose. Each creature in the line must make a Dexterity saving throw. A creature takes 3d8 fire damage on a failed save, or half as much damage on a successful one.\n"
            "At Higher Levels. When you cast this spell using a spell slot of 3rd level or higher, the damage increases by 1d8 for each slot level above 2nd."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "c35d0d674101dcc6")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "A line of roaring flame 30 feet long and 5 feet wide emanates from you in a direction you choose.",
                    ),
                    (
                        "Area",
                        "A line 30 feet long and 5 feet wide, in a direction you choose",
                    ),
                    ("Save", "Dexterity, made by each creature in the line"),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (("3d8 Fire damage", "Half as much damage"),),
            ),
            Option(
                "At Higher Levels",
                (Facts((("Damage", "+1d8 for each slot level above 2nd"),)),),
            ),
        ]


class Aid(ClassSpell):
    rules = SpellRules(
        name="Aid",
        level=2,
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
        range=Range(RangeType.FOOT, 30),
        components=Components(
            verbal=True, somatic=True, material="a strip of white cloth"
        ),
        duration=Duration(DurationType.HOUR, 8),
        source="Player's Handbook",
        description=(
            "Choose up to three creatures within range. Each target’s Hit Point maximum and current Hit Points increase by 5 for the duration.\n"
            "Using a Higher-Level Spell Slot. Each target’s Hit Points increase by 5 for each spell slot level above 2."
        ),
        usage_tags=("heal",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "60bd730010139a96")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Targets", "Up to three creatures within range"),
                    (
                        "Effect",
                        "Each target's Hit Point maximum and current Hit Points increase by 5 for the duration",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Hit Points", "+5 for each spell slot level above 2"),)),),
            ),
        ]

    def combat_effects(
        self, character: CharacterView | None = None
    ) -> list[CombatEffect]:
        return [
            CombatEffect(
                conditions=(
                    CombatCondition(
                        "Aid", modifiers=(HitPointMaximum("5", upcast="5"),)
                    ),
                ),
                targets=CombatTargets(3),
            ),
        ]


class AirBubble(ClassSpell):
    rules = SpellRules(
        name="Air Bubble",
        level=2,
        school=School.CONJURATION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.DRUID,
            CharacterClass.RANGER,
            CharacterClass.SORCERER,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(somatic=True),
        duration=Duration(DurationType.HOUR, 24),
        source="Spelljammer: Adventures in Space - Astral Adventurer's Guide",
        description=(
            "You create a spectral globe around the head of a willing creature you can see within range. The globe is filled with fresh air that lasts until the spell ends. If the creature has more than one head, the globe of air appears around only one of its heads (which is all the creature needs to avoid suffocation, assuming that all its heads share the same respiratory system).\n"
            "At Higher Levels. When you cast this spell using a spell slot of 3rd level or higher, you can create two additional globes of fresh air for each slot level above 2nd."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "2b335d8e5043b6e2")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You create a spectral globe around the head of a willing creature you can see within range.",
                    ),
                    ("Target", "A willing creature you can see within range"),
                    (
                        "Effect",
                        "The globe is filled with fresh air that lasts until the spell ends",
                    ),
                    (
                        "Several heads",
                        "The globe appears around only one of its heads, which is all the creature needs to avoid suffocation, assuming that all its heads share the same respiratory system",
                    ),
                )
            ),
            Option(
                "At Higher Levels",
                (Facts((("Globes", "+2 globes for each slot level above 2nd"),)),),
            ),
        ]


class AlterSelf(ClassSpell):
    rules = SpellRules(
        name="Alter Self",
        level=2,
        school=School.TRANSMUTATION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.SORCERER,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.HOUR, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "You alter your physical form. Choose one of the following options. Its effects last for the duration, during which you can take a Magic action to replace the option you chose with a different one.\n"
            "Aquatic Adaptation. You sprout gills and grow webs between your fingers. You can breathe underwater and gain a Swim Speed equal to your Speed.\n"
            "Change Appearance. You alter your appearance. You decide what you look like, including your height, weight, facial features, sound of your voice, hair length, coloration, and other distinguishing characteristics. You can make yourself appear as a member of another species, though none of your statistics change. You can’t appear as a creature of a different size, and your basic shape stays the same; if you’re bipedal, you can’t use this spell to become quadrupedal, for instance. For the duration, you can take a Magic action to change your appearance in this way again.\n"
            "Natural Weapons. You grow claws (Slashing), fangs (Piercing), horns (Piercing), or hooves (Bludgeoning). When you use your Unarmed Strike to deal damage with that new growth, it deals 1d6 damage of the type in parentheses instead of dealing the normal damage for your Unarmed Strike, and you use your spellcasting ability modifier for the attack and damage rolls rather than using Strength."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "4c271adb779a5917")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You alter your physical form, choosing one option below. For the duration, you can take a Magic action to swap it for a different option."
            ),
            Option(
                "Aquatic Adaptation",
                (
                    Facts(
                        (
                            (
                                "Effect",
                                "You sprout gills and grow webs between your fingers",
                            ),
                            ("Breathing", "You can breathe underwater"),
                            ("Swim Speed", "Equal to your Speed"),
                        )
                    ),
                ),
            ),
            Option(
                "Change Appearance",
                (
                    Facts(
                        (
                            (
                                "You decide",
                                "Your height, weight, facial features, sound of your voice, hair length, coloration, and other distinguishing characteristics",
                            ),
                            (
                                "Species",
                                "You can appear as a member of another species, though none of your statistics change",
                            ),
                            (
                                "Limits",
                                "You can't appear as a different size, and your basic shape stays the same (if you're bipedal, you can't become quadrupedal)",
                            ),
                            (
                                "Change again",
                                "For the duration, you can take a Magic action to change your appearance in this way again",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Natural Weapons",
                (
                    Facts(
                        (
                            (
                                "Growth",
                                "Claws (Slashing), fangs (Piercing), horns (Piercing), or hooves (Bludgeoning)",
                            ),
                            (
                                "Unarmed Strike",
                                "When you use your Unarmed Strike to deal damage with the growth, it deals 1d6 damage of the type in parentheses instead of the normal damage for your Unarmed Strike",
                            ),
                            (
                                "Attack and damage",
                                "You use your spellcasting ability modifier for the attack and damage rolls rather than Strength",
                            ),
                        )
                    ),
                ),
            ),
        ]


class AnimalMessenger(ClassSpell):
    rules = SpellRules(
        name="Animal Messenger",
        level=2,
        school=School.ENCHANTMENT,
        classes=(CharacterClass.BARD, CharacterClass.DRUID, CharacterClass.RANGER),
        casting_time=CastingTime(CastingTimeType.ACTION, ritual=True),
        range=Range(RangeType.FOOT, 30),
        components=Components(verbal=True, somatic=True, material="a morsel of food"),
        duration=Duration(DurationType.HOUR, 24),
        source="Player's Handbook",
        description=(
            "A Tiny Beast of your choice that you can see within range must succeed on a Charisma saving throw, or it attempts to deliver a message for you (if the target’s Challenge Rating isn’t 0, it automatically succeeds). You specify a location you have visited and a recipient who matches a general description, such as “a person dressed in the uniform of the town guard” or “a red-haired dwarf wearing a pointed hat.” You also communicate a message of up to twenty-five words. The Beast travels for the duration toward the specified location, covering about 25 miles per 24 hours or 50 miles if the Beast can fly.\n"
            "When the Beast arrives, it delivers your message to the creature that you described, mimicking your communication. If the Beast doesn’t reach its destination before the spell ends, the message is lost, and the Beast returns to where you cast the spell.\n"
            "Using a Higher-Level Spell Slot. The spell’s duration increases by 48 hours for each spell slot level above 2."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.CREATURE,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "ee176954a1c05761")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("A Tiny Beast carries a message for you."),
            Facts(
                (
                    (
                        "Target",
                        "A Tiny Beast of your choice that you can see within range",
                    ),
                    (
                        "Save",
                        "Charisma; if the target's Challenge Rating isn't 0, it automatically succeeds",
                    ),
                    ("Failed save", "It attempts to deliver a message for you"),
                )
            ),
            Facts(
                (
                    (
                        "Destination",
                        'A location you have visited, and a recipient who matches a general description, such as "a person dressed in the uniform of the town guard" or "a red-haired dwarf wearing a pointed hat"',
                    ),
                    ("Message", "Up to twenty-five words"),
                    (
                        "Travel",
                        "For the duration, toward the specified location, covering about 25 miles per 24 hours, or 50 miles if the Beast can fly",
                    ),
                    (
                        "Arrival",
                        "It delivers your message to the creature that you described, mimicking your communication",
                    ),
                    (
                        "Too late",
                        "If it doesn't reach its destination before the spell ends, the message is lost, and the Beast returns to where you cast the spell",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (
                    Facts(
                        (("Duration", "+48 hours for each spell slot level above 2"),)
                    ),
                ),
            ),
        ]


class ArcaneLock(ClassSpell):
    rules = SpellRules(
        name="Arcane Lock",
        level=2,
        school=School.ABJURATION,
        classes=(CharacterClass.ARTIFICER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.TOUCH),
        components=Components(
            verbal=True,
            somatic=True,
            material="gold dust worth 25+ GP, which the spell consumes",
        ),
        duration=Duration(DurationType.UNTIL_DISPELLED),
        source="Player's Handbook",
        description="You touch a closed door, window, gate, container, or hatch and magically lock it for the duration. This lock can’t be unlocked by any nonmagical means. You and any creatures you designate when you cast the spell can open and close the object despite the lock. You can also set a password that, when spoken within 5 feet of the object, unlocks it for 1 minute.",
        usage_tags=("utility",),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "54b7b69d0ab6611c")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You magically lock a closed door, window, gate, container, or hatch you touch."
            ),
            Facts(
                (
                    (
                        "Lock",
                        "For the duration, it can't be unlocked by any nonmagical means",
                    ),
                    (
                        "Access",
                        "You and any creatures you designate when you cast the spell can open and close the object despite the lock",
                    ),
                    (
                        "Password",
                        "You can set a password that, when spoken within 5 feet of the object, unlocks it for 1 minute",
                    ),
                )
            ),
        ]


class ArcaneVigor(ClassSpell):
    rules = SpellRules(
        name="Arcane Vigor",
        level=2,
        school=School.ABJURATION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.SORCERER,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.BONUS_ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "You tap into your life force to heal yourself. Roll one or two of your unexpended Hit Point Dice, and regain a number of Hit Points equal to the roll’s total plus your spellcasting ability modifier. Those dice are then expended.\n"
            "Using a Higher-Level Spell Slot. The number of unexpended Hit Dice you can roll increases by one for each spell slot level above 2."
        ),
        usage_tags=("heal",),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "4bb17e80e9835aac")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Flavor", "You tap into your life force to heal yourself."),
                    (
                        "Healing",
                        "Roll one or two of your unexpended Hit Point Dice, and regain Hit Points equal to the roll's total + your spellcasting ability modifier",
                    ),
                    ("Afterward", "Those dice are then expended"),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (
                    Facts(
                        (
                            (
                                "Hit Dice",
                                "+1 unexpended Hit Die you can roll for each spell slot level above 2",
                            ),
                        )
                    ),
                ),
            ),
        ]


class Augury(ClassSpell):
    rules = SpellRules(
        name="Augury",
        level=2,
        school=School.DIVINATION,
        classes=(CharacterClass.CLERIC, CharacterClass.DRUID, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.MINUTE, 1, ritual=True),
        range=Range(RangeType.SELF),
        components=Components(
            verbal=True,
            somatic=True,
            material="specially marked sticks, bones, cards, or other divinatory tokens worth 25+ GP",
        ),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "You receive an omen from an otherworldly entity about the results of a course of action that you plan to take within the next 30 minutes. The DM chooses the omen from the Omens table.\n"
            "The spell doesn’t account for circumstances, such as other spells, that might change the results.\n"
            "If you cast the spell more than once before finishing a Long Rest, there is a cumulative 25 percent chance for each casting after the first that you get no answer."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "ac1e9cecd900526d")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You receive an omen from an otherworldly entity about the results of a course of action that you plan to take within the next 30 minutes."
            ),
            Facts(
                (
                    ("Omen", "The DM chooses the omen from the Omens table"),
                    (
                        "Limit",
                        "The spell doesn't account for circumstances, such as other spells, that might change the results",
                    ),
                    (
                        "Recasting",
                        "If you cast the spell more than once before finishing a Long Rest, there is a cumulative 25 percent chance for each casting after the first that you get no answer",
                    ),
                )
            ),
            Table(
                ("Omen", "For results that will be..."),
                (
                    ("Weal", "Good"),
                    ("Woe", "Bad"),
                    ("Weal and woe", "Good and bad"),
                    ("Indifference", "Neither especially good nor bad"),
                ),
            ),
        ]


class Barkskin(ClassSpell):
    rules = SpellRules(
        name="Barkskin",
        level=2,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.DRUID, CharacterClass.RANGER),
        casting_time=CastingTime(CastingTimeType.BONUS_ACTION),
        range=Range(RangeType.TOUCH),
        components=Components(verbal=True, somatic=True, material="a handful of bark"),
        duration=Duration(DurationType.HOUR, 1),
        source="Player's Handbook",
        description="You touch a willing creature. Until the spell ends, the target’s skin assumes a bark-like appearance, and the target has an Armor Class of 17 if its AC is lower than that.",
        usage_tags=("buff",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "faf62c5d263b020b")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Flavor", "The target's skin assumes a bark-like appearance."),
                    ("Target", "A willing creature you touch"),
                    (
                        "AC",
                        "Until the spell ends, the target has an Armor Class of 17 if its AC is lower than that",
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
                    CombatCondition("Barkskin", modifiers=(ArmorClassMinimum(17),)),
                ),
            ),
        ]


class BattleFamiliar(ClassSpell):
    rules = SpellRules(
        name="Battle Familiar",
        level=2,
        school=School.CONJURATION,
        classes=(CharacterClass.DRUID, CharacterClass.WARLOCK, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 10),
        components=Components(
            verbal=True, somatic=True, material="a diamond worth 25+ GP"
        ),
        duration=Duration(DurationType.HOUR, 1),
        source="Arcana Unleashed",
        description=(
            "You conjure a familiar imbued with magical might. The familiar appears in an unoccupied space within range; resembles an animal of your choice but is a Celestial, Fey, or Fiend (your choice); and uses the Battle Familiar stat block. When you cast this spell, choose the Brute, Flyer, or Stalker form. The choice determines certain details in the stat block.\n"
            "Combat. The familiar is an ally to you and your allies. It rolls its own Initiative and acts on its own turn.\n"
            "Disappearance of the Familiar. The battle familiar disappears when the spell ends, if it drops to 0 Hit Points, or if you die. When it disappears, it leaves behind in its space anything it was wearing or carrying. If you cast this spell again, you decide whether you summon the familiar that disappeared or a different one.\n"
            "One Familiar at a Time. You can’t have more than one familiar at a time. If you cast this spell while you already have a familiar from this spell, that familiar is replaced by the new one.\n"
            "If you have a familiar from the Find Familiar spell when you cast this spell, you empower your existing familiar rather than conjuring a new one. For the duration, your familiar can attack in addition to taking other actions as normal, and your familiar’s game statistics are replaced by the Battle Familiar stat block, but it retains its creature type, alignment, Hit Points, Hit Point Dice, and any features granted by the Find Familiar spell. Your familiar gains a number of Temporary Hit Points equal to the Hit Points of the battle familiar. Battle Familiar ends early if the familiar has no more Temporary Hit Points left, and these Temporary Hit Points vanish if any remain when Battle Familiar ends. Your familiar reverts to its previous form when Battle Familiar ends.\n"
            "Using a Higher-Level Spell Slot. Use the spell slot’s level for the spell’s level in the stat block."
        ),
        usage_tags=("summon",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "05858608bf7cdff3")


class BeastSense(ClassSpell):
    rules = SpellRules(
        name="Beast Sense",
        level=2,
        school=School.DIVINATION,
        classes=(CharacterClass.DRUID, CharacterClass.RANGER),
        casting_time=CastingTime(CastingTimeType.ACTION, ritual=True),
        range=Range(RangeType.TOUCH),
        components=Components(somatic=True),
        duration=Duration(DurationType.HOUR, 1, concentration=True),
        source="Player's Handbook",
        description="You touch a willing Beast. For the duration, you can perceive through the Beast’s senses as well as your own. When perceiving through the Beast’s senses, you benefit from any special senses it has.",
        usage_tags=("utility",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "f3074c476c12665e")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You perceive the world through a Beast's senses."),
            Facts(
                (
                    ("Target", "A willing Beast you touch"),
                    (
                        "Senses",
                        "For the duration, you can perceive through the Beast's senses as well as your own",
                    ),
                    (
                        "Special senses",
                        "When perceiving through its senses, you benefit from any special senses it has",
                    ),
                )
            ),
        ]


class BlindnessDeafness(ClassSpell):
    rules = SpellRules(
        name="Blindness/Deafness",
        level=2,
        school=School.TRANSMUTATION,
        classes=(
            CharacterClass.BARD,
            CharacterClass.CLERIC,
            CharacterClass.SORCERER,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 120),
        components=Components(verbal=True),
        duration=Duration(DurationType.MINUTE, 1),
        source="Player's Handbook",
        description=(
            "One creature that you can see within range must succeed on a Constitution saving throw, or it has the Blinded or Deafened condition (your choice) for the duration. At the end of each of its turns, the target repeats the save, ending the spell on itself on a success.\n"
            "Using a Higher-Level Spell Slot. You can target one additional creature for each spell slot level above 2."
        ),
        usage_tags=("control",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "9316d63edc411037")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Target", "One creature that you can see within range"),
                    ("Save", "Constitution"),
                    (
                        "Failed save",
                        "Blinded or Deafened (your choice) for the duration",
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
                        (("Targets", "+1 creature for each spell slot level above 2"),)
                    ),
                ),
            ),
        ]


class Blur(ClassSpell):
    rules = SpellRules(
        name="Blur",
        level=2,
        school=School.ILLUSION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.SORCERER,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description="Your body becomes blurred. For the duration, any creature has Disadvantage on attack rolls against you. An attacker is immune to this effect if it perceives you with Blindsight or Truesight.",
        usage_tags=("buff", "control"),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "1b686a091cc0b3ee")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Flavor", "Your body becomes blurred."),
                    (
                        "Effect",
                        "For the duration, any creature has Disadvantage on attack rolls against you",
                    ),
                    (
                        "Unaffected",
                        "An attacker is immune to this effect if it perceives you with Blindsight or Truesight",
                    ),
                )
            )
        ]


class BorrowedKnowledge(ClassSpell):
    rules = SpellRules(
        name="Borrowed Knowledge",
        level=2,
        school=School.DIVINATION,
        classes=(
            CharacterClass.BARD,
            CharacterClass.CLERIC,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(
            verbal=True, somatic=True, material="a book worth at least 25 gp"
        ),
        duration=Duration(DurationType.HOUR, 1),
        source="Strixhaven: A Curriculum of Chaos",
        description="You draw on knowledge from spirits of the past. Choose one skill in which you lack proficiency. For the spell's duration, you have proficiency in the chosen skill. The spell ends early if you cast it again.",
        usage_tags=("buff",),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "78066e249ff2510f")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Flavor", "You draw on knowledge from spirits of the past."),
                    ("Skill", "Choose one skill in which you lack proficiency"),
                    (
                        "Effect",
                        "For the spell's duration, you have proficiency in the chosen skill",
                    ),
                    ("Ends early", "If you cast this spell again"),
                )
            )
        ]


class BrandingSmite(ClassSpell):
    rules = SpellRules(
        name="Branding Smite",
        level=2,
        school=School.EVOCATION,
        classes=(CharacterClass.PALADIN,),
        casting_time=CastingTime(CastingTimeType.BONUS_ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "The next time you hit a creature with a weapon attack before this spell ends, the weapon gleams with astral radiance as you strike. The attack deals an extra 2d6 radiant damage to the target, which becomes visible if it is invisible, and the target sheds dim light in a 5-foot radius and can't become invisible until the spell ends.\n"
            "At Higher Levels. When you cast this spell using a spell slot of 3rd level or higher, the extra damage increases by 1d6 for each slot level above 2nd."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "1fb2610a62a03cfa")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Flavor", "The weapon gleams with astral radiance as you strike."),
                    (
                        "Trigger",
                        "The next time you hit a creature with a weapon attack before this spell ends",
                    ),
                    (
                        "Damage",
                        "The attack deals an extra 2d6 Radiant damage to the target",
                    ),
                    (
                        "Revealed",
                        "The target becomes visible if it is invisible, and it sheds dim light in a 5-foot radius and can't become invisible until the spell ends",
                    ),
                )
            ),
            Option(
                "At Higher Levels",
                (Facts((("Extra damage", "+1d6 for each slot level above 2nd"),)),),
            ),
        ]


class CalmEmotions(ClassSpell):
    rules = SpellRules(
        name="Calm Emotions",
        level=2,
        school=School.ENCHANTMENT,
        classes=(CharacterClass.BARD, CharacterClass.CLERIC),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "Each Humanoid in a 20-foot-radius Sphere centered on a point you choose within range must succeed on a Charisma saving throw or be affected by one of the following effects (choose for each creature):\n"
            "The creature has Immunity to the Charmed and Frightened conditions until the spell ends. If the creature was already Charmed or Frightened, those conditions are suppressed for the duration.\n"
            "The creature becomes Indifferent about creatures of your choice that it’s Hostile toward. This indifference ends if the target takes damage or witnesses its allies taking damage. When the spell ends, the creature’s attitude returns to normal."
        ),
        usage_tags=("heal",),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "4c9011d45a0f865d")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Area",
                        "20-foot-radius Sphere centered on a point you choose within range",
                    ),
                    ("Save", "Charisma, made by each Humanoid in the Sphere"),
                    (
                        "Failed save",
                        "One of the effects below (choose for each creature)",
                    ),
                )
            ),
            Option(
                "Immunity",
                (
                    Facts(
                        (
                            (
                                "Effect",
                                "The creature has Immunity to the Charmed and Frightened conditions until the spell ends",
                            ),
                            (
                                "Already affected",
                                "If it was already Charmed or Frightened, those conditions are suppressed for the duration",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Indifference",
                (
                    Facts(
                        (
                            (
                                "Effect",
                                "The creature becomes Indifferent about creatures of your choice that it's Hostile toward",
                            ),
                            (
                                "Ends early",
                                "If the target takes damage or witnesses its allies taking damage",
                            ),
                            ("Spell ends", "The creature's attitude returns to normal"),
                        )
                    ),
                ),
            ),
        ]


class CloudOfDaggers(ClassSpell):
    rules = SpellRules(
        name="Cloud of Daggers",
        level=2,
        school=School.CONJURATION,
        classes=(
            CharacterClass.BARD,
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True, somatic=True, material="a sliver of glass"),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "You conjure spinning daggers in a 5-foot Cube centered on a point within range. Each creature in that area takes 4d4 Slashing damage. A creature also takes this damage if it enters the Cube or ends its turn there or if the Cube moves into its space. A creature takes this damage only once per turn.\n"
            "On your later turns, you can take a Magic action to teleport the Cube up to 30 feet.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 2d4 for each spell slot level above 2."
        ),
        usage_tags=("buff", "damage"),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "2894f5c3c00a3d0f")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You conjure spinning daggers in a 5-foot Cube centered on a point within range.",
                    ),
                    ("Area", "5-foot Cube centered on a point within range"),
                    ("Damage", "4d4 Slashing damage to each creature in the area"),
                    (
                        "Also",
                        "A creature also takes this damage if it enters the Cube or ends its turn there, or if the Cube moves into its space",
                    ),
                    ("Limit", "A creature takes this damage only once per turn"),
                    (
                        "Move",
                        "On your later turns, you can take a Magic action to teleport the Cube up to 30 feet",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Damage", "+2d4 for each spell slot level above 2"),)),),
            ),
        ]


class ConjureTools(ClassSpell):
    rules = SpellRules(
        name="Conjure Tools",
        level=2,
        school=School.CONJURATION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.BARD,
            CharacterClass.RANGER,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 30),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.HOUR, 8),
        source="D&D Beyond Drops - September 2026",
        description=(
            "This spell creates a set of Artisan’s Tools of your choice. You have proficiency with these tools. At the end of the spell’s duration, the tools vanish, but any items created or transformed by the tools remain. The spell ends early if you cast it again or if the tools are more than 10 feet away from you.\n"
            "Using a Higher-Level Spell Slot. If cast with a level 3 spell slot, you work as efficiently as two characters when determining how much time it takes to craft nonmagical items using the tools."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "a1263ebba0b035e7")


class ContinualFlame(ClassSpell):
    rules = SpellRules(
        name="Continual Flame",
        level=2,
        school=School.EVOCATION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.CLERIC,
            CharacterClass.DRUID,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.TOUCH),
        components=Components(
            verbal=True,
            somatic=True,
            material="ruby dust worth 50+ GP, which the spell consumes",
        ),
        duration=Duration(DurationType.UNTIL_DISPELLED),
        source="Player's Handbook",
        description="A flame springs from an object that you touch. The effect casts Bright Light in a 20-foot radius and Dim Light for an additional 20 feet. It looks like a regular flame, but it creates no heat and consumes no fuel. The flame can be covered or hidden but not smothered or quenched.",
        usage_tags=("utility",),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "9ef6eba9a428899c")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("A flame springs from an object that you touch."),
            Facts(
                (
                    (
                        "Light",
                        "Bright Light in a 20-foot radius and Dim Light for an additional 20 feet",
                    ),
                    (
                        "The flame",
                        "It looks like a regular flame, but it creates no heat and consumes no fuel",
                    ),
                    (
                        "Covering",
                        "It can be covered or hidden but not smothered or quenched",
                    ),
                )
            ),
        ]


class CordonOfArrows(ClassSpell):
    rules = SpellRules(
        name="Cordon of Arrows",
        level=2,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.RANGER,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.TOUCH),
        components=Components(
            verbal=True, somatic=True, material="an ornamental braid"
        ),
        duration=Duration(DurationType.HOUR, 8),
        source="Player's Handbook",
        description=(
            "You touch up to four nonmagical Arrows or Bolts and plant them in the ground in your space. Until the spell ends, the ammunition can’t be physically uprooted, and whenever a creature other than you enters a space within 30 feet of the ammunition for the first time on a turn or ends its turn there, one piece of ammunition flies up to strike it. The creature must succeed on a Dexterity saving throw or take 2d4 Piercing damage. The piece of ammunition is then destroyed. The spell ends when none of the ammunition remains planted in the ground.\n"
            "When you cast this spell, you can designate any creatures you choose, and the spell ignores them.\n"
            "Using a Higher-Level Spell Slot. The amount of ammunition that can be affected increases by two for each spell slot level above 2."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "42c4e3b3664757fb")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You plant ammunition in the ground that shoots at intruders."),
            Facts(
                (
                    (
                        "Ammunition",
                        "Up to four nonmagical Arrows or Bolts you touch, planted in the ground in your space; until the spell ends, they can't be physically uprooted",
                    ),
                    (
                        "Trigger",
                        "A creature other than you enters a space within 30 feet of the ammunition for the first time on a turn or ends its turn there; one piece of ammunition flies up to strike it",
                    ),
                    ("Save", "Dexterity"),
                    ("Failed save", "2d4 Piercing damage"),
                    ("Successful save", "No damage"),
                    ("Afterward", "The piece of ammunition is then destroyed"),
                    (
                        "Ignored",
                        "When you cast the spell, you can designate any creatures you choose, and the spell ignores them",
                    ),
                    (
                        "Ends",
                        "When none of the ammunition remains planted in the ground",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (
                    Facts(
                        (("Ammunition", "+2 pieces for each spell slot level above 2"),)
                    ),
                ),
            ),
        ]


class CrownOfMadness(ClassSpell):
    rules = SpellRules(
        name="Crown of Madness",
        level=2,
        school=School.ENCHANTMENT,
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
        source="Player's Handbook",
        description=(
            "One creature that you can see within range must succeed on a Wisdom saving throw or have the Charmed condition for the duration. The creature succeeds automatically if it isn’t Humanoid.\n"
            "A spectral crown appears on the Charmed target's head, and it must use its action before moving on each of its turns to make a melee attack against a creature other than itself that you mentally choose. The target can act normally on its turn if you choose no creature or if no creature is within its reach. The target repeats the save at the end of each of its turns, ending the spell on itself on a success.\n"
            "On your later turns, you must take the Magic action to maintain control of the target, or the spell ends."
        ),
        usage_tags=("control",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "67e3d92febdd0403")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "A spectral crown appears on the Charmed target's head.",
                    ),
                    ("Target", "One creature that you can see within range"),
                    (
                        "Save",
                        "Wisdom; the creature succeeds automatically if it isn't Humanoid",
                    ),
                    ("Failed save", "Charmed for the duration"),
                )
            ),
            Option(
                "While Charmed",
                (
                    Facts(
                        (
                            (
                                "Its turns",
                                "It must use its action before moving on each of its turns to make a melee attack against a creature other than itself that you mentally choose",
                            ),
                            (
                                "No target",
                                "It can act normally on its turn if you choose no creature or if no creature is within its reach",
                            ),
                            (
                                "Repeat save",
                                "At the end of each of its turns, ending the spell on itself on a success",
                            ),
                            (
                                "Control",
                                "On your later turns, you must take the Magic action to maintain control of the target, or the spell ends",
                            ),
                        )
                    ),
                ),
            ),
        ]


class Darkness(ClassSpell):
    rules = SpellRules(
        name="Darkness",
        level=2,
        school=School.EVOCATION,
        classes=(
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True, material="bat fur and a piece of coal"),
        duration=Duration(DurationType.MINUTE, 10, concentration=True),
        source="Player's Handbook",
        description=(
            "For the duration, magical Darkness spreads from a point within range and fills a 15-foot-radius Sphere. Darkvision can’t see through it, and nonmagical light can’t illuminate it.\n"
            "Alternatively, you cast the spell on an object that isn’t being worn or carried, causing the Darkness to fill a 15-foot Emanation originating from that object. Covering that object with something opaque, such as a bowl or helm, blocks the Darkness.\n"
            "If any of this spell’s area overlaps with an area of Bright Light or Dim Light created by a spell of level 2 or lower, that other spell is dispelled."
        ),
        usage_tags=("buff", "control"),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "edfb5807bfcd8471")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "For the duration, magical Darkness spreads from a point or an object."
            ),
            Facts(
                (
                    (
                        "Area",
                        "15-foot-radius Sphere spreading from a point within range",
                    ),
                    (
                        "Or",
                        "Cast on an object that isn't being worn or carried, the Darkness fills a 15-foot Emanation originating from that object; covering the object with something opaque, such as a bowl or helm, blocks the Darkness",
                    ),
                    (
                        "Darkness",
                        "Darkvision can't see through it, and nonmagical light can't illuminate it",
                    ),
                    (
                        "Dispels",
                        "If any of this spell's area overlaps with an area of Bright Light or Dim Light created by a spell of level 2 or lower, that other spell is dispelled",
                    ),
                )
            ),
        ]


class Darkvision(ClassSpell):
    rules = SpellRules(
        name="Darkvision",
        level=2,
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
        components=Components(verbal=True, somatic=True, material="a dried carrot"),
        duration=Duration(DurationType.HOUR, 8),
        source="Player's Handbook",
        description="For the duration, a willing creature you touch has Darkvision with a range of 150 feet.",
        usage_tags=("buff",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "70d2f295a796eb2c")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You grant a willing creature the ability to see in the dark."),
            Facts(
                (
                    ("Target", "A willing creature you touch"),
                    ("Effect", "Darkvision with a range of 150 feet for the duration"),
                )
            ),
        ]


class DeathArmor(ClassSpell):
    rules = SpellRules(
        name="Death Armor",
        level=2,
        school=School.NECROMANCY,
        classes=(CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.TOUCH),
        components=Components(
            verbal=True,
            somatic=True,
            material="an onyx worth 50+ GP, which the spell consumes",
        ),
        duration=Duration(DurationType.HOUR, 1),
        source="Forgotten Realms - Heroes of Faerun",
        description="For the duration, an inky aura surrounds one creature you touch. The target has Advantage on Death Saving Throws, and once per turn, when a creature within 5 feet of the target hits it with a melee attack roll, the attacker takes 2d4 Necrotic damage.",
        usage_tags=("buff", "damage"),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "2af8bce04431f2c5")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "For the duration, an inky aura surrounds one creature you touch.",
                    ),
                    ("Target", "One creature you touch"),
                    ("Death saves", "The target has Advantage on Death Saving Throws"),
                    (
                        "Retaliation",
                        "Once per turn, when a creature within 5 feet of the target hits it with a melee attack roll, the attacker takes 2d4 Necrotic damage",
                    ),
                )
            )
        ]


class DeryansHelpfulHomunculi(ClassSpell):
    rules = SpellRules(
        name="Deryan's Helpful Homunculi",
        level=2,
        school=School.CONJURATION,
        classes=(CharacterClass.CLERIC, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION, ritual=True),
        range=Range(RangeType.SELF),
        components=Components(
            verbal=True,
            somatic=True,
            material="powdered gemstones worth 100+ GP, which the spell consumes, and one set of Artisan’s Tools with which you have proficiency",
        ),
        duration=Duration(DurationType.HOUR, 8),
        source="Forgotten Realms - Heroes of Faerun",
        description=(
            "You summon a group of helpful spirits, which lasts for the duration. The spirits appear as homunculi or as another Construct of your choice but are intangible and invulnerable, and they are considered to have proficiency in the Arcana skill and with the set of Artisan’s Tools used in the spell’s casting.\n"
            "If you are crafting an item, the spirits function as a single assistant for your crafting, halving the crafting time."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "c67c75b7596f5747")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You summon a group of helpful spirits, which lasts for the duration."
            ),
            Facts(
                (
                    (
                        "Appearance",
                        "Homunculi or another Construct of your choice, but intangible and invulnerable",
                    ),
                    (
                        "Proficiency",
                        "They are considered to have proficiency in the Arcana skill and with the set of Artisan's Tools used in the spell's casting",
                    ),
                    (
                        "Crafting",
                        "If you are crafting an item, the spirits function as a single assistant for your crafting, halving the crafting time",
                    ),
                )
            ),
        ]


class DetectThoughts(ClassSpell):
    rules = SpellRules(
        name="Detect Thoughts",
        level=2,
        school=School.DIVINATION,
        classes=(CharacterClass.BARD, CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True, material="1 Copper Piece"),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "You activate one of the effects below. Until the spell ends, you can activate either effect as a Magic action on your later turns.\n"
            "Sense Thoughts. You sense the presence of thoughts within 30 feet of yourself that belong to creatures that know languages or are telepathic. You don’t read the thoughts, but you know that a thinking creature is present.\n"
            "The spell is blocked by 1 foot of stone, dirt, or wood; 1 inch of metal; or a thin sheet of lead.\n"
            "Read Thoughts. Target one creature you can see within 30 feet of yourself or one creature within 30 feet of yourself that you detected with the Sense Thoughts option. You learn what is most on the target’s mind right now. If the target doesn’t know any languages and isn’t telepathic, you learn nothing.\n"
            "As a Magic action on your next turn, you can try to probe deeper into the target’s mind. If you probe deeper, the target makes a Wisdom saving throw. On a failed save, you discern the target’s reasoning, emotions, and something that looms large in its mind (such as a worry, love, or hate). On a successful save, the spell ends. Either way, the target knows that you are probing into its mind, and until you shift your attention away from the target’s mind, the target can take an action on its turn to make an Intelligence (Arcana) check against your spell save DC, ending the spell on a success."
        ),
        usage_tags=("buff",),
        target=FeatureTarget.CREATURE,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "9565907d2a19a61e")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You sense and read the thoughts of nearby minds. Activate one option below when you cast the spell; until it ends, you can activate either one as a Magic action on your later turns."
            ),
            Facts(
                (
                    (
                        "Blocked by",
                        "1 foot of stone, dirt, or wood; 1 inch of metal; or a thin sheet of lead",
                    ),
                )
            ),
            Option(
                "Sense Thoughts",
                (
                    Facts(
                        (
                            ("Area", "Within 30 feet of you"),
                            (
                                "Effect",
                                "You sense the presence of thoughts of creatures that know languages or are telepathic; you don't read the thoughts, but you know a thinking creature is present",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Read Thoughts",
                (
                    Facts(
                        (
                            (
                                "Target",
                                "One creature you can see within 30 feet of you, or one within 30 feet you detected with Sense Thoughts",
                            ),
                            (
                                "Effect",
                                "You learn what is most on its mind right now; you learn nothing if it knows no languages and isn't telepathic",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Probe Deeper",
                (
                    Facts(
                        (
                            (
                                "Action",
                                "Magic action on your next turn, after Read Thoughts",
                            ),
                            ("Save", "Wisdom"),
                            (
                                "Failed save",
                                "You discern its reasoning, emotions, and something that looms large in its mind (such as a worry, love, or hate)",
                            ),
                            ("Successful save", "The spell ends"),
                            (
                                "Either way",
                                "The target knows you're probing its mind; until you shift your attention away, it can take an action to make an Intelligence (Arcana) check against your spell save DC, ending the spell on a success",
                            ),
                        )
                    ),
                ),
            ),
        ]


class DisruptiveTune(ClassSpell):
    rules = SpellRules(
        name="Disruptive Tune",
        level=2,
        school=School.ABJURATION,
        classes=(CharacterClass.BARD, CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 120),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Arcana Unleashed",
        description="A distracting melody momentarily fills a 20-foot-radius Sphere centered on a point you choose within range. Each creature in the Sphere makes a Constitution saving throw. On a failed save, a target loses Concentration, and it has Disadvantage on Constitution saving throws to maintain Concentration for the spell’s duration.",
        usage_tags=("control",),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "200a6f2de32fe121")


class DragonsBreath(ClassSpell):
    rules = SpellRules(
        name="Dragon's Breath",
        level=2,
        school=School.TRANSMUTATION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.SORCERER,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.BONUS_ACTION),
        range=Range(RangeType.TOUCH),
        components=Components(verbal=True, somatic=True, material="a hot pepper"),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "You touch one willing creature, and choose Acid, Cold, Fire, Lightning, or Poison. Until the spell ends, the target can take a Magic action to exhale a 15-foot Cone. Each creature in that area makes a Dexterity saving throw, taking 3d6 damage of the chosen type on a failed save or half as much damage on a successful one.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 1d6 for each spell slot level above 2."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "2a732c335cc8cbc8")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Target", "One willing creature you touch"),
                    (
                        "Damage type",
                        "Acid, Cold, Fire, Lightning, or Poison (choose when casting)",
                    ),
                    (
                        "Breath",
                        "Until the spell ends, the target can take a Magic action to exhale a 15-foot Cone",
                    ),
                    ("Save", "Dexterity, made by each creature in the Cone"),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (("3d6 damage of the chosen type", "Half as much damage"),),
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Damage", "+1d6 for each spell slot level above 2"),)),),
            ),
        ]


class DuelingGround(ClassSpell):
    rules = SpellRules(
        name="Dueling Ground",
        level=2,
        school=School.ABJURATION,
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
        casting_time=CastingTime(CastingTimeType.MINUTE, 10, ritual=True),
        range=Range(RangeType.TOUCH),
        components=Components(
            verbal=True, somatic=True, material="a silk flag worth 100+ GP"
        ),
        duration=Duration(DurationType.HOUR, 1),
        source="Arcana Unleashed",
        description=(
            "You create a magical dueling ground bounded by a glowing, rune-scribed circle in a 15-foot-radius Sphere centered on a point on the ground you touch.\n"
            "As part of creating the dueling ground, you designate two willing creatures within the Sphere as the targets. The spell ends early if a creature other than one of the targets enters the Sphere.\n"
            "If a target drops to 0 Hit Points while in the dueling ground, the target is Stable and teleports to the nearest unoccupied space outside the dueling ground. If a target is subjected to an effect that would kill it instantly without dealing damage while in the dueling ground, the target doesn’t die and instead has 0 Hit Points and the Unconscious condition, is Stable, and teleports to the nearest unoccupied space outside the dueling ground.\n"
            "When only one target remains in the dueling ground, runes matching those on the ground around the Sphere briefly flash around the remaining target’s head like a crown.\n"
            "Using a Higher-Level Spell Slot. You can target one additional willing creature for each spell slot level above 2."
        ),
        usage_tags=("buff", "heal"),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "ff05e9008f17fbb7")


class DustDevil(ClassSpell):
    rules = SpellRules(
        name="Dust Devil",
        level=2,
        school=School.CONJURATION,
        classes=(CharacterClass.DRUID, CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True, somatic=True, material="a pinch of dust"),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Xanathar's Guide to Everything",
        description=(
            "Choose an unoccupied 5-foot cube of air that you can see within range. An elemental force that resembles a dust devil appears in the cube and lasts for the spell's duration.\n"
            "Any creature that ends its turn within 5 feet of the dust devil must make a Strength saving throw. On a failed save, the creature takes 1d8 bludgeoning damage and is pushed 10 feet away. On a successful save, the creature takes half as much damage and isn't pushed.\n"
            "As a bonus action, you can move the dust devil up to 30 feet in any direction. If the dust devil moves over sand, dust, loose dirt, or small gravel, it sucks up the material and forms a 10-foot-radius cloud of debris around itself that lasts until the start of your next turn. The cloud heavily obscures its area.\n"
            "At Higher Levels. When you cast this spell using a spell slot of 3rd level or higher, the damage increases by 1d8 for each slot level above 2nd."
        ),
        usage_tags=("damage", "utility"),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "f811bb50df455e62")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "An elemental force that resembles a dust devil appears in the cube and lasts for the spell's duration.",
                    ),
                    (
                        "Appears",
                        "In an unoccupied 5-foot cube of air that you can see within range",
                    ),
                    (
                        "Save",
                        "Strength, made by any creature that ends its turn within 5 feet of the dust devil",
                    ),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (
                    (
                        "1d8 Bludgeoning damage, and pushed 10 feet away",
                        "Half as much damage, and not pushed",
                    ),
                ),
            ),
            Option(
                "Moving It",
                (
                    Facts(
                        (
                            ("Action", "A bonus action"),
                            ("Movement", "Up to 30 feet in any direction"),
                            (
                                "Debris",
                                "If it moves over sand, dust, loose dirt, or small gravel, it sucks up the material and forms a 10-foot-radius cloud of debris around itself that lasts until the start of your next turn; the cloud heavily obscures its area",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "At Higher Levels",
                (Facts((("Damage", "+1d8 for each slot level above 2nd"),)),),
            ),
        ]


class Earthbind(ClassSpell):
    rules = SpellRules(
        name="Earthbind",
        level=2,
        school=School.TRANSMUTATION,
        classes=(
            CharacterClass.DRUID,
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 300),
        components=Components(verbal=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Xanathar's Guide to Everything",
        description="Choose one creature you can see within range. Yellow strips of magical energy loop around the creature. The target must succeed on a Strength saving throw or its flying speed (if any) is reduced to 0 feet for the spell's duration. An airborne creature affected by this spell descends at 60 feet per round until it reaches the ground or the spell ends.",
        usage_tags=("utility",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "c89ba85a87dc84d8")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "Yellow strips of magical energy loop around the creature.",
                    ),
                    ("Target", "One creature you can see within range"),
                    ("Save", "Strength"),
                    (
                        "Failed save",
                        "Its flying speed (if any) is reduced to 0 feet for the spell's duration",
                    ),
                    (
                        "Airborne",
                        "An airborne creature affected by this spell descends at 60 feet per round until it reaches the ground or the spell ends",
                    ),
                )
            )
        ]


class ElminstersElusion(ClassSpell):
    rules = SpellRules(
        name="Elminster's Elusion",
        level=2,
        school=School.ABJURATION,
        classes=(CharacterClass.WIZARD,),
        casting_time=CastingTime(CastingTimeType.BONUS_ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 10, concentration=True),
        source="Forgotten Realms - Heroes of Faerun",
        description="Arcane wards protect you against magic for the duration. You have Advantage on saving throws against spells and magical effects. Additionally, if you succeed on a saving throw against a spell or magical effect and would normally take half as much damage, you instead take no damage.",
        usage_tags=("buff",),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "a50d98d286842409")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "Arcane wards protect you against magic for the duration.",
                    ),
                    (
                        "Saves",
                        "Advantage on saving throws against spells and magical effects",
                    ),
                    (
                        "Half damage",
                        "If you succeed on a saving throw against a spell or magical effect and would normally take half as much damage, you instead take no damage",
                    ),
                )
            )
        ]


class EnhanceAbility(ClassSpell):
    rules = SpellRules(
        name="Enhance Ability",
        level=2,
        school=School.TRANSMUTATION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.BARD,
            CharacterClass.CLERIC,
            CharacterClass.DRUID,
            CharacterClass.RANGER,
            CharacterClass.SORCERER,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.TOUCH),
        components=Components(verbal=True, somatic=True, material="fur or a feather"),
        duration=Duration(DurationType.HOUR, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "You touch a creature and choose Strength, Dexterity, Intelligence, Wisdom, or Charisma. For the duration, the target has Advantage on ability checks using the chosen ability.\n"
            "Using a Higher-Level Spell Slot. You can target one additional creature for each spell slot level above 2. You can choose a different ability for each target."
        ),
        usage_tags=("buff",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "fafcd06e702ee2ba")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Target", "A creature you touch"),
                    (
                        "Ability",
                        "Choose Strength, Dexterity, Intelligence, Wisdom, or Charisma",
                    ),
                    (
                        "Effect",
                        "For the duration, the target has Advantage on ability checks using the chosen ability",
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
                                "+1 creature for each spell slot level above 2",
                            ),
                            (
                                "Abilities",
                                "You can choose a different ability for each target",
                            ),
                        )
                    ),
                ),
            ),
        ]


class EnlargeReduce(ClassSpell):
    rules = SpellRules(
        name="Enlarge/Reduce",
        level=2,
        school=School.TRANSMUTATION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.BARD,
            CharacterClass.DRUID,
            CharacterClass.SORCERER,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 30),
        components=Components(
            verbal=True, somatic=True, material="a pinch of powdered iron"
        ),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "For the duration, the spell enlarges or reduces a creature or an object you can see within range (see the chosen effect below). A targeted object must be neither worn nor carried. If the target is an unwilling creature, it can make a Constitution saving throw. On a successful save, the spell has no effect.\n"
            "Everything that a targeted creature is wearing and carrying changes size with it. Any item it drops returns to normal size at once. A thrown weapon or piece of ammunition returns to normal size immediately after it hits or misses a target.\n"
            "Enlarge. The target’s size increases by one category - from Medium to Large, for example. The target also has Advantage on Strength checks and Strength saving throws. The target’s attacks with its enlarged weapons or Unarmed Strikes deal an extra 1d4 damage on a hit.\n"
            "Reduce. The target’s size decreases by one category - from Medium to Small, for example. The target also has Disadvantage on Strength checks and Strength saving throws. The target’s attacks with its reduced weapons or Unarmed Strikes deal 1d4 less damage on a hit (this can’t reduce the damage below 1)."
        ),
        usage_tags=("buff",),
        target=FeatureTarget.CREATURE,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "8d1f833578ed00b2")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You enlarge or reduce a creature or an object you can see within range."
            ),
            Facts(
                (
                    (
                        "Target",
                        "A creature, or an object that is neither worn nor carried",
                    ),
                    (
                        "Unwilling",
                        "The creature can make a Constitution save; on a success, the spell has no effect",
                    ),
                    (
                        "Gear",
                        "Everything a creature wears and carries changes size with it; any item it drops returns to normal size at once, and a thrown weapon or piece of ammunition returns to normal size immediately after it hits or misses a target",
                    ),
                )
            ),
            Table(
                ("", "Enlarge", "Reduce"),
                (
                    (
                        "Size",
                        "One category larger (Medium to Large, for example)",
                        "One category smaller (Medium to Small, for example)",
                    ),
                    ("Strength checks and saves", "Advantage", "Disadvantage"),
                    (
                        "Damage with its weapons or Unarmed Strikes",
                        "+1d4 on a hit",
                        "-1d4 on a hit (not below 1)",
                    ),
                ),
            ),
        ]

    def combat_effects(
        self, character: CharacterView | None = None
    ) -> list[CombatEffect]:
        strength = (D20Test.ABILITY_CHECK, D20Test.SAVING_THROW)
        return [
            CombatEffect(
                name="Enlarge/Reduce: Enlarge",
                conditions=(
                    CombatCondition(
                        "Enlarge/Reduce",
                        modifiers=(
                            Size(steps=1),
                            D20Mode(strength, RollMode.ADVANTAGE, (Ability.STRENGTH,)),
                            Note(
                                "Its attacks with its enlarged weapons or Unarmed"
                                " Strikes deal an extra 1d4 damage on a hit."
                            ),
                        ),
                    ),
                ),
                notes=(
                    "An unwilling target makes a Constitution save first; on a success, the spell has no effect.",
                ),
            ),
            CombatEffect(
                name="Enlarge/Reduce: Reduce",
                roll=EffectRoll.SAVE,
                save_ability=Ability.CONSTITUTION,
                conditions=(
                    CombatCondition(
                        "Enlarge/Reduce",
                        modifiers=(
                            Size(steps=-1),
                            D20Mode(
                                strength, RollMode.DISADVANTAGE, (Ability.STRENGTH,)
                            ),
                            Note(
                                "Its attacks with its reduced weapons or Unarmed"
                                " Strikes deal 1d4 less damage on a hit (not below 1)."
                            ),
                        ),
                    ),
                ),
                notes=("Only an unwilling target saves.",),
            ),
        ]


class Enthrall(ClassSpell):
    rules = SpellRules(
        name="Enthrall",
        level=2,
        school=School.ENCHANTMENT,
        classes=(CharacterClass.BARD, CharacterClass.WARLOCK),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description="You weave a distracting string of words, causing creatures of your choice that you can see within range to make a Wisdom saving throw. Any creature you or your companions are fighting automatically succeeds on this save. On a failed save, a target has a −10 penalty to Wisdom (Perception) checks and Passive Perception until the spell ends.",
        usage_tags=("control",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "94cdab294eb7dd3d")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Flavor", "You weave a distracting string of words."),
                    (
                        "Targets",
                        "Creatures of your choice that you can see within range",
                    ),
                    (
                        "Save",
                        "Wisdom; any creature you or your companions are fighting automatically succeeds",
                    ),
                    (
                        "Failed save",
                        "A -10 penalty to Wisdom (Perception) checks and Passive Perception until the spell ends",
                    ),
                )
            )
        ]


class FindSteed(ClassSpell):
    rules = SpellRules(
        name="Find Steed",
        level=2,
        school=School.CONJURATION,
        classes=(CharacterClass.PALADIN,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 30),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "You summon an otherworldly being that appears as a loyal steed in an unoccupied space of your choice within range. This creature uses the Otherworldly Steed stat block. If you already have a steed from this spell, the steed is replaced by the new one.\n"
            "The steed resembles a Large, rideable animal of your choice, such as a horse, a camel, a dire wolf, or an elk. Whenever you cast the spell, choose the steed’s creature type—Celestial, Fey, or Fiend—which determines certain traits in the stat block.\n"
            "Combat. The steed is an ally to you and your allies. In combat, it shares your Initiative count, and it functions as a controlled mount while you ride it (as defined in the rules on mounted combat). If you have the Incapacitated condition, the steed takes its turn immediately after yours and acts independently, focusing on protecting you.\n"
            "Disappearance of the Steed. The steed disappears if it drops to 0 Hit Points or if you die. When it disappears, it leaves behind anything it was wearing or carrying. If you cast this spell again, you decide whether you summon the steed that disappeared or a different one.\n"
            "Using a Higher-Level Spell Slot. Use the spell slot’s level for the spell’s level in the stat block."
        ),
        usage_tags=("control", "summon"),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "b9295cf2466bd6c0")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You summon an otherworldly being that appears as a loyal steed in an unoccupied space of your choice within range.",
                    ),
                    ("Appears", "In an unoccupied space of your choice within range"),
                    (
                        "Form",
                        "A Large, rideable animal of your choice, such as a horse, a camel, a dire wolf, or an elk",
                    ),
                    (
                        "Creature type",
                        "Celestial, Fey, or Fiend, chosen whenever you cast the spell; it determines certain traits in the stat block",
                    ),
                    ("Stat block", "Otherworldly Steed (below)"),
                    (
                        "One steed",
                        "If you already have a steed from this spell, the steed is replaced by the new one",
                    ),
                )
            ),
            Option(
                "Combat",
                (
                    Facts(
                        (
                            ("Allegiance", "An ally to you and your allies"),
                            ("Initiative", "It shares your Initiative count"),
                            (
                                "Mount",
                                "It functions as a controlled mount while you ride it (as defined in the rules on mounted combat)",
                            ),
                            (
                                "Incapacitated",
                                "If you have the Incapacitated condition, the steed takes its turn immediately after yours and acts independently, focusing on protecting you",
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
                            ("When", "If it drops to 0 Hit Points or if you die"),
                            (
                                "Its gear",
                                "It leaves behind anything it was wearing or carrying",
                            ),
                            (
                                "Recasting",
                                "You decide whether you summon the steed that disappeared or a different one",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Otherworldly Steed",
                (
                    Facts(
                        (
                            ("Type", "Large Celestial, Fey, or Fiend (your choice)"),
                            ("AC", "10 + 1 per spell level"),
                            ("Hit Points", "5 + 10 per spell level"),
                            ("Speed", "60 ft., Fly 60 ft. (requires level 4+ spell)"),
                            (
                                "Abilities",
                                "Str 18, Dex 12, Con 14, Int 6, Wis 12, Cha 8",
                            ),
                            ("Senses", "Passive Perception 11"),
                            ("Languages", "Telepathy 1 mile (works only with you)"),
                            (
                                "Life Bond",
                                "When you regain Hit Points from a level 1+ spell, the steed regains the same number of Hit Points if you're within 5 feet of it",
                            ),
                            (
                                "Otherworldly Slam",
                                "Melee Attack Roll: Bonus equals your spell attack modifier, reach 5 ft. Hit: 1d8 + the spell's level Radiant (Celestial), Psychic (Fey), or Necrotic (Fiend) damage",
                            ),
                            (
                                "Fell Glare",
                                "Bonus Action (Fiend only; recharges after a Long Rest). Wisdom saving throw against your spell save DC, one creature within 60 feet the steed can see. Failure: Frightened until the end of your next turn",
                            ),
                            (
                                "Fey Step",
                                "Bonus Action (Fey only; recharges after a Long Rest). The steed teleports, along with its rider, to an unoccupied space of your choice up to 60 feet away from itself",
                            ),
                            (
                                "Healing Touch",
                                "Bonus Action (Celestial only; recharges after a Long Rest). One creature within 5 feet of the steed regains Hit Points equal to 2d8 + the spell's level",
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


class FindTraps(ClassSpell):
    rules = SpellRules(
        name="Find Traps",
        level=2,
        school=School.DIVINATION,
        classes=(CharacterClass.CLERIC, CharacterClass.DRUID, CharacterClass.RANGER),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 120),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "You sense any trap within range that is within line of sight. A trap, for the purpose of this spell, includes any object or mechanism that was created to cause damage or other danger. Thus, the spell would sense the Alarm or Glyph of Warding spell or a mechanical pit trap, but it wouldn’t reveal a natural weakness in the floor, an unstable ceiling, or a hidden sinkhole.\n"
            "This spell reveals that a trap is present but not its location. You do learn the general nature of the danger posed by a trap you sense."
        ),
        usage_tags=("heal",),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "4adb35d6fb8aabe5")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You sense traps within range."),
            Facts(
                (
                    ("Area", "Any trap within range that is within line of sight"),
                    (
                        "A trap",
                        "Any object or mechanism that was created to cause damage or other danger",
                    ),
                    (
                        "Examples",
                        "It would sense the Alarm or Glyph of Warding spell or a mechanical pit trap, but not a natural weakness in the floor, an unstable ceiling, or a hidden sinkhole",
                    ),
                    (
                        "You learn",
                        "That a trap is present, and the general nature of the danger it poses, but not its location",
                    ),
                )
            ),
        ]


class FlameBlade(ClassSpell):
    rules = SpellRules(
        name="Flame Blade",
        level=2,
        school=School.EVOCATION,
        classes=(CharacterClass.DRUID, CharacterClass.SORCERER),
        casting_time=CastingTime(CastingTimeType.BONUS_ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True, material="a sumac leaf"),
        duration=Duration(DurationType.MINUTE, 10, concentration=True),
        source="Player's Handbook",
        description=(
            "You evoke a fiery blade in your free hand. The blade is similar in size and shape to a scimitar, and it lasts for the duration. If you let go of the blade, it disappears, but you can evoke it again as a Bonus Action.\n"
            "As a Magic action, you can make a melee spell attack with the fiery blade. On a hit, the target takes Fire damage equal to 3d6 plus your spellcasting ability modifier.\n"
            "The flaming blade sheds Bright Light in a 10-foot radius and Dim Light for an additional 10 feet.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 1d6 for each spell slot level above 2."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "4882e0c86df6e4d4")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Flavor", "You evoke a fiery blade in your free hand."),
                    ("Appears", "In your free hand"),
                    (
                        "Blade",
                        "Similar in size and shape to a scimitar; it lasts for the duration",
                    ),
                    (
                        "Letting go",
                        "If you let go of the blade, it disappears, but you can evoke it again as a Bonus Action",
                    ),
                    (
                        "Light",
                        "Bright Light in a 10-foot radius and Dim Light for an additional 10 feet",
                    ),
                )
            ),
            Option(
                "Attack",
                (
                    Facts(
                        (
                            ("Action", "Magic action"),
                            ("Attack", "Melee spell attack with the fiery blade"),
                            (
                                "On a hit",
                                "3d6 + your spellcasting ability modifier Fire damage",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Damage", "+1d6 for each spell slot level above 2"),)),),
            ),
        ]


class FlamingSphere(ClassSpell):
    rules = SpellRules(
        name="Flaming Sphere",
        level=2,
        school=School.CONJURATION,
        classes=(CharacterClass.DRUID, CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True, somatic=True, material="a ball of wax"),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "You create a 5-foot-diameter sphere of fire in an unoccupied space on the ground within range. It lasts for the duration. Any creature that ends its turn within 5 feet of the sphere makes a Dexterity saving throw, taking 2d6 Fire damage on a failed save or half as much damage on a successful one.\n"
            "As a Bonus Action, you can move the sphere up to 30 feet, rolling it along the ground. If you move the sphere into a creature’s space, that creature makes the save against the sphere, and the sphere stops moving for the turn.\n"
            "When you move the sphere, you can direct it over barriers up to 5 feet tall and jump it across pits up to 10 feet wide. Flammable objects that aren’t being worn or carried start burning if touched by the sphere, and it sheds Bright Light in a 20-foot radius and Dim Light for an additional 20 feet.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 1d6 for each spell slot level above 2."
        ),
        usage_tags=("buff", "damage"),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "ae3d70b8c077f9ad")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You create a 5-foot-diameter sphere of fire in an unoccupied space on the ground within range."
            ),
            Facts(
                (
                    ("Appears", "In an unoccupied space on the ground within range"),
                    (
                        "Light",
                        "Bright Light in a 20-foot radius and Dim Light for an additional 20 feet",
                    ),
                    (
                        "Objects",
                        "Flammable objects that aren't being worn or carried start burning if touched by the sphere",
                    ),
                    (
                        "Save",
                        "Dexterity, when a creature ends its turn within 5 feet of the sphere",
                    ),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (("2d6 Fire damage", "Half as much damage"),),
            ),
            Option(
                "Roll the Sphere",
                (
                    Facts(
                        (
                            ("Action", "Bonus Action"),
                            (
                                "Movement",
                                "Up to 30 feet along the ground, over barriers up to 5 feet tall and across pits up to 10 feet wide",
                            ),
                            (
                                "Ramming",
                                "Moving it into a creature's space makes that creature save against it, and the sphere stops moving for the turn",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Damage", "+1d6 for each spell slot level above 2"),)),),
            ),
        ]


class FlockOfFamiliars(ClassSpell):
    rules = SpellRules(
        name="Flock of Familiars",
        level=2,
        school=School.CONJURATION,
        classes=(CharacterClass.WARLOCK, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.MINUTE, 1),
        range=Range(RangeType.TOUCH),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.HOUR, 1, concentration=True),
        source="Lost Laboratory of Kwalish",
        description=(
            "You temporarily summon three familiars – spirits that take animal forms of your choice. Each familiar uses the same rules and options for a familiar conjured by the Find Familiar spell. All the familiars conjured by this spell must be the same type of creature (celestials, fey, or fiends; your choice). If you already have a familiar conjured by the Find Familiar spell or similar means, then one fewer familiars are conjured by this spell.\n"
            "Familiars summoned by this spell can telepathically communicate with you and share their visual or auditory senses while they are within 1 mile of you.\n"
            "When you cast a spell with a range of touch, one of the familiars conjured by this spell can deliver the spell, as normal. However, you can cast a touch spell through only one familiar per turn.\n"
            "At Higher Levels. When you cast this spell using a spell slot of 3rd level or higher, you conjure an additional familiar for each slot level above 2nd."
        ),
        usage_tags=("utility", "summon"),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "fda28b1dd381ed2a")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You temporarily summon three familiars, spirits that take animal forms of your choice."
            ),
            Facts(
                (
                    (
                        "Rules",
                        "Each familiar uses the same rules and options as a familiar conjured by the Find Familiar spell",
                    ),
                    (
                        "Type",
                        "All of them must be the same type of creature (celestials, fey, or fiends; your choice)",
                    ),
                    (
                        "Existing familiar",
                        "If you already have a familiar conjured by the Find Familiar spell or similar means, one fewer familiar is conjured",
                    ),
                    (
                        "Telepathy",
                        "While within 1 mile of you, they can telepathically communicate with you and share their visual or auditory senses",
                    ),
                    (
                        "Touch spells",
                        "One of them can deliver a spell with a range of touch, as normal, but you can cast a touch spell through only one familiar per turn",
                    ),
                )
            ),
            Option(
                "At Higher Levels",
                (Facts((("Familiars", "+1 familiar for each slot level above 2nd"),)),),
            ),
        ]


class GentleRepose(ClassSpell):
    rules = SpellRules(
        name="Gentle Repose",
        level=2,
        school=School.NECROMANCY,
        classes=(CharacterClass.CLERIC, CharacterClass.PALADIN, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION, ritual=True),
        range=Range(RangeType.TOUCH),
        components=Components(
            verbal=True,
            somatic=True,
            material="2 Copper Pieces, which the spell consumes",
        ),
        duration=Duration(DurationType.DAY, 10),
        source="Player's Handbook",
        description=(
            "You touch a corpse or other remains. For the duration, the target is protected from decay and can’t become Undead.\n"
            "The spell also effectively extends the time limit on raising the target from the dead, since days spent under the influence of this spell don’t count against the time limit of spells such as Raise Dead."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "08594474183f2829")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You preserve a corpse or other remains you touch."),
            Facts(
                (
                    (
                        "Effect",
                        "For the duration, the target is protected from decay and can't become Undead",
                    ),
                    (
                        "Raising",
                        "Days spent under the influence of this spell don't count against the time limit of spells such as Raise Dead",
                    ),
                )
            ),
        ]


class GiftOfGab(ClassSpell):
    rules = SpellRules(
        name="Gift of Gab",
        level=2,
        school=School.ENCHANTMENT,
        classes=(CharacterClass.BARD, CharacterClass.WIZARD),
        casting_time=CastingTime(
            CastingTimeType.REACTION,
            trigger="which you take when you speak to another creature",
        ),
        range=Range(RangeType.SELF),
        components=Components(
            verbal=True,
            somatic=True,
            material="2 gold coins, which is consumed as tax for using the spell",
        ),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Acquisitions Inc.",
        description="When you cast this spell, you skillfully reshape the memories of listeners in your immediate area, so that each creature of your choice within 5 feet of you forgets everything you said within the last 6 seconds. Those creatures then remember that you actually said the words you speak as the verbal component of the spell.",
        usage_tags=("utility",),
        target=FeatureTarget.CREATURE,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "31c461204a5f84a4")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You skillfully reshape the memories of listeners in your immediate area.",
                    ),
                    ("Trigger", "You speak to another creature"),
                    ("Targets", "Each creature of your choice within 5 feet of you"),
                    (
                        "Effect",
                        "They forget everything you said within the last 6 seconds, then remember that you actually said the words you speak as the verbal component of the spell",
                    ),
                )
            )
        ]


class GustOfWind(ClassSpell):
    rules = SpellRules(
        name="Gust of Wind",
        level=2,
        school=School.EVOCATION,
        classes=(
            CharacterClass.DRUID,
            CharacterClass.RANGER,
            CharacterClass.SORCERER,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True, material="a legume seed"),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "A Line of strong wind 60 feet long and 10 feet wide blasts from you in a direction you choose for the duration. Each creature in the Line must succeed on a Strength saving throw or be pushed 15 feet away from you in a direction following the Line. A creature that ends its turn in the Line must make the same save.\n"
            "Any creature in the Line must spend 2 feet of movement for every 1 foot it moves when moving closer to you.\n"
            "The gust disperses gas or vapor, and it extinguishes candles and similar unprotected flames in the area. It causes protected flames, such as those of lanterns, to dance wildly and has a 50 percent chance to extinguish them.\n"
            "As a Bonus Action on your later turns, you can change the direction in which the Line blasts from you."
        ),
        usage_tags=("control",),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "fa7d2c487d270740")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("A Line of strong wind blasts from you for the duration."),
            Facts(
                (
                    (
                        "Area",
                        "Line 60 feet long and 10 feet wide, in a direction you choose",
                    ),
                    (
                        "Save",
                        "Strength, made by each creature in the Line, and by a creature that ends its turn in the Line",
                    ),
                    (
                        "Failed save",
                        "Pushed 15 feet away from you in a direction following the Line",
                    ),
                    (
                        "Moving closer",
                        "Any creature in the Line must spend 2 feet of movement for every 1 foot it moves when moving closer to you",
                    ),
                    (
                        "Gas and flames",
                        "The gust disperses gas or vapor and extinguishes candles and similar unprotected flames in the area; protected flames, such as those of lanterns, dance wildly and have a 50 percent chance to be extinguished",
                    ),
                    (
                        "Direction",
                        "As a Bonus Action on your later turns, you can change the direction in which the Line blasts from you",
                    ),
                )
            ),
        ]


class HealingSpirit(ClassSpell):
    rules = SpellRules(
        name="Healing Spirit",
        level=2,
        school=School.CONJURATION,
        classes=(CharacterClass.DRUID, CharacterClass.RANGER),
        casting_time=CastingTime(CastingTimeType.BONUS_ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Xanathar's Guide to Everything",
        description=(
            "You call forth a nature spirit to soothe the wounded. The intangible spirit appears in a space that is a 5-foot cube you can see within range. The spirit looks like a transparent beast or fey (your choice).\n"
            "Until the spell ends, whenever you or a creature you can see moves into the spirit's space for the first time on a turn or starts its turn there, you can cause the spirit to restore 1d6 hit points to that creature (no action required). The spirit can't heal constructs or undead.\n"
            "As a bonus action on your turn, you can move the Spirit up to 30 feet to a space you can see. The spirit can heal a number of times equal to 1 + your spellcasting ability modifier (minimum of twice). After healing that number of times, the spirit disappears.\n"
            "At Higher Levels. When you cast this spell using a spell slot of 3rd level or higher, the healing increases 1d6 for each slot level above 2nd."
        ),
        usage_tags=("heal", "utility", "summon"),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "ee9dbda52a6226d4")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Flavor", "You call forth a nature spirit to soothe the wounded."),
                    (
                        "Spirit",
                        "Intangible, in a space that is a 5-foot cube you can see within range; it looks like a transparent beast or fey (your choice)",
                    ),
                    (
                        "Healing",
                        "Until the spell ends, whenever you or a creature you can see moves into its space for the first time on a turn or starts its turn there, you can cause it to restore 1d6 hit points to that creature (no action required)",
                    ),
                    ("Can't heal", "Constructs or undead"),
                    (
                        "Move",
                        "As a bonus action on your turn, you can move the spirit up to 30 feet to a space you can see",
                    ),
                    (
                        "Uses",
                        "It can heal a number of times equal to 1 + your spellcasting ability modifier (minimum of twice); after that, it disappears",
                    ),
                )
            ),
            Option(
                "At Higher Levels",
                (Facts((("Healing", "+1d6 for each slot level above 2nd"),)),),
            ),
        ]


class HeatMetal(ClassSpell):
    rules = SpellRules(
        name="Heat Metal",
        level=2,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.ARTIFICER, CharacterClass.BARD, CharacterClass.DRUID),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(
            verbal=True, somatic=True, material="a piece of iron and a flame"
        ),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "Choose a manufactured metal object, such as a metal weapon or a suit of Heavy or Medium metal armor, that you can see within range. You cause the object to glow red-hot. Any creature in physical contact with the object takes 2d8 Fire damage when you cast the spell. Until the spell ends, you can take a Bonus Action on each of your later turns to deal this damage again if the object is within range.\n"
            "If a creature is holding or wearing the object and takes the damage from it, the creature must succeed on a Constitution saving throw or drop the object if it can. If it doesn’t drop the object, it has Disadvantage on attack rolls and ability checks until the start of your next turn.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 1d8 for each spell slot level above 2."
        ),
        usage_tags=("control", "damage"),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "608b44ce4aa8ac20")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Flavor", "You cause the object to glow red-hot."),
                    (
                        "Target",
                        "A manufactured metal object you can see within range, such as a metal weapon or a suit of Heavy or Medium metal armor",
                    ),
                    (
                        "Damage",
                        "2d8 Fire damage to any creature in physical contact with the object, when you cast the spell",
                    ),
                    (
                        "Again",
                        "Until the spell ends, you can take a Bonus Action on each of your later turns to deal this damage again if the object is within range",
                    ),
                )
            ),
            Option(
                "Holding or Wearing It",
                (
                    Facts(
                        (
                            (
                                "Trigger",
                                "A creature holding or wearing the object takes its damage",
                            ),
                            ("Save", "Constitution"),
                            ("Failed save", "It drops the object, if it can"),
                            (
                                "Not dropped",
                                "If it doesn't drop the object, it has Disadvantage on attack rolls and ability checks until the start of your next turn",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Damage", "+1d8 for each spell slot level above 2"),)),),
            ),
        ]


class HomunculusServant(ClassSpell):
    rules = SpellRules(
        name="Homunculus Servant",
        level=2,
        school=School.CONJURATION,
        classes=(CharacterClass.ARTIFICER,),
        casting_time=CastingTime(CastingTimeType.HOUR, 1, ritual=True),
        range=Range(RangeType.FOOT, 10),
        components=Components(
            verbal=True, somatic=True, material="a gem worth 100+ GP"
        ),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Eberron - Forge of the Artificer",
        description=(
            "You summon a special homunculus in an unoccupied space within range. This creature uses the Homunculus Servant stat block. If you already have a homunculus from this spell, the homunculus is replaced by the new one. You determine the homunculus’s appearance, such as a mechanical-looking bird, winged vials, or miniature animate cauldrons.\n"
            "Combat The homunculus is an ally to you and your allies. In combat, it shares your Initiative count, but it takes its turn immediately after yours. It obeys your commands (no action required by you). If you don’t issue any, it takes the Dodge action and uses its movement to avoid danger.\n"
            "Using a Higher-Level Spell Slot Use the spell slot’s level for the spell’s level in the stat block."
        ),
        usage_tags=("summon",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "a464974b21a6e8f6")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You summon a special homunculus."),
            Facts(
                (
                    ("Appears", "In an unoccupied space within range"),
                    (
                        "Stat block",
                        "Homunculus Servant (not included in this spell's data)",
                    ),
                    (
                        "Appearance",
                        "You determine it, such as a mechanical-looking bird, winged vials, or miniature animate cauldrons",
                    ),
                    (
                        "One homunculus",
                        "If you already have a homunculus from this spell, it is replaced by the new one",
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
                                "It obeys your commands (no action required by you); if you don't issue any, it takes the Dodge action and uses its movement to avoid danger",
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


class JimsGlowingCoin(ClassSpell):
    rules = SpellRules(
        name="Jim's Glowing Coin",
        level=2,
        school=School.ENCHANTMENT,
        classes=(CharacterClass.WIZARD,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(
            somatic=True,
            material="a coin, 2 gold coins, which is consumed as tax for using the spell",
        ),
        duration=Duration(DurationType.MINUTE, 1),
        source="Acquisitions Inc.",
        description="When you cast the spell, you hurl the coin that is the spell's material component to any spot within range. The coin lights up as if under the effect of a light spell. Each creature of your choice that you can see within 30 feet of the coin must succeed on a Wisdom saving throw or be distracted for the duration. While distracted, a creature has disadvantage on Wisdom (Perception) checks and initiative rolls.",
        usage_tags=("buff", "utility"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "6f51d9bffcc00b4d")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You hurl a glowing coin that distracts creatures around it."),
            Facts(
                (
                    (
                        "Coin",
                        "You hurl the coin that is the spell's material component to any spot within range; it lights up as if under the effect of a light spell",
                    ),
                    (
                        "Targets",
                        "Each creature of your choice that you can see within 30 feet of the coin",
                    ),
                    ("Save", "Wisdom"),
                    (
                        "Failed save",
                        "Distracted for the duration; while distracted, it has Disadvantage on Wisdom (Perception) checks and initiative rolls",
                    ),
                )
            ),
        ]


class KineticJaunt(ClassSpell):
    rules = SpellRules(
        name="Kinetic Jaunt",
        level=2,
        school=School.TRANSMUTATION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.BARD,
            CharacterClass.SORCERER,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.BONUS_ACTION),
        range=Range(RangeType.SELF),
        components=Components(somatic=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Strixhaven: A Curriculum of Chaos",
        description=(
            "You magically empower your movement with dancelike steps, giving yourself the following benefits for the duration:\n"
            "Your walking speed increases by 10 feet.\n"
            "You don't provoke opportunity attacks.\n"
            "You can move through the space of another creature, and it doesn't count as difficult terrain. If you end your turn in another creature's space, you are shunted to the last unoccupied space you occupied, and you take 1d8 force damage."
        ),
        usage_tags=("buff", "control", "damage", "utility"),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "aaf9550565dbd7bc")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You magically empower your movement with dancelike steps.",
                    ),
                    ("Speed", "Your walking speed increases by 10 feet"),
                    ("Opportunity", "You don't provoke opportunity attacks"),
                    (
                        "Moving through",
                        "You can move through the space of another creature, and it doesn't count as Difficult Terrain",
                    ),
                    (
                        "Ending there",
                        "If you end your turn in another creature's space, you are shunted to the last unoccupied space you occupied, and you take 1d8 Force damage",
                    ),
                )
            )
        ]


class Knock(ClassSpell):
    rules = SpellRules(
        name="Knock",
        level=2,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.BARD, CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "Choose an object that you can see within range. The object can be a door, a box, a chest, a set of manacles, a padlock, or another object that contains a mundane or magical means that prevents access.\n"
            "A target that is held shut by a mundane lock or that is stuck or barred becomes unlocked, unstuck, or unbarred. If the object has multiple locks, only one of them is unlocked.\n"
            "If the target is held shut by Arcane Lock , that spell is suppressed for 10 minutes, during which time the target can be opened and closed.\n"
            "When you cast the spell, a loud knock, audible up to 300 feet away, emanates from the target."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "5f73946942554bb9")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You open an object that prevents access."),
            Facts(
                (
                    (
                        "Target",
                        "An object you can see within range: a door, a box, a chest, a set of manacles, a padlock, or another object that contains a mundane or magical means that prevents access",
                    ),
                    (
                        "Mundane",
                        "A target held shut by a mundane lock, or that is stuck or barred, becomes unlocked, unstuck, or unbarred; if it has multiple locks, only one of them is unlocked",
                    ),
                    (
                        "Arcane Lock",
                        "If the target is held shut by Arcane Lock, that spell is suppressed for 10 minutes, during which time the target can be opened and closed",
                    ),
                    (
                        "Noise",
                        "When you cast the spell, a loud knock, audible up to 300 feet away, emanates from the target",
                    ),
                )
            ),
        ]


class LesserRestoration(ClassSpell):
    rules = SpellRules(
        name="Lesser Restoration",
        level=2,
        school=School.ABJURATION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.BARD,
            CharacterClass.CLERIC,
            CharacterClass.DRUID,
            CharacterClass.PALADIN,
            CharacterClass.RANGER,
        ),
        casting_time=CastingTime(CastingTimeType.BONUS_ACTION),
        range=Range(RangeType.TOUCH),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description="You touch a creature and end one condition on it: Blinded, Deafened, Paralyzed, or Poisoned.",
        usage_tags=("heal",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "e8e10e2afa974cca")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You touch a creature and end one condition on it."),
            Facts((("Conditions", "Blinded, Deafened, Paralyzed, or Poisoned"),)),
        ]

    def combat_effects(
        self, character: CharacterView | None = None
    ) -> list[CombatEffect]:
        # "End one condition": a row per condition it can end.
        return [
            CombatEffect(
                name=f"Lesser Restoration: {condition.value}",
                ends_conditions=(condition,),
            )
            for condition in (
                Condition.BLINDED,
                Condition.DEAFENED,
                Condition.PARALYZED,
                Condition.POISONED,
            )
        ]


class Levitate(ClassSpell):
    rules = SpellRules(
        name="Levitate",
        level=2,
        school=School.TRANSMUTATION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.SORCERER,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True, somatic=True, material="a metal spring"),
        duration=Duration(DurationType.MINUTE, 10, concentration=True),
        source="Player's Handbook",
        description=(
            "One creature or loose object of your choice that you can see within range rises vertically up to 20 feet and remains suspended there for the duration. The spell can levitate an object that weighs up to 500 pounds. An unwilling creature that succeeds on a Constitution saving throw is unaffected.\n"
            "The target can move only by pushing or pulling against a fixed object or surface within reach (such as a wall or a ceiling), which allows it to move as if it were climbing. You can change the target’s altitude by up to 20 feet in either direction on your turn. If you are the target, you can move up or down as part of your move. Otherwise, you can take a Magic action to move the target, which must remain within the spell’s range.\n"
            "When the spell ends, the target floats gently to the ground if it is still aloft."
        ),
        usage_tags=("buff",),
        target=FeatureTarget.CREATURE,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "7ae1e8655b6d7876")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "A creature or loose object rises up to 20 feet and stays suspended there for the duration."
            ),
            Facts(
                (
                    (
                        "Target",
                        "One creature or loose object of your choice you can see within range; an object can weigh up to 500 pounds",
                    ),
                    (
                        "Unwilling",
                        "A creature that succeeds on a Constitution save is unaffected",
                    ),
                    (
                        "Its movement",
                        "Only by pushing or pulling against a fixed object or surface within reach (such as a wall or a ceiling), as if climbing",
                    ),
                    (
                        "Altitude",
                        "You can change it by up to 20 feet either way on your turn: as part of your move if you're the target, otherwise as a Magic action (the target must stay within range)",
                    ),
                    (
                        "Spell ends",
                        "The target floats gently to the ground if still aloft",
                    ),
                )
            ),
        ]


class LocateAnimalsOrPlants(ClassSpell):
    rules = SpellRules(
        name="Locate Animals or Plants",
        level=2,
        school=School.DIVINATION,
        classes=(CharacterClass.BARD, CharacterClass.DRUID, CharacterClass.RANGER),
        casting_time=CastingTime(CastingTimeType.ACTION, ritual=True),
        range=Range(RangeType.SELF),
        components=Components(
            verbal=True, somatic=True, material="fur from a bloodhound"
        ),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description="Describe or name a specific kind of Beast, Plant creature, or nonmagical plant. You learn the direction and distance to the closest creature or plant of that kind within 5 miles, if any are present.",
        usage_tags=("utility",),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "7fa746c0ee120e74")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You find the nearest creature or plant of a kind you name."),
            Facts(
                (
                    (
                        "Choose",
                        "Describe or name a specific kind of Beast, Plant creature, or nonmagical plant",
                    ),
                    (
                        "You learn",
                        "The direction and distance to the closest creature or plant of that kind within 5 miles, if any are present",
                    ),
                )
            ),
        ]


class LocateObject(ClassSpell):
    rules = SpellRules(
        name="Locate Object",
        level=2,
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
        components=Components(verbal=True, somatic=True, material="a forked twig"),
        duration=Duration(DurationType.MINUTE, 10, concentration=True),
        source="Player's Handbook",
        description=(
            "Describe or name an object that is familiar to you. You sense the direction to the object’s location if that object is within 1,000 feet of you. If the object is in motion, you know the direction of its movement.\n"
            "The spell can locate a specific object known to you if you have seen it up close—within 30 feet—at least once. Alternatively, the spell can locate the nearest object of a particular kind, such as a certain kind of apparel, jewelry, furniture, tool, or weapon.\n"
            "This spell can’t locate an object if any thickness of lead blocks a direct path between you and the object."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "bec0ceb5ebf9d96e")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You sense the direction to an object familiar to you."),
            Facts(
                (
                    ("Choose", "Describe or name an object that is familiar to you"),
                    (
                        "You sense",
                        "The direction to the object's location, if it is within 1,000 feet of you; if it's in motion, you know the direction of its movement",
                    ),
                    (
                        "Specific object",
                        "The spell can locate a specific object known to you if you have seen it up close (within 30 feet) at least once",
                    ),
                    (
                        "Kind of object",
                        "Alternatively, it can locate the nearest object of a particular kind, such as a certain kind of apparel, jewelry, furniture, tool, or weapon",
                    ),
                    (
                        "Blocked by",
                        "Any thickness of lead blocking a direct path between you and the object",
                    ),
                )
            ),
        ]


class MagicMouth(ClassSpell):
    rules = SpellRules(
        name="Magic Mouth",
        level=2,
        school=School.ILLUSION,
        classes=(CharacterClass.ARTIFICER, CharacterClass.BARD, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.MINUTE, 1, ritual=True),
        range=Range(RangeType.FOOT, 30),
        components=Components(
            verbal=True,
            somatic=True,
            material="jade dust worth 10+ GP, which the spell consumes",
        ),
        duration=Duration(DurationType.UNTIL_DISPELLED),
        source="Player's Handbook",
        description=(
            "You implant a message within an object in range - a message that is uttered when a trigger condition is met. Choose an object that you can see and that isn’t being worn or carried by another creature. Then speak the message, which must be 25 words or fewer, though it can be delivered over as long as 10 minutes. Finally, determine the circumstance that will trigger the spell to deliver your message.\n"
            "When that trigger occurs, a magical mouth appears on the object and recites the message in your voice and at the same volume you spoke. If the object you chose has a mouth or something that looks like a mouth (for example, the mouth of a statue), the magical mouth appears there, so the words appear to come from the object’s mouth. When you cast this spell, you can have the spell end after it delivers its message, or it can remain and repeat its message whenever the trigger occurs.\n"
            "The trigger can be as general or as detailed as you like, though it must be based on visual or audible conditions that occur within 30 feet of the object. For example, you could instruct the mouth to speak when any creature moves within 30 feet of the object or when a silver bell rings within 30 feet of it."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "7fdad6e913652fb2")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You implant a message within an object, uttered when a trigger condition is met."
            ),
            Facts(
                (
                    (
                        "Object",
                        "One you can see within range that isn't being worn or carried by another creature",
                    ),
                    (
                        "Message",
                        "25 words or fewer, though it can be delivered over as long as 10 minutes",
                    ),
                    (
                        "Trigger",
                        "As general or as detailed as you like, but it must be based on visual or audible conditions that occur within 30 feet of the object, such as any creature moving within 30 feet of it, or a silver bell ringing within 30 feet of it",
                    ),
                    (
                        "Delivery",
                        "A magical mouth appears on the object and recites the message in your voice and at the same volume you spoke; if the object has a mouth or something that looks like a mouth (such as a statue's), the magical mouth appears there",
                    ),
                    (
                        "Repeating",
                        "When you cast the spell, choose whether it ends after delivering its message, or remains and repeats its message whenever the trigger occurs",
                    ),
                )
            ),
        ]


class MagicWeapon(ClassSpell):
    rules = SpellRules(
        name="Magic Weapon",
        level=2,
        school=School.TRANSMUTATION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.PALADIN,
            CharacterClass.RANGER,
            CharacterClass.SORCERER,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.BONUS_ACTION),
        range=Range(RangeType.TOUCH),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.HOUR, 1),
        source="Player's Handbook",
        description=(
            "You touch a nonmagical weapon. Until the spell ends, that weapon becomes a magic weapon with a +1 bonus to attack rolls and damage rolls. The spell ends early if you cast it again.\n"
            "Using a Higher-Level Spell Slot. The bonus increases to +2 with a level 3–5 spell slot. The bonus increases to +3 with a level 6+ spell slot."
        ),
        usage_tags=("buff",),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "c36bcf18699931ee")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You touch a nonmagical weapon, and it becomes a magic weapon."),
            Facts(
                (
                    (
                        "Bonus",
                        "+1 to attack rolls and damage rolls, until the spell ends",
                    ),
                    ("Ends early", "If you cast this spell again"),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (
                    Table(
                        ("Slot level", "Bonus"),
                        (("2", "+1"), ("3-5", "+2"), ("6+", "+3")),
                    ),
                ),
            ),
        ]


class MaximilliansEarthenGrasp(ClassSpell):
    rules = SpellRules(
        name="Maximillian's Earthen Grasp",
        level=2,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 30),
        components=Components(
            verbal=True, somatic=True, material="a miniature hand sculpted from clay"
        ),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Xanathar's Guide to Everything",
        description=(
            "You choose a 5-foot-square unoccupied space on the ground that you can see within range. A Medium hand made from compacted soil rises there and reaches for one creature you can see within 5 feet of it. The target must make a Strength saving throw. On a failed save, the target takes 2d6 bludgeoning damage and is restrained for the spell's duration.\n"
            "As an action, you can cause the hand to crush the restrained target, who must make a Strength saving throw. It takes 2d6 bludgeoning damage on a failed save, or half as much damage on a successful one.\n"
            "To break out, the restrained target can use its action to make a Strength check against your spell save DC. On a success, the target escapes and is no longer restrained by the hand.\n"
            "As an action, you can cause the hand to reach for a different creature or to move to a different unoccupied space within range. The hand releases a restrained target if you do either."
        ),
        usage_tags=("control", "damage", "utility"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "f4a42a99f2f34017")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "A Medium hand made from compacted soil rises from the ground and reaches for a creature."
            ),
            Facts(
                (
                    (
                        "Hand",
                        "Rises in a 5-foot-square unoccupied space on the ground that you can see within range",
                    ),
                    ("Target", "One creature you can see within 5 feet of the hand"),
                    ("Save", "Strength"),
                    (
                        "Failed save",
                        "2d6 Bludgeoning damage, and Restrained for the spell's duration",
                    ),
                    ("Successful save", "No effect"),
                )
            ),
            Option(
                "Crush",
                (
                    Facts(
                        (
                            (
                                "Action",
                                "As an action, you can cause the hand to crush the restrained target",
                            ),
                            ("Save", "Strength, made by the restrained target"),
                            ("Failed save", "2d6 Bludgeoning damage"),
                            ("Successful save", "Half as much damage"),
                        )
                    ),
                ),
            ),
            Option(
                "Breaking Out",
                (
                    Facts(
                        (
                            (
                                "Action",
                                "The restrained target can use its action to make a Strength check against your spell save DC",
                            ),
                            (
                                "On a success",
                                "It escapes and is no longer restrained by the hand",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Reach or Move",
                (
                    Facts(
                        (
                            (
                                "Action",
                                "As an action, you can cause the hand to reach for a different creature or to move to a different unoccupied space within range",
                            ),
                            (
                                "Release",
                                "The hand releases a restrained target if you do either",
                            ),
                        )
                    ),
                ),
            ),
        ]


class MelfsAcidArrow(ClassSpell):
    rules = SpellRules(
        name="Melf's Acid Arrow",
        level=2,
        school=School.EVOCATION,
        classes=(CharacterClass.WIZARD,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 90),
        components=Components(
            verbal=True, somatic=True, material="powdered rhubarb leaf"
        ),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "A shimmering green arrow streaks toward a target within range and bursts in a spray of acid. Make a ranged spell attack against the target. On a hit, the target takes 4d4 Acid damage and 2d4 Acid damage at the end of its next turn. On a miss, the arrow splashes the target with acid for half as much of the initial damage only.\n"
            "Using a Higher-Level Spell Slot. The damage (both initial and later) increases by 1d4 for each spell slot level above 2."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "5d7915a10ca62b6d")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "A shimmering green arrow streaks toward a target within range and bursts in a spray of acid.",
                    ),
                    ("Target", "A target within range"),
                    ("Attack", "Ranged spell attack"),
                )
            ),
            Table(
                ("On a hit", "On a miss"),
                (
                    (
                        "4d4 Acid damage, and 2d4 Acid damage at the end of its next turn",
                        "Half as much of the initial damage only",
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
                                "Both the initial and the later damage increase by 1d4 for each spell slot level above 2",
                            ),
                        )
                    ),
                ),
            ),
        ]


class MindSpike(ClassSpell):
    rules = SpellRules(
        name="Mind Spike",
        level=2,
        school=School.DIVINATION,
        classes=(
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 120),
        components=Components(somatic=True),
        duration=Duration(DurationType.HOUR, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "You drive a spike of psionic energy into the mind of one creature you can see within range. The target makes a Wisdom saving throw, taking 3d8 Psychic damage on a failed save or half as much damage on a successful one. On a failed save, you also always know the target’s location until the spell ends, but only while the two of you are on the same plane of existence. While you have this knowledge, the target can’t become hidden from you, and if it has the Invisible condition, it gains no benefit from that condition against you.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 1d8 for each spell slot level above 2."
        ),
        usage_tags=("buff", "damage", "heal"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "5b7032e9a00c5bb8")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You drive a spike of psionic energy into the mind of one creature you can see within range.",
                    ),
                    ("Target", "One creature you can see within range"),
                    ("Save", "Wisdom"),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (
                    (
                        "3d8 Psychic damage, and you track it (below)",
                        "Half as much damage",
                    ),
                ),
            ),
            Option(
                "Tracking",
                (
                    Facts(
                        (
                            (
                                "Location",
                                "On a failed save, you always know the target's location until the spell ends, but only while the two of you are on the same plane of existence",
                            ),
                            (
                                "Hiding",
                                "While you have this knowledge, the target can't become hidden from you",
                            ),
                            (
                                "Invisible",
                                "If it has the Invisible condition, it gains no benefit from that condition against you",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Damage", "+1d8 for each spell slot level above 2"),)),),
            ),
        ]


class MirrorImage(ClassSpell):
    rules = SpellRules(
        name="Mirror Image",
        level=2,
        school=School.ILLUSION,
        classes=(
            CharacterClass.BARD,
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 1),
        source="Player's Handbook",
        description=(
            "Three illusory duplicates of yourself appear in your space. Until the spell ends, the duplicates move with you and mimic your actions, shifting position so it’s impossible to track which image is real.\n"
            "Each time a creature hits you with an attack roll during the spell’s duration, roll a d6 for each of your remaining duplicates. If any of the d6s rolls a 3 or higher, one of the duplicates is hit instead of you, and the duplicate is destroyed. The duplicates otherwise ignore all other damage and effects. The spell ends when all three duplicates are destroyed.\n"
            "A creature is unaffected by this spell if it has the Blinded condition, Blindsight, or Truesight."
        ),
        usage_tags=("buff", "control", "damage"),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "29971b1bc6eef790")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "Three illusory duplicates of you appear in your space. They move with you and mimic your actions, so it's impossible to track which image is real."
            ),
            Facts(
                (
                    (
                        "When hit",
                        "Each time a creature hits you with an attack roll, roll a d6 for each remaining duplicate",
                    ),
                    (
                        "On a 3+",
                        "If any d6 rolls 3 or higher, a duplicate is hit instead of you and is destroyed",
                    ),
                    ("Otherwise", "The duplicates ignore all other damage and effects"),
                    ("Ends", "When all three duplicates are destroyed"),
                    (
                        "Unaffected",
                        "A creature with the Blinded condition, Blindsight, or Truesight",
                    ),
                )
            ),
        ]


class MistyStep(ClassSpell):
    rules = SpellRules(
        name="Misty Step",
        level=2,
        school=School.CONJURATION,
        classes=(
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.BONUS_ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description="Briefly surrounded by silvery mist, you teleport up to 30 feet to an unoccupied space you can see.",
        usage_tags=("buff",),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "e63f246df3f5cdae")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "Briefly surrounded by silvery mist, you teleport up to 30 feet to an unoccupied space you can see.",
                    ),
                    ("Teleport", "Up to 30 feet to an unoccupied space you can see"),
                )
            )
        ]

    def combat_effects(
        self, character: CharacterView | None = None
    ) -> list[CombatEffect]:
        return []


class NathairsMischief(ClassSpell):
    rules = SpellRules(
        name="Nathair's Mischief",
        level=2,
        school=School.ILLUSION,
        classes=(CharacterClass.BARD, CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(
            somatic=True, material="a piece of crust from an apple pie"
        ),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Fizban's Treasury of Dragons",
        description="You fill a 20-foot cube you can see within range with fey and draconic magic. Roll on the Mischievous Surge table to determine the magical effect produced, and roll again at the start of each of your turns until the spell ends. You can move the cube up to 10 feet before you roll.",
        usage_tags=("utility",),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "126bd708d10b3631")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You fill a 20-foot cube you can see within range with fey and draconic magic.",
                    ),
                    ("Area", "A 20-foot cube you can see within range"),
                    (
                        "Effect",
                        "Roll on the Mischievous Surge table to determine the magical effect produced, and roll again at the start of each of your turns until the spell ends",
                    ),
                    ("Moving", "You can move the cube up to 10 feet before you roll"),
                    (
                        "Table",
                        "The Mischievous Surge table isn't included in this spell's data",
                    ),
                )
            )
        ]


class NystulsMagicAura(ClassSpell):
    rules = SpellRules(
        name="Nystul's Magic Aura",
        level=2,
        school=School.ILLUSION,
        classes=(CharacterClass.WIZARD,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.TOUCH),
        components=Components(
            verbal=True, somatic=True, material="a small square of silk"
        ),
        duration=Duration(DurationType.HOUR, 24),
        source="Player's Handbook",
        description=(
            "With a touch, you place an illusion on a willing creature or an object that isn’t being worn or carried. A creature gains the Mask effect below, and an object gains the False Aura effect below. The effect lasts for the duration. If you cast the spell on the same target every day for 30 days, the illusion lasts until dispelled.\n"
            "Mask (Creature). Choose a creature type other than the target’s actual type. Spells and other magical effects treat the target as if it were a creature of the chosen type.\n"
            "False Aura (Object). You change the way the target appears to spells and magical effects that detect magical auras, such as Detect Magic . You can make a nonmagical object appear magical, make a magic item appear nonmagical, or change the object’s aura so that it appears to belong to a school of magic you choose."
        ),
        usage_tags=("buff",),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "53393cfca9a67a1f")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "With a touch, you place an illusion on a willing creature or an object that isn't being worn or carried."
            ),
            Facts(
                (
                    (
                        "Permanent",
                        "If you cast the spell on the same target every day for 30 days, the illusion lasts until dispelled",
                    ),
                )
            ),
            Option(
                "Mask (Creature)",
                (
                    Facts(
                        (
                            (
                                "Effect",
                                "Choose a creature type other than the target's actual type; spells and other magical effects treat the target as if it were a creature of the chosen type",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "False Aura (Object)",
                (
                    Facts(
                        (
                            (
                                "Effect",
                                "You change the way the target appears to spells and magical effects that detect magical auras, such as Detect Magic",
                            ),
                            (
                                "Options",
                                "Make a nonmagical object appear magical, make a magic item appear nonmagical, or change the object's aura so that it appears to belong to a school of magic you choose",
                            ),
                        )
                    ),
                ),
            ),
        ]


class PassWithoutTrace(ClassSpell):
    rules = SpellRules(
        name="Pass without Trace",
        level=2,
        school=School.ABJURATION,
        classes=(CharacterClass.DRUID, CharacterClass.RANGER),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(
            verbal=True, somatic=True, material="ashes from burned mistletoe"
        ),
        duration=Duration(DurationType.HOUR, 1, concentration=True),
        source="Player's Handbook",
        description="You radiate a concealing aura in a 30-foot Emanation for the duration. While in the aura, you and each creature you choose have a +10 bonus to Dexterity (Stealth) checks and leave no tracks.",
        usage_tags=("buff",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "607a07f6e6d5cea0")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You radiate a concealing aura for the duration."),
            Facts(
                (
                    ("Area", "30-foot Emanation"),
                    (
                        "Effect",
                        "While in the aura, you and each creature you choose have a +10 bonus to Dexterity (Stealth) checks and leave no tracks",
                    ),
                )
            ),
        ]


class PhantasmalForce(ClassSpell):
    rules = SpellRules(
        name="Phantasmal Force",
        level=2,
        school=School.ILLUSION,
        classes=(CharacterClass.BARD, CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True, somatic=True, material="a bit of fleece"),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "You attempt to craft an illusion in the mind of a creature you can see within range. The target makes an Intelligence saving throw. On a failed save, you create a phantasmal object, creature, or other phenomenon that is no larger than a 10-foot Cube and that is perceivable only to the target for the duration. The phantasm includes sound, temperature, and other stimuli.\n"
            "The target can take a Study action to examine the phantasm with an Intelligence (Investigation) check against your spell save DC. If the check succeeds, the target realizes that the phantasm is an illusion, and the spell ends.\n"
            "While affected by the spell, the target treats the phantasm as if it were real and rationalizes any illogical outcomes from interacting with it. For example, if the target steps through a phantasmal bridge and survives the fall, it believes the bridge exists and something else caused it to fall.\n"
            "An affected target can even take damage from the illusion if the phantasm represents a dangerous creature or hazard. On each of your turns, such a phantasm can deal 2d8 Psychic damage to the target if it is in the phantasm’s area or within 5 feet of the phantasm. The target perceives the damage as a type appropriate to the illusion."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "75fe37c2333cc44b")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You craft an illusion in a creature's mind that only it can perceive, and which can even hurt it."
            ),
            Facts(
                (
                    ("Target", "A creature you can see within range"),
                    ("Save", "Intelligence"),
                    (
                        "Failed save",
                        "A phantasmal object, creature, or other phenomenon no larger than a 10-foot Cube, perceivable only to the target, for the duration",
                    ),
                    ("Senses", "It includes sound, temperature, and other stimuli"),
                )
            ),
            Facts(
                (
                    (
                        "Belief",
                        "The target treats it as real and rationalizes illogical outcomes: stepping through a phantasmal bridge and surviving the fall, it believes something else made it fall",
                    ),
                    (
                        "Damage",
                        "If the phantasm represents a dangerous creature or hazard, it can deal 2d8 Psychic damage to the target on each of your turns if the target is in the phantasm's area or within 5 feet of it",
                    ),
                    (
                        "Damage type",
                        "The target perceives the damage as a type appropriate to the illusion",
                    ),
                    (
                        "Seeing through",
                        "The target can take the Study action to make an Intelligence (Investigation) check against your spell save DC; on a success, it realizes it's an illusion, and the spell ends",
                    ),
                )
            ),
        ]


class PinkySwear(ClassSpell):
    rules = SpellRules(
        name="Pinky Swear",
        level=2,
        school=School.ABJURATION,
        classes=(CharacterClass.BARD, CharacterClass.PALADIN, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.TOUCH),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.HOUR, 24),
        source="D&D Beyond Drops - September 2026",
        description=(
            "You touch a creature and speak a promise of no more than 25 words that you vow to keep.\n"
            "For the duration of the spell, if you knowingly break the promise, the target immediately knows of your breach if it is within 1 mile, and you start burning, taking 1 Fire damage at the start of each of your turns instead of the normal burning damage."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.CREATURE,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "ff8a4ceae475b658")


class PrayerOfHealing(ClassSpell):
    rules = SpellRules(
        name="Prayer of Healing",
        level=2,
        school=School.ABJURATION,
        classes=(CharacterClass.CLERIC, CharacterClass.PALADIN),
        casting_time=CastingTime(CastingTimeType.MINUTE, 10),
        range=Range(RangeType.FOOT, 30),
        components=Components(verbal=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "Up to five creatures of your choice who remain within range for the spell’s entire casting gain the benefits of a Short Rest and also regain 2d8 Hit Points. A creature can’t be affected by this spell again until that creature finishes a Long Rest.\n"
            "Using a Higher-Level Spell Slot. The healing increases by 1d8 for each spell slot level above 2."
        ),
        usage_tags=("heal",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "d7e4455bf8976322")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("Up to five creatures recover as if from a Short Rest."),
            Facts(
                (
                    (
                        "Targets",
                        "Up to five creatures of your choice who remain within range for the spell's entire casting",
                    ),
                    (
                        "Effect",
                        "They gain the benefits of a Short Rest and also regain 2d8 Hit Points",
                    ),
                    (
                        "Limit",
                        "A creature can't be affected by this spell again until that creature finishes a Long Rest",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Healing", "+1d8 for each spell slot level above 2"),)),),
            ),
        ]


class ProtectionFromPoison(ClassSpell):
    rules = SpellRules(
        name="Protection from Poison",
        level=2,
        school=School.ABJURATION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.CLERIC,
            CharacterClass.DRUID,
            CharacterClass.PALADIN,
            CharacterClass.RANGER,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.TOUCH),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.HOUR, 1),
        source="Player's Handbook",
        description="You touch a creature and end the Poisoned condition on it. For the duration, the target has Advantage on saving throws to avoid or end the Poisoned condition, and it has Resistance to Poison damage.",
        usage_tags=("buff",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "79678c22a2e39c5f")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You touch a creature and end the Poisoned condition on it."),
            Facts(
                (
                    (
                        "Saves",
                        "For the duration, Advantage on saving throws to avoid or end the Poisoned condition",
                    ),
                    ("Resistance", "Resistance to Poison damage for the duration"),
                )
            ),
        ]


class Pyrotechnics(ClassSpell):
    rules = SpellRules(
        name="Pyrotechnics",
        level=2,
        school=School.TRANSMUTATION,
        classes=(
            CharacterClass.BARD,
            CharacterClass.SORCERER,
            CharacterClass.WIZARD,
            CharacterClass.ARTIFICER,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Xanathar's Guide to Everything",
        description=(
            "Choose an area of flame that you can see and that can fit within a 5-foot cube within range. You can extinguish the fire in that area, and you create either fireworks or smoke.\n"
            "Fireworks. The target explodes with a dazzling display of colors. Each creature within 10 feet of the target must succeed on a Constitution saving throw or become blinded until the end of your next turn.\n"
            "Smoke. Thick black smoke spreads out from the target in a 20-foot radius, moving around corners. The area of the smoke is heavily obscured. The smoke persists for 1 minute or until a strong wind disperses it."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "69035e49d7126703")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You transform a flame into fireworks or smoke."),
            Facts(
                (
                    (
                        "Target",
                        "An area of flame that you can see and that can fit within a 5-foot cube within range",
                    ),
                    ("Extinguish", "You can extinguish the fire in that area"),
                )
            ),
            Option(
                "Fireworks",
                (
                    Facts(
                        (
                            (
                                "Effect",
                                "The target explodes with a dazzling display of colors",
                            ),
                            ("Targets", "Each creature within 10 feet of the target"),
                            ("Save", "Constitution"),
                            ("Failed save", "Blinded until the end of your next turn"),
                        )
                    ),
                ),
            ),
            Option(
                "Smoke",
                (
                    Facts(
                        (
                            (
                                "Area",
                                "Thick black smoke spreads out from the target in a 20-foot radius, moving around corners",
                            ),
                            ("Visibility", "The area of the smoke is heavily obscured"),
                            ("Lasts", "1 minute, or until a strong wind disperses it"),
                        )
                    ),
                ),
            ),
        ]


class RayOfEnfeeblement(ClassSpell):
    rules = SpellRules(
        name="Ray of Enfeeblement",
        level=2,
        school=School.NECROMANCY,
        classes=(CharacterClass.WARLOCK, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "A beam of enervating energy shoots from you toward a creature within range. The target must make a Constitution saving throw. On a successful save, the target has Disadvantage on the next attack roll it makes until the start of your next turn.\n"
            "On a failed save, the target has Disadvantage on Strength-based D20 Tests for the duration. During that time, it also subtracts 1d8 from all its damage rolls. The target repeats the save at the end of each of its turns, ending the spell on a success."
        ),
        usage_tags=("buff",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "ff858b782bebfe1b")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "A beam of enervating energy shoots from you toward a creature within range.",
                    ),
                    ("Target", "A creature within range"),
                    ("Save", "Constitution"),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (
                    (
                        "For the duration, Disadvantage on Strength-based D20 Tests, and it subtracts 1d8 from all its damage rolls",
                        "Disadvantage on the next attack roll it makes until the start of your next turn",
                    ),
                ),
            ),
            Facts(
                (
                    (
                        "Repeat save",
                        "On a failed save, the target repeats the save at the end of each of its turns, ending the spell on a success",
                    ),
                )
            ),
        ]


class RimesBindingIce(ClassSpell):
    rules = SpellRules(
        name="Rime's Binding Ice",
        level=2,
        school=School.EVOCATION,
        classes=(CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF, area=Area(30, AreaShape.CONE)),
        components=Components(somatic=True, material="a vial of meltwater"),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Fizban's Treasury of Dragons",
        description=(
            "A burst of cold energy emanates from you in a 30-foot cone. Each creature in that area must make a Constitution saving throw. On a failed save, a creature takes 3d8 cold damage and is hindered by ice formations for 1 minute, or until it or another creature within reach of it uses an action to break away the ice. A creature hindered by ice has its speed reduced to 0. On a successful save, a creature takes half as much damage and isn't hindered by ice.\n"
            "At Higher Levels. When you cast this spell using a spell slot of 3rd level or higher, increase the cold damage by 1d8 for each slot level above 2nd."
        ),
        usage_tags=("control", "damage"),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "3b36f53886801278")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "A burst of cold energy emanates from you in a 30-foot cone.",
                    ),
                    ("Area", "30-foot cone"),
                    ("Save", "Constitution, made by each creature in the area"),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (
                    (
                        "3d8 Cold damage, and hindered by ice formations for 1 minute, or until it or another creature within reach of it uses an action to break away the ice",
                        "Half as much damage, and not hindered by ice",
                    ),
                ),
            ),
            Facts(
                (("Hindered", "A creature hindered by ice has its speed reduced to 0"),)
            ),
            Option(
                "At Higher Levels",
                (Facts((("Cold damage", "+1d8 for each slot level above 2nd"),)),),
            ),
        ]


class RopeTrick(ClassSpell):
    rules = SpellRules(
        name="Rope Trick",
        level=2,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.ARTIFICER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.TOUCH),
        components=Components(verbal=True, somatic=True, material="a segment of rope"),
        duration=Duration(DurationType.HOUR, 1),
        source="Player's Handbook",
        description=(
            "You touch a rope. One end of it hovers upward until the rope hangs perpendicular to the ground or the rope reaches a ceiling. At the rope’s upper end, an Invisible 3-foot-by-5-foot portal opens to an extradimensional space that lasts until the spell ends. That space can be reached by climbing the rope, which can be pulled into or dropped out of it.\n"
            "The space can hold up to eight Medium or smaller creatures. Attacks, spells, and other effects can’t pass into or out of the space, but creatures inside it can see through the portal. Anything inside the space drops out when the spell ends."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "c1d957e49fa897e8")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You touch a rope, which rises to an Invisible portal into an extradimensional space."
            ),
            Facts(
                (
                    (
                        "Rope",
                        "One end hovers upward until the rope hangs perpendicular to the ground or reaches a ceiling",
                    ),
                    (
                        "Portal",
                        "At the rope's upper end, an Invisible 3-foot-by-5-foot portal opens to an extradimensional space that lasts until the spell ends",
                    ),
                    (
                        "Access",
                        "The space can be reached by climbing the rope, which can be pulled into or dropped out of it",
                    ),
                    ("Capacity", "Up to eight Medium or smaller creatures"),
                    (
                        "Sealed",
                        "Attacks, spells, and other effects can't pass into or out of the space, but creatures inside it can see through the portal",
                    ),
                    ("Spell ends", "Anything inside the space drops out"),
                )
            ),
        ]


class SearingOrb(ClassSpell):
    rules = SpellRules(
        name="Searing Orb",
        level=2,
        school=School.EVOCATION,
        classes=(CharacterClass.CLERIC, CharacterClass.PALADIN),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(
            somatic=True, material="Metallic flakes and a pinch of phosphorus"
        ),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="D&D Beyond Drops - June 2026",
        description=(
            "You create and hurl a pulsing orb of energy at one creature within range. Make a ranged spell attack against the target. On a hit, the target takes 3d4 Radiant damage. Hit or miss, the orb then explodes in a flash of light. The target and each creature within 10 feet of it make a Constitution saving throw. On a failed save, a creature has the Blinded condition until the end of its next turn.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 1d4 for each spell slot level above 2."
        ),
        usage_tags=("control", "damage"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "1cb060299f20996f")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You create and hurl a pulsing orb of energy at one creature within range. Hit or miss, the orb then explodes in a flash of light.",
                    ),
                    ("Target", "One creature within range"),
                    ("Attack", "Ranged spell attack"),
                    ("On a hit", "3d4 Radiant damage"),
                )
            ),
            Option(
                "Explosion",
                (
                    Facts(
                        (
                            ("When", "Hit or miss, the orb then explodes"),
                            (
                                "Targets",
                                "The target and each creature within 10 feet of it",
                            ),
                            ("Save", "Constitution"),
                            ("Failed save", "Blinded until the end of its next turn"),
                            ("Successful save", "No effect"),
                        )
                    ),
                ),
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Damage", "+1d4 for each spell slot level above 2"),)),),
            ),
        ]


class SeeInvisibility(ClassSpell):
    rules = SpellRules(
        name="See Invisibility",
        level=2,
        school=School.DIVINATION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.BARD,
            CharacterClass.SORCERER,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True, material="a pinch of talc"),
        duration=Duration(DurationType.HOUR, 1),
        source="Player's Handbook",
        description="For the duration, you see creatures and objects that have the Invisible condition as if they were visible, and you can see into the Ethereal Plane. Creatures and objects there appear ghostly.",
        usage_tags=("buff",),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "8d51b92ea47a3515")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "For the duration, you see the invisible and the Ethereal Plane."
            ),
            Facts(
                (
                    (
                        "Invisible",
                        "You see creatures and objects that have the Invisible condition as if they were visible",
                    ),
                    (
                        "Ethereal Plane",
                        "You can see into it; creatures and objects there appear ghostly",
                    ),
                )
            ),
        ]

    def combat_effects(
        self, character: CharacterView | None = None
    ) -> list[CombatEffect]:
        return [
            CombatEffect(
                conditions=(CombatCondition("See Invisibility"),),
                targets_self=True,
                notes=(
                    "You see creatures and objects with the Invisible condition as if they were visible.",
                ),
            )
        ]


class ShadowBlade(ClassSpell):
    rules = SpellRules(
        name="Shadow Blade",
        level=2,
        school=School.ILLUSION,
        classes=(
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.BONUS_ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Xanathar's Guide to Everything",
        description=(
            "You weave together threads of shadow to create a sword of solidified gloom in your hand. This magic sword lasts until the spell ends. It counts as a simple melee weapon with which you are proficient. It deals 2d8 psychic damage on a hit and has the finesse, light, and thrown properties (range 20/60). In addition, when you use the sword to attack a target that is in dim light or darkness, you make the attack roll with advantage.\n"
            "If you drop the weapon or throw it, it dissipates at the end of the turn. Thereafter, while the spell persists, you can use a bonus action to cause the sword to reappear in your hand.\n"
            "At Higher Levels. When you cast this spell using a 3rd- or 4th-level spell slot, the damage increases to 3d8. When you cast it using a 5th- or 6th-level spell slot, the damage increases to 4d8. When you cast it using a spell slot of 7th level or higher, the damage increases to 5d8."
        ),
        usage_tags=("damage", "utility"),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "dda571028ab20538")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You weave together threads of shadow to create a sword of solidified gloom in your hand.",
                    ),
                    (
                        "Weapon",
                        "A magic sword that lasts until the spell ends; it counts as a simple melee weapon with which you are proficient",
                    ),
                    ("Damage", "2d8 Psychic damage on a hit"),
                    ("Properties", "Finesse, light, and thrown (range 20/60)"),
                    (
                        "Advantage",
                        "When you use the sword to attack a target that is in dim light or darkness, you make the attack roll with Advantage",
                    ),
                    (
                        "Dropped or thrown",
                        "It dissipates at the end of the turn; thereafter, while the spell persists, you can use a bonus action to cause it to reappear in your hand",
                    ),
                )
            ),
            Option(
                "At Higher Levels",
                (
                    Table(
                        ("Slot level", "Damage"),
                        (
                            ("2nd", "2d8"),
                            ("3rd-4th", "3d8"),
                            ("5th-6th", "4d8"),
                            ("7th+", "5d8"),
                        ),
                    ),
                ),
            ),
        ]


class ShiningSmite(ClassSpell):
    rules = SpellRules(
        name="Shining Smite",
        level=2,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.PALADIN,),
        casting_time=CastingTime(
            CastingTimeType.BONUS_ACTION,
            trigger="which you take immediately after hitting a creature with a Melee weapon or an Unarmed Strike",
        ),
        range=Range(RangeType.SELF),
        components=Components(verbal=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "The target hit by the strike takes an extra 2d6 Radiant damage from the attack. Until the spell ends, the target sheds Bright Light in a 5-foot radius, attack rolls against it have Advantage, and it can’t benefit from the Invisible condition.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 1d6 for each spell slot level above 2."
        ),
        usage_tags=("damage", "heal"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "aa6de4b69c066400")

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
                        "The target takes an extra 2d6 Radiant damage from the attack",
                    ),
                    (
                        "Until it ends",
                        "The target sheds Bright Light in a 5-foot radius, attack rolls against it have Advantage, and it can't benefit from the Invisible condition",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Damage", "+1d6 for each spell slot level above 2"),)),),
            ),
        ]


class Silence(ClassSpell):
    rules = SpellRules(
        name="Silence",
        level=2,
        school=School.ILLUSION,
        classes=(CharacterClass.BARD, CharacterClass.CLERIC, CharacterClass.RANGER),
        casting_time=CastingTime(CastingTimeType.ACTION, ritual=True),
        range=Range(RangeType.FOOT, 120),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 10, concentration=True),
        source="Player's Handbook",
        description="For the duration, no sound can be created within or pass through a 20-foot-radius Sphere centered on a point you choose within range. Any creature or object entirely inside the Sphere has Immunity to Thunder damage, and creatures have the Deafened condition while entirely inside it. Casting a spell that includes a Verbal component is impossible there.",
        usage_tags=("control",),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "218da00b7cebf64a")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "For the duration, no sound can be created within or pass through an area."
            ),
            Facts(
                (
                    (
                        "Area",
                        "20-foot-radius Sphere centered on a point you choose within range",
                    ),
                    (
                        "Thunder",
                        "Any creature or object entirely inside the Sphere has Immunity to Thunder damage",
                    ),
                    (
                        "Deafened",
                        "Creatures have the Deafened condition while entirely inside it",
                    ),
                    (
                        "Spells",
                        "Casting a spell that includes a Verbal component is impossible there",
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
                    CombatCondition(Condition.DEAFENED),
                    CombatCondition(
                        "Silence", modifiers=(DamageImmunity((DamageType.THUNDER,)),)
                    ),
                ),
                notes=(
                    "Each creature entirely inside the 20-foot-radius Sphere: take Deafened and the Silence badge (Immunity to Thunder damage) off when it leaves.",
                    "Inside, objects have Immunity to Thunder damage too, and no spell with a Verbal component can be cast.",
                ),
            )
        ]


class Skywrite(ClassSpell):
    rules = SpellRules(
        name="Skywrite",
        level=2,
        school=School.TRANSMUTATION,
        classes=(
            CharacterClass.BARD,
            CharacterClass.DRUID,
            CharacterClass.WIZARD,
            CharacterClass.ARTIFICER,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION, ritual=True),
        range=Range(RangeType.SIGHT),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.DAY, 1, concentration=True),
        source="Xanathar's Guide to Everything",
        description="You cause up to ten words to form in a part of the sky you can see. The words appear to be made of cloud and remain in place for the spell's duration. The words dissipate when the spell ends. A strong wind can disperse the clouds and end the spell early.",
        usage_tags=("utility",),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "e3d8d75d0d4188dc")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You cause words to form in the sky."),
            Facts(
                (
                    ("Words", "Up to ten words, in a part of the sky you can see"),
                    (
                        "Appearance",
                        "Made of cloud, remaining in place for the spell's duration",
                    ),
                    (
                        "Ends",
                        "The words dissipate when the spell ends; a strong wind can disperse the clouds and end the spell early",
                    ),
                )
            ),
        ]


class SnillocsSnowballSwarm(ClassSpell):
    rules = SpellRules(
        name="Snilloc's Snowball Swarm",
        level=2,
        school=School.EVOCATION,
        classes=(CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 90),
        components=Components(
            verbal=True,
            somatic=True,
            material="a piece of ice or a small white rock chip",
        ),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Xanathar's Guide to Everything",
        description=(
            "A flurry of magic snowballs erupts from a point you choose within range. Each creature in a 5-foot-radius sphere centered on that point must make a Dexterity saving throw. A creature takes 3d6 cold damage on a failed save, or half as much damage on a successful one.\n"
            "At Higher Levels. When you cast this spell using a spell slot of 3rd level or higher, the damage increases by 1d6 for each slot level above 2nd."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "b2d91320f462223d")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "A flurry of magic snowballs erupts from a point you choose within range.",
                    ),
                    (
                        "Area",
                        "5-foot-radius sphere centered on a point you choose within range",
                    ),
                    ("Save", "Dexterity, made by each creature in the sphere"),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (("3d6 Cold damage", "Half as much damage"),),
            ),
            Option(
                "At Higher Levels",
                (Facts((("Damage", "+1d6 for each slot level above 2nd"),)),),
            ),
        ]


class SpiderClimb(ClassSpell):
    rules = SpellRules(
        name="Spider Climb",
        level=2,
        school=School.TRANSMUTATION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.TOUCH),
        components=Components(
            verbal=True, somatic=True, material="a drop of bitumen and a spider"
        ),
        duration=Duration(DurationType.HOUR, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "Until the spell ends, one willing creature you touch gains the ability to move up, down, and across vertical surfaces and along ceilings, while leaving its hands free. The target also gains a Climb Speed equal to its Speed.\n"
            "Using a Higher-Level Spell Slot. You can target one additional creature for each spell slot level above 2."
        ),
        usage_tags=("buff",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "9fbb1fd0fb15b31d")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Target", "One willing creature you touch"),
                    (
                        "Climbing",
                        "Until the spell ends, it can move up, down, and across vertical surfaces and along ceilings, while leaving its hands free",
                    ),
                    ("Climb Speed", "Equal to its Speed"),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (
                    Facts(
                        (("Targets", "+1 creature for each spell slot level above 2"),)
                    ),
                ),
            ),
        ]


class SprayOfCards(ClassSpell):
    rules = SpellRules(
        name="Spray of Cards",
        level=2,
        school=School.CONJURATION,
        classes=(
            CharacterClass.BARD,
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF, area=Area(15, AreaShape.CONE)),
        components=Components(verbal=True, somatic=True, material="a deck of cards"),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="The Book of Many Things",
        description=(
            "You spray a 15-foot cone of spectral cards. Each creature in that area must make a Dexterity saving throw. On a failed save, a creature takes 2d10 force damage and has the blinded condition until the end of its next turn. On a successful save, a creature takes half as much damage only.\n"
            "At Higher Levels. When you cast this spell using a spell slot of 3rd level or higher, the damage increases by 1d10 for each slot level above 2nd."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "d35379f9c183c642")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Flavor", "You spray a 15-foot cone of spectral cards."),
                    ("Area", "15-foot cone"),
                    ("Save", "Dexterity, made by each creature in the area"),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (
                    (
                        "2d10 Force damage, and Blinded until the end of its next turn",
                        "Half as much damage only",
                    ),
                ),
            ),
            Option(
                "At Higher Levels",
                (Facts((("Damage", "+1d10 for each slot level above 2nd"),)),),
            ),
        ]


class SummonBeast(ClassSpell):
    rules = SpellRules(
        name="Summon Beast",
        level=2,
        school=School.CONJURATION,
        classes=(CharacterClass.DRUID, CharacterClass.RANGER),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 90),
        components=Components(
            verbal=True,
            somatic=True,
            material="a feather, tuft of fur, and fish tail inside a gilded acorn worth 200+ GP",
        ),
        duration=Duration(DurationType.HOUR, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "You call forth a bestial spirit. It manifests in an unoccupied space that you can see within range and uses the Bestial Spirit stat block. When you cast the spell, choose an environment: Air, Land, or Water. The creature resembles an animal of your choice that is native to the chosen environment, which determines certain details in its stat block. The creature disappears when it drops to 0 Hit Points or when the spell ends.\n"
            "The creature is an ally to you and your allies. In combat, the creature shares your Initiative count, but it takes its turn immediately after yours. It obeys your verbal commands (no action required by you). If you don’t issue any, it takes the Dodge action and uses its movement to avoid danger.\n"
            "Using a Higher-Level Spell Slot. Use the spell slot’s level for the spell’s level in the stat block."
        ),
        usage_tags=("summon",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "ba64f9f3bea0a10d")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You call forth a bestial spirit."),
            Facts(
                (
                    ("Appears", "In an unoccupied space that you can see within range"),
                    (
                        "Environment",
                        "Air, Land, or Water, chosen when you cast the spell; the creature resembles an animal of your choice native to that environment, which determines certain details in its stat block",
                    ),
                    ("Stat block", "Bestial Spirit (below)"),
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
                "Bestial Spirit",
                (
                    Facts(
                        (
                            ("Type", "Small Beast"),
                            ("AC", "11 + the spell's level"),
                            (
                                "Hit Points",
                                "20 (Air only) or 30 (Land and Water only) + 5 for each spell level above 2",
                            ),
                            (
                                "Speed",
                                "30 ft., Climb 30 ft. (Land only), Fly 60 ft. (Air only), Swim 30 ft. (Water only)",
                            ),
                            (
                                "Abilities",
                                "Str 18, Dex 11, Con 16, Int 4, Wis 14, Cha 5",
                            ),
                            ("Senses", "Darkvision 60 ft., Passive Perception 12"),
                            ("Languages", "Understands the languages you know"),
                            (
                                "Flyby",
                                "Air only. The spirit doesn't provoke Opportunity Attacks when it flies out of an enemy's reach",
                            ),
                            (
                                "Pack Tactics",
                                "Land and Water only. The spirit has Advantage on an attack roll against a creature if at least one of the spirit's allies is within 5 feet of the creature and the ally doesn't have the Incapacitated condition",
                            ),
                            (
                                "Water Breathing",
                                "Water only. The spirit can breathe only underwater",
                            ),
                            (
                                "Multiattack",
                                "The spirit makes a number of Rend attacks equal to half this spell's level (round down)",
                            ),
                            (
                                "Rend",
                                "Melee Attack Roll: Bonus equals your spell attack modifier, reach 5 ft. Hit: 1d8 + 4 + the spell's level Piercing damage",
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


class TashasMindWhip(ClassSpell):
    rules = SpellRules(
        name="Tasha's Mind Whip",
        level=2,
        school=School.ENCHANTMENT,
        classes=(CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 90),
        components=Components(verbal=True),
        duration=Duration(DurationType.ROUND, 1),
        source="Tasha's Cauldron of Everything",
        description=(
            "You psychically lash out at one creature you can see within range. The target must make an Intelligence saving throw. On a failed save, the target takes 3d6 psychic damage, and it can't take a reaction until the end of its next turn. Moreover, on its next turn, it must choose whether it gets a move, an action, or a bonus action; it gets only one of the three. On a successful save, the target takes half as much damage and suffers none of the spell's other effects.\n"
            "At Higher Levels. When you cast this spell using a spell slot of 3rd level or higher, you can target one additional creature for each slot level above 2nd. The creatures must be within 30 feet of each other when you target them."
        ),
        usage_tags=("control", "damage", "utility"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "eb56d2f68419bdc8")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You psychically lash out at one creature you can see within range.",
                    ),
                    ("Target", "One creature you can see within range"),
                    ("Save", "Intelligence"),
                )
            ),
            Option(
                "Failed Save",
                (
                    Facts(
                        (
                            ("Damage", "3d6 Psychic damage"),
                            (
                                "Reaction",
                                "It can't take a reaction until the end of its next turn",
                            ),
                            (
                                "Its next turn",
                                "It must choose whether it gets a move, an action, or a bonus action; it gets only one of the three",
                            ),
                        )
                    ),
                ),
            ),
            Facts(
                (
                    (
                        "Successful save",
                        "Half as much damage, and none of the spell's other effects",
                    ),
                )
            ),
            Option(
                "At Higher Levels",
                (
                    Facts(
                        (
                            ("Targets", "+1 creature for each slot level above 2nd"),
                            (
                                "Spacing",
                                "The creatures must be within 30 feet of each other when you target them",
                            ),
                        )
                    ),
                ),
            ),
        ]


class TortoiseShell(ClassSpell):
    rules = SpellRules(
        name="Tortoise Shell",
        level=2,
        school=School.ABJURATION,
        classes=(CharacterClass.ARTIFICER, CharacterClass.DRUID, CharacterClass.RANGER),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.TOUCH),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="D&D Beyond Drops - June 2026",
        description="You touch a willing creature. Until the spell ends, the target’s skin hardens into a tortoise shell while it remains in place, and the target gains a +3 bonus to AC. If the target moves using its action, Bonus Action, Reaction, or movement, the bonus becomes +1 instead until the start of its next turn.",
        usage_tags=("buff",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "ea8dc38123b45510")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Flavor", "The target's skin hardens into a tortoise shell."),
                    ("Target", "A willing creature you touch"),
                    ("AC", "+3 bonus until the spell ends"),
                    (
                        "Moving",
                        "If the target moves, the bonus becomes +1 instead until the start of its next turn",
                    ),
                )
            )
        ]


class UncertainFooting(ClassSpell):
    rules = SpellRules(
        name="Uncertain Footing",
        level=2,
        school=School.ILLUSION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.BARD,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 120),
        components=Components(verbal=True, somatic=True, material="a distorted lens"),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Arcana Unleashed",
        description="You create illusory obstacles such as rocks or spikes in an attempt to confuse up to three creatures you can see within range, affecting their ability to move. Each target makes an Intelligence saving throw. On a failed save, a target’s Speed is halved, and it can’t take the Dash action. A hampered target repeats the save at the end of each of its turns, ending the spell on itself on a success.",
        usage_tags=("control",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "b73259efec1b1537")


class VortexWarp(ClassSpell):
    rules = SpellRules(
        name="Vortex Warp",
        level=2,
        school=School.CONJURATION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.SORCERER,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 90),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Strixhaven: A Curriculum of Chaos",
        description=(
            "You magically twist space around another creature you can see within range. The target must succeed on a Constitution saving throw (the target can choose to fail), or the target is teleported to an unoccupied space of your choice that you can see within range. The chosen space must be on a surface or in a liquid that can support the target without the target having to squeeze.\n"
            "At Higher Levels. When you cast this spell using a spell slot of 3rd level or higher, the range of the spell increases by 30 feet for each slot level above 2nd."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "2d202f1d710e9dba")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You magically twist space around another creature you can see within range.",
                    ),
                    ("Target", "Another creature you can see within range"),
                    ("Save", "Constitution; the target can choose to fail"),
                    (
                        "Failed save",
                        "Teleported to an unoccupied space of your choice that you can see within range",
                    ),
                    (
                        "Destination",
                        "The space must be on a surface or in a liquid that can support the target without the target having to squeeze",
                    ),
                )
            ),
            Option(
                "At Higher Levels",
                (Facts((("Range", "+30 feet for each slot level above 2nd"),)),),
            ),
        ]


class WardingBond(ClassSpell):
    rules = SpellRules(
        name="Warding Bond",
        level=2,
        school=School.ABJURATION,
        classes=(CharacterClass.CLERIC, CharacterClass.PALADIN),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.TOUCH),
        components=Components(
            verbal=True,
            somatic=True,
            material="a pair of platinum rings worth 50+ GP each, which you and the target must wear for the duration",
        ),
        duration=Duration(DurationType.HOUR, 1),
        source="Player's Handbook",
        description=(
            "You touch another creature that is willing and create a mystic connection between you and the target until the spell ends. While the target is within 60 feet of you, it gains a +1 bonus to AC and saving throws, and it has Resistance to all damage. Also, each time it takes damage, you take the same amount of damage.\n"
            "The spell ends if you drop to 0 Hit Points or if you and the target become separated by more than 60 feet. It also ends if the spell is cast again on either of the connected creatures."
        ),
        usage_tags=("buff",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "eb5c083525cb5577")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You create a mystic connection between you and another willing creature you touch."
            ),
            Facts(
                (
                    (
                        "Within 60 feet",
                        "While the target is within 60 feet of you, it gains a +1 bonus to AC and saving throws, and it has Resistance to all damage",
                    ),
                    (
                        "Shared damage",
                        "Each time the target takes damage, you take the same amount of damage",
                    ),
                )
            ),
            Option(
                "The Spell Ends If",
                (
                    Facts(
                        (
                            ("You", "You drop to 0 Hit Points"),
                            (
                                "Distance",
                                "You and the target become separated by more than 60 feet",
                            ),
                            (
                                "Recasting",
                                "The spell is cast again on either of the connected creatures",
                            ),
                        )
                    ),
                ),
            ),
        ]


class WardingWind(ClassSpell):
    rules = SpellRules(
        name="Warding Wind",
        level=2,
        school=School.EVOCATION,
        classes=(
            CharacterClass.BARD,
            CharacterClass.DRUID,
            CharacterClass.SORCERER,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True),
        duration=Duration(DurationType.MINUTE, 10, concentration=True),
        source="Xanathar's Guide to Everything",
        description=(
            "A strong wind (20 miles per hour) blows around you in a 10-foot radius and moves with you, remaining centered on you. The wind lasts for the spell's duration.\n"
            "The wind has the following effects:\n"
            "It deafens you and other creatures in its area.\n"
            "It extinguishes unprotected flames in its area that are torch-sized or smaller.\n"
            "The area is difficult terrain for creatures other than you.\n"
            "The attack rolls of ranged weapon attacks have disadvantage if they pass in or out of the wind.\n"
            "It hedges out vapor, gas, and fog that can be dispersed by strong wind."
        ),
        usage_tags=("control", "damage"),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "6d6e38fc09883836")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "A strong wind (20 miles per hour) blows around you in a 10-foot radius for the duration, moving with you and remaining centered on you."
            ),
            Facts(
                (
                    ("Deafens", "You and other creatures in its area"),
                    (
                        "Flames",
                        "It extinguishes unprotected flames in its area that are torch-sized or smaller",
                    ),
                    (
                        "Terrain",
                        "The area is Difficult Terrain for creatures other than you",
                    ),
                    (
                        "Ranged attacks",
                        "The attack rolls of ranged weapon attacks have Disadvantage if they pass in or out of the wind",
                    ),
                    (
                        "Gas",
                        "It hedges out vapor, gas, and fog that can be dispersed by strong wind",
                    ),
                )
            ),
        ]


class WarpSense(ClassSpell):
    rules = SpellRules(
        name="Warp Sense",
        level=2,
        school=School.DIVINATION,
        classes=(
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True, material="a razorvine leaf"),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Planescape - Adventures in the Multiverse",
        description="For the duration, you sense the presence of portals, even inactive ones, within 30 feet of yourself. If you detect a portal in this way, you can use your action to study it. Make a DC 15 ability check using your spellcasting ability. On a successful check, you learn the destination plane of the portal and what portal key it requires, then the spell ends. On a failed check, you learn nothing and can't study that portal again using this spell until you cast it again. The spell can penetrate most barriers but is blocked by 1 foot of stone, 1 inch of common metal, a thin sheet of lead, or 3 feet of wood or dirt.",
        usage_tags=("utility",),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "042125f9fb154bf4")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "For the duration, you sense the presence of portals, even inactive ones, within 30 feet of yourself."
            ),
            Facts(
                (
                    (
                        "Study",
                        "If you detect a portal, you can use your action to study it: make a DC 15 ability check using your spellcasting ability",
                    ),
                    (
                        "Success",
                        "You learn the destination plane of the portal and what portal key it requires, then the spell ends",
                    ),
                    (
                        "Failure",
                        "You learn nothing and can't study that portal again using this spell until you cast it again",
                    ),
                    (
                        "Blocked by",
                        "The spell can penetrate most barriers but is blocked by 1 foot of stone, 1 inch of common metal, a thin sheet of lead, or 3 feet of wood or dirt",
                    ),
                )
            ),
        ]


class Web(ClassSpell):
    rules = SpellRules(
        name="Web",
        level=2,
        school=School.CONJURATION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.SORCERER,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True, somatic=True, material="a bit of spiderweb"),
        duration=Duration(DurationType.HOUR, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "You conjure a mass of sticky webbing at a point within range. The webs fill a 20-foot Cube there for the duration. The webs are Difficult Terrain, and the area within them is Lightly Obscured.\n"
            "If the webs aren’t anchored between two solid masses (such as walls or trees) or layered across a floor, wall, or ceiling, the web collapses on itself, and the spell ends at the start of your next turn. Webs layered over a flat surface have a depth of 5 feet.\n"
            "The first time a creature enters the webs on a turn or starts its turn there, it must succeed on a Dexterity saving throw or have the Restrained condition while in the webs or until it breaks free.\n"
            "A creature Restrained by the webs can take an action to make a Strength (Athletics) check against your spell save DC. If it succeeds, it is no longer Restrained.\n"
            "The webs are flammable. Any 5-foot Cube of webs exposed to fire burns away in 1 round, dealing 2d4 Fire damage to any creature that starts its turn in the fire."
        ),
        usage_tags=("control",),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "9bd51f3fe06ecc79")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You conjure a mass of sticky webbing at a point within range."),
            Facts(
                (
                    ("Area", "20-foot Cube"),
                    (
                        "Terrain",
                        "The webs are Difficult Terrain, and the area is Lightly Obscured",
                    ),
                    (
                        "Anchoring",
                        "Unless anchored between two solid masses (such as walls or trees) or layered across a floor, wall, or ceiling, the web collapses, and the spell ends at the start of your next turn",
                    ),
                    ("Depth", "5 feet, when layered over a flat surface"),
                )
            ),
            Facts(
                (
                    (
                        "Save",
                        "Dexterity, the first time a creature enters the webs on a turn or starts its turn there",
                    ),
                    (
                        "Failed save",
                        "Restrained while in the webs or until it breaks free",
                    ),
                    (
                        "Escape",
                        "A Restrained creature can take an action to make a Strength (Athletics) check against your spell save DC, ending the condition on a success",
                    ),
                    (
                        "Flammable",
                        "The webs are flammable: any 5-foot Cube of webs exposed to fire burns away in 1 round, dealing 2d4 Fire damage to any creature that starts its turn in the fire",
                    ),
                )
            ),
        ]


class WitherAndBloom(ClassSpell):
    rules = SpellRules(
        name="Wither and Bloom",
        level=2,
        school=School.NECROMANCY,
        classes=(CharacterClass.DRUID, CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(
            verbal=True, somatic=True, material="a withered vine twisted into a loop"
        ),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Arcana Unleashed",
        description=(
            "You invoke both death and life in a 10-foot-radius Sphere centered on a point within range. Each creature of your choice in that area makes a Constitution saving throw, taking 3d6 Necrotic damage on a failed save or half as much damage on a successful one. Nonmagical plants in that area that aren’t creatures, such as trees and shrubs, wither.\n"
            "In addition, one creature of your choice in that area can roll one of its unexpended Hit Point Dice and regain a number of Hit Points equal to the roll plus your spellcasting ability modifier. That die is then expended.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 1d6 for each spell slot level above 2. The number of Hit Point Dice that can be rolled and expended increases by one for each spell slot level above 2. You add your spellcasting modifier to the number of Hit Points regained by this spell only once, regardless of the number of Hit Point Dice rolled and expended."
        ),
        usage_tags=("damage", "heal"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "347bc9238e433ef3")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You invoke both death and life in a 10-foot-radius Sphere centered on a point within range.",
                    ),
                    ("Area", "10-foot-radius Sphere centered on a point within range"),
                    (
                        "Save",
                        "Constitution, made by each creature of your choice in the area",
                    ),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (("3d6 Necrotic damage", "Half as much damage"),),
            ),
            Facts(
                (
                    (
                        "Plants",
                        "Nonmagical plants in the area that aren't creatures, such as trees and shrubs, wither",
                    ),
                )
            ),
            Option(
                "Bloom",
                (
                    Facts(
                        (
                            ("Target", "One creature of your choice in the area"),
                            (
                                "Healing",
                                "It can roll one of its unexpended Hit Point Dice and regain Hit Points equal to the roll + your spellcasting ability modifier; that die is then expended",
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
                            ("Damage", "+1d6 for each spell slot level above 2"),
                            (
                                "Hit Point Dice",
                                "+1 die that can be rolled and expended for each spell slot level above 2",
                            ),
                            (
                                "Modifier",
                                "You add your spellcasting modifier to the Hit Points regained only once, regardless of the number of Hit Point Dice rolled and expended",
                            ),
                        )
                    ),
                ),
            ),
        ]


class ZoneOfTruth(ClassSpell):
    rules = SpellRules(
        name="Zone of Truth",
        level=2,
        school=School.ENCHANTMENT,
        classes=(CharacterClass.BARD, CharacterClass.CLERIC, CharacterClass.PALADIN),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 10),
        source="Player's Handbook",
        description=(
            "You create a magical zone that guards against deception in a 15-foot-radius Sphere centered on a point within range. Until the spell ends, a creature that enters the spell’s area for the first time on a turn or starts its turn there makes a Charisma saving throw. On a failed save, a creature can’t speak a deliberate lie while in the radius. You know whether a creature succeeds or fails on this save.\n"
            "An affected creature is aware of the spell and can avoid answering questions to which it would normally respond with a lie. Such a creature can be evasive yet must be truthful."
        ),
        usage_tags=("control",),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "fc6262943de4ffc9")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You create a magical zone that guards against deception."),
            Facts(
                (
                    ("Area", "15-foot-radius Sphere centered on a point within range"),
                    (
                        "Save",
                        "Charisma, made by a creature that enters the area for the first time on a turn or starts its turn there",
                    ),
                    (
                        "Failed save",
                        "The creature can't speak a deliberate lie while in the radius",
                    ),
                    ("You know", "Whether a creature succeeds or fails on this save"),
                    (
                        "Affected",
                        "An affected creature is aware of the spell and can avoid answering questions to which it would normally respond with a lie; it can be evasive yet must be truthful",
                    ),
                )
            ),
        ]

    def combat_effects(
        self, character: CharacterView | None = None
    ) -> list[CombatEffect]:
        return []


class FortunesFavor(ClassSpell):
    rules = SpellRules(
        name="Fortune's Favor",
        level=2,
        school=School.DIVINATION,
        classes=(CharacterClass.WIZARD,),
        casting_time=CastingTime(CastingTimeType.MINUTE, 1),
        range=Range(RangeType.FOOT, 60),
        components=Components(
            verbal=True,
            somatic=True,
            material="a white pearl worth at least 100 gp, which the spell consumes",
        ),
        duration=Duration(DurationType.HOUR, 1),
        source="Explorer's Guide to Wildemount",
        description=(
            "You impart latent luck to yourself or one willing creature you can see within range. When the chosen creature makes an attack roll, an ability check, or a saving throw before the spell ends, it can dismiss this spell on itself to roll an additional d20 and choose which of the d20s to use. Alternatively, when an attack roll is made against the chosen creature, it can dismiss this spell on itself to roll a d20 and choose which of the d20s to use, the one it rolled or the one the attacker rolled.\n"
            "If the original d20 roll has advantage or disadvantage, the creature rolls the additional d20 after advantage or disadvantage has been applied to the original roll.\n"
            "At Higher Levels. When you cast this spell using a spell slot of 3rd level or higher, you can target one additional creature for each slot level above 2nd."
        ),
        usage_tags=("buff", "utility"),
        target=FeatureTarget.ALLY,
        school_note="Dunamancy",
    )
    converted_from = RecordStamp("spells_dnd5e.json", "9fac2daad225aa27")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You impart latent luck to yourself or one willing creature you can see within range.",
                    ),
                    ("Target", "You or one willing creature you can see within range"),
                    (
                        "Its rolls",
                        "When it makes an attack roll, an ability check, or a saving throw before the spell ends, it can dismiss this spell on itself to roll an additional d20 and choose which of the d20s to use",
                    ),
                    (
                        "Attacked",
                        "Alternatively, when an attack roll is made against it, it can dismiss this spell on itself to roll a d20 and choose which of the d20s to use, the one it rolled or the one the attacker rolled",
                    ),
                    (
                        "Advantage",
                        "If the original d20 roll has advantage or disadvantage, the creature rolls the additional d20 after advantage or disadvantage has been applied to the original roll",
                    ),
                )
            ),
            Option(
                "At Higher Levels",
                (Facts((("Targets", "+1 creature for each slot level above 2nd"),)),),
            ),
        ]


class ImmovableObject(ClassSpell):
    rules = SpellRules(
        name="Immovable Object",
        level=2,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.WIZARD,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.TOUCH),
        components=Components(
            verbal=True,
            somatic=True,
            material="gold dust worth at least 25 gp, which the spell consumes",
        ),
        duration=Duration(DurationType.HOUR, 1),
        source="Explorer's Guide to Wildemount",
        description=(
            "You touch an object that weighs no more than 10 pounds and cause it to become magically fixed in place. You and the creatures you designate when you cast this spell can move the object normally. You can also set a password that, when spoken within 5 feet of the object, suppresses this spell for 1 minute.\n"
            "If the object is fixed in the air, it can hold up to 4,000 pounds of weight. More weight causes the object to fall. Otherwise, a creature can use an action to make a Strength check against your spell save DC. On a success, the creature can move the object up to 10 feet.\n"
            "At Higher Levels. If you cast this spell using a spell slot of 4th or 5th level, the DC to move the object increases by 5, it can carry up to 8,000 pounds of weight, and the duration increases to 24 hours. If you cast this spell using a spell slot of 6th level or higher, the DC to move the object increases by 10, it can carry up to 20,000 pounds of weight, and the effect is permanent until dispelled."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.OBJECT,
        school_note="Dunamancy:Graviturgy",
    )
    converted_from = RecordStamp("spells_dnd5e.json", "6a042ca5f74a2037")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You touch an object that weighs no more than 10 pounds and cause it to become magically fixed in place."
            ),
            Facts(
                (
                    (
                        "Exceptions",
                        "You and the creatures you designate when you cast this spell can move the object normally",
                    ),
                    (
                        "Password",
                        "You can set a password that, when spoken within 5 feet of the object, suppresses this spell for 1 minute",
                    ),
                    (
                        "In the air",
                        "If the object is fixed in the air, it can hold up to 4,000 pounds of weight; more weight causes it to fall",
                    ),
                    (
                        "Otherwise",
                        "A creature can use an action to make a Strength check against your spell save DC; on a success, it can move the object up to 10 feet",
                    ),
                )
            ),
            Option(
                "At Higher Levels",
                (
                    Table(
                        (
                            "Slot level",
                            "DC to move it",
                            "Weight it can carry",
                            "Duration",
                        ),
                        (
                            ("2nd-3rd", "Your spell save DC", "4,000 pounds", "1 hour"),
                            ("4th-5th", "+5", "8,000 pounds", "24 hours"),
                            (
                                "6th+",
                                "+10",
                                "20,000 pounds",
                                "Permanent until dispelled",
                            ),
                        ),
                    ),
                ),
            ),
        ]


class Wristpocket(ClassSpell):
    rules = SpellRules(
        name="Wristpocket",
        level=2,
        school=School.CONJURATION,
        classes=(CharacterClass.WIZARD,),
        casting_time=CastingTime(CastingTimeType.ACTION, ritual=True),
        range=Range(RangeType.SELF),
        components=Components(somatic=True),
        duration=Duration(DurationType.HOUR, 1, concentration=True),
        source="Explorer's Guide to Wildemount",
        description=(
            "You flick your wrist, causing one object in your hand to vanish. The object, which only you can be holding and can weigh no more than 5 pounds, is transported to an extradimensional space, where it remains for the duration.\n"
            "Until the spell ends, you can use your action to summon the object to your free hand, and you can use your action to return the object to the extradimensional space. An object still in the pocket plane when the spell ends appears in your space, at your feet."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.OBJECT,
        school_note="Dunamancy",
    )
    converted_from = RecordStamp("spells_dnd5e.json", "6f6db8b00eb53574")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You flick your wrist, causing one object in your hand to vanish.",
                    ),
                    (
                        "Object",
                        "One that only you are holding, weighing no more than 5 pounds",
                    ),
                    (
                        "Retrieve",
                        "Until the spell ends, you can use your action to summon the object to your free hand, and you can use your action to return it to the extradimensional space",
                    ),
                    (
                        "Spell ends",
                        "An object still in the pocket plane appears in your space, at your feet",
                    ),
                )
            )
        ]


class Consecration(ClassSpell):
    rules = SpellRules(
        name="Consecration",
        level=2,
        school=School.EVOCATION,
        classes=(CharacterClass.PALADIN,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="World of Warcraft",
        description="You consecrate the area in a 15-foot Emanation originating from you. Creatures of your choice that start their turn in the Emanation take 1d8 Radiant damage. The Emanation is Difficult Terrain for Fiends and Undead.",
        usage_tags=("control", "damage"),
    )
    converted_from = RecordStamp("spells_dnd2024.json", "9be47dc7e44c4440")


class CurseOfAgony(ClassSpell):
    rules = SpellRules(
        name="Curse of Agony",
        level=2,
        school=School.NECROMANCY,
        classes=(CharacterClass.WARLOCK,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 30),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 1),
        source="World of Warcraft",
        description="You curse one creature within range with excruciating pain. The target makes a Constitution saving throw; the spell’s damage starts at 1d4 Psychic damage. On a failed save, the target takes the spell’s damage, and the spell’s damage die increases: from 1d4 to 1d6, 1d6 to 1d8, 1d8 to 1d10, or 1d10 to 1d12 (the maximum). On a successful save, the target takes the spell’s damage, and the effect ends. The target repeats the save at the end of each of its turns.",
        usage_tags=("damage",),
    )
    converted_from = RecordStamp("spells_dnd2024.json", "bdb8cad1a051fec4")


class DeathAndDecay(ClassSpell):
    rules = SpellRules(
        name="Death and Decay",
        level=2,
        school=School.NECROMANCY,
        classes=(),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="World of Warcraft",
        description="Corruption ripples out in a 20-foot-radius Sphere from a point on the ground you can see within range. Each creature in that area makes a Wisdom saving throw. On a failed save, a target takes 2d6 Necrotic damage and is cursed until the end of your next turn. If you deal damage to a cursed target with an attack roll, the target takes an extra 1d6 Necrotic damage. On a successful save, the target takes half as much damage only.",
        usage_tags=("damage",),
    )
    converted_from = RecordStamp("spells_dnd2024.json", "81430137750e2684")


class DreamBreath(ClassSpell):
    rules = SpellRules(
        name="Dream Breath",
        level=2,
        school=School.ABJURATION,
        classes=(CharacterClass.SORCERER,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="World of Warcraft",
        description=(
            "You exhale verdant healing magic. Each creature of your choice in a 15-foot Cone regains 2d6 Hit Points.\n"
            "Using a Higher-Level Spell Slot. The healing increases by 2d6 for each spell slot level above 2."
        ),
        usage_tags=("heal",),
    )
    converted_from = RecordStamp("spells_dnd2024.json", "12834cef3528a4b9")


class Eruption(ClassSpell):
    rules = SpellRules(
        name="Eruption",
        level=2,
        school=School.EVOCATION,
        classes=(CharacterClass.SORCERER,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="World of Warcraft",
        description=(
            "The ground in a 20-foot-radius Sphere centered on a point within range erupts with flames. Each creature in the Sphere makes a Dexterity saving throw, taking 3d8 Fire damage on a failed save or half as much damage on a successful one.\n"
            "The cracks turn the ground in the Sphere into Difficult Terrain until the end of your next turn, at which point they close.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 1d8 for each spell slot level above 2."
        ),
        usage_tags=("control", "damage"),
    )
    converted_from = RecordStamp("spells_dnd2024.json", "1d749683e74b48dc")


class EyeBeam(ClassSpell):
    rules = SpellRules(
        name="Eye Beam",
        level=2,
        school=School.EVOCATION,
        classes=(),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="World of Warcraft",
        description=(
            "You concentrate your magic into your eyes. When you cast the spell, and as a Magic action on your subsequent turns for the duration, you can unleash a burst of fel magic. Each creature in a 15-foot Cone makes a Dexterity saving throw, taking 3d6 Force damage on a failed save or half as much damage on a successful one.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 1d6 for each spell slot level above 1."
        ),
        usage_tags=("damage",),
    )
    converted_from = RecordStamp("spells_dnd2024.json", "82302b52bbd0a1d0")


class FeralProwl(ClassSpell):
    rules = SpellRules(
        name="Feral Prowl",
        level=2,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.DRUID,),
        casting_time=CastingTime(CastingTimeType.BONUS_ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True),
        duration=Duration(DurationType.MINUTE, 1),
        source="World of Warcraft",
        description="You shape-shift as if you had used Wild Shape, but you don’t expend a use of your Wild Shape. You have the Invisible condition until the spell ends. The spell ends early immediately after you make an attack roll, deal damage, cast a spell, or revert to your natural form.",
        usage_tags=("buff",),
    )
    converted_from = RecordStamp("spells_dnd2024.json", "93875a044bf7697a")


class FieryBrand(ClassSpell):
    rules = SpellRules(
        name="Fiery Brand",
        level=2,
        school=School.EVOCATION,
        classes=(),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 30),
        components=Components(verbal=True),
        duration=Duration(DurationType.MINUTE, 1),
        source="World of Warcraft",
        description=(
            "You magically place a fiery demonic symbol on a creature within range, which makes a Wisdom saving throw. On a failed save, the creature takes 3d10 Fire damage and is cursed. While it remains cursed, you have Resistance to all damage it deals. On a successful save, it takes half as much damage only.\n"
            "A cursed creature repeats the save at the end of each of its turns, ending the spell on a success."
        ),
        usage_tags=("buff", "damage"),
    )
    converted_from = RecordStamp("spells_dnd2024.json", "91085f1a54effcb3")


class Frostscythe(ClassSpell):
    rules = SpellRules(
        name="Frostscythe",
        level=2,
        school=School.EVOCATION,
        classes=(),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="World of Warcraft",
        description=(
            "Sweeping your weapon before you, you unleash a blast of icy cold. Each creature in a 20-foot Cone makes a Constitution saving throw. On a failed save, a creature takes 3d8 Cold damage, and its Speed is reduced by 10 feet for 1 minute. On a successful save, a creature takes half as much damage only.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 1d8 for each spell slot level above 2."
        ),
        usage_tags=("control", "damage"),
    )
    converted_from = RecordStamp("spells_dnd2024.json", "7a8a4f1ce71af28b")


class RoarOfUrsoc(ClassSpell):
    rules = SpellRules(
        name="Roar of Ursoc",
        level=2,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.DRUID,),
        casting_time=CastingTime(CastingTimeType.BONUS_ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True),
        duration=Duration(DurationType.ROUND, 1),
        source="World of Warcraft",
        description="You shape-shift as if you had used Wild Shape, but you don’t expend a use of your Wild Shape. Until the start of your next turn, any creature that starts its turn within 5 feet of you has Disadvantage on attack rolls against any creature other than you.",
        usage_tags=("control",),
    )
    converted_from = RecordStamp("spells_dnd2024.json", "9efb5d6628a32db9")


class SigilOfFlame(ClassSpell):
    rules = SpellRules(
        name="Sigil of Flame",
        level=2,
        school=School.EVOCATION,
        classes=(),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 90),
        components=Components(verbal=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="World of Warcraft",
        description=(
            "You inscribe a sigil in the air that then appears on a creature you can see within range. The target makes a Constitution saving throw, taking 2d8 Fire damage on a failed save or half as much damage on a successful one. Whether or not the target fails its saving throw, it radiates heat in a 10-foot Emanation originating from itself until the end of its next turn. At the start of the target’s next turn, the target and each creature in the Emanation must succeed on a Constitution saving throw or take 1d8 Fire damage.\n"
            "Using a Higher-Level Spell Slot. The damage (both initial and later) increases by 1d8 for each spell slot level above 2."
        ),
        usage_tags=("damage",),
    )
    converted_from = RecordStamp("spells_dnd2024.json", "f269ef1d2564d287")


SPELLS = [
    AganazzarsScorcher,
    Aid,
    AirBubble,
    AlterSelf,
    AnimalMessenger,
    ArcaneLock,
    ArcaneVigor,
    Augury,
    Barkskin,
    BattleFamiliar,
    BeastSense,
    BlindnessDeafness,
    Blur,
    BorrowedKnowledge,
    BrandingSmite,
    CalmEmotions,
    CloudOfDaggers,
    ConjureTools,
    Consecration,
    ContinualFlame,
    CordonOfArrows,
    CrownOfMadness,
    CurseOfAgony,
    Darkness,
    Darkvision,
    DeathAndDecay,
    DeathArmor,
    DeryansHelpfulHomunculi,
    DetectThoughts,
    DisruptiveTune,
    DragonsBreath,
    DreamBreath,
    DuelingGround,
    DustDevil,
    Earthbind,
    ElminstersElusion,
    EnhanceAbility,
    EnlargeReduce,
    Enthrall,
    Eruption,
    EyeBeam,
    FeralProwl,
    FieryBrand,
    FindSteed,
    FindTraps,
    FlameBlade,
    FlamingSphere,
    FlockOfFamiliars,
    FortunesFavor,
    Frostscythe,
    GentleRepose,
    GiftOfGab,
    GustOfWind,
    HealingSpirit,
    HeatMetal,
    HoldPerson,
    HomunculusServant,
    ImmovableObject,
    Invisibility,
    JimsGlowingCoin,
    KineticJaunt,
    Knock,
    LesserRestoration,
    Levitate,
    LocateAnimalsOrPlants,
    LocateObject,
    MagicMouth,
    MagicWeapon,
    MaximilliansEarthenGrasp,
    MelfsAcidArrow,
    MindSpike,
    MirrorImage,
    MistyStep,
    Moonbeam,
    NathairsMischief,
    NystulsMagicAura,
    PassWithoutTrace,
    PhantasmalForce,
    PinkySwear,
    PrayerOfHealing,
    ProtectionFromPoison,
    Pyrotechnics,
    RayOfEnfeeblement,
    RimesBindingIce,
    RoarOfUrsoc,
    RopeTrick,
    ScorchingRay,
    SearingOrb,
    SeeInvisibility,
    ShadowBlade,
    Shatter,
    ShiningSmite,
    SigilOfFlame,
    Silence,
    Skywrite,
    SnillocsSnowballSwarm,
    SpiderClimb,
    SpikeGrowth,
    SpiritualWeapon,
    SprayOfCards,
    Suggestion,
    SummonBeast,
    TashasMindWhip,
    TortoiseShell,
    UncertainFooting,
    VortexWarp,
    WardingBond,
    WardingWind,
    WarpSense,
    Web,
    WitherAndBloom,
    Wristpocket,
    ZoneOfTruth,
]
