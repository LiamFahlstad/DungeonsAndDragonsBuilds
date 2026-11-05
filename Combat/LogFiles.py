"""Reading and writing the campaign's JSON logs (encounter logs, player logs)
safely.

The combat window rewrites a log on every event, so a crash, a power cut or a
full disk in the middle of a write must not leave half a file: write_json
writes a temporary file next to the log and swaps it in with one rename, so
the log on disk is always either the old version or the new one. read_json
turns a log that still can't be read (edited by hand, cut off before this
existed) into a BrokenLogError that names the file and says how to get it
back, instead of a bare JSONDecodeError from deep inside a replay."""

import json
import os
import time
from pathlib import Path

# The temporary file a write goes to first: "<log>.json.tmp", so it never
# matches "*.json" (prepare_encounters, the Load Encounter dialog).
TMP_SUFFIX = ".tmp"
# Windows refuses a rename onto a file another program has open for a moment
# (a virus scanner, an editor reloading it); try again this many times.
REPLACE_ATTEMPTS = 5
REPLACE_WAIT_SECONDS = 0.1


class BrokenLogError(Exception):
    """A log on disk that isn't valid JSON."""

    def __init__(self, path: Path, error: json.JSONDecodeError):
        self.path = path
        backups = sorted(path.parent.glob(f"{path.stem}_restarted_*.json"))
        lines = [
            f"The log {path} can't be read ({error.msg}, line {error.lineno}).",
            "Get the last committed version back with:",
            f"    git checkout -- {path.as_posix()}",
        ]
        if backups:
            lines.append("or copy one of its backups over it:")
            lines += [f"    {b.name}" for b in backups]
        super().__init__("\n".join(lines))


def read_json(path: str | Path):
    """The JSON in the file at `path`. Raises BrokenLogError when it isn't
    valid JSON, and FileNotFoundError when it isn't there."""
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    try:
        return json.loads(text)
    except json.JSONDecodeError as error:
        raise BrokenLogError(path, error) from error


def write_json(path: str | Path, data, encoder: type[json.JSONEncoder] | None = None):
    """Write `data` as indented JSON to `path` all at once: into a temporary
    file beside it first (flushed to disk), then renamed over it."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(data, indent=2, cls=encoder)
    tmp = path.with_name(path.name + TMP_SUFFIX)
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    for attempt in range(REPLACE_ATTEMPTS):
        try:
            os.replace(tmp, path)
            return
        except PermissionError:
            if attempt == REPLACE_ATTEMPTS - 1:
                raise
            time.sleep(REPLACE_WAIT_SECONDS)
