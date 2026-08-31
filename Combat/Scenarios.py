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
