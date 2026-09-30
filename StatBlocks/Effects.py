from StatBlocks.AbilityRequirements import AbilityRequirements
from StatBlocks.AbilityScores import AbilityScores
from StatBlocks.ArmorClass import ArmorClass
from StatBlocks.CarryingCapacity import CarryingCapacity
from StatBlocks.ClassLevels import ClassLevels
from StatBlocks.Defenses import Defenses
from StatBlocks.EquipmentTraining import EquipmentTraining
from StatBlocks.HitPoints import HitPoints
from StatBlocks.Initiative import Initiative
from StatBlocks.Languages import Languages
from StatBlocks.SavingThrows import SavingThrows
from StatBlocks.Senses import Senses
from StatBlocks.Skills import Skills
from StatBlocks.Speed import Speed
from StatBlocks.Spellcasting import Spellcasting
from StatBlocks.WeaponBonuses import WeaponBonuses
from StatBlocks.WornArmor import WornArmor


class Effects:
    """Everything a Character's features, armor, weapons, items and fighting
    styles record, one part per concern (StatBlocks/*.py). Internal to
    Character: it builds a fresh one from its sources whenever they change
    (Character._get_effects) and answers every query from it.

    Each part owns its own state and the queries on it; see
    Notes/feature-application-model.md. Every part is always present, even
    when empty. Abilities, speed and spellcasting start from the character's
    build choices (base scores, species speed, class spellcasting ability);
    every other part starts empty, because every proficiency, expertise and
    bonus arrives as an effect (e.g. ClassProficiencies, ClassSkillChoice,
    FreeBackgroundSkillProficiency)."""

    def __init__(
        self, abilities: AbilityScores, base_speed: int, spellcasting: Spellcasting
    ):
        self.abilities = abilities
        self.speed = Speed(base_speed)
        self.spellcasting = spellcasting
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

    def validate(self, class_levels: ClassLevels) -> None:
        """Check every recorded requirement against the complete set of
        effects: expertise needs proficiency, ability minimums (an armor's
        Strength, multiclass prerequisites) need the scores."""
        self.skills.validate()
        self.ability_requirements.validate(self.abilities, class_levels)
