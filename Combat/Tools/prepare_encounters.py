"""Check a campaign's encounters.py and prepare each encounter's log,
CombatLogs/<encounter id>.json: the encounter, who takes part, and its
monsters and allies at full HP, ready to be played (Combat/EncounterLogs.py).
The combat window only plays prepared encounters.

Run from the repo root:
    python -m Combat.Tools.prepare_encounters                         # the default campaign
    python -m Combat.Tools.prepare_encounters --campaign time_loop_pr
    python -m Combat.Tools.prepare_encounters --all                   # every campaign
    python -m Combat.Tools.prepare_encounters --check                 # check only, write nothing
    python -m Combat.Tools.prepare_encounters wrath_of_durmor         # only these encounters

Nothing is written while the config has problems (unknown monsters or
builds, players not in the party, bad or repeated ids). A log that isn't
prepared yet is written; one not started yet is rewritten when the config
changed; a fight in progress or ended is left as it is (it only gets the
header older logs lack). Combat/Campaigns/ENCOUNTERS.md documents the config.
"""

import argparse
import sys

import Combat.Scenarios as Scenarios
from Combat.Campaign import Campaign
from Combat.EncounterConfig import resolve_players, validate
from Combat.EncounterLogs import prepare_log, scenario_log_path


def prepare_campaign(
    campaign: Campaign, only: list[str] | None = None, write: bool = True
) -> tuple[list[str], list[tuple[str, str]]]:
    """(problems, [(encounter id, what happened to its log)]). Nothing is
    written when there are problems."""
    assert campaign.config is not None, f"{campaign.name} has no encounters.py"
    party_names = [cs.character_name for cs in campaign.players()]
    problems = validate(campaign.config, party_names)
    known = {s.name for s in campaign.scenarios}
    problems += [
        f"no encounter called {name!r}" for name in only or [] if name not in known
    ]
    if problems:
        return problems, []
    results = []
    for scenario in campaign.scenarios:
        if only and scenario.name not in only:
            continue
        players = resolve_players(scenario.players, party_names)
        path = scenario_log_path(campaign.combat_log_dir, scenario.name)
        results.append((scenario.name, prepare_log(path, scenario, players, write)))
    return problems, results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("encounters", nargs="*", help="only these encounter ids")
    parser.add_argument(
        "--campaign",
        choices=sorted(Scenarios.CAMPAIGNS),
        default=Scenarios.DEFAULT_CAMPAIGN,
    )
    parser.add_argument("--all", action="store_true", help="every campaign")
    parser.add_argument(
        "--check", action="store_true", help="check the config; write nothing"
    )
    args = parser.parse_args(argv)

    campaigns = (
        list(Scenarios.CAMPAIGNS.values())
        if args.all
        else [Scenarios.CAMPAIGNS[args.campaign]]
    )
    failed = False
    for campaign in campaigns:
        print(f"{campaign.display_title} ({campaign.folder / 'encounters.py'})")
        problems, results = prepare_campaign(
            campaign, args.encounters or None, write=not args.check
        )
        for problem in problems:
            print(f"  PROBLEM: {problem}")
        failed |= bool(problems)
        for name, what in results:
            if args.check:
                what = {
                    "prepared": "would be prepared",
                    "updated": "would be updated",
                    "in progress, header added": "in progress, header would be added",
                }.get(what, what)
            print(f"  {name:<40} {what}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
