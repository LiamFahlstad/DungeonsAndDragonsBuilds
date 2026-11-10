"""Golden rows of the combat UI's Custom Effect picker (effect_options.py):
every row of each campaign party member and of the homebrew monsters that
describe their abilities, and every spell with combat effects, cast by a
monster with a known DC and attack bonus.

A change to how a spell, feature or monster ability fills the form shows up
here as a field-by-field diff. Read it before regenerating with
UPDATE_SNAPSHOTS=1: a row that changed without meaning to is a bug
(Notes/combat-effects-plan.md, Q1).
"""

import re

import pytest

from CharacterContent.Spells.SpellFactory import SpellFactory
from Combat.CombatUIQt.effect_options import ALL_SPELLS, effect_options
from Combat.EncounterLogs import _plain
from Combat.Monsters.CR_0.monsters_homebrew import DwarfLifeCleric
from Combat.Monsters.CR_1.monsters_homebrew import HumanPaladinOfDevotion
from Combat.Monsters.CR_3.monsters_homebrew import MirelleTheGildedKnight
from Combat.Monsters.CR_5.monsters_homebrew import MiraPrincessOfTheLoop
from Combat.PlayerCombatant import combatant_from_character, combatant_from_stat_block
from Model.Content.CombatModifiers import modifier_to_dict
from Combat.Scenarios import CAMPAIGNS
from tests._combat_ui import check_golden
from tests._snapshot_helpers import SNAPSHOT_DIR

# One file per test: the tests run in parallel, and each rewrites its own.
GOLDEN_DIR = SNAPSHOT_DIR / "picker_rows"


def _check(key: str, rows: dict) -> None:
    name = re.sub(r"[^A-Za-z0-9]+", "_", key).strip("_")
    check_golden(GOLDEN_DIR / f"{name}.json", key, rows)


# What a row fills in and shows; tooltip (the rules text) and the monster
# action it spends are left out.
_FIELDS = (
    "row_name",
    "summary",
    "note",
    "roll",
    "ability",
    "dc",
    "bonus",
    "half_on_save",
    "repeat_save",
    "damage",
    "amount_kind",
    "upcast",
    "condition",
    "duration_seconds",
    "until",
    "slot_level",
    "spell_level",
    "action_cost",
    "concentration",
    "counts_uses",
    "feature_name",
    "spell_name",
    "is_unavailable",
    "is_curated",
)

MEMBERS = [
    (name, builder)
    for name, campaign in sorted(CAMPAIGNS.items())
    if campaign.config is not None
    for builder in campaign.config.party_spec.members
]
MONSTERS = [
    DwarfLifeCleric,
    HumanPaladinOfDevotion,
    MirelleTheGildedKnight,
    MiraPrincessOfTheLoop,
]
CASTER = {
    "name": "Caster",
    "actions": [
        {
            "name": "Spellcasting",
            "description": "It casts a spell (spell save DC 15, +7 to hit with spell attacks).",
        }
    ],
}


def _row(option) -> dict:
    row = {field: getattr(option, field) for field in _FIELDS}
    row["slot_level"] = repr(option.slot_level)  # a PactSlot isn't a plain level
    # Only the rows whose badges give modifiers (Bless, Shield of Faith) say
    # so, so the rows of all the others read as they did.
    if option.badge_modifiers:
        row["badge_modifiers"] = {
            badge: [modifier_to_dict(m) for m in modifiers]
            for badge, modifiers in option.badge_modifiers
        }
    return row


def _rows(char: dict, all_spells=()) -> dict:
    """Each row by category and name ("Features | Turn Undead"), so a row
    added or removed shows as just that in a diff; a second row of the same
    name gets " #2"."""
    rows: dict = {}
    for title, options in effect_options(char, all_spells=list(all_spells)):
        for option in options:
            key = f"{title} | {option.name}"
            number = 2
            while key in rows:
                key = f"{title} | {option.name} #{number}"
                number += 1
            rows[key] = _row(option)
    return rows


@pytest.mark.parametrize(
    "campaign, builder",
    MEMBERS,
    ids=[f"{campaign}-{builder.__name__}" for campaign, builder in MEMBERS],
)
def test_a_party_members_rows(campaign, builder):
    char = combatant_from_character(builder().build())
    _check(f"{campaign}/{builder.__name__}", _rows(char))


@pytest.mark.parametrize("monster", MONSTERS, ids=[m.__name__ for m in MONSTERS])
def test_a_monsters_rows(monster):
    char = _plain({"c": combatant_from_stat_block(monster())})["c"]
    _check(f"monster/{monster.__name__}", _rows(char))


def test_every_described_spell():
    described = sorted(
        (s for s in SpellFactory.all_spells() if s.combat_effects() is not None),
        key=lambda spell: (spell.level, spell.name),
    )
    rows = _rows(CASTER, described)
    # Alarm and the like aren't in All spells: nothing to apply.
    spells = {k: v for k, v in rows.items() if k.startswith(ALL_SPELLS)}
    _check("caster/described spells", spells)
