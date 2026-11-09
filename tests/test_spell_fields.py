"""The spell card's four top lines as dataclasses
(CharacterContent/Spells/SpellFactory/SpellFields.py): what each source
wording means, the 2024 wording each writes back, and that every scraped
record reads."""

import json

import pytest

from CharacterContent.Spells.SpellFactory import DataSpell, SpellFactory
from CharacterContent.Spells.SpellFactory.Enums import (
    AreaShape,
    CastingTimeType,
    DurationType,
    RangeType,
)
from CharacterContent.Spells.SpellFactory.SpellFields import (
    Area,
    CastingTime,
    Components,
    Duration,
    Range,
)

FIELDS = {
    "casting_time": CastingTime,
    "range": Range,
    "components": Components,
    "duration": Duration,
}


@pytest.mark.parametrize("path", SpellFactory.json_paths)
def test_every_record_reads_and_writes_back(path):
    """Every scraped wording reads, and the 2024 wording it writes reads back
    as the same value. A new wording a scrape brings in fails here, not on
    a character sheet."""
    with open(path, encoding="utf-8") as f:
        records = json.load(f)
    for name, record in records.items():
        for key, field_type in FIELDS.items():
            value = field_type.from_text(record.get(key) or "")
            assert field_type.from_text(value.text) == value, (name, key)


# ---------------------------------------------------------------------------
# Casting time


@pytest.mark.parametrize(
    "text, value, card",
    [
        ("Action", CastingTime(CastingTimeType.ACTION), "Action"),
        ("1 action", CastingTime(CastingTimeType.ACTION), "Action"),
        ("1 Bonus Action", CastingTime(CastingTimeType.BONUS_ACTION), "Bonus Action"),
        ("1 minute", CastingTime(CastingTimeType.MINUTE, 1), "1 minute"),
        ("1 Hour", CastingTime(CastingTimeType.HOUR, 1), "1 hour"),
        ("24 hours", CastingTime(CastingTimeType.HOUR, 24), "24 hours"),
        (
            "10 minutes or Ritual",
            CastingTime(CastingTimeType.MINUTE, 10, ritual=True),
            "10 minutes or Ritual",
        ),
        (
            "Reaction, which you take in response to taking damage",
            CastingTime(
                CastingTimeType.REACTION,
                trigger="which you take in response to taking damage",
            ),
            "Reaction, which you take in response to taking damage",
        ),
        (
            "1 reaction, which you take when you or a creature within 60 feet of you falls",
            CastingTime(
                CastingTimeType.REACTION,
                trigger="which you take when you or a creature within 60 feet of you falls",
            ),
            "Reaction, which you take when you or a creature within 60 feet of you falls",
        ),
        (
            "1 action or 8 hours",
            CastingTime(
                CastingTimeType.ACTION,
                alternative=CastingTime(CastingTimeType.HOUR, 8),
            ),
            "Action or 8 hours",
        ),
        (
            "Action (Overgrowth) or 8 hours (Enrichment)",
            CastingTime(
                CastingTimeType.ACTION,
                note="Overgrowth",
                alternative=CastingTime(CastingTimeType.HOUR, 8, note="Enrichment"),
            ),
            "Action (Overgrowth) or 8 hours (Enrichment)",
        ),
    ],
)
def test_casting_times(text, value, card):
    assert CastingTime.from_text(text) == value
    assert value.text == card


@pytest.mark.parametrize("text", ["Two actions", "2 actions", "minute", "Ritual"])
def test_unreadable_casting_times(text):
    with pytest.raises(ValueError):
        CastingTime.from_text(text)


@pytest.mark.parametrize(
    "make",
    [
        lambda: CastingTime(CastingTimeType.ACTION, 2),  # an Action has no amount
        lambda: CastingTime(CastingTimeType.MINUTE),  # a minute needs one
        lambda: CastingTime(
            CastingTimeType.REACTION,
            trigger="which you take when hit",
            alternative=CastingTime(CastingTimeType.ACTION),
        ),
        lambda: CastingTime(
            CastingTimeType.ACTION,
            alternative=CastingTime(CastingTimeType.MINUTE, 1, ritual=True),
        ),
        lambda: CastingTime(
            CastingTimeType.REACTION, trigger="which you take when hit", ritual=True
        ),
    ],
)
def test_impossible_casting_times(make):
    with pytest.raises(ValueError):
        make()


