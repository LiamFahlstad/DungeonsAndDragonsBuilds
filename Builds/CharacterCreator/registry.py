"""Runtime introspection of the codebase for the Character Creator UI.

Discovers character classes, subclasses, species, feats, spell enums and
equipment so the UI can offer them as choices without hardcoding anything.
"""

import ast
import enum
import importlib
import inspect
import sys
import textwrap
import types
import typing
from pathlib import Path

import attr

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def ensure_repo_on_path():
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))


ensure_repo_on_path()

from CharacterConfigs.BaseClasses import ClassBuilder  # noqa: E402
from Definitions import Skill  # noqa: E402


class ClassInfo:
    def __init__(self, key, module, level_classes, skills_block):
        self.key = key  # e.g. "Cleric"
        self.module = module
        self.level_classes = level_classes  # dict[int, type]
        self.skills_block = skills_block  # SkillsBlockInfo or None


class SubclassInfo:
    def __init__(self, key, class_key, module, level_classes, args_class):
        self.key = key  # module stem, e.g. "ClericKnowledge"
        self.class_key = class_key  # e.g. "Cleric"
        self.module = module
        self.level_classes = level_classes  # dict[int, type]
        self.args_class = args_class  # <X>CustomStarterClassArgs


class SpeciesInfo:
    def __init__(self, module_name, cls):
        self.module_name = module_name  # e.g. "Warforged"
        self.cls = cls


class SkillsBlockInfo:
    def __init__(self, cls, allowed_skills, num_proficiencies):
        self.cls = cls
        self.allowed_skills = allowed_skills  # list[Skill]
        self.num_proficiencies = num_proficiencies


def _classes_defined_in(module):
    return [
        cls
        for cls in vars(module).values()
        if inspect.isclass(cls) and cls.__module__ == module.__name__
    ]


def _level_of(cls) -> int:
    field = attr.fields_dict(cls).get("level")
    if field is None or field.default is attr.NOTHING:
        raise ValueError(f"{cls.__name__} has no level default")
    return field.default


def _collect_level_classes(module, base) -> dict:
    """All attrs LevelFeatures subclasses of `base` defined in `module`, by level."""
    result = {}
    for cls in _classes_defined_in(module):
        if not issubclass(cls, base) or inspect.isabstract(cls):
            continue
        if not attr.has(cls):
            continue
        try:
            result[_level_of(cls)] = cls
        except ValueError:
            continue
    return result


def _resolve_attr_chain(node, module):
    """Resolve an ast.Name/ast.Attribute chain (e.g. Features.Foo.Bar)
    against a module's namespace. Returns None when unresolvable."""
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if not isinstance(node, ast.Name) or module is None:
        return None
    obj = getattr(module, node.id, None)
    for part in reversed(parts):
        if obj is None:
            return None
        obj = getattr(obj, part, None)
    return obj


def _skill_constants_in_source(cls) -> list:
    """Ordered, unique Skill member names written as Skill.X constants
    anywhere in a class' source (a choice pool by convention)."""
    try:
        tree = ast.parse(textwrap.dedent(inspect.getsource(cls)))
    except (OSError, TypeError, SyntaxError):
        return []
    nodes = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id == "Skill"
        and node.attr in Skill.__members__
    ]
    nodes.sort(key=lambda node: (node.lineno, node.col_offset))
    found = []
    for node in nodes:
        if node.attr not in found:
            found.append(node.attr)
    return found


def _base_level_bases():
    return tuple(
        getattr(ClassBuilder, f"BaseClassLevel{n}")
        for n in range(1, 21)
        if hasattr(ClassBuilder, f"BaseClassLevel{n}")
    )


def _subclass_level_bases():
    return tuple(
        getattr(ClassBuilder, f"SubclassLevel{n}")
        for n in range(1, 21)
        if hasattr(ClassBuilder, f"SubclassLevel{n}")
    )


