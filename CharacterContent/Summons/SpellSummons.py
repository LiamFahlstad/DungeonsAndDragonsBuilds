"""What each summon spell summons: the hand-written part of a spell, kept
apart from the scraped spell JSON, as a spell class's usage_tags are.

`Spell.summons` looks a spell up here by name. Each entry is a factory that
makes the spell's SummonSpec (Model/Content/Summons.py); Notes/summon-
framework-plan.md, Appendix A, lists which spells get one and in which step.

A factory takes the casting ability of the spell it summons for (the
`spell_casting_ability` it was granted with, or None), not the character:
the spec's `build`, `choices` and `count` already get the character when
they run, but which ability a spell is cast with belongs to that copy of the
spell, not to the character (a Wizard/Cleric can have Animate Dead through
either), and a spirit's attack bonus and save DC use it.
"""

from typing import Callable

from Core.Definitions import Ability
from Model.Content.Summons import SummonSpec

SpellSummonFactory = Callable[[Ability | None], SummonSpec]

# Spell name (as in the spell JSON) -> the factory of what it summons.
# Filled in by the plan's Phase 4 steps (S4.5 onwards).
SPELL_SUMMONS: dict[str, SpellSummonFactory] = {}
