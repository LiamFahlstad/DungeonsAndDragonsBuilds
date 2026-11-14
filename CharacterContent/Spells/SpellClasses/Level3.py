"""Level 3 spells as classes (CharacterContent/Spells/SpellFactory/ClassSpell.py),
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
    EffectRoll,
    TurnEdge,
    TurnOf,
)
from Model.Content.CombatModifiers import (
    ArmorClass,
    AtTurnEnd,
    D20Mode,
    D20Test,
    Note,
    Resistance,
    RollMode,
    Speed,
    WhoseTurn,
)
from Model.Content.Feature import FeatureTarget
from Model.Content.FeatureText import Block, Facts, Option, Paragraph, Table
from Model.View import CharacterView


class Fireball(ClassSpell):
    rules = SpellRules(
        name="Fireball",
        level=3,
        school=School.EVOCATION,
        classes=(CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 150),
        components=Components(
            verbal=True, somatic=True, material="a ball of bat guano and sulfur"
        ),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "A bright streak flashes from you to a point you choose within range and then blossoms with a low roar into a fiery explosion. Each creature in a 20-foot-radius Sphere centered on that point makes a Dexterity saving throw, taking 8d6 Fire damage on a failed save or half as much damage on a successful one.\n"
            "Flammable objects in the area that aren’t being worn or carried start burning.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 1d6 for each spell slot level above 3."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "315e1e81cac3d7f1")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "A bright streak flashes from you to a point you choose within range and then blossoms with a low roar into a fiery explosion.",
                    ),
                    (
                        "Area",
                        "20-foot-radius Sphere centered on a point you choose within range",
                    ),
                    ("Save", "Dexterity, made by each creature in the area"),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (("8d6 Fire damage", "Half as much damage"),),
            ),
            Facts(
                (
                    (
                        "Objects",
                        "Flammable objects in the area that aren't being worn or carried start burning",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Damage", "+1d6 for each spell slot level above 3"),)),),
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
                damage=(CombatDamage("8d6", DamageType.FIRE, upcast="1d6"),),
            )
        ]


class LightningBolt(ClassSpell):
    rules = SpellRules(
        name="Lightning Bolt",
        level=3,
        school=School.EVOCATION,
        classes=(CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(
            verbal=True, somatic=True, material="a bit of fur and a crystal rod"
        ),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "A stroke of lightning forming a 100-foot-long, 5-foot-wide Line blasts out from you in a direction you choose. Each creature in the Line makes a Dexterity saving throw, taking 8d6 Lightning damage on a failed save or half as much damage on a successful one.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 1d6 for each spell slot level above 3."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "56b7a047f62896ae")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "A stroke of lightning forming a 100-foot-long, 5-foot-wide Line blasts out from you in a direction you choose.",
                    ),
                    (
                        "Area",
                        "Line 100 feet long and 5 feet wide, in a direction you choose",
                    ),
                    ("Save", "Dexterity, made by each creature in the Line"),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (("8d6 Lightning damage", "Half as much damage"),),
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Damage", "+1d6 for each spell slot level above 3"),)),),
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
                damage=(CombatDamage("8d6", DamageType.LIGHTNING, upcast="1d6"),),
            )
        ]


class AnimateDead(ClassSpell):
    rules = SpellRules(
        name="Animate Dead",
        level=3,
        school=School.NECROMANCY,
        classes=(CharacterClass.CLERIC, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.MINUTE, 1),
        range=Range(RangeType.FOOT, 10),
        components=Components(
            verbal=True,
            somatic=True,
            material="a drop of blood, a piece of flesh, and a pinch of bone dust",
        ),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "Choose a pile of bones or a corpse of a Medium or Small Humanoid within range. The target becomes an Undead creature: a Skeleton if you chose bones or a Zombie if you chose a corpse (see appendix B for the stat blocks).\n"
            "On each of your turns, you can take a Bonus Action to mentally command any creature you made with this spell if the creature is within 60 feet of you (if you control multiple creatures, you can command any of them at the same time, issuing the same command to each one). You decide what action the creature will take and where it will move on its next turn, or you can issue a general command, such as to guard a chamber or corridor. If you issue no commands, the creature takes the Dodge action and moves only to avoid harm. Once given an order, the creature continues to follow it until its task is complete.\n"
            "The creature is under your control for 24 hours, after which it stops obeying any command you’ve given it. To maintain control of the creature for another 24 hours, you must cast this spell on the creature again before the current 24-hour period ends. This use of the spell reasserts your control over up to four creatures you have animated with this spell rather than animating a new creature.\n"
            "Using a Higher-Level Spell Slot. You animate or reassert control over two additional Undead creatures for each spell slot level above 3. Each of the creatures must come from a different corpse or pile of bones."
        ),
        usage_tags=("summon",),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "e68049108b02a0d2")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You raise a Skeleton or a Zombie to serve you."),
            Facts(
                (
                    (
                        "Target",
                        "A pile of bones or a corpse of a Medium or Small Humanoid within range",
                    ),
                    (
                        "Result",
                        "It becomes an Undead creature: a Skeleton if you chose bones, or a Zombie if you chose a corpse (see appendix B for the stat blocks)",
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
                                "On each of your turns, you can take a Bonus Action to mentally command any creature you made with this spell if it is within 60 feet of you",
                            ),
                            (
                                "Several",
                                "If you control multiple creatures, you can command any of them at the same time, issuing the same command to each one",
                            ),
                            (
                                "Orders",
                                "You decide what action the creature will take and where it will move on its next turn, or you can issue a general command, such as to guard a chamber or corridor; once given an order, it continues to follow it until its task is complete",
                            ),
                            (
                                "No command",
                                "It takes the Dodge action and moves only to avoid harm",
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
                                "24 hours, after which the creature stops obeying any command you've given it",
                            ),
                            (
                                "Reasserting",
                                "To maintain control for another 24 hours, you must cast this spell on the creature again before the current 24-hour period ends",
                            ),
                            (
                                "Up to four",
                                "This use of the spell reasserts your control over up to four creatures you have animated with this spell, rather than animating a new creature",
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
                                "Creatures",
                                "Animate or reassert control over two additional Undead creatures for each spell slot level above 3",
                            ),
                            (
                                "Remains",
                                "Each of the creatures must come from a different corpse or pile of bones",
                            ),
                        )
                    ),
                ),
            ),
        ]


class Antagonize(ClassSpell):
    rules = SpellRules(
        name="Antagonize",
        level=3,
        school=School.ENCHANTMENT,
        classes=(
            CharacterClass.BARD,
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 30),
        components=Components(
            verbal=True, somatic=True, material="a playing card depicting a rogue"
        ),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="The Book of Many Things",
        description=(
            "Range: 30 feet\n"
            "Components: V, S, M (a playing card depicting a rogue)\n"
            "Duration: Instantaneous\n"
            "You whisper magical words that antagonize one creature of your choice within range. The target must make a Wisdom saving throw. On a failed save, the target takes 4d4 psychic damage and must immediately use its reaction to make a melee attack against another creature of your choice that you can see. If the target can't make this attack (for example, because there is no one within its reach or because its reaction is unavailable), the target instead has disadvantage on the next attack roll it makes before the start of your next turn. On a successful save, the target takes half as much damage only.\n"
            "At Higher Levels. When you cast this spell using a spell slot of 4th level or higher, the damage increases by 1d4 for each slot level above 3rd."
        ),
        usage_tags=("buff", "control", "damage", "utility"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "53a25abb1c1ea381")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You whisper magical words that antagonize one creature of your choice within range.",
                    ),
                    ("Target", "One creature of your choice within range"),
                    ("Save", "Wisdom"),
                )
            ),
            Option(
                "Failed Save",
                (
                    Facts(
                        (
                            ("Damage", "4d4 Psychic damage"),
                            (
                                "Reaction",
                                "It must immediately use its reaction to make a melee attack against another creature of your choice that you can see",
                            ),
                            (
                                "Can't attack",
                                "If it can't make this attack (for example, because there is no one within its reach or because its reaction is unavailable), it instead has Disadvantage on the next attack roll it makes before the start of your next turn",
                            ),
                        )
                    ),
                ),
            ),
            Facts((("Successful save", "Half as much damage only"),)),
            Option(
                "At Higher Levels",
                (Facts((("Damage", "+1d4 for each slot level above 3rd"),)),),
            ),
        ]


class AshardalonsStride(ClassSpell):
    rules = SpellRules(
        name="Ashardalon's Stride",
        level=3,
        school=School.TRANSMUTATION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.RANGER,
            CharacterClass.SORCERER,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.BONUS_ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Fizban's Treasury of Dragons",
        description=(
            "The billowing flames of a dragon blast from your feet, granting you explosive speed. For the duration, your speed increases by 20 feet and moving doesn't provoke opportunity attacks.\n"
            "When you move within 5 feet of a creature or an object that isn't being worn or carried, it takes 1d6 fire damage from your trail of heat. A creature or object can take this damage only once during a turn.\n"
            "At Higher Levels. When you cast this spell using a spell slot of 4th level or higher, increase your speed by 5 feet for each spell slot level above 3rd. The spell deals an additional 1d6 fire damage for each slot level above 3rd."
        ),
        usage_tags=("buff", "damage"),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "7e5c978441e4ab7e")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "The billowing flames of a dragon blast from your feet, granting you explosive speed.",
                    ),
                    ("Speed", "For the duration, your speed increases by 20 feet"),
                    ("Opportunity", "Moving doesn't provoke opportunity attacks"),
                    (
                        "Trail of heat",
                        "When you move within 5 feet of a creature or an object that isn't being worn or carried, it takes 1d6 Fire damage",
                    ),
                    (
                        "Limit",
                        "A creature or object can take this damage only once during a turn",
                    ),
                )
            ),
            Option(
                "At Higher Levels",
                (
                    Facts(
                        (
                            ("Speed", "+5 feet for each spell slot level above 3rd"),
                            (
                                "Damage",
                                "+1d6 Fire damage for each slot level above 3rd",
                            ),
                        )
                    ),
                ),
            ),
        ]


class AstralFlood(ClassSpell):
    rules = SpellRules(
        name="Astral Flood",
        level=3,
        school=School.EVOCATION,
        classes=(
            CharacterClass.BARD,
            CharacterClass.CLERIC,
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(
            verbal=True, somatic=True, material="a mixture of water and powdered silver"
        ),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="D&D Beyond Drops - May 2026",
        description=(
            "You channel energy from the Astral Sea to unleash a torrent of magic from yourself. Choose Cold or Radiant for the type of energy channeled. Each creature in a 30-foot Cone originating from you makes a Dexterity saving throw. On a failed save, the target takes 4d10 damage of the chosen type and suffers an additional effect determined by the damage type:\n"
            "Cold Damage. The target has Disadvantage on the next D20 Test it makes before the end of your next turn.\n"
            "Radiant Damage. The target has the Blinded condition until the end of your next turn.\n"
            "On a successful save, the target takes half as much damage only.\n"
            "Using a Higher-Level Spell Slot: The damage increases by 1d10 for each spell slot above 3."
        ),
        usage_tags=("control", "damage"),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "ceea7e0269a78610")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You channel energy from the Astral Sea to unleash a torrent of magic from yourself.",
                    ),
                    (
                        "Choice",
                        "Choose Cold or Radiant for the type of energy channeled",
                    ),
                    ("Area", "30-foot Cone originating from you"),
                    ("Save", "Dexterity, made by each creature in the Cone"),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (
                    (
                        "4d10 damage of the chosen type, and the target suffers an additional effect determined by the damage type (below)",
                        "Half as much damage only",
                    ),
                ),
            ),
            Table(
                ("Damage type", "Additional effect"),
                (
                    (
                        "Cold",
                        "The target has Disadvantage on the next D20 Test it makes before the end of your next turn",
                    ),
                    (
                        "Radiant",
                        "The target has the Blinded condition until the end of your next turn",
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
                                "The damage increases by 1d10 for each spell slot above 3",
                            ),
                        )
                    ),
                ),
            ),
        ]


class AuraOfVitality(ClassSpell):
    rules = SpellRules(
        name="Aura of Vitality",
        level=3,
        school=School.ABJURATION,
        classes=(CharacterClass.CLERIC, CharacterClass.DRUID, CharacterClass.PALADIN),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description="An aura radiates from you in a 30-foot Emanation for the duration. When you create the aura and at the start of each of your turns while it persists, you can restore 2d6 Hit Points to one creature in it.",
        usage_tags=("buff", "heal"),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "46852f5fc8be61cf")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Area", "30-foot Emanation"),
                    (
                        "Healing",
                        "When you create the aura and at the start of each of your turns while it persists, you can restore 2d6 Hit Points to one creature in it",
                    ),
                )
            )
        ]


class BeaconOfHope(ClassSpell):
    rules = SpellRules(
        name="Beacon of Hope",
        level=3,
        school=School.ABJURATION,
        classes=(CharacterClass.CLERIC,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 30),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description="Choose any number of creatures within range. For the duration, each target has Advantage on Wisdom saving throws and Death Saving Throws and regains the maximum number of Hit Points possible from any healing.",
        usage_tags=("buff", "heal"),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "acc646c8ffa47b88")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Targets", "Any number of creatures within range"),
                    (
                        "Saves",
                        "For the duration, each target has Advantage on Wisdom saving throws and Death Saving Throws",
                    ),
                    (
                        "Healing",
                        "Each target regains the maximum number of Hit Points possible from any healing",
                    ),
                )
            )
        ]


class BestowCurse(ClassSpell):
    rules = SpellRules(
        name="Bestow Curse",
        level=3,
        school=School.NECROMANCY,
        classes=(CharacterClass.BARD, CharacterClass.CLERIC, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.TOUCH),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "You touch a creature, which must succeed on a Wisdom saving throw or become cursed for the duration. Until the curse ends, the target suffers one of the following effects of your choice:\n"
            "Choose one ability. The target has Disadvantage on ability checks and saving throws made with that ability.\n"
            "The target has Disadvantage on attack rolls against you.\n"
            "In combat, the target must succeed on a Wisdom saving throw at the start of each of its turns or be forced to take the Dodge action on that turn.\n"
            "If you deal damage to the target with an attack roll or a spell, the target takes an extra 1d8 Necrotic damage.\n"
            "Using a Higher-Level Spell Slot. If you cast this spell using a level 4 spell slot, you can maintain Concentration on it for up to 10 minutes. If you use a level 5+ spell slot, the spell doesn't require Concentration, and the duration becomes 8 hours (level 5–6 slot) or 24 hours (level 7–8 slot). If you use a level 9 spell slot, the spell lasts until dispelled."
        ),
        usage_tags=("buff", "control", "damage"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "01df50acfd99f1d4")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You touch a creature and curse it."),
            Facts(
                (
                    ("Target", "A creature you touch"),
                    ("Save", "Wisdom"),
                    (
                        "Failed save",
                        "Cursed for the duration, suffering one of the effects below (your choice) until the curse ends",
                    ),
                )
            ),
            Table(
                ("Curse", "Effect"),
                (
                    (
                        "Ability",
                        "Choose one ability; the target has Disadvantage on ability checks and saving throws made with that ability",
                    ),
                    (
                        "Attacks on you",
                        "The target has Disadvantage on attack rolls against you",
                    ),
                    (
                        "Lost turns",
                        "In combat, the target must succeed on a Wisdom saving throw at the start of each of its turns or be forced to take the Dodge action on that turn",
                    ),
                    (
                        "Extra damage",
                        "If you deal damage to the target with an attack roll or a spell, the target takes an extra 1d8 Necrotic damage",
                    ),
                ),
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (
                    Table(
                        ("Slot level", "Duration"),
                        (
                            ("3", "Concentration, up to 1 minute"),
                            ("4", "Concentration, up to 10 minutes"),
                            ("5-6", "8 hours, without Concentration"),
                            ("7-8", "24 hours, without Concentration"),
                            ("9", "Until dispelled, without Concentration"),
                        ),
                    ),
                ),
            ),
        ]


class BlindingSmite(ClassSpell):
    rules = SpellRules(
        name="Blinding Smite",
        level=3,
        school=School.EVOCATION,
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
            "The target hit by the strike takes an extra 3d8 Radiant damage from the attack, and the target has the Blinded condition until the spell ends. At the end of each of its turns, the Blinded target makes a Constitution saving throw, ending the spell on itself on a success.\n"
            "Using a Higher-Level Spell Slot. The extra damage increases by 1d8 for each spell slot level above 3."
        ),
        usage_tags=("control", "damage"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "52c1ccba4de7e2dc")

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
                        "The target takes an extra 3d8 Radiant damage from the attack",
                    ),
                    (
                        "Blinded",
                        "The target has the Blinded condition until the spell ends",
                    ),
                    (
                        "Repeat save",
                        "At the end of each of its turns, the Blinded target makes a Constitution saving throw, ending the spell on itself on a success",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Extra damage", "+1d8 for each spell slot level above 3"),)),),
            ),
        ]


class Blink(ClassSpell):
    rules = SpellRules(
        name="Blink",
        level=3,
        school=School.TRANSMUTATION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.SORCERER,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 1),
        source="Player's Handbook",
        description=(
            "Roll 1d6 at the end of each of your turns for the duration. On a roll of 4–6, you vanish from your current plane of existence and appear in the Ethereal Plane (the spell ends instantly if you are already on that plane). While on the Ethereal Plane, you can perceive the plane you left, which is cast in shades of gray, but you can’t see anything there more than 60 feet away. You can affect and be affected only by other creatures on the Ethereal Plane, and creatures on the other plane can’t perceive you unless they have a special ability that lets them perceive things on the Ethereal Plane.\n"
            "You return to the other plane at the start of your next turn and when the spell ends if you are on the Ethereal Plane. You return to an unoccupied space of your choice that you can see within 10 feet of the space you left. If no unoccupied space is available within that range, you appear in the nearest unoccupied space."
        ),
        usage_tags=("buff",),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "958dd46c71ec0190")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Roll", "1d6 at the end of each of your turns"),
                    (
                        "On a 4-6",
                        "You vanish from your current plane of existence and appear in the Ethereal Plane (the spell ends instantly if you are already on that plane)",
                    ),
                )
            ),
            Option(
                "On the Ethereal Plane",
                (
                    Facts(
                        (
                            (
                                "Seeing",
                                "You can perceive the plane you left, which is cast in shades of gray, but you can't see anything there more than 60 feet away",
                            ),
                            (
                                "Interaction",
                                "You can affect and be affected only by other creatures on the Ethereal Plane",
                            ),
                            (
                                "Hidden",
                                "Creatures on the other plane can't perceive you unless they have a special ability that lets them perceive things on the Ethereal Plane",
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
                                "When",
                                "At the start of your next turn, and when the spell ends if you are on the Ethereal Plane",
                            ),
                            (
                                "Where",
                                "An unoccupied space of your choice that you can see within 10 feet of the space you left; if none is available within that range, the nearest unoccupied space",
                            ),
                        )
                    ),
                ),
            ),
        ]


class CacophonicShield(ClassSpell):
    rules = SpellRules(
        name="Cacophonic Shield",
        level=3,
        school=School.EVOCATION,
        classes=(CharacterClass.BARD, CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 10, concentration=True),
        source="Forgotten Realms - Heroes of Faerun",
        description=(
            "Thunderous reverberations fill a 10-foot Emanation originating from you for the duration. Whenever the Emanation enters a creature’s space and whenever a creature enters the Emanation or ends its turn there, the creature makes a Constitution saving throw. On a failed save, the creature takes 3d6 Thunder damage and has the Deafened condition until the start of your next turn. On a successful save, the creature takes half as much damage only. A creature makes this save only once per turn. When you cast this spell, you can designate creatures to be unaffected by it.\n"
            "In addition, you have Resistance to Thunder damage, and ranged attack rolls against you are made with Disadvantage.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 1d6 for each spell slot level above 3."
        ),
        usage_tags=("buff", "control", "damage", "heal"),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "f04197480e617622")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "Thunderous reverberations fill a 10-foot Emanation originating from you for the duration.",
                    ),
                    ("Area", "10-foot Emanation originating from you"),
                    (
                        "Unaffected",
                        "When you cast this spell, you can designate creatures to be unaffected by it",
                    ),
                    (
                        "Save",
                        "Constitution, whenever the Emanation enters a creature's space and whenever a creature enters the Emanation or ends its turn there; a creature makes this save only once per turn",
                    ),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (
                    (
                        "3d6 Thunder damage, and Deafened until the start of your next turn",
                        "Half as much damage only",
                    ),
                ),
            ),
            Facts(
                (
                    (
                        "You",
                        "You have Resistance to Thunder damage, and ranged attack rolls against you are made with Disadvantage",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Damage", "+1d6 for each spell slot level above 3"),)),),
            ),
        ]


class CallLightning(ClassSpell):
    rules = SpellRules(
        name="Call Lightning",
        level=3,
        school=School.CONJURATION,
        classes=(CharacterClass.DRUID,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 120),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 10, concentration=True),
        source="Player's Handbook",
        description=(
            "A storm cloud appears at a point within range that you can see above yourself. It takes the shape of a Cylinder that is 10 feet tall with a 60-foot radius.\n"
            "When you cast the spell, choose a point you can see under the cloud. A lightning bolt shoots from the cloud to that point. Each creature within 5 feet of that point makes a Dexterity saving throw, taking 3d10 Lightning damage on a failed save or half as much damage on a successful one.\n"
            "Until the spell ends, you can take a Magic action to call down lightning in that way again, targeting the same point or a different one.\n"
            "If you’re outdoors in a storm when you cast this spell, the spell gives you control over that storm instead of creating a new one. Under such conditions, the spell’s damage increases by 1d10.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 1d10 for each spell slot level above 3."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "0fa9f6c614fd7175")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "A storm cloud appears above you, and you call lightning down from it."
            ),
            Facts(
                (
                    (
                        "Cloud",
                        "A Cylinder 10 feet tall with a 60-foot radius, at a point within range that you can see above yourself",
                    ),
                    (
                        "Strike",
                        "When you cast the spell, choose a point you can see under the cloud; a lightning bolt shoots from the cloud to that point",
                    ),
                    (
                        "Save",
                        "Dexterity, made by each creature within 5 feet of that point",
                    ),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (("3d10 Lightning damage", "Half as much damage"),),
            ),
            Facts(
                (
                    (
                        "Again",
                        "Until the spell ends, you can take a Magic action to call down lightning in that way again, targeting the same point or a different one",
                    ),
                    (
                        "In a storm",
                        "If you're outdoors in a storm when you cast this spell, it gives you control over that storm instead of creating a new one, and the spell's damage increases by 1d10",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Damage", "+1d10 for each spell slot level above 3"),)),),
            ),
        ]


class Catnap(ClassSpell):
    rules = SpellRules(
        name="Catnap",
        level=3,
        school=School.ENCHANTMENT,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.BARD,
            CharacterClass.SORCERER,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 30),
        components=Components(somatic=True, material="a pinch of sand"),
        duration=Duration(DurationType.MINUTE, 10),
        source="Arcana Unleashed",
        description=(
            "You make a calming gesture, and up to three willing creatures of your choice that you can see within range have the Unconscious condition for the spell’s duration. The spell ends on a target if it takes damage or another creature takes an action to shake it awake. If a target has the Unconscious condition from this spell for the full duration, that target gains the benefits of finishing a Short Rest, and it can’t be affected by this spell again until it finishes a Long Rest.\n"
            "Using a Higher-Level Spell Slot. You can target one additional willing creature for each spell slot level above 3."
        ),
        usage_tags=("heal", "utility"),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "b50cd14febc5e9cb")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Targets",
                        "Up to three willing creatures of your choice that you can see within range",
                    ),
                    (
                        "Effect",
                        "Each target has the Unconscious condition for the spell’s duration",
                    ),
                    (
                        "Ends early",
                        "The spell ends on a target if it takes damage or another creature takes an action to shake it awake",
                    ),
                    (
                        "Full duration",
                        "If a target has the Unconscious condition from this spell for the full duration, that target gains the benefits of finishing a Short Rest",
                    ),
                    (
                        "Limit",
                        "That target can’t be affected by this spell again until it finishes a Long Rest",
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
                                "You can target one additional willing creature for each spell slot level above 3",
                            ),
                        )
                    ),
                ),
            ),
        ]


class Clairvoyance(ClassSpell):
    rules = SpellRules(
        name="Clairvoyance",
        level=3,
        school=School.DIVINATION,
        classes=(
            CharacterClass.BARD,
            CharacterClass.CLERIC,
            CharacterClass.SORCERER,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.MINUTE, 10),
        range=Range(RangeType.MILE, 1),
        components=Components(
            verbal=True,
            somatic=True,
            material="a focus worth 100+ GP, either a jeweled horn for hearing or a glass eye for seeing",
        ),
        duration=Duration(DurationType.MINUTE, 10, concentration=True),
        source="Player's Handbook",
        description=(
            "You create an Invisible sensor within range in a location familiar to you (a place you have visited or seen before) or in an obvious location that is unfamiliar to you (such as behind a door, around a corner, or in a grove of trees). The intangible, invulnerable sensor remains in place for the duration.\n"
            "When you cast the spell, choose seeing or hearing. You can use the chosen sense through the sensor as if you were in its space. As a Bonus Action, you can switch between seeing and hearing.\n"
            "A creature that sees the sensor (such as a creature benefiting from See Invisibility or Truesight) sees a luminous orb about the size of your fist."
        ),
        usage_tags=("buff",),
    )
    converted_from = RecordStamp("spells_dnd2024.json", "f2d0445d3282a262")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You create an Invisible sensor through which you can see or hear."
            ),
            Facts(
                (
                    (
                        "Location",
                        "Within range, in a location familiar to you (a place you have visited or seen before) or in an obvious location that is unfamiliar to you (such as behind a door, around a corner, or in a grove of trees)",
                    ),
                    (
                        "Sensor",
                        "Intangible and invulnerable; it remains in place for the duration",
                    ),
                    (
                        "Sense",
                        "Choose seeing or hearing when you cast the spell; you can use it through the sensor as if you were in its space",
                    ),
                    (
                        "Switching",
                        "As a Bonus Action, you can switch between seeing and hearing",
                    ),
                    (
                        "Seen as",
                        "A creature that sees the sensor (such as one benefiting from See Invisibility or Truesight) sees a luminous orb about the size of your fist",
                    ),
                )
            ),
        ]


class ConjureAnimals(ClassSpell):
    rules = SpellRules(
        name="Conjure Animals",
        level=3,
        school=School.CONJURATION,
        classes=(CharacterClass.DRUID, CharacterClass.RANGER),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 10, concentration=True),
        source="Player's Handbook",
        description=(
            "You conjure nature spirits that appear as a Large pack of spectral, intangible animals in an unoccupied space you can see within range. The pack lasts for the duration, and you choose the spirits’ animal form, such as wolves, serpents, or birds.\n"
            "You have Advantage on Strength saving throws while you’re within 5 feet of the pack, and when you move on your turn, you can also move the pack up to 30 feet to an unoccupied space you can see.\n"
            "Whenever the pack moves within 10 feet of a creature you can see and whenever a creature you can see enters a space within 10 feet of the pack or ends its turn there, you can force that creature to make a Dexterity saving throw. On a failed save, the creature takes 3d10 Slashing damage. A creature makes this save only once per turn.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 1d10 for each spell slot level above 3."
        ),
        usage_tags=("damage", "summon"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "9d6c93eb09530f4d")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You conjure nature spirits that appear as a Large pack of spectral, intangible animals."
            ),
            Facts(
                (
                    (
                        "Appears",
                        "In an unoccupied space you can see within range, for the duration",
                    ),
                    (
                        "Form",
                        "An animal form you choose, such as wolves, serpents, or birds",
                    ),
                    (
                        "Your saves",
                        "Advantage on Strength saving throws while you're within 5 feet of the pack",
                    ),
                    (
                        "Moving",
                        "When you move on your turn, you can also move the pack up to 30 feet to an unoccupied space you can see",
                    ),
                )
            ),
            Option(
                "Attacks",
                (
                    Facts(
                        (
                            (
                                "Trigger",
                                "Whenever the pack moves within 10 feet of a creature you can see, and whenever a creature you can see enters a space within 10 feet of the pack or ends its turn there, you can force that creature to make a Dexterity saving throw",
                            ),
                            ("Failed save", "3d10 Slashing damage"),
                            ("Successful save", "No damage"),
                            ("Limit", "A creature makes this save only once per turn"),
                        )
                    ),
                ),
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Damage", "+1d10 for each spell slot level above 3"),)),),
            ),
        ]


class ConjureBarrage(ClassSpell):
    rules = SpellRules(
        name="Conjure Barrage",
        level=3,
        school=School.CONJURATION,
        classes=(CharacterClass.RANGER,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(
            verbal=True,
            somatic=True,
            material="a Melee or Ranged weapon worth at least 1 CP",
        ),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "You brandish the weapon used to cast the spell and conjure similar spectral weapons (or ammunition appropriate to the weapon) that launch forward and then disappear. Each creature of your choice that you can see in a 60-foot Cone makes a Dexterity saving throw, taking 5d8 Force damage on a failed save or half as much damage on a successful one.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 1d8 for each spell slot level above 3."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "c5484f373a623d52")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You brandish the weapon used to cast the spell and conjure similar spectral weapons (or ammunition appropriate to the weapon) that launch forward and then disappear.",
                    ),
                    ("Area", "60-foot Cone"),
                    (
                        "Targets",
                        "Each creature of your choice that you can see in the Cone",
                    ),
                    ("Save", "Dexterity"),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (("5d8 Force damage", "Half as much damage"),),
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Damage", "+1d8 for each spell slot level above 3"),)),),
            ),
        ]


class ConjureConstructs(ClassSpell):
    rules = SpellRules(
        name="Conjure Constructs",
        level=3,
        school=School.CONJURATION,
        classes=(CharacterClass.WIZARD,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True, somatic=True, material="a brass cog"),
        duration=Duration(DurationType.MINUTE, 10, concentration=True),
        source="Forgotten Realms - Heroes of Faerun",
        description=(
            "You conjure a group of intangible, orderly spirits that appear as a Medium group of modrons or other Constructs in an unoccupied space you can see within range. The spirits last for the duration.\n"
            "When you cast this spell and as a Magic action on subsequent turns, you can command the spirits to target one creature or object you can see within 5 feet of the spirits and create one of the following effects:\n"
            "Clockwork Force. The target makes a Dexterity saving throw, taking 3d6 Force damage on a failed save or half as much damage on a successful one.\n"
            "Orderly Ward. The target gains Temporary Hit Points equal to 1d6 plus your spellcasting ability modifier.\n"
            "When you move on your turn, you can also move the spirits up to 30 feet to an unoccupied space you can see.\n"
            "Using a Higher-Level Spell Slot. The damage and Temporary Hit Points both increase by 1d6 for each spell slot level above 3."
        ),
        usage_tags=("heal",),
        target=FeatureTarget.CREATURE,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "57d95ddd76d7fb13")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You conjure intangible, orderly spirits that appear as a Medium group of modrons or other Constructs."
            ),
            Facts(
                (
                    (
                        "Appears",
                        "In an unoccupied space you can see within range, for the duration",
                    ),
                    (
                        "Moving",
                        "When you move on your turn, you can also move the spirits up to 30 feet to an unoccupied space you can see",
                    ),
                    (
                        "Commanding",
                        "When you cast this spell and as a Magic action on subsequent turns, you can command the spirits to target one creature or object you can see within 5 feet of them with one of the effects below",
                    ),
                )
            ),
            Option(
                "Clockwork Force",
                (
                    Facts(
                        (
                            ("Save", "Dexterity"),
                            ("Failed save", "3d6 Force damage"),
                            ("Successful save", "Half as much damage"),
                        )
                    ),
                ),
            ),
            Option(
                "Orderly Ward",
                (
                    Facts(
                        (
                            (
                                "Effect",
                                "The target gains Temporary Hit Points equal to 1d6 + your spellcasting ability modifier",
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
                                "The damage and Temporary Hit Points both increase by 1d6 for each spell slot level above 3",
                            ),
                        )
                    ),
                ),
            ),
        ]


class Counterspell(ClassSpell):
    rules = SpellRules(
        name="Counterspell",
        level=3,
        school=School.ABJURATION,
        classes=(
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(
            CastingTimeType.REACTION,
            trigger="which you take when you see a creature within 60 feet of yourself casting a spell with Verbal, Somatic, or Material components",
        ),
        range=Range(RangeType.FOOT, 60),
        components=Components(somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description="You attempt to interrupt a creature in the process of casting a spell. The creature makes a Constitution saving throw. On a failed save, the spell dissipates with no effect, and the action, Bonus Action, or Reaction used to cast it is wasted. If that spell was cast with a spell slot, the slot isn’t expended.",
        usage_tags=("control",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "6846cc9748298e87")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You attempt to interrupt a creature in the process of casting a spell."
            ),
            Facts(
                (
                    (
                        "Trigger",
                        "You see a creature within 60 feet of yourself casting a spell with Verbal, Somatic, or Material components",
                    ),
                    ("Save", "Constitution, made by the caster"),
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
        ]


class CreateFoodAndWater(ClassSpell):
    rules = SpellRules(
        name="Create Food and Water",
        level=3,
        school=School.CONJURATION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.CLERIC,
            CharacterClass.PALADIN,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 30),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description="You create 45 pounds of food and 30 gallons of fresh water on the ground or in containers within range - both useful in fending off the hazards of malnutrition and dehydration. The food is bland but nourishing and looks like a food of your choice, and the water is clean. The food spoils after 24 hours if uneaten.",
        usage_tags=("utility",),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "e231d8ffc1f96561")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You create food and water, useful in fending off the hazards of malnutrition and dehydration."
            ),
            Facts(
                (
                    (
                        "Creates",
                        "45 pounds of food and 30 gallons of fresh water, on the ground or in containers within range",
                    ),
                    (
                        "Food",
                        "Bland but nourishing, and looks like a food of your choice; it spoils after 24 hours if uneaten",
                    ),
                    ("Water", "Clean"),
                )
            ),
        ]


class CrusadersMantle(ClassSpell):
    rules = SpellRules(
        name="Crusader's Mantle",
        level=3,
        school=School.EVOCATION,
        classes=(CharacterClass.PALADIN,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description="You radiate a magical aura in a 30-foot Emanation. While in the aura, you and your allies each deal an extra 1d4 Radiant damage when hitting with a weapon or an Unarmed Strike.",
        usage_tags=("buff", "damage"),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "6877e4c35803156f")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You radiate a magical aura that empowers your and your allies' strikes."
            ),
            Facts(
                (
                    ("Area", "30-foot Emanation"),
                    (
                        "Effect",
                        "While in the aura, you and your allies each deal an extra 1d4 Radiant damage when hitting with a weapon or an Unarmed Strike",
                    ),
                )
            ),
        ]


class Daylight(ClassSpell):
    rules = SpellRules(
        name="Daylight",
        level=3,
        school=School.EVOCATION,
        classes=(
            CharacterClass.CLERIC,
            CharacterClass.DRUID,
            CharacterClass.PALADIN,
            CharacterClass.RANGER,
            CharacterClass.SORCERER,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.HOUR, 1),
        source="Player's Handbook",
        description=(
            "For the duration, sunlight spreads from a point within range and fills a 60-foot-radius Sphere. The sunlight’s area is Bright Light and sheds Dim Light for an additional 60 feet.\n"
            "Alternatively, you cast the spell on an object that isn’t being worn or carried, causing the sunlight to fill a 60-foot Emanation originating from that object. Covering that object with something opaque, such as a bowl or helm, blocks the sunlight.\n"
            "If any of this spell’s area overlaps with an area of Darkness created by a spell of level 3 or lower, that other spell is dispelled."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "70066e113bcd274d")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("For the duration, sunlight spreads from a point or an object."),
            Facts(
                (
                    (
                        "Area",
                        "60-foot-radius Sphere spreading from a point within range",
                    ),
                    (
                        "Light",
                        "The sunlight's area is Bright Light and sheds Dim Light for an additional 60 feet",
                    ),
                    (
                        "Or",
                        "Cast on an object that isn't being worn or carried, the sunlight fills a 60-foot Emanation originating from that object; covering the object with something opaque, such as a bowl or helm, blocks the sunlight",
                    ),
                    (
                        "Dispels",
                        "If any of this spell's area overlaps with an area of Darkness created by a spell of level 3 or lower, that other spell is dispelled",
                    ),
                )
            ),
        ]


class DispelMagic(ClassSpell):
    rules = SpellRules(
        name="Dispel Magic",
        level=3,
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
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 120),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "Choose one creature, object, or magical effect within range. Any ongoing spell of level 3 or lower on the target ends. For each ongoing spell of level 4 or higher on the target, make an ability check using your spellcasting ability (DC 10 plus that spell’s level). On a successful check, the spell ends.\n"
            "Using a Higher-Level Spell Slot. You automatically end a spell on the target if the spell’s level is equal to or less than the level of the spell slot you use."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.CREATURE,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "1f8815625563cd25")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You end spells on a creature, an object, or a magical effect."),
            Facts(
                (
                    ("Target", "One creature, object, or magical effect within range"),
                    (
                        "Level 3 or lower",
                        "Any ongoing spell of level 3 or lower on the target ends",
                    ),
                    (
                        "Level 4 or higher",
                        "For each such spell, make an ability check using your spellcasting ability (DC 10 + that spell's level); on a successful check, the spell ends",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (
                    Facts(
                        (
                            (
                                "Automatic",
                                "You automatically end a spell on the target if the spell's level is equal to or less than the level of the spell slot you use",
                            ),
                        )
                    ),
                ),
            ),
        ]


class ElementalWeapon(ClassSpell):
    rules = SpellRules(
        name="Elemental Weapon",
        level=3,
        school=School.TRANSMUTATION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.DRUID,
            CharacterClass.PALADIN,
            CharacterClass.RANGER,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.TOUCH),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.HOUR, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "A nonmagical weapon you touch becomes a magic weapon. Choose one of the following damage types: Acid, Cold, Fire, Lightning, or Thunder. For the duration, the weapon has a +1 bonus to attack rolls and deals an extra 1d4 damage of the chosen type when it hits.\n"
            "Using a Higher-Level Spell Slot. If you use a level 5–6 spell slot, the bonus to attack rolls increases to +2, and the extra damage increases to 2d4. If you use a level 7+ spell slot, the bonus increases to +3, and the extra damage increases to 3d4."
        ),
        usage_tags=("buff", "damage"),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "a6c0acca704c144c")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("A nonmagical weapon you touch becomes a magic weapon."),
            Facts(
                (
                    ("Damage type", "Choose Acid, Cold, Fire, Lightning, or Thunder"),
                    (
                        "Effect",
                        "For the duration, the weapon has a +1 bonus to attack rolls and deals an extra 1d4 damage of the chosen type when it hits",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (
                    Table(
                        ("Slot level", "Attack bonus", "Extra damage"),
                        (
                            ("3-4", "+1", "1d4"),
                            ("5-6", "+2", "2d4"),
                            ("7+", "+3", "3d4"),
                        ),
                    ),
                ),
            ),
        ]


class EnemiesAbound(ClassSpell):
    rules = SpellRules(
        name="Enemies Abound",
        level=3,
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
        source="Xanathar's Guide to Everything",
        description=(
            "You reach into the mind of one creature you can see and force it to make an Intelligence saving throw. A creature automatically succeeds if it is immune to being frightened. On a failed save, the target loses the ability to distinguish friend from foe, regarding all creatures it can see as enemies until the spell ends. Each time the target takes damage, it can repeat the saving throw, ending the effect on itself on a success.\n"
            "Whenever the affected creature chooses another creature as a target, it must choose the target at random from among the creatures it can see within range of the attack, spell, or other ability it's using. If an enemy provokes an opportunity attack from the affected creature, the creature must make that attack if it is able to."
        ),
        usage_tags=("control", "damage", "utility"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "deb52bde27f9dcbc")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Flavor", "You reach into the mind of one creature you can see."),
                    ("Target", "One creature you can see"),
                    (
                        "Save",
                        "Intelligence; a creature automatically succeeds if it is immune to being frightened",
                    ),
                    (
                        "Failed save",
                        "The target loses the ability to distinguish friend from foe, regarding all creatures it can see as enemies until the spell ends",
                    ),
                    (
                        "Repeat save",
                        "Each time the target takes damage, it can repeat the saving throw, ending the effect on itself on a success",
                    ),
                    (
                        "Choosing targets",
                        "Whenever it chooses another creature as a target, it must choose at random from among the creatures it can see within range of the attack, spell, or other ability it's using",
                    ),
                    (
                        "Opportunity attacks",
                        "If an enemy provokes an opportunity attack from it, it must make that attack if it is able to",
                    ),
                )
            )
        ]


class EruptingEarth(ClassSpell):
    rules = SpellRules(
        name="Erupting Earth",
        level=3,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.DRUID, CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 120),
        components=Components(
            verbal=True, somatic=True, material="a piece of obsidian"
        ),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Xanathar's Guide to Everything/Elemental Evil Player's Companion",
        description=(
            "Choose a point you can see on the ground within range. A fountain of churned earth and stone erupts in a 20-foot cube centered on that point. Each creature in that area must make a Dexterity saving throw. A creature takes 3d12 bludgeoning damage on a failed save, or half as much damage on a successful one. Additionally, the ground in that area becomes difficult terrain until cleared away. Each 5-foot-square portion of the area requires at least 1 minute to clear by hand.\n"
            "At Higher Levels. When you cast this spell using a spell slot of 4th level or higher, the damage increases by 1d12 for each slot level above 3rd."
        ),
        usage_tags=("buff", "control", "damage", "utility"),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "557faf75b1164e3a")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "A fountain of churned earth and stone erupts in a 20-foot cube centered on that point.",
                    ),
                    (
                        "Area",
                        "20-foot cube centered on a point you can see on the ground within range",
                    ),
                    ("Save", "Dexterity, made by each creature in the area"),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (("3d12 Bludgeoning damage", "Half as much damage"),),
            ),
            Facts(
                (
                    (
                        "Terrain",
                        "The ground in the area becomes Difficult Terrain until cleared away; each 5-foot-square portion requires at least 1 minute to clear by hand",
                    ),
                )
            ),
            Option(
                "At Higher Levels",
                (Facts((("Damage", "+1d12 for each slot level above 3rd"),)),),
            ),
        ]


class FastFriends(ClassSpell):
    rules = SpellRules(
        name="Fast Friends",
        level=3,
        school=School.ENCHANTMENT,
        classes=(),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 30),
        components=Components(verbal=True),
        duration=Duration(DurationType.HOUR, 1, concentration=True),
        source="Acquisitions Inc.",
        description=(
            "When you cast this spell, choose one humanoid within range that can see and hear you, and that can understand you. The creature must succeed on a Wisdom saving throw or become charmed by you for the duration. While the creature is charmed in this way, it undertakes to perform any services or activities you ask of it in a friendly manner, to the best of its ability.\n"
            "You can set the creature new tasks when a previous task is completed, or if you decide to end its current task. If the service or activity might cause harm to the creature, or if it conflicts with the creature's normal activities and desires, the creature can make another Wisdom saving throw to try to end the effect. This save is made with advantage if you or your companions are fighting the creature. If the activity would result in certain death for the creature, the spell ends.\n"
            "When the spell ends, the creature knows it was charmed by you.\n"
            "At Higher Levels: When you cast this spell using a spell slot of 4th level or higher, you can target one additional creature for each slot level above 3rd.\n"
            "Spell Lists: Bard , Cleric , Wizard"
        ),
        usage_tags=("damage", "utility"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "d45d18ec4b44a296")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You charm a humanoid into performing services for you."),
            Facts(
                (
                    (
                        "Target",
                        "One humanoid within range that can see and hear you, and that can understand you",
                    ),
                    ("Save", "Wisdom"),
                    ("Failed save", "Charmed by you for the duration"),
                    (
                        "Services",
                        "While charmed this way, it undertakes to perform any services or activities you ask of it in a friendly manner, to the best of its ability",
                    ),
                    (
                        "New tasks",
                        "You can set the creature new tasks when a previous task is completed, or if you decide to end its current task",
                    ),
                    (
                        "Resisting",
                        "If the service or activity might cause harm to the creature, or conflicts with its normal activities and desires, it can make another Wisdom saving throw to try to end the effect, with Advantage if you or your companions are fighting it",
                    ),
                    (
                        "Certain death",
                        "If the activity would result in certain death for the creature, the spell ends",
                    ),
                    (
                        "Afterward",
                        "When the spell ends, the creature knows it was charmed by you",
                    ),
                )
            ),
            Option(
                "At Higher Levels",
                (Facts((("Targets", "+1 creature for each slot level above 3rd"),)),),
            ),
        ]


class Fear(ClassSpell):
    rules = SpellRules(
        name="Fear",
        level=3,
        school=School.ILLUSION,
        classes=(
            CharacterClass.BARD,
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True, material="a white feather"),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "Each creature in a 30-foot Cone must succeed on a Wisdom saving throw or drop whatever it is holding and have the Frightened condition for the duration.\n"
            "A Frightened creature takes the Dash action and moves away from you by the safest route on each of its turns unless there is nowhere to move. If the creature ends its turn in a space where it doesn’t have line of sight to you, the creature makes a Wisdom saving throw. On a successful save, the spell ends on that creature."
        ),
        usage_tags=("control",),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "5e6e1a387b8b0920")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Area", "30-foot Cone"),
                    ("Save", "Wisdom, made by each creature in the Cone"),
                    (
                        "Failed save",
                        "It drops whatever it is holding and has the Frightened condition for the duration",
                    ),
                    ("Successful save", "No effect"),
                )
            ),
            Option(
                "While Frightened",
                (
                    Facts(
                        (
                            (
                                "Fleeing",
                                "The creature takes the Dash action and moves away from you by the safest route on each of its turns, unless there is nowhere to move",
                            ),
                            (
                                "Repeat save",
                                "If it ends its turn in a space where it doesn't have line of sight to you, it makes a Wisdom saving throw; on a success, the spell ends on that creature",
                            ),
                        )
                    ),
                ),
            ),
        ]


class FeignDeath(ClassSpell):
    rules = SpellRules(
        name="Feign Death",
        level=3,
        school=School.NECROMANCY,
        classes=(
            CharacterClass.BARD,
            CharacterClass.CLERIC,
            CharacterClass.DRUID,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION, ritual=True),
        range=Range(RangeType.TOUCH),
        components=Components(
            verbal=True, somatic=True, material="a pinch of graveyard dirt"
        ),
        duration=Duration(DurationType.HOUR, 1),
        source="Player's Handbook",
        description=(
            "You touch a willing creature and put it into a cataleptic state that is indistinguishable from death.\n"
            "For the duration, the target appears dead to outward inspection and to spells used to determine the target’s status. The target has the Blinded and Incapacitated conditions, and its Speed is 0.\n"
            "The target also has Resistance to all damage except Psychic damage, and it has Immunity to the Poisoned condition."
        ),
        usage_tags=("buff",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "58f89090d925dd54")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You touch a willing creature and put it into a cataleptic state that is indistinguishable from death."
            ),
            Facts(
                (
                    (
                        "Appearance",
                        "For the duration, the target appears dead to outward inspection and to spells used to determine its status",
                    ),
                    (
                        "Conditions",
                        "The target has the Blinded and Incapacitated conditions, and its Speed is 0",
                    ),
                    ("Resistance", "To all damage except Psychic damage"),
                    ("Immunity", "To the Poisoned condition"),
                )
            ),
        ]


class FlameArrows(ClassSpell):
    rules = SpellRules(
        name="Flame Arrows",
        level=3,
        school=School.TRANSMUTATION,
        classes=(
            CharacterClass.DRUID,
            CharacterClass.RANGER,
            CharacterClass.SORCERER,
            CharacterClass.WIZARD,
            CharacterClass.ARTIFICER,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.TOUCH),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.HOUR, 1, concentration=True),
        source="Xanathar's Guide to Everything",
        description=(
            "You touch a quiver containing arrows or bolts. When a target is hit by a ranged weapon attack using a piece of ammunition drawn from the quiver, the target takes an extra 1d6 fire damage. The spell's magic ends on the piece of ammunition when it hits or misses, and the spell ends when twelve pieces of ammunition have been drawn from the quiver.\n"
            "At Higher Levels. When you cast this spell using a spell slot of 4th level or higher, the number of pieces of ammunition you can affect with this spell increases by two for each slot level above 3rd."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "df8a47f1b2515572")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You touch a quiver containing arrows or bolts."),
            Facts(
                (
                    (
                        "Extra damage",
                        "When a target is hit by a ranged weapon attack using a piece of ammunition drawn from the quiver, it takes an extra 1d6 Fire damage",
                    ),
                    (
                        "Each piece",
                        "The spell's magic ends on the piece of ammunition when it hits or misses",
                    ),
                    (
                        "Ends",
                        "When twelve pieces of ammunition have been drawn from the quiver",
                    ),
                )
            ),
            Option(
                "At Higher Levels",
                (Facts((("Ammunition", "+2 pieces for each slot level above 3rd"),)),),
            ),
        ]


class Fly(ClassSpell):
    rules = SpellRules(
        name="Fly",
        level=3,
        school=School.TRANSMUTATION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.TOUCH),
        components=Components(verbal=True, somatic=True, material="a feather"),
        duration=Duration(DurationType.MINUTE, 10, concentration=True),
        source="Player's Handbook",
        description=(
            "You touch a willing creature. For the duration, the target gains a Fly Speed of 60 feet and can hover. When the spell ends, the target falls if it is still aloft unless it can stop the fall.\n"
            "Using a Higher-Level Spell Slot. You can target one additional creature for each spell slot level above 3."
        ),
        usage_tags=("buff",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "e1813e79d1435943")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You touch a willing creature and grant it flight."),
            Facts(
                (
                    (
                        "Effect",
                        "For the duration, the target gains a Fly Speed of 60 feet and can hover",
                    ),
                    (
                        "Spell ends",
                        "The target falls if it is still aloft, unless it can stop the fall",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (
                    Facts(
                        (("Targets", "+1 creature for each spell slot level above 3"),)
                    ),
                ),
            ),
        ]


class GaldersTower(ClassSpell):
    rules = SpellRules(
        name="Galder's Tower",
        level=3,
        school=School.CONJURATION,
        classes=(CharacterClass.WIZARD,),
        casting_time=CastingTime(CastingTimeType.MINUTE, 10),
        range=Range(RangeType.FOOT, 30),
        components=Components(
            verbal=True,
            somatic=True,
            material="a fragment of stone, wood, or other building material",
        ),
        duration=Duration(DurationType.HOUR, 24),
        source="Lost Laboratory of Kwalish",
        description=(
            "You conjure a two-story tower made of stone, wood, or similar suitably sturdy materials. The tower can be round or square in shape. Each level of the tower is 10 feet tall and has an area of up to 100 square feet. Access between levels consists of a simple ladder and hatch. Each level takes one of the following forms, chosen by you when you cast the spell:\n"
            "A bedroom with a bed, chairs, chest, and magical fireplace\n"
            "A study with desks, books, bookshelves, parchments, ink, and ink pens\n"
            "A dining space with a table, chairs, magical fireplace, containers, and cooking utensils\n"
            "A lounge with couches, armchairs, side tables and footstools\n"
            "A washroom with toilets, washtubs, a magical brazier, and sauna benches\n"
            "An observatory with a telescope and maps of the night sky\n"
            "An unfurnished, empty room\n"
            "The interior of the tower is warm and dry, regardless of conditions outside. Any equipment or furnishings conjured with the tower dissipate into smoke if removed from it. At the end of the spell's duration, all creatures and objects within the tower that were not created by the spell appear safely outside on the ground, and all traces of the tower and its furnishings disappear.\n"
            "You can cast this spell again while it is active to maintain the tower's existence for another 24 hours. You can create a permanent tower by casting this spell in the same location and with the same configuration every day for one year.\n"
            "At Higher Levels. When you cast this spell using a spell slot of 4th level or higher, the tower can have one additional story for each slot level beyond 3rd."
        ),
        usage_tags=("utility", "summon"),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "3dc46ee7321e0ef0")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You conjure a two-story tower made of stone, wood, or similar suitably sturdy materials."
            ),
            Facts(
                (
                    ("Shape", "Round or square"),
                    (
                        "Each level",
                        "10 feet tall, with an area of up to 100 square feet; access between levels is a simple ladder and hatch",
                    ),
                    ("Interior", "Warm and dry, regardless of conditions outside"),
                    (
                        "Furnishings",
                        "Any equipment or furnishings conjured with the tower dissipate into smoke if removed from it",
                    ),
                    (
                        "Spell ends",
                        "All creatures and objects within the tower that were not created by the spell appear safely outside on the ground, and all traces of the tower and its furnishings disappear",
                    ),
                    (
                        "Extending",
                        "You can cast this spell again while it is active to maintain the tower's existence for another 24 hours",
                    ),
                    (
                        "Permanent",
                        "You can create a permanent tower by casting this spell in the same location and with the same configuration every day for one year",
                    ),
                )
            ),
            Table(
                ("Level form", "Contents"),
                (
                    ("Bedroom", "A bed, chairs, chest, and magical fireplace"),
                    (
                        "Study",
                        "Desks, books, bookshelves, parchments, ink, and ink pens",
                    ),
                    (
                        "Dining space",
                        "A table, chairs, magical fireplace, containers, and cooking utensils",
                    ),
                    ("Lounge", "Couches, armchairs, side tables, and footstools"),
                    (
                        "Washroom",
                        "Toilets, washtubs, a magical brazier, and sauna benches",
                    ),
                    ("Observatory", "A telescope and maps of the night sky"),
                    ("Empty", "An unfurnished, empty room"),
                ),
            ),
            Option(
                "At Higher Levels",
                (Facts((("Stories", "+1 story for each slot level beyond 3rd"),)),),
            ),
        ]


class GaseousForm(ClassSpell):
    rules = SpellRules(
        name="Gaseous Form",
        level=3,
        school=School.TRANSMUTATION,
        classes=(
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.TOUCH),
        components=Components(verbal=True, somatic=True, material="a bit of gauze"),
        duration=Duration(DurationType.HOUR, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "A willing creature you touch shape-shifts, along with everything it’s wearing and carrying, into a misty cloud for the duration. The spell ends on the target if it drops to 0 Hit Points or if it takes a Magic action to end the spell on itself.\n"
            "While in this form, the target’s only method of movement is a Fly Speed of 10 feet, and it can hover. The target can enter and occupy the space of another creature. The target has Resistance to Bludgeoning, Piercing, and Slashing damage; it has Immunity to the Prone condition; and it has Advantage on Strength, Dexterity, and Constitution saving throws. The target can pass through narrow openings, but it treats liquids as though they were solid surfaces.\n"
            "The target can’t talk or manipulate objects, and any objects it was carrying or holding can’t be dropped, used, or otherwise interacted with. Finally, the target can’t attack or cast spells.\n"
            "Using a Higher-Level Spell Slot. You can target one additional creature for each spell slot level above 3."
        ),
        usage_tags=("buff",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "f2d88e8bac69a9b9")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "A willing creature you touch shape-shifts, along with everything it's wearing and carrying, into a misty cloud for the duration."
            ),
            Facts(
                (
                    (
                        "Movement",
                        "Its only method of movement is a Fly Speed of 10 feet, and it can hover",
                    ),
                    (
                        "Spaces",
                        "It can enter and occupy the space of another creature, and pass through narrow openings, but it treats liquids as though they were solid surfaces",
                    ),
                    ("Resistance", "To Bludgeoning, Piercing, and Slashing damage"),
                    ("Immunity", "To the Prone condition"),
                    (
                        "Saves",
                        "Advantage on Strength, Dexterity, and Constitution saving throws",
                    ),
                    (
                        "Can't",
                        "Talk, manipulate objects, attack, or cast spells; any objects it was carrying or holding can't be dropped, used, or otherwise interacted with",
                    ),
                    (
                        "Ends early",
                        "If the target drops to 0 Hit Points, or if it takes a Magic action to end the spell on itself",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (
                    Facts(
                        (("Targets", "+1 creature for each spell slot level above 3"),)
                    ),
                ),
            ),
        ]


class GlyphOfWarding(ClassSpell):
    rules = SpellRules(
        name="Glyph of Warding",
        level=3,
        school=School.ABJURATION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.BARD,
            CharacterClass.CLERIC,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.HOUR, 1),
        range=Range(RangeType.TOUCH),
        components=Components(
            verbal=True,
            somatic=True,
            material="powdered diamond worth 200+ GP, which the spell consumes",
        ),
        duration=Duration(DurationType.UNTIL_DISPELLED_OR_TRIGGERED),
        source="Player's Handbook",
        description=(
            "You inscribe a glyph that later unleashes a magical effect. You inscribe it either on a surface (such as a table or a section of floor) or within an object that can be closed (such as a book or chest) to conceal the glyph. The glyph can cover an area no larger than 10 feet in diameter. If the surface or object is moved more than 10 feet from where you cast this spell, the glyph is broken, and the spell ends without being triggered.\n"
            "The glyph is nearly imperceptible and requires a successful Wisdom (Perception) check against your spell save DC to notice.\n"
            "When you inscribe the glyph, you set its trigger and choose whether it’s an explosive rune or a spell glyph, as explained below.\n"
            "Set the Trigger. You decide what triggers the glyph when you cast the spell. For glyphs inscribed on a surface, common triggers include touching or stepping on the glyph, removing another object covering it, or approaching within a certain distance of it. For glyphs inscribed within an object, common triggers include opening that object or seeing the glyph. Once a glyph is triggered, this spell ends.\n"
            "You can refine the trigger so that only creatures of certain types activate it (for example, the glyph could be set to affect Aberrations). You can also set conditions for creatures that don’t trigger the glyph, such as those who say a certain password.\n"
            "Explosive Rune. When triggered, the glyph erupts with magical energy in a 20-foot-radius Sphere centered on the glyph. Each creature in the area makes a Dexterity saving throw. A creature takes 5d8 Acid, Cold, Fire, Lightning, or Thunder damage (your choice when you create the glyph) on a failed save or half as much damage on a successful one.\n"
            "Spell Glyph. You can store a prepared spell of level 3 or lower in the glyph by casting it as part of creating the glyph. The spell must target a single creature or an area. The spell being stored has no immediate effect when cast in this way.\n"
            "When the glyph is triggered, the stored spell takes effect. If the spell has a target, it targets the creature that triggered the glyph. If the spell affects an area, the area is centered on that creature. If the spell summons Hostile creatures or creates harmful objects or traps, they appear as close as possible to the intruder and attack it. If the spell requires Concentration, it lasts until the end of its full duration.\n"
            "Using a Higher-Level Spell Slot. The damage of an explosive rune increases by 1d8 for each spell slot level above 3. If you create a spell glyph, you can store any spell of up to the same level as the spell slot you use for the Glyph of Warding."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "d0febe59f443bb22")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You inscribe a glyph that later unleashes a magical effect."),
            Facts(
                (
                    (
                        "Where",
                        "On a surface (such as a table or a section of floor) or within an object that can be closed (such as a book or chest) to conceal the glyph",
                    ),
                    ("Size", "An area no larger than 10 feet in diameter"),
                    (
                        "Moved",
                        "If the surface or object is moved more than 10 feet from where you cast this spell, the glyph is broken, and the spell ends without being triggered",
                    ),
                    (
                        "Noticing it",
                        "The glyph is nearly imperceptible and requires a successful Wisdom (Perception) check against your spell save DC to notice",
                    ),
                    (
                        "Type",
                        "When you inscribe the glyph, you set its trigger and choose whether it's an explosive rune or a spell glyph",
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
                                "Common triggers include touching or stepping on the glyph, removing another object covering it, or approaching within a certain distance of it",
                            ),
                            (
                                "In an object",
                                "Common triggers include opening that object or seeing the glyph",
                            ),
                            (
                                "Refining",
                                "You can refine the trigger so that only creatures of certain types activate it (for example, Aberrations), and set conditions for creatures that don't trigger it, such as those who say a certain password",
                            ),
                            ("Triggered", "Once a glyph is triggered, this spell ends"),
                        )
                    ),
                ),
            ),
            Option(
                "Explosive Rune",
                (
                    Facts(
                        (
                            ("Area", "20-foot-radius Sphere centered on the glyph"),
                            ("Save", "Dexterity, made by each creature in the area"),
                            (
                                "Failed save",
                                "5d8 Acid, Cold, Fire, Lightning, or Thunder damage (your choice when you create the glyph)",
                            ),
                            ("Successful save", "Half as much damage"),
                        )
                    ),
                ),
            ),
            Option(
                "Spell Glyph",
                (
                    Facts(
                        (
                            (
                                "Storing",
                                "You can store a prepared spell of level 3 or lower in the glyph by casting it as part of creating the glyph; it must target a single creature or an area, and it has no immediate effect when cast this way",
                            ),
                            (
                                "Triggered",
                                "The stored spell takes effect; if it has a target, it targets the creature that triggered the glyph, and if it affects an area, the area is centered on that creature",
                            ),
                            (
                                "Summons",
                                "If the spell summons Hostile creatures or creates harmful objects or traps, they appear as close as possible to the intruder and attack it",
                            ),
                            (
                                "Concentration",
                                "If the spell requires Concentration, it lasts until the end of its full duration",
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
                                "Explosive rune",
                                "Its damage increases by 1d8 for each spell slot level above 3",
                            ),
                            (
                                "Spell glyph",
                                "You can store any spell of up to the same level as the spell slot you use for the Glyph of Warding",
                            ),
                        )
                    ),
                ),
            ),
        ]


class Haste(ClassSpell):
    rules = SpellRules(
        name="Haste",
        level=3,
        school=School.TRANSMUTATION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.SORCERER,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 30),
        components=Components(
            verbal=True, somatic=True, material="a shaving of licorice root"
        ),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "Choose a willing creature that you can see within range. Until the spell ends, the target’s Speed is doubled, it gains a +2 bonus to Armor Class, it has Advantage on Dexterity saving throws, and it gains an additional action on each of its turns. That action can be used to take only the Attack (one attack only), Dash, Disengage, Hide, or Utilize action.\n"
            "When the spell ends, the target is Incapacitated and has a Speed of 0 until the end of its next turn, as a wave of lethargy washes over it."
        ),
        usage_tags=("buff",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "cf95f9e1af96e68d")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "Until the spell ends, a willing creature you can see within range moves and acts faster."
            ),
            Facts(
                (
                    ("Speed", "Doubled"),
                    ("AC", "+2 bonus to Armor Class"),
                    ("Saves", "Advantage on Dexterity saving throws"),
                    (
                        "Extra action",
                        "An additional action on each of its turns, which can be used to take only the Attack (one attack only), Dash, Disengage, Hide, or Utilize action",
                    ),
                    (
                        "Spell ends",
                        "The target is Incapacitated and has a Speed of 0 until the end of its next turn, as a wave of lethargy washes over it",
                    ),
                )
            ),
        ]

    def combat_effects(
        self, character: CharacterView | None = None
    ) -> list[CombatEffect]:
        next_turn = (TurnEdge.END, TurnOf.TARGET)
        return [
            CombatEffect(
                conditions=(
                    CombatCondition(
                        "Haste",
                        modifiers=(
                            Speed(multiplier=2),
                            ArmorClass(2),
                            D20Mode(
                                (D20Test.SAVING_THROW,),
                                RollMode.ADVANTAGE,
                                (Ability.DEXTERITY,),
                            ),
                            Note(
                                "An additional action on each of its turns: the"
                                " Attack (one attack only), Dash, Disengage, Hide"
                                " or Utilize action only."
                            ),
                        ),
                    ),
                ),
                notes=("When the spell ends, pick Haste: lethargy for the target.",),
            ),
            CombatEffect(
                name="Haste: lethargy",
                conditions=(
                    CombatCondition(Condition.INCAPACITATED, until=next_turn),
                    CombatCondition(
                        "Haste",
                        until=next_turn,
                        modifiers=(Speed(set_to=0),),
                    ),
                ),
                spends_use=False,
                notes=(
                    "As Haste ends on the target: its badge then gives a Speed of 0 instead. Part of the same casting: it spends no slot.",
                ),
            ),
        ]


class HungerOfHadar(ClassSpell):
    rules = SpellRules(
        name="Hunger of Hadar",
        level=3,
        school=School.CONJURATION,
        classes=(CharacterClass.WARLOCK,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 150),
        components=Components(verbal=True, somatic=True, material="a pickled tentacle"),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "You open a gateway to the Far Realm, a region infested with unspeakable horrors. A 20-foot-radius Sphere of Darkness appears, centered on a point with range and lasting for the duration. The Sphere is Difficult Terrain, and it is filled with strange whispers and slurping noises, which can be heard up to 30 feet away. No light, magical or otherwise, can illuminate the area, and creatures fully within it have the Blinded condition.\n"
            "Any creature that starts its turn in the area takes 2d6 Cold damage. Any creature that ends its turn there must succeed on a Dexterity saving throw or take 2d6 Acid damage from otherworldly tentacles.\n"
            "Using a Higher-Level Spell Slot. The Cold or Acid damage (your choice) increases by 1d6 for each spell slot level above 3."
        ),
        usage_tags=("control", "damage"),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "496550e6532b9cdf")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You open a gateway to the Far Realm, a region infested with unspeakable horrors.",
                    ),
                    (
                        "Area",
                        "20-foot-radius Sphere of Darkness centered on a point within range, lasting for the duration",
                    ),
                    ("Terrain", "The Sphere is Difficult Terrain"),
                    (
                        "Sound",
                        "Strange whispers and slurping noises, which can be heard up to 30 feet away",
                    ),
                    (
                        "Light",
                        "No light, magical or otherwise, can illuminate the area",
                    ),
                    ("Blinded", "Creatures fully within it have the Blinded condition"),
                )
            ),
            Facts(
                (
                    (
                        "Start of turn",
                        "Any creature that starts its turn in the area takes 2d6 Cold damage",
                    ),
                    (
                        "End of turn",
                        "Any creature that ends its turn there must succeed on a Dexterity saving throw or take 2d6 Acid damage from otherworldly tentacles",
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
                                "The Cold or Acid damage (your choice) increases by 1d6 for each spell slot level above 3",
                            ),
                        )
                    ),
                ),
            ),
        ]


class HypnoticPattern(ClassSpell):
    rules = SpellRules(
        name="Hypnotic Pattern",
        level=3,
        school=School.ILLUSION,
        classes=(
            CharacterClass.BARD,
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 120),
        components=Components(somatic=True, material="a pinch of confetti"),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "You create a twisting pattern of colors in a 30-foot Cube within range. The pattern appears for a moment and vanishes. Each creature in the area who can see the pattern must succeed on a Wisdom saving throw or have the Charmed condition for the duration. While Charmed, the creature has the Incapacitated condition and a Speed of 0.\n"
            "The spell ends for an affected creature if it takes any damage or if someone else uses an action to shake the creature out of its stupor."
        ),
        usage_tags=("control",),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "0719d025dab9bcf1")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You create a twisting pattern of colors in a 30-foot Cube within range. The pattern appears for a moment and vanishes.",
                    ),
                    ("Area", "30-foot Cube within range"),
                    (
                        "Save",
                        "Wisdom, made by each creature in the area who can see the pattern",
                    ),
                    (
                        "Failed save",
                        "Charmed for the duration; while Charmed, the creature has the Incapacitated condition and a Speed of 0",
                    ),
                    (
                        "Ends early",
                        "For an affected creature, if it takes any damage or if someone else uses an action to shake it out of its stupor",
                    ),
                )
            )
        ]


class InciteGreed(ClassSpell):
    rules = SpellRules(
        name="Incite Greed",
        level=3,
        school=School.ENCHANTMENT,
        classes=(
            CharacterClass.CLERIC,
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 30),
        components=Components(
            verbal=True, somatic=True, material="a gem worth at least 50 gp"
        ),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Acquisitions Inc.",
        description=(
            "When you cast this spell, you present the gem used as the material component and choose any number of creatures within range that can see you. Each target must succeed on a Wisdom saving throw or be charmed by you until the spell ends, or until you or your companions do anything harmful to it. While charmed in this way, a creature can do nothing but use its movement to approach you in a safe manner. While an affected creature is within 5 feet of you, it cannot move, but simply stares greedily at the gem you present.\n"
            "At the end of each of its turns, an affected target can make a Wisdom saving throw. If it succeeds, this effect ends for that target."
        ),
        usage_tags=("control", "utility"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "d7dd8196c84643d7")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "When you cast this spell, you present the gem used as the material component."
            ),
            Facts(
                (
                    (
                        "Targets",
                        "Any number of creatures within range that can see you",
                    ),
                    ("Save", "Wisdom"),
                    (
                        "Failed save",
                        "Charmed by you until the spell ends, or until you or your companions do anything harmful to it",
                    ),
                    (
                        "Charmed",
                        "It can do nothing but use its movement to approach you in a safe manner; while within 5 feet of you, it can't move, but simply stares greedily at the gem you present",
                    ),
                    (
                        "Repeat save",
                        "At the end of each of its turns; if it succeeds, the effect ends for that target",
                    ),
                )
            ),
        ]


class InflictDoubt(ClassSpell):
    rules = SpellRules(
        name="Inflict Doubt",
        level=3,
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
        source="Arcana Unleashed",
        description="You inflict self-doubt on a creature you can see within range. The target must succeed on a Wisdom saving throw or have Disadvantage on D20 Tests for the duration. At the end of each of its turns, the target repeats the save, ending the spell on itself on a success.",
        usage_tags=("control",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "d25a875c9f98c9b9")


class IntellectFortress(ClassSpell):
    rules = SpellRules(
        name="Intellect Fortress",
        level=3,
        school=School.ABJURATION,
        classes=(),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 30),
        components=Components(verbal=True),
        duration=Duration(DurationType.HOUR, 1, concentration=True),
        source="Tasha's Cauldron of Everything",
        description=(
            "For the duration, you or one willing creature you can see within range has resistance to psychic damage, as well as advantage on Intelligence, Wisdom, and Charisma saving throws.\n"
            "At Higher Levels. When you cast this spell using a spell slot of 4th level or higher, you can target one additional creature for each slot level above 3rd. The creatures must be within 30 feet of each other when you target them.\n"
            "Spell Lists: Artificer , Bard (Optional) , Sorcerer (Optional) , Warlock (Optional) , Wizard"
        ),
        usage_tags=("buff", "utility"),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "ffdc4e20cb3bbbfa")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Target", "You or one willing creature you can see within range"),
                    (
                        "Effect",
                        "For the duration, Resistance to Psychic damage, and Advantage on Intelligence, Wisdom, and Charisma saving throws",
                    ),
                )
            ),
            Option(
                "At Higher Levels",
                (
                    Facts(
                        (
                            ("Targets", "+1 creature for each slot level above 3rd"),
                            (
                                "Spacing",
                                "The creatures must be within 30 feet of each other when you target them",
                            ),
                        )
                    ),
                ),
            ),
        ]


class LaeralsSilverLance(ClassSpell):
    rules = SpellRules(
        name="Laeral's Silver Lance",
        level=3,
        school=School.EVOCATION,
        classes=(CharacterClass.CLERIC, CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(
            verbal=True, somatic=True, material="a silver pin worth 250+ GP"
        ),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Forgotten Realms - Heroes of Faerun",
        description=(
            "Silver energy bursts out from you in a 120-foot-long, 5-foot-wide Line. Each creature of your choice in the Line makes a Strength saving throw. On a failed save, a creature takes 3d10 Force damage and has the Prone condition. On a successful save, a creature takes half as much damage only.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 1d10 for every spell slot level above 3."
        ),
        usage_tags=("control", "damage"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "ef2b6ba6ed468689")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "Silver energy bursts out from you in a 120-foot-long, 5-foot-wide Line.",
                    ),
                    ("Area", "Line 120 feet long and 5 feet wide"),
                    (
                        "Save",
                        "Strength, made by each creature of your choice in the Line",
                    ),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (
                    (
                        "3d10 Force damage, and the Prone condition",
                        "Half as much damage only",
                    ),
                ),
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Damage", "+1d10 for every spell slot level above 3"),)),),
            ),
        ]


class LeomundsTinyHut(ClassSpell):
    rules = SpellRules(
        name="Leomund's Tiny Hut",
        level=3,
        school=School.EVOCATION,
        classes=(CharacterClass.BARD, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.MINUTE, 1, ritual=True),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True, material="a crystal bead"),
        duration=Duration(DurationType.HOUR, 8),
        source="Player's Handbook",
        description=(
            "A 10-foot Emanation springs into existence around you and remains stationary for the duration. The spell fails when you cast it if the Emanation isn’t big enough to fully encapsulate all creatures in its area.\n"
            "Creatures and objects within the Emanation when you cast the spell can move through it freely. All other creatures and objects are barred from passing through it. Spells of level 3 or lower can’t be cast through it, and the effects of such spells can’t extend into it.\n"
            "The atmosphere inside the Emanation is comfortable and dry, regardless of the weather outside. Until the spell ends, you can command the interior to have Dim Light or Darkness (no action required). The Emanation is opaque from the outside and of any color you choose, but it’s transparent from the inside.\n"
            "The spell ends early if you leave the Emanation or if you cast it again."
        ),
        usage_tags=("buff",),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "d03395ed0f4dd7ac")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "A 10-foot Emanation springs into existence around you and remains stationary for the duration."
            ),
            Facts(
                (
                    (
                        "Fails if",
                        "The Emanation isn't big enough to fully encapsulate all creatures in its area when you cast it",
                    ),
                    (
                        "Passage",
                        "Creatures and objects within it when you cast the spell can move through it freely; all other creatures and objects are barred from passing through it",
                    ),
                    (
                        "Spells",
                        "Spells of level 3 or lower can't be cast through it, and the effects of such spells can't extend into it",
                    ),
                    (
                        "Inside",
                        "Comfortable and dry, regardless of the weather outside",
                    ),
                    (
                        "Light",
                        "Until the spell ends, you can command the interior to have Dim Light or Darkness (no action required)",
                    ),
                    (
                        "Walls",
                        "Opaque from the outside and of any color you choose, but transparent from the inside",
                    ),
                    (
                        "Ends early",
                        "If you leave the Emanation or if you cast this spell again",
                    ),
                )
            ),
        ]


class LifeTransference(ClassSpell):
    rules = SpellRules(
        name="Life Transference",
        level=3,
        school=School.NECROMANCY,
        classes=(),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 30),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Xanathar's Guide to Everything",
        description=(
            "You sacrifice some of your health to mend another creature's injuries. You take 4d8 necrotic damage, which can't be reduced in any way, and one creature of your choice that you can see within range regains a number of hit points equal to twice the necrotic damage you take.\n"
            "At Higher Levels: When you cast this spell using a spell slot of 4th level or higher, the damage increases by 1d8 for each slot level above 3rd.\n"
            "Spell Lists: Cleric , Wizard"
        ),
        usage_tags=("damage", "heal", "utility"),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "a07cf4332781f80d")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You sacrifice some of your health to mend another creature's injuries.",
                    ),
                    (
                        "Cost",
                        "You take 4d8 Necrotic damage, which can't be reduced in any way",
                    ),
                    (
                        "Target",
                        "One creature of your choice that you can see within range",
                    ),
                    (
                        "Healing",
                        "It regains hit points equal to twice the Necrotic damage you take",
                    ),
                )
            ),
            Option(
                "At Higher Levels",
                (Facts((("Damage", "+1d8 for each slot level above 3rd"),)),),
            ),
        ]


class LightningArrow(ClassSpell):
    rules = SpellRules(
        name="Lightning Arrow",
        level=3,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.RANGER,),
        casting_time=CastingTime(
            CastingTimeType.BONUS_ACTION,
            trigger="which you take immediately after hitting or missing a target with a ranged attack using a weapon",
        ),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "As your attack hits or misses the target, the weapon or ammunition you’re using transforms into a lightning bolt. Instead of taking any damage or other effects from the attack, the target takes 4d8 Lightning damage on a hit or half as much damage on a miss. Each creature within 10 feet of the target then makes a Dexterity saving throw, taking 2d8 Lightning damage on a failed save or half as much damage on a successful one.\n"
            "The weapon or ammunition then returns to its normal form.\n"
            "Using a Higher-Level Spell Slot. The damage for both effects of the spell increases by 1d8 for each spell slot level above 3."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "a5cafb7bb5bc9cf6")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "As your attack hits or misses the target, the weapon or ammunition you're using transforms into a lightning bolt.",
                    ),
                    (
                        "Trigger",
                        "Immediately after you hit or miss a target with a ranged attack using a weapon",
                    ),
                    (
                        "The target",
                        "Instead of taking any damage or other effects from the attack, it takes 4d8 Lightning damage on a hit, or half as much damage on a miss",
                    ),
                    (
                        "Nearby",
                        "Each creature within 10 feet of the target then makes a Dexterity saving throw",
                    ),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (("2d8 Lightning damage", "Half as much damage"),),
            ),
            Facts(
                (
                    (
                        "Afterward",
                        "The weapon or ammunition then returns to its normal form",
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
                                "The damage for both effects of the spell increases by 1d8 for each spell slot level above 3",
                            ),
                        )
                    ),
                ),
            ),
        ]


class MagicCircle(ClassSpell):
    rules = SpellRules(
        name="Magic Circle",
        level=3,
        school=School.ABJURATION,
        classes=(
            CharacterClass.CLERIC,
            CharacterClass.PALADIN,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.MINUTE, 1),
        range=Range(RangeType.FOOT, 10),
        components=Components(
            verbal=True,
            somatic=True,
            material="salt and powdered silver worth 100+ GP, which the spell consumes",
        ),
        duration=Duration(DurationType.HOUR, 1),
        source="Player's Handbook",
        description=(
            "You create a 10-foot-radius, 20-foot-tall Cylinder of magical energy centered on a point on the ground that you can see within range. Glowing runes appear wherever the Cylinder intersects with the floor or other surface.\n"
            "Choose one or more of the following types of creatures: Celestials, Elementals, Fey, Fiends, or Undead. The circle affects a creature of the chosen type in the following ways:\n"
            "The creature can’t willingly enter the Cylinder by nonmagical means. If the creature tries to use teleportation or interplanar travel to do so, it must first succeed on a Charisma saving throw.\n"
            "The creature has Disadvantage on attack rolls against targets within the Cylinder.\n"
            "Targets within the Cylinder can’t be possessed by or gain the Charmed or Frightened condition from the creature.\n"
            "Each time you cast this spell, you can cause its magic to operate in the reverse direction, preventing a creature of the specified type from leaving the Cylinder and protecting targets outside it.\n"
            "Using a Higher-Level Spell Slot. The duration increases by 1 hour for each spell slot level above 3."
        ),
        usage_tags=("buff", "control"),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "045f35b90ccf86b4")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You create a Cylinder of magical energy that wards against certain kinds of creatures."
            ),
            Facts(
                (
                    (
                        "Area",
                        "10-foot-radius, 20-foot-tall Cylinder centered on a point on the ground that you can see within range; glowing runes appear wherever it intersects with the floor or other surface",
                    ),
                    (
                        "Creature types",
                        "Choose one or more: Celestials, Elementals, Fey, Fiends, or Undead",
                    ),
                )
            ),
            Option(
                "Effects on Those Creatures",
                (
                    Facts(
                        (
                            (
                                "Entering",
                                "The creature can't willingly enter the Cylinder by nonmagical means; if it tries to use teleportation or interplanar travel to do so, it must first succeed on a Charisma saving throw",
                            ),
                            (
                                "Attacks",
                                "It has Disadvantage on attack rolls against targets within the Cylinder",
                            ),
                            (
                                "Protection",
                                "Targets within the Cylinder can't be possessed by or gain the Charmed or Frightened condition from it",
                            ),
                        )
                    ),
                ),
            ),
            Facts(
                (
                    (
                        "Reversed",
                        "Each time you cast this spell, you can cause its magic to operate in the reverse direction, preventing a creature of the specified type from leaving the Cylinder and protecting targets outside it",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Duration", "+1 hour for each spell slot level above 3"),)),),
            ),
        ]


class MajorImage(ClassSpell):
    rules = SpellRules(
        name="Major Image",
        level=3,
        school=School.ILLUSION,
        classes=(
            CharacterClass.BARD,
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 120),
        components=Components(verbal=True, somatic=True, material="a bit of fleece"),
        duration=Duration(DurationType.MINUTE, 10, concentration=True),
        source="Player's Handbook",
        description=(
            "You create the image of an object, a creature, or some other visible phenomenon that is no larger than a 20-foot Cube. The image appears at a spot that you can see within range and lasts for the duration. It seems real, including sounds, smells, and temperature appropriate to the thing depicted, but it can’t deal damage or cause conditions.\n"
            "If you are within range of the illusion, you can take a Magic action to cause the image to move to any other spot within range. As the image changes location, you can alter its appearance so that its movements appear natural for the image. For example, if you create an image of a creature and move it, you can alter the image so that it appears to be walking. Similarly, you can cause the illusion to make different sounds at different times, even making it carry on a conversation, for example.\n"
            "Physical interaction with the image reveals it to be an illusion, for things can pass through it. A creature that takes a Study action to examine the image can determine that it is an illusion with a successful Intelligence (Investigation) check against your spell save DC. If a creature discerns the illusion for what it is, the creature can see through the image, and its other sensory qualities become faint to the creature.\n"
            "Using a Higher-Level Spell Slot. The spell lasts until dispelled, without requiring Concentration, if cast with a level 4+ spell slot."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "bc78d6452c116e79")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You create the image of an object, a creature, or some other visible phenomenon that seems real."
            ),
            Facts(
                (
                    (
                        "Size",
                        "No larger than a 20-foot Cube, at a spot that you can see within range",
                    ),
                    (
                        "Senses",
                        "It seems real, including sounds, smells, and temperature appropriate to the thing depicted, but it can't deal damage or cause conditions",
                    ),
                    (
                        "Moving it",
                        "If you are within range of the illusion, you can take a Magic action to move the image to any other spot within range; as it moves, you can alter its appearance so its movements appear natural (a creature can appear to be walking)",
                    ),
                    (
                        "Sounds",
                        "You can cause the illusion to make different sounds at different times, even making it carry on a conversation",
                    ),
                    (
                        "Touch",
                        "Physical interaction with the image reveals it to be an illusion, for things can pass through it",
                    ),
                    (
                        "Seeing through",
                        "A creature that takes a Study action to examine the image can determine that it is an illusion with a successful Intelligence (Investigation) check against your spell save DC",
                    ),
                    (
                        "Once discerned",
                        "The creature can see through the image, and its other sensory qualities become faint to the creature",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (
                    Facts(
                        (
                            (
                                "Level 4+ slot",
                                "The spell lasts until dispelled, without requiring Concentration",
                            ),
                        )
                    ),
                ),
            ),
        ]


class MassHealingWord(ClassSpell):
    rules = SpellRules(
        name="Mass Healing Word",
        level=3,
        school=School.ABJURATION,
        classes=(CharacterClass.BARD, CharacterClass.CLERIC),
        casting_time=CastingTime(CastingTimeType.BONUS_ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "Up to six creatures of your choice that you can see within range regain Hit Points equal to 2d4 plus your spellcasting ability modifier.\n"
            "Using a Higher-Level Spell Slot. The healing increases by 1d4 for each spell slot level above 3."
        ),
        usage_tags=("heal",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "4e8f4012df394813")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("Up to six creatures you can see regain Hit Points."),
            Facts(
                (
                    (
                        "Targets",
                        "Up to six creatures of your choice that you can see within range",
                    ),
                    ("Healing", "2d4 + your spellcasting ability modifier"),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Healing", "+1d4 for each spell slot level above 3"),)),),
            ),
        ]


class MeldIntoStone(ClassSpell):
    rules = SpellRules(
        name="Meld into Stone",
        level=3,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.CLERIC, CharacterClass.DRUID, CharacterClass.RANGER),
        casting_time=CastingTime(CastingTimeType.ACTION, ritual=True),
        range=Range(RangeType.TOUCH),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.HOUR, 8),
        source="Player's Handbook",
        description=(
            "You step into a stone object or surface large enough to fully contain your body, merging yourself and your equipment with the stone for the duration. You must touch the stone to do so. Nothing of your presence remains visible or otherwise detectable by nonmagical senses.\n"
            "While merged with the stone, you can’t see what occurs outside it, and any Wisdom (Perception) checks you make to hear sounds outside it are made with Disadvantage. You remain aware of the passage of time and can cast spells on yourself while merged in the stone. You can use 5 feet of movement to leave the stone where you entered it, which ends the spell. You otherwise can’t move.\n"
            "Minor physical damage to the stone doesn’t harm you, but its partial destruction or a change in its shape (to the extent that you no longer fit within it) expels you and deals 6d6 Force damage to you. The stone’s complete destruction (or transmutation into a different substance) expels you and deals 50 Force damage to you. If expelled, you move into an unoccupied space closest to where you first entered and have the Prone condition."
        ),
        usage_tags=("control", "damage"),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "30fbddb9ec754637")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You step into a stone object or surface large enough to fully contain your body, merging yourself and your equipment with the stone for the duration."
            ),
            Facts(
                (
                    ("Entering", "You must touch the stone to do so"),
                    (
                        "Hidden",
                        "Nothing of your presence remains visible or otherwise detectable by nonmagical senses",
                    ),
                    (
                        "Senses",
                        "You can't see what occurs outside the stone, and Wisdom (Perception) checks you make to hear sounds outside it are made with Disadvantage",
                    ),
                    (
                        "Inside",
                        "You remain aware of the passage of time and can cast spells on yourself",
                    ),
                    (
                        "Leaving",
                        "You can use 5 feet of movement to leave the stone where you entered it, which ends the spell; you otherwise can't move",
                    ),
                )
            ),
            Option(
                "Damage to the Stone",
                (
                    Facts(
                        (
                            (
                                "Minor",
                                "Minor physical damage to the stone doesn't harm you",
                            ),
                            (
                                "Partial",
                                "Its partial destruction, or a change in its shape to the extent that you no longer fit within it, expels you and deals 6d6 Force damage to you",
                            ),
                            (
                                "Complete",
                                "Its complete destruction (or transmutation into a different substance) expels you and deals 50 Force damage to you",
                            ),
                            (
                                "Expelled",
                                "You move into an unoccupied space closest to where you first entered and have the Prone condition",
                            ),
                        )
                    ),
                ),
            ),
        ]


class MelfsMinuteMeteors(ClassSpell):
    rules = SpellRules(
        name="Melf's Minute Meteors",
        level=3,
        school=School.EVOCATION,
        classes=(CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(
            verbal=True,
            somatic=True,
            material="niter, sulfur, and pine tar formed into a bead",
        ),
        duration=Duration(DurationType.MINUTE, 10, concentration=True),
        source="Xanathar's Guide to Everything",
        description=(
            "You create six tiny meteors in your space. They float in the air and orbit you for the spell's duration. When you cast the spell — and as a bonus action on each of your turns thereafter — you can expend one or two of the meteors, sending them streaking toward a point or points you choose within 120 feet of you. Once a meteor reaches its destination or impacts against a solid surface, the meteor explodes. Each creature within 5 feet of the point where the meteor explodes must make a Dexterity saving throw. A creature takes 2d6 fire damage on a failed save, or half as much damage on a successful one.\n"
            "At Higher Levels. When you cast this spell using a spell slot of 4th level or higher, the number of meteors created increases by two for each slot level above 3rd."
        ),
        usage_tags=("damage", "utility"),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "31d4cd9e18b1a1d2")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You create six tiny meteors in your space. They float in the air and orbit you for the spell's duration.",
                    ),
                    (
                        "Meteors",
                        "Six, in your space; they orbit you for the spell's duration",
                    ),
                    (
                        "Launching",
                        "When you cast the spell, and as a bonus action on each of your turns thereafter, you can expend one or two meteors, sending them streaking toward a point or points you choose within 120 feet of you",
                    ),
                    (
                        "Explosion",
                        "A meteor explodes once it reaches its destination or impacts against a solid surface",
                    ),
                    (
                        "Save",
                        "Dexterity, made by each creature within 5 feet of the point where the meteor explodes",
                    ),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (("2d6 Fire damage", "Half as much damage"),),
            ),
            Option(
                "At Higher Levels",
                (Facts((("Meteors", "+2 meteors for each slot level above 3rd"),)),),
            ),
        ]


class MotivationalSpeech(ClassSpell):
    rules = SpellRules(
        name="Motivational Speech",
        level=3,
        school=School.ENCHANTMENT,
        classes=(),
        casting_time=CastingTime(CastingTimeType.MINUTE, 1),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True),
        duration=Duration(DurationType.HOUR, 1),
        source="Acquisitions Inc.",
        description=(
            "Choose up to five creatures within range that can hear you. For the duration, each affected creature gains 5 temporary hit points and has advantage on Wisdom saving throws. If an affected creature is hit by an attack, it has advantage on the next attack roll it makes. Once an affected creature loses the temporary hit points granted by this spell, the spell ends for that creature.\n"
            "At Higher Levels: When you cast this spell using a spell slot of 4th level or higher, the temporary hit points increase by 5 for each slot level above 3rd.\n"
            "Spell Lists: Bard , Cleric"
        ),
        usage_tags=("buff", "damage", "heal"),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "67f08d4b5c1215b3")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Targets", "Up to five creatures within range that can hear you"),
                    (
                        "Temporary hit points",
                        "For the duration, each gains 5 temporary hit points",
                    ),
                    ("Saves", "Advantage on Wisdom saving throws"),
                    (
                        "When hit",
                        "If an affected creature is hit by an attack, it has Advantage on the next attack roll it makes",
                    ),
                    (
                        "Ends",
                        "Once an affected creature loses the temporary hit points granted by this spell, the spell ends for that creature",
                    ),
                )
            ),
            Option(
                "At Higher Levels",
                (
                    Facts(
                        (("Temporary hit points", "+5 for each slot level above 3rd"),)
                    ),
                ),
            ),
        ]


class Nondetection(ClassSpell):
    rules = SpellRules(
        name="Nondetection",
        level=3,
        school=School.ABJURATION,
        classes=(CharacterClass.BARD, CharacterClass.RANGER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.TOUCH),
        components=Components(
            verbal=True,
            somatic=True,
            material="a pinch of diamond dust worth 25+ GP, which the spell consumes",
        ),
        duration=Duration(DurationType.HOUR, 8),
        source="Player's Handbook",
        description="For the duration, you hide a target that you touch from Divination spells. The target can be a willing creature, or it can be a place or an object no larger than 10 feet in any dimension. The target can’t be targeted by any Divination spell or perceived through magical scrying sensors.",
        usage_tags=("utility",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "e6dd19c9740b84d1")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You hide a target that you touch from Divination spells for the duration."
            ),
            Facts(
                (
                    (
                        "Target",
                        "A willing creature, or a place or an object no larger than 10 feet in any dimension",
                    ),
                    (
                        "Effect",
                        "It can't be targeted by any Divination spell or perceived through magical scrying sensors",
                    ),
                )
            ),
        ]


class PhantomSteed(ClassSpell):
    rules = SpellRules(
        name="Phantom Steed",
        level=3,
        school=School.ILLUSION,
        classes=(CharacterClass.WIZARD,),
        casting_time=CastingTime(CastingTimeType.MINUTE, 1, ritual=True),
        range=Range(RangeType.FOOT, 30),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.HOUR, 1),
        source="Player's Handbook",
        description=(
            "A Large, quasi-real, horselike creature appears on the ground in an unoccupied space of your choice within range. You decide the creature’s appearance, and it is equipped with a saddle, bit, and bridle. Any of the equipment created by the spell vanishes in a puff of smoke if it is carried more than 10 feet away from the steed.\n"
            "For the duration, you or a creature you choose can ride the steed. The steed uses the Riding Horse stat block (see appendix B), except it has a Speed of 100 feet and can travel 13 miles in an hour. When the spell ends, the steed gradually fades, giving the rider 1 minute to dismount. The spell ends early if the steed takes any damage."
        ),
        usage_tags=("utility", "summon"),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "b9e343c51fba46ab")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "A Large, quasi-real, horselike creature appears on the ground in an unoccupied space of your choice within range."
            ),
            Facts(
                (
                    (
                        "Appearance",
                        "You decide it; it is equipped with a saddle, bit, and bridle",
                    ),
                    (
                        "Equipment",
                        "Any of the equipment created by the spell vanishes in a puff of smoke if it is carried more than 10 feet away from the steed",
                    ),
                    (
                        "Riders",
                        "For the duration, you or a creature you choose can ride the steed",
                    ),
                    (
                        "Statistics",
                        "The Riding Horse stat block (see appendix B), except it has a Speed of 100 feet and can travel 13 miles in an hour",
                    ),
                    (
                        "Spell ends",
                        "The steed gradually fades, giving the rider 1 minute to dismount",
                    ),
                    ("Ends early", "If the steed takes any damage"),
                )
            ),
        ]


class PlantGrowth(ClassSpell):
    rules = SpellRules(
        name="Plant Growth",
        level=3,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.BARD, CharacterClass.DRUID, CharacterClass.RANGER),
        casting_time=CastingTime(
            CastingTimeType.ACTION,
            note="Overgrowth",
            alternative=CastingTime(CastingTimeType.HOUR, 8, note="Enrichment"),
        ),
        range=Range(RangeType.FOOT, 150),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "This spell channels vitality into plants. The casting time you use determines whether the spell has the Overgrowth or the Enrichment effect below.\n"
            "Overgrowth. Choose a point within range. All normal plants in a 100-foot-radius Sphere centered on that point become thick and overgrown. A creature moving through that area must spend 4 feet of movement for every 1 foot it moves. You can exclude one or more areas of any size within the spell’s area from being affected.\n"
            "Enrichment. All plants in a half-mile radius centered on a point within range become enriched for 365 days. The plants yield twice the normal amount of food when harvested. They can benefit from only one Plant Growth per year."
        ),
        usage_tags=("control",),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "41a28aaddf891720")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts((("Flavor", "This spell channels vitality into plants."),)),
            Paragraph(
                "The casting time you use determines whether the spell has the Overgrowth or the Enrichment effect below."
            ),
            Option(
                "Overgrowth (Action)",
                (
                    Facts(
                        (
                            (
                                "Area",
                                "All normal plants in a 100-foot-radius Sphere centered on a point within range become thick and overgrown",
                            ),
                            (
                                "Movement",
                                "A creature moving through that area must spend 4 feet of movement for every 1 foot it moves",
                            ),
                            (
                                "Exclusions",
                                "You can exclude one or more areas of any size within the spell's area from being affected",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Enrichment (8 Hours)",
                (
                    Facts(
                        (
                            (
                                "Area",
                                "All plants in a half-mile radius centered on a point within range become enriched for 365 days",
                            ),
                            (
                                "Harvest",
                                "The plants yield twice the normal amount of food when harvested",
                            ),
                            (
                                "Limit",
                                "They can benefit from only one Plant Growth per year",
                            ),
                        )
                    ),
                ),
            ),
        ]


class ProtectionFromEnergy(ClassSpell):
    rules = SpellRules(
        name="Protection from Energy",
        level=3,
        school=School.ABJURATION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.CLERIC,
            CharacterClass.DRUID,
            CharacterClass.RANGER,
            CharacterClass.SORCERER,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.TOUCH),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.HOUR, 1, concentration=True),
        source="Player's Handbook",
        description="For the duration, the willing creature you touch has Resistance to one damage type of your choice: Acid, Cold, Fire, Lightning, or Thunder.",
        usage_tags=("buff",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "4bfcebb4ea59e3f0")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You protect a willing creature you touch from one kind of energy."
            ),
            Facts(
                (
                    (
                        "Effect",
                        "For the duration, Resistance to one damage type of your choice: Acid, Cold, Fire, Lightning, or Thunder",
                    ),
                )
            ),
        ]

    def combat_effects(
        self, character: CharacterView | None = None
    ) -> list[CombatEffect]:
        return [
            CombatEffect(
                name="Protection from Energy: Acid",
                conditions=(
                    CombatCondition(
                        "Protection from Energy",
                        modifiers=(Resistance((DamageType.ACID,)),),
                    ),
                ),
            ),
            CombatEffect(
                name="Protection from Energy: Cold",
                conditions=(
                    CombatCondition(
                        "Protection from Energy",
                        modifiers=(Resistance((DamageType.COLD,)),),
                    ),
                ),
            ),
            CombatEffect(
                name="Protection from Energy: Fire",
                conditions=(
                    CombatCondition(
                        "Protection from Energy",
                        modifiers=(Resistance((DamageType.FIRE,)),),
                    ),
                ),
            ),
            CombatEffect(
                name="Protection from Energy: Lightning",
                conditions=(
                    CombatCondition(
                        "Protection from Energy",
                        modifiers=(Resistance((DamageType.LIGHTNING,)),),
                    ),
                ),
            ),
            CombatEffect(
                name="Protection from Energy: Thunder",
                conditions=(
                    CombatCondition(
                        "Protection from Energy",
                        modifiers=(Resistance((DamageType.THUNDER,)),),
                    ),
                ),
            ),
        ]


class RemoveCurse(ClassSpell):
    rules = SpellRules(
        name="Remove Curse",
        level=3,
        school=School.ABJURATION,
        classes=(
            CharacterClass.CLERIC,
            CharacterClass.PALADIN,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.TOUCH),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description="At your touch, all curses affecting one creature or object end. If the object is a cursed magic item, its curse remains, but the spell breaks its owner’s Attunement to the object so it can be removed or discarded.",
        usage_tags=("heal",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "1fe3e27620560a64")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "At your touch, all curses affecting one creature or object end."
            ),
            Facts(
                (
                    (
                        "Cursed magic item",
                        "Its curse remains, but the spell breaks its owner's Attunement to the object so it can be removed or discarded",
                    ),
                )
            ),
        ]


class Revivify(ClassSpell):
    rules = SpellRules(
        name="Revivify",
        level=3,
        school=School.NECROMANCY,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.CLERIC,
            CharacterClass.DRUID,
            CharacterClass.PALADIN,
            CharacterClass.RANGER,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.TOUCH),
        components=Components(
            verbal=True,
            somatic=True,
            material="a diamond worth 300+ GP, which the spell consumes",
        ),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description="You touch a creature that has died within the last minute. That creature revives with 1 Hit Point. This spell can’t revive a creature that has died of old age, nor does it restore any missing body parts.",
        usage_tags=("heal",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "4800de4fc6621f38")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You touch a creature that has died within the last minute, and it revives with 1 Hit Point."
            ),
            Facts(
                (
                    (
                        "Can't",
                        "Revive a creature that has died of old age, or restore any missing body parts",
                    ),
                )
            ),
        ]


class Sending(ClassSpell):
    rules = SpellRules(
        name="Sending",
        level=3,
        school=School.DIVINATION,
        classes=(CharacterClass.BARD, CharacterClass.CLERIC, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.UNLIMITED),
        components=Components(verbal=True, somatic=True, material="a copper wire"),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "You send a short message of 25 words or fewer to a creature you have met or a creature described to you by someone who has met it. The target hears the message in its mind, recognizes you as the sender if it knows you, and can answer in a like manner immediately. The spell enables targets to understand the meaning of your message.\n"
            "You can send the message across any distance and even to other planes of existence, but if the target is on a different plane than you, there is a 5 percent chance that the message doesn’t arrive. You know if the delivery fails.\n"
            "Upon receiving your message, a creature can block your ability to reach it again with this spell for 8 hours. If you try to send another message during that time, you learn that you are blocked, and the spell fails."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "77d1d63d3f8934c2")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You send a short message to a creature, which can answer immediately."
            ),
            Facts(
                (
                    (
                        "Target",
                        "A creature you have met, or a creature described to you by someone who has met it",
                    ),
                    ("Message", "25 words or fewer"),
                    (
                        "Receiving",
                        "The target hears the message in its mind, recognizes you as the sender if it knows you, and can answer in a like manner immediately; the spell enables targets to understand the meaning of your message",
                    ),
                    ("Distance", "Any distance, even to other planes of existence"),
                    (
                        "Other planes",
                        "If the target is on a different plane than you, there is a 5 percent chance that the message doesn't arrive; you know if the delivery fails",
                    ),
                    (
                        "Blocking",
                        "Upon receiving your message, a creature can block your ability to reach it again with this spell for 8 hours; if you try during that time, you learn that you are blocked, and the spell fails",
                    ),
                )
            ),
        ]


class SleetStorm(ClassSpell):
    rules = SpellRules(
        name="Sleet Storm",
        level=3,
        school=School.CONJURATION,
        classes=(CharacterClass.DRUID, CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 150),
        components=Components(
            verbal=True, somatic=True, material="a miniature umbrella"
        ),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "Until the spell ends, sleet falls in a 40-foot-tall, 20-foot-radius Cylinder centered on a point you choose within range. The area is Heavily Obscured, and exposed flames in the area are doused.\n"
            "Ground in the Cylinder is Difficult Terrain. When a creature enters the Cylinder for the first time on a turn or starts its turn there, it must succeed on a Dexterity saving throw or have the Prone condition and lose Concentration."
        ),
        usage_tags=("control",),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "0bc838633fd3162e")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("Until the spell ends, sleet falls in an area."),
            Facts(
                (
                    (
                        "Area",
                        "40-foot-tall, 20-foot-radius Cylinder centered on a point you choose within range",
                    ),
                    (
                        "Visibility",
                        "Heavily Obscured, and exposed flames in the area are doused",
                    ),
                    ("Terrain", "Ground in the Cylinder is Difficult Terrain"),
                    (
                        "Save",
                        "Dexterity, when a creature enters the Cylinder for the first time on a turn or starts its turn there",
                    ),
                    ("Failed save", "The Prone condition, and it loses Concentration"),
                )
            ),
        ]


class Slow(ClassSpell):
    rules = SpellRules(
        name="Slow",
        level=3,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.BARD, CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 120),
        components=Components(verbal=True, somatic=True, material="a drop of molasses"),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "You alter time around up to six creatures of your choice in a 40-foot Cube within range. Each target must succeed on a Wisdom saving throw or be affected by this spell for the duration.\n"
            "An affected target’s Speed is halved, it takes a −2 penalty to AC and Dexterity saving throws, and it can’t take Reactions. On its turns, it can take either an action or a Bonus Action, not both, and it can make only one attack if it takes the Attack action. If it casts a spell with a Somatic component, there is a 25 percent chance the spell fails as a result of the target making the spell’s gestures too slowly.\n"
            "An affected target repeats the save at the end of each of its turns, ending the spell on itself on a success."
        ),
        usage_tags=("control",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "5e21b6574b64ec6c")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You alter time around up to six creatures."),
            Facts(
                (
                    (
                        "Targets",
                        "Up to six creatures of your choice in a 40-foot Cube within range",
                    ),
                    ("Save", "Wisdom"),
                    ("Failed save", "Affected by this spell for the duration (below)"),
                    (
                        "Repeat save",
                        "At the end of each of its turns, ending the spell on itself on a success",
                    ),
                )
            ),
            Option(
                "Affected Target",
                (
                    Facts(
                        (
                            ("Speed", "Halved"),
                            (
                                "Defenses",
                                "A -2 penalty to AC and Dexterity saving throws",
                            ),
                            ("Reactions", "It can't take Reactions"),
                            (
                                "Its turns",
                                "It can take either an action or a Bonus Action, not both, and it can make only one attack if it takes the Attack action",
                            ),
                            (
                                "Spells",
                                "If it casts a spell with a Somatic component, there is a 25 percent chance the spell fails as a result of the target making the spell's gestures too slowly",
                            ),
                        )
                    ),
                ),
            ),
        ]


class SpeakWithDead(ClassSpell):
    rules = SpellRules(
        name="Speak with Dead",
        level=3,
        school=School.NECROMANCY,
        classes=(CharacterClass.BARD, CharacterClass.CLERIC, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 10),
        components=Components(verbal=True, somatic=True, material="burning incense"),
        duration=Duration(DurationType.MINUTE, 10),
        source="Player's Handbook",
        description=(
            "You grant the semblance of life to a corpse of your choice within range, allowing it to answer questions you pose. The corpse must have a mouth, and this spell fails if the deceased creature was Undead when it died. The spell also fails if the corpse was the target of this spell within the past 10 days.\n"
            "Until the spell ends, you can ask the corpse up to five questions. The corpse knows only what it knew in life, including the languages it knew. Answers are usually brief, cryptic, or repetitive, and the corpse is under no compulsion to offer a truthful answer if you are antagonistic toward it or it recognizes you as an enemy. This spell doesn’t return the creature’s soul to its body, only its animating spirit. Thus, the corpse can’t learn new information, doesn’t comprehend anything that has happened since it died, and can’t speculate about future events."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.CREATURE,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "dd765b4d698b3156")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You grant the semblance of life to a corpse of your choice within range, allowing it to answer questions you pose.",
                    ),
                    (
                        "Target",
                        "A corpse of your choice within range; it must have a mouth",
                    ),
                    (
                        "Fails if",
                        "The deceased creature was Undead when it died, or the corpse was the target of this spell within the past 10 days",
                    ),
                    ("Questions", "Up to five, until the spell ends"),
                    (
                        "Knowledge",
                        "Only what it knew in life, including the languages it knew",
                    ),
                    (
                        "Answers",
                        "Usually brief, cryptic, or repetitive; the corpse is under no compulsion to offer a truthful answer if you are antagonistic toward it or it recognizes you as an enemy",
                    ),
                    (
                        "Limits",
                        "The spell doesn't return the creature's soul to its body, only its animating spirit, so the corpse can't learn new information, doesn't comprehend anything that has happened since it died, and can't speculate about future events",
                    ),
                )
            )
        ]


class SpeakWithPlants(ClassSpell):
    rules = SpellRules(
        name="Speak with Plants",
        level=3,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.BARD, CharacterClass.DRUID, CharacterClass.RANGER),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 10),
        source="Player's Handbook",
        description=(
            "You imbue plants in an immobile 30-foot Emanation with limited sentience and animation, giving them the ability to communicate with you and follow your simple commands. You can question plants about events in the spell’s area within the past day, gaining information about creatures that have passed, weather, and other circumstances.\n"
            "You can also turn Difficult Terrain caused by plant growth (such as thickets and undergrowth) into ordinary terrain that lasts for the duration. Or you can turn ordinary terrain where plants are present into Difficult Terrain that lasts for the duration.\n"
            "The spell doesn’t enable plants to uproot themselves and move about, but they can move their branches, tendrils, and stalks for you.\n"
            "If a Plant creature is in the area, you can communicate with it as if you shared a common language."
        ),
        usage_tags=("control",),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "372f0407527bac06")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You imbue plants in an immobile 30-foot Emanation with limited sentience and animation, giving them the ability to communicate with you and follow your simple commands.",
                    ),
                    ("Area", "An immobile 30-foot Emanation"),
                    (
                        "Talking",
                        "The plants can communicate with you and follow your simple commands",
                    ),
                    (
                        "Questions",
                        "You can question them about events in the spell's area within the past day, gaining information about creatures that have passed, weather, and other circumstances",
                    ),
                    (
                        "Terrain",
                        "You can turn Difficult Terrain caused by plant growth (such as thickets and undergrowth) into ordinary terrain, or turn ordinary terrain where plants are present into Difficult Terrain, for the duration",
                    ),
                    (
                        "Movement",
                        "The plants can't uproot themselves and move about, but they can move their branches, tendrils, and stalks for you",
                    ),
                    (
                        "Plant creatures",
                        "You can communicate with one in the area as if you shared a common language",
                    ),
                )
            )
        ]


class SpiritGuardians(ClassSpell):
    rules = SpellRules(
        name="Spirit Guardians",
        level=3,
        school=School.CONJURATION,
        classes=(CharacterClass.CLERIC,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True, material="a prayer scroll"),
        duration=Duration(DurationType.MINUTE, 10, concentration=True),
        source="Player's Handbook",
        description=(
            "Protective spirits flit around you in a 15-foot Emanation for the duration. If you are good or neutral, their spectral form appears angelic or fey (your choice). If you are evil, they appear fiendish.\n"
            "When you cast this spell, you can designate creatures to be unaffected by it. Any other creature’s Speed is halved in the Emanation, and whenever the Emanation enters a creature’s space and whenever a creature enters the Emanation or ends its turn there, the creature must make a Wisdom saving throw. On a failed save, the creature takes 3d8 Radiant damage (if you are good or neutral) or 3d8 Necrotic damage (if you are evil). On a successful save, the creature takes half as much damage. A creature makes this save only once per turn.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 1d8 for each spell slot level above 3."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "e65a14ffc2403fdc")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "Protective spirits flit around you in a 15-foot Emanation for the duration.",
                    ),
                    ("Area", "15-foot Emanation"),
                    (
                        "Appearance",
                        "Angelic or fey (your choice) if you are good or neutral; fiendish if you are evil",
                    ),
                    (
                        "Unaffected",
                        "When you cast this spell, you can designate creatures to be unaffected by it",
                    ),
                    ("Speed", "Any other creature's Speed is halved in the Emanation"),
                    (
                        "Save",
                        "Wisdom, whenever the Emanation enters a creature's space and whenever a creature enters the Emanation or ends its turn there; a creature makes this save only once per turn",
                    ),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (
                    (
                        "3d8 Radiant damage (if you are good or neutral) or 3d8 Necrotic damage (if you are evil)",
                        "Half as much damage",
                    ),
                ),
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Damage", "+1d8 for each spell slot level above 3"),)),),
            ),
        ]

    def combat_effects(
        self, character: CharacterView | None = None
    ) -> list[CombatEffect]:
        return [
            CombatEffect(
                conditions=(
                    CombatCondition(
                        "Spirit Guardians",
                        modifiers=(
                            AtTurnEnd(
                                "Spirit Guardians: damage",
                                WhoseTurn.ENEMY,
                                when="it ends its turn in the Emanation",
                            ),
                        ),
                    ),
                ),
                notes=(
                    "The badge goes on the caster, or on the enemies it's aimed at: either way the turn column asks, as each enemy of the caster ends its turn, whether it's in the 15-foot Emanation, for the damage row. Any other creature's Speed is halved in it.",
                ),
            ),
            CombatEffect(
                name="Spirit Guardians: damage",
                roll=EffectRoll.SAVE,
                save_ability=Ability.WISDOM,
                half_on_success=True,
                damage=(CombatDamage("3d8", DamageType.RADIANT, upcast="1d8"),),
                spends_use=False,
                notes=(
                    "When the Emanation enters a creature's space, or a creature enters it or ends its turn there; once per turn for each creature. Necrotic instead if the caster is evil. Cast with a higher slot: 1d8 more per level above 3 (type it in; picking a slot here spends one).",
                ),
            ),
        ]


class SpiritShroud(ClassSpell):
    rules = SpellRules(
        name="Spirit Shroud",
        level=3,
        school=School.NECROMANCY,
        classes=(
            CharacterClass.CLERIC,
            CharacterClass.PALADIN,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.BONUS_ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Tasha's Cauldron of Everything",
        description=(
            "You call forth spirits of the dead, which flit around you for the spell's duration. The spirits are intangible and invulnerable.\n"
            "Until the spell ends, any attack you make deals 1d8 extra damage when you hit a creature within 10 feet of you. This damage is radiant, necrotic, or cold (your choice when you cast the spell). Any creature that takes this damage can't regain hit points until the start of your next turn.\n"
            "In addition, any creature of your choice that you can see that starts its turn within 10 feet of you has its speed reduced by 10 feet until the start of your next turn.\n"
            "At Higher Levels. When you cast this spell using a spell slot of 4th level or higher, the damage increases by 1d8 for every two slot levels above 3rd."
        ),
        usage_tags=("damage", "heal", "utility"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "17cd76a078650888")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You call forth spirits of the dead, which flit around you for the spell's duration.",
                    ),
                    ("Spirits", "Intangible and invulnerable"),
                    (
                        "Extra damage",
                        "Until the spell ends, any attack you make deals 1d8 extra damage when you hit a creature within 10 feet of you",
                    ),
                    (
                        "Damage type",
                        "Radiant, Necrotic, or Cold (your choice when you cast the spell)",
                    ),
                    (
                        "No healing",
                        "Any creature that takes this damage can't regain hit points until the start of your next turn",
                    ),
                    (
                        "Slowing",
                        "Any creature of your choice that you can see that starts its turn within 10 feet of you has its speed reduced by 10 feet until the start of your next turn",
                    ),
                )
            ),
            Option(
                "At Higher Levels",
                (
                    Table(
                        ("Slot level", "Extra damage"),
                        (
                            ("3rd-4th", "1d8"),
                            ("5th-6th", "2d8"),
                            ("7th-8th", "3d8"),
                            ("9th", "4d8"),
                        ),
                    ),
                ),
            ),
        ]


class StinkingCloud(ClassSpell):
    rules = SpellRules(
        name="Stinking Cloud",
        level=3,
        school=School.CONJURATION,
        classes=(CharacterClass.BARD, CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 90),
        components=Components(verbal=True, somatic=True, material="a rotten egg"),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "You create a 20-foot-radius Sphere of yellow, nauseating gas centered on a point within range. The cloud is Heavily Obscured. The cloud lingers in the air for the duration or until a strong wind (such as the one created by Gust of Wind ) disperses it.\n"
            "Each creature that starts its turn in the Sphere must succeed on a Constitution saving throw or have the Poisoned condition until the end of the current turn. While Poisoned in this way, the creature can’t take an action or a Bonus Action."
        ),
        usage_tags=("control",),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "810d156dc4bae4f7")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You create a 20-foot-radius Sphere of yellow, nauseating gas centered on a point within range.",
                    ),
                    ("Area", "20-foot-radius Sphere centered on a point within range"),
                    ("Visibility", "Heavily Obscured"),
                    (
                        "Lasts",
                        "For the duration, or until a strong wind (such as the one created by Gust of Wind) disperses it",
                    ),
                    (
                        "Save",
                        "Constitution, made by each creature that starts its turn in the Sphere",
                    ),
                    (
                        "Failed save",
                        "Poisoned until the end of the current turn; while Poisoned in this way, it can't take an action or a Bonus Action",
                    ),
                )
            )
        ]


class SummonFey(ClassSpell):
    rules = SpellRules(
        name="Summon Fey",
        level=3,
        school=School.CONJURATION,
        classes=(
            CharacterClass.DRUID,
            CharacterClass.RANGER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 90),
        components=Components(
            verbal=True, somatic=True, material="a gilded flower worth 300+ GP"
        ),
        duration=Duration(DurationType.HOUR, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "You call forth a Fey spirit. It manifests in an unoccupied space that you can see within range and uses the Fey Spirit stat block. When you cast the spell, choose a mood: Fuming, Mirthful, or Tricksy. The creature resembles a Fey creature of your choice marked by the chosen mood, which determines certain details in its stat block. The creature disappears when it drops to 0 Hit Points or when the spell ends.\n"
            "The creature is an ally to you and your allies. In combat, the creature shares your Initiative count, but it takes its turn immediately after yours. It obeys your verbal commands (no action required by you). If you don’t issue any, it takes the Dodge action and uses its movement to avoid danger.\n"
            "Using a Higher-Level Spell Slot. Use the spell slot’s level for the spell’s level in the stat block."
        ),
        usage_tags=("summon",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "214bd2e68669df0c")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You call forth a Fey spirit."),
            Facts(
                (
                    ("Appears", "In an unoccupied space that you can see within range"),
                    (
                        "Mood",
                        "Fuming, Mirthful, or Tricksy, chosen when you cast the spell; the creature resembles a Fey creature of your choice marked by that mood, which determines certain details in its stat block",
                    ),
                    ("Stat block", "Fey Spirit (below)"),
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
                "Fey Spirit",
                (
                    Facts(
                        (
                            ("Type", "Small Fey"),
                            ("AC", "12 + the spell's level"),
                            ("Hit Points", "30 + 10 for each spell level above 3"),
                            ("Speed", "30 ft., Fly 30 ft."),
                            (
                                "Abilities",
                                "Str 13, Dex 16, Con 14, Int 14, Wis 11, Cha 16",
                            ),
                            ("Immunities", "Charmed"),
                            ("Senses", "Darkvision 60 ft., Passive Perception 10"),
                            ("Languages", "Sylvan, understands the languages you know"),
                            (
                                "Multiattack",
                                "The spirit makes a number of Fey Blade attacks equal to half this spell's level (round down)",
                            ),
                            (
                                "Fey Blade",
                                "Melee Attack Roll: Bonus equals your spell attack modifier, reach 5 ft. Hit: 2d6 + 3 + the spell's level Force damage",
                            ),
                            (
                                "Fey Step",
                                "Bonus Action. The spirit magically teleports up to 30 feet to an unoccupied space it can see. Then one of the following effects occurs, based on the spirit's chosen mood",
                            ),
                            (
                                "Fuming",
                                "The spirit has Advantage on the next attack roll it makes before the end of this turn",
                            ),
                            (
                                "Mirthful",
                                "Wisdom saving throw against your spell save DC, one creature the spirit can see within 10 feet of itself. Failure: The target is Charmed by you and the spirit for 1 minute or until the target takes any damage",
                            ),
                            (
                                "Tricksy",
                                "The spirit fills a 10-foot Cube within 5 feet of it with magical Darkness, which lasts until the end of its next turn",
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


class SummonLesserDemons(ClassSpell):
    rules = SpellRules(
        name="Summon Lesser Demons",
        level=3,
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
            "You utter foul words, summoning demons from the chaos of the Abyss. Roll on the following table to determine what appears.\n"
            "The DM chooses the demons, such as manes or dretches, and you choose the unoccupied spaces you can see within range where they appear. A summoned demon disappears when it drops to 0 hit points or when the spell ends.\n"
            "The demons are hostile to all creatures, including you. Roll initiative for the summoned demons as a group, which has its own turns. The demons pursue and attack the nearest non-demons to the best of their ability.\n"
            "As part of casting the spell, you can form a circle on the ground with the blood used as a material component. The circle is large enough to encompass your space. While the spell lasts, the summoned demons can't cross the circle or harm it, and they can't target anyone within it. Using the material component in this manner consumes it when the spell ends.\n"
            "At Higher Levels. When you cast this spell using a spell slot of 6th or 7th level, you summon twice as many demons. If you cast it using a spell slot of 8th or 9th level, you summon three times as many demons."
        ),
        usage_tags=("utility", "summon"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "cdcc00f6b53555df")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You utter foul words, summoning demons from the chaos of the Abyss.",
                    ),
                )
            ),
            Paragraph("Roll on the table to determine what appears."),
            Table(
                ("d6", "Demons summoned"),
                (
                    ("1-2", "Two demons of challenge rating 1 or lower"),
                    ("3-4", "Four demons of challenge rating 1/2 or lower"),
                    ("5-6", "Eight demons of challenge rating 1/4 or lower"),
                ),
            ),
            Facts(
                (
                    (
                        "Choosing",
                        "The DM chooses the demons, such as manes or dretches, and you choose the unoccupied spaces you can see within range where they appear",
                    ),
                    (
                        "Disappear",
                        "A summoned demon disappears when it drops to 0 hit points or when the spell ends",
                    ),
                    (
                        "Hostile",
                        "The demons are hostile to all creatures, including you",
                    ),
                    (
                        "Initiative",
                        "Roll initiative for the summoned demons as a group, which has its own turns",
                    ),
                    (
                        "Behavior",
                        "They pursue and attack the nearest non-demons to the best of their ability",
                    ),
                )
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
                                "While the spell lasts, the summoned demons can't cross the circle or harm it, and they can't target anyone within it",
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
                (
                    Table(
                        ("Slot level", "Demons"),
                        (
                            ("6th-7th", "Twice as many"),
                            ("8th-9th", "Three times as many"),
                        ),
                    ),
                ),
            ),
        ]


class SummonShadowspawn(ClassSpell):
    rules = SpellRules(
        name="Summon Shadowspawn",
        level=3,
        school=School.CONJURATION,
        classes=(CharacterClass.WARLOCK, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 90),
        components=Components(
            verbal=True,
            somatic=True,
            material="tears inside a crystal vial worth at least 300 gp",
        ),
        duration=Duration(DurationType.HOUR, 1, concentration=True),
        source="Tasha's Cauldron of Everything",
        description=(
            "You call forth a shadowy spirit. It manifests in an unoccupied space that you can see within range. This corporeal form uses the Shadow Spirit stat block. When you cast the spell, choose an emotion: Fury, Despair, or Fear. The creature resembles a misshapen biped marked by the chosen emotion, which determines certain traits in its stat block. The creature disappears when it drop to 0 hit points or when the spell ends.\n"
            "The creature is an ally to you and your companions. In combat, the creature shares your initiative count, but it takes its turn immediately after your. It obeys your verbal commands (no action required by you). If you don't issue any, it takes the Dodge action and it uses its move to avoid danger.\n"
            "At Higher Levels. When you cast the spell using a spell slot of 4th level or higher, use the higher level wherever the spell's level appears on the stat block."
        ),
        usage_tags=("utility", "summon"),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "dc9ae178d523eb96")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You call forth a shadowy spirit."),
            Facts(
                (
                    ("Appears", "In an unoccupied space that you can see within range"),
                    (
                        "Emotion",
                        "Fury, Despair, or Fear, chosen when you cast the spell; the creature resembles a misshapen biped marked by that emotion, which determines certain traits in its stat block",
                    ),
                    ("Stat block", "Shadow Spirit (not included in this spell's data)"),
                    (
                        "Disappears",
                        "When it drops to 0 hit points or when the spell ends",
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
                                "It shares your initiative count, but it takes its turn immediately after yours",
                            ),
                            (
                                "Commands",
                                "It obeys your verbal commands (no action required by you); if you don't issue any, it takes the Dodge action and uses its move to avoid danger",
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
                                "Use the higher level wherever the spell's level appears on the stat block",
                            ),
                        )
                    ),
                ),
            ),
        ]


class SummonUndead(ClassSpell):
    rules = SpellRules(
        name="Summon Undead",
        level=3,
        school=School.NECROMANCY,
        classes=(CharacterClass.WARLOCK, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 90),
        components=Components(
            verbal=True, somatic=True, material="a gilded skull worth 300+ GP"
        ),
        duration=Duration(DurationType.HOUR, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "You call forth an Undead spirit. It manifests in an unoccupied space that you can see within range and uses the Undead Spirit stat block. When you cast the spell, choose the creature’s form: Ghostly, Putrid, or Skeletal. The spirit resembles an Undead creature with the chosen form, which determines certain details in its stat block. The creature disappears when it drops to 0 Hit Points or when the spell ends.\n"
            "The creature is an ally to you and your allies. In combat, the creature shares your Initiative count, but it takes its turn immediately after yours. It obeys your verbal commands (no action required by you). If you don’t issue any, it takes the Dodge action and uses its movement to avoid danger.\n"
            "Using a Higher-Level Spell Slot. Use the spell slot’s level for the spell’s level in the stat block."
        ),
        usage_tags=("summon",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "6fe63d001d5483ad")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You call forth an Undead spirit."),
            Facts(
                (
                    ("Appears", "In an unoccupied space that you can see within range"),
                    (
                        "Form",
                        "Ghostly, Putrid, or Skeletal, chosen when you cast the spell; it determines certain details in its stat block",
                    ),
                    ("Stat block", "Undead Spirit (below)"),
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
                "Undead Spirit",
                (
                    Facts(
                        (
                            ("Type", "Medium Undead"),
                            ("AC", "11 + the spell's level"),
                            (
                                "Hit Points",
                                "30 (Ghostly and Putrid only) or 20 (Skeletal only) + 10 for each spell level above 3",
                            ),
                            ("Speed", "30 ft., Fly 40 ft. (hover; Ghostly only)"),
                            (
                                "Abilities",
                                "Str 12, Dex 16, Con 15, Int 4, Wis 10, Cha 9",
                            ),
                            (
                                "Immunities",
                                "Necrotic, Poison; Exhaustion, Frightened, Paralyzed, Poisoned",
                            ),
                            ("Senses", "Darkvision 60 ft., Passive Perception 10"),
                            ("Languages", "Understands the languages you know"),
                            (
                                "Festering Aura",
                                "Putrid only. Constitution saving throw against your spell save DC, any creature (other than you) that starts its turn within a 5-foot Emanation originating from the spirit. Failure: The creature has the Poisoned condition until the start of its next turn",
                            ),
                            (
                                "Incorporeal Passage",
                                "Ghostly only. The spirit can move through other creatures and objects as if they were Difficult Terrain. If it ends its turn inside an object, it is shunted to the nearest unoccupied space and takes 1d10 Force damage for every 5 feet traveled",
                            ),
                            (
                                "Multiattack",
                                "The spirit makes a number of attacks equal to half this spell's level (round down)",
                            ),
                            (
                                "Deathly Touch",
                                "Ghostly only. Melee Attack Roll: Bonus equals your spell attack modifier, reach 5 ft. Hit: 1d8 + 3 + the spell's level Necrotic damage, and the target has the Frightened condition until the end of its next turn",
                            ),
                            (
                                "Grave Bolt",
                                "Skeletal only. Ranged Attack Roll: Bonus equals your spell attack modifier, range 150 ft. Hit: 2d4 + 3 + the spell's level Necrotic damage",
                            ),
                            (
                                "Rotting Claw",
                                "Putrid only. Melee Attack Roll: Bonus equals your spell attack modifier, reach 5 ft. Hit: 1d6 + 3 + the spell's level Slashing damage. If the target has the Poisoned condition, it has the Paralyzed condition until the end of its next turn",
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


class SylunesViper(ClassSpell):
    rules = SpellRules(
        name="Sylune's Viper",
        level=3,
        school=School.CONJURATION,
        classes=(CharacterClass.DRUID, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.BONUS_ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True, material="a snake fang"),
        duration=Duration(DurationType.HOUR, 1),
        source="Forgotten Realms - Heroes of Faerun",
        description=(
            "A shimmering, spectral snake encircles your body for the duration. You gain 15 Temporary Hit Points; the spell ends early if you have no Temporary Hit Points left.\n"
            "While the spell is active, you gain the following benefits:\n"
            "Climbing. You gain a Climb Speed equal to your Speed.\n"
            "Venomous Bite. As a Magic action, you can make a ranged spell attack using the snake against one creature within 50 feet. On a hit, the target takes 1d6 Force damage and has the Poisoned condition until the start of your next turn. While Poisoned, the target has the Incapacitated condition.\n"
            "Using a Higher-Level Spell Slot. For each spell slot level above 3, the number of Temporary Hit Points you gain from this spell increases by 5, and the damage of Venomous Bite increases by 1d6."
        ),
        usage_tags=("buff", "control", "damage", "heal"),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "6cdd1e262a721862")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "A shimmering, spectral snake encircles your body for the duration.",
                    ),
                    ("Temporary Hit Points", "You gain 15 Temporary Hit Points"),
                    ("Ends early", "If you have no Temporary Hit Points left"),
                    ("Climbing", "You gain a Climb Speed equal to your Speed"),
                )
            ),
            Option(
                "Venomous Bite",
                (
                    Facts(
                        (
                            ("Action", "Magic action"),
                            (
                                "Attack",
                                "Ranged spell attack using the snake against one creature within 50 feet",
                            ),
                            (
                                "On a hit",
                                "1d6 Force damage, and the target has the Poisoned condition until the start of your next turn; while Poisoned, it has the Incapacitated condition",
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
                                "Temporary Hit Points",
                                "+5 for each spell slot level above 3",
                            ),
                            (
                                "Venomous Bite",
                                "+1d6 damage for each spell slot level above 3",
                            ),
                        )
                    ),
                ),
            ),
        ]


class ThunderStep(ClassSpell):
    rules = SpellRules(
        name="Thunder Step",
        level=3,
        school=School.CONJURATION,
        classes=(),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 90),
        components=Components(verbal=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Xanathar's Guide to Everything",
        description=(
            "You teleport yourself to an unoccupied space you can see within range. Immediately after you disappear, a thunderous boom sounds, and each creature within 10 feet of the space you left must make a Constitution saving throw, taking 3d10 thunder damage on a failed save, or half as much damage on a successful one. The thunder can be heard from up to 300 feet away.\n"
            "You can bring along objects as long as their weight doesn't exceed what you can carry. You can also teleport one willing creature of your size or smaller who is carrying gear up to its carrying capacity. The creature must be within 5 feet of you when you cast this spell, and there must be an unoccupied space within 5 feet of your destination space for the creature to appear in; otherwise, the creature is left behind.\n"
            "At Higher Levels. When you cast this spell using a spell slot of 4th level or higher, the damage increases by 1d10 for each slot level above 3rd.\n"
            "Spell lists. Sorcerer , Warlock , Wizard"
        ),
        usage_tags=("damage", "utility"),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "7e0fa6fae04ac912")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "Immediately after you disappear, a thunderous boom sounds.",
                    ),
                    ("Teleport", "To an unoccupied space you can see within range"),
                    (
                        "Boom",
                        "Immediately after you disappear, each creature within 10 feet of the space you left makes a Constitution saving throw",
                    ),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (("3d10 Thunder damage", "Half as much damage"),),
            ),
            Facts(
                (
                    ("Sound", "The thunder can be heard from up to 300 feet away"),
                    (
                        "Objects",
                        "You can bring along objects as long as their weight doesn't exceed what you can carry",
                    ),
                    (
                        "Passenger",
                        "You can also teleport one willing creature of your size or smaller who is carrying gear up to its carrying capacity",
                    ),
                    (
                        "Its conditions",
                        "It must be within 5 feet of you when you cast this spell, and there must be an unoccupied space within 5 feet of your destination space for it to appear in; otherwise, it is left behind",
                    ),
                )
            ),
            Option(
                "At Higher Levels",
                (Facts((("Damage", "+1d10 for each slot level above 3rd"),)),),
            ),
        ]


class TidalWave(ClassSpell):
    rules = SpellRules(
        name="Tidal Wave",
        level=3,
        school=School.CONJURATION,
        classes=(CharacterClass.DRUID, CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 120),
        components=Components(verbal=True, somatic=True, material="a drop of water"),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Xanathar's Guide to Everything",
        description="You conjure up a wave of water that crashes down on an area within range. The area can be up to 30 feet long, up to 10 feet wide, and up to 10 feet tall. Each creature in that area must make a Dexterity saving throw. On a failure, a creature takes 4d8 bludgeoning damage and is knocked prone. On a success, a creature takes half as much damage and isn't knocked prone. The water then spreads out across the ground in all directions, extinguishing unprotected flames in its area and within 30 feet of it.",
        usage_tags=("control", "damage"),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "588fa34f575eae8d")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You conjure up a wave of water that crashes down on an area within range.",
                    ),
                    (
                        "Area",
                        "Up to 30 feet long, up to 10 feet wide, and up to 10 feet tall",
                    ),
                    ("Save", "Dexterity, made by each creature in the area"),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (
                    (
                        "4d8 Bludgeoning damage, and knocked Prone",
                        "Half as much damage, and not knocked Prone",
                    ),
                ),
            ),
            Facts(
                (
                    (
                        "Flames",
                        "The water then spreads out across the ground in all directions, extinguishing unprotected flames in its area and within 30 feet of it",
                    ),
                )
            ),
        ]


class TinyServant(ClassSpell):
    rules = SpellRules(
        name="Tiny Servant",
        level=3,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.WIZARD, CharacterClass.ARTIFICER),
        casting_time=CastingTime(CastingTimeType.MINUTE, 1),
        range=Range(RangeType.TOUCH),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.HOUR, 8),
        source="Xanathar's Guide to Everything",
        description=(
            "You touch one Tiny, nonmagical object that isn't attached to another object or a surface and isn't being carried by another creature. The target animates and sprouts little arms and legs, becoming a creature under your control until the spell ends or the creature drops to 0 hit points. See the stat block for its statistics.\n"
            "As a bonus action, you can mentally command the creature if it is within 120 feet of you. (If you control multiple creatures with this spell, you can command any or all of them at the same time, issuing the same command to each one.) You decide what action the creature will take and where it will move during its next turn, or you can issue a simple, general command, such as to fetch a key, stand watch, or stack some books. If you issue no commands, the servant does nothing other than defend itself against hostile creatures. Once given an order, the servant continues to follow that order until its task is complete.\n"
            "When the creature drops to 0 hit points, it reverts to its original form, and any remaining damage carries over to that form.\n"
            "At Higher Levels. When you cast this spell using a spell slot of 4th level or higher, you can animate two additional objects for each slot level above 3rd."
        ),
        usage_tags=("summon",),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "11376a01f7f24cfc")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Flavor", "The target animates and sprouts little arms and legs."),
                    (
                        "Target",
                        "One Tiny, nonmagical object you touch that isn't attached to another object or a surface and isn't being carried by another creature",
                    ),
                    (
                        "Effect",
                        "It becomes a creature under your control until the spell ends or the creature drops to 0 hit points",
                    ),
                    ("Stat block", "Tiny Servant (not included in this spell's data)"),
                    (
                        "0 hit points",
                        "It reverts to its original form, and any remaining damage carries over to that form",
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
                                "As a bonus action, you can mentally command the creature if it is within 120 feet of you",
                            ),
                            (
                                "Several",
                                "If you control multiple creatures with this spell, you can command any or all of them at the same time, issuing the same command to each one",
                            ),
                            (
                                "Orders",
                                "You decide what action it will take and where it will move during its next turn, or you can issue a simple, general command, such as to fetch a key, stand watch, or stack some books; once given an order, it continues to follow that order until its task is complete",
                            ),
                            (
                                "No command",
                                "The servant does nothing other than defend itself against hostile creatures",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "At Higher Levels",
                (Facts((("Objects", "+2 objects for each slot level above 3rd"),)),),
            ),
        ]


class Tongues(ClassSpell):
    rules = SpellRules(
        name="Tongues",
        level=3,
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
        components=Components(verbal=True, material="a miniature ziggurat"),
        duration=Duration(DurationType.HOUR, 1),
        source="Player's Handbook",
        description="This spell grants the creature you touch the ability to understand any spoken or signed language that it hears or sees. Moreover, when the target communicates by speaking or signing, any creature that knows at least one language can understand it if that creature can hear the speech or see the signing.",
        usage_tags=("utility",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "c3f4d4471e746c8b")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You grant the creature you touch the ability to understand and be understood in any language."
            ),
            Facts(
                (
                    (
                        "Understanding",
                        "It can understand any spoken or signed language that it hears or sees",
                    ),
                    (
                        "Being understood",
                        "When it communicates by speaking or signing, any creature that knows at least one language can understand it if that creature can hear the speech or see the signing",
                    ),
                )
            ),
        ]


class VampiricTouch(ClassSpell):
    rules = SpellRules(
        name="Vampiric Touch",
        level=3,
        school=School.NECROMANCY,
        classes=(
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
            "The touch of your shadow-wreathed hand can siphon life force from others to heal your wounds. Make a melee spell attack against one creature within reach. On a hit, the target takes 3d6 Necrotic damage, and you regain Hit Points equal to half the amount of Necrotic damage dealt.\n"
            "Until the spell ends, you can make the attack again on each of your turns as a Magic action, targeting the same creature or a different one.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 1d6 for each spell slot level above 3."
        ),
        usage_tags=("damage", "heal"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "51d7b94f0d736658")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "The touch of your shadow-wreathed hand can siphon life force from others to heal your wounds.",
                    ),
                    ("Target", "One creature within reach"),
                    ("Attack", "Melee spell attack"),
                    (
                        "On a hit",
                        "3d6 Necrotic damage, and you regain Hit Points equal to half the amount of Necrotic damage dealt",
                    ),
                    (
                        "Again",
                        "Until the spell ends, you can make the attack again on each of your turns as a Magic action, targeting the same creature or a different one",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Damage", "+1d6 for each spell slot level above 3"),)),),
            ),
        ]


class WallOfSand(ClassSpell):
    rules = SpellRules(
        name="Wall of Sand",
        level=3,
        school=School.EVOCATION,
        classes=(CharacterClass.WIZARD,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 90),
        components=Components(verbal=True, somatic=True, material="a handful of sand"),
        duration=Duration(DurationType.MINUTE, 10, concentration=True),
        source="Xanathar's Guide to Everything",
        description="You conjure up a wall of swirling sand on the ground at a point you can see within range. You can make the wall up to 30 feet long, 10 feet high, and 10 feet thick, and it vanishes when the spell ends. It blocks line of sight but not movement. A creature is blinded while in the wall's space and must spend 3 feet of movement for every 1 foot it moves there.",
        usage_tags=("control", "utility"),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "cba5420c92fdaf59")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You conjure up a wall of swirling sand on the ground at a point you can see within range."
            ),
            Facts(
                (
                    (
                        "Size",
                        "Up to 30 feet long, 10 feet high, and 10 feet thick; it vanishes when the spell ends",
                    ),
                    ("Sight", "It blocks line of sight but not movement"),
                    (
                        "Inside",
                        "A creature is blinded while in the wall's space and must spend 3 feet of movement for every 1 foot it moves there",
                    ),
                )
            ),
        ]


class WallOfWater(ClassSpell):
    rules = SpellRules(
        name="Wall of Water",
        level=3,
        school=School.EVOCATION,
        classes=(CharacterClass.DRUID, CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True, somatic=True, material="a drop of water"),
        duration=Duration(DurationType.MINUTE, 10, concentration=True),
        source="Xanathar's Guide to Everything",
        description=(
            "You conjure up a wall of water on the ground at a point you can see within range. You can make the wall up to 30 feet long, 10 feet high, and 1 foot thick, or you can make a ringed wall up to 20 feet in diameter, 20 feet high, and 1 foot thick. The wall vanishes when the spell ends. The wall's space is difficult terrain.\n"
            "Any ranged weapon attack that enters the wall's space has disadvantage on the attack roll, and fire damage is halved if the fire effect passes through the wall to reach its target. Spells that deal cold damage that pass through the wall cause the area of the wall they pass through to freeze solid (at least a 5-foot square section is frozen). Each 5-foot-square frozen section has AC 5 and 15 hit points. Reducing a frozen section to 0 hit points destroys it. When a section is destroyed, the wall's water doesn't fill it."
        ),
        usage_tags=("control", "damage", "utility"),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "6d782b1d1afaf195")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You conjure up a wall of water on the ground at a point you can see within range."
            ),
            Facts(
                (
                    (
                        "Shape",
                        "A wall up to 30 feet long, 10 feet high, and 1 foot thick, or a ringed wall up to 20 feet in diameter, 20 feet high, and 1 foot thick; it vanishes when the spell ends",
                    ),
                    ("Terrain", "The wall's space is Difficult Terrain"),
                    (
                        "Ranged attacks",
                        "Any ranged weapon attack that enters the wall's space has Disadvantage on the attack roll",
                    ),
                    (
                        "Fire",
                        "Fire damage is halved if the fire effect passes through the wall to reach its target",
                    ),
                    (
                        "Cold",
                        "Spells that deal cold damage that pass through the wall cause the area of the wall they pass through to freeze solid (at least a 5-foot-square section)",
                    ),
                    (
                        "Frozen sections",
                        "Each 5-foot-square frozen section has AC 5 and 15 hit points; reducing one to 0 hit points destroys it, and the wall's water doesn't fill it",
                    ),
                )
            ),
        ]


class WaterBreathing(ClassSpell):
    rules = SpellRules(
        name="Water Breathing",
        level=3,
        school=School.TRANSMUTATION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.DRUID,
            CharacterClass.RANGER,
            CharacterClass.SORCERER,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION, ritual=True),
        range=Range(RangeType.FOOT, 30),
        components=Components(verbal=True, somatic=True, material="a short reed"),
        duration=Duration(DurationType.HOUR, 24),
        source="Player's Handbook",
        description="This spell grants up to ten willing creatures of your choice within range the ability to breathe underwater until the spell ends. Affected creatures also retain their normal mode of respiration.",
        usage_tags=("buff",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "8307a4cfaa8173f8")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("Up to ten willing creatures can breathe underwater."),
            Facts(
                (
                    (
                        "Targets",
                        "Up to ten willing creatures of your choice within range",
                    ),
                    (
                        "Effect",
                        "They can breathe underwater until the spell ends, and they also retain their normal mode of respiration",
                    ),
                )
            ),
        ]


class WaterWalk(ClassSpell):
    rules = SpellRules(
        name="Water Walk",
        level=3,
        school=School.TRANSMUTATION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.CLERIC,
            CharacterClass.DRUID,
            CharacterClass.RANGER,
            CharacterClass.SORCERER,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION, ritual=True),
        range=Range(RangeType.FOOT, 30),
        components=Components(verbal=True, somatic=True, material="a piece of cork"),
        duration=Duration(DurationType.HOUR, 1),
        source="Player's Handbook",
        description=(
            "This spell grants the ability to move across any liquid surface - such as water, acid, mud, snow, quicksand, or lava - as if it were harmless solid ground (creatures crossing molten lava can still take damage from the heat). Up to ten willing creatures of your choice within range gain this ability for the duration.\n"
            "An affected target must take a Bonus Action to pass from the liquid’s surface into the liquid itself and vice versa, but if the target falls into the liquid, the target passes through the surface into the liquid below."
        ),
        usage_tags=("buff",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "c104e53acf7ac6e2")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("Up to ten willing creatures can walk on liquid."),
            Facts(
                (
                    (
                        "Targets",
                        "Up to ten willing creatures of your choice within range",
                    ),
                    (
                        "Effect",
                        "For the duration, they can move across any liquid surface (such as water, acid, mud, snow, quicksand, or lava) as if it were harmless solid ground",
                    ),
                    (
                        "Lava",
                        "Creatures crossing molten lava can still take damage from the heat",
                    ),
                    (
                        "Into the liquid",
                        "An affected target must take a Bonus Action to pass from the liquid's surface into the liquid itself and vice versa, but if it falls into the liquid, it passes through the surface into the liquid below",
                    ),
                )
            ),
        ]


class WindWall(ClassSpell):
    rules = SpellRules(
        name="Wind Wall",
        level=3,
        school=School.EVOCATION,
        classes=(CharacterClass.DRUID, CharacterClass.RANGER),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 120),
        components=Components(
            verbal=True, somatic=True, material="a fan and a feather"
        ),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "A wall of strong wind rises from the ground at a point you choose within range. You can make the wall up to 50 feet long, 15 feet high, and 1 foot thick. You can shape the wall in any way you choose so long as it makes one continuous path along the ground. The wall lasts for the duration.\n"
            "When the wall appears, each creature in its area makes a Strength saving throw, taking 4d8 Bludgeoning damage on a failed save or half as much damage on a successful one.\n"
            "The strong wind keeps fog, smoke, and other gases at bay. Small or smaller flying creatures or objects can’t pass through the wall. Loose, lightweight materials brought into the wall fly upward. Arrows, bolts, and other ordinary projectiles launched at targets behind the wall are deflected upward and miss automatically. Boulders hurled by Giants or siege engines, and similar projectiles, are unaffected. Creatures in gaseous form can’t pass through it."
        ),
        usage_tags=("control", "damage"),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "357a1ac7efb15592")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "A wall of strong wind rises from the ground at a point you choose within range."
            ),
            Facts(
                (
                    (
                        "Size",
                        "Up to 50 feet long, 15 feet high, and 1 foot thick, in any shape that makes one continuous path along the ground; it lasts for the duration",
                    ),
                    (
                        "Save",
                        "Strength, made by each creature in its area when the wall appears",
                    ),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (("4d8 Bludgeoning damage", "Half as much damage"),),
            ),
            Option(
                "The Wind",
                (
                    Facts(
                        (
                            ("Gases", "It keeps fog, smoke, and other gases at bay"),
                            (
                                "Small flyers",
                                "Small or smaller flying creatures or objects can't pass through the wall",
                            ),
                            (
                                "Loose materials",
                                "Loose, lightweight materials brought into the wall fly upward",
                            ),
                            (
                                "Projectiles",
                                "Arrows, bolts, and other ordinary projectiles launched at targets behind the wall are deflected upward and miss automatically; boulders hurled by Giants or siege engines, and similar projectiles, are unaffected",
                            ),
                            (
                                "Gaseous form",
                                "Creatures in gaseous form can't pass through it",
                            ),
                        )
                    ),
                ),
            ),
        ]


class PulseWave(ClassSpell):
    rules = SpellRules(
        name="Pulse Wave",
        level=3,
        school=School.EVOCATION,
        classes=(CharacterClass.WIZARD,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF, area=Area(30, AreaShape.CONE)),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Explorer's Guide to Wildemount",
        description=(
            "You create intense pressure, unleash it in a 30-foot cone, and decide whether the pressure pulls or pushes creatures and objects. Each creature in that cone must make a Constitution saving throw. A creature takes 6d6 force damage on a failed save, or half as much damage on a successful one. And every creature that fails the save is either pulled 15 feet toward you or pushed 15 feet away from you, depending on the choice you made for the spell.\n"
            "In addition, unsecured objects that are completely within the cone are likewise pulled or pushed 15 feet.\n"
            "At Higher Levels. When you cast this spell using a spell slot of 4th level or higher, the damage increases by 1d6 and the distance pulled or pushed increases by 5 feet for each slot level above 3rd."
        ),
        usage_tags=("damage", "utility"),
        target=FeatureTarget.AREA,
        school_note="Dunamancy",
    )
    converted_from = RecordStamp("spells_dnd5e.json", "7be9195f99eaabff")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You create intense pressure and unleash it in a cone, deciding whether it pulls or pushes."
            ),
            Facts(
                (
                    ("Area", "30-foot cone"),
                    ("Save", "Constitution, made by each creature in the cone"),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (
                    (
                        "6d6 Force damage, and pulled 15 feet toward you or pushed 15 feet away from you (your choice for the spell)",
                        "Half as much damage",
                    ),
                ),
            ),
            Facts(
                (
                    (
                        "Objects",
                        "Unsecured objects that are completely within the cone are likewise pulled or pushed 15 feet",
                    ),
                )
            ),
            Option(
                "At Higher Levels",
                (
                    Facts(
                        (
                            ("Damage", "+1d6 for each slot level above 3rd"),
                            (
                                "Distance",
                                "+5 feet pulled or pushed for each slot level above 3rd",
                            ),
                        )
                    ),
                ),
            ),
        ]


class BlisteringScales(ClassSpell):
    rules = SpellRules(
        name="Blistering Scales",
        level=3,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.SORCERER,),
        casting_time=CastingTime(CastingTimeType.BONUS_ACTION),
        range=Range(RangeType.FOOT, 30),
        components=Components(
            verbal=True, somatic=True, material="a scale of a Dragon"
        ),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="World of Warcraft",
        description=(
            "Choose a willing creature you can see within range. Five explosive scales form on the target, granting it a +1 bonus to AC for the duration. If a creature hits the target with a melee attack roll before the spell ends, a scale explodes, and the attacking creature takes 1d8 Fire damage. The spell ends early if the target has no explosive scales.\n"
            "Using a Higher-Level Spell Slot. The number of explosive scales that form on the target increases by one for each spell slot level above 3."
        ),
        usage_tags=("buff", "damage"),
    )
    converted_from = RecordStamp("spells_dnd2024.json", "8b9e03826b0f85cb")


class DemonSpikes(ClassSpell):
    rules = SpellRules(
        name="Demon Spikes",
        level=3,
        school=School.TRANSMUTATION,
        classes=(),
        casting_time=CastingTime(CastingTimeType.BONUS_ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True),
        duration=Duration(DurationType.MINUTE, 1),
        source="World of Warcraft",
        description="You surge with fel power and sprout hard, jagged spikes. You gain a +2 bonus to AC for the duration, and when a creature within 5 feet of you hits you with a melee attack roll, it takes 10 Piercing damage.",
        usage_tags=("buff", "damage"),
    )
    converted_from = RecordStamp("spells_dnd2024.json", "6766d8203243447a")


class EmeraldBlossom(ClassSpell):
    rules = SpellRules(
        name="Emerald Blossom",
        level=3,
        school=School.CONJURATION,
        classes=(CharacterClass.SORCERER,),
        casting_time=CastingTime(CastingTimeType.BONUS_ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="World of Warcraft",
        description=(
            "You conjure a spectral bulb that sprouts from the ground in an unoccupied space that you can see within range. The bulb lasts for the duration.\n"
            "The bulb emits healing magic in a 10-foot Emanation at the end of each of your turns. Allies of your choice in the Emanation regain 5 Hit Points. The bulb vanishes when it restores a total of 20 Hit Points.\n"
            "Using a Higher-Level Spell Slot. The total Hit Points the bulb can restore increases by 5 for each spell slot level above 3."
        ),
        usage_tags=("heal",),
    )
    converted_from = RecordStamp("spells_dnd2024.json", "7f19f4958e02b930")


class Flurry(ClassSpell):
    rules = SpellRules(
        name="Flurry",
        level=3,
        school=School.EVOCATION,
        classes=(CharacterClass.WIZARD,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 120),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="World of Warcraft",
        description=(
            "You hurl three shards of ice at one target within range or at several. Make a ranged spell attack for each shard. On a hit, the target takes 3d6 Cold damage. On a Critical Hit, the target has the Restrained condition until the end of your next turn.\n"
            "Using a Higher-Level Spell Slot. You create one additional shard of ice for each spell slot level above 3."
        ),
        usage_tags=("control", "damage"),
    )
    converted_from = RecordStamp("spells_dnd2024.json", "6ebfbcb5f5339585")


class GuidedPrayer(ClassSpell):
    rules = SpellRules(
        name="Guided Prayer",
        level=3,
        school=School.EVOCATION,
        classes=(CharacterClass.PALADIN,),
        casting_time=CastingTime(
            CastingTimeType.REACTION,
            trigger="which you take when you become Bloodied or take damage while you are Bloodied",
        ),
        range=Range(RangeType.SELF),
        components=Components(verbal=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="World of Warcraft",
        description="You regain Hit Points equal to 8d4 plus your spellcasting ability modifier. You have Advantage on the next attack roll you make before the end of your next turn.",
        usage_tags=("buff", "heal"),
    )
    converted_from = RecordStamp("spells_dnd2024.json", "b5fae8914b0a3095")


class HandOfGuldan(ClassSpell):
    rules = SpellRules(
        name="Hand of Gul'dan",
        level=3,
        school=School.CONJURATION,
        classes=(CharacterClass.WARLOCK,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 120),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="World of Warcraft",
        description=(
            "A demonic meteor hurtles from you to a point you choose within range and then erupts. Each creature in a 20-foot-radius Sphere centered on that point makes a Dexterity saving throw, taking 2d8 Fire damage plus 2d8 Necrotic damage on a failed save or half as much damage on a successful one.\n"
            "Demonic spirits resembling fel imps flit about the Sphere for the duration. A creature that enters the Sphere or ends its turn there makes a Dexterity saving throw, taking 1d8 Fire damage plus 1d8 Necrotic damage on a failed save or half as much damage on a successful one. A creature can be affected by this spell only once per turn."
        ),
        usage_tags=("damage",),
    )
    converted_from = RecordStamp("spells_dnd2024.json", "9ea60ff2f5db043f")


class LeechingStrike(ClassSpell):
    rules = SpellRules(
        name="Leeching Strike",
        level=3,
        school=School.NECROMANCY,
        classes=(),
        casting_time=CastingTime(
            CastingTimeType.BONUS_ACTION,
            trigger="which you take immediately after hitting a target with a Melee weapon or an Unarmed Strike",
        ),
        range=Range(RangeType.SELF),
        components=Components(verbal=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="World of Warcraft",
        description=(
            "The target hit by the strike takes an extra 3d8 Necrotic damage from the attack, and you regain 3d4 Hit Points.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 1d8, and the Hit Points you regain increase by 1d4, for each spell slot level above 3."
        ),
        usage_tags=("damage", "heal"),
    )
    converted_from = RecordStamp("spells_dnd2024.json", "1ddaa8765dae83ee")


class Metamorphosis(ClassSpell):
    rules = SpellRules(
        name="Metamorphosis",
        level=3,
        school=School.TRANSMUTATION,
        classes=(),
        casting_time=CastingTime(CastingTimeType.BONUS_ACTION),
        range=Range(RangeType.SELF),
        components=Components(
            verbal=True,
            somatic=True,
            material="one soul fragment, which the spell consumes",
        ),
        duration=Duration(DurationType.MINUTE, 1),
        source="World of Warcraft",
        description=(
            "Uttering an incantation, you draw on fel or Void magic to transform yourself, taking on demonic features. You gain one of the following benefits of your choice until the spell ends:\n"
            "Devourer. When you roll damage for a spell, weapon, or feature that deals Force damage, you can treat any 1 or 2 on a damage die as a 3.\n"
            "Havoc. Whenever you hit a creature with an attack roll using a Melee weapon, the target takes an extra 1d6 Fire damage.\n"
            "Vengeance. You have a +2 bonus to AC, and your Hit Point maximum and your current Hit Points increase by 5 for the spell’s duration."
        ),
        usage_tags=("buff", "damage", "heal"),
    )
    converted_from = RecordStamp("spells_dnd2024.json", "49fc8a3067205528")


class PrayerOfMending(ClassSpell):
    rules = SpellRules(
        name="Prayer of Mending",
        level=3,
        school=School.ABJURATION,
        classes=(CharacterClass.CLERIC,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True, material="a pinch of powdered silver"),
        duration=Duration(DurationType.MINUTE, 1),
        source="World of Warcraft",
        description=(
            "You place a holy ward on one willing creature in range. The next time that creature takes damage, the ward activates, and the creature regains Hit Points equal to 1d8 plus your spellcasting ability modifier. The ward then jumps to another ally of your choice within 30 feet of the warded creature, with the same effect. If no ally is in range, the spell ends, and it ends after the ward has healed five times.\n"
            "Using a Higher-Level Spell Slot. The spell can heal one additional time for each spell slot level above 3."
        ),
        usage_tags=("heal",),
    )
    converted_from = RecordStamp("spells_dnd2024.json", "dafb8bf0c91fa16d")


class RainOfFire(ClassSpell):
    rules = SpellRules(
        name="Rain of Fire",
        level=3,
        school=School.EVOCATION,
        classes=(CharacterClass.WARLOCK,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 120),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="World of Warcraft",
        description=(
            "Hellfire rains down in a 20-foot-radius, 40-foot-high Cylinder centered on a point within range. Until the spell ends, you can take a Magic action on later turns to move the Cylinder up to 60 feet.\n"
            "When the Cylinder appears, each creature in it makes a Dexterity saving throw, taking 3d8 Fire damage on a failed save or half as much damage on a successful one. A creature also makes this save when the spell’s area moves into its space and when it enters the spell’s area or ends its turn there. A creature makes this save only once per turn.\n"
            "You have Advantage on spell attack rolls against a creature in the Cylinder, and you deal an extra 1d6 Necrotic damage to the target if you hit.\n"
            "Using a Higher-Level Spell Slot. The Fire damage increases by 1d8 for each spell slot level above 3."
        ),
        usage_tags=("buff", "damage"),
    )
    converted_from = RecordStamp("spells_dnd2024.json", "6f8797a4bb42ebdd")


class Regrowth(ClassSpell):
    rules = SpellRules(
        name="Regrowth",
        level=3,
        school=School.ABJURATION,
        classes=(CharacterClass.DRUID,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 120),
        components=Components(verbal=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="World of Warcraft",
        description="One creature you can see within range regains 3d8 Hit Points. For the duration, the target regains 1d8 Hit Points at the start of each of your turns. The spell ends early once it restores at least 24 Hit Points.",
        usage_tags=("heal",),
    )
    converted_from = RecordStamp("spells_dnd2024.json", "dd90726a86b69316")


class RemorselessWinter(ClassSpell):
    rules = SpellRules(
        name="Remorseless Winter",
        level=3,
        school=School.EVOCATION,
        classes=(),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="World of Warcraft",
        description=(
            "You drain the warmth from nearby creatures. Each creature of your choice in a 30-foot Emanation originating from you makes a Constitution saving throw, taking 6d6 Cold damage on a failed save or half as much damage on a successful one. Whether or not a creature succeeds on its saving throw, its Speed is reduced to 10 feet until the end of its next turn as clinging frost hinders its movement.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 1d6 for each spell slot level above 3."
        ),
        usage_tags=("control", "damage"),
    )
    converted_from = RecordStamp("spells_dnd2024.json", "c9b942788bf593a7")


class SerpentSting(ClassSpell):
    rules = SpellRules(
        name="Serpent Sting",
        level=3,
        school=School.NECROMANCY,
        classes=(CharacterClass.RANGER,),
        casting_time=CastingTime(
            CastingTimeType.BONUS_ACTION,
            trigger="which you take immediately after hitting a creature with a weapon",
        ),
        range=Range(RangeType.SELF),
        components=Components(verbal=True),
        duration=Duration(DurationType.MINUTE, 1),
        source="World of Warcraft",
        description="The target takes an extra 4d6 Poison damage from the attack, and the target has the Poisoned condition until the spell ends. At the end of each of its turns, the Poisoned target makes a Constitution saving throw. On a failed save, the creature takes 2d6 Poison damage. On a successful save, the spell ends.",
        usage_tags=("control", "damage"),
    )
    converted_from = RecordStamp("spells_dnd2024.json", "41d2f2d3ace868c1")


class SoulReap(ClassSpell):
    rules = SpellRules(
        name="Soul Reap",
        level=3,
        school=School.NECROMANCY,
        classes=(),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="World of Warcraft",
        description=(
            "You cut a hole in the fabric of reality, sending a bolt of cosmic matter toward a creature in range. Make a ranged spell attack against the target, which gains no benefit from Half Cover or Three-Quarters Cover. On a hit, you deal 6d6 Force damage.\n"
            "If you roll a 6 on a d6 for this spell, you can roll another d6 and add it to the damage. When you cast this spell, the maximum number of these d6s you can add to the spell’s damage equals your spellcasting ability modifier.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 1d6 for each spell slot level above 3."
        ),
        usage_tags=("damage",),
    )
    converted_from = RecordStamp("spells_dnd2024.json", "8531d568e6c83e04")


SPELLS = [
    AnimateDead,
    Antagonize,
    AshardalonsStride,
    AstralFlood,
    AuraOfVitality,
    BeaconOfHope,
    BestowCurse,
    BlindingSmite,
    Blink,
    BlisteringScales,
    CacophonicShield,
    CallLightning,
    Catnap,
    Clairvoyance,
    ConjureAnimals,
    ConjureBarrage,
    ConjureConstructs,
    Counterspell,
    CreateFoodAndWater,
    CrusadersMantle,
    Daylight,
    DemonSpikes,
    DispelMagic,
    ElementalWeapon,
    EmeraldBlossom,
    EnemiesAbound,
    EruptingEarth,
    FastFriends,
    Fear,
    FeignDeath,
    Fireball,
    FlameArrows,
    Flurry,
    Fly,
    GaldersTower,
    GaseousForm,
    GlyphOfWarding,
    GuidedPrayer,
    HandOfGuldan,
    Haste,
    HungerOfHadar,
    HypnoticPattern,
    InciteGreed,
    InflictDoubt,
    IntellectFortress,
    LaeralsSilverLance,
    LeechingStrike,
    LeomundsTinyHut,
    LifeTransference,
    LightningArrow,
    LightningBolt,
    MagicCircle,
    MajorImage,
    MassHealingWord,
    MeldIntoStone,
    MelfsMinuteMeteors,
    Metamorphosis,
    MotivationalSpeech,
    Nondetection,
    PhantomSteed,
    PlantGrowth,
    PrayerOfMending,
    ProtectionFromEnergy,
    PulseWave,
    RainOfFire,
    Regrowth,
    RemorselessWinter,
    RemoveCurse,
    Revivify,
    Sending,
    SerpentSting,
    SleetStorm,
    Slow,
    SoulReap,
    SpeakWithDead,
    SpeakWithPlants,
    SpiritGuardians,
    SpiritShroud,
    StinkingCloud,
    SummonFey,
    SummonLesserDemons,
    SummonShadowspawn,
    SummonUndead,
    SylunesViper,
    ThunderStep,
    TidalWave,
    TinyServant,
    Tongues,
    VampiricTouch,
    WallOfSand,
    WallOfWater,
    WaterBreathing,
    WaterWalk,
    WindWall,
]