class Registry:
    def __init__(self):
        self._classes = None
        self._subclasses = None
        self._species = None
        self._spell_enums = None
        self._name_to_import = None
        self._granted_members = {}
        self._skill_pools = {}
        self._enum_param_hints = {}

    # --------------------------------------------------- unconditional grants

    def granted_member_names(self, module) -> set:
        """Enum member names a class/subclass module grants unconditionally:
        constant Enum.MEMBER arguments to add_spell(...)/add_cantrip(...)
        calls in the module source. Default spell/cantrip picks are seeded
        away from these because the sheet rejects duplicates."""
        if module is None:
            return set()
        cached = self._granted_members.get(module.__name__)
        if cached is not None:
            return cached
        names = set()
        try:
            tree = ast.parse(inspect.getsource(module))
        except (OSError, TypeError, SyntaxError):
            tree = None
        if tree is not None:
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                func = node.func
                if not (
                    isinstance(func, ast.Attribute)
                    and func.attr in ("add_spell", "add_cantrip")
                ):
                    continue
                for arg in node.args:
                    if not isinstance(arg, ast.Attribute) or not arg.attr.isupper():
                        continue
                    root = arg.value
                    while isinstance(root, ast.Attribute):
                        root = root.value
                    if isinstance(root, ast.Name) and root.id != "self":
                        names.add(arg.attr)
        self._granted_members[module.__name__] = names
        return names

    def skill_pool_hints(self, cls) -> dict:
        """param name -> ordered list of Skill member names allowed for a
        level class' param. Derived by convention: add_features passes
        self.<param> to a feature class whose source enumerates Skill.X
        constants — its choice pool (e.g. BlessingsOfKnowledge, Primal
        Knowledge). Used to pick valid default choices; empty when a param
        has no discoverable restriction."""
        cache_key = f"{cls.__module__}.{cls.__qualname__}"
        cached = self._skill_pools.get(cache_key)
        if cached is not None:
            return cached
        hints = {}
        module = sys.modules.get(cls.__module__)
        try:
            tree = ast.parse(textwrap.dedent(inspect.getsource(cls)))
        except (OSError, TypeError, SyntaxError):
            tree = None
        if tree is not None:
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                args = list(node.args) + [kw.value for kw in node.keywords]
                param_names = [
                    arg.attr
                    for arg in args
                    if isinstance(arg, ast.Attribute)
                    and isinstance(arg.value, ast.Name)
                    and arg.value.id == "self"
                ]
                if not param_names:
                    continue
                feature_cls = _resolve_attr_chain(node.func, module)
                if not inspect.isclass(feature_cls):
                    continue
                pool = _skill_constants_in_source(feature_cls)
                if pool:
                    for name in param_names:
                        hints.setdefault(name, pool)
        self._skill_pools[cache_key] = hints
        return hints

    def enum_param_hints(self, cls) -> dict:
        """param name -> [enum classes] for constructor params that are
        annotated as plain str but hold enum members in practice: the class'
        source passes the param to a call together with an enum class (e.g.
        MagicInitiateWizard's _resolve_spell_enum(cantrip_1,
        WizardLevel0Spells)). Lets the UI offer an enum dropdown instead of a
        free-text field."""
        cache_key = f"{cls.__module__}.{cls.__qualname__}"
        cached = self._enum_param_hints.get(cache_key)
        if cached is not None:
            return cached
        hints = {}
        module = sys.modules.get(cls.__module__)
        param_names = {name for name, _annotation, _required in signature_params(cls)}
        try:
            tree = ast.parse(textwrap.dedent(inspect.getsource(cls)))
        except (OSError, TypeError, SyntaxError):
            tree = None
        if tree is not None and param_names:
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                args = list(node.args) + [kw.value for kw in node.keywords]
                names = [
                    arg.id
                    for arg in args
                    if isinstance(arg, ast.Name) and arg.id in param_names
                ]
                enums = [
                    obj
                    for arg in args
                    if isinstance(arg, (ast.Name, ast.Attribute))
                    for obj in [_resolve_attr_chain(arg, module)]
                    if inspect.isclass(obj) and issubclass(obj, enum.Enum)
                ]
                if names and enums:
                    for name in names:
                        hints.setdefault(name, enums)
        self._enum_param_hints[cache_key] = hints
        return hints

    # ------------------------------------------------------------- classes

    def classes(self) -> dict:
        """dict[class key, ClassInfo], e.g. {"Cleric": ClassInfo, ...}"""
        if self._classes is not None:
            return self._classes
        base_bases = _base_level_bases()
        result = {}
        base_dir = REPO_ROOT / "CharacterConfigs" / "BaseClasses"
        for path in sorted(base_dir.glob("*Base.py")):
            key = path.stem[: -len("Base")]
            try:
                module = importlib.import_module(
                    f"CharacterConfigs.BaseClasses.{path.stem}"
                )
            except Exception:
                continue
            level_classes = _collect_level_classes(module, base_bases)
            if not level_classes:
                continue
            result[key] = ClassInfo(
                key=key,
                module=module,
                level_classes=level_classes,
                skills_block=self._skills_block_for(key),
            )
        self._classes = result
        return result

    def _skills_block_for(self, key):
        import StatBlocks.SkillsStatBlock as skills_module

        cls = getattr(skills_module, f"{key}SkillsStatBlock", None)
        if cls is None:
            return None
        try:
            allowed, num = _parse_skills_block_source(cls)
        except Exception:
            return None
        return SkillsBlockInfo(cls, allowed, num)

    # ---------------------------------------------------------- subclasses

    def subclasses(self) -> dict:
        """dict[subclass key (module stem), SubclassInfo]"""
        if self._subclasses is not None:
            return self._subclasses
        subclass_bases = _subclass_level_bases()
        class_keys = sorted(self.classes(), key=len, reverse=True)
        result = {}
        sub_dir = REPO_ROOT / "CharacterConfigs" / "SubClasses"
        for path in sorted(sub_dir.glob("*.py")):
            if path.stem.startswith("__"):
                continue
            try:
                module = importlib.import_module(
                    f"CharacterConfigs.SubClasses.{path.stem}"
                )
            except Exception:
                continue
            args_class = None
            for cls in _classes_defined_in(module):
                if cls.__name__.endswith("CustomStarterClassArgs"):
                    args_class = cls
                    break
            level_classes = _collect_level_classes(module, subclass_bases)
            if args_class is None:
                continue
            class_key = next(
                (k for k in class_keys if path.stem.startswith(k)), None
            )
            if class_key is None:
                continue
            result[path.stem] = SubclassInfo(
                key=path.stem,
                class_key=class_key,
                module=module,
                level_classes=level_classes,
                args_class=args_class,
            )
        self._subclasses = result
        return result

    def subclasses_for(self, class_key) -> dict:
        return {
            key: info
            for key, info in self.subclasses().items()
            if info.class_key == class_key
        }

    def subclass_by_args_class_name(self, args_class_name):
        for info in self.subclasses().values():
            if info.args_class.__name__ == args_class_name:
                return info
        return None

    # ------------------------------------------------------------- species

    def species(self) -> dict:
        """dict[species builder class name, SpeciesInfo]"""
        if self._species is not None:
            return self._species
        from SpeciesConfigs.SpeciesBuilder import SpeciesBuilder

        result = {}
        species_dir = REPO_ROOT / "SpeciesConfigs"
        for path in sorted(species_dir.glob("*.py")):
            if path.stem in ("SpeciesBuilder", "__init__"):
                continue
            try:
                module = importlib.import_module(f"SpeciesConfigs.{path.stem}")
            except Exception:
                continue
            for cls in _classes_defined_in(module):
                if (
                    issubclass(cls, SpeciesBuilder)
                    and cls is not SpeciesBuilder
                    and not inspect.isabstract(cls)
                ):
                    result[cls.__name__] = SpeciesInfo(path.stem, cls)
        self._species = result
        return result

    # ----------------------------------------------------- feats and spells

    def feat_module(self, name):
        return importlib.import_module(f"Features.CharacterFeats.{name}")

    def concrete_subclasses(self, base) -> list:
        """Non-abstract subclasses of `base` defined in base's module."""
        module = importlib.import_module(base.__module__)
        result = []
        for cls in _classes_defined_in(module):
            if (
                issubclass(cls, base)
                and cls is not base
                and not inspect.isabstract(cls)
            ):
                result.append(cls)
        result.sort(key=lambda c: c.__name__)
        return result

    def spell_enums(self) -> dict:
        """dict[enum class name, enum class] from Spells.SpellLists."""
        if self._spell_enums is not None:
            return self._spell_enums
        module = importlib.import_module("Spells.SpellLists")
        self._spell_enums = {
            cls.__name__: cls
            for cls in vars(module).values()
            if inspect.isclass(cls)
            and issubclass(cls, enum.Enum)
            and cls.__module__ == module.__name__
        }
        return self._spell_enums

    def equipment(self, kind) -> list:
        """kind: "Weapons" or "Armor" -> concrete equipment classes."""
        module = importlib.import_module(f"Features.Equipment.{kind}")
        base_name = "AbstractWeapon" if kind == "Weapons" else "AbstractArmor"
        base = getattr(module, base_name)
        return self.concrete_subclasses(base)

    # -------------------------------------------------- import resolution

    def name_to_import(self) -> dict:
        """Maps top-level identifiers used in expressions to their import.

        Value is (from_module, imported_name).
        """
        if self._name_to_import is not None:
            return self._name_to_import
        mapping = {}

        import Definitions as definitions_module

        for name, obj in vars(definitions_module).items():
            if inspect.isclass(obj) and obj.__module__ == "Definitions":
                mapping[name] = ("Definitions", name)

        for name in self.spell_enums():
            mapping[name] = ("Spells.SpellLists", name)

        for name in ("Backgrounds", "EpicBoon", "GeneralFeats", "OriginFeats"):
            mapping[name] = ("Features.CharacterFeats", name)

        mapping["Armor"] = ("Features.Equipment", "Armor")
        mapping["Weapons"] = ("Features.Equipment", "Weapons")
        mapping["Items"] = ("Features.Items", "Items")
        mapping["SpellSlots"] = ("Features.ClassFeatures", "SpellSlots")
        mapping["ToolProficiency"] = (
            "ToolProficiencies.ToolProficiencies",
            "ToolProficiency",
        )
        # Module alias so ToolProficiencies.ThievesTools() style expressions
        # (emitted by the tool proficiency picker) import cleanly.
        mapping["ToolProficiencies"] = ("ToolProficiencies", "ToolProficiencies")

        import StatBlocks.AbilitiesStatBlock as abilities_module

        for name, obj in vars(abilities_module).items():
            if inspect.isclass(obj) and obj.__module__ == abilities_module.__name__:
                mapping[name] = ("StatBlocks.AbilitiesStatBlock", name)

        import StatBlocks.SkillsStatBlock as skills_module

        for name, obj in vars(skills_module).items():
            if inspect.isclass(obj) and obj.__module__ == skills_module.__name__:
                mapping[name] = ("StatBlocks.SkillsStatBlock", name)

        for info in self.species().values():
            mapping[info.module_name] = ("SpeciesConfigs", info.module_name)

        # Feature modules referenced inside expressions, e.g.
        # FightingStyles.Defense(), Maneuvers.PrecisionAttack(), GoliathFeatures.
        features_dir = REPO_ROOT / "Features"
        for package in features_dir.iterdir():
            if not package.is_dir() or package.name.startswith("__"):
                continue
            for path in package.rglob("*.py"):
                if path.stem.startswith("__") or "__pycache__" in path.parts:
                    continue
                module_dotted = ".".join(path.parent.relative_to(REPO_ROOT).parts)
                mapping.setdefault(path.stem, (module_dotted, path.stem))

        # Warlock invocations, e.g. InvocationsLevel2.AGONIZING_BLAST.
        try:
            invocations = importlib.import_module("Invocations.Definitions")
            for name, obj in vars(invocations).items():
                if inspect.isclass(obj) and obj.__module__ == invocations.__name__:
                    mapping.setdefault(name, ("Invocations.Definitions", name))
        except Exception:
            pass

        # Aliases some hand-written builds use for the spells module.
        mapping.setdefault("SpellDefinitions", ("Spells", "Definitions as SpellDefinitions"))
        mapping.setdefault("SpellsDefinitions", ("Spells", "Definitions as SpellsDefinitions"))
        mapping.setdefault("Definitions", ("", "Definitions"))

        self._name_to_import = mapping
        return mapping

    # ------------------------------------------------------- level params

    def level_params(self, cls) -> list:
        """[(param name, resolved annotation)] for an attrs level class."""
        params = []
        try:
            hints = typing.get_type_hints(cls)
        except Exception:
            hints = {}
        for field in attr.fields(cls):
            if not field.init:
                continue
            annotation = hints.get(field.name, field.type)
            params.append((field.name, annotation, field.default is attr.NOTHING))
        return params


