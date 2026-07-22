from Core.Definitions import ARTIFICER_HIT_DIE
from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class ArmorerToolsOfTheTrade(Feature):
    def __init__(self):
        super().__init__(name="Tools of the Trade", origin="Armorer Artificer Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you adopt this specialization at 3rd level, you gain proficiency with heavy armor. You also gain proficiency with smith's tools. If you already have this tool proficiency, you gain proficiency with one other type of artisan's tools of your choice."
        return description


class ArmorerSpells(Feature):
    def __init__(self):
        super().__init__(name="Armorer Spells", origin="Armorer Artificer Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Starting at 3rd level, you always have certain spells prepared after you reach particular levels in this class, as shown in the Armorer Spells table. These spells count as artificer spells for you, but they don't count against the number of artificer spells you prepare.\n"
            "Armorer Spells\n"
            "Artificer Level	Armorer Spells\n"
            "3rd	Magic Missile, Thunderwave\n"
            "5th	Mirror Image, Shatter\n"
            "9th	Hypnotic Pattern, Lightning Bolt\n"
            "13th	Fire Shield, Greater Invisibility\n"
            "17th	Passwall, Wall of Force"
        )
        return description


class ArcaneArmor(Feature):
    def __init__(self):
        super().__init__(name="Arcane Armor", origin="Armorer Artificer Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Beginning at 3rd level, your metallurgical pursuits have led to you making armor a conduit for your magic. As an action, you can turn a suit of armor you are wearing into Arcane Armor, provided you have smith's tools in hand.\n"
            "You gain the following benefits while wearing this armor.\n"
            "If the armor normally has a Strength requirement, the arcane armor lacks this requirement for you.\n"
            "You can use the arcane armor as a spellcasting focus for your artificer spells.\n"
            "The armor attaches to you and can't be removed against your will. It also expands to cover your entire body, although you can retract or deploy the helmet as a bonus action. The armor replaces any missing limbs, functioning identically to a body part it is replacing.\n"
            "You can doff or don the armor as an action.\n"
            "The armor continues to be Arcane Armor until you don another suit of armor or you die."
        )
        return description


class ArmorModel(Feature):
    def __init__(self):
        super().__init__(name="Armor Model", origin="Armorer Artificer Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Beginning at 3rd level, you can customize your Arcane Armor. When you do so, choose one of the following armor models: Guardian or Infiltrator. The model you choose gives you special benefits while you wear it.\n"
            "Each model includes a special weapon. When you attack with that weapon, you can add your Intelligence modifier, instead of Strength or Dexterity, to the attack and damage rolls.\n"
            "You can change the armor's model whenever you finish a short or long rest, provided you have smith's tools in hand.\n"
            "Guardian. You design your armor to be in the front line of conflict. It has the following features.\n"
            "Thunder Gauntlets. Each of the armor's gauntlets counts as a simple melee weapon while you aren't holding anything in it, and it deals 1d8 thunder damage on a hit. A creature hit by the gauntlet has disadvantage on attack rolls against targets other than you until the start of your next turn, as the armor magically emits a distracting pulse when the creature attacks someone else.\n"
            "Defensive Field. As a bonus action, you can gain temporary hit points equal to your level in this class, replacing any temporary hit points you already have. You lose these temporary hit points if you doff the armor. You can use this bonus action a number of times equal to your proficiency bonus, and you regain all expended uses when you finish a long rest.\n"
            "Infiltrator. You customize your armor for subtle undertakings. It has the following features.\n"
            "Lightning Launcher. A gemlike node appears on one of your armored fists or on the chest (your choice). It counts as a simple ranged weapon, with a normal range of 90 feet and a long range of 300 feet, and it deals 1d6 lightning damage on a hit. Once on each of your turns when you hit a creature with it, you can deal an extra 1d6 lightning damage to that target.\n"
            "Powered Steps. Your walking speed increases by 5 feet.\n"
            "Dampening Field. You have advantage on Dexterity (Stealth) checks. If the armor normally imposes disadvantage on such checks, the advantage and disadvantage cancel each other, as normal."
        )
        return description


class ArmorerExtraAttack(Feature):
    def __init__(self):
        super().__init__(name="Extra Attack", origin="Armorer Artificer Level 5")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Starting at 5th level, you can attack twice, rather than once, whenever you take the Attack action on your turn."
        return description


class ArmorModifications(Feature):
    def __init__(self):
        super().__init__(name="Armor Modifications", origin="Armorer Artificer Level 9")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "At 9th level, you learn how to use your artificer infusions to specially modify your Arcane Armor. That armor now counts as separate items for the purposes of your Infuse Item feature: armor (the chest piece), boots, helmet, and the armor's special weapon. Each of those items can bear one of your infusions, and the infusions transfer over if you change your armor's model with the Armor Model feature. In addition, the maximum number of items you can infuse at once increases by 2, but those extra items must be part of your Arcane Armor."
        )
        return description


class PerfectedArmor(Feature):
    def __init__(self):
        super().__init__(name="Perfected Armor", origin="Armorer Artificer Level 15")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "At 15th level, your Arcane Armor gains additional benefits based on its model, as shown below.\n"
            "Guardian. When a Huge or smaller creature you can see ends its turn within 30 feet of you, you can use your reaction to magically force it to make a Strength saving throw against your spell save DC. On a failed save, you pull the creature up to 25 feet directly to an unoccupied space. If you pull the target to a space within 5 feet of you, you can make a melee weapon attack against it as part of this reaction.\n"
            "You can use this reaction a number of times equal to your proficiency bonus, and you regain all expended uses of it when you finish a long rest.\n"
            "Infiltrator. Any creature that takes lightning damage from your Lightning Launcher glimmers with magical light until the start of your next turn. The glimmering creature sheds dim light in a 5-foot radius, and it has disadvantage on attack rolls against you, as the light jolts it if it attacks you. In addition, the next attack roll against it has advantage, and if that attack hits, the target takes an extra 1d6 lightning damage."
        )
        return description
