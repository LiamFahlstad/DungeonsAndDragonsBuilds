"""Registry of runnable combat scenarios. Select one with `python RunCombatSimulator.py --scenario <name>`."""

import Combat.Campaigns.CurseOfTheLich.Encounters as CurseOfTheLichEncounters
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

CURSE_OF_THE_LICH_BLACK_TONGUES_SKIRMISH = _register(
    CombatScenario(
        name="curse_of_the_lich_black_tongues_skirmish",
        combatants=lambda: CurseOfTheLichEncounters.get_black_tongues_skirmish_combatants(),
        character_sheets=lambda: CurseOfTheLichEncounters.get_players(),
    )
)

CURSE_OF_THE_LICH_YELLOW_CAPES_PATROL = _register(
    CombatScenario(
        name="curse_of_the_lich_yellow_capes_patrol",
        combatants=lambda: CurseOfTheLichEncounters.get_yellow_capes_patrol_combatants(),
        character_sheets=lambda: CurseOfTheLichEncounters.get_players(),
    )
)

CURSE_OF_THE_LICH_BLACK_TONGUES_RITUAL = _register(
    CombatScenario(
        name="curse_of_the_lich_black_tongues_ritual",
        combatants=lambda: CurseOfTheLichEncounters.get_black_tongues_ritual_combatants(),
        character_sheets=lambda: CurseOfTheLichEncounters.get_players(),
    )
)

CURSE_OF_THE_LICH_YELLOW_CAPES_LAST_STAND = _register(
    CombatScenario(
        name="curse_of_the_lich_yellow_capes_last_stand",
        combatants=lambda: CurseOfTheLichEncounters.get_yellow_capes_last_stand_combatants(),
        character_sheets=lambda: CurseOfTheLichEncounters.get_players(),
    )
)

CURSE_OF_THE_LICH_MOUTH_THAT_WALKS = _register(
    CombatScenario(
        name="curse_of_the_lich_mouth_that_walks",
        combatants=lambda: CurseOfTheLichEncounters.get_mouth_that_walks_combatants(),
        character_sheets=lambda: CurseOfTheLichEncounters.get_players(),
    )
)
