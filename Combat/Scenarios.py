"""Registry of runnable combat scenarios. Select one with `python RunCombat.py --scenario <name>`."""

import Combat.Campaigns.GrimsCastle.Encounters as GrimsCastleEncounters
import Combat.Campaigns.TimeLoop.Encounters as TimeLoopEncounters
from Builds.Characters.OptimizedPaladinVengeance import OptimizedPaladinVengeanceCharacterBuilder
from Combat.Monsters.CR_24 import AncientRedDragon
from Combat.Scenario import CombatScenario

SCENARIOS: dict[str, CombatScenario] = {}


def _register(scenario: CombatScenario) -> CombatScenario:
    SCENARIOS[scenario.name] = scenario
    return scenario


TIME_LOOP_SQUARE = _register(
    CombatScenario(
        name="time_loop_square",
        combatants=lambda: (
            TimeLoopEncounters.get_players()
            + TimeLoopEncounters.get_square_combatants()
            + GrimsCastleEncounters.get_bull()
            + [AncientRedDragon()]
        ),
        character_sheets=lambda: [OptimizedPaladinVengeanceCharacterBuilder().build()],
    )
)

TIME_LOOP_DRUNK_OXE = _register(
    CombatScenario(
        name="time_loop_drunk_oxe",
        combatants=lambda: (
            TimeLoopEncounters.get_players() + TimeLoopEncounters.get_drunk_oxe_combatants()
        ),
        character_sheets=lambda: [OptimizedPaladinVengeanceCharacterBuilder().build()],
    )
)

GRIMS_CASTLE_BULL = _register(
    CombatScenario(
        name="grims_castle_bull",
        combatants=lambda: GrimsCastleEncounters.get_players() + GrimsCastleEncounters.get_bull(),
    )
)
