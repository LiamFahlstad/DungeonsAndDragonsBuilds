"""A creature's stat block and its starting combat state: BasicCombatantData
(hit points, AC, conditions, ...) and ExtendedCombatantData (the full monster
stat block). Shared by the monster catalog (Combat/Monsters), companions and
wild shapes (CharacterContent) and the combat engine."""

from dataclasses import dataclass as dataclass_decorator
from enum import Enum
from typing import Callable, Optional

from attr import dataclass

from Core.Definitions import Ability, Condition, CreatureSize, DamageType, Skill
from Model.Creatures.MonsterAbilities import MonsterAbility


def _normalize_ability_keyed_dict(d: Optional[dict]) -> dict:
    """Allow `Ability` enum members as dict keys (e.g. `{Ability.STRENGTH: 10}`)
    alongside plain short-name strings (`{"STR": 10}`), collapsing both to
    short-name string keys — the form the rest of the combat pipeline expects."""
    if not d:
        return {}
    return {
        (key.short_name if isinstance(key, Ability) else key): value
        for key, value in d.items()
    }


class MonsterType(str, Enum):
    ABERRATION = "Aberration"
    BEAST = "Beast"
    CELESTIAL = "Celestial"
    CONSTRUCT = "Construct"
    DRAGON = "Dragon"
    ELEMENTAL = "Elemental"
    FEY = "Fey"
    FIEND = "Fiend"
    GIANT = "Giant"
    HUMANOID = "Humanoid"
    MONSTROSITY = "Monstrosity"
    OOZE = "Ooze"
    PLANT = "Plant"
    UNDEAD = "Undead"


class Alignment(str, Enum):
    LAWFUL_GOOD = "Lawful Good"
    NEUTRAL_GOOD = "Neutral Good"
    CHAOTIC_GOOD = "Chaotic Good"
    LAWFUL_NEUTRAL = "Lawful Neutral"
    NEUTRAL = "Neutral"
    CHAOTIC_NEUTRAL = "Chaotic Neutral"
    LAWFUL_EVIL = "Lawful Evil"
    NEUTRAL_EVIL = "Neutral Evil"
    CHAOTIC_EVIL = "Chaotic Evil"
    UNALIGNED = "Unaligned"
    ANY_ALIGNMENT = "Any Alignment"


class Visibility(str, Enum):
    LIGHTLY_OBSCURED = "Lightly Obscured"
    HEAVILY_OBSCURED = "Heavily Obscured"
    INVISIBLE = "Invisible"
    DARKNESS = "Darkness"
    HALF_COVER = "Half Cover"
    THREE_QUARTERS_COVER = "Three-Quarters Cover"
    TOTAL_COVER = "Total Cover"

    @staticmethod
    def list_all():
        return [vis.value for vis in Visibility]


@dataclass_decorator
class DamageTypeEntry:
    """One resistance/immunity/vulnerability entry from a monster's stat block,
    e.g. "Bludgeoning, Piercing, and Slashing from Nonmagical Attacks" becomes
    DamageTypeEntry(damage_types=[BLUDGEONING, PIERCING, SLASHING], note="from Nonmagical Attacks").
    """

    damage_types: list[DamageType]
    note: str = ""


