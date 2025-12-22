from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Definitions import Ability, DiceRollCondition, Skill
from Features import Weapons, Maneuvers
from Features.BaseFeatures import CharacterFeature, TextFeature


WIZARD_HIT_DIE = 6


class RitualAdept(TextFeature):
    def __init__(self):
        super().__init__(name="Ritual Adept", origin="Wizard Level 1")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "You can cast any spell as a Ritual if that spell has the Ritual tag and the spell is in your spellbook. You needn't have the spell prepared, but you must read from the book to cast a spell in this way."


class ArcaneRecovery(TextFeature):
    def __init__(self):
        super().__init__(name="Ritual Adept", origin="Wizard Level 1")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:

        text = (
            "You can regain some of your magical energy by studying your spellbook. When you finish a Short Rest, you can choose expended spell slots to recover. The spell slots can have a combined level equal to no more than half your Wizard level (round up), and none of the slots can be level 6 or higher. For example, if you're a level 4 Wizard, you can recover up to two levels' worth of spell slots, regaining either one level 2 spell slot or two level 1 spell slots.\n"
            "Once you use this feature, you can't do so again until you finish a Long Rest."
        )
        return text


class Scholar(CharacterFeature):
    """While studying magic, you also specialized in another field of study. Choose one of the following skills in which you have proficiency: Arcana, History, Investigation, Medicine, Nature, or Religion. You have Expertise in the chosen skill."""

    def __init__(self, skill: Skill):
        if skill not in [
            Skill.ARCANA,
            Skill.HISTORY,
            Skill.INVESTIGATION,
            Skill.MEDICINE,
            Skill.NATURE,
            Skill.RELIGION,
        ]:
            raise ValueError(
                "Scholar skill must be one of: Arcana, History, Investigation, Medicine, Nature, Religion"
            )
        self.skill = skill

    def modify(self, character_stat_block: CharacterStatBlock):
        character_stat_block.skills.add_skill_expertise(self.skill)


class MemorizeSpell(TextFeature):
    def __init__(self):
        super().__init__(name="Memorize Spell", origin="Wizard Level 5")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "Whenever you finish a Short Rest, you can study your spellbook and replace one of the level 1+ Wizard spells you have prepared for your Spellcasting feature with another level 1+ spell from the book."


class SpellMastery(TextFeature):
    def __init__(self):
        super().__init__(name="Spell Mastery", origin="Wizard Level 18")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        text = (
            "You have achieved such mastery over certain spells that you can cast them at will. Choose a level 1 and a level 2 spell in your spellbook that have a casting time of an action. You always have those spells prepared, and you can cast them at their lowest level without expending a spell slot. To cast either spell at a higher level, you must expend a spell slot.\n"
            "Whenever you finish a Long Rest, you can study your spellbook and replace one of those spells with an eligible spell of the same level from the book.Rest, you can study your spellbook and replace one of those spells with an eligible spell of the same level from the book."
        )
        return text


class SignatureSpells(TextFeature):
    def __init__(self):
        super().__init__(name="Signature Spells", origin="Wizard Level 20")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "Choose two level 3 spells in your spellbook as your signature spells. You always have these spells prepared, and you can cast each of them once at level 3 without expending a spell slot. When you do so, you can't cast them in this way again until you finish a Short or Long Rest. To cast either spell at a higher level, you must expend a spell slot."


### Abjurer Subclass Features ###


class AbjurationSavant(TextFeature):
    def __init__(self):
        super().__init__(name="Abjuration Savant", origin="Abjurer Wizard Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Choose two Wizard spells from the Abjuration school, each of which must be no higher than level 2, and add them to your spellbook for free.\n"
            "In addition, whenever you gain access to a new level of spell slots in this class, you can add one Wizard spell from the Abjuration school to your spell book for free. The chosen spell must be of a level for which you have spell slots."
        )
        return description


