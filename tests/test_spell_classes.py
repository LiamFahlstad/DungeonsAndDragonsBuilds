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

import dataclasses
import json
from pathlib import Path

import pytest

from CharacterContent.Spells import SpellClassConverter as converter
from CharacterContent.Spells.SpellClasses import MODULES, SPELL_CLASSES
from CharacterContent.Spells.SpellFactory import (
    ClassSpell,
    DataSpell,
    RecordStamp,
    SpellFactory,
    SpellRules,
)
from CharacterContent.Spells.SpellFactory.Enums import (
    CastingTimeType,
    DurationType,
    RangeType,
    School,
)
from CharacterContent.Spells.SpellFactory.SpellFields import (
    CastingTime,
    Components,
    Duration,
    Range,
)
from Core.Definitions import Ability, CharacterClass, Condition, DamageType
from Model.Content.CombatEffect import (
    CombatCondition,
    CombatDamage,
    CombatEffect,
    CombatHitPoints,
    CombatInstances,
    EffectRoll,
    TurnEdge,
    TurnOf,
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


def test_a_spell_without_a_class_comes_from_its_record(monkeypatch):
    """Every spell is a class now, so Fireball's is hidden: a spell scraped
    and not converted yet is its record."""
    others = {n: c for n, c in SPELL_CLASSES.items() if n != "Fireball"}
    monkeypatch.setattr(SpellFactory, "_spell_classes", staticmethod(lambda: others))
    assert type(SpellFactory.create("Fireball")) is DataSpell


def test_every_spell_is_listed_once():
    names = SpellFactory.spell_names()
    assert len(names) == len(set(names))
    assert set(CLASS_NAMES) <= set(names)
    spells = {spell.name: spell for spell in SpellFactory.all_spells()}
    assert all(type(spells[name]) is SPELL_CLASSES[name] for name in CLASS_NAMES)


def test_every_spell_the_sources_have_is_a_class():
    """S.4 converted them all: a record without a class is a spell scraped
    since, to convert (SpellClassConverter --name) before giving it tags,
    an improved description or combat effects."""
    assert [
        name for name in SpellFactory._load_json() if name not in SPELL_CLASSES
    ] == []


def test_no_companion_file_is_left():
    """A class is its spell's one source. SpellFactory no longer reads the
    old spells_<source>_extended/_improved/_combat_effects.json files, so one
    written now would be silently ignored."""
    spells_dir = Path("CharacterContent/Spells")
    left = [
        path.name
        for suffix in ("_extended", "_improved", "_combat_effects")
        for path in spells_dir.glob(f"spells_*{suffix}.json")
    ]
    assert left == []


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
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Homebrew",
        description="",
    )
    values.update(changes)
    return SpellRules(**values)  # type: ignore[arg-type]


class _Test(ClassSpell):
    rules = _rules(
        casting_time=CastingTime(CastingTimeType.MINUTE, 1, ritual=True),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True, somatic=True, material="a pinch of salt"),
        duration=Duration(DurationType.HOUR, 1, concentration=True),
        classes=(CharacterClass.CLERIC, CharacterClass.WIZARD),
    )


