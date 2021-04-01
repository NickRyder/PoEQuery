from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Set


class SaleType(Enum):
    PRICED_WITH_INFO = "priced_with_info"
    PRICED = "priced"
    UNPRICED = "unpriced"
    ANY = "any"

    def __str__(self):
        return self.value


class CategoryType(Enum):
    ANY = "any"
    ANY_WEAPON = "weapon"
    ONE_HANDED_WEAPON = "weapon.one"
    ONE_HANDED_MELEE_WEAPON = "weapon.onemelee"
    TWO_HANDED_MELEE_WEAPON = "weapon.twomelee"
    BOW = "weapon.bow"
    CLAW = "weapon.claw"
    ANY_DAGGER = "weapon.dagger"
    BASE_DAGGER = "weapon.basedagger"
    RUNE_DAGGER = "weapon.runedagger"
    ONE_HANDED_AXE = "weapon.oneaxe"
    ONE_HANDED_MACE = "weapon.onemace"
    ONE_HANDED_SWORD = "weapon.onesword"
    SCEPTRE = "weapon.sceptre"
    ANY_STAFF = "weapon.staff"
    BASE_STAFF = "weapon.basestaff"
    WARSTAFF = "weapon.warstaff"
    TWO_HANDED_AXE = "weapon.twoaxe"
    TWO_HANDED_MACE = "weapon.twomace"
    TWO_HANDED_SWORD = "weapon.twosword"
    WAND = "weapon.wand"
    FISHING_ROD = None
    ANY_ARMOUR = "armour"
    BODY_ARMOUR = "armour.chest"
    BOOTS = "armour.boots"
    GLOVES = "armour.gloves"
    HELMET = "armour.helmet"
    SHIELD = "armour.shield"
    QUIVER = "armour.quiver"
    ANY_ACCESSORY = "accessory"
    AMULET = "accessory.amulet"
    BELT = "accessory.belt"
    RING = "accessory.ring"
    TRINKET = "accessory.trinket"
    ANY_GEM = "gem"
    SKILL_GEM = "gem.skill"
    SUPPORT_GEM = "gem.support"
    AWAKENED_SUPPORT_GEM = "gem.supportgemplus"
    ANY_JEWEL = "jewel"
    BASE_JEWEL = "jewel.base"
    ABYSS_JEWEL = "jewel.abyss"
    CLUSTER_JEWEL = "jewel.cluster"
    FLASK = None
    MAP = None
    MAP_FRAGMENT = None
    MAVENS_INVITATION = None
    SCARAB = None
    WATCHSTONE = None
    LEAGUESTONE = None
    PROPHECY = None
    DIVINATION_CARD = None
    CAPTURED_BEAST = None
    METAMORPH_SAMPLE = None
    ANY_HEIST_EQUIPMENT = None
    HEIST_GEAR = None
    HEIST_TOOL = None
    HEIST_CLOAK = None
    HEIST_BROOCH = None
    ANY_HEIST_MISSION = None
    HEIST_CONTRACT = None
    HEIST_BLUEPRINT = None
    ANY_CURRENCY = None
    UNIQUE_FRAGMENT = None
    RESONATOR = None
    FOSSIL = None
    INCUBATOR = None
    HEIST_TARGET = None

    def __init__(self):
        return NotImplemented

    def __str__(self):
        return self.value


@dataclass(unsafe_hash=True)
class StatFilter:
    id: str
    min: Optional[float] = None
    max: Optional[float] = None
    disabled: bool = False

    def _value_json(self):
        value_json = {}
        if self.min is not None:
            value_json["min"] = self.min
        if self.max is not None:
            value_json["max"] = self.max

        return value_json

    def to_json(self):
        value_json = self._value_json()
        filter_json = {
            "id": self.id,
            "disabled": self.disabled,
        }
        if value_json:
            filter_json["value"] = value_json

        return filter_json


@dataclass
class StatFilters:
    filters: Set[StatFilter] = field(default_factory=set)
    type: str = "and"

    def to_json(self):
        return {
            "type": self.type,
            # "disabled": False,
            "filters": {stat_filter.to_json() for stat_filter in self.filters},
        }


