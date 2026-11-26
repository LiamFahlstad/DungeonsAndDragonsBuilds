"""How a d20 roll is made once the modifiers count: a saving throw's plan, by
what the save is against (always_on.SaveAgainst). Qt-free. The first of the
roll plans to leave modifiers.py, which keeps the modifiers on a combatant
(Notes/combat-ui-refactor-plan.md, step 9a: roll_plans.py takes the save and
attack plans); the attack plan is still there.
"""

from Model.Content.CombatModifiers import D20Test

from .always_on import SaveAgainst, settled_saves
from .modifiers import RollPlan, _label, _plan, modifiers_on


def save_plan(
    char: dict,
    ability: str,
    mode: str,
    typed: bool = False,
    against: SaveAgainst | None = None,
) -> RollPlan:
    """Char's saving throw of `ability` ("DEX"), asked for with `mode`.
    `typed`: a total rolled at the table, which only an automatic failure
    changes; its mode and bonuses are the GM's. `against`: what the save is
    against, which settles a modifier that counts only against some (Magic
    Resistance's spells, Brave's Frightened, War Caster's Concentration);
    None: not known, so those are only noted."""
    sources = settled_saves(((_label(c), m) for c, m in modifiers_on(char)), against)
    return _plan(mode, sources, D20Test.SAVING_THROW, ability, typed)