def test_the_enums_and_fields_read_as_the_cards_text():
    spell = _Test()
    assert spell.casting_time == "1 minute or Ritual"
    assert spell.range == "60 feet"
    assert spell.components == "V, S, M (a pinch of salt)"
    assert spell.duration == "Concentration, up to 1 hour"
    assert (spell.casting_time_type, spell.is_ritual) == (CastingTimeType.MINUTE, True)
    assert (spell.range_feet, spell.duration_seconds) == (60, 3600)
    assert spell.is_concentration
    assert (spell.has_verbal, spell.has_somatic, spell.has_material) == (
        True,
        True,
        True,
    )
    assert spell.material_description == "a pinch of salt"
    assert (spell.school, spell.school_enum) == ("Evocation", School.EVOCATION)
    assert spell.classes == ["Cleric", "Wizard"]
    assert all(type(name) is str for name in spell.classes)


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
            roll=EffectRoll.SAVE,
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
                CombatCondition("Test", until=(TurnEdge.END, TurnOf.SOURCE)),
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
        "CastingTime": CastingTime,
        "CastingTimeType": CastingTimeType,
        "Components": Components,
        "Duration": Duration,
        "DurationType": DurationType,
        "Range": Range,
        "RangeType": RangeType,
        "Condition": Condition,
        "School": School,
        "SpellRules": SpellRules,
        "DamageType": DamageType,
        "CombatCondition": CombatCondition,
        "CombatDamage": CombatDamage,
        "CombatEffect": CombatEffect,
        "CombatHitPoints": CombatHitPoints,
        "CombatInstances": CombatInstances,
        "EffectRoll": EffectRoll,
        "TurnEdge": TurnEdge,
        "TurnOf": TurnOf,
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
    # A spell's JSON has its roll and turn as text; the class names them.
    effect = converter.source_of(
        CombatEffect.from_dict(
            {
                "roll": "attack",
                "conditions": [{"name": "Prone", "until": ["end", "target"]}],
            }
        )
    )
    assert "roll=EffectRoll.ATTACK" in effect
    assert "until=(TurnEdge.END, TurnOf.TARGET)" in effect
    rules = converter.source_of(_Test.rules)
    assert "school=School.EVOCATION" in rules
    assert "classes=(CharacterClass.CLERIC, CharacterClass.WIZARD)" in rules
    assert "casting_time=CastingTime(CastingTimeType.MINUTE, 1, ritual=True)" in rules
    assert "range=Range(RangeType.FOOT, 60)" in rules
    assert (
        "components=Components(verbal=True, somatic=True, material='a pinch of salt')"
        in rules
    )
    assert "duration=Duration(DurationType.HOUR, 1, concentration=True)" in rules


def _record(**changes) -> DataSpell:
    record = dict(SpellFactory._load_json()["Fireball"])
    record.update(changes)
    return DataSpell(record)


@pytest.mark.parametrize(
    "changes",
    [
        {"school": "Evocation (Dunamancy) (Chronurgy)"},
        {"school": "Evocation (Dunamancy)", "classes": ["Wizard (Chronurgy)"]},
        {"classes": ["Wizard (Chronurgy)", "Sorcerer (Graviturgy)"]},
        {"components": None},
        {"casting_time": "Two actions"},
        {"range": "Within earshot"},
        {"duration": "Until the stars are right"},
    ],
)
def test_a_spell_the_enums_cant_say_is_left_as_json(changes):
    with pytest.raises(converter.CannotConvert):
        converter.class_source(_record(**changes))


@pytest.mark.parametrize(
    "changes, school, note, card",
    [
        (
            {"school": "Evocation (Dunamancy:Graviturgy)", "classes": ["Wizard"]},
            School.EVOCATION,
            "Dunamancy:Graviturgy",
            "Evocation (Dunamancy:Graviturgy)",
        ),
        (
            {
                "school": "Transmutation (Dunamancy:Graviturgy)",
                "classes": ["Wizard (Graviturgy)"],
            },
            School.TRANSMUTATION,
            "Dunamancy:Graviturgy",
            "Transmutation (Dunamancy:Graviturgy)",
        ),
        # The note only on the class (Sapping Sting): the school takes it.
        (
            {"school": "Necromancy", "classes": ["Wizard (Dunamancy)"]},
            School.NECROMANCY,
            "Dunamancy",
            "Necromancy (Dunamancy)",
        ),
    ],
)
def test_a_school_or_class_note_is_the_school_note(changes, school, note, card):
    """Q15 of the combat-effects plan: Wildemount's Dunamancy is a note on
    the school, and "Wizard (Dunamancy)" is the Wizard class."""
    json_spell = _record(**changes)
    source = converter.class_source(json_spell)
    assert f"school_note={note!r}" in source
    class_spell = _class_from_source(source)()
    assert class_spell.rules.school is school
    assert class_spell.rules.classes == (CharacterClass.WIZARD,)
    assert class_spell.school == card
    assert class_spell.school_enum is school
    assert converter.differences(json_spell, class_spell) == []


