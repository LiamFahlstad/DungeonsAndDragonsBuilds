"""CharacterSources: everything a player chose and was granted, as a builder
fills it in. Mutable while a character is being built; `Character(sources)`
(Model/Character.py) is the finished, read-only character worked out from
it. Builders write here through a Grants scope (Model/Grants.py), which stamps
every grant with where it came from.
"""

from typing import Optional

import attr

import Core.Definitions as Definitions
from Core.Definitions import Ability, CharacterClass
from Model.AbilityScores import AbilityScores
from Model.ClassLevels import ClassLevels
from Model.Content.Armor import AbstractArmor
from Model.Content.Effect import Effect
from Model.Content.Feature import Feature
from Model.Content.FightingStyle import FightingStyle
from Model.Content.Item import Item
from Model.Content.Weapon import AbstractWeapon
from Model.FeatureGrants import FeatureGrant, IfParentMissing
from Model.Inventory import Inventory
from Model.Records.GrantStamp import GrantStamp
from Model.Spells import SpellGrant, SpellReplacement


class SpellSource:
    """Shared `source=` labels for add_spell/add_cantrip (any free text works)."""

    CHOSEN = "Chosen spell"


@attr.s(auto_attribs=True)
class CharacterSources:
    character_name: Optional[str] = None
    is_example: bool = False
    # Levels, level-by-level history, base class and subclasses - see
    # Model/ClassLevels.py.
    class_levels: ClassLevels = attr.Factory(ClassLevels)
    # The player's ability scores before any increase - immutable; the final
    # scores are Character.get_ability_score() (see Model/AbilityIncreases.py).
    base_abilities: Optional[AbilityScores] = None
    # Walking speed given by the species, before any bonus.
    base_speed: Optional[int] = None
    size: Optional[Definitions.CreatureSize] = None

    # Every feature granted, plain or as an extension, each with its stamp.
    # Their order decides nothing: the sheet sorts them
    # (Presentation/FeatureOrder.py), and no stat depends on it.
    feature_grants: list[FeatureGrant] = attr.Factory(list)
    invocations: list[str] = attr.Factory(list)
    # Every spell and cantrip granted, and every declared replacement - see
    # Model/Spells.py. Character.spells is the resolved list.
    spell_grants: list[SpellGrant] = attr.Factory(list)
    spell_replacements: list[SpellReplacement] = attr.Factory(list)
    spell_casting_ability: Optional[Ability] = None
    # Spell slots set outright rather than worked out from caster levels.
    fixed_spell_slots: dict[int, int] = attr.Factory(dict)

    weapon_masteries: list[AbstractWeapon] = attr.Factory(list)
    fighting_styles: list[FightingStyle] = attr.Factory(list)
    # Armor, weapons and items, grouped into labeled entries (Starting
    # Equipment, then adventuring gear added later), plus starting and
    # current gold - see Model/Inventory.py.
    inventory: Inventory = attr.Factory(Inventory)
    experience_points: int = 0
    # Effects granted on their own rather than by a feature or gear: a test
    # or tool recording one improvement on a bare character (add_effect).
    extra_effects: list[Effect] = attr.Factory(list)

    def copy(self) -> "CharacterSources":
        """An independent copy: changing either one never changes the other.
        Features, spells and gear themselves are shared - nothing changes them
        once they're made."""
        return attr.evolve(
            self,
            class_levels=self.class_levels.copy(),
            feature_grants=list(self.feature_grants),
            invocations=list(self.invocations),
            spell_grants=list(self.spell_grants),
            spell_replacements=list(self.spell_replacements),
            fixed_spell_slots=dict(self.fixed_spell_slots),
            weapon_masteries=list(self.weapon_masteries),
            fighting_styles=list(self.fighting_styles),
            inventory=self.inventory.copy(),
            extra_effects=list(self.extra_effects),
        )

    # ── Class levels ──────────────────────────────────────────────────────────

    @property
    def character_level(self) -> int:
        return self.class_levels.character_level

    def get_class_level(self, character_class: CharacterClass) -> int:
        return self.class_levels.get_class_level(character_class)

    def record_class_level(
        self, character_level: int, character_class: CharacterClass
    ) -> None:
        self.class_levels.record_class_level(character_level, character_class)

    def set_class_level(self, character_class: CharacterClass, level: int) -> None:
        """Set the character's total level in `character_class` (a builder
        resuming a class states the class's final total level)."""
        self.class_levels.level_per_class[character_class] = level

    # ── Features ─────────────────────────────────────────────────────────────

    def add_feature(
        self,
        feature: Feature,
        *,
        stamp: GrantStamp,
        extends: type | Feature | None = None,
        if_missing: IfParentMissing = IfParentMissing.ERROR,
    ) -> None:
        """Grant `feature` - or, with `extends`, grant it as an extension of
        that feature (a type, or a feature instance): see FeatureGrant.
        `stamp` says where it's granted from; builders grant through a Grants
        scope (Model/Grants.py), which stamps it."""
        if extends is None and if_missing != IfParentMissing.ERROR:
            raise ValueError("if_missing only applies with extends=.")
        self.feature_grants.append(FeatureGrant(feature, stamp, extends, if_missing))

    def add_fighting_style(self, fighting_style: FightingStyle) -> None:
        self.fighting_styles.append(fighting_style)

    def add_weapon_mastery(self, weapon: AbstractWeapon) -> None:
        self.weapon_masteries.append(weapon)

    def add_invocation(self, invocation: str) -> None:
        self.invocations.append(invocation)

    def add_effect(self, effect: Effect) -> None:
        """Grant an effect on its own (anything with apply(effects)), for a
        test or tool recording one improvement on a bare character."""
        self.extra_effects.append(effect)

    # ── Spells ───────────────────────────────────────────────────────────────

    def add_spell(
        self,
        spell: str,
        spell_casting_ability: Optional[Ability] = None,
        additional_ruling: Optional[str] = None,
        source: Optional[str] = None,
        *,
        stamp: GrantStamp,
    ) -> None:
        """Grant a spell. `source` is a free-text label for the sheet ("Chosen
        spell"); `stamp` says where it's granted from (builders grant through
        a Grants scope, Model/Grants.py). The same spell from two different
        grants is listed for each; twice from one grant fails validate()."""
        self.spell_grants.append(
            SpellGrant(
                name=spell,
                ability=self._resolve_spell_casting_ability(spell_casting_ability),
                ruling=additional_ruling,
                grant_level=stamp.level,
                granted_by=stamp.granted_by,
                source=source,
            )
        )

    def add_cantrip(
        self,
        cantrip: str,
        spell_casting_ability: Optional[Ability] = None,
        additional_ruling: Optional[str] = None,
        source: Optional[str] = None,
        *,
        stamp: GrantStamp,
    ) -> None:
        self.add_spell(
            cantrip, spell_casting_ability, additional_ruling, source, stamp=stamp
        )

    def replace_spells(self, replace_spells: dict[str, str]) -> None:
        for old_spell, new_spell in replace_spells.items():
            self.replace_spell(old_spell, new_spell)

    def replace_spell(
        self,
        old_spell: str,
        new_spell: str,
        new_spell_ability: Optional[Ability] = None,
        new_additional_ruling: Optional[str] = None,
    ) -> None:
        """Declare that every grant of `old_spell` is `new_spell` instead
        (resolved when the spells are read, so it may be declared before the
        old spell is granted). It keeps the old grant's level and label."""
        self.spell_replacements.append(
            SpellReplacement(
                old=old_spell,
                new=new_spell,
                ability=new_spell_ability,
                ruling=new_additional_ruling,
            )
        )

    def _resolve_spell_casting_ability(
        self, spell_casting_ability: Optional[Ability]
    ) -> Ability:
        if spell_casting_ability is not None:
            return spell_casting_ability
        if self.spell_casting_ability is None:
            raise ValueError(
                "Spell casting ability must be provided if not already set."
            )
        return self.spell_casting_ability

    # ── Gear outside starting equipment and adventuring gear ─────────────────

    def add_armor(self, armor: AbstractArmor) -> None:
        self.inventory.add_armor(armor)

    def add_weapon(self, weapon: AbstractWeapon) -> None:
        # Proficiency isn't decided here: the weapon works it out on read
        # (AbstractWeapon.is_proficient).
        self.inventory.add_weapon(weapon)

    def add_item(self, item: Item, quantity: int = 1) -> None:
        self.inventory.add_item(item, quantity)
