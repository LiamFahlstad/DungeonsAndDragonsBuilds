"""Generates a build file (same style as the hand-written ones in
Builds/Characters/) from a BuildSpec."""

import ast
import subprocess
import sys

from Builds.CharacterCreator import registry as registry_module
from Builds.CharacterCreator.model import BuildSpec, builder_class_name

INDENT = "    "

_ABILITIES_CLASS_BY_MODE = {
    "standard_array": "StandardArrayAbilitiesStatBlock",
    "point_buy": "PointBuyAbilitiesStatBlock",
    "manual": "AbilitiesStatBlock",
}


def _abilities_class_name(spec: BuildSpec) -> str:
    return _ABILITIES_CLASS_BY_MODE.get(spec.ability_score_mode, "AbilitiesStatBlock")


def generate(spec: BuildSpec) -> str:
    registry = registry_module.get_registry()
    if spec.class_key not in registry.classes():
        raise ValueError(f"Unknown class {spec.class_key!r}.")
    class_info = registry.classes()[spec.class_key]
    if not spec.subclass_key:
        available = sorted(registry.subclasses_for(spec.class_key))
        if available:
            raise ValueError(
                f"No subclass selected for {spec.class_key}. "
                f"Pick one of: {', '.join(available)}."
            )
        raise ValueError(
            f"{spec.class_key} has no subclasses implemented yet "
            f"(no CharacterConfigs/SubClasses2024 module with a "
            f"*CustomStarterClassArgs class), so a build cannot be generated."
        )
    if spec.subclass_key not in registry.subclasses():
        raise ValueError(f"Unknown subclass {spec.subclass_key!r}.")
    subclass_info = registry.subclasses()[spec.subclass_key]

    body = _starter_builder_source(spec, class_info, subclass_info)
    class_source = _character_builder_source(spec, registry)
    imports = _imports_source(spec, registry, class_info, subclass_info)

    return "\n".join([imports, "", "", body, "", "", class_source, ""])


def _used_level_classes(spec, class_info, subclass_info):
    base = {
        level: cls
        for level, cls in sorted(class_info.level_classes.items())
        if level <= spec.level
    }
    sub = {
        level: cls
        for level, cls in sorted(subclass_info.level_classes.items())
        if level <= spec.level
    }
    return base, sub


def _level_call(cls, params: dict, indent: str) -> str:
    if not params:
        return f"{cls.__name__}()"
    lines = [f"{cls.__name__}("]
    for name, expr in params.items():
        if expr is None or expr == "":
            continue
        lines.append(f"{indent}{INDENT}{name}={expr},")
    lines.append(f"{indent})")
    return "\n".join(lines)


