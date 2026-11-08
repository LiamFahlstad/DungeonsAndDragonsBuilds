"""Spells written as classes (CharacterContent/Spells/SpellFactory/ClassSpell.py,
CharacterContent/Spells/SpellClasses), which SpellFactory uses instead of a
spell's JSON record, and the converter that writes them from the JSON
(CharacterContent/Spells/SpellClassConverter.py).

What a class must say comes from its JSON record (the converter's own check)
and from the rules (tests/test_spell_combat_effects.py,
tests/test_spell_improved_descriptions.py); these tests cover the plumbing:
the class wins, it's the spell's one source, and the converter writes
Python that means what the JSON meant.
"""

import json

import pytest

from CharacterContent.Spells import SpellClassConverter as converter
from CharacterContent.Spells.SpellClasses import MODULES, SPELL_CLASSES
from CharacterContent.Spells.SpellFactory import (
    ClassSpell,
    DataSpell,
    SpellFactory,
    SpellRules,
)
from CharacterContent.Spells.SpellFactory.Enums import Component, School
from Core.Definitions import Ability, CharacterClass, Condition, DamageType
from Model.Content.CombatEffect import (
    CombatCondition,
    CombatDamage,
    CombatEffect,
    CombatHitPoints,
    CombatInstances,
)
from Model.Content.Feature import FeatureTarget
from Model.Content.FeatureText import Facts, Option, Paragraph, Table

CLASS_NAMES = sorted(SPELL_CLASSES)


def _json(path: str) -> dict:
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


# ---------------------------------------------------------------------------
# The factory


def test_there_are_spell_classes():
    assert "Fireball" in SPELL_CLASSES


@pytest.mark.parametrize("name", CLASS_NAMES)
def test_the_factory_makes_its_class(name):
    spell = SpellFactory.create(name, Ability.WISDOM, "A ruling", "Chosen spell")
    assert type(spell) is SPELL_CLASSES[name]
    assert isinstance(spell, ClassSpell)
    assert spell.name == name
    # What the grant says rides on the spell as on a JSON one.
    assert spell.spell_casting_ability is Ability.WISDOM
    assert (spell.additional_ruling, spell.grant_source) == (
        "A ruling",
        "Chosen spell",
    )


def test_a_spell_without_a_class_comes_from_its_record():
    name = next(n for n in SpellFactory.spell_names() if n not in SPELL_CLASSES)
    assert type(SpellFactory.create(name)) is DataSpell


def test_every_spell_is_listed_once():
    names = SpellFactory.spell_names()
    assert len(names) == len(set(names))
    assert set(CLASS_NAMES) <= set(names)
    spells = {spell.name: spell for spell in SpellFactory.all_spells()}
    assert all(type(spells[name]) is SPELL_CLASSES[name] for name in CLASS_NAMES)


@pytest.mark.parametrize("name", CLASS_NAMES)
def test_a_class_is_its_spells_one_source(name):
    """The converter took the spell out of its source's companion files: an
    entry left there would never be read, and would drift from the class."""
    path = next(
        (p for p in SpellFactory.json_paths if name in _json(p)),
        None,
    )
    if path is None:
        return  # a spell only a class has
    for companion in converter.companion_paths(path):
        assert name not in _json(str(companion)), f"{name} is in {companion.name}"


@pytest.mark.parametrize("name", CLASS_NAMES)
def test_a_class_is_in_the_module_of_its_level(name):
    spell_class = SPELL_CLASSES[name]
    module = spell_class.__module__.rsplit(".", 1)[-1]
    assert module == converter.module_name(spell_class.rules.level)
    assert spell_class.__name__ == converter.class_name(name)


def test_every_module_lists_its_classes():
    for module in MODULES:
        defined = {
            value
            for value in vars(module).values()
            if isinstance(value, type)
            and issubclass(value, ClassSpell)
            and value is not ClassSpell
            and value.__module__ == module.__name__
        }
        assert defined == set(module.SPELLS), module.__name__


def test_rules_need_a_name_and_a_level():
    with pytest.raises(ValueError):
        _rules(name=" ")
    with pytest.raises(ValueError):
        _rules(name="Big Bang", level=10)


