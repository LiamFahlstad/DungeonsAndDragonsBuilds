import Core.Definitions as Definitions
from CharacterContent.Features.ClassFeatures.Monk.MonkFeatures import LEVEL_TO_MARTIAL_ARTS_DIE
from CharacterContent.Features.Core.BaseFeatures import Feature, FeatureActivation
from CharacterContent.Items.Weapons import WeaponDamageRolls
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class RadiantSunBolt(Feature):
    def __init__(self):
        super().__init__(name="Radiant Sun Bolt", origin="Way of the Sun Soul Monk Level 3", activation=FeatureActivation(action_type="bonus_action", range="30 Feet"), usage_tags=["damage"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        monk_level = character_stat_block.get_class_level(Definitions.CharacterClass.MONK)
        martial_arts_die = LEVEL_TO_MARTIAL_ARTS_DIE.get(monk_level, WeaponDamageRolls.D4)
        description = (
            "You can hurl searing bolts of magical radiance.\n"
            "\n"
            "You gain a new attack option that you can use with the Attack action. This special attack is a ranged spell attack with a range of 30 feet. You are proficient with it, and you add your Dexterity modifier to its attack and damage rolls. "
            f"Its damage is radiant, and its damage die is a d4. This die changes as you gain monk levels, as shown in the Martial Arts column of the Monk table. At your current monk level, this die is {martial_arts_die.value}.\n"
            "\n"
            "When you take the Attack action on your turn and use this special attack as part of it, you can spend 1 ki point to make the special attack twice as a bonus action.\n"
            "\n"
            "When you gain the Extra Attack feature, this special attack can be used for any of the attacks you make as part of the Attack action."
        )
        return description


class SearingArcStrike(Feature):
    def __init__(self):
        super().__init__(name="Searing Arc Strike", origin="Way of the Sun Soul Monk Level 6", activation=FeatureActivation(action_type="bonus_action"), usage_tags=["damage"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        monk_level = character_stat_block.get_class_level(Definitions.CharacterClass.MONK)
        max_ki_spent = monk_level // 2
        description = (
            "You gain the ability to channel your ki into searing waves of energy. Immediately after you take the Attack action on your turn, you can spend 2 ki points to cast the Burning Hands spell as a bonus action.\n"
            "\n"
            f"You can spend additional ki points to cast Burning Hands as a higher level spell. Each additional ki point you spend increases the spell's level by 1. The maximum number of ki points (2 plus any additional points) that you can spend on the spell equals half your monk level ({max_ki_spent})."
        )
        return description

    def get_table_description(self, character_stat_block: CharacterStatBlock) -> list[tuple[str, str]]:
        monk_level = character_stat_block.get_class_level(Definitions.CharacterClass.MONK)
        max_ki_spent = monk_level // 2
        return [
            ("Trigger", "After you take the Attack action on your turn"),
            ("Action", "Bonus action"),
            ("Base Cost", "2 ki points"),
            ("Spell", "Burning Hands"),
            ("Upcasting", "+1 level per additional ki point"),
            ("Max Ki", f"Half monk level ({max_ki_spent})"),
        ]


class SearingSunburst(Feature):
    def __init__(self):
        super().__init__(name="Searing Sunburst", origin="Way of the Sun Soul Monk Level 11", activation=FeatureActivation(action_type="action", range="150 Feet (20-Foot-Radius Sphere)"), usage_tags=["damage"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain the ability to create an orb of light that erupts into a devastating explosion. As an action, you magically create an orb and hurl it at a point you choose within 150 feet, where it erupts into a sphere of radiant light for a brief but deadly instant.\n"
            "\n"
            "Each creature in that 20-foot-radius sphere must succeed on a Constitution saving throw or take 2d6 radiant damage. A creature doesn't need to make the save if the creature is behind total cover that is opaque.\n"
            "\n"
            "You can increase the sphere's damage by spending ki points. Each point you spend, up to a maximum of 3, increases the damage by 2d6."
        )
        return description

    def get_table_description(self, character_stat_block: CharacterStatBlock) -> list[tuple[str, str]]:
        return [
            ("Action", "Action"),
            ("Range", "150 feet (target point)"),
            ("Area", "20-foot-radius sphere"),
            ("Save", "Constitution"),
            ("Base Damage", "2d6 radiant (failed save)"),
            ("Extra Damage", "+2d6 per ki point (max 3 ki)"),
            ("Cover", "Total opaque cover negates save requirement"),
        ]


class SunShield(Feature):
    def __init__(self):
        super().__init__(name="Sun Shield", origin="Way of the Sun Soul Monk Level 17", activation=FeatureActivation(action_type="reaction", range="30 Feet"), usage_tags=["damage"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        wis_mod = character_stat_block.get_ability_modifier(Definitions.Ability.WISDOM)
        damage = 5 + wis_mod
        description = (
            "You become wreathed in a luminous, magical aura. You shed bright light in a 30-foot radius and dim light for an additional 30 feet. You can extinguish or restore the light as a bonus action.\n"
            "\n"
            f"If a creature hits you with a melee attack while this light shines, you can use your reaction to deal radiant damage to the creature. The radiant damage equals 5 + your Wisdom modifier ({damage})."
        )
        return description
