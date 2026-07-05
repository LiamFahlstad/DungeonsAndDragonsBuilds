from dataclasses import dataclass as dataclass_decorator
from enum import Enum
from typing import Optional

from attr import dataclass


class Action(str, Enum):
    HEAL = "heal"
    DAMAGE = "damage"
    ADD_CONDITION = "add_condition"
    REMOVE_CONDITION = "remove_condition"
    ADD_SPELL_SLOT = "add_spell_slot"
    REMOVE_SPELL_SLOT = "remove_spell_slot"
    DEATH_SAVE_FAIL = "death_save_fail"
    DEATH_SAVE_SUCCESS = "death_save_success"


class Condition(str, Enum):
    BLINDED = "Blinded"
    BLOODIED = "Bloodied"
    CHARMED = "Charmed"
    CONCENTRATING = "Concentrating"
    FRIGHTENED = "Frightened"
    GRAPPLED = "Grappled"
    PARALYZED = "Paralyzed"
    POISONED = "Poisoned"
    PRONE = "Prone"
    STUNNED = "Stunned"

    @staticmethod
    def list_all():
        return [cond.value for cond in Condition]


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
class MonsterAbility:
    """A single ability (trait, action, etc.) from a monster's stat block."""

    name: str
    description: str


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
    create_name: Optional[str] = None  # Instance name (display name), distinct from creature type
    visibility_states: Optional[list[Visibility]] = None

    def __attrs_post_init__(self):
        if self.spell_slots is None:
            self.spell_slots = {}
        if self.ability_scores is None:
            self.ability_scores = {}
        if self.saving_throws is None:
            self.saving_throws = {}
        if self.max_hp is None:
            self.max_hp = self.hp
        if self.visibility_states is None:
            self.visibility_states = []

    def as_dict(self, character=None):
        return {
            "name": self.name if self.name is not None else self.combatant_type,
            "create_name": self.create_name if self.create_name is not None else self.combatant_type,
            "combatant_type": self.combatant_type,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "ac": self.ac,
            "temp_hp": self.temp_hp,
            "conditions": self.conditions,
            "visibility_states": self.visibility_states if self.visibility_states is not None else [],
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
    monster_type: str = ""  # e.g. "Large beast"
    ac_note: str = ""  # e.g. "natural armor"
    hp_formula: str = ""  # e.g. "8d10+8"
    speed: str = ""
    skills: Optional[dict[str, int]] = None
    damage_vulnerabilities: Optional[list[str]] = None
    damage_resistances: Optional[list[str]] = None
    damage_immunities: Optional[list[str]] = None
    condition_immunities: Optional[list[str]] = None
    senses: str = ""
    languages: str = ""
    traits: Optional[list] = None  # special traits / passive abilities
    actions: Optional[list] = None  # standard action entries
    bonus_actions: Optional[list] = None  # bonus actions (some monsters)
    reactions: Optional[list] = None  # reactions
    legendary_actions: Optional[list] = None  # legendary actions
    legendary_resistances: int = 0  # count of legendary resistances
    lair_actions: Optional[list] = None  # lair actions
    mythic_actions: Optional[list] = None  # mythic actions (some monsters)

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
