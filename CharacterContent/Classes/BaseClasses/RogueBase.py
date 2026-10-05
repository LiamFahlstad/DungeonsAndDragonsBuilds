from typing import Optional

import attr

import Core.Definitions as Definitions
from CharacterContent.Classes.BaseClasses import ClassBuilder
from Model.Character import Character
from Model.Grants import Grants
from Core.Definitions import Ability, CharacterClass, Skill
from CharacterContent.Features.CharacterFeats import EpicBoon, GeneralFeats
from CharacterContent.Features.ClassFeatures import SpellSlots
from CharacterContent.Items import Armor, Weapons
from CharacterContent.Items import Packs
from CharacterContent.Features.ClassFeatures.Rogue import RogueFeatures


@attr.dataclass
class RogueLevel1(ClassBuilder.BaseClassLevel1):
    skill_expertise_1: Definitions.Skill
    skill_expertise_2: Definitions.Skill
    weapon_mastery_1: Weapons.AbstractWeapon
    weapon_mastery_2: Weapons.AbstractWeapon

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_weapon_mastery(self.weapon_mastery_1)
        data.add_weapon_mastery(self.weapon_mastery_2)

        data.add_feature(
            RogueFeatures.Expertise(self.skill_expertise_1, self.skill_expertise_2)
        )
        data.add_feature(RogueFeatures.SneakAttack())
        data.add_feature(RogueFeatures.ThievesCant())
        data.add_feature(RogueFeatures.WeaponMastery())
        return data


@attr.dataclass
class RogueLevel2(ClassBuilder.BaseClassLevel2):

    def add_features(self, data: Grants) -> Grants:
        data.add_feature(RogueFeatures.CunningAction())
        return data


@attr.dataclass
class RogueLevel3(ClassBuilder.BaseClassLevel3):

    def add_features(self, data: Grants) -> Grants:
        data.add_feature(RogueFeatures.SteadyAim())
        return data


@attr.dataclass
class RogueLevel4(ClassBuilder.BaseClassLevel4):
    general_feat: GeneralFeats.GeneralFeat

    def add_features(self, data: Grants) -> Grants:
        self.general_feat.origin = f"Rogue Level {self.level}"
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class RogueLevel5(ClassBuilder.BaseClassLevel5):

    def add_features(self, data: Grants) -> Grants:
        data.add_feature(
            RogueFeatures.CunningStrike(), extends=RogueFeatures.SneakAttack
        )
        data.add_feature(RogueFeatures.UncannyDodge())
        return data


@attr.dataclass
class RogueLevel6(ClassBuilder.BaseClassLevel6):
    skill_expertise_1: Definitions.Skill
    skill_expertise_2: Definitions.Skill

    def add_features(self, data: Grants) -> Grants:
        data.add_feature(
            RogueFeatures.Expertise(self.skill_expertise_1, self.skill_expertise_2)
        )
        return data


@attr.dataclass
class RogueLevel7(ClassBuilder.BaseClassLevel7):

    def add_features(self, data: Grants) -> Grants:
        data.add_feature(RogueFeatures.Evasion())
        data.add_feature(RogueFeatures.ReliableTalent())
        return data


@attr.dataclass
class RogueLevel8(ClassBuilder.BaseClassLevel8):
    general_feat: GeneralFeats.GeneralFeat

    def add_features(self, data: Grants) -> Grants:
        self.general_feat.origin = f"Rogue Level {self.level}"
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class RogueLevel9(ClassBuilder.BaseClassLevel9):

    def add_features(self, data: Grants) -> Grants:
        return data


@attr.dataclass
class RogueLevel10(ClassBuilder.BaseClassLevel10):
    general_feat: GeneralFeats.GeneralFeat

    def add_features(self, data: Grants) -> Grants:
        self.general_feat.origin = f"Rogue Level {self.level}"
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class RogueLevel11(ClassBuilder.BaseClassLevel11):

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(
            RogueFeatures.ImprovedCunningStrike(), extends=RogueFeatures.SneakAttack
        )
        return data


@attr.dataclass
class RogueLevel12(ClassBuilder.BaseClassLevel12):
    general_feat: GeneralFeats.GeneralFeat

    def add_features(self, data: Grants) -> Grants:
        self.general_feat.origin = f"Rogue Level {self.level}"
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class RogueLevel13(ClassBuilder.BaseClassLevel13):

    def add_features(self, data: Grants) -> Grants:
        return data


@attr.dataclass
class RogueLevel14(ClassBuilder.BaseClassLevel14):

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(
            RogueFeatures.DeviousStrikes(), extends=RogueFeatures.SneakAttack
        )
        return data


@attr.dataclass
class RogueLevel15(ClassBuilder.BaseClassLevel15):

    def add_features(self, data: Grants) -> Grants:
        data.add_feature(RogueFeatures.SlipperyMind())
        return data


@attr.dataclass
class RogueLevel16(ClassBuilder.BaseClassLevel16):
    general_feat: GeneralFeats.GeneralFeat

    def add_features(self, data: Grants) -> Grants:
        self.general_feat.origin = f"Rogue Level {self.level}"
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class RogueLevel17(ClassBuilder.BaseClassLevel17):

    def add_features(self, data: Grants) -> Grants:
        return data


@attr.dataclass
class RogueLevel18(ClassBuilder.BaseClassLevel18):

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(RogueFeatures.Elusive())
        return data


@attr.dataclass
class RogueLevel19(ClassBuilder.BaseClassLevel19):
    epic_boon: EpicBoon.EpicBoon

    def add_features(self, data: Grants) -> Grants:
        self.epic_boon.origin = f"Rogue Level {self.level}"
        data.add_feature(self.epic_boon)
        return data


@attr.dataclass
class RogueLevel20(ClassBuilder.BaseClassLevel20):

    def add_features(self, data: Grants) -> Grants:
        data.add_feature(RogueFeatures.StrokeOfLuck())
        return data


class RogueCustomStarterClassArgs(ClassBuilder.CustomStarterClassArgs):
    def __init__(
        self,
        subclass: str,
        skills: list[Skill],
        caster_type: Optional[SpellSlots.CasterType] = None,
    ):
        super().__init__(
            base_class=CharacterClass.ROGUE,
            subclass=subclass,
            default_equipment=[
                Weapons.Shortsword(),
                Weapons.Dagger(),
                Weapons.Scimitar(),
                Armor.LeatherArmor(),
            ],
            skills=skills,
            armor_proficiencies=[
                Definitions.ArmorType.LIGHT,
            ],
            weapon_proficiencies=[
                Weapons.WeaponProficiency.SIMPLE,
                Weapons.WeaponProficiency.MARTIAL_FINESSE_OR_LIGHT,
            ],
            spell_casting_ability=(
                Ability.INTELLIGENCE if caster_type is not None else None
            ),
            caster_type=caster_type,
            default_pack=Packs.BurglarsPack(),
        )


class RogueMulticlassBuilder(ClassBuilder.MulticlassBuilder):

    def __init__(
        self,
        rogue_level_features: ClassBuilder.BaseClassLevelFeatures,
        rogue_level: int,
        subclass: str,
        replace_spells: Optional[dict[str, str]] = None,
        caster_type: Optional[SpellSlots.CasterType] = None,
    ):
        self.subclass = subclass
        super().__init__(
            base_class=CharacterClass.ROGUE,
            base_class_level_features=rogue_level_features,
            base_class_level=rogue_level,
            subclass=subclass,
            replace_spells=replace_spells,
            spell_casting_ability=(
                Ability.INTELLIGENCE if caster_type is not None else None
            ),
            caster_type=caster_type,
        )
