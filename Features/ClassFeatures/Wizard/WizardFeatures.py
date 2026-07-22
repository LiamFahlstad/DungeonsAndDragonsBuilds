from Core.Definitions import Skill, WIZARD_HIT_DIE
from Features.Core.BaseFeatures import Feature
from Features.Core.SubFeatures import SkillExpertiseChoice
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class RitualAdept(Feature):
    def __init__(self):
        super().__init__(name="Ritual Adept", origin="Wizard Level 1")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "You can cast any spell as a Ritual if that spell has the Ritual tag and the spell is in your spellbook. You needn't have the spell prepared, but you must read from the book to cast a spell in this way."


class ArcaneRecovery(Feature):
    def __init__(self):
        super().__init__(name="Arcane Recovery", origin="Wizard Level 1")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:

        text = (
            "You can regain some of your magical energy by studying your spellbook. When you finish a Short Rest, you can choose expended spell slots to recover. The spell slots can have a combined level equal to no more than half your Wizard level (round up), and none of the slots can be level 6 or higher. For example, if you're a level 4 Wizard, you can recover up to two levels' worth of spell slots, regaining either one level 2 spell slot or two level 1 spell slots.\n"
            "Once you use this feature, you can't do so again until you finish a Long Rest."
        )
        return text


class Scholar(Feature):
    SKILL_POOL = [
        Skill.ARCANA,
        Skill.HISTORY,
        Skill.INVESTIGATION,
        Skill.MEDICINE,
        Skill.NATURE,
        Skill.RELIGION,
    ]

    def __init__(self, skill: Skill):
        super().__init__(name="Scholar", origin="Wizard Level 2")
        self._expertise = SkillExpertiseChoice(
            [skill],
            self.SKILL_POOL,
            count=1,
            error_prefix="Scholar skill must be one of: Arcana, History, Investigation, Medicine, Nature, Religion",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return f"While studying magic, you specialized in {self._expertise.skills[0].value}. You have Expertise in it."

    def apply(self, character_stat_block: CharacterStatBlock):
        self._expertise.apply(character_stat_block)


class MemorizeSpell(Feature):
    def __init__(self):
        super().__init__(name="Memorize Spell", origin="Wizard Level 5")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "Whenever you finish a Short Rest, you can study your spellbook and replace one of the level 1+ Wizard spells you have prepared for your Spellcasting feature with another level 1+ spell from the book."


class SpellMastery(Feature):
    def __init__(self):
        super().__init__(name="Spell Mastery", origin="Wizard Level 18")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        text = (
            "You have achieved such mastery over certain spells that you can cast them at will. Choose a level 1 and a level 2 spell in your spellbook that have a casting time of an action. You always have those spells prepared, and you can cast them at their lowest level without expending a spell slot. To cast either spell at a higher level, you must expend a spell slot.\n"
            "Whenever you finish a Long Rest, you can study your spellbook and replace one of those spells with an eligible spell of the same level from the book."
        )
        return text


class SignatureSpells(Feature):
    def __init__(self):
        super().__init__(name="Signature Spells", origin="Wizard Level 20")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "Choose two level 3 spells in your spellbook as your signature spells. You always have these spells prepared, and you can cast each of them once at level 3 without expending a spell slot. When you do so, you can't cast them in this way again until you finish a Short or Long Rest. To cast either spell at a higher level, you must expend a spell slot."
