from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import Combat.EncounterConfig as EncounterConfig
from Combat.Scenario import CombatScenario


@dataclass
class Campaign:
    """A self-contained campaign living in Combat/Campaigns/<Campaign>/: its
    tracked party, its scenarios, and the folders holding its logs.

    `name` is the key used on the command line (--campaign). `players` builds
    the party's members, tracked by --player-log, and `party_allies` the
    allies who travel with them (Combat/PartyAllies.py). Player logs live in
    `<folder>/PlayerLogs/` (the party's is `<party_id>.json`), encounter logs
    in `<folder>/CombatLogs/`. Campaigns are made from their encounters.py
    config (from_config)."""

    name: str
    folder: Path
    players: Callable[[], list]
    scenarios: list[CombatScenario] = field(default_factory=list)
    # How the statistics report names it, e.g. "Curse of the Lich"; defaults to
    # `name` title-cased.
    title: str = ""
    # The encounters.py config it was made from (from_config), for checking it.
    config: EncounterConfig.CampaignSpec | None = None
    # The party's allies (PartySpec.allies), and the party's id, which names
    # its player log.
    party_allies: list[EncounterConfig.CombatantSpec] = field(default_factory=list)
    party_id: str = "main_party"

    @property
    def display_title(self) -> str:
        return self.title or self.name.replace("_", " ").title()

    @property
    def player_log_dir(self) -> Path:
        return self.folder / "PlayerLogs"

    @property
    def combat_log_dir(self) -> Path:
        return self.folder / "CombatLogs"

    @property
    def default_player_log(self) -> Path:
        """The party's player log, PlayerLogs/<party id>.json."""
        return self.player_log_dir / f"{self.party_id}.json"

    def owns_player_log(self, path: str | Path) -> bool:
        """Whether `path` is a player log in this campaign's PlayerLogs/."""
        return Path(path).resolve().parent == self.player_log_dir.resolve()

    @classmethod
    def from_config(
        cls, spec: EncounterConfig.CampaignSpec, folder: str | Path
    ) -> "Campaign":
        """The campaign `spec` (its encounters.py CONFIG, see
        Combat/Campaigns/ENCOUNTERS.md) describes, with its logs in `folder`."""
        party = spec.party_spec
        return cls(
            name=spec.name,
            title=spec.title,
            folder=Path(folder),
            players=lambda: EncounterConfig.build_party(spec),
            scenarios=[CombatScenario.from_spec(e, party) for e in spec.encounters],
            config=spec,
            party_allies=list(party.allies),
            party_id=party.id,
        )
