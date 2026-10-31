"""Search filtering for the categorized pickers (rules, features, spells)."""

from typing import Any, Callable

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QTreeWidgetItem


def first_visible_item(
    category_items: dict[str, QTreeWidgetItem],
) -> QTreeWidgetItem | None:
    """The first entry the search left showing, categories in their order."""
    for cat_item in category_items.values():
        for i in range(cat_item.childCount()):
            child = cat_item.child(i)
            if child is not None and not child.isHidden():
                return child
    return None


def filter_category_tree(
    category_items: dict[str, QTreeWidgetItem],
    query: str,
    matches: Callable[[Any, str], bool],
) -> None:
    """Hide every child whose UserRole payload doesn't match `query` (already
    stripped and lowercased by the caller), hide categories left empty, and
    while a query is active expand only the categories that still have hits."""
    for cat_item in category_items.values():
        any_visible = False
        for i in range(cat_item.childCount()):
            child = cat_item.child(i)
            assert child is not None, i
            visible = matches(child.data(0, Qt.ItemDataRole.UserRole), query)
            child.setHidden(not visible)
            any_visible = any_visible or visible
        cat_item.setHidden(not any_visible)
        if query:
            cat_item.setExpanded(any_visible)
