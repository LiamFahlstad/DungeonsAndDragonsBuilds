"""Loads Combat/rules.json into structured, searchable Rule objects.

To add or edit a rule, just edit rules.json directly -- each entry is
{"name": ..., "category": ..., "body": ...}. "category" is optional and
defaults to "General" if omitted.
"""

import json
from dataclasses import dataclass
from pathlib import Path

RULES_FILE = Path(__file__).parent / "rules.json"

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


def load_rules() -> list[Rule]:
    entries = json.loads(RULES_FILE.read_text(encoding="utf-8"))
    rules = [
        Rule(
            name=entry["name"],
            category=entry.get("category") or DEFAULT_CATEGORY,
            body=entry["body"],
        )
        for entry in entries
    ]
    return sorted(rules, key=lambda r: r.name.lower())


def group_by_category(rules: list[Rule]) -> dict[str, list[Rule]]:
    grouped: dict[str, list[Rule]] = {}
    for rule in rules:
        grouped.setdefault(rule.category, []).append(rule)
    return dict(
        sorted(grouped.items(), key=lambda kv: (kv[0] == DEFAULT_CATEGORY, kv[0]))
    )
