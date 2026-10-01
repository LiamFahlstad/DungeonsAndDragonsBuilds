from Core.Definitions import Sense
from Model.Recorder import Recorder, records


class Senses(Recorder):
    """Special senses (Darkvision, Blindsight, ...), each granted at a range
    by one or more sources. "Gain it, or +N if you already have it" grants
    (add_sense_or_extension) are kept separately and added on top of the best
    plain grant, so the result doesn't depend on which applied first.

    Merge rule: best plain grant + sum of extensions, per sense. Reads list
    senses in enum order and sources sorted by (source, range)."""

    def __init__(self):
        # Every (range, source) pair granted per sense; the range itself is
        # worked out on read - see ranges.
        self._sense_sources: dict[Sense, list[tuple[int, str]]] = {}
        # "...or if you already have it, its range increases by N" grants.
        self._sense_extensions: dict[Sense, list[tuple[int, str]]] = {}

    @records
    def add_sense(self, sense: Sense, range_feet: int, source: str) -> None:
        """Grant a sense. The same sense from several sources keeps the best range."""
        self._sense_sources.setdefault(sense, []).append((range_feet, source))

    @records
    def add_sense_or_extension(
        self, sense: Sense, range_feet: int, source: str
    ) -> None:
        """Grant a sense out to `range_feet` - or, if the character already has
        it, increase its range by `range_feet` (e.g. Umbral Sight)."""
        self._sense_extensions.setdefault(sense, []).append((range_feet, source))

    @property
    def ranges(self) -> dict[Sense, int]:
        """Range per sense: the best plain grant plus every extension. "Gain it,
        or +N if you already have it" is N on top of whatever else grants it,
        so the result doesn't depend on which applied first."""
        ranges = {}
        for sense in Sense:
            if sense not in self._sense_sources and sense not in self._sense_extensions:
                continue
            best = max((r for r, _ in self._sense_sources.get(sense, [])), default=0)
            extra = sum(r for r, _ in self._sense_extensions.get(sense, []))
            ranges[sense] = best + extra
        return ranges

    def get_sense_range(self, sense: Sense) -> int:
        return self.ranges.get(sense, 0)

    def get_sense_sources(self, sense: Sense) -> list[tuple[int, str]]:
        """Plain grants, then extensions, each sorted by (source, range)."""

        def by_source(grant: tuple[int, str]) -> tuple[str, int]:
            return grant[1], grant[0]

        return sorted(self._sense_sources.get(sense, []), key=by_source) + [
            (range_feet, f"{source} (+{range_feet} ft. if already had)")
            for range_feet, source in sorted(
                self._sense_extensions.get(sense, []), key=by_source
            )
        ]