@dataclass
class BasicCombatantData:
    combatant_type: str
    hp: int
    ac: int
    temp_hp: int
    conditions: list[Condition]
    spell_slots: Optional[dict[int, int]] = None
    ability_scores: Optional[dict[str, int]] = None
    saving_throws: Optional[dict[str, int]] = None
    max_hp: Optional[int] = None
    name: Optional[str] = None  # Optional custom name for the combatant
    create_name: Optional[str] = (
        None  # Instance name (display name), distinct from creature type
    )
    visibility_states: Optional[list[Visibility]] = None

    def __attrs_post_init__(self):
        if self.spell_slots is None:
            self.spell_slots = {}
        self.ability_scores = _normalize_ability_keyed_dict(self.ability_scores)
        self.saving_throws = _normalize_ability_keyed_dict(self.saving_throws)
        if self.max_hp is None:
            self.max_hp = self.hp
        if self.visibility_states is None:
            self.visibility_states = []

    def as_dict(self, character=None):
        return {
            "name": self.name if self.name is not None else self.combatant_type,
            "create_name": (
                self.create_name
                if self.create_name is not None
                else self.combatant_type
            ),
            "combatant_type": self.combatant_type,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "ac": self.ac,
            "temp_hp": self.temp_hp,
            "conditions": self.conditions,
            "visibility_states": (
                self.visibility_states if self.visibility_states is not None else []
            ),
            "spell_slots": self.spell_slots if self.spell_slots is not None else {},
            "Ability Scores": (
                self.ability_scores if self.ability_scores is not None else {}
            ),
            "Saving Throws": (
                self.saving_throws if self.saving_throws is not None else {}
            ),
        }

    def set_name(self, new_name: str):
        self.name = new_name

    def set_create_name(self, new_create_name: str):
        self.create_name = new_create_name


@dataclass
class ExtendedCombatantData(BasicCombatantData):
    """Extended combatant data with additional monster stat block information."""

    cr: str = ""
    monster_type: Optional[MonsterType] = None
    monster_type_note: str = (
        ""  # e.g. "Metallic" or "Swarm of Tiny" -- subtype/swarm qualifier alongside monster_type
    )
    alignment: Optional[Alignment] = None
    size: Optional[CreatureSize] = None
    ac_note: str = ""  # e.g. "natural armor"
    hp_formula: str = ""  # e.g. "8d10+8"
    speed_ground_ft: Optional[int] = None
    speed_fly_ft: Optional[int] = None
    speed_climb_ft: Optional[int] = None
    speed_special_rules: str = (
        ""  # e.g. "hover" or any speed text that doesn't fit the fields above
    )
    skills: Optional[dict[Skill, int]] = None
    damage_vulnerabilities: Optional[list[DamageTypeEntry]] = None
    damage_resistances: Optional[list[DamageTypeEntry]] = None
    damage_immunities: Optional[list[DamageTypeEntry]] = None
    condition_immunities: Optional[list[Condition]] = None
    senses: str = ""
    languages: str = ""
    description: str = ""  # freeform flavor text / notes about the monster
    traits: Optional[list[MonsterAbility]] = None  # special traits / passive abilities
    actions: Optional[list[MonsterAbility]] = None  # standard action entries
    bonus_actions: Optional[list[MonsterAbility]] = (
        None  # bonus actions (some monsters)
    )
    reactions: Optional[list[MonsterAbility]] = None  # reactions
    legendary_actions: Optional[list[MonsterAbility]] = None  # legendary actions
    legendary_resistances: int = 0  # count of legendary resistances
    lair_actions: Optional[list[MonsterAbility]] = None  # lair actions
    mythic_actions: Optional[list[MonsterAbility]] = (
        None  # mythic actions (some monsters)
    )

    def __attrs_post_init__(self):
        super().__attrs_post_init__()
        if self.skills is None:
            self.skills = {}
        if self.damage_vulnerabilities is None:
            self.damage_vulnerabilities = []
        if self.damage_resistances is None:
            self.damage_resistances = []
        if self.damage_immunities is None:
            self.damage_immunities = []
        if self.condition_immunities is None:
            self.condition_immunities = []
        for field in (
            "traits",
            "actions",
            "bonus_actions",
            "reactions",
            "legendary_actions",
            "lair_actions",
            "mythic_actions",
        ):
            if getattr(self, field) is None:
                setattr(self, field, [])
        if self.legendary_resistances is None:
            self.legendary_resistances = 0


# A stat block class from the monster catalog, built with no arguments
# (BrownBear()) - what a Druid's known Wild Shape forms are.
CreatureForm = Callable[[], ExtendedCombatantData]
