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
    the 'Players' group tracked by --player-log. Player logs live in
    `<folder>/PlayerLogs/`, encounter logs in `<folder>/CombatLogs/`.
    Campaigns are made from their encounters.json (from_config)."""

    name: str
    folder: Path
    players: Callable[[], list]
    scenarios: list[CombatScenario] = field(default_factory=list)
    # How the statistics report names it, e.g. "Curse of the Lich"; defaults to
    # `name` title-cased.
    title: str = ""
    # The encounters.json it was made from (from_config), for checking it.
    config: EncounterConfig.CampaignSpec | None = None

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
        return self.player_log_dir / "main_party.json"

    @classmethod
    def from_config(cls, folder: str | Path) -> "Campaign":
        """The campaign <folder>/encounters.json describes (see
        Combat/Campaigns/ENCOUNTERS.md)."""
        spec = EncounterConfig.load(folder)
        return cls(
            name=spec.name,
            title=spec.title,
            folder=Path(folder),
            players=lambda: EncounterConfig.build_party(spec),
            scenarios=[CombatScenario.from_spec(e) for e in spec.encounters],
            config=spec,
        )
