"""Every part's merge rule is commutative (Notes/model-refactor-plan.md, Step 2).

Each test records the same small set of contributions into a fresh part in
every order (itertools.permutations) and expects every read to come back
identical, including the order of listed sources. The conflict rules (two
CasterTypes for one class, two body armors) must raise in every order.

These cover combinations no build exercises; the build-level checks are
tests/test_feature_apply_order.py and tests/test_order_invariance.py.
"""

import itertools
from typing import Any, Callable

import pytest

from CharacterContent.Items.Weapons import WeaponProficiency
from CharacterContent.ToolProficiencies.Proficiencies import SmithsTools, ThievesTools
from Core.Definitions import (
    Ability,
    ArmorType,
    CharacterClass,
    Condition,
    DamageType,
    DiceRollCondition,
    Language,
    Sense,
    Skill,
)
from Core.SpellcastingRules import CasterType
from Model.AbilityRequirements import AbilityRequirements
from Model.AbilityIncreases import AbilityIncreases
from Model.ArmorClass import ArmorClass, ArmorClassFormula
from Model.Bonuses import Bonuses
from Model.CarryingCapacity import CarryingCapacity
from Model.ClassLevels import ClassLevels
from Model.Defenses import Defenses
from Model.EquipmentTraining import EquipmentTraining
from Model.Initiative import Initiative
from Model.Languages import Languages
from Model.SavingThrows import SavingThrows
from Model.Senses import Senses
from Model.Skills import Skills
from Model.Speed import Speed
from Model.Spellcasting import Spellcasting
from Model.WeaponBonuses import WeaponBonus, WeaponBonuses
from Model.WornArmor import WornArmor
from tests._fake_view import FakeView
from Model.Records.SourcedValue import SourcedValue

# Formulas are resolved against a character; these ignore it.
VIEW: Any = object()

ADV = DiceRollCondition.ADVANTAGE
DIS = DiceRollCondition.DISADVANTAGE


def _same_in_every_order(
    make_part: Callable[[], Any],
    records: list[Callable[[Any], None]],
    read: Callable[[Any], Any],
) -> Any:
    results = []
    for ordered in itertools.permutations(records):
        part = make_part()
        for record in ordered:
            record(part)
        results.append(read(part))
    assert all(result == results[0] for result in results), results
    return results[0]


def _raises_in_every_order(make_part, records, match: str) -> None:
    for ordered in itertools.permutations(records):
        part = make_part()
        with pytest.raises(ValueError, match=match):
            for record in ordered:
                record(part)


def test_bonuses_sum_and_list_sources_sorted():
    result = _same_in_every_order(
        Bonuses,
        [
            lambda b: b.add(1, "Bless"),
            lambda b: b.add(2, "Archery"),
            lambda b: b.add_formula(lambda view: 3, "Wisdom"),
            lambda b: b.add_formula(lambda view: 1, "Charisma"),
        ],
        lambda b: (b.total(VIEW), b.sources(VIEW)),
    )
    expected_sources = [
        SourcedValue(2, "Archery"),
        SourcedValue(1, "Bless"),
        SourcedValue(1, "Charisma"),
        SourcedValue(3, "Wisdom"),
    ]
    assert result == (7, expected_sources)


