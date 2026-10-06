"""Granted features and the extension tree they form.

A feature is granted plainly (a card of its own) or as an extension of
another feature (a rider or upgrade shown on the parent's card). Extensions
are declared, not attached: ExtensionTree finds each extension's parent from
the complete set of grants, so parent and extension may be granted in either
order.
"""

from enum import Enum
from typing import Optional

import attr

from Model.Records.GrantStamp import GrantStamp
from Model.Sources import GrantedFeature


class IfParentMissing(Enum):
    """What happens to an extension whose parent isn't granted."""

    # The build is wrong: raise.
    ERROR = "error"
    # Leave it out: an upgrade to whichever of two choices was made.
    DROP = "drop"
    # Show it as a feature of its own.
    STANDALONE = "standalone"


@attr.s(frozen=True, auto_attribs=True, eq=False)
class FeatureGrant:
    """One granted feature, stamped with where it came from.

    extends: None for a feature with a card of its own; otherwise the parent
    it extends. A feature type (matched with isinstance against the plain
    grants: exactly one must match) or a granted feature instance."""

    feature: GrantedFeature
    stamp: GrantStamp = GrantStamp()
    extends: type | GrantedFeature | None = None
    if_missing: IfParentMissing = IfParentMissing.ERROR


class ExtensionTree:
    """Which feature each extension extends, resolved from every grant."""

    def __init__(
        self,
        children: dict[int, list[GrantedFeature]],
        standalone: list[GrantedFeature],
    ):
        # {id(parent): [extension, ...]}, in grant order.
        self._children = children
        # Extensions whose parent isn't granted, shown as features of their
        # own (IfParentMissing.STANDALONE).
        self.standalone = standalone

    @classmethod
    def resolve(cls, feature_grants: list[FeatureGrant]) -> "ExtensionTree":
        """Raises if an extension's parent isn't granted (unless if_missing
        says otherwise), or if a parent type matches more than one plain
        grant."""
        plain_features = [g.feature for g in feature_grants if g.extends is None]
        granted_ids = {id(g.feature) for g in feature_grants}
        children: dict[int, list[GrantedFeature]] = {}
        standalone: list[GrantedFeature] = []
        for grant in feature_grants:
            if grant.extends is None:
                continue
            parent = _find_parent(grant, plain_features, granted_ids)
            if parent is not None:
                children.setdefault(id(parent), []).append(grant.feature)
            elif grant.if_missing == IfParentMissing.STANDALONE:
                standalone.append(grant.feature)
        return cls(children, standalone)

    def children_of(self, feature: GrantedFeature) -> list[GrantedFeature]:
        """The extensions granted onto `feature`, in grant order."""
        return self._children.get(id(feature), [])


def _find_parent(
    extension: FeatureGrant,
    plain_features: list[GrantedFeature],
    granted_ids: set[int],
) -> Optional[GrantedFeature]:
    """The granted feature `extension` extends, or None if it isn't granted
    and if_missing allows that."""
    parent = extension.extends
    if isinstance(parent, type):
        label = parent.__name__
        matches = [f for f in plain_features if isinstance(f, parent)]
    else:
        assert parent is not None
        label = parent.name
        matches = [parent] if id(parent) in granted_ids else []

    if len(matches) > 1:
        raise ValueError(
            f"{extension.feature.name} extends {label}, but {len(matches)} "
            "granted features match it - extend a specific instance instead."
        )
    if matches:
        return matches[0]
    if extension.if_missing == IfParentMissing.ERROR:
        raise ValueError(
            f"{extension.feature.name} extends {label}, which isn't granted."
        )
    return None
