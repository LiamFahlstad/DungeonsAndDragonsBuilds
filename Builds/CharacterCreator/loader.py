"""Parses an existing build file (e.g. Builds/OptimizedBarbarianBerserker.py)
into a BuildSpec so the UI can preload it.

Works on the source AST (no import of the build) and degrades gracefully:
anything it cannot map to a structured field is kept as a raw expression
string or reported as a warning.
"""

import ast
from pathlib import Path

from Builds.CharacterCreator import registry as registry_module
from Builds.CharacterCreator.model import BuildSpec


class LoadError(Exception):
    pass


def load_build_file(path) -> tuple:
    """Returns (BuildSpec, warnings: list[str])."""
    path = Path(path)
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    warnings = []

    # Inline simple constants (e.g. `monk_level = 3`) so every extracted
    # expression stands alone, then unparse nodes single-line, comment-free.
    tree = _InlineConstants(_simple_constants(tree)).visit(tree)

    def seg(node) -> str:
        return ast.unparse(node)

    builder_class = _find_character_builder_class(tree)
    if builder_class is None:
        raise LoadError(
            f"{path.name}: found no class inheriting from CharacterBuilder."
        )

    init_kwargs = _super_init_kwargs(builder_class)
    if init_kwargs is None:
        raise LoadError(
            f"{path.name}: could not find super().__init__(...) call in "
            f"{builder_class.name}."
        )

    spec = BuildSpec()
    spec.background_bonuses = []
    spec.background_skills = []
    spec.abilities = {}

    name_node = init_kwargs.get("name")
    if isinstance(name_node, ast.Constant) and isinstance(name_node.value, str):
        spec.name = name_node.value
    else:
        warnings.append("Could not read the character name; using a default.")

    if "multiclass_builders" in init_kwargs:
        warnings.append(
            "This build uses multiclassing, which the creator UI does not "
            "support yet. Only the starter class was loaded."
        )

    starter_call = _resolve_starter_call(tree, init_kwargs.get("starter_class_builder"))
    if starter_call is None:
        raise LoadError(f"{path.name}: could not locate the StarterClassBuilder call.")

    _parse_starter_call(spec, starter_call, seg, warnings)
    _parse_species(spec, init_kwargs.get("species_builder"), seg, warnings)
    _carry_unknown_imports(spec, tree)
    return spec, warnings


# --------------------------------------------------------------- AST helpers


def _simple_constants(tree) -> dict:
    """`name = <literal>` assignments anywhere in the file (module or function)."""
    constants = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    constants[target.id] = node.value.value
    return constants


class _InlineConstants(ast.NodeTransformer):
    def __init__(self, constants):
        self.constants = constants

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load) and node.id in self.constants:
            return ast.Constant(value=self.constants[node.id])
        return node


def _carry_unknown_imports(spec, tree):
    """Keep import lines for identifiers the registry cannot resolve.

    Hand-written builds sometimes use custom aliases, e.g.
    `from Spells import Definitions as SpellDefs`. Codegen only knows the
    conventional names, so remember the original import for anything else.
    """
    registry = registry_module.get_registry()
    known = registry.name_to_import()

    alias_lines = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            for alias in node.names:
                bound = alias.asname or alias.name
                as_clause = f" as {alias.asname}" if alias.asname else ""
                alias_lines[bound] = (
                    f"from {node.module} import {alias.name}{as_clause}"
                )
        elif isinstance(node, ast.Import):
            for alias in node.names:
                bound = alias.asname or alias.name.split(".")[0]
                as_clause = f" as {alias.asname}" if alias.asname else ""
                alias_lines[bound] = f"import {alias.name}{as_clause}"

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

    needed = set()
    for expression in expressions:
        if not expression.strip():
            continue
        try:
            parsed = ast.parse(expression)
        except SyntaxError:
            continue
        for node in ast.walk(parsed):
            if isinstance(node, ast.Name):
                needed.add(node.id)

    for name in sorted(needed):
        if name not in known and name in alias_lines:
            line = alias_lines[name]
            if line not in spec.extra_imports:
                spec.extra_imports.append(line)


def _find_character_builder_class(tree):
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            for base in node.bases:
                if _dotted_name(base).endswith("CharacterBuilder"):
                    return node
    return None


