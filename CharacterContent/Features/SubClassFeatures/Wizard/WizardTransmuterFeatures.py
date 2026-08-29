from Core.Definitions import Ability, WIZARD_HIT_DIE
from CharacterContent.Features.Core.BaseFeatures import Feature, FeatureUses
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class TransmutationSavant(Feature):
    def __init__(self):
        super().__init__(name="Transmutation Savant", origin="Transmuter Wizard Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Choose two Wizard spells from the Transmutation school, each of which must be no higher than level 2, and add them to your spellbook for free.\n"
            "In addition, whenever you gain access to a new level of spell slots in this class, you can add one Wizard spell from the Transmutation school to your spellbook for free. The chosen spell must be of a level for which you have spell slots."
        )
        return description


class TransmutersStone(Feature):
    def __init__(self):
        super().__init__(name="Transmuter's Stone", origin="Transmuter Wizard Level 3", usage_tags=["buff"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you finish a Long Rest, you can create a magic stone that lasts until you use this feature again. The stone is a Tiny object, and you can use it as a Spellcasting Focus for your Wizard spells. A creature with the stone in its possession gains proficiency in Constitution saving throws and one of the following benefits, which you choose when you create the stone. You can change the stone's benefit when you cast a Transmutation spell using a spell slot.\n"
            "    * Darkvision: The bearer gains Darkvision with a range of 60 feet or increases the range of its Darkvision by 60 feet.\n"
            "    * Resistance: The bearer gains Resistance to Acid, Cold, Fire, Lightning, Poison, or Thunder damage (your choice each time you choose this benefit).\n"
            "    * Speed: The bearer's Speed increases by 10 feet."
        )
        return description


class WondrousAlteration(Feature):
    def __init__(self):
        super().__init__(name="Wondrous Alteration", origin="Transmuter Wizard Level 3", usage_tags=["buff", "damage", "utility"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You always have the Alter Self spell prepared and can cast it once without expending a spell slot. You regain the ability to cast it in this way when you finish a Long Rest.\n"
            "While under the effects of Alter Self, you gain an additional benefit for each of its options.\n"
            "    * Aquatic Adaptation: While underwater, you can take the Dash action as a Bonus Action.\n"
            "    * Change Appearance: You have Advantage on Charisma (Deception) checks.\n"
            "    * Natural Weapons: The damage of your new growth increases to 2d6 damage of the type associated with the growth. You also have Advantage on Constitution saving throws to maintain Concentration."
        )
        return description


class EmpoweredTransmutation(Feature):
    def __init__(self):
        super().__init__(name="Empowered Transmutation", origin="Transmuter Wizard Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        int_mod = character_stat_block.get_ability_modifier(Ability.INTELLIGENCE)
        uses = max(1, int_mod)
        description = (
            "When you use a spell slot to cast a Transmutation spell that doesn't make an attack roll or force a saving throw, such as Fly or Magic Weapon, you can increase the spell's effective level by 1.\n"
            f"You can use this feature a number of times equal to your Intelligence modifier ({int_mod}) (minimum of once), and you regain all expended uses when you finish a Long Rest."
        )
        return StringUtils.add_boxes(description, uses, regain_all_on="long rest")


class PotentStone(Feature):
    def __init__(self):
        super().__init__(name="Potent Stone", origin="Transmuter Wizard Level 10", usage_tags=["buff"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your Transmuter's Stone is more versatile. When you create your Transmuter's Stone, you can choose up to two benefits. You can choose each option other than Resistance only once. If you choose Resistance twice, you must choose different damage types. You can change either or both benefits when you cast a Transmutation spell using a spell slot.\n"
            "In addition, the following are now among your benefit options for Transmuter's Stone.\n"
            "    * Mighty Build: The bearer has Advantage on Strength saving throws. The bearer also counts as one size larger when determining its carrying capacity.\n"
            "    * Tremorsense: The bearer gains Tremorsense with a range of 30 feet."
        )
        return description


class ShapeShifter(Feature):
    def __init__(self):
        super().__init__(name="Shape-Shifter", origin="Transmuter Wizard Level 10")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You always have the Polymorph spell prepared and can cast it once without expending a spell slot. You regain the ability to cast it in this way when you finish a Long Rest.\n"
            "In addition, when you target yourself with the spell, you can modify the spell to gain the benefits below. Once you modify the spell using this feature, you can't do so again until you finish a Long Rest.\n"
            "    * Game Statistics: In addition to retaining the features specified in the spell, you retain your memories and ability to communicate. You also retain your Intelligence, Wisdom, and Charisma scores; proficiencies; class features; and feats.\n"
            "    * Transmute Spells: While shape-shifted, you can cast spells, but only Transmutation spells that don't have a Material component that has a specified cost or that is consumed by the spell."
        )
        return description


class MasterTransmuter(Feature):
    def __init__(self):
        super().__init__(name="Master Transmuter", origin="Transmuter Wizard Level 14", action_type="action", usage_tags=["heal", "utility"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "While you carry your Transmuter's Stone, you can take a Magic action to consume the reserve of transmutation magic stored inside and choose one of the following benefits. After you use the stone in this way, it crumbles to dust. You can prevent the stone from crumbling by expending a level 7+ spell slot as part of the Magic action you take using this feature.\n"
            "    * Major Transformation: You can transmute one nonmagical object—no larger than a 10-foot Cube or eight connected 5-foot Cubes—into another nonmagical object of similar size and mass and of equal or lesser value. You must spend 10 minutes handling the object to transform it.\n"
            "    * Panacea: You touch a creature as part of this Magic action, and the target regains a number of Hit Points equal to half its Hit Point maximum (round down). The target is cured of all magical contagions, and any curses affecting the target are lifted, including the target's Attunement to a cursed item. If the target has the Poisoned or Petrified condition, those conditions end.\n"
            "    * Restore Life: You cast the Raise Dead spell without expending a spell slot, using the stone in place of the required Material components.\n"
            "    * Restore Youth: You touch one willing creature as part of this Magic action, and the target's Exhaustion level, if any, decreases to 0, and it permanently appears 3d10 years younger, to a minimum of young adulthood."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Action", "Magic action; stone crumbles after use unless prevented"),
            ("Cost", "Stone use (or expend level 7+ slot to prevent crumbling)"),
            ("Major Transformation", "Transmute nonmagical object (≤10 ft cube or 8×5 ft cubes) to similar object, 10 min handling"),
            ("Panacea", "Touch creature: regain half max HP, cure contagions/curses, end Poisoned/Petrified"),
            ("Restore Life", "Cast Raise Dead without slot, stone replaces components"),
            ("Restore Youth", "Touch willing: end Exhaustion, age permanently 3d10 years younger (min adulthood)"),
        ]