def test_a_school_note_is_the_text_inside_the_brackets():
    rules = SPELL_CLASSES["Fireball"].rules
    with pytest.raises(ValueError, match="school_note"):
        dataclasses.replace(rules, school_note="(Dunamancy)")


@pytest.mark.parametrize(
    "changes, school",
    [
        # The 2014 source's key, with a casting time that doesn't say so (DI-065).
        ({"ritual": True}, "Evocation"),
        # Wristpocket's "(Ritual)" in the school.
        (
            {"school": "Conjuration (Ritual) (Dunamancy)", "level": 2},
            "Conjuration (Dunamancy)",
        ),
    ],
)
def test_a_ritual_only_the_record_says_is_a_ritual(changes, school):
    json_spell = _record(casting_time="1 action", **changes)
    assert json_spell.is_ritual
    class_spell = _class_from_source(converter.class_source(json_spell))()
    assert class_spell.rules.casting_time == CastingTime(
        CastingTimeType.ACTION, ritual=True
    )
    assert class_spell.casting_time == "Action or Ritual"
    assert class_spell.school == school
    assert converter.differences(json_spell, class_spell) == []


def test_a_record_without_the_ritual_key_is_no_ritual():
    assert not _record(casting_time="1 action", ritual=False).is_ritual


def test_a_class_writes_the_card_lines_in_the_2024_wording():
    """The converter reads the record's wording and the class writes the
    2024 card's; a scraped slip ("V,S") is no reason to stay JSON."""
    source = converter.class_source(
        _record(casting_time="1 action", components="V,S", range="150 ft")
    )
    assert "casting_time=CastingTime(CastingTimeType.ACTION)" in source
    assert "range=Range(RangeType.FOOT, 150)" in source
    assert "components=Components(verbal=True, somatic=True)" in source


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


@pytest.mark.parametrize(
    "range_text, differs", [("150 Feet", False), ("150ft", False), ("120 feet", True)]
)
def test_differences_compare_what_the_card_lines_mean(range_text, differs):
    """Another wording of the same range is no difference; another range is."""
    made = SPELL_CLASSES["Fireball"]()
    record = dict(SpellFactory._load_json()["Fireball"], range=range_text)
    found = converter.differences(DataSpell(record), made)
    assert any(d.startswith("range_spec") for d in found) is differs


def test_a_converted_class_gives_what_its_json_gave():
    """Fireball as a class against Fireball's record: the converter's own
    check, run on a real spell. The record has only the rules, so the class
    differs from it only in what was written in the class since."""
    record = DataSpell(SpellFactory._load_json()["Fireball"])
    made = SPELL_CLASSES["Fireball"]()
    found = converter.differences(record, made, made.combat_effects())
    assert [d for d in found if not d.startswith(converter._NOT_RULES)] == []
    assert {d.split(":")[0] for d in found} == {
        "usage_tags",
        "target",
        "improved_description",
    }


def test_adding_to_a_module_keeps_what_is_there(tmp_path):
    path = tmp_path / "Level1.py"
    path.write_text(
        '"""Doc."""\n\nfrom Model.Content.Summons import SummonSpec\n'
        "from CharacterContent.Spells.SpellFactory.ClassSpell import ClassSpell\n\n\n"
        "class Old(ClassSpell):\n    pass  # edited by hand\n\n\nSPELLS = [Old]\n",
        encoding="utf-8",
    )
    text = converter.add_to_module(
        path,
        1,
        {
            "New": "class New(ClassSpell):\n"
            "    rules = SpellRules(description='Range: Self. Duration: Special.')\n"
        },
    )
    # A word in a string is no name: a description saying "Range" imports nothing.
    assert "SpellFields" not in text
    assert "pass  # edited by hand" in text
    assert "from Model.Content.Summons import SummonSpec" in text
    assert "SpellRules" in text.split("class Old")[0]  # imported now
    assert text.rstrip().endswith("SPELLS = [New, Old]")
    with pytest.raises(ValueError, match="already has"):
        converter.add_to_module(path, 1, {"Old": "class Old(ClassSpell):\n    pass\n"})


