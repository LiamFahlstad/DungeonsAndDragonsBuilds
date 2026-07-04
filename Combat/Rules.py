"""Parses Combat/rules.txt into structured, searchable Rule objects.

rules.txt is a flattened glossary export: each rule is a short heading line
(optionally tagged "Name [Category]") followed by one or more body lines.
Some headings are just cross-reference stubs (a bare list of terms with no
body of their own, defined properly later in the file) -- those are dropped.
"""

import re
from dataclasses import dataclass
from pathlib import Path

RULES_FILE = Path(__file__).parent / "rules.txt"

_INTRO_MARKER = "Here are definitions of various rules."
_HEADING_MAX_LEN = 50
_HEADING_RE = re.compile(r"^(?P<name>.+?)\s*\[(?P<category>[^\]]+)\]$")
_BRACKET_RE = re.compile(r"\[[^\]]*\]")
_LOWERCASE_CONNECTORS = {"and", "or", "of", "the", "a", "an", "in", "on", "to"}

DEFAULT_CATEGORY = "General"


@dataclass(frozen=True)
class Rule:
    name: str
    category: str
    body: str

    def matches(self, query: str) -> bool:
        query = query.lower().strip()
        if not query:
            return True
        return query in self.name.lower() or query in self.body.lower()


def _is_heading(line: str) -> bool:
    """Heuristic: rule headings are short, Title Case standalone terms with no
    period -- as opposed to body/bullet lines, which are full (if unpunctuated)
    prose fragments that happen to be short too."""
    if not line or len(line) > _HEADING_MAX_LEN or "." in line:
        return False
    words = [w for w in _BRACKET_RE.sub("", line).split() if w]
    significant = [w for w in words if w.lower() not in _LOWERCASE_CONNECTORS]
    if not significant:
        return False
    capitalized = sum(1 for w in significant if w[0].isupper())
    return capitalized / len(significant) >= 0.8


def _split_name_category(heading: str) -> tuple[str, str]:
    match = _HEADING_RE.match(heading)
    if match:
        return match.group("name").strip(), match.group("category").strip()
    return heading.strip(), DEFAULT_CATEGORY


def _parse_entries(lines: list[str]) -> list[tuple[str, str, list[str]]]:
    entries: list[tuple[str, str, list[str]]] = []
    current_body: list[str] | None = None

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        if _is_heading(line):
            name, category = _split_name_category(line)
            current_body = []
            entries.append((name, category, current_body))
        elif current_body is not None:
            current_body.append(line)

    return entries


def load_rules() -> list[Rule]:
    """Parse rules.txt and return all rules with non-empty bodies, sorted by name.

    When a term appears more than once (cross-reference stubs vs. the real
    later definition), the last occurrence with a non-empty body wins.
    """
    text = RULES_FILE.read_text(encoding="utf-8")
    lines = text.splitlines()

    start = 0
    for i, line in enumerate(lines):
        if _INTRO_MARKER in line:
            start = i + 1
            break
    lines = lines[start:]

    rules: dict[str, Rule] = {}
    for name, category, body_lines in _parse_entries(lines):
        body = "\n\n".join(body_lines).strip()
        if not body:
            continue
        rules[name] = Rule(name=name, category=category, body=body)

    return sorted(rules.values(), key=lambda r: r.name.lower())


def group_by_category(rules: list[Rule]) -> dict[str, list[Rule]]:
    grouped: dict[str, list[Rule]] = {}
    for rule in rules:
        grouped.setdefault(rule.category, []).append(rule)
    return dict(
        sorted(grouped.items(), key=lambda kv: (kv[0] == DEFAULT_CATEGORY, kv[0]))
    )