def _super_init_kwargs(class_def):
    for node in class_def.body:
        if isinstance(node, ast.FunctionDef) and node.name == "__init__":
            for call in ast.walk(node):
                if (
                    isinstance(call, ast.Call)
                    and isinstance(call.func, ast.Attribute)
                    and call.func.attr == "__init__"
                    and isinstance(call.func.value, ast.Call)
                    and _dotted_name(call.func.value.func) == "super"
                ):
                    return {kw.arg: kw.value for kw in call.keywords if kw.arg}
    return None


def _resolve_starter_call(tree, node):
    """Resolve the starter_class_builder value to the StarterClassBuilder call."""
    if node is None:
        return None
    if isinstance(node, ast.Call):
        name = _dotted_name(node.func)
        if name.endswith("StarterClassBuilder"):
            return node
        # A call like get_starter_class_builder(): inline its return value.
        function = _find_function(tree, name)
        if function is not None:
            for statement in ast.walk(function):
                if isinstance(statement, ast.Return) and isinstance(
                    statement.value, ast.Call
                ):
                    return _resolve_starter_call(tree, statement.value)
    return None


def _find_function(tree, name):
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    return None


def _dotted_name(node) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return f"{_dotted_name(node.value)}.{node.attr}"
    return ""


def _call_kwargs(call):
    return {kw.arg: kw.value for kw in call.keywords if kw.arg}


# ------------------------------------------------------------ starter parse


def _parse_starter_call(spec, call, seg, warnings):
    registry = registry_module.get_registry()
    kwargs = _call_kwargs(call)
    handled = set()

    def take(name):
        handled.add(name)
        return kwargs.get(name)

    # non_generic_arguments -> subclass + class skills
    args_node = take("non_generic_arguments")
    if isinstance(args_node, ast.Call):
        args_class_name = _dotted_name(args_node.func).split(".")[-1]
        subclass_info = registry.subclass_by_args_class_name(args_class_name)
        if subclass_info is not None:
            spec.subclass_key = subclass_info.key
            spec.class_key = subclass_info.class_key
        else:
            warnings.append(
                f"Unknown starter args class {args_class_name!r}; "
                "class/subclass selection may be wrong."
            )
        for name, value in _call_kwargs(args_node).items():
            if name == "skills":
                _parse_skills(spec, value, seg, warnings)
            else:
                spec.starter_args_extra[name] = seg(value)
    else:
        warnings.append("Could not parse non_generic_arguments.")

    level_node = take("base_class_level")
    if isinstance(level_node, ast.Constant) and isinstance(level_node.value, int):
        spec.level = level_node.value
    else:
        warnings.append("Could not read base_class_level; defaulting to 4.")

    abilities_node = take("abilities")
    if isinstance(abilities_node, ast.Call):
        spec.use_standard_array = _dotted_name(abilities_node.func).split(".")[
            -1
        ].startswith("StandardArray")
        for name, value in _call_kwargs(abilities_node).items():
            if isinstance(value, ast.Constant) and isinstance(value.value, int):
                spec.abilities[name] = value.value
    if len(spec.abilities) != 6:
        warnings.append("Could not read all six ability scores.")
        defaults = BuildSpec().abilities
        for key, value in defaults.items():
            spec.abilities.setdefault(key, value)

    bonuses_node = take("background_ability_bonuses")
    for element in _first_list_arg(bonuses_node):
        if isinstance(element, ast.Tuple) and len(element.elts) == 2:
            ability = _enum_member(element.elts[0])
            amount = element.elts[1]
            if ability and isinstance(amount, ast.Constant):
                spec.background_bonuses.append((ability, amount.value))
                continue
        warnings.append("Skipped an unparseable background ability bonus.")

    skills_node = take("background_skill_proficiencies")
    for element in _first_list_arg(skills_node):
        member = _enum_member(element)
        if member:
            spec.background_skills.append(member)
        else:
            warnings.append("Skipped an unparseable background skill.")

    origin_node = take("origin_feat")
    if origin_node is not None:
        spec.origin_feat_expr = seg(origin_node)

    default_equipment_node = take("add_default_equipment")
    if isinstance(default_equipment_node, ast.Constant):
        spec.add_default_equipment = bool(default_equipment_node.value)

    for field_name, target in (("armor", "armor_exprs"), ("weapons", "weapon_exprs")):
        node = take(field_name)
        if node is None:
            continue
        if isinstance(node, ast.List):
            getattr(spec, target).extend(seg(element) for element in node.elts)
        else:
            warnings.append(f"Could not parse {field_name} list.")

    features_node = take("base_class_level_features")
    if isinstance(features_node, ast.Call):
        feature_kwargs = _call_kwargs(features_node)
        _parse_levels(
            spec.base_level_params,
            feature_kwargs.get("base_class_features_by_level"),
            registry.classes().get(spec.class_key),
            seg,
            warnings,
        )
        subclass_info = registry.subclasses().get(spec.subclass_key)
        _parse_levels(
            spec.subclass_level_params,
            feature_kwargs.get("subclass_features_by_level"),
            subclass_info,
            seg,
            warnings,
        )
    else:
        warnings.append("Could not parse base_class_level_features.")

    for optional_name, attr_name in (
        ("replace_spells", "replace_spells_expr"),
        ("items", "items_expr"),
        ("tool_proficiencies", "tool_proficiencies_expr"),
    ):
        node = take(optional_name)
        if node is not None:
            setattr(spec, attr_name, seg(node))

    for name, value in kwargs.items():
        if name not in handled:
            spec.extra_starter_kwargs[name] = seg(value)


