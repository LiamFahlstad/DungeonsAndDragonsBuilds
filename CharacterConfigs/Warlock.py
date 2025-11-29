from Definitions import Ability, Skill, CharacterClass, WarlockSubclass
from Features import GeneralFeats, OriginFeats
import CharacterSheetCreator
from Features import Armor
from Features import Backgrounds
from Features import FightingStyles
from Features import Weapons
from Features.ClassFeatures import WarlockFeatures
import StatBlocks

DATA = CharacterSheetCreator.CharacterSheetData()

##########################################
# ================ CHANGE ============== #
##########################################

# ================ GENERAL ============= #

DATA.character_name = "Greta"
DATA.character_class = CharacterClass.WARLOCK
DATA.level = 4
DATA.character_subclass = WarlockSubclass.THE_ARCHFEY
DATA.spell_casting_ability = Ability.CHARISMA
DATA.add_feature(WarlockFeatures.SpellSlots())

# ================ LEVEL 0 ============= #

# Distribute 15, 14, 13, 12, 10, 8 among your abilities.
DATA.abilities = StatBlocks.StandardArrayAbilitiesStatBlock(
    strength=8,
    dexterity=10,
    constitution=14,
    intelligence=12,
    wisdom=13,
    charisma=15,
)

# Choose two skills to be proficient in
DATA.skills = StatBlocks.WarlockSkillsStatBlock(
    proficiencies={
        Skill.ARCANA: True,
        Skill.DECEPTION: False,
        Skill.HISTORY: True,
        Skill.INTIMIDATION: False,
        Skill.INVESTIGATION: False,
        Skill.NATURE: False,
        Skill.RELIGION: False,
    }
)

# Leave as is: Paladin specific saving throws
DATA.saving_throws = StatBlocks.WarlockSavingThrowsStatBlock()

# Leave as is: Paladin specific combat stats
DATA.hit_die = WarlockFeatures.WARLOCK_HIT_DIE

DATA.add_feature(
    # Free background feature
    # Distribute +2 and +1 to two different ability scores
    # OR +1 to three different ability scores
    Backgrounds.FreeBackgroundAbilityBonus(
        [
            (Ability.CONSTITUTION, 1),
            (Ability.CHARISMA, 2),
        ]
    )
)

# Starting armor
DATA.add_armor(Armor.LeatherArmor())

# Starting weapons
DATA.add_weapon(Weapons.Dagger(player_is_proficient=True))
DATA.add_weapon(Weapons.LightCrossbow(player_is_proficient=True))

# Origin feat
DATA.add_feature(OriginFeats.Lucky())

# ================ LEVEL 1 ============= #
if DATA.level >= 1:
    # Prepared spells
    DATA.add_spell("Hex")
    DATA.add_spell("Charm Person")

    # Cantrips
    DATA.add_spell("Mage Hand")
    DATA.add_spell("Eldritch Blast")

    # Invocations
    DATA.add_invocation("Eldritch Mind")

# ================ LEVEL 2 ============= #
if DATA.level >= 2:
    # Prepared spells
    DATA.add_spell("Spider Climb")
    DATA.add_feature(WarlockFeatures.MagicalCunning())

    # Invocations
    DATA.add_invocation("Agonizing Blast")
    DATA.add_invocation("Repelling Blast")

# ================ LEVEL 3 ============= #
if DATA.level >= 3:
    # Prepared spells
    DATA.add_spell("Mirror Image")

    # Automatic feature
    if DATA.character_subclass == WarlockSubclass.THE_ARCHFEY:
        DATA.add_spell("Calm Emotions")
        DATA.add_spell("Faerie Fire")
        DATA.add_spell("Misty Step")
        DATA.add_spell("Phantasmal Force")
        DATA.add_spell("Sleep")

        DATA.add_feature(WarlockFeatures.StepsOfTheFey())


# ================ LEVEL 4 ============= #
if DATA.level >= 4:
    # Prepared spells
    DATA.add_spell("Crown of Madness")

    # Cantrips
    DATA.add_spell("Minor Illusion")

    # Choose one ability score to increase by 2
    # OR two ability scores to increase by 1 each
    DATA.add_feature(
        GeneralFeats.AbilityScoreImprovement(
            [
                (Ability.CHARISMA, 1),
                (Ability.CONSTITUTION, 1),
            ]
        )
    )

# ================ LEVEL 5 ============= #
if DATA.level >= 5:
    pass

##########################################
# ========== MANUAL ADDITIONS ========== #
##########################################

##########################################
# ============ LEAVE AS IS ============= #
##########################################
