"""Ledger: everything a Character's effects record, one part per concern
(the other modules in this folder). The write side is LedgerWriter
(Model/Ledger/LedgerWriter.py)."""

from Core.Definitions import Ability
from Core.Rules import UNTRAINED_ARMOR_ABILITIES
from Model.Ledger.AbilityIncreases import AbilityIncreases
from Model.Ledger.AbilityRequirements import AbilityRequirements
from Model.Ledger.ArmorClass import ArmorClass
from Model.Ledger.CarryingCapacity import CarryingCapacity
from Model.Ledger.Defenses import Defenses
from Model.Ledger.EquipmentTraining import EquipmentTraining
from Model.Ledger.HitPoints import HitPoints
from Model.Ledger.Initiative import Initiative
from Model.Ledger.Languages import Languages
from Model.Ledger.SavingThrows import SavingThrows
from Model.Ledger.Senses import Senses
from Model.Ledger.Skills import Skills
from Model.Ledger.Speed import Speed
from Model.Ledger.Spellcasting import Spellcasting
from Model.Ledger.WeaponBonuses import WeaponBonuses
from Model.Ledger.WornArmor import WornArmor
from Model.View import CharacterView


class Ledger:
    """Everything a Character's features, armor, weapons, items and fighting
    styles record, one part per concern (Model/Ledger/*.py). Private to
    Character: it fills one once (Character._ledger) and answers every query
    from it. Effects record into it only through the write-only LedgerWriter
    (Model/Ledger/LedgerWriter.py), and only while the Character fills it.

    Each part owns its own state and the queries on it; see
    Notes/feature-application-model.md. Every part is always present, and
    starts empty: parts hold only what effects record, never a copy of a
    source (base scores, base speed and the spellcasting ability stay on the
    Character, and resolvers read them through the view)."""

    def __init__(self):
        self.ability_increases = AbilityIncreases()
        self.speed = Speed()
        self.spellcasting = Spellcasting()
        self.skills = Skills()
        self.saving_throws = SavingThrows()
        self.carrying_capacity = CarryingCapacity()
        self.armor_class = ArmorClass()
        self.worn_armor = WornArmor()
        self.hit_points = HitPoints()
        self.equipment_training = EquipmentTraining()
        self.languages = Languages()
        self.defenses = Defenses()
        self.senses = Senses()
        self.ability_requirements = AbilityRequirements()
        self.initiative = Initiative()
        self.weapon_bonuses = WeaponBonuses()

    # -- Rules that combine two parts ------------------------------------------
    # Armor training (2024 PHB): "If you wear armor and lack training with it,
    # you have Disadvantage on any D20 Test that involves Strength or
    # Dexterity, and you can't cast spells. If you use a Shield and lack
    # training with it, you don't gain its AC bonus." Worked out on read from
    # the worn armor and the training granted, so it doesn't matter which
    # applied first.

    def is_wearing_untrained_armor(self) -> bool:
        armor_type = self.worn_armor.body_armor_type
        return (
            armor_type is not None
            and armor_type not in self.equipment_training.armor_training
        )

    def has_shield_training(self) -> bool:
        return self.equipment_training.has_shield_training

    def has_untrained_armor_disadvantage(self, ability: Ability) -> bool:
        """Disadvantage on D20 Tests with `ability` from untrained armor."""
        return (
            self.is_wearing_untrained_armor() and ability in UNTRAINED_ARMOR_ABILITIES
        )

    def armor_warnings(self) -> list[str]:
        """Legal but bad armor choices the player should know about."""
        warnings = []
        armor_type = self.worn_armor.body_armor_type
        if self.is_wearing_untrained_armor() and armor_type is not None:
            warnings.append(
                f"Wearing {self.worn_armor.body_armor_name or 'armor'} without "
                f"{armor_type.value} armor training: "
                "Disadvantage on every D20 Test that involves Strength or "
                "Dexterity, and you can't cast spells."
            )
        if self.worn_armor.shield_wielded and not self.has_shield_training():
            warnings.append(
                "Wielding a Shield without Shield training: it grants no AC bonus."
            )
        return warnings

    def validate(self, view: CharacterView) -> None:
        """Check every recorded requirement against the complete set of
        effects: expertise needs proficiency, ability minimums (an armor's
        Strength, multiclass prerequisites) need the scores."""
        self.skills.validate()
        self.ability_requirements.validate(view)