# ---------------------------------------------------------------------------
# Writing combat effects into a class (the spell-mechanics skill's `add`)

_EFFECTS = [
    CombatEffect(
        roll=EffectRoll.SAVE,
        save_ability=Ability.CONSTITUTION,
        damage=(CombatDamage("2d6", DamageType.THUNDER, upcast="1d6"),),
        conditions=(CombatCondition(Condition.PRONE),),
    )
]


def _class_from_source(source: str) -> type:
    """The class `source` (one class, as class_source() writes it) defines,
    with every name the converter can import."""
    namespace: dict = {}
    for name, module in converter._IMPORTS.items():
        namespace[name] = getattr(__import__(module, fromlist=[name]), name)
    exec(source, namespace)
    return next(
        value
        for value in namespace.values()
        if isinstance(value, type)
        and issubclass(value, ClassSpell)
        and value is not ClassSpell
    )


def test_a_class_can_be_written_with_other_combat_effects():
    """convert() with effects: the class gives those, not the record's
    (here, none), and keeps everything else the record says."""
    spell = _record()
    assert spell.combat_effects() is None
    made = _class_from_source(converter.class_source(spell, _EFFECTS))()
    assert made.combat_effects() == _EFFECTS
    assert converter.differences(spell, made, _EFFECTS) == []
    # Checked against the record's effects instead, they differ.
    assert converter.differences(spell, made) == ["combat_effects differ"]


_MODULE = '''"""Doc."""

from CharacterContent.Spells.SpellFactory.ClassSpell import ClassSpell


class HasOne(ClassSpell):
    x = 1

    @staticmethod
    def combat_effects(character=None):
        # written by hand
        return []

    def summons(self):
        return []


class HasNone(ClassSpell):
    x = 2


SPELLS = [HasNone, HasOne]
'''


def test_a_classs_combat_effects_method_is_replaced_or_added():
    text = converter.with_effects_method(_MODULE, "HasOne", _EFFECTS)
    text = converter.with_effects_method(text, "HasNone", _EFFECTS)
    text = converter.module_with(text, {})
    # The old method went, decorator and comment included; the rest stayed.
    assert "written by hand" not in text and "@staticmethod" not in text
    assert "def summons(self):" in text
    assert text.count("def combat_effects(") == 2
    # What the new code names is imported now, and SPELLS is unchanged.
    assert "from Model.Content.CombatEffect import" in text
    assert text.rstrip().endswith("SPELLS = [HasNone, HasOne]")
    namespace: dict = {}
    exec(text, namespace)
    for name in ("HasOne", "HasNone"):
        assert namespace[name]().combat_effects() == _EFFECTS
    assert (namespace["HasOne"].x, namespace["HasNone"].x) == (1, 2)
    with pytest.raises(ValueError, match="no class"):
        converter.with_effects_method(_MODULE, "Missing", _EFFECTS)


@pytest.fixture
def classes_package(tmp_path, monkeypatch):
    """An empty stand-in for SpellClasses, so _write_checked can write and
    import modules without touching the real ones."""
    package = tmp_path / "spell_classes_stand_in"
    package.mkdir()
    # Like the real one, it imports its modules.
    (package / "__init__.py").write_text(
        "from . import Level1\n\nSPELL_CLASSES = {}\n", encoding="utf-8"
    )
    (package / "Level1.py").write_text("X = 1\n", encoding="utf-8")
    monkeypatch.syspath_prepend(str(tmp_path))
    monkeypatch.setattr(converter, "CLASSES_DIR", package)
    monkeypatch.setattr(converter, "PACKAGE", package.name)
    yield package
    converter._forget_classes()


