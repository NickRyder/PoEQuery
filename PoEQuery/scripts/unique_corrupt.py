from functools import lru_cache

from PoEQuery.affix_finder import find_affixes
from PoEQuery.official_api_query import OfficialApiQuery, StatFilter, StatFilters
from tqdm import tqdm

from PoEQuery.official_api import (
    search_and_fetch_batched,
)
from PoEQuery.wiki_api import fetch_all_query

unique_query = {
    "title": "Special:CargoExport",
    "tables": "items,",
    "fields": "items.name, items.base_item, items.class_id",
    "where": 'items.rarity = "Unique"',
    "order by": "`cargo__items`.`name`,`cargo__items`.`base_item`",
    "limit": "5000",
    "format": "json",
}

wiki_unique_fetch = fetch_all_query(unique_query)

print(f"{len(wiki_unique_fetch)} Uniques Fetched from Wiki")


item_classes = dict(
    BOW="weapon.bow",
    CLAW="weapon.claw",
    BASE_DAGGER="weapon.basedagger",
    RUNE_DAGGER="weapon.runedagger",
    ONE_HANDED_AXE="weapon.oneaxe",
    ONE_HANDED_MACE="weapon.onemace",
    ONE_HANDED_SWORD="weapon.onesword",
    SCEPTRE="weapon.sceptre",
    BASE_STAFF="weapon.basestaff",
    WARSTAFF="weapon.warstaff",
    TWO_HANDED_AXE="weapon.twoaxe",
    TWO_HANDED_MACE="weapon.twomace",
    TWO_HANDED_SWORD="weapon.twosword",
    WAND="weapon.wand",
    BODY_ARMOUR="armour.chest",
    BOOTS="armour.boots",
    GLOVES="armour.gloves",
    HELMET="armour.helmet",
    SHIELD="armour.shield",
    QUIVER="armour.quiver",
    AMULET="accessory.amulet",
    BELT="accessory.belt",
    RING="accessory.ring",
    BASE_JEWEL="jewel.base",
    ABYSS_JEWEL="jewel.abyss",
    CLUSTER_JEWEL="jewel.cluster",
)

wiki_item_class_to_api_item_class = {
    "LifeFlask": None,
    "One Hand Sword": "ONE_HANDED_SWORD",
    "Wand": "WAND",
    "AtlasRegionUpgradeItem": None,
    "Rune Dagger": "RUNE_DAGGER",
    "Thrusting One Hand Sword": "ONE_HANDED_SWORD",
    "Map": None,
    "Ring": "RING",
    "Body Armour": "BODY_ARMOUR",
    "One Hand Axe": "ONE_HANDED_AXE",
    "Claw": "CLAW",
    "Staff": "BASE_STAFF",
    "FishingRod": None,
    "Belt": "BELT",
    "Shield": "SHIELD",
    "HybridFlask": None,
    "One Hand Mace": "ONE_HANDED_MACE",
    "Warstaff": "WARSTAFF",
    "HeistContract": None,
    "Sceptre": "SCEPTRE",
    "Jewel": "BASE_JEWEL",
    "UtilityFlask": None,
    "Bow": "BOW",
    "Dagger": "BASE_DAGGER",
    "Helmet": "HELMET",
    "Amulet": "AMULET",
    "Two Hand Axe": "TWO_HANDED_AXE",
    "UtilityFlaskCritical": None,
    "Quiver": "QUIVER",
    "Two Hand Mace": "TWO_HANDED_MACE",
    "Two Hand Sword": "TWO_HANDED_SWORD",
    "Boots": "BOOTS",
    "UniqueFragment": None,
    "ManaFlask": None,
    "Gloves": "GLOVES",
}


@lru_cache(maxsize=None)
def get_corrupt_for_item_class(category):
    non_corrupt = find_affixes(
        OfficialApiQuery(
            stat_filters=[
                StatFilters(
                    [
                        StatFilter(
                            id="pseudo.pseudo_number_of_implicit_mods", min=1, max=1
                        )
                    ]
                )
            ],
            category=category,
            corrupted=False,
            sale_type="priced",
            synthesised=False,
        ),
        affix_type="implicit",
    )
    corrupt = find_affixes(
        OfficialApiQuery(
            stat_filters=[
                StatFilters(
                    [
                        StatFilter(
                            id="pseudo.pseudo_number_of_implicit_mods", min=1, max=1
                        )
                    ]
                )
            ],
            category=category,
            corrupted=True,
            sale_type="priced",
            synthesised=False,
        ),
        affix_type="implicit",
    )
    return corrupt.difference(non_corrupt)


# print(get_corrupt_for_item_class("accessory.ring"))
t = tqdm(wiki_unique_fetch)
for values in t:
    name_ = values["name"]
    type_ = values["base item"]
    t.set_description(f"{name_} {type_}")

    item_class = wiki_item_class_to_api_item_class[values["class id"]]

    if item_class is None:
        continue
    corrupt_mods = get_corrupt_for_item_class(item_classes[item_class])

    queries = []
    for mod in corrupt_mods:

        query = OfficialApiQuery(
            stat_filters=[
                StatFilters(mod.to_query_stat_filters()),
            ],
            corrupted=True,
            sale_type="priced",
            name=name_,
            type=type_,
            indexed="2week",
        )
        queries.append(query)
    results = search_and_fetch_batched(queries)
