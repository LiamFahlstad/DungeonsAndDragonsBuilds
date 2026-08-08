from Core import Definitions
from Core.Definitions import Ability, WIZARD_HIT_DIE
from CharacterContent.Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class AbjurationSavant(Feature):
    def __init__(self):
        super().__init__(name="Abjuration Savant", origin="Abjuration Wizard Level 3", skippable_in_concise=True)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "The gold and time you must spend to copy an Abjuration spell into your spellbook is halved."
        return description


class ArcaneWard(Feature):
    def __init__(self):
        super().__init__(name="Arcane Ward", origin="Abjuration Wizard Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        int_mod = character_stat_block.get_ability_modifier(Ability.INTELLIGENCE)
        description = (
            f"You can weave magic around yourself for protection. When you cast an abjuration spell of 1st level or higher, you can simultaneously use a strand of the spell's magic to create a magical ward on yourself that lasts until you finish a long rest. The ward has hit points equal to twice your wizard level + your Intelligence modifier ({int_mod}). Whenever you take damage, the ward takes the damage instead. If this damage reduces the ward to 0 hit points, you take any remaining damage.\n"
            "While the ward has 0 hit points, it can't absorb damage, but its magic remains. Whenever you cast an abjuration spell of 1st level or higher, the ward regains a number of hit points equal to twice the level of the spell.\n"
            "Once you create the ward, you can't create it again until you finish a long rest."
        )
        return description

    def get_table_description(self, character_stat_block: CharacterStatBlock) -> list[tuple[str, str]]:
        wizard_level = character_stat_block.get_class_level(
            Definitions.CharacterClass.WIZARD
        )
        int_mod = character_stat_block.get_ability_modifier(Ability.INTELLIGENCE)
        ward_hp = 2 * wizard_level + int_mod
        return [
            ("Trigger", "Cast an abjuration spell of 1st level or higher"),
            ("Ward HP", f"2 × wizard level + Int modifier = {ward_hp}"),
            ("Protection", "Ward absorbs all damage until 0 HP, then you take remaining"),
            ("Recharge", "Regains HP equal to 2 × spell level when you cast abjuration spell"),
            ("Limit", "Once per long rest"),
        ]


class ProjectedWard(Feature):
    def __init__(self):
        super().__init__(name="Projected Ward", origin="Abjuration Wizard Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When a creature that you can see within 30 feet of you takes damage, you can use your reaction to cause your Arcane Ward to absorb that damage. If this damage reduces the ward to 0 hit points, the warded creature takes any remaining damage."
        return description


class ImprovedAbjuration(Feature):
    def __init__(self):
        super().__init__(name="Improved Abjuration", origin="Abjuration Wizard Level 10", skippable_in_concise=True)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you cast an abjuration spell that requires you to make an ability check as a part of casting that spell (as in Counterspell and Dispel Magic), you add your proficiency bonus to that ability check."
        return description


class SpellResistance(Feature):
    def __init__(self):
        super().__init__(name="Spell Resistance", origin="Abjuration Wizard Level 14", skippable_in_concise=True)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You have advantage on saving throws against spells.\n"
            "Furthermore, you have resistance against the damage of spells."
        )
        return description
