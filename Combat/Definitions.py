from dataclasses import dataclass as dataclass_decorator
from enum import Enum
from typing import Optional

from attr import dataclass

from Definitions import Skill


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
    DEAFENED = "Deafened"
    EXHAUSTION = "Exhaustion"
    FRIGHTENED = "Frightened"
    GRAPPLED = "Grappled"
    INCAPACITATED = "Incapacitated"
    INVISIBLE = "Invisible"
    PARALYZED = "Paralyzed"
    PETRIFIED = "Petrified"
    POISONED = "Poisoned"
    PRONE = "Prone"
    RESTRAINED = "Restrained"
    STUNNED = "Stunned"
    UNCONSCIOUS = "Unconscious"

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


class DamageType(str, Enum):
    ACID = "Acid"
    BLUDGEONING = "Bludgeoning"
    COLD = "Cold"
    FIRE = "Fire"
    FORCE = "Force"
    LIGHTNING = "Lightning"
    NECROTIC = "Necrotic"
    PIERCING = "Piercing"
    POISON = "Poison"
    PSYCHIC = "Psychic"
    RADIANT = "Radiant"
    SLASHING = "Slashing"
    THUNDER = "Thunder"


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
    monster_type: str = ""  # e.g. "Large beast"
    ac_note: str = ""  # e.g. "natural armor"
    hp_formula: str = ""  # e.g. "8d10+8"
    speed: str = ""
    skills: Optional[dict[Skill, int]] = None
    damage_vulnerabilities: Optional[list[DamageTypeEntry]] = None
    damage_resistances: Optional[list[DamageTypeEntry]] = None
    damage_immunities: Optional[list[DamageTypeEntry]] = None
    condition_immunities: Optional[list[Condition]] = None
    senses: str = ""
    languages: str = ""
    traits: Optional[list[MonsterAbility]] = None  # special traits / passive abilities
    actions: Optional[list[MonsterAbility]] = None  # standard action entries
    bonus_actions: Optional[list[MonsterAbility]] = None  # bonus actions (some monsters)
    reactions: Optional[list[MonsterAbility]] = None  # reactions
    legendary_actions: Optional[list[MonsterAbility]] = None  # legendary actions
    legendary_resistances: int = 0  # count of legendary resistances
    lair_actions: Optional[list[MonsterAbility]] = None  # lair actions
    mythic_actions: Optional[list[MonsterAbility]] = None  # mythic actions (some monsters)

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


