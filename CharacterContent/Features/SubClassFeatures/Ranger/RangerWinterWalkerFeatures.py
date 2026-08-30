
from Core.Definitions import CharacterClass, DamageType, RANGER_HIT_DIE, MAX_ABILITY_MODIFIER
from CharacterContent.Features.Core.BaseFeatures import Feature, FeatureUses, FeatureActivation, ActionType, RegainedOn, FeatureTarget
from CharacterContent.Features.Core.Improvements import DamageResistance
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class FrigidExplorer(Feature):
    def __init__(self):
        super().__init__(name="Frigid Explorer", origin="Winter Walker Ranger Level 3", usage_tags=["buff", "damage"])
        self._resistance = DamageResistance(DamageType.COLD, self.name)

    def apply(self, character_stat_block: CharacterStatBlock):
        self._resistance.apply(character_stat_block)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain the following benefits.\n"
            "Biting Cold. Damage from your weapon attacks, Ranger spells, and Ranger features ignores Resistance to Cold damage.\n"
            "Frost Resistance. You have Resistance to Cold damage.\n"
            "Polar Strikes. When you hit a creature with an attack roll using a weapon, you can deal an extra 1d4 Cold damage to the target, which can take this extra damage only once per turn. When you reach Ranger level 11, this extra damage increases to 1d6."
        )
        return description


class HuntersRime(Feature):
    def __init__(self):
        super().__init__(name="Hunter's Rime", origin="Winter Walker Ranger Level 3", usage_tags=["heal", "control"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Ice rimes you and your prey, protecting you and hindering them. When you cast Hunter's Mark, you gain Temporary Hit Points equal to 1d10 plus your Ranger level.\n"
            "Additionally, while a creature is marked by your Hunter's Mark, it can't take the Disengage action."
        )
        return description


class WinterWalkerSpells(Feature):
    def __init__(self):
        super().__init__(
            name="Winter Walker Spells", origin="Winter Walker Ranger Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you reach a Ranger level specified in the Winter Walker Spells table, you thereafter always have the listed spells prepared.\n"
            "Winter Walker Spells\n"
            "Ranger Level	Spells\n"
            "3	Ice Knife\n"
            "5	Hold Person\n"
            "9	Remove Curse\n"
            "13	Ice Storm\n"
            "17	Cone of Cold"
        )
        return description


class FortifyingSoul(Feature):
    def __init__(self):
        super().__init__(name="Fortifying Soul", origin="Winter Walker Ranger Level 7", activation=FeatureActivation(action_type=ActionType.ACTION, duration="1 Hour"), usage_tags=["heal", "buff"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your experience surviving harrowing environments allows you to bolster your allies in addition to yourself. As a Magic action, choose a number of creatures you can see equal to your Wisdom modifier (minimum of one). Each chosen creature regains Hit Points equal to 1d10 plus your Ranger level and has Advantage on saving throws to avoid or end the Frightened condition for 1 hour.\n"
            "Once you use this feature, you can't use it again until you finish a Long Rest."
        )
        return description

    def get_table_description(self, character_stat_block: CharacterStatBlock) -> list[tuple[str, str]]:
        wis_mod = character_stat_block.get_wisdom_modifier()
        ranger_level = character_stat_block.get_class_level(CharacterClass.RANGER)
        targets = max(1, wis_mod)
        healing = f"1d10 + {ranger_level}"
        return [
            ("Action", "Magic action"),
            ("Targets", f"Up to {targets} creatures"),
            ("Healing", healing),
            ("Secondary Effect", "Advantage on Frightened saves for 1 hour"),
            ("Recharge", "Long Rest"),
        ]



    def regained_on(self, character_stat_block: CharacterStatBlock) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def target(self, character_stat_block: CharacterStatBlock) -> "FeatureTarget | None":
        return FeatureTarget.ALLY
class ChillingRetribution(Feature):
    def __init__(self):
        super().__init__(
            name="Chilling Retribution", origin="Winter Walker Ranger Level 11", activation=FeatureActivation(action_type=ActionType.REACTION, duration="Until End of Your Next Turn"), usage_tags=["control"], uses=FeatureUses(max_uses=MAX_ABILITY_MODIFIER, regain_all_on="long rest", current_formula="Current amount: equal to your Wisdom modifier.")
        )

    def calculate_dc(self, character_stat_block: CharacterStatBlock) -> int:
        return character_stat_block.calculate_difficulty_class()


    def regained_on(self, character_stat_block: CharacterStatBlock) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def target(self, character_stat_block: CharacterStatBlock) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY

    def number_of_uses(self, character_stat_block: CharacterStatBlock) -> int:
        return max(1, character_stat_block.get_wisdom_modifier())

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When a creature hits you with an attack roll, you can take a Reaction to force the creature to make a Wisdom saving throw against your spell save DC. On a failed save, the target has the Stunned condition until the end of your next turn. While the target is Stunned, its Speed is reduced to 0 feet.\n"
            "You can use this feature a number of times equal to your Wisdom modifier (minimum of once), and you regain all expended uses when you finish a Long Rest."
        )
        return description

    def get_table_description(self, character_stat_block: CharacterStatBlock) -> list[tuple[str, str]]:
        uses = self.number_of_uses(character_stat_block)
        return [
            ("Trigger", "Creature hits you with attack roll"),
            ("Action", "Reaction"),
            ("Save", "Wisdom save vs. spell save DC"),
            ("Effect on Failure", "Stunned until end of your next turn (Speed 0)"),
            ("Uses", f"{uses} per Long Rest"),
        ]


class FrozenHaunt(Feature):
    def __init__(self):
        super().__init__(name="Frozen Haunt", origin="Winter Walker Ranger Level 15", activation=FeatureActivation(range="15-Foot Emanation"), usage_tags=["damage", "buff"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you cast Hunter's Mark, you can adopt a ghostly, snowy form. This form lasts until the spell ends, and while you are in this form, you gain the following benefits. Once you use this feature, you can't use it again until you finish a Long Rest unless you expend a level 4+ spell slot (no action required).\n"
            "Frozen Soul. You have Immunity to Cold damage. When you first adopt this form and at the start of each of your subsequent turns, each creature of your choice in a 15-foot Emanation originating from you takes 2d4 Cold damage.\n"
            "Partially Incorporeal. You have Immunity to the Grappled, Prone, and Restrained conditions. You can move through creatures and objects as if they were Difficult Terrain, but you take 1d10 Force damage if you end your turn inside a creature or an object. If the form ends while you are inside a creature or an object, you are shunted to the nearest unoccupied space."
        )
        return description

    def target(self, character_stat_block: CharacterStatBlock) -> "FeatureTarget | None":
        return FeatureTarget.AREA
