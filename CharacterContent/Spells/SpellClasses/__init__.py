"""Spells written as classes, one module per level, and SPELL_CLASSES:
each class by its spell's name, which SpellFactory uses instead of the
spell's JSON record. Written by CharacterContent/Spells/
SpellClassConverter.py; a module it doesn't know is not listed."""

from . import Cantrips
from . import Level1
from . import Level2
from . import Level3
from . import Level4
from CharacterContent.Spells.SpellFactory.ClassSpell import ClassSpell

MODULES: tuple = (
    Cantrips,
    Level1,
    Level2,
    Level3,
    Level4,
)

SPELL_CLASSES: dict[str, type[ClassSpell]] = {}
for _module in MODULES:
    for _spell in _module.SPELLS:
        if _spell.rules.name in SPELL_CLASSES:
            raise ValueError(f"Two classes for the spell {_spell.rules.name!r}")
        SPELL_CLASSES[_spell.rules.name] = _spell
