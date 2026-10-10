import attr

from Core.Definitions import Sense


@attr.s(frozen=True, auto_attribs=True)
class SenseGrant:
    """One grant of a sense: its range in feet and where it comes from."""

    range_feet: int
    source: str


def _by_source(grant: SenseGrant) -> tuple[str, int]:
    return grant.source, grant.range_feet


class Senses:
    """Special senses (Darkvision, Blindsight, ...), each granted at a range
    by one or more sources. "Gain it, or +N if you already have it" grants
    (add_sense_or_extension) are kept separately and added on top of the best
    plain grant, so the result doesn't depend on which applied first.

    Merge rule: best plain grant + sum of extensions, per sense. Reads list
    senses in enum order and sources sorted by (source, range)."""

    def __init__(self):
        # Every grant per sense; the range itself is worked out on read -
        # see ranges.
        self._sense_sources: dict[Sense, list[SenseGrant]] = {}
        # "...or if you already have it, its range increases by N" grants.
        self._sense_extensions: dict[Sense, list[SenseGrant]] = {}

    def add_sense(self, sense: Sense, range_feet: int, source: str) -> None:
        """Grant a sense. The same sense from several sources keeps the best range."""
        grant = SenseGrant(range_feet, source)
        self._sense_sources.setdefault(sense, []).append(grant)

    def add_sense_or_extension(
        self, sense: Sense, range_feet: int, source: str
    ) -> None:
        """Grant a sense out to `range_feet` - or, if the character already has
        it, increase its range by `range_feet` (e.g. Umbral Sight)."""
        grant = SenseGrant(range_feet, source)
        self._sense_extensions.setdefault(sense, []).append(grant)

    @property
    def ranges(self) -> dict[Sense, int]:
        """Range per sense: the best plain grant plus every extension. "Gain it,
        or +N if you already have it" is N on top of whatever else grants it,
        so the result doesn't depend on which applied first."""
        ranges = {}
        for sense in Sense:
            plain = self._sense_sources.get(sense, [])
            extensions = self._sense_extensions.get(sense, [])
            if not plain and not extensions:
                continue
            best = max((grant.range_feet for grant in plain), default=0)
            extra = sum(grant.range_feet for grant in extensions)
            ranges[sense] = best + extra
        return ranges

    def get_sense_range(self, sense: Sense) -> int:
        return self.ranges.get(sense, 0)

    def get_sense_sources(self, sense: Sense) -> list[SenseGrant]:
        """Plain grants, then extensions, each sorted by (source, range). An
        extension's source says it only adds to a sense already had."""
        plain = sorted(self._sense_sources.get(sense, []), key=_by_source)
        extensions = []
        for grant in sorted(self._sense_extensions.get(sense, []), key=_by_source):
            label = f"{grant.source} (+{grant.range_feet} ft. if already had)"
            extensions.append(SenseGrant(grant.range_feet, label))
        return plain + extensions
