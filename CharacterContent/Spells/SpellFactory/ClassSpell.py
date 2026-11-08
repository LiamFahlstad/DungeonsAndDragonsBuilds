"""A spell written as a Python class, the way a Feature is: its rules as a
SpellRules record, and what it does as methods (combat_effects(),
improved_description, summons()). SpellFactory uses the class of a spell's
name instead of its JSON record; a spell without a class still comes from
the JSON (DataSpell). See Notes/combat-effects-plan.md, "Spells as classes".

    class Fireball(ClassSpell):
        rules = SpellRules(
            name="Fireball",
            level=3,
            school="Evocation",
            classes=("Sorcerer", "Wizard"),
            casting_time="Action",
            range="150 feet",
            components="V, S, M (a ball of bat guano and sulfur)",
            duration="Instantaneous",
            source="Player's Handbook",
            usage_tags=("damage",),
            description="A bright streak flashes from you ...",
        )

        def combat_effects(self, character=None) -> list[CombatEffect]:
            return [CombatEffect(roll="save", save_ability=Ability.DEXTERITY, ...)]

CharacterContent/Spells/SpellClassConverter.py writes such a class from a
spell's JSON record and its companion files; from then on the class is the
spell's one source, edited by hand.
"""

from dataclasses import dataclass
from typing import ClassVar, Optional

from Model.Content.Feature import FeatureTarget

from .Spell import Spell


@dataclass(frozen=True)
class SpellRules:
    """What a spell's card and the rules say about it, as the spell sources
    record it (spells_<source>.json): the fields every spell has, plus the
    sheet's usage_tags and target (spells_<source>_extended.json)."""

    name: str
    level: int
    school: str
    classes: tuple[str, ...]
    casting_time: str
    range: str
    components: str
    duration: str
    source: str
    description: str
    usage_tags: tuple[str, ...] = ()
    target: Optional[FeatureTarget] = None

    def __post_init__(self):
        if not self.name.strip():
            raise ValueError("A spell needs a name")
        if not 0 <= self.level <= 9:
            raise ValueError(f"{self.name}: level {self.level} isn't 0-9")


class ClassSpell(Spell):
    """A spell defined by a class (see the module docstring). Subclasses set
    `rules`, and override combat_effects(), improved_description and
    summons() as the spell needs; what they don't override is the Spell
    default (nothing described, the source text, no summons)."""

    rules: ClassVar[SpellRules]

    @property
    def name(self) -> str:
        return self.rules.name

    @property
    def level(self) -> int:
        return self.rules.level

    @property
    def school(self) -> str:
        return self.rules.school

    @property
    def classes(self) -> list[str]:
        return list(self.rules.classes)

    @property
    def casting_time(self) -> str:
        return self.rules.casting_time

    @property
    def range(self) -> str:
        return self.rules.range

    @property
    def components(self) -> str:
        return self.rules.components

    @property
    def duration(self) -> str:
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
