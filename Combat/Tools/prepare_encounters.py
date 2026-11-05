"""Check a campaign's encounters.py and get each encounter's log,
CombatLogs/<encounter id>.json, ready: an empty {} until the encounter is
opened, when the combat window sets it up from its EncounterSpec
(Combat/EncounterLogs.py). Run it after changing encounters.py: a log whose
fight hasn't started is emptied, so the changed config sets it up.

Run from the repo root:
    python -m Combat.Tools.prepare_encounters                         # the default campaign
    python -m Combat.Tools.prepare_encounters --campaign time_loop_pr
    python -m Combat.Tools.prepare_encounters --all                   # every campaign
    python -m Combat.Tools.prepare_encounters --check                 # check only, write nothing
    python -m Combat.Tools.prepare_encounters wrath_of_durmor         # only these encounters

Nothing is written while the config has problems (unknown monsters or
builds, players not in the party, bad or repeated ids). A missing log is
created empty; one set up but not started is emptied; a fight in progress
or ended is left as it is, and so is a log that can't be read (it says how to
get it back). Logs in CombatLogs/ named after no encounter (an id that was
renamed or removed) are listed, since the window never opens them.
Combat/Campaigns/ENCOUNTERS.md documents the config.
"""

import argparse
import sys
from pathlib import Path

import Combat.Scenarios as Scenarios
from Combat.Campaign import Campaign
from Combat.EncounterConfig import validate
from Combat.EncounterLogs import empty_log, scenario_log_path
from Combat.LogFiles import BrokenLogError

# What a log that can't be read gets, in prepare_campaign's results.
BROKEN = "can't be read, left as it is"


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
        path = scenario_log_path(campaign.combat_log_dir, scenario.name)
        try:
            results.append((scenario.name, empty_log(path, write)))
        except BrokenLogError as error:
            results.append((scenario.name, f"{BROKEN}\n{error}"))
    return problems, results


def logs_without_encounter(campaign: Campaign) -> list[Path]:
    """The logs in the campaign's CombatLogs/ named after no encounter in
    its encounters.py (not counting restart backups): the window never opens
    them, and their fight is lost to the party's state."""
    folder = Path(campaign.combat_log_dir)
    if not folder.is_dir():
        return []
    known = {s.name for s in campaign.scenarios}
    return sorted(
        path
        for path in folder.glob("*.json")
        if path.stem not in known and "_restarted_" not in path.stem
    )


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
                    "created empty": "would be created empty",
                    "emptied": "would be emptied",
                }.get(what, what)
            failed |= what.startswith(BROKEN)
            print(f"  {name:<40} {what}")
        for path in logs_without_encounter(campaign):
            print(
                f"  NO ENCOUNTER: {path.name} matches no encounter id in "
                "encounters.py; rename it to the encounter's id, or delete it"
            )
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