class TestSkills:
    def test_proficiency_and_expertise(self):
        result = _same_in_every_order(
            Skills,
            [
                lambda s: s.add_skill_expertise(Skill.STEALTH),
                lambda s: s.add_skill_proficiency(Skill.STEALTH),
                lambda s: s.add_skill_proficiency(Skill.STEALTH),
                lambda s: s.add_skill_proficiency(Skill.ARCANA),
            ],
            lambda s: [(s.is_proficient(k), s.has_expertise(k)) for k in Skill],
        )
        assert result[list(Skill).index(Skill.STEALTH)] == (True, True)

    def test_bonuses(self):
        _same_in_every_order(
            Skills,
            [
                lambda s: s.add_skill_bonus(Skill.ARCANA, 1, "Item"),
                lambda s: s.add_skill_bonus(Skill.ARCANA, 2, "Feat"),
                lambda s: s.add_derived_bonus(Skill.ARCANA, lambda view: 3, "Order"),
            ],
            lambda s: (
                s.get_total_bonus(Skill.ARCANA, VIEW),
                s.get_all_bonus_sources(Skill.ARCANA, VIEW),
            ),
        )

    def test_roll_conditions(self):
        result = _same_in_every_order(
            Skills,
            [
                lambda s: s.set_roll_condition(Skill.STEALTH, ADV, "Cloak"),
                lambda s: s.set_roll_condition(Skill.STEALTH, DIS, "Armor"),
                lambda s: s.set_roll_condition(Skill.STEALTH, ADV, "Boots"),
                lambda s: s.set_roll_condition(Skill.PERCEPTION, ADV, "Keen"),
            ],
            lambda s: [
                (
                    s.roll_condition(k, FakeView()),
                    s.roll_condition_sources(k, FakeView()),
                    s.roll_condition_reasons(k, FakeView()),
                )
                for k in (Skill.STEALTH, Skill.PERCEPTION)
            ],
        )
        stealth, perception = result
        assert stealth[0] == DiceRollCondition.NEUTRAL
        assert stealth[1] == {ADV: ["Boots", "Cloak"], DIS: ["Armor"]}
        assert perception[2] == ["Keen"]

    def test_ability_overrides(self):
        result = _same_in_every_order(
            Skills,
            [
                lambda s: s.update_skill_to_ability(Skill.ARCANA, Ability.CHARISMA),
                lambda s: s.update_skill_to_ability(Skill.ARCANA, Ability.WISDOM),
                lambda s: s.update_skill_to_ability(Skill.ARCANA, Ability.WISDOM),
            ],
            lambda s: s.get_skill_abilities(Skill.ARCANA),
        )
        assert result == [Ability.WISDOM, Ability.CHARISMA]


def test_saving_throws():
    result = _same_in_every_order(
        SavingThrows,
        [
            lambda t: t.add_proficiency(Ability.DEXTERITY),
            lambda t: t.add_proficiency_or_alternative(
                Ability.DEXTERITY, [Ability.CONSTITUTION, Ability.WISDOM]
            ),
            lambda t: t.add_proficiency_or_alternative(
                Ability.CONSTITUTION, [Ability.WISDOM]
            ),
            lambda t: t.add_advantage(Ability.WISDOM),
            lambda t: t.add_bonus(Ability.WISDOM, 1),
        ],
        lambda t: [
            (t.is_proficient(a), t.is_advantaged(a), t.get_total_bonus(a, VIEW))
            for a in Ability
        ],
    )
    proficient = {a for a, (p, _adv, _bonus) in zip(Ability, result) if p}
    assert proficient == {Ability.DEXTERITY, Ability.CONSTITUTION, Ability.WISDOM}


def test_defenses():
    result = _same_in_every_order(
        Defenses,
        [
            lambda d: d.add_damage_resistance(DamageType.FIRE, "Tiefling"),
            lambda d: d.add_damage_resistance(DamageType.FIRE, "Armor"),
            lambda d: d.add_damage_resistance(DamageType.COLD, "Ring"),
            lambda d: d.add_damage_immunity(DamageType.POISON, "Feat"),
            lambda d: d.add_condition_immunity(Condition.CHARMED, "Fey"),
        ],
        lambda d: (
            list(d.damage_resistances.items()),
            list(d.damage_immunities.items()),
            list(d.condition_immunities.items()),
            d.get_damage_resistance_sources(DamageType.FIRE),
        ),
    )
    assert result[0] == [
        (DamageType.COLD, ["Ring"]),
        (DamageType.FIRE, ["Armor", "Tiefling"]),
    ]


def test_languages():
    result = _same_in_every_order(
        Languages,
        [
            lambda l: l.add(Language.ELVISH, "Species"),
            lambda l: l.add(Language.COMMON, "Species"),
            lambda l: l.add(Language.ELVISH, "Background"),
        ],
        lambda l: (list(l.known.items()), l.sources(Language.ELVISH)),
    )
    assert result[0] == [
        (Language.COMMON, ["Species"]),
        (Language.ELVISH, ["Background", "Species"]),
    ]


