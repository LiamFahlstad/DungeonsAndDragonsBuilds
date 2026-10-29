import argparse
import sys

import Combat.Scenarios as Scenarios
from Combat.CombatUIQt import CombatAppQt
from Combat.EncounterConfig import resolve_players
from Combat.EncounterLogs import is_prepared, scenario_log_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DnD Combat Engine")
    parser.add_argument(
        "--scenario",
        choices=sorted(Scenarios.SCENARIOS.keys()),
        default=None,
        help="Encounter to play, an id from its campaign's encounters.json. Its log, "
        "CombatLogs/<id>.json, must be prepared first (python -m "
        "Combat.Tools.prepare_encounters). When it holds a fight in progress, the window "
        "asks whether to continue it or restart it (the old log is kept as a backup). Omit "
        "it with --player-log to open the party between encounters.",
    )
    parser.add_argument(
        "--campaign",
        choices=sorted(Scenarios.CAMPAIGNS.keys()),
        default=None,
        help="Campaign to run: its encounters.json gives the party --player-log tracks "
        "and the encounters Load Encounter offers. Defaults to --scenario's campaign, or "
        f"'{Scenarios.DEFAULT_CAMPAIGN}' when no scenario is given.",
    )
    parser.add_argument(
        "--player-log",
        default=None,
        help="Path to a persistent player log JSON file "
        "(e.g. Combat/Campaigns/CurseOfTheLich/PlayerLogs/main_party.json). "
        "It is the party's journal: one line per encounter or rest, each encounter pointing "
        "to its log with the details. The campaign's party is loaded and brought to its "
        "current HP/conditions/slots by replaying those logs since the last long rest. "
        "Who of the party takes part in an encounter is in encounters.json.",
    )
    parser.add_argument(
        "--rest",
        choices=["long", "short"],
        default=None,
        help="Apply a rest to the tracked party instead of launching a session (requires "
        "--player-log). 'long' records a long rest in the player log, after which the party "
        "is fully rested (HP, spell slots, feature uses), without opening any window. "
        "'short' opens a small healing window (not the main combat window) where each "
        "player can be healed a manually-entered amount.",
    )
    parser.add_argument(
        "--difficulty",
        action="store_true",
        help="Print the D&D 2024 difficulty analysis for --scenario's encounter against the "
        "levels of the players taking part (from encounters.json), then exit without "
        "opening the application window.",
    )
    args = parser.parse_args()

    if args.rest and not args.player_log:
        parser.error("--rest requires --player-log")

    if args.difficulty and args.rest:
        parser.error("--difficulty cannot be combined with --rest")

    if args.scenario:
        campaign = Scenarios.SCENARIO_CAMPAIGNS[args.scenario]
        if args.campaign and args.campaign != campaign.name:
            parser.error(
                f"--scenario {args.scenario} belongs to campaign '{campaign.name}', "
                f"not '{args.campaign}'"
            )
    else:
        campaign = Scenarios.CAMPAIGNS[args.campaign or Scenarios.DEFAULT_CAMPAIGN]

    if args.rest:
        from Combat.CombatUIQt.rest import apply_long_rest, run_short_rest

        if args.rest == "long":
            apply_long_rest(args.player_log)
            print(
                f"Long rest recorded in {args.player_log}: the party is fully rested "
                "from the next run on."
            )
        else:
            run_short_rest(args.player_log, campaign)
        sys.exit(0)

    if args.scenario is None and not args.player_log:
        args.scenario = campaign.scenarios[0].name

    scenario = Scenarios.SCENARIOS[args.scenario] if args.scenario else None

    if args.difficulty:
        if scenario is None or not (combatants := scenario.build_combatants()):
            parser.error(
                "--difficulty requires --scenario to have monsters to evaluate"
            )
        allies = scenario.build_allies()
        party = campaign.players()
        taking_part = resolve_players(
            scenario.players, [cs.character_name for cs in party]
        )
        character_sheets = [cs for cs in party if cs.character_name in taking_part]
        if not character_sheets:
            parser.error(
                f"--difficulty requires character levels, and {campaign.name}'s "
                "encounters.json has no party taking part in this encounter"
            )

        from Combat.EncounterDifficulty import (
            classify_difficulty,
            combatant_cr,
            cr_to_xp,
            evaluate_encounter_combatants,
        )

        character_levels = [cs.character_level for cs in character_sheets]
        result = evaluate_encounter_combatants(character_levels, combatants)

        print(f"Scenario: {args.scenario}")
        print(f"Party levels: {character_levels}")
        print(f"Monsters: {[c.combatant_type for c in combatants]}")
        if allies:
            print(f"Allies: {[c.combatant_type for c in allies]}")
        print(f"Base XP: {result.base_xp}")
        print(f"Adjusted XP: {result.adjusted_xp}")
        print(
            "Party thresholds -- "
            f"Low: {result.thresholds.low}, "
            f"Moderate: {result.thresholds.moderate}, "
            f"High: {result.thresholds.high}"
        )
        if allies:
            # Friendly NPCs offset the monsters: rate the fight on monster XP
            # minus the allies' own XP value.
            ally_xp = sum(cr_to_xp(combatant_cr(a)) for a in allies)
            net_xp = result.adjusted_xp - ally_xp
            print(f"Difficulty (monsters only): {result.difficulty}")
            print(f"Ally XP: -{ally_xp}")
            print(f"Net XP (monsters - allies): {net_xp}")
            print(f"Difficulty: {classify_difficulty(net_xp, result.thresholds)}")
        else:
            print(f"Difficulty: {result.difficulty}")
        print(f"XP awarded: {result.xp_awarded}")
        sys.exit(0)

    log_path = None
    if scenario is not None:
        log_path = scenario_log_path(campaign.combat_log_dir, scenario.name)
        if not is_prepared(log_path):
            parser.error(
                f"encounter '{scenario.name}' isn't prepared yet. Prepare its log with:\n"
                f"  python -m Combat.Tools.prepare_encounters --campaign {campaign.name}"
            )

    app = CombatAppQt(
        combatants=[],
        character_sheets=campaign.players() if args.player_log else [],
        combat_log_dir=campaign.combat_log_dir,
        combatants_per_column=scenario.combatants_per_column if scenario else 4,
        log_path=log_path,
        player_log_path=args.player_log,
        scenario_name=args.scenario,
        scenarios=campaign.scenarios,
    )
    app.run()
