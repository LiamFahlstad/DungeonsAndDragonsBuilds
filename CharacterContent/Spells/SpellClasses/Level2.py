"""Level 2 spells as classes (CharacterContent/Spells/SpellFactory/ClassSpell.py),
which SpellFactory uses instead of their JSON records. Written by
CharacterContent/Spells/SpellClassConverter.py; edit them by hand from
then on: each class is its spell's one source."""

from CharacterContent.Spells.SpellFactory.ClassSpell import ClassSpell, SpellRules
from CharacterContent.Spells.SpellFactory.Enums import Component, School
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
        casting_time="Action",
        range="60 feet",
        components=(Component.VERBAL, Component.SOMATIC, Component.MATERIAL),
        material="a straight piece of iron",
        duration="Concentration, up to 1 minute",
        source="Player's Handbook",
        description=(
            "Choose a Humanoid that you can see within range. The target must succeed on a Wisdom saving throw or have the Paralyzed condition for the duration. At the end of each of its turns, the target repeats the save, ending the spell on itself on a success.\n"
            "Using a Higher-Level Spell Slot. You can target one additional Humanoid for each spell slot level above 2."
        ),
        usage_tags=("control",),
        target=FeatureTarget.ENEMY,
    )

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
                roll="save",
                save_ability=Ability.WISDOM,
                repeat_save=True,
                conditions=(CombatCondition(Condition.PARALYZED),),
                notes=("Humanoids only. One more target per slot level above 2.",),
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
        casting_time="Action",
        range="Touch",
        components=(Component.VERBAL, Component.SOMATIC, Component.MATERIAL),
        material="an eyelash in gum arabic",
        duration="Concentration, up to 1 hour",
        source="Player's Handbook",
        description=(
            "A creature you touch has the Invisible condition until the spell ends. The spell ends early immediately after the target makes an attack roll, deals damage, or casts a spell.\n"
            "Using a Higher-Level Spell Slot. You can target one additional creature for each spell slot level above 2."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.ALLY,
    )

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
                notes=(
                    "It ends right after the target makes an attack roll, deals damage or casts a spell. One more target per slot level above 2.",
                ),
            )
        ]


class Moonbeam(ClassSpell):
    rules = SpellRules(
        name="Moonbeam",
        level=2,
        school=School.EVOCATION,
        classes=(CharacterClass.DRUID,),
        casting_time="Action",
        range="120 feet",
        components=(Component.VERBAL, Component.SOMATIC, Component.MATERIAL),
        material="a moonseed leaf",
        duration="Concentration, up to 1 minute",
        source="Player's Handbook",
        description=(
            "A silvery beam of pale light shines down in a 5-foot-radius, 40-foot-high Cylinder centered on a point within range. Until the spell ends, Dim Light fills the Cylinder, and you can take a Magic action on later turns to move the Cylinder up to 60 feet.\n"
            "When the Cylinder appears, each creature in it makes a Constitution saving throw. On a failed save, a creature takes 2d10 Radiant damage, and if the creature is shape-shifted (as a result of the Polymorph spell, for example), it reverts to its true form and can’t shape-shift until it leaves the Cylinder. On a successful save, a creature takes half as much damage only. A creature also makes this save when the spell’s area moves into its space and when it enters the spell’s area or ends its turn there. A creature makes this save only once per turn.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 1d10 for each spell slot level above 2."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.AREA,
    )

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
                roll="save",
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
        casting_time="Action",
        range="120 feet",
        components=(Component.VERBAL, Component.SOMATIC),
        duration="Instantaneous",
        source="Player's Handbook",
        description=(
            "You hurl three fiery rays. You can hurl them at one target within range or at several. Make a ranged spell attack for each ray. On a hit, the target takes 2d6 Fire damage.\n"
            "Using a Higher-Level Spell Slot. You create one additional ray for each spell slot level above 2."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.ENEMY,
    )

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
                roll="attack",
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
        casting_time="Action",
        range="60 feet",
        components=(Component.VERBAL, Component.SOMATIC, Component.MATERIAL),
        material="a chip of mica",
        duration="Instantaneous",
        source="Player's Handbook",
        description=(
            "A loud noise erupts from a point of your choice within range. Each creature in a 10-foot-radius Sphere centered there makes a Constitution saving throw, taking 3d8 Thunder damage on a failed save or half as much damage on a successful one. A Construct has Disadvantage on the save.\n"
            "A nonmagical object that isn’t being worn or carried also takes the damage if it’s in the spell’s area.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 1d8 for each spell slot level above 2."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.AREA,
    )

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
                roll="save",
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
        casting_time="Action",
        range="150 feet",
        components=(Component.VERBAL, Component.SOMATIC, Component.MATERIAL),
        material="seven thorns",
        duration="Concentration, up to 10 minutes",
        source="Player's Handbook",
        description=(
            "The ground in a 20-foot-radius Sphere centered on a point within range sprouts hard spikes and thorns. The area becomes Difficult Terrain for the duration. When a creature moves into or within the area, it takes 2d4 Piercing damage for every 5 feet it travels.\n"
            "The transformation of the ground is camouflaged to look natural. Any creature that can’t see the area when the spell is cast must take a Search action and succeed on a Wisdom (Perception or Survival) check against your spell save DC to recognize the terrain as hazardous before entering it."
        ),
        usage_tags=("control", "damage"),
        target=FeatureTarget.AREA,
    )

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
        casting_time="Bonus Action",
        range="60 feet",
        components=(Component.VERBAL, Component.SOMATIC),
        duration="Concentration, up to 1 minute",
        source="Player's Handbook",
        description=(
            "You create a floating, spectral force that resembles a weapon of your choice and lasts for the duration. The force appears within range in a space of your choice, and you can immediately make one melee spell attack against one creature within 5 feet of the force. On a hit, the target takes Force damage equal to 1d8 plus your spellcasting ability modifier.\n"
            "As a Bonus Action on your later turns, you can move the force up to 20 feet and repeat the attack against a creature within 5 feet of it.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 1d8 for every slot level above 2."
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
                roll="attack",
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
        casting_time="Action",
        range="30 feet",
        components=(Component.VERBAL, Component.MATERIAL),
        material="a drop of honey",
        duration="Concentration, up to 8 hours",
        source="Player's Handbook",
        description=(
            "You suggest a course of activity—described in no more than 25 words—to one creature you can see within range that can hear and understand you. The suggestion must sound achievable and not involve anything that would obviously deal damage to the target or its allies. For example, you could say, “Fetch the key to the cult’s treasure vault, and give the key to me.” Or you could say, “Stop fighting, leave this library peacefully, and don’t return.”\n"
            "The target must succeed on a Wisdom saving throw or have the Charmed condition for the duration or until you or your allies deal damage to the target. The Charmed target pursues the suggestion to the best of its ability. The suggested activity can continue for the entire duration, but if the suggested activity can be completed in a shorter time, the spell ends for the target upon completing it."
        ),
        usage_tags=("control",),
        target=FeatureTarget.ENEMY,
    )

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
                roll="save",
                save_ability=Ability.WISDOM,
                conditions=(CombatCondition(Condition.CHARMED),),
                notes=(
                    "The target must be able to hear and understand you. It ends early if you or your allies damage it, or when the suggested activity is done.",
                ),
            )
        ]


SPELLS = [
    HoldPerson,
    Invisibility,
    Moonbeam,
    ScorchingRay,
    Shatter,
    SpikeGrowth,
    SpiritualWeapon,
    Suggestion,
]