def _starter_builder_source(spec, class_info, subclass_info):
    registry = registry_module.get_registry()
    skills_block = class_info.skills_block
    base_levels, sub_levels = _used_level_classes(spec, class_info, subclass_info)

    lines = []
    lines.append("def get_starter_class_builder():")
    lines.append(f"{INDENT}return StarterClassBuilder(")
    arg = f"{INDENT * 2}"

    # non_generic_arguments
    lines.append(f"{arg}non_generic_arguments={subclass_info.args_class.__name__}(")
    if skills_block is not None:
        lines.append(f"{arg}{INDENT}skills={skills_block.cls.__name__}(")
        lines.append(f"{arg}{INDENT * 2}proficiencies={{")
        for skill in skills_block.allowed_skills:
            value = bool(spec.class_skills.get(skill.name, False))
            lines.append(f"{arg}{INDENT * 3}Skill.{skill.name}: {value},")
        lines.append(f"{arg}{INDENT * 2}}}")
        lines.append(f"{arg}{INDENT}),")
    for name, expr in spec.starter_args_extra.items():
        lines.append(f"{arg}{INDENT}{name}={expr},")
    lines.append(f"{arg}),")

    lines.append(f"{arg}base_class_level={spec.level},")

    abilities_class = _abilities_class_name(spec)
    if spec.ability_score_mode == "standard_array":
        lines.append(f"{arg}# Distribute 15, 14, 13, 12, 10, 8 among your abilities.")
    elif spec.ability_score_mode == "point_buy":
        lines.append(f"{arg}# Point buy: scores 8-15, total cost must equal 27.")
    lines.append(f"{arg}abilities={abilities_class}(")
    for ability in (
        "strength",
        "dexterity",
        "constitution",
        "intelligence",
        "wisdom",
        "charisma",
    ):
        lines.append(f"{arg}{INDENT}{ability}={spec.abilities[ability]},")
    lines.append(f"{arg}),")

    lines.append(f"{arg}background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(")
    lines.append(f"{arg}{INDENT}[")
    for ability_name, bonus in spec.background_bonuses:
        lines.append(f"{arg}{INDENT * 2}(Ability.{ability_name}, {bonus}),")
    lines.append(f"{arg}{INDENT}]")
    lines.append(f"{arg}),")

    lines.append(
        f"{arg}background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency("
    )
    lines.append(f"{arg}{INDENT}[")
    for skill_name in spec.background_skills:
        lines.append(f"{arg}{INDENT * 2}Skill.{skill_name},")
    lines.append(f"{arg}{INDENT}]")
    lines.append(f"{arg}),")

    lines.append(f"{arg}add_default_equipment={spec.add_default_equipment},")
    lines.append(f"{arg}origin_feat={spec.origin_feat_expr},")

    if spec.armor_exprs:
        lines.append(f"{arg}armor=[")
        for expr in spec.armor_exprs:
            lines.append(f"{arg}{INDENT}{expr},")
        lines.append(f"{arg}],")
    if spec.weapon_exprs:
        lines.append(f"{arg}weapons=[")
        for expr in spec.weapon_exprs:
            lines.append(f"{arg}{INDENT}{expr},")
        lines.append(f"{arg}],")

    lines.append(f"{arg}base_class_level_features=ClassBuilder.BaseClassLevelFeatures(")
    lines.append(f"{arg}{INDENT}base_class_features_by_level={{")
    for level, cls in base_levels.items():
        params = spec.base_level_params.get(level, {})
        call = _level_call(cls, params, f"{arg}{INDENT * 2}")
        lines.append(f"{arg}{INDENT * 2}{level}: {call},")
    lines.append(f"{arg}{INDENT}}},")
    lines.append(f"{arg}{INDENT}subclass_features_by_level={{")
    for level, cls in sub_levels.items():
        params = spec.subclass_level_params.get(level, {})
        call = _level_call(cls, params, f"{arg}{INDENT * 2}")
        lines.append(f"{arg}{INDENT * 2}{level}: {call},")
    lines.append(f"{arg}{INDENT}}},")
    lines.append(f"{arg}),")

    if spec.replace_spells_expr:
        lines.append(f"{arg}replace_spells={spec.replace_spells_expr},")
    if spec.items_expr:
        lines.append(f"{arg}items={spec.items_expr},")
    if spec.tool_proficiencies_expr:
        lines.append(f"{arg}tool_proficiencies={spec.tool_proficiencies_expr},")
    for name, expr in spec.extra_starter_kwargs.items():
        lines.append(f"{arg}{name}={expr},")

    lines.append(f"{INDENT})")
    return "\n".join(lines)


def _character_builder_source(spec, registry):
    species_info = registry.species()[spec.species_class]
    species_args = "".join(
        f"\n{INDENT * 4}{name}={expr}," for name, expr in spec.species_params.items()
    )
    if species_args:
        species_call = (
            f"{species_info.module_name}.{spec.species_class}({species_args}"
            f"\n{INDENT * 3})"
        )
    else:
        species_call = f"{species_info.module_name}.{spec.species_class}()"

    class_name = builder_class_name(spec.name)
    return (
        f"class {class_name}(CharacterBuilder):\n"
        f"{INDENT}def __init__(self):\n"
        f"{INDENT * 2}super().__init__(\n"
        f"{INDENT * 3}name={spec.name!r},\n"
        f"{INDENT * 3}starter_class_builder=get_starter_class_builder(),\n"
        f"{INDENT * 3}species_builder={species_call},\n"
        f"{INDENT * 2})"
    )


def _collect_identifiers(source: str) -> set:
    """All top-level identifiers referenced in generated code expressions."""
    names = set()
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return names
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            names.add(node.id)
    return names


