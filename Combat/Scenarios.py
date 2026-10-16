"""Registry of runnable combat scenarios. Select one with `python RunCombatSimulator.py --scenario <name>`."""

import Combat.Campaigns.CurseOfTheLich.Encounters as CurseOfTheLichEncounters
from Combat.Scenario import CombatScenario

SCENARIOS: dict[str, CombatScenario] = {}


def _register(scenario: CombatScenario) -> CombatScenario:
    SCENARIOS[scenario.name] = scenario
    return scenario


ASHELM_CHURCH = _register(
    CombatScenario(
        name="ashelm_church",
        combatants=lambda: CurseOfTheLichEncounters.get_accursed_ambush_combatants(),
    )
)

GOBLIN_SCOUTING_PARTY = _register(
    CombatScenario(
        name="goblin_scouting_party",
        combatants=lambda: CurseOfTheLichEncounters.get_goblin_scouting_party_combatants(),
        allies=lambda: CurseOfTheLichEncounters.get_stonehill_allies(),
        combatants_per_column=5,
    )
)

GOBLIN_WARBAND_AMBUSH = _register(
    CombatScenario(
        name="goblin_warband_ambush",
        combatants=lambda: CurseOfTheLichEncounters.get_goblin_warband_ambush_combatants(),
        allies=lambda: CurseOfTheLichEncounters.get_stonehill_allies(),
        combatants_per_column=5,
    )
)

WRATH_OF_DURMOR = _register(
    CombatScenario(
        name="wrath_of_durmor",
        combatants=lambda: CurseOfTheLichEncounters.get_wrath_of_durmor_combatants(),
        allies=lambda: CurseOfTheLichEncounters.get_stonehill_allies(),
        combatants_per_column=5,
    )
)
