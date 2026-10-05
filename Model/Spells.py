"""A character's spells as order-free grants (Notes/model-refactor-plan.md,
Step 9).

Every spell is a SpellGrant: who granted it (`granted_by`, stamped by the
builder's Grants scope - "Wizard", "Rock Gnome", "Magic Initiate"), at which
class-relative level, plus an optional free-text `source` label shown on the
sheet ("Chosen spell"). A replacement ("swap Shield for Absorb Elements") is a
SpellReplacement, resolved when the spells are read - so neither the order
spells are granted in nor the order of grants and replacements matters.
"""

from typing import Optional

import attr

from Core.Definitions import Ability


@attr.s(frozen=True, auto_attribs=True)
class SpellGrant:
    name: str
    ability: Ability
    ruling: Optional[str]
    grant_level: int
    granted_by: str
    source: Optional[str] = None


@attr.s(frozen=True, auto_attribs=True)
class SpellReplacement:
    """Every grant of `old` becomes `new`, keeping its grant level, who
    granted it and its label. `ability`/`ruling` override the old grant's
    when given."""

    old: str
    new: str
    ability: Optional[Ability] = None
    ruling: Optional[str] = None


def resolve_spells(
    grants: list[SpellGrant], replacements: list[SpellReplacement]
) -> list[SpellGrant]:
    """The spells a character knows, in canonical order (grant level, name,
    granted_by, source). Raises on a replacement of a spell nobody grants, on
    two replacements of one spell, on a chain (a replacement of a spell that
    is itself a replacement - its result would depend on the order they
    resolve in), and on one spell granted twice by the same grant."""
    by_old: dict[str, SpellReplacement] = {}
    for replacement in replacements:
        if replacement.old in by_old:
            raise ValueError(f"Spell {replacement.old} is replaced twice.")
        by_old[replacement.old] = replacement
    granted = {grant.name for grant in grants}
    for replacement in replacements:
        if replacement.old not in granted:
            raise ValueError(f"Spell {replacement.old} not found to replace.")
        if replacement.new in by_old:
            raise ValueError(
                f"Spell replacements chain ({replacement.old} -> {replacement.new} "
                f"-> {by_old[replacement.new].new}); replace each spell once."
            )

    resolved = []
    for grant in grants:
        replacement = by_old.get(grant.name)
        if replacement is not None:
            grant = attr.evolve(
                grant,
                name=replacement.new,
                ability=replacement.ability or grant.ability,
                ruling=(
                    replacement.ruling
                    if replacement.ruling is not None
                    else grant.ruling
                ),
            )
        resolved.append(grant)

    seen: set[tuple[str, str]] = set()
    for grant in resolved:
        key = (grant.name, grant.granted_by)
        if key in seen:
            raise ValueError(
                f"Spell {grant.name} already added (granted twice by "
                f"{grant.granted_by})."
            )
        seen.add(key)
    return sorted(
        resolved,
        key=lambda g: (g.grant_level, g.name, g.granted_by, g.source or ""),
    )
