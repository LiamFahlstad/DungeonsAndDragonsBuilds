"""The shapes of the sources a Character holds: features, fighting styles,
armor, weapons and items. They live in CharacterContent, which imports the
Model, so the Model names them only through these Protocols. A feature or an
item satisfies them structurally, without importing this module.

Each Protocol lists exactly what the Model reads. Widen one only when Model
code starts reading something new.
"""

from typing import Optional, Protocol

from Model.Effects import Effects


class Effect(Protocol):
    """Anything that records into a character's Ledger."""

    def apply(self, effects: Effects) -> None: ...


class GrantedFeature(Effect, Protocol):
    """A feature, feat or fighting-style card on the sheet. `extensions`
    goes away in Step 8 of Notes/model-refactor-plan.md, when extensions
    become declared grants on the Character."""

    name: str
    extensions: list["GrantedFeature"]


class Gear(Effect, Protocol):
    """Armor, a weapon or an item: carried, maybe worn, maybe attuned."""

    name: str
    is_wearing: Optional[bool]
    requires_attunement: bool
    value: Optional[float]


class ArmorGear(Gear, Protocol):
    is_shield: bool