def _parse_skills_block_source(cls):
    """Extract allowed_skills and num_proficiencies from a skills block class."""
    source = textwrap.dedent(inspect.getsource(cls))
    tree = ast.parse(source)
    allowed = None
    num = None
    namespace = {"Skill": Skill, "list": list}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "allowed_skills":
                    allowed = eval(  # noqa: S307 - trusted repo source
                        compile(ast.Expression(node.value), "<skills>", "eval"),
                        namespace,
                    )
        if isinstance(node, ast.keyword) and node.arg == "num_proficiencies":
            if isinstance(node.value, ast.Constant):
                num = node.value.value
    if allowed is None or num is None:
        raise ValueError(f"Could not parse skills block {cls.__name__}")
    return list(allowed), num


# ------------------------------------------------------ annotation editors


class EditorKind:
    ENUM = "enum"  # options: list of enum classes
    CLASS = "class"  # options: base class (pick a subclass)
    INT = "int"
    FLOAT = "float"
    BOOL = "bool"
    STR = "str"
    SKILL_LIST = "skill_list"
    ABILITY_BONUS_LIST = "ability_bonus_list"
    LIST = "list"  # payload: item annotation
    DICT = "dict"  # payload: (key annotation, value annotation)
    RAW = "raw"


class ResolvedAnnotation:
    def __init__(self, kind, payload=None, optional=False):
        self.kind = kind
        self.payload = payload
        self.optional = optional


