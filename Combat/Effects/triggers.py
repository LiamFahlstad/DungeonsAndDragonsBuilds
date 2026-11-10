"""What lasting effects do as a turn starts or ends (Notes/combat-effects-plan.md,
step 3.5): the AtTurnStart and AtTurnEnd a badge's modifiers hold, as the
records in char["active_effects"] keep them. This finds which come with a
turn; the combat window uses each (TurnPanelMixin): Hit Points it gives
itself, and anything else, or anything with a `when`, is a prompt for the GM.

A trigger of WhoseTurn.BEARER comes with each turn of whoever has the badge
(Heroism's target). One of WhoseTurn.ENEMY comes with each turn of every
creature not on the side of the badge's caster (Spirit Guardians'), once
however many creatures have the badge: Cast Spell puts it on the targets a
spell is aimed at, the Custom Effect dialog on whoever is targeted, and
neither says where the Emanation is. A trigger counts only while its badge is
on, as a modifier does. Nothing here imports Qt."""

from collections.abc import Callable, Iterable
from dataclasses import dataclass

from Combat.PartyAllies import is_party_ally
from Combat.Summons import owner_name
from Model.Content.CombatModifiers import (
    AtTurnEnd,
    AtTurnStart,
    Trigger,
    WhoseTurn,
)

from .modifiers import _effects_with_modifiers


@dataclass(frozen=True)
class Firing:
    """One trigger coming with one creature's turn: the badge's `bearer`
    has `badge` (its record's `source` and `caster`, if known), and
    `trigger` happens to `target`, whose turn it is."""

    bearer: dict
    badge: str
    source: str | None
    caster: str | None
    trigger: Trigger
    target: dict

    @property
    def is_prompt(self) -> bool:
        """Whether the GM decides it: it has a `when` (where creatures are)."""
        return bool(self.trigger.when)

    @property
    def prompt(self) -> str:
        """The question the turn column asks about it: "Tiger: if it ends its
        turn in the Emanation, Edmund's Spirit Guardians: damage"."""
        whose = f"{self.caster}'s " if self.caster else ""
        when = f"if {self.trigger.when}, " if self.trigger.when else ""
        return f"{self.target['name']}: {when}{whose}{self.trigger.effect}"


def on_party_side(char: dict) -> bool:
    """Whether char fights on the party's side: a player, a party ally, or a
    player's summon."""
    return bool(
        char.get("_is_player") or is_party_ally(char) or owner_name(char) is not None
    )


def firings(
    chars: Iterable[dict],
    turn: Iterable[dict],
    kind: type[AtTurnStart] | type[AtTurnEnd],
    find: Callable[[str], dict | None],
) -> list[Firing]:
    """The triggers of `kind` that come with the turn of the creatures in
    `turn`, from the badges every one of `chars` has. `find` gives a
    combatant by name (the caster of an enemy-turn trigger, to know its
    side); a trigger of a caster that isn't in the fight comes with no
    enemy's turn."""
    chars = list(chars)
    turn = list(turn)
    found: list[Firing] = []
    seen: set[tuple] = set()
    for bearer in chars:
        for effect, modifier in _effects_with_modifiers(bearer):
            if not isinstance(modifier, kind):
                continue
            caster = effect.get("caster")
            if modifier.whose is WhoseTurn.BEARER:
                targets = [c for c in turn if c is bearer]
            else:
                whose = find(caster) if caster else None
                if whose is None:
                    continue
                targets = [
                    c
                    for c in turn
                    if c is not whose and on_party_side(c) != on_party_side(whose)
                ]
            for target in targets:
                key = (caster, effect["name"], modifier, target["name"])
                if modifier.whose is WhoseTurn.ENEMY and key in seen:
                    continue
                seen.add(key)
                found.append(
                    Firing(
                        bearer=bearer,
                        badge=effect["name"],
                        source=effect.get("source"),
                        caster=caster,
                        trigger=modifier,
                        target=target,
                    )
                )
    return found
