import argparse
import sys

import Combat.Scenarios as Scenarios
from Combat.CombatUIQt import CombatAppQt
from Combat.EncounterLogs import scenario_log_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DnD Combat Engine")
    parser.add_argument(
        "--scenario",
        choices=sorted(Scenarios.SCENARIOS.keys()),
        default=None,
        help="Combat scenario to run. Omit to run without an encounter "
        "(e.g. an out-of-combat adventure session when combined with --player-log).",
    )
    parser.add_argument(
        "--log",
        default=None,
        help="Path to a Combat/Campaigns/<Campaign>/CombatLogs/*.json encounter log to "
        "use. Defaults to --scenario's own log, CombatLogs/<scenario>.json (created if "
        "missing). When the log holds a fight in progress, the window asks whether to "
        "continue it (HP/conditions/round where it left off) or restart it with fresh "
        "monsters (the old log is kept as a backup).",
    )
    parser.add_argument(
        "--campaign",
        choices=sorted(Scenarios.CAMPAIGNS.keys()),
        default=None,
        help="Campaign to run: its 'Players' group is what --player-log tracks, and new "
        "encounter logs are written to its CombatLogs folder. Defaults to --scenario's "
        f"campaign, or '{Scenarios.DEFAULT_CAMPAIGN}' when no scenario is given.",
    )
    parser.add_argument(
        "--player-log",
        default=None,
        help="Path to a persistent player log JSON file "
        "(e.g. Combat/Campaigns/CurseOfTheLich/PlayerLogs/main_party.json). "
        "It is the party's journal: one line per encounter, adventure or rest, each pointing "
        "to the encounter log with the details. The 'Players' combatant group is loaded and "
        "brought to its current HP/conditions/slots by replaying those logs since the last "
        "long rest.",
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
        "party's levels, then exit without opening the application window. Requires character "
        "levels: pass --player-log to source them from a tracked party, or use a scenario whose "
        "build_character_sheets provides them.",
    )
    parser.add_argument(
        "--absent",
        nargs="+",
        default=[],
        metavar="NAME",
        help="Leave these players out of the tracked party for this session (requires "
        "--player-log). Matches case-insensitively on part of the character name, e.g. "
        "--absent Gabriel. Their player-log history is kept and picked up again the next "
        "time they're loaded.",
    )
    args = parser.parse_args()

    if args.absent and not args.player_log:
        parser.error("--absent requires --player-log")

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

    if args.scenario and args.log is None:
        args.log = str(scenario_log_path(campaign.combat_log_dir, args.scenario))

    scenario = Scenarios.SCENARIOS[args.scenario] if args.scenario else None
    combatants = scenario.build_combatants() if scenario else []
    allies = scenario.build_allies() if scenario else []
    character_sheets = scenario.build_character_sheets() if scenario else []

    if args.player_log:
        players_group = campaign.players()
        for absent in args.absent:
            matches = [
                cs
                for cs in players_group
                if absent.lower() in cs.character_name.lower()
            ]
            if not matches:
                parser.error(f"--absent: no player name contains '{absent}'")
            players_group = [cs for cs in players_group if cs not in matches]
        player_names = {cs.character_name for cs in players_group}
        character_sheets = [
            cs for cs in character_sheets if cs.character_name not in player_names
        ]
        character_sheets = players_group + character_sheets

    if args.difficulty:
        if not combatants:
            parser.error(
                "--difficulty requires --scenario to have monsters to evaluate"
            )
        if not character_sheets:
            parser.error(
                "--difficulty requires character levels; pass --player-log to load a "
                "tracked party, or use a scenario whose build_character_sheets provides them"
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

    app = CombatAppQt(
        combatants=allies + combatants,
        character_sheets=character_sheets,
        combat_log_dir=campaign.combat_log_dir,
        combatants_per_column=scenario.combatants_per_column if scenario else 4,
        resume_log_path=args.log,
        player_log_path=args.player_log,
        scenario_name=args.scenario,
        scenarios=campaign.scenarios,
    )
    app.run()