def _imports_source(spec, registry, class_info, subclass_info):
    base_levels, sub_levels = _used_level_classes(spec, class_info, subclass_info)

    # Everything the generated body references.
    expressions = [spec.origin_feat_expr or ""]
    expressions += spec.armor_exprs + spec.weapon_exprs
    expressions += [e or "" for e in spec.starter_args_extra.values()]
    expressions += [e or "" for e in spec.extra_starter_kwargs.values()]
    expressions += [e or "" for e in spec.species_params.values()]
    for params in list(spec.base_level_params.values()) + list(
        spec.subclass_level_params.values()
    ):
        expressions += [e or "" for e in params.values()]
    for optional in (
        spec.replace_spells_expr,
        spec.items_expr,
        spec.tool_proficiencies_expr,
    ):
        if optional:
            expressions.append(optional)

    referenced = set()
    for expr in expressions:
        if expr.strip():
            referenced |= _collect_identifiers(expr)
    referenced |= {"Ability", "Skill"}
    referenced.add("Backgrounds")

    name_to_import = registry.name_to_import()
    from_imports = {}  # module -> set of names

    def add(module, name):
        from_imports.setdefault(module, set()).add(name)

    add("Builds.CharacterBuilder", "CharacterBuilder")
    add("CharacterConfigs.BaseClasses", "ClassBuilder")
    add("CharacterConfigs.BaseClasses.ClassBuilder", "StarterClassBuilder")
    add(
        f"CharacterConfigs.BaseClasses.{spec.class_key}Base",
        None,  # placeholder; real names added below
    )
    from_imports[f"CharacterConfigs.BaseClasses.{spec.class_key}Base"] = {
        cls.__name__ for cls in base_levels.values()
    }
    subclass_names = {cls.__name__ for cls in sub_levels.values()}
    subclass_names.add(subclass_info.args_class.__name__)
    from_imports[subclass_info.module.__name__] = subclass_names

    if class_info.skills_block is not None:
        add("StatBlocks.SkillsStatBlock", class_info.skills_block.cls.__name__)
    abilities_class = _abilities_class_name(spec)
    add("StatBlocks.AbilitiesStatBlock", abilities_class)

    species_info = registry.species()[spec.species_class]
    add("SpeciesConfigs", species_info.module_name)

    for name in sorted(referenced):
        if name in name_to_import:
            module, imported = name_to_import[name]
            add(module, imported)

    lines = []
    plain = sorted(from_imports.pop("", set()))
    for name in plain:
        lines.append(f"import {name}")
    for module in sorted(from_imports):
        names = sorted(n for n in from_imports[module] if n)
        if not names:
            continue
        single = f"from {module} import {', '.join(names)}"
        if len(single) <= 88:
            lines.append(single)
        else:
            lines.append(f"from {module} import (")
            for name in names:
                lines.append(f"{INDENT}{name},")
            lines.append(")")
    for line in spec.extra_imports:
        if line not in lines:
            lines.append(line)
    return "\n".join(lines)


def validate_build_file(path) -> tuple:
    """Import the generated file in a subprocess and run .build().

    Returns (ok: bool, output: str).
    """
    code = (
        "import importlib.util, sys\n"
        f"sys.path.insert(0, {str(registry_module.REPO_ROOT)!r})\n"
        f"spec = importlib.util.spec_from_file_location('generated_build', {str(path)!r})\n"
        "module = importlib.util.module_from_spec(spec)\n"
        "spec.loader.exec_module(module)\n"
        "from Builds.CharacterBuilder import CharacterBuilder\n"
        "builders = [obj for obj in vars(module).values()\n"
        "            if isinstance(obj, type)\n"
        "            and issubclass(obj, CharacterBuilder)\n"
        "            and obj is not CharacterBuilder]\n"
        "assert builders, 'No CharacterBuilder subclass found'\n"
        "data = builders[0]().build()\n"
        "print('OK:', data.character_name)\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        cwd=str(registry_module.REPO_ROOT),
        timeout=120,
    )
    output = (result.stdout or "") + (result.stderr or "")
    return result.returncode == 0, output.strip()