class ArcaneWard(TextFeature):
    def __init__(self):
        super().__init__(name="Arcane Ward", origin="Abjurer Wizard Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        int_mod = character_stat_block.get_ability_modifier(Ability.INTELLIGENCE)
        description = (
            f"You can weave magic around yourself for protection. When you cast an Abjuration spell with a spell slot, you can simultaneously use a strand of the spell's magic to create a magical ward on yourself that lasts until you finish a Long Rest. The ward has a Hit Point maximum equal to twice your Wizard level plus your Intelligence modifier ({int_mod}). Whenever you take damage, the ward takes the damage instead, and if you have any Resistances or Vulnerabilities, apply them before reducing the ward's Hit Points. If the damage reduces the ward to O Hit Points, you take any remaining damage. While the ward has 0 Hit Points, it can't absorb damage, but its magic remains.\n"
            "Whenever you cast an Abjuration spell with a spell slot, the ward regains a number of Hit Points equal to twice the level of the spell slot. Alternatively, as a Bonus Action, you can expend a spell slot, and the ward regains a number of Hit Points equal to twice the level of the spell slot expended.\n"
            "Once you create the ward, you can't create it again until you finish a Long Rest."
        )
        return description


class ProjectedWard(TextFeature):
    def __init__(self):
        super().__init__(name="Projected Ward", origin="Abjurer Wizard Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When a creature that you can see within 30 feet of yourself takes damage, you can take a Reaction to cause your Arcane Ward to absorb that damage. If this damage reduces the ward to 0 Hit Points, the warded creature takes any remaining damage. If the creature has any Resistances or Vulnerabilities, apply them before reducing the ward's Hit Points."
        return description


class SpellBreaker(TextFeature):
    def __init__(self):
        super().__init__(name="Spell Breaker", origin="Abjurer Wizard Level 10")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You always have the Counterspell and Dispel Magic spells prepared. In addition, you can cast Dispel Magic as a Bonus Action, and you can add your Proficiency Bonus to its ability check.\n"
            "When you cast either spell with a spell slot, that slot isn't expended if the spell fails to stop a spell."
        )
        return description


class SpellResistance(TextFeature):
    def __init__(self):
        super().__init__(name="Spell Resistance", origin="Abjurer Wizard Level 14")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You have Advantage on saving throws against spells, and you have Resistance to the damage of spells."
        return description


### Bladesinger Subclass Features ###


class Bladesong(TextFeature):
    def __init__(self):
        super().__init__(name="Bladesong", origin="Bladesinger Wizard Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        int_mod = character_stat_block.get_ability_modifier(Ability.INTELLIGENCE)
        description = (
            "As a Bonus Action, you invoke an elven magic called the Bladesong, provided you aren't wearing armor or using a Shield.\n"
            "The Bladesong lasts for 1 minute and ends early if you have the Incapacitated condition, if you don armor or a Shield, or if you use two hands to make an attack with a weapon. You can dismiss the Bladesong at any time (no action required).\n"
            f"While the Bladesong is active, you gain the following benefits. You can invoke the Bladesong a number of times equal to your Intelligence modifier ({int_mod}, minimum of once), and you regain all expended uses when you finish a Long Rest. You regain one expended use when you use Arcane Recovery.\n"
            f" * Agility: You gain a bonus to your AC equal to your Intelligence modifier ({int_mod}, minimum of +1), and your Speed increases by 10 feet. In addition, you have Advantage on Dexterity (Acrobatics) checks.\n"
            f" * Bladework: Whenever you attack with a weapon with which you have proficiency, you can use your Intelligence modifier ({int_mod}) for the attack and damage rolls instead of using Strength or Dexterity.\n"
            f" * Focus: When you make a Constitution saving throw to maintain Concentration, you can add your Intelligence modifier ({int_mod}) to the total."
        )
        return description


class TrainingInWarAndSong(TextFeature):
    def __init__(self, skill: Skill):
        if skill not in [
            Skill.ACROBATICS,
            Skill.ATHLETICS,
            Skill.PERFORMANCE,
            Skill.PERSUASION,
        ]:
            raise ValueError(
                "Training in War and Song skill must be one of: Acrobatics, Athletics, Performance, Persuasion"
            )
        self.skill = skill
        super().__init__(
            name="Training in War and Song", origin="Bladesinger Wizard Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        character_stat_block.skills.add_skill_proficiency(self.skill)
        description = (
            "You gain proficiency with all Melee Martial weapons that don't have the Two-Handed or Heavy property. You can use a Melee weapon with which you have proficiency as a Spellcasting Focus for your Wizard spells.\n"
            "You also gain proficiency in one of the following skills of your choice: Acrobatics, Athletics, Performance, or Persuasion."
        )
        return description


class ExtraAttack(TextFeature):
    def __init__(self):
        super().__init__(name="Extra Attack", origin="Bladesinger Wizard Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can attack twice, instead of once, whenever you take the Attack action on your turn. Moreover, you can cast one of your Wizard cantrips that has a casting time of an action in place of one of those attacks."
        return description


class SongOfDefense(TextFeature):
    def __init__(self):
        super().__init__(name="Song of Defense", origin="Bladesinger Wizard Level 10")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you take damage while your Bladesong is active, you can take a Reaction to expend one spell slot and reduce the damage taken by an amount equal to five times the spell slot's level."
        return description


class SongOfVictory(TextFeature):
    def __init__(self):
        super().__init__(name="Song of Victory", origin="Bladesinger Wizard Level 14")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "After you cast a spell that has a casting time of an action, you can make one attack with a weapon as a Bonus Action."
        return description


### Diviner Subclass Features ###


class DivinationSavant(TextFeature):
    def __init__(self):
        super().__init__(name="Divination Savant", origin="Diviner Wizard Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Choose two Wizard spells from the Divination school, each of which must be no higher than level 2, and add them to your spellbook for free.\n"
            "In addition, whenever you gain access to a new level of spell slots in this class, you can add one Wizard spell from the Divination school to your spellbook for free. The chosen spell must be of a level for which you have spell slots."
        )
        return description


class Portent(TextFeature):
    def __init__(self):
        super().__init__(name="Portent", origin="Diviner Wizard Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Glimpses of the future begin to press on your awareness. Whenever you finish a Long Rest, roll two d20s and record the numbers rolled. You can replace any D20 Test made by you or a creature that you can see with one of these foretelling rolls. You must choose to do so before the roll, and you can replace a roll in this way only once per turn.\n"
            "Each foretelling roll can be used only once. When you finish a Long Rest, you lose any unused foretelling rolls."
        )
        return description


class ExpertDivination(TextFeature):
    def __init__(self):
        super().__init__(name="Expert Divination", origin="Diviner Wizard Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Casting Divination spells comes so easily to you that it expends only a fraction of your spellcasting efforts. When you cast a Divination spell using a level 2+ spell slot, you regain one expended spell slot. The slot you regain must be of a level lower than the slot you expended and can't be higher than level 5.\n"
        return description


class TheThirdEye(TextFeature):
    def __init__(self):
        super().__init__(name="The Third Eye", origin="Diviner Wizard Level 10")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can increase your powers of perception. As a Bonus Action, choose one of the following benefits, which lasts until you start a Short or Long Rest. You can't use this feature again until you finish a Short or Long Rest.\n"
            " * Darkvision: You gain Darkvision with a range of 120 feet.\n"
            " * Greater Comprehension: You can read any language.\n"
            " * See Invisibility: You can cast See Invisibility without expending a spell slot."
        )
        return description


class GreaterPortent(TextFeature):
    def __init__(self):
        super().__init__(name="Greater Portent", origin="Diviner Wizard Level 14")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "The visions in your dreams intensify and paint a more accurate picture in your mind of what is to come. Roll three d20s for your Portent feature rather than two."
        return description


### Evoker Subclass Features ###


class EvocationSavant(TextFeature):
    def __init__(self):
        super().__init__(name="Evocation Savant", origin="Evoker Wizard Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Choose two Wizard spells from the Evocation school, each of which must be no higher than level 2, and add them to your spellbook for free.\n"
            "In addition, whenever you gain access to a new level of spell slots in this class, you can add one Wizard spell from the Evocation school to your spellbook for free. The chosen spell must be of a level for which you have spell slots."
        )
        return description


class PotentCantrip(TextFeature):
    def __init__(self):
        super().__init__(name="Potent Cantrip", origin="Evoker Wizard Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Your damaging cantrips affect even creatures that avoid the brunt of the effect. When you cast a cantrip at a creature and you miss with the attack roll or the target succeeds on a saving throw against the cantrip, the target takes half the cantrip's damage (if any) but suffers no additional effect from the cantrip."
        return description


class SculptSpells(TextFeature):
    def __init__(self):
        super().__init__(name="Sculpt Spells", origin="Evoker Wizard Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can create pockets of relative safety within the effects of your evocations. When you cast an Evocation spell that affects other creatures that you can see, you can choose a number of them equal to 1 plus the spell's level. The chosen creatures automatically succeed on their saving throws against the spell, and they take no damage if they would normally take half damage on a successful save."
        return description


class EmpoweredEvocation(TextFeature):
    def __init__(self):
        super().__init__(name="Empowered Evocation", origin="Evoker Wizard Level 10")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        int_mod = character_stat_block.get_ability_modifier(Ability.INTELLIGENCE)
        description = f"Whenever you cast a Wizard spell from the Evocation school, you can add your Intelligence modifier ({int_mod}) to one damage roll of that spell."
        return description


class Overchannel(TextFeature):
    def __init__(self):
        super().__init__(name="Overchannel", origin="Evoker Wizard Level 14")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can increase the power of your spells. When you cast a Wizard spell with a spell slot of levels 1-5 that deals damage, you can deal maximum damage with that spell on the turn you cast it.\n"
            "The first time you do so, you suffer no adverse effect. If you use this feature again before you finish a Long Rest, you take 2d12 Necrotic damage for each level of the spell slot immediately after you cast it. This damage ignores Resistance and Immunity.\n"
            "Each time you use this feature again before finishing a Long Rest, the Necrotic damage per spell level increases by 1d12."
        )
        return description


### Illusionist Subclass Features ###


class IllusionSavant(TextFeature):
    def __init__(self):
        super().__init__(name="Illusion Savant", origin="Illusionist Wizard Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Choose two Wizard spells from the Illusion school, each of which must be no higher than level 2, and add them to your spellbook for free.\n"
            "In addition, whenever you gain access to a new level of spell slots in this class, you can add one Wizard spell from the Illusion school to your spellbook for free. The chosen spell must be of a level for which you have spell slots."
        )
        return description


class ImprovedIllusions(TextFeature):
    def __init__(self):
        super().__init__(name="Improved Illusions", origin="Illusionist Wizard Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can cast Illusion spells without providing Verbal components, and if an Illusion spell you cast has a range of 10+ feet, the range increases by 60 feet.\n"
            "You also know the Minor Illusion cantrip. If you already know it, you learn a different Wizard cantrip of your choice. The cantrip doesn't count against your number of cantrips known. You can create both a sound and an image with a single casting of Minor Illusion, and you can cast it as a Bonus Action."
        )
        return description


class PhantasmalCreatures(TextFeature):
    def __init__(self):
        super().__init__(
            name="Phantasmal Creatures", origin="Illusionist Wizard Level 6"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You always have the Summon Beast and Summon Fey spells prepared. Whenever you cast either spell, you can change its school to Illusion, which causes the summoned creature to appear spectral. You can cast the Illusion version of each spell without expending a spell slot, but casting it without a slot halves the creature's Hit Points. Once you cast either spell without a spell slot, you must finish a Long Rest before you can cast the spell in that way again."
        return description


class IllusorySelf(TextFeature):
    def __init__(self):
        super().__init__(name="Illusory Self", origin="Illusionist Wizard Level 10")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When a creature hits you with an attack roll, you can take a Reaction to interpose an illusory duplicate of yourself between the attacker and yourself. The attack automatically misses you, then the illusion dissipates.\n"
            "Once you use this feature, you can't use it again until you finish a Short or Long Rest. You can also restore your use of it by expending a level 2+ spell slot (no action required)."
        )
        return description


class IllusoryReality(TextFeature):
    def __init__(self):
        super().__init__(name="Illusory Reality", origin="Illusionist Wizard Level 14")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You have learned to weave shadow magic into your illusions to give them a semi-reality. When you cast an Illusion spell with a spell slot, you can choose one inanimate, nonmagical object that is part of the illusion and make that object real. You can do this on your turn as a Bonus Action while the spell is ongoing. The object remains real for 1 minute, during which it can't deal damage or give any conditions. For example, you can create an illusion of a bridge over a chasm and then make it real and cross it."
        return description
