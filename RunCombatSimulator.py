import argparse
import sys

import Combat.Scenarios as Scenarios
from Combat.CombatUIQt import CombatAppQt

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
        help="Path to a Combat/Campaigns/<Campaign>/CombatLogs/*.json file to resume from, "
        "picking up the combatants' HP/conditions/round where that log left off",
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
        "The 'Players' combatant group is loaded, preloading HP/conditions/etc. from the most "
        "recent session, and every action taken against a player is appended to this file "
        "across runs. A new session entry ('encounter' if --scenario is given, else 'adventure') "
        "is started each run.",
    )
    parser.add_argument(
        "--rest",
        choices=["long", "short"],
        default=None,
        help="Apply a rest to the tracked party instead of launching a session (requires "
        "--player-log). 'long' fully restores HP and spell slots by resetting the player "
        "log in place, first backing up its session history to a new, timestamped sibling "
        "file, without opening any window. 'short' opens a small healing window (not the "
        "main combat window) where each player can be healed a manually-entered amount, "
        "updating the existing player log in place.",
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
            backup_path = apply_long_rest(args.player_log)
            print(
                f"Long rest applied. Player log reset; old session history backed up to: {backup_path}"
            )
        else:
            run_short_rest(args.player_log, campaign)
        sys.exit(0)

    if args.scenario is None and not args.player_log:
        args.scenario = campaign.scenarios[0].name

    scenario = Scenarios.SCENARIOS[args.scenario] if args.scenario else None
    combatants = scenario.build_combatants() if scenario else []
    allies = scenario.build_allies() if scenario else []
    character_sheets = scenario.build_character_sheets() if scenario else []

    if args.player_log:
        players_group = campaign.players()
        for absent in args.absent:
            matches = [
                cs for cs in players_group if absent.lower() in cs.character_name.lower()
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
            ally_xp = sum(cr_to_xp(a.cr) for a in allies)
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
    )
    app.run()
