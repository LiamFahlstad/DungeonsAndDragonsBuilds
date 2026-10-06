from typing import Optional

import attr

import Core.Definitions as Definitions
from CharacterContent.Classes.BaseClasses import ClassBuilder
from Model.Character import Character
from Model.Grants import Grants
from Core.Definitions import CharacterClass, Skill
from CharacterContent.Features.CharacterFeats import EpicBoon, GeneralFeats
from CharacterContent.Items import Weapons
from CharacterContent.Items import Packs
from CharacterContent.Features.ClassFeatures.Barbarian import BarbarianFeatures


@attr.dataclass
class BarbarianLevel1(ClassBuilder.BaseClassLevel1):
    weapon_mastery_1: Weapons.AbstractWeapon
    weapon_mastery_2: Weapons.AbstractWeapon

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_weapon_mastery(self.weapon_mastery_1)
        data.add_weapon_mastery(self.weapon_mastery_2)

        data.add_feature(BarbarianFeatures.Rage())
        # Its AC formula only applies while no armor is worn (a Shield is
        # fine), so it's granted unconditionally - the gear isn't known yet.
        data.add_feature(BarbarianFeatures.UnarmoredDefense())
        data.add_feature(BarbarianFeatures.UnarmoredDefenseText())
        data.add_feature(BarbarianFeatures.WeaponMastery())


@attr.dataclass
class BarbarianLevel2(ClassBuilder.BaseClassLevel2):

    def add_features(self, data: Grants) -> None:
        data.add_feature(BarbarianFeatures.DangerSenseText())
        data.add_feature(BarbarianFeatures.DangerSense())
        data.add_feature(BarbarianFeatures.RecklessAttack())


@attr.dataclass
class BarbarianLevel3(ClassBuilder.BaseClassLevel3):
    skill_proficiency: Definitions.Skill

    def add_features(self, data: Grants) -> None:
        data.add_feature(
            BarbarianFeatures.PrimalKnowledgeSkillProficiency(self.skill_proficiency)
        )
        data.add_feature(BarbarianFeatures.PrimalKnowledge())


@attr.dataclass
class BarbarianLevel4(ClassBuilder.BaseClassLevel4):
    general_feat: GeneralFeats.GeneralFeat

    def add_features(self, data: Grants) -> None:
        data.add_feature(self.general_feat)


@attr.dataclass
class BarbarianLevel5(ClassBuilder.BaseClassLevel5):

    def add_features(self, data: Grants) -> None:
        data.add_feature(
            BarbarianFeatures.FastMovement(),
            extends=BarbarianFeatures.UnarmoredDefenseText,
        )
        data.add_feature(BarbarianFeatures.FastMovementBonus())
        data.add_feature(BarbarianFeatures.ExtraAttack())


@attr.dataclass
class BarbarianLevel6(ClassBuilder.BaseClassLevel6):

    def add_features(self, data: Grants) -> None:
        pass


@attr.dataclass
class BarbarianLevel7(ClassBuilder.BaseClassLevel7):

    def add_features(self, data: Grants) -> None:
        data.add_feature(BarbarianFeatures.FeralInstinct())
        data.add_feature(
            BarbarianFeatures.InstinctivePounce(), extends=BarbarianFeatures.Rage
        )


@attr.dataclass
class BarbarianLevel8(ClassBuilder.BaseClassLevel8):
    general_feat: GeneralFeats.GeneralFeat

    def add_features(self, data: Grants) -> None:
        data.add_feature(self.general_feat)


@attr.dataclass
class BarbarianLevel9(ClassBuilder.BaseClassLevel9):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            BarbarianFeatures.BrutalStrike(), extends=BarbarianFeatures.RecklessAttack
        )


@attr.dataclass
class BarbarianLevel10(ClassBuilder.BaseClassLevel10):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        pass


@attr.dataclass
class BarbarianLevel11(ClassBuilder.BaseClassLevel11):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            BarbarianFeatures.RelentlessRage(), extends=BarbarianFeatures.Rage
        )


@attr.dataclass
class BarbarianLevel12(ClassBuilder.BaseClassLevel12):
    general_feat: GeneralFeats.GeneralFeat

    def add_features(self, data: Grants) -> None:
        data.add_feature(self.general_feat)


@attr.dataclass
class BarbarianLevel13(ClassBuilder.BaseClassLevel13):

    def add_features(self, data: Grants) -> None:
        data.add_feature(
            BarbarianFeatures.ImprovedBrutalStrikeLevel13(),
            extends=BarbarianFeatures.RecklessAttack,
        )


@attr.dataclass
class BarbarianLevel14(ClassBuilder.BaseClassLevel14):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        pass


@attr.dataclass
class BarbarianLevel15(ClassBuilder.BaseClassLevel15):

    def add_features(self, data: Grants) -> None:
        data.add_feature(
            BarbarianFeatures.PersistentRage(), extends=BarbarianFeatures.Rage
        )


@attr.dataclass
class BarbarianLevel16(ClassBuilder.BaseClassLevel16):
    general_feat: GeneralFeats.GeneralFeat

    def add_features(self, data: Grants) -> None:
        data.add_feature(self.general_feat)


@attr.dataclass
class BarbarianLevel17(ClassBuilder.BaseClassLevel17):

    def add_features(self, data: Grants) -> None:
        data.add_feature(
            BarbarianFeatures.ImprovedBrutalStrikeLevel17(),
            extends=BarbarianFeatures.RecklessAttack,
        )


@attr.dataclass
class BarbarianLevel18(ClassBuilder.BaseClassLevel18):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(BarbarianFeatures.IndomitableMight())


@attr.dataclass
class BarbarianLevel19(ClassBuilder.BaseClassLevel19):
    epic_boon: EpicBoon.EpicBoon

    def add_features(self, data: Grants) -> None:
        data.add_feature(self.epic_boon)


@attr.dataclass
class BarbarianLevel20(ClassBuilder.BaseClassLevel20):

    def add_features(self, data: Grants) -> None:
        data.add_feature(BarbarianFeatures.PrimalChampion())


class BarbarianCustomStarterClassArgs(ClassBuilder.CustomStarterClassArgs):
    def __init__(
        self,
        subclass: str,
        skills: list[Skill],
    ):
        super().__init__(
            base_class=CharacterClass.BARBARIAN,
            subclass=subclass,
            default_equipment=[
                Weapons.UnarmedStrike(),
                Weapons.Greataxe(),
            ],
            skills=skills,
            armor_proficiencies=[
                Definitions.ArmorType.LIGHT,
                Definitions.ArmorType.MEDIUM,
                Definitions.ArmorType.SHIELD,
            ],
            weapon_proficiencies=[
                Weapons.WeaponProficiency.SIMPLE,
                Weapons.WeaponProficiency.MARTIAL,
            ],
            default_pack=Packs.ExplorersPack(),
        )


class BarbarianMulticlassBuilder(ClassBuilder.MulticlassBuilder):

    def __init__(
        self,
        barbarian_level_features: ClassBuilder.BaseClassLevelFeatures,
        barbarian_level: int,
        subclass: str,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        self.subclass = subclass
        super().__init__(
            base_class=CharacterClass.BARBARIAN,
            base_class_level_features=barbarian_level_features,
            base_class_level=barbarian_level,
            subclass=subclass,
            replace_spells=replace_spells,
        )
