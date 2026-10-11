"""Creature ability_scores / saving_throws keys (Model/Creatures/Combatants.py).

Stat blocks look scores up by Ability.short_name, so a misspelled key used to
render silently as 10 (+0). Keys are now normalised and checked on creation.
"""

import pytest

from Core.Definitions import Ability
from Model.Creatures.Combatants import BasicCombatantData


def _creature(**kwargs) -> BasicCombatantData:
    return BasicCombatantData(
        combatant_type="Test", hp=1, ac=10, temp_hp=0, conditions=[], **kwargs
    )


def test_ability_enum_keys_become_short_names():
    creature = _creature(
        ability_scores={Ability.STRENGTH: 16, Ability.CHARISMA: 8},
        saving_throws={Ability.DEXTERITY: 3},
    )
    assert creature.ability_scores == {"STR": 16, "CHA": 8}
    assert creature.saving_throws == {"DEX": 3}


def test_short_name_string_keys_are_accepted():
    creature = _creature(ability_scores={"WIS": 14})
    assert creature.ability_scores == {"WIS": 14}


@pytest.mark.parametrize("bad_key", ["Str", "str", "Strength", "STRENGTH"])
@pytest.mark.parametrize("field", ["ability_scores", "saving_throws"])
def test_other_keys_are_rejected(field, bad_key):
    with pytest.raises(ValueError, match="Invalid ability key"):
        _creature(**{field: {bad_key: 10}})