class ConditionRule(Enum):
    """Each member stores (heading, description) taken from the rules glossary."""

    BLINDED = (
        "Blinded [Condition]",
        "While you have the Blinded condition, you experience the following effects.\n\n"
        "Can't See. You can't see and automatically fail any ability check that requires sight.\n\n"
        "Attacks Affected. Attack rolls against you have Advantage, and your attack rolls have Disadvantage.",
    )
    CHARMED = (
        "Charmed [Condition]",
        "While you have the Charmed condition, you experience the following effects.\n\n"
        "Can't Harm the Charmer. You can't attack the charmer or target the charmer with damaging abilities or magical effects.\n\n"
        "Social Advantage. The charmer has Advantage on any ability check to interact with you socially.",
    )
    CONCENTRATING = (
        "Concentration",
        "Some spells and other effects require Concentration to remain active. "
        "If the effect's creator loses Concentration, the effect ends. "
        "The creator can end Concentration at any time (no action required). "
        "The following factors break Concentration.\n\n"
        "Another Concentration Effect. You lose Concentration on an effect the moment you start casting a spell "
        "that requires Concentration or activate another effect that requires Concentration.\n\n"
        "Damage. If you take damage, you must succeed on a Constitution saving throw to maintain Concentration. "
        "The DC equals 10 or half the damage taken (round down), whichever is higher, up to a maximum DC of 30.\n\n"
        "Incapacitated or Dead. Your Concentration ends if you have the Incapacitated condition or you die.",
    )
    DEAFENED = (
        "Deafened [Condition]",
        "While you have the Deafened condition, you experience the following effect.\n\n"
        "Can't Hear. You can't hear and automatically fail any ability check that requires hearing.",
    )
    EXHAUSTION = (
        "Exhaustion [Condition]",
        "Exhaustion is measured in six levels. An effect can give a creature one or more levels of "
        "Exhaustion, as specified in the effect's description.\n\n"
        "Effects of Exhaustion. A creature suffers the effects of its greatest level of Exhaustion. "
        "Each level gives a cumulative -2 penalty to D20 Tests, and the creature's Speed is reduced by "
        "5 feet per level.\n\n"
        "Removing Exhaustion Levels. Finishing a Long Rest removes one level of Exhaustion from the "
        "creature, provided that the creature has also had some food and drink.\n\n"
        "Effects Cumulative. Multiple instances of Exhaustion add their Exhaustion levels together, up "
        "to a maximum level of 6. If a creature already has Exhaustion and something would give it 6 "
        "more levels, the creature dies.",
    )
    FRIGHTENED = (
        "Frightened [Condition]",
        "While you have the Frightened condition, you experience the following effects.\n\n"
        "Ability Checks and Attacks Affected. You have Disadvantage on ability checks and attack rolls "
        "while the source of fear is within line of sight.\n\n"
        "Can't Approach. You can't willingly move closer to the source of fear.",
    )
    GRAPPLED = (
        "Grappled [Condition]",
        "While you have the Grappled condition, you experience the following effects.\n\n"
        "Speed 0. Your Speed is 0 and can't increase.\n\n"
        "Attacks Affected. You have Disadvantage on attack rolls against any target other than the grappler.\n\n"
        "Movable. The grappler can drag or carry you when it moves, but every foot of movement costs it "
        "1 extra foot unless you are Tiny or two or more sizes smaller than it.",
    )
    INCAPACITATED = (
        "Incapacitated [Condition]",
        "While you have the Incapacitated condition, you experience the following effects.\n\n"
        "Inactive. You can't take any action, Bonus Action, or Reaction.\n\n"
        "No Concentration. Your Concentration is broken if you had it.\n\n"
        "Speechless. You can't speak.\n\n"
        "Surprised. If you're Incapacitated when you roll Initiative, you have Disadvantage on the roll.",
    )
    INVISIBLE = (
        "Invisible [Condition]",
        "While you have the Invisible condition, you experience the following effects.\n\n"
        "Surprise. If you're Invisible when you roll Initiative, you have Advantage on the roll.\n\n"
        "Concealed. You can't be seen without the aid of magic or a special sense. For the purpose of "
        "Hiding, you're heavily obscured. Your location can be detected by any noise you make or any "
        "tracks you leave.\n\n"
        "Attacks Affected. Attack rolls against you have Disadvantage, and your attack rolls have Advantage.",
    )
    PARALYZED = (
        "Paralyzed [Condition]",
        "While you have the Paralyzed condition, you experience the following effects.\n\n"
        "Incapacitated. You have the Incapacitated condition.\n\n"
        "Speed 0. Your Speed is 0 and can't increase.\n\n"
        "Saving Throws Affected. You automatically fail Strength and Dexterity saving throws.\n\n"
        "Attacks Affected. Attack rolls against you have Advantage.\n\n"
        "Automatic Critical Hits. Any attack roll that hits you is a Critical Hit if the attacker is within 5 feet of you.",
    )
    PETRIFIED = (
        "Petrified [Condition]",
        "While you have the Petrified condition, you experience the following effects.\n\n"
        "Turned to Inert Substance. You are transformed, along with any nonmagical objects you are "
        "wearing or carrying, into a solid inanimate substance (usually stone). Your weight increases "
        "by a factor of ten, and you cease aging.\n\n"
        "Incapacitated. You have the Incapacitated condition.\n\n"
        "Attacks Affected. Attack rolls against you have Advantage.\n\n"
        "Saving Throws Affected. You automatically fail Strength and Dexterity saving throws.\n\n"
        "Resistances. You have Resistance to all damage.\n\n"
        "Poison Immunity. You have Immunity to the Poisoned condition.",
    )
    POISONED = (
        "Poisoned [Condition]",
        "While you have the Poisoned condition, you experience the following effect.\n\n"
        "Ability Checks and Attacks Affected. You have Disadvantage on attack rolls and ability checks.",
    )
    PRONE = (
        "Prone [Condition]",
        "While you have the Prone condition, you experience the following effects.\n\n"
        "Restricted Movement. Your only movement options are to crawl or to spend an amount of movement "
        "equal to half your Speed (round down) to right yourself and thereby end the condition. "
        "If your Speed is 0, you can't right yourself.\n\n"
        "Attacks Affected. You have Disadvantage on attack rolls. An attack roll against you has Advantage "
        "if the attacker is within 5 feet of you. Otherwise, that attack roll has Disadvantage.",
    )
    RESTRAINED = (
        "Restrained [Condition]",
        "While you have the Restrained condition, you experience the following effects.\n\n"
        "Speed 0. Your Speed is 0 and can't increase.\n\n"
        "Attacks Affected. Attack rolls against you have Advantage, and your attack rolls have Disadvantage.\n\n"
        "Saving Throws Affected. You have Disadvantage on Dexterity saving throws.",
    )
    STUNNED = (
        "Stunned [Condition]",
        "While you have the Stunned condition, you experience the following effects.\n\n"
        "Incapacitated. You have the Incapacitated condition.\n\n"
        "Saving Throws Affected. You automatically fail Strength and Dexterity saving throws.\n\n"
        "Attacks Affected. Attack rolls against you have Advantage.",
    )
    UNCONSCIOUS = (
        "Unconscious [Condition]",
        "While you have the Unconscious condition, you experience the following effects.\n\n"
        "Incapacitated. You have the Incapacitated condition, and you can't speak.\n\n"
        "Unaware. You're unaware of your surroundings.\n\n"
        "Drop and Prone. You drop whatever you're holding and fall Prone.\n\n"
        "Saving Throws Affected. You automatically fail Strength and Dexterity saving throws.\n\n"
        "Attacks Affected. Attack rolls against you have Advantage.\n\n"
        "Automatic Critical Hits. Any attack roll that hits you is a Critical Hit if the attacker is within 5 feet of you.",
    )

    @property
    def heading(self) -> str:
        return self.value[0]

    @property
    def description(self) -> str:
        return self.value[1]

    @classmethod
    def from_name(cls, name: str) -> "ConditionRule | None":
        try:
            return cls[name.upper().replace(" ", "_")]
        except KeyError:
            pass
        name_lower = name.lower()
        for member in cls:
            if member.heading.lower().startswith(name_lower):
                return member
        return None