def _rules(**changes) -> SpellRules:
    values = dict(
        name="Test Spell",
        level=1,
        school=School.EVOCATION,
        classes=(CharacterClass.WIZARD,),
        casting_time="Action",
        range="Self",
        components=(Component.VERBAL,),
        duration="Instantaneous",
        source="Homebrew",
        description="",
    )
    values.update(changes)
    return SpellRules(**values)  # type: ignore[arg-type]


class _Test(ClassSpell):
    rules = _rules(
        components=(Component.VERBAL, Component.SOMATIC, Component.MATERIAL),
        material="a pinch of salt",
        classes=(CharacterClass.CLERIC, CharacterClass.WIZARD),
    )


def test_the_enums_read_as_the_cards_text():
    spell = _Test()
    assert spell.components == "V, S, M (a pinch of salt)"
    assert (spell.has_verbal, spell.has_somatic, spell.has_material) == (
        True,
        True,
        True,
    )
    assert spell.material_description == "a pinch of salt"
    assert (spell.school, spell.school_enum) == ("Evocation", School.EVOCATION)
    assert spell.classes == ["Cleric", "Wizard"]
    assert all(type(name) is str for name in spell.classes)


@pytest.mark.parametrize(
    "components, material",
    [
        ((Component.SOMATIC, Component.VERBAL), ""),  # not in card order
        ((Component.VERBAL, Component.VERBAL), ""),
        ((Component.VERBAL,), "a pinch of salt"),  # a material without an M
    ],
)
def test_components_are_v_s_m_once_each(components, material):
    with pytest.raises(ValueError):
        _rules(components=components, material=material)


def test_a_rules_condition_is_kept_as_its_name():
    """CombatCondition(Condition.PRONE) is CombatCondition("Prone"): the
    dialog and the logs see text, whichever way the class wrote it."""
    prone = CombatCondition(Condition.PRONE)
    assert prone == CombatCondition("Prone")
    assert type(prone.name) is str


# ---------------------------------------------------------------------------
# The converter writes Python that means what the JSON meant


@pytest.mark.parametrize(
    "value",
    [
        CombatEffect(
            name="Test: one",
            roll="save",
            save_ability=Ability.DEXTERITY,
            half_on_success=True,
            repeat_save=True,
            damage=(
                CombatDamage("8d6", DamageType.FIRE, upcast="1d6"),
                CombatDamage("3d8", None, (DamageType.ACID, DamageType.COLD)),
                CombatDamage(
                    "1d8",
                    DamageType.NECROTIC,
                    cantrip=((5, "2d8"), (11, "3d8"), (17, "4d8")),
                    when="the target is hurt",
                ),
            ),
            conditions=(
                CombatCondition("Prone"),
                CombatCondition("Test", until=("end", "source")),
            ),
            instances=CombatInstances(3, upcast=1, noun="ray"),
            spends_use=False,
            notes=("It's a note.", 'With "quotes".'),
        ),
        CombatEffect(healing=CombatHitPoints("2d8", upcast="2d8", add_modifier=True)),
        [
            Paragraph("Text with a\nline break."),
            Facts((("Flavor", "It's it."), ("Save", "Dexterity"))),
            Table(("A", "B"), (("1", "2"),)),
            Option("Using a Higher-Level Spell Slot", (Facts((("Damage", "+1d6"),)),)),
            Option("Empty"),
        ],
        FeatureTarget.AREA,
        "One line\nanother line\n",
        _Test.rules,
    ],
)
def test_written_source_reads_back_as_the_same_value(value):
    names = {
        "Ability": Ability,
        "CharacterClass": CharacterClass,
        "Component": Component,
        "Condition": Condition,
        "School": School,
        "SpellRules": SpellRules,
        "DamageType": DamageType,
        "CombatCondition": CombatCondition,
        "CombatDamage": CombatDamage,
        "CombatEffect": CombatEffect,
        "CombatHitPoints": CombatHitPoints,
        "CombatInstances": CombatInstances,
        "FeatureTarget": FeatureTarget,
        "Facts": Facts,
        "Option": Option,
        "Paragraph": Paragraph,
        "Table": Table,
    }
    assert eval(converter.source_of(value), names) == value