# ---------------------------------------------------------------------------
# Range


@pytest.mark.parametrize(
    "text, value, feet, card",
    [
        ("Self", Range(RangeType.SELF), None, "Self"),
        ("Touch", Range(RangeType.TOUCH), None, "Touch"),
        ("Sight", Range(RangeType.SIGHT), None, "Sight"),
        ("150 feet", Range(RangeType.FOOT, 150), 150, "150 feet"),
        ("60ft", Range(RangeType.FOOT, 60), 60, "60 feet"),
        ("30 Feet", Range(RangeType.FOOT, 30), 30, "30 feet"),
        ("120 feet.", Range(RangeType.FOOT, 120), 120, "120 feet"),
        ("1,000 feet", Range(RangeType.FOOT, 1000), 1000, "1,000 feet"),
        ("1 mile", Range(RangeType.MILE, 1), 5280, "1 mile"),
        ("500 miles", Range(RangeType.MILE, 500), 500 * 5280, "500 miles"),
        (
            "Self (15-foot cone)",
            Range(RangeType.SELF, area=Area(15, AreaShape.CONE)),
            None,
            "Self (15-foot cone)",
        ),
        (
            "Self (10-foot-radius sphere)",
            Range(RangeType.SELF, area=Area(10, AreaShape.SPHERE)),
            None,
            "Self (10-foot-radius sphere)",
        ),
        (
            "Self (15-foot-radius)",
            Range(RangeType.SELF, area=Area(15, AreaShape.RADIUS)),
            None,
            "Self (15-foot radius)",
        ),
        (
            "Self (5-mile radius)",
            Range(RangeType.SELF, area=Area(5, AreaShape.RADIUS, miles=True)),
            None,
            "Self (5-mile radius)",
        ),
    ],
)
def test_ranges(text, value, feet, card):
    assert Range.from_text(text) == value
    assert value.feet == feet
    assert value.text == card


@pytest.mark.parametrize(
    "text", ["Within earshot", "feet", "Self (a cone)", "Self (15-foot blob)"]
)
def test_unreadable_ranges(text):
    with pytest.raises(ValueError):
        Range.from_text(text)


@pytest.mark.parametrize(
    "make",
    [
        lambda: Range(RangeType.FOOT),
        lambda: Range(RangeType.FOOT, 0),
        lambda: Range(RangeType.TOUCH, 5),
        lambda: Range(RangeType.FOOT, 60, area=Area(10, AreaShape.CUBE)),
    ],
)
def test_impossible_ranges(make):
    with pytest.raises(ValueError):
        make()


# ---------------------------------------------------------------------------
# Components


@pytest.mark.parametrize(
    "text, value, card",
    [
        ("V", Components(verbal=True), "V"),
        ("V, S", Components(verbal=True, somatic=True), "V, S"),
        ("V,S", Components(verbal=True, somatic=True), "V, S"),
        ("S, M", Components(somatic=True, material=""), "S, M"),
        (
            "V, S, M (a diamond worth 300+ GP, which the spell consumes)",
            Components(
                verbal=True,
                somatic=True,
                material="a diamond worth 300+ GP, which the spell consumes",
            ),
            "V, S, M (a diamond worth 300+ GP, which the spell consumes)",
        ),
        (
            "Component: V, S, M (a miniature tiara)",
            Components(verbal=True, somatic=True, material="a miniature tiara"),
            "V, S, M (a miniature tiara)",
        ),
        ("M(a feather)", Components(material="a feather"), "M (a feather)"),
        ("", Components(), ""),
    ],
)
def test_components(text, value, card):
    assert Components.from_text(text) == value
    assert value.text == card


@pytest.mark.parametrize("text", ["S, V", "V, V", "V (salt)", "X", "V, M (salt"])
def test_unreadable_components(text):
    with pytest.raises(ValueError):
        Components.from_text(text)


