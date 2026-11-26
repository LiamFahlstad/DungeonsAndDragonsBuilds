"""What a combatant has all the time, and what a saving throw is against
(Notes/combat-effects-plan.md, step 9.2). Qt-free, and below modifiers.py,
which reads it: modifiers_on counts these beside the rules conditions, cover
and badges.

Always on: a player's features say theirs (Feature.combat_modifiers: War
Caster, Brave, Danger Sense), a stat block's traits theirs by name
(TRAIT_MODIFIERS: Magic Resistance), as Feature.movement and TRAIT_MOVEMENT
do for moving (Combat/Arena/speeds.py). A modifier its bearer loses while it
has a condition (Danger Sense's "unless you have the Incapacitated
condition": D20Mode.unless_conditions) is left out then.

What a save is against (SaveAgainst), where the simulator rolls one, settles
a D20Mode that counts only against some saves, as a distance settles
Prone's AttacksAgainst: Magic Resistance's Advantage counts against a spell,
Brave's against Frightened, War Caster's in a Concentration save. One that
can't be told stays a note for the GM, as a `when` is (plan principle 8):
Magic Resistance against a feature's effect, which may be magical.
"""

from collections.abc import Iterable
from dataclasses import dataclass, replace

from Core.Definitions import Condition
from Model.Content.CombatModifiers import D20Mode, D20Test, Modifier, RollMode
from Model.Content.RulesConditions import rules_condition

# Stat-block traits that are always-on rules for rolls, by name: every Magic
# Resistance, structured (MagicResistance) or as generated text, reads "has
# Advantage on saving throws against spells and other magical effects".
TRAIT_MODIFIERS: dict[str, tuple[Modifier, ...]] = {
    "Magic Resistance": (
        D20Mode((D20Test.SAVING_THROW,), RollMode.ADVANTAGE, against_spells=True),
    ),
}


def _trait_names(char: dict) -> list[str]:
    """The names of char's stat-block traits, from the stat block or a
    saved log's dicts."""
    return [
        str(t.get("name") if isinstance(t, dict) else getattr(t, "name", ""))
        for t in char.get("traits") or ()
    ]


def always_on_modifiers(
    char: dict, held: Iterable[Condition]
) -> list[tuple[str, Modifier]]:
    """Each modifier char has all the time, with what gives it: its
    features' (Feature.combat_modifiers) and its stat block's traits'
    (TRAIT_MODIFIERS), less those a condition it `held`s stops."""
    sheet = char.get("_stat_block")
    found = [
        (feature.name, modifier)
        for feature in char.get("_feature_objects") or ()
        for modifier in getattr(feature, "combat_modifiers", lambda _: ())(sheet)
    ]
    found += [
        (name, modifier)
        for name in _trait_names(char)
        for modifier in TRAIT_MODIFIERS.get(name, ())
    ]
    stopped = set(held)
    return [
        (label, m)
        for label, m in found
        if not stopped & set(getattr(m, "unless_conditions", ()))
    ]


@dataclass(frozen=True)
class SaveAgainst:
    """What a saving throw is against, as far as the simulator knows where
    it's rolled. `spell`: whether it's against a spell (a spell's row, or a
    monster's or a feature's casting of one), None when that isn't known
    (an effect typed in); `conditions`: the conditions it would give, or the
    one a repeat save ends, by name; `concentration`: a save to keep
    Concentration."""

    spell: bool | None = None
    conditions: tuple[str, ...] = ()
    concentration: bool = False


# A Concentration save: against the damage taken, not a spell (War Caster).
KEEPS_CONCENTRATION = SaveAgainst(spell=False, concentration=True)


def _gate_holds(modifier: D20Mode, against: SaveAgainst | None) -> bool | str:
    """Whether a D20Mode's save gates hold for a save `against` that (None:
    nothing known about it): True, False, or what the GM is to judge, for a
    `when` ("the effect is magical")."""
    judged: list[str] = []
    if modifier.against_spells:
        # "spells and other magical effects": a spell's counts; anything
        # else may still be magical, which the GM knows.
        if against is None or against.spell is None:
            judged.append("the save is against a spell or other magical effect")
        elif not against.spell:
            judged.append("the effect is magical")
    if modifier.against_conditions:
        names = " or ".join(c.value for c in modifier.against_conditions)
        if against is None:
            judged.append(f"the save is to avoid or end the {names} condition")
        else:
            given = {rules_condition(name) for name in against.conditions}
            if not given & set(modifier.against_conditions):
                return False
    if modifier.concentration:
        if against is None:
            judged.append("the save is to keep Concentration")
        elif not against.concentration:
            return False
    return " and ".join(judged) if judged else True


def settled_saves(
    sources: Iterable[tuple[str, Modifier]], against: SaveAgainst | None
) -> list[tuple[str, Modifier]]:
    """A save's sources with their save gates settled by what it's against:
    one that holds counts, one that doesn't is left out, and one that can't
    be told is a `when`, noted for the GM."""
    settled: list[tuple[str, Modifier]] = []
    for label, modifier in sources:
        gated = isinstance(modifier, D20Mode) and (
            modifier.against_spells
            or modifier.against_conditions
            or modifier.concentration
        )
        if not gated:
            settled.append((label, modifier))
            continue
        assert isinstance(modifier, D20Mode)
        holds = _gate_holds(modifier, against)
        if holds is False:
            continue
        plain = replace(
            modifier, against_spells=False, against_conditions=(), concentration=False
        )
        if holds is not True:
            when = f"{modifier.when} and {holds}" if modifier.when else holds
            plain = replace(plain, when=when)
        settled.append((label, plain))
    return settled