def test_senses():
    result = _same_in_every_order(
        Senses,
        [
            lambda s: s.add_sense(Sense.DARKVISION, 60, "Elf"),
            lambda s: s.add_sense(Sense.DARKVISION, 120, "Goggles"),
            lambda s: s.add_sense_or_extension(Sense.DARKVISION, 60, "Umbral Sight"),
            lambda s: s.add_sense(Sense.BLINDSIGHT, 10, "Fighting Style"),
        ],
        lambda s: (
            list(s.ranges.items()),
            s.get_sense_sources(Sense.DARKVISION),
        ),
    )
    assert result[0] == [(Sense.DARKVISION, 180), (Sense.BLINDSIGHT, 10)]


def test_carrying_capacity():
    result = _same_in_every_order(
        CarryingCapacity,
        [
            lambda c: c.add_bonus("Pack Mule", 2),
            lambda c: c.add_bonus("Bag of Holding", 5),
            lambda c: c.add_bonus("Backpack", 1),
        ],
        lambda c: (
            c.sources(FakeView({Ability.STRENGTH: 12})),
            c.total(FakeView({Ability.STRENGTH: 12})),
        ),
    )
    assert result[0][0] == SourcedValue(4, "Person")
    assert result[1] == 12


def test_weapon_bonuses():
    def every_weapon(weapon):
        return True

    _same_in_every_order(
        WeaponBonuses,
        [
            lambda w: w.add_attack_bonus(WeaponBonus(every_weapon, 2, "Archery")),
            lambda w: w.add_attack_bonus(WeaponBonus(every_weapon, 1, "Bracers")),
            lambda w: w.add_damage_bonus(WeaponBonus(every_weapon, 2, "Dueling")),
            lambda w: w.add_damage_bonus(WeaponBonus(every_weapon, 2, "Bracers")),
        ],
        lambda w: (w.attack_bonuses(None), w.damage_bonuses(None)),
    )


class TestEquipmentTraining:
    def test_set_union(self):
        result = _same_in_every_order(
            EquipmentTraining,
            [
                lambda e: e.add_weapon_proficiency(WeaponProficiency.MARTIAL),
                lambda e: e.add_armor_training(ArmorType.SHIELD),
                lambda e: e.add_tool_proficiency(SmithsTools()),
                lambda e: e.add_tool_proficiency(ThievesTools()),
            ],
            lambda e: (
                e.weapon_proficiencies,
                e.armor_training,
                [t.name for t in e.tool_proficiencies],
            ),
        )
        assert result[2] == sorted([SmithsTools().name, ThievesTools().name])

    def test_the_same_tool_from_two_sources_is_listed_once(self):
        # Thieves' Tools from both Rogue and the Criminal background.
        result = _same_in_every_order(
            EquipmentTraining,
            [
                lambda e: e.add_tool_proficiency(ThievesTools()),
                lambda e: e.add_tool_proficiency(ThievesTools()),
            ],
            lambda e: [t.name for t in e.tool_proficiencies],
        )
        assert result == [ThievesTools().name]


class TestSpellcasting:
    LEVELS = ClassLevels(
        base_class=CharacterClass.WIZARD,
        level_per_class={CharacterClass.WIZARD: 5, CharacterClass.WARLOCK: 3},
    )

    def test_casters_combine(self):
        _same_in_every_order(
            Spellcasting,
            [
                lambda s: s.register_caster(
                    CharacterClass.WIZARD, CasterType.FULL_CASTER
                ),
                lambda s: s.register_caster(
                    CharacterClass.WIZARD, CasterType.FULL_CASTER
                ),
                lambda s: s.register_caster(
                    CharacterClass.WARLOCK, CasterType.WARLOCK_CASTER
                ),
                lambda s: s.add_spell_save_dc_bonus(1),
            ],
            lambda s: (
                s.spell_slots(FakeView(class_levels=self.LEVELS)),
                s.pact_magic_slots(FakeView(class_levels=self.LEVELS)),
                s.difficulty_class(Ability.INTELLIGENCE, FakeView()),
            ),
        )

    def test_two_caster_types_for_one_class_raise(self):
        _raises_in_every_order(
            Spellcasting,
            [
                lambda s: s.register_caster(
                    CharacterClass.WIZARD, CasterType.FULL_CASTER
                ),
                lambda s: s.register_caster(
                    CharacterClass.WIZARD, CasterType.HALF_CASTER
                ),
            ],
            match="registered as both",
        )


