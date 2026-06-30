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


class Condition(str, Enum):
    BLINDED = "Blinded"
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


@dataclass_decorator
class MonsterAbility:
    """A single ability (trait, action, etc.) from a monster's stat block."""
    name: str
    description: str


@dataclass
class BasicCombatantData:
    name: str
    hp: int
    ac: int
    temp_hp: int
    conditions: list[Condition]
    spell_slots: Optional[dict[int, int]] = None
    ability_scores: Optional[dict[str, int]] = None
    saving_throws: Optional[dict[str, int]] = None
    max_hp: Optional[int] = None

    def __attrs_post_init__(self):
        if self.spell_slots is None:
            self.spell_slots = {}
        if self.ability_scores is None:
            self.ability_scores = {}
        if self.saving_throws is None:
            self.saving_throws = {}
        if self.max_hp is None:
            self.max_hp = self.hp

    def as_dict(self, character=None):
        return {
            "name": self.name,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "ac": self.ac,
            "temp_hp": self.temp_hp,
            "conditions": self.conditions,
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
    traits: Optional[list] = None               # special traits / passive abilities
    actions: Optional[list] = None              # standard action entries
    bonus_actions: Optional[list] = None        # bonus actions (some monsters)
    reactions: Optional[list] = None            # reactions
    legendary_actions: Optional[list] = None    # legendary actions
    legendary_resistances: int = 0              # count of legendary resistances
    lair_actions: Optional[list] = None         # lair actions
    mythic_actions: Optional[list] = None       # mythic actions (some monsters)

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
        for field in ("traits", "actions", "bonus_actions", "reactions",
                      "legendary_actions", "lair_actions", "mythic_actions"):
            if getattr(self, field) is None:
                setattr(self, field, [])
        if self.legendary_resistances is None:
            self.legendary_resistances = 0