# ---------------------------------------------------------------------------
# Duration


@pytest.mark.parametrize(
    "text, value, seconds, card",
    [
        ("Instantaneous", Duration(DurationType.INSTANTANEOUS), 0, "Instantaneous"),
        ("Instantanous", Duration(DurationType.INSTANTANEOUS), 0, "Instantaneous"),
        ("1 round", Duration(DurationType.ROUND, 1), 6, "1 round"),
        ("24 Hours", Duration(DurationType.HOUR, 24), 86400, "24 hours"),
        ("10 days", Duration(DurationType.DAY, 10), 864000, "10 days"),
        (
            "Concentration, up to 1 minute",
            Duration(DurationType.MINUTE, 1, concentration=True),
            60,
            "Concentration, up to 1 minute",
        ),
        (
            "Concentration up to 10 minutes",
            Duration(DurationType.MINUTE, 10, concentration=True),
            600,
            "Concentration, up to 10 minutes",
        ),
        (
            "Up to 8 hours",
            Duration(DurationType.HOUR, 8, up_to=True),
            8 * 3600,
            "Up to 8 hours",
        ),
        (
            "Until dispelled",
            Duration(DurationType.UNTIL_DISPELLED),
            None,
            "Until dispelled",
        ),
        (
            "Until dispelled or triggered",
            Duration(DurationType.UNTIL_DISPELLED_OR_TRIGGERED),
            None,
            "Until dispelled or triggered",
        ),
        ("Special", Duration(DurationType.SPECIAL), None, "Special"),
        (
            "Instantaneous or 1 hour",
            Duration(
                DurationType.INSTANTANEOUS, alternative=Duration(DurationType.HOUR, 1)
            ),
            0,
            "Instantaneous or 1 hour",
        ),
        (
            "Concentration, up to 1 minute or until dispelled",
            Duration(
                DurationType.MINUTE,
                1,
                concentration=True,
                alternative=Duration(DurationType.UNTIL_DISPELLED),
            ),
            60,
            "Concentration, up to 1 minute or until dispelled",
        ),
        (
            "Instantaneous (see below)",
            Duration(DurationType.INSTANTANEOUS, note="see below"),
            0,
            "Instantaneous (see below)",
        ),
    ],
)
def test_durations(text, value, seconds, card):
    assert Duration.from_text(text) == value
    assert value.seconds == seconds
    assert value.text == card


@pytest.mark.parametrize(
    "text",
    [
        "Forever",
        "Concentration, Instantaneous",  # nothing to be "up to"
        "1 minute and 1 round",
        "1 minute or",
    ],
)
def test_unreadable_durations(text):
    with pytest.raises(ValueError):
        Duration.from_text(text)


@pytest.mark.parametrize(
    "make",
    [
        lambda: Duration(DurationType.MINUTE),
        lambda: Duration(DurationType.SPECIAL, 1),
        lambda: Duration(DurationType.MINUTE, 1, concentration=True, up_to=True),
    ],
)
def test_impossible_durations(make):
    with pytest.raises(ValueError):
        make()


# ---------------------------------------------------------------------------
# A JSON spell reads its record's text through them


def _record(**changes) -> DataSpell:
    record = dict(SpellFactory._load_json()["Fireball"])
    record.update(changes)
    return DataSpell(record)


def test_a_json_spell_keeps_its_records_wording_but_reads_its_meaning():
    spell = _record(
        casting_time="1 action or Ritual",
        range="90 ft",
        components="Component: V, S",
        duration="Concentration up to 10 minutes",
    )
    assert spell.casting_time == "1 action or Ritual"  # the card is the record's
    assert (spell.casting_time_type, spell.is_ritual) == (CastingTimeType.ACTION, True)
    assert spell.range_feet == 90
    assert (spell.has_verbal, spell.has_somatic, spell.has_material) == (
        True,
        True,
        False,
    )
    assert (spell.is_concentration, spell.duration_seconds) == (True, 600)


def test_a_record_without_components_has_none():
    spell = _record(components=None)
    assert spell.components_spec == Components()
    assert not (spell.has_verbal or spell.has_somatic or spell.has_material)
