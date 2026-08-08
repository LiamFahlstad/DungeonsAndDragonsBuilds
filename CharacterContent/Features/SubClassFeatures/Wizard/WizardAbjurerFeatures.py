import Core.Definitions as Definitions
from Core.Definitions import Ability, WIZARD_HIT_DIE
from CharacterContent.Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class AbjurationSavant(Feature):
    def __init__(self):
        super().__init__(name="Abjuration Savant", origin="Abjurer Wizard Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Choose two Wizard spells from the Abjuration school, each of which must be no higher than level 2, and add them to your spellbook for free.\n"
            "In addition, whenever you gain access to a new level of spell slots in this class, you can add one Wizard spell from the Abjuration school to your spell book for free. The chosen spell must be of a level for which you have spell slots."
        )
        return description


class ArcaneWard(Feature):
    def __init__(self):
        super().__init__(name="Arcane Ward", origin="Abjurer Wizard Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        int_mod = character_stat_block.get_ability_modifier(Ability.INTELLIGENCE)
        description = (
            f"You can weave magic around yourself for protection. When you cast an Abjuration spell with a spell slot, you can simultaneously use a strand of the spell's magic to create a magical ward on yourself that lasts until you finish a Long Rest. The ward has a Hit Point maximum equal to twice your Wizard level plus your Intelligence modifier ({int_mod}). Whenever you take damage, the ward takes the damage instead, and if you have any Resistances or Vulnerabilities, apply them before reducing the ward's Hit Points. If the damage reduces the ward to 0 Hit Points, you take any remaining damage. While the ward has 0 Hit Points, it can't absorb damage, but its magic remains.\n"
            "Whenever you cast an Abjuration spell with a spell slot, the ward regains a number of Hit Points equal to twice the level of the spell slot. Alternatively, as a Bonus Action, you can expend a spell slot, and the ward regains a number of Hit Points equal to twice the level of the spell slot expended.\n"
            "Once you create the ward, you can't create it again until you finish a Long Rest."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        wizard_level = character_stat_block.get_class_level(
            Definitions.CharacterClass.WIZARD
        )
        int_mod = character_stat_block.get_ability_modifier(Ability.INTELLIGENCE)
        max_hp = 2 * wizard_level + int_mod
        return [
            ("Ward HP Maximum", f"{max_hp} (2 × Wizard level + INT mod)"),
            ("Restoration", "Cast abjuration spell OR Bonus Action + spell slot (2× slot level HP)"),
            ("Duration", "Until Long Rest"),
            ("Usage", "Once per Long Rest"),
        ]


class ProjectedWard(Feature):
    def __init__(self):
        super().__init__(name="Projected Ward", origin="Abjurer Wizard Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When a creature that you can see within 30 feet of yourself takes damage, you can take a Reaction to cause your Arcane Ward to absorb that damage. If this damage reduces the ward to 0 Hit Points, the warded creature takes any remaining damage. If the creature has any Resistances or Vulnerabilities, apply them before reducing the ward's Hit Points."
        return description


class SpellBreaker(Feature):
    def __init__(self):
        super().__init__(name="Spell Breaker", origin="Abjurer Wizard Level 10")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You always have the Counterspell and Dispel Magic spells prepared. In addition, you can cast Dispel Magic as a Bonus Action, and you can add your Proficiency Bonus to its ability check.\n"
            "When you cast either spell with a spell slot, that slot isn't expended if the spell fails to stop a spell."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Spells Prepared", "Counterspell, Dispel Magic (always)"),
            ("Dispel Magic Action", "Bonus Action (instead of Action)"),
            ("Dispel Magic Bonus", "Add Proficiency Bonus to ability check"),
            ("Slot Efficiency", "Slots not expended if spell fails to stop a spell"),
        ]


class SpellResistance(Feature):
    def __init__(self):
        super().__init__(name="Spell Resistance", origin="Abjurer Wizard Level 14")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You have Advantage on saving throws against spells, and you have Resistance to the damage of spells."
        return description