class TestWornArmor:
    def test_armor_and_shield(self):
        result = _same_in_every_order(
            WornArmor,
            [
                lambda w: w.set_body_armor(ArmorType.HEAVY, "Plate"),
                lambda w: w.wield_shield(),
                lambda w: w.wield_shield(),
            ],
            lambda w: (w.body_armor_type, w.body_armor_name, w.shield_wielded),
        )
        assert result == (ArmorType.HEAVY, "Plate", True)

    def test_two_body_armors_raise(self):
        _raises_in_every_order(
            WornArmor,
            [
                lambda w: w.set_body_armor(ArmorType.HEAVY, "Plate"),
                lambda w: w.set_body_armor(ArmorType.LIGHT, "Leather"),
            ],
            match="multiple armors",
        )


def test_armor_class():
    scores = {Ability.DEXTERITY: 16, Ability.CONSTITUTION: 14, Ability.WISDOM: 14}
    result = _same_in_every_order(
        ArmorClass,
        [
            lambda a: a.add_armor_class_formula(
                ArmorClassFormula(
                    10,
                    frozenset({Ability.DEXTERITY, Ability.WISDOM}),
                    allows_shield=False,
                )
            ),
            lambda a: a.add_armor_class_formula(
                ArmorClassFormula(
                    10, frozenset({Ability.DEXTERITY, Ability.CONSTITUTION})
                )
            ),
            lambda a: a.add_bonus(1),
            lambda a: a.add_shield_bonus(2),
        ],
        lambda a: [
            a.total(
                FakeView(
                    scores,
                    is_wielding_shield=wielding,
                    has_shield_training=trained,
                )
            )
            for wielding in (False, True)
            for trained in (False, True)
        ],
    )
    # Unarmored Defense (10 + 3 + 2) without a Shield, 10 + DEX + CON with one.
    assert result == [16, 16, 16, 18]


def test_ability_score_increases():
    view = FakeView({Ability.STRENGTH: 15})
    result = _same_in_every_order(
        AbilityIncreases,
        [
            lambda s: s.add(Ability.STRENGTH, 2, max_score=20),
            lambda s: s.add(Ability.STRENGTH, 2, max_score=20),
            lambda s: s.add(Ability.STRENGTH, 4, max_score=25),
            lambda s: s.add(Ability.STRENGTH, 2),
        ],
        lambda s: (
            s.own_score(Ability.STRENGTH, view),
            s.score(Ability.STRENGTH, view),
        ),
    )
    # 15 +2 +2 (to 19, cap 20), then +4 to 23 (cap 25); +2 from an item on top.
    assert result == (23, 25)


def test_ability_requirements_report_the_same_failure():
    view = FakeView()
    messages = set()
    for ordered in itertools.permutations(
        [
            (Ability.STRENGTH, 15, "Plate"),
            (Ability.STRENGTH, 13, "Chain Mail"),
            (Ability.DEXTERITY, 13, "Feat"),
        ]
    ):
        requirements = AbilityRequirements()
        for ability, minimum, reason in ordered:
            requirements.add_ability_requirement(ability, minimum, reason)
        with pytest.raises(ValueError) as error:
            requirements.validate(view)
        messages.add(str(error.value))
    assert messages == {"Strength score must be at least 13 (Chain Mail)."}


def test_initiative():
    _same_in_every_order(
        Initiative,
        [
            lambda i: i.add_proficiency(),
            lambda i: i.add_roll_condition(ADV),
            lambda i: i.add_roll_condition(DIS),
            lambda i: i.add_bonus(2),
            lambda i: i.add_derived_bonus(lambda view: 3),
        ],
        lambda i: (i.total(FakeView()), i.roll_condition(FakeView())),
    )


def test_speed():
    result = _same_in_every_order(
        Speed,
        [
            lambda s: s.add_bonus(10),
            lambda s: s.add_derived_bonus(lambda view: 5),
        ],
        lambda s: s.total(FakeView(base_speed=30)),
    )
    assert result == 45