def resolve_annotation(annotation) -> ResolvedAnnotation:
    """Map a type annotation to a UI editor description."""
    from Definitions import Ability

    optional = False
    args = _union_members(annotation)
    if args is not None:
        non_none = [a for a in args if a is not type(None)]
        optional = len(non_none) < len(args)
        if len(non_none) == 1:
            annotation = non_none[0]
            nested = _union_members(annotation)
            if nested is None:
                resolved = resolve_annotation(annotation)
                resolved.optional = resolved.optional or optional
                return resolved
            args = nested
            non_none = [a for a in args if a is not type(None)]
        if non_none and all(
            inspect.isclass(a) and issubclass(a, enum.Enum) for a in non_none
        ):
            return ResolvedAnnotation(EditorKind.ENUM, non_none, optional)
        return ResolvedAnnotation(EditorKind.RAW, optional=optional)

    if inspect.isclass(annotation):
        if issubclass(annotation, enum.Enum):
            return ResolvedAnnotation(EditorKind.ENUM, [annotation], optional)
        if annotation is int:
            return ResolvedAnnotation(EditorKind.INT, optional=optional)
        if annotation is bool:
            return ResolvedAnnotation(EditorKind.BOOL, optional=optional)
        if annotation is float:
            return ResolvedAnnotation(EditorKind.FLOAT, optional=optional)
        if annotation is str:
            return ResolvedAnnotation(EditorKind.STR, optional=optional)
        return ResolvedAnnotation(EditorKind.CLASS, annotation, optional)

    origin = typing.get_origin(annotation)
    if origin in (list, typing.List):
        (item,) = typing.get_args(annotation) or (None,)
        if item is Skill:
            return ResolvedAnnotation(EditorKind.SKILL_LIST, optional=optional)
        item_origin = typing.get_origin(item)
        if item_origin in (tuple, typing.Tuple):
            tuple_args = typing.get_args(item)
            if len(tuple_args) == 2 and tuple_args[0] is Ability and tuple_args[1] is int:
                return ResolvedAnnotation(
                    EditorKind.ABILITY_BONUS_LIST, optional=optional
                )
        if item is not None:
            return ResolvedAnnotation(EditorKind.LIST, item, optional)
    if origin in (dict, typing.Dict):
        args = typing.get_args(annotation)
        if len(args) == 2:
            return ResolvedAnnotation(EditorKind.DICT, tuple(args), optional)
    return ResolvedAnnotation(EditorKind.RAW, optional=optional)


def _union_members(annotation):
    """Return union member types, or None if not a union."""
    if isinstance(annotation, types.UnionType):
        return list(typing.get_args(annotation))
    if typing.get_origin(annotation) is typing.Union:
        return list(typing.get_args(annotation))
    return None


def signature_params(cls) -> list:
    """[(name, annotation, required)] for a class __init__, excluding self."""
    try:
        signature = inspect.signature(cls.__init__)
    except (TypeError, ValueError):
        return []
    try:
        # Resolves quoted annotations (e.g. damage_roll: "WeaponsDamageRolls")
        # that inspect.signature leaves as strings.
        hints = typing.get_type_hints(cls.__init__)
    except Exception:
        hints = {}
    params = []
    for name, param in signature.parameters.items():
        if name == "self" or param.kind in (
            inspect.Parameter.VAR_POSITIONAL,
            inspect.Parameter.VAR_KEYWORD,
        ):
            continue
        annotation = (
            param.annotation
            if param.annotation is not inspect.Parameter.empty
            else None
        )
        annotation = hints.get(name, annotation)
        params.append((name, annotation, param.default is inspect.Parameter.empty))
    return params


_registry = None


def get_registry() -> Registry:
    global _registry
    if _registry is None:
        _registry = Registry()
    return _registry
