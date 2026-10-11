"""Every spell card says where the character got the spell
(Presentation/SpellCards.py spell_source_label): chosen at a class level,
granted by a subclass/species/feat, or the grant's own label."""

import pytest

from Presentation.SpellCards import spell_source_label
from tests._snapshot_helpers import BUILD_PARAMS, build


def _labels(name: str) -> dict[str, list[str]]:
    character = build(name)
    labels: dict[str, list[str]] = {}
    for grant in character.spells:
        labels.setdefault(getattr(grant.name, "value", grant.name), []).append(
            spell_source_label(grant, character)
        )
    return labels


def test_every_spell_has_a_source():
    missing = []
    for name in BUILD_PARAMS:
        character = build(name)
        for grant in character.spells:
            if not spell_source_label(grant, character):
                missing.append(f"{name}: {grant.name}")
    assert not missing, "\n".join(missing)


@pytest.mark.parametrize(
    "build_name, spell, label",
    [
        # A grant with its own label.
        ("Y2024_Druid_Moon_Maggie", "Cure Wounds", "Circle of the Moon Spells table (Circle of the Moon Druid Level 3)"),
        # Subclass spells name the subclass the way its feature cards do.
        ("Y2024ClericLightAmaraSunkindleCharacterBuilder", "Burning Hands", "Granted by Light Domain Cleric Level 3"),
        # A species trait.
        ("Y2014WizardChronurgyAurelioTimewardCharacterBuilder", "Mending", "Granted by Rock Gnome"),
    ],
)
def test_source_examples(build_name, spell, label):
    assert label in _labels(build_name)[spell]


def test_class_picks_are_marked_chosen():
    labels = _labels("Y2024ClericLightAmaraSunkindleCharacterBuilder")
    chosen = [l for ls in labels.values() for l in ls if l.startswith("Chosen at Cleric Level")]
    assert chosen
