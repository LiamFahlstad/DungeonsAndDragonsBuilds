from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from Model.Character import Character
from Model.Grants import Grants
from Core.Definitions import Ability, CharacterClass, Skill
from CharacterContent.Features.CharacterFeats import EpicBoon, GeneralFeats
from CharacterContent.Items import Weapons
from CharacterContent.Items import Packs
from CharacterContent.Features.ClassFeatures import SpellSlots
from CharacterContent.Features.ClassFeatures.Monk import MonkFeatures


@attr.dataclass
class MonkLevel1(ClassBuilder.BaseClassLevel1):
    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(MonkFeatures.MartialArts())
        data.add_feature(MonkFeatures.UnarmoredDefense())
        return data


@attr.dataclass
class MonkLevel2(ClassBuilder.BaseClassLevel2):
    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        monks_focus = MonkFeatures.MonksFocus()
        data.add_feature(MonkFeatures.FlurryOfBlows(), extends=monks_focus)
        data.add_feature(MonkFeatures.PatientDefense(), extends=monks_focus)
        data.add_feature(MonkFeatures.StepOfTheWind(), extends=monks_focus)
        data.add_feature(monks_focus)
        data.add_feature(MonkFeatures.UnarmoredMovement())
        data.add_feature(MonkFeatures.UncannyMetabolism())

        return data


@attr.dataclass
class MonkLevel3(ClassBuilder.BaseClassLevel3):
    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(MonkFeatures.DeflectAttacks(), extends=MonkFeatures.MonksFocus)
        return data


@attr.dataclass
class MonkLevel4(ClassBuilder.BaseClassLevel4):
    general_feat: GeneralFeats.GeneralFeat

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        self.general_feat.origin = f"Monk Level {self.level}"
        data.add_feature(self.general_feat)
        data.add_feature(MonkFeatures.SlowFall())
        return data


@attr.dataclass
class MonkLevel5(ClassBuilder.BaseClassLevel5):
    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(MonkFeatures.StunningStrike(), extends=MonkFeatures.MonksFocus)
        data.add_feature(MonkFeatures.ExtraAttack())
        return data


@attr.dataclass
class MonkLevel6(ClassBuilder.BaseClassLevel6):
    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(MonkFeatures.EmpoweredStrikes())
        return data


@attr.dataclass
class MonkLevel7(ClassBuilder.BaseClassLevel7):
    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(MonkFeatures.Evasion())
        return data


@attr.dataclass
class MonkLevel8(ClassBuilder.BaseClassLevel8):
    general_feat: GeneralFeats.GeneralFeat

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        self.general_feat.origin = f"Monk Level {self.level}"
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class MonkLevel9(ClassBuilder.BaseClassLevel9):
    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(MonkFeatures.AcrobaticMovement())
        return data


@attr.dataclass
class MonkLevel10(ClassBuilder.BaseClassLevel10):
    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(
            MonkFeatures.HeightenedFocus(), extends=MonkFeatures.MonksFocus
        )
        data.add_feature(MonkFeatures.SelfRestoration())
        return data


@attr.dataclass
class MonkLevel11(ClassBuilder.BaseClassLevel11):
    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        return data


@attr.dataclass
class MonkLevel12(ClassBuilder.BaseClassLevel12):
    general_feat: GeneralFeats.GeneralFeat

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        self.general_feat.origin = f"Monk Level {self.level}"
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class MonkLevel13(ClassBuilder.BaseClassLevel13):
    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(MonkFeatures.DeflectEnergy(), extends=MonkFeatures.MonksFocus)
        return data


@attr.dataclass
class MonkLevel14(ClassBuilder.BaseClassLevel14):
    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(MonkFeatures.DisciplinedSurvivorSavingThrows())
        data.add_feature(
            MonkFeatures.DisciplinedSurvivorMartialFocus(),
            extends=MonkFeatures.MonksFocus,
        )

        return data


@attr.dataclass
class MonkLevel15(ClassBuilder.BaseClassLevel15):
    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(MonkFeatures.PerfectFocus())
        return data


@attr.dataclass
class MonkLevel16(ClassBuilder.BaseClassLevel16):
    general_feat: GeneralFeats.GeneralFeat

    def add_features(self, data: Grants) -> Grants:
        self.general_feat.origin = f"Monk Level {self.level}"
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class MonkLevel17(ClassBuilder.BaseClassLevel17):
    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        return data


@attr.dataclass
class MonkLevel18(ClassBuilder.BaseClassLevel18):
    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(
            MonkFeatures.SuperiorDefense(), extends=MonkFeatures.MonksFocus
        )
        return data


@attr.dataclass
class MonkLevel19(ClassBuilder.BaseClassLevel19):
    epic_boon: EpicBoon.EpicBoon

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        self.epic_boon.origin = f"Monk Level {self.level}"
        data.add_feature(self.epic_boon)
        return data


@attr.dataclass
class MonkLevel20(ClassBuilder.BaseClassLevel20):
    def add_features(self, data: Grants) -> Grants:
        data.add_feature(MonkFeatures.BodyAndMind())
        return data


class MonkCustomStarterClassArgs(ClassBuilder.CustomStarterClassArgs):
    def __init__(
        self,
        subclass: str,
        skills: list[Skill],
        monk_level: int,
        unarmed_strike: Ability,
        caster_type: Optional[SpellSlots.CasterType] = None,
    ):

        martial_arts_die = MonkFeatures.LEVEL_TO_MARTIAL_ARTS_DIE[monk_level]

        super().__init__(
            base_class=CharacterClass.MONK,
            subclass=subclass,
            default_equipment=[
                Weapons.UnarmedStrike(
                    player_is_proficient=True,
                    ability=unarmed_strike,
                    damage_roll=martial_arts_die,
                ),
                Weapons.Spear(),
                Weapons.Dagger(),
            ],
            skills=skills,
            armor_proficiencies=None,
            weapon_proficiencies=[
                Weapons.WeaponProficiency.SIMPLE,
                Weapons.WeaponProficiency.MARTIAL_LIGHT,
            ],
            spell_casting_ability=Ability.WISDOM if caster_type is not None else None,
            caster_type=caster_type,
            default_pack=Packs.ExplorersPack(),
        )


class MonkMulticlassBuilder(ClassBuilder.MulticlassBuilder):

    def __init__(
        self,
        monk_level_features: ClassBuilder.BaseClassLevelFeatures,
        monk_level: int,
        subclass: str,
        replace_spells: Optional[dict[str, str]] = None,
        caster_type: Optional[SpellSlots.CasterType] = None,
    ):
        self.subclass = subclass
        super().__init__(
            base_class=CharacterClass.MONK,
            base_class_level_features=monk_level_features,
            base_class_level=monk_level,
            subclass=subclass,
            replace_spells=replace_spells,
            spell_casting_ability=Ability.WISDOM,
            caster_type=caster_type,
        )