@pytest.mark.parametrize(
    "new_text, problem",
    [
        ("X = 2\n", ["the check says no"]),  # the check fails
        ("X = (\n", None),  # it doesn't even parse
    ],
)
def test_written_classes_that_fail_their_check_are_put_back(
    classes_package, new_text, problem
):
    level1, level2 = classes_package / "Level1.py", classes_package / "Level2.py"
    problems, written = converter._write_checked(
        {level1: new_text, level2: "Y = 1\n"},
        lambda classes: ["the check says no"],
    )
    if problem is not None:
        assert problems == problem
    else:
        assert problems and "don't import" in problems[0]
    assert written == [level1, level2]
    assert level1.read_text(encoding="utf-8") == "X = 1\n"
    assert not level2.exists()


def test_written_classes_that_pass_their_check_are_kept(classes_package):
    level1 = classes_package / "Level1.py"
    seen = []
    problems, _ = converter._write_checked(
        {level1: "X=2\n"}, lambda classes: seen.append(classes) or []
    )
    assert problems == [] and seen == [{}]
    assert level1.read_text(encoding="utf-8") == "X = 2\n"  # Black ran


# ---------------------------------------------------------------------------
# Drift: a re-scrape that changes a converted spell's record


def test_no_class_has_drifted_from_its_record():
    """A class keeps the record it was converted from. When a re-scrape
    changes that record, merge what changed into the class by hand, then
    `python -m CharacterContent.Spells.SpellClassConverter --accept <spell>`
    (`--drift` shows what changed)."""
    assert converter.drifted() == []


def test_a_record_stamp_is_the_records_content_not_its_key_order():
    record = {"name": "X", "level": 1}
    assert RecordStamp.of("a.json", record) == RecordStamp.of(
        "a.json", {"level": 1, "name": "X"}
    )
    assert RecordStamp.of("a.json", record) != RecordStamp.of(
        "a.json", {"name": "X", "level": 2}
    )
    assert RecordStamp.of("a.json", record) != RecordStamp.of("b.json", record)


def test_a_converted_class_is_stamped_with_its_record():
    made = _class_from_source(converter.class_source(_record()))
    assert made.converted_from == converter.stamp_for("Fireball")
    assert made.converted_from.source == "spells_dnd2024.json"


@pytest.fixture
def rescraped_fireball(monkeypatch):
    """Fireball's 2024 record as a re-scrape that changed its range would
    leave it."""
    found = converter.scraped_record("Fireball")
    assert found is not None
    path, record = found
    changed = dict(converter._RAW_SOURCES[path])
    changed["Fireball"] = dict(record, range="120 feet")
    monkeypatch.setitem(converter._RAW_SOURCES, path, changed)


def test_a_changed_record_is_found_with_what_to_merge(rescraped_fireball):
    assert converter.drifted() == [
        ("Fireball", "its record in spells_dnd2024.json changed since it was converted")
    ]
    report = converter.drift_report("Fireball")
    assert len(report) == 2  # the range, and the range in feet it gives
    assert report[0].startswith("range_spec")
    assert any(d.startswith("range_feet") for d in report)


def test_a_stamp_is_replaced_or_added_after_the_rules():
    text = (
        "class A(ClassSpell):\n"
        "    rules = SpellRules(\n        name='A',\n    )\n"
        "    converted_from = RecordStamp('old.json', 'abc')\n"
        "\n    def summons(self):\n        return []\n"
        "\n\nclass B(ClassSpell):\n    rules = 1\n\n    x = 2\n"
    )
    stamp = RecordStamp("new.json", "def")
    text = converter.with_stamp(text, "A", stamp)
    text = converter.with_stamp(text, "B", stamp)
    assert "old.json" not in text
    assert text.count("converted_from = RecordStamp('new.json', 'def')") == 2
    # B's goes right after its rules, before the rest of the class.
    assert "    rules = 1\n    converted_from = RecordStamp(" in text
    assert "def summons(self):" in text
