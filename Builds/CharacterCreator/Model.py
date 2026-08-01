"""Plain data model describing a build, shared by the UI, loader and codegen.

Complex values (feats, weapons, species arguments, spells) are stored as
Python expression strings exactly as they appear in a build file, e.g.
"GeneralFeats.WarCaster(character_level=4, ability=Ability.WISDOM)".
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class BuildSpec:
    name: str = "New Character"
    class_key: str = "Fighter"  # e.g. "Cleric"
    subclass_key: str = ""  # e.g. "ClericKnowledge" (module stem)
    level: int = 4

    # lowercase ability name -> score
    abilities: dict = field(default_factory=lambda: dict(
        strength=15, dexterity=13, constitution=14,
        intelligence=10, wisdom=12, charisma=8,
    ))
    # "manual", "standard_array" or "point_buy"
    ability_score_mode: str = "standard_array"

    # Skill member name -> proficient (covers the class' allowed skills)
    class_skills: dict = field(default_factory=dict)

    # (Ability member name, bonus)
    background_bonuses: list = field(default_factory=lambda: [("STRENGTH", 2), ("CONSTITUTION", 1)])
    # Skill member names
    background_skills: list = field(default_factory=lambda: ["PERCEPTION", "SURVIVAL"])

    origin_feat_expr: str = "OriginFeats.Tough()"
    add_default_equipment: bool = True
    armor_exprs: list = field(default_factory=list)
    weapon_exprs: list = field(default_factory=list)

    # level -> {param name -> expression}
    base_level_params: dict = field(default_factory=dict)
    subclass_level_params: dict = field(default_factory=dict)

    # Extra args passed to <Subclass>CustomStarterClassArgs besides skills
    starter_args_extra: dict = field(default_factory=dict)
    # Extra kwargs passed to StarterClassBuilder we don't model structurally
    extra_starter_kwargs: dict = field(default_factory=dict)

    # Extra import lines (loader carries over custom aliases it saw)
    extra_imports: list = field(default_factory=list)

    replace_spells_expr: Optional[str] = None
    items_expr: Optional[str] = None
    tool_proficiencies_expr: Optional[str] = None

    species_class: str = "HumanSpeciesBuilder"
    species_params: dict = field(default_factory=dict)  # param -> expression


def builder_class_name(name: str) -> str:
    """Character name -> generated builder class name."""
    cleaned = "".join(ch for ch in name.title() if ch.isalnum())
    if not cleaned:
        cleaned = "Generated"
    if cleaned[0].isdigit():
        cleaned = "Build" + cleaned
    return cleaned + "CharacterBuilder"


def default_file_name(name: str) -> str:
    cleaned = "".join(ch for ch in name.title() if ch.isalnum())
    return (cleaned or "GeneratedBuild") + ".py"