@dataclass
class OfficialApiQuery:
    stat_filters: List[StatFilters] = field(default_factory=lambda: [StatFilters()])
    name: Optional[str] = None
    type: Optional[str] = None
    corrupted: Optional[bool] = None
    mirrored: Optional[bool] = None
    synthesised: Optional[bool] = None
    alternate_art: Optional[bool] = False
    talisman_tier_max: Optional[int] = None
    quality_max: Optional[int] = None
    rarity: Optional[str] = None
    category: Optional[str] = None
    indexed: Optional[str] = None
    sale_type: Optional[str] = None  # priced
    identified: Optional[bool] = None
    enchanted: Optional[bool] = None
    fractured: Optional[bool] = None
    crafted: Optional[bool] = None

    sockets_b: Optional[int] = None
    sockets_g: Optional[int] = None
    sockets_r: Optional[int] = None
    sockets_w: Optional[int] = None

    links_b: Optional[int] = None
    links_g: Optional[int] = None
    links_r: Optional[int] = None
    links_w: Optional[int] = None

    def _get_socket_filters(self):
        filters = {}

        sockets = {}
        if self.sockets_b is not None:
            sockets["b"] = self.sockets_b
        if self.sockets_g is not None:
            sockets["g"] = self.sockets_g
        if self.sockets_r is not None:
            sockets["r"] = self.sockets_r
        if self.sockets_w is not None:
            sockets["w"] = self.sockets_w
        if sockets:
            filters["sockets"] = sockets

        links = {}
        if self.links_b is not None:
            links["b"] = self.links_b
        if self.links_g is not None:
            links["g"] = self.links_g
        if self.links_r is not None:
            links["r"] = self.links_r
        if self.links_w is not None:
            links["w"] = self.links_w
        if links:
            filters["links"] = links

        return {"filters": filters}

    def _get_misc_filters(self):
        filters = {}
        if self.corrupted is not None:
            filters["corrupted"] = {"option": str(self.corrupted).lower()}
        if self.mirrored is not None:
            filters["mirrored"] = {"option": str(self.mirrored).lower()}
        if self.synthesised is not None:
            filters["synthesised_item"] = {"option": str(self.synthesised).lower()}
        if self.alternate_art is not None:
            filters["alternate_art"] = {"option": str(self.alternate_art).lower()}
        if self.identified is not None:
            filters["identified"] = {"option": str(self.identified).lower()}
        if self.enchanted is not None:
            filters["enchanted"] = {"option": str(self.enchanted).lower()}
        if self.fractured is not None:
            filters["fractured_item"] = {"option": str(self.fractured).lower()}
        if self.crafted is not None:
            filters["crafted"] = {"option": str(self.crafted).lower()}
        if self.talisman_tier_max is not None:
            filters["talisman_tier"] = {"max": self.talisman_tier_max}
        if self.quality_max is not None:
            filters["quality"] = {"max": self.quality_max}
        return {"filters": filters}

    def _get_type_filters(self):
        filters = {}
        if self.rarity is not None:
            filters["rarity"] = {"option": self.rarity}
        if self.category is not None:
            filters["category"] = {"option": self.category}
        return {"filters": filters}

    def _get_trade_filters(self):
        filters = {}
        if self.sale_type is not None:
            filters["sale_type"] = {"option": self.sale_type}
        if self.indexed is not None:
            filters["indexed"] = {"option": self.indexed}
        return {"filters": filters}

    def _get_filters(self):
        filters = {}
        misc_filters = self._get_misc_filters()
        if misc_filters["filters"]:
            filters["misc_filters"] = misc_filters
        trade_filters = self._get_trade_filters()
        if trade_filters["filters"]:
            filters["trade_filters"] = trade_filters
        type_filters = self._get_type_filters()
        if type_filters["filters"]:
            filters["type_filters"] = type_filters
        socket_filters = self._get_socket_filters()
        if socket_filters["filters"]:
            filters["socket_filters"] = socket_filters

        return filters

    def _get_status(self):
        return {"option": "any"}

    def _get_stats(self):
        return [stat_filters.to_json() for stat_filters in self.stat_filters]

    def to_json(self):
        query_json = {
            "query": {
                "status": self._get_status(),
                "stats": self._get_stats(),
            }
        }
        filters = self._get_filters()
        if filters:
            query_json["query"]["filters"] = filters
        if self.name is not None:
            query_json["query"]["name"] = self.name
        if self.type is not None:
            query_json["query"]["type"] = self.type

        query_json["sort"] = {"price": "asc"}
        return query_json
