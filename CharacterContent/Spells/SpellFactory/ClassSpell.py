"""A spell written as a Python class, the way a Feature is: its rules as a
SpellRules record, and what it does as methods (combat_effects(),
improved_description, summons()). SpellFactory uses the class of a spell's
name instead of its JSON record; a spell without a class still comes from
the JSON (DataSpell). See Notes/combat-effects-plan.md, "Spells as classes".

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
            usage_tags=("damage",),
            description="A bright streak flashes from you ...",
        )

        def combat_effects(self, character=None) -> list[CombatEffect]:
            return [CombatEffect(roll=EffectRoll.SAVE, save_ability=Ability.DEXTERITY, ...)]

What has a fixed set of values is an enum (the school, the classes), and
the casting time, range, components and duration are the dataclasses of
SpellFields.py, which write the card's text back in the 2024 wording.

CharacterContent/Spells/SpellClassConverter.py writes such a class from a
spell's JSON record and its companion files; from then on the class is the
spell's one source, edited by hand.
"""

import hashlib
import json
from dataclasses import dataclass
from typing import ClassVar, Optional

from Core.Definitions import CharacterClass
from Model.Content.Feature import FeatureTarget, UsageTag

from .Enums import School
from .Spell import Spell
from .SpellFields import CastingTime, Components, Duration, Range


@dataclass(frozen=True)
class SpellRules:
    """What a spell's card and the rules say about it, as the spell sources
    record it (spells_<source>.json): the fields every spell has, plus the
    sheet's usage_tags and target (spells_<source>_extended.json)."""

    name: str
    level: int
    school: School
    classes: tuple[CharacterClass, ...]
    casting_time: CastingTime
    range: Range
    components: Components
    duration: Duration
    source: str
    description: str
    usage_tags: tuple[UsageTag, ...] = ()
    target: Optional[FeatureTarget] = None
    # What the card shows in brackets after the school: Wildemount's
    # "Dunamancy" or "Dunamancy:Graviturgy" (Evocation (Dunamancy:Graviturgy)).
    school_note: str = ""

    def __post_init__(self):
        if not self.name.strip():
            raise ValueError("A spell needs a name")
        if not 0 <= self.level <= 9:
            raise ValueError(f"{self.name}: level {self.level} isn't 0-9")
        if self.school_note != self.school_note.strip() or any(
            bracket in self.school_note for bracket in "()"
        ):
            raise ValueError(
                f"{self.name}: school_note {self.school_note!r} is the text "
                "inside the brackets"
            )


@dataclass(frozen=True)
class RecordStamp:
    """Which scraped record a class was written from: the source file's name
    (spells_dnd2024.json) and a hash of the record as that file has it. A
    re-scrape that changes the record changes the hash, and
    tests/test_spell_classes.py lists the class for a person to merge (the
    class keeps the text it was converted from; see SpellClassConverter
    --drift and --accept)."""

    source: str
    sha1: str

    @classmethod
    def of(cls, source: str, record: dict) -> "RecordStamp":
        text = json.dumps(record, sort_keys=True, ensure_ascii=False)
        digest = hashlib.sha1(text.encode("utf-8")).hexdigest()[:16]
        return cls(source, digest)


class ClassSpell(Spell):
    """A spell defined by a class (see the module docstring). Subclasses set
    `rules`, and override combat_effects(), improved_description and
    summons() as the spell needs; what they don't override is the Spell
    default (nothing described, the source text, no summons).

    `converted_from` is the scraped record the class was written from, or
    None for a spell that has no record (homebrew)."""

    rules: ClassVar[SpellRules]
    converted_from: ClassVar[Optional[RecordStamp]] = None

    @property
    def name(self) -> str:
        return self.rules.name

    @property
    def level(self) -> int:
        return self.rules.level

    @property
    def school(self) -> str:
        if self.rules.school_note:
            return f"{self.rules.school.value} ({self.rules.school_note})"
        return self.rules.school.value

    @property
    def school_enum(self) -> School:
        return self.rules.school

    @property
    def classes(self) -> list[str]:
        return [character_class.value for character_class in self.rules.classes]

    @property
    def casting_time(self) -> str:
        return self.rules.casting_time.text

    @property
    def casting_time_spec(self) -> CastingTime:
        return self.rules.casting_time

    @property
    def range(self) -> str:
        return self.rules.range.text

    @property
    def range_spec(self) -> Range:
        return self.rules.range

    @property
    def components(self) -> str:
        return self.rules.components.text

    @property
    def components_spec(self) -> Components:
        return self.rules.components

    @property
    def duration(self) -> str:
        return self.rules.duration.text

    @property
    def duration_spec(self) -> Duration:
        return self.rules.duration

    @property
    def description(self) -> str:
        return self.rules.description

    @property
    def source(self) -> str:
        return self.rules.source

    @property
    def usage_tags(self) -> list[str]:
        return list(self.rules.usage_tags)

    @property
    def target(self) -> Optional[FeatureTarget]:
        return self.rules.target