def test_written_source_uses_enums_where_there_are_some():
    assert converter.source_of(CombatCondition("Prone")) == (
        "CombatCondition(Condition.PRONE)"
    )
    assert converter.source_of(CombatCondition("Bless")) == "CombatCondition('Bless')"
    rules = converter.source_of(_Test.rules)
    assert "school=School.EVOCATION" in rules
    assert "classes=(CharacterClass.CLERIC, CharacterClass.WIZARD)" in rules
    # The material is written beside its component, not after the text.
    assert rules.index("material=") == rules.index("components=") + len(
        "components=(Component.VERBAL, Component.SOMATIC, Component.MATERIAL), "
    )


def _record(**changes) -> DataSpell:
    record = dict(SpellFactory._load_json()["Fireball"])
    record.update(changes)
    return DataSpell(record)


@pytest.mark.parametrize(
    "changes",
    [
        {"school": "Evocation (Dunamancy)"},
        {"classes": ["Wizard (Dunamancy)"]},
        {"components": "V,S"},
        {"components": "V, S, M(a diamond)"},
        {"components": None},
    ],
)
def test_a_spell_the_enums_cant_say_is_left_as_json(changes):
    with pytest.raises(converter.CannotConvert):
        converter.class_source(_record(**changes))


@pytest.mark.parametrize(
    "spell, name",
    [
        ("Fireball", "Fireball"),
        ("Tasha's Hideous Laughter", "TashasHideousLaughter"),
        ("Green-Flame Blade", "GreenFlameBlade"),
        ("Melf’s Acid Arrow", "MelfsAcidArrow"),
    ],
)
def test_class_names(spell, name):
    assert converter.class_name(spell) == name


def test_a_converted_class_gives_what_its_json_gave():
    """Fireball as a class against Fireball's JSON with its companions put
    back: the converter's own check, run on a real spell."""
    record = dict(SpellFactory._load_json()["Fireball"])
    made = SPELL_CLASSES["Fireball"]()
    blocks, effects = made.improved_description, made.combat_effects()
    assert blocks is not None and effects is not None
    record.update(
        usage_tags=made.usage_tags,
        target=made.target.value if made.target else None,
        improved_description=[_block_json(b) for b in blocks],
        combat_effects=[e.to_dict() for e in effects],
    )
    assert converter.differences(DataSpell(record), made) == []


def _block_json(block) -> dict:
    if isinstance(block, Facts):
        return {"facts": [list(row) for row in block.rows]}
    if isinstance(block, Table):
        return {
            "table": {
                "columns": list(block.columns),
                "rows": [list(r) for r in block.rows],
            }
        }
    if isinstance(block, Option):
        return {
            "option": {
                "name": block.name,
                "blocks": [_block_json(b) for b in block.blocks],
            }
        }
    return {"paragraph": block.text}


def test_removing_an_entry_keeps_the_rest_of_the_file_as_it_is():
    text = '{\n  "A": [\n    {"x": 1}\n  ],\n  "B": {"y": [1,\n    2]},\n  "C": []\n}\n'
    assert (
        converter.remove_entry(text, "B")
        == '{\n  "A": [\n    {"x": 1}\n  ],\n  "C": []\n}\n'
    )
    assert (
        converter.remove_entry(text, "C")
        == '{\n  "A": [\n    {"x": 1}\n  ],\n  "B": {"y": [1,\n    2]}\n}\n'
    )
    assert converter.remove_entry(text, "Z") == text


def test_adding_to_a_module_keeps_what_is_there(tmp_path):
    path = tmp_path / "Level1.py"
    path.write_text(
        '"""Doc."""\n\nfrom Model.Content.Summons import SummonSpec\n'
        "from CharacterContent.Spells.SpellFactory.ClassSpell import ClassSpell\n\n\n"
        "class Old(ClassSpell):\n    pass  # edited by hand\n\n\nSPELLS = [Old]\n",
        encoding="utf-8",
    )
    text = converter.add_to_module(
        path, 1, {"New": "class New(ClassSpell):\n    rules = SpellRules()\n"}
    )
    assert "pass  # edited by hand" in text
    assert "from Model.Content.Summons import SummonSpec" in text
    assert "SpellRules" in text.split("class Old")[0]  # imported now
    assert text.rstrip().endswith("SPELLS = [New, Old]")
    with pytest.raises(ValueError, match="already has"):
        converter.add_to_module(path, 1, {"Old": "class Old(ClassSpell):\n    pass\n"})