def _parse_skills(spec, node, seg, warnings):
    if not isinstance(node, ast.Call):
        warnings.append("Could not parse the class skills stat block.")
        return
    proficiencies = _call_kwargs(node).get("proficiencies")
    if not isinstance(proficiencies, ast.Dict):
        warnings.append("Could not parse class skill proficiencies.")
        return
    for key, value in zip(proficiencies.keys, proficiencies.values):
        member = _enum_member(key)
        if member and isinstance(value, ast.Constant):
            spec.class_skills[member] = bool(value.value)
        else:
            warnings.append("Skipped an unparseable class skill entry.")


def _parse_levels(target, node, info, seg, warnings):
    """Parse a {level: LevelClass(...)} dict into {level: {param: expr}}."""
    if node is None:
        return
    if not isinstance(node, ast.Dict):
        warnings.append("Could not parse a level features dict.")
        return
    import attr as attr_module

    for key, value in zip(node.keys, node.values):
        if not (isinstance(key, ast.Constant) and isinstance(key.value, int)):
            warnings.append("Skipped a level entry with a non-literal level.")
            continue
        level = key.value
        if not isinstance(value, ast.Call):
            warnings.append(f"Skipped unparseable features for level {level}.")
            continue
        params = {}
        for kw in value.keywords:
            if kw.arg:
                params[kw.arg] = seg(kw.value)
        if value.args:
            # Positional arguments: map them onto the attrs field order.
            field_names = []
            if info is not None and level in info.level_classes:
                field_names = [
                    field.name
                    for field in attr_module.fields(info.level_classes[level])
                    if field.init
                ]
            for index, argument in enumerate(value.args):
                if index < len(field_names):
                    params[field_names[index]] = seg(argument)
                else:
                    warnings.append(
                        f"Level {level}: dropped a positional argument "
                        "that could not be matched."
                    )
        target[level] = params


def _parse_species(spec, node, seg, warnings):
    registry = registry_module.get_registry()
    if not isinstance(node, ast.Call):
        warnings.append("Could not parse the species builder; using Human.")
        return
    class_name = _dotted_name(node.func).split(".")[-1]
    if class_name not in registry.species():
        warnings.append(f"Unknown species builder {class_name!r}; using Human.")
        return
    spec.species_class = class_name
    spec.species_params = {}
    for name, value in _call_kwargs(node).items():
        spec.species_params[name] = seg(value)
    if node.args:
        params = registry_module.signature_params(registry.species()[class_name].cls)
        for index, argument in enumerate(node.args):
            if index < len(params):
                spec.species_params[params[index][0]] = seg(argument)
            else:
                warnings.append("Species builder: dropped an extra positional argument.")


def _first_list_arg(node):
    if isinstance(node, ast.Call) and node.args and isinstance(node.args[0], ast.List):
        return node.args[0].elts
    return []


def _enum_member(node):
    """Skill.HISTORY -> "HISTORY" (the member name), else None."""
    if isinstance(node, ast.Attribute):
        return node.attr
    return None
