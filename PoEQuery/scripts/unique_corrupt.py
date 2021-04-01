from functools import lru_cache
from PoEQuery.affix_finder import find_affixes
from PoEQuery.official_api_result import OfficialApiResult
from pandas.core.frame import DataFrame
from PoEQuery.official_api_query import OfficialApiQuery, StatFilter, StatFilters
import json
import traceback
from collections import defaultdict

import os
import pandas as pd

from PoEQuery.official_api import (search_query, fetch_results,
                         recurse_fetch_query_with_query_divider)
from PoEQuery.query_generator import generate_by_ilvl, generate_by_price
from PoEQuery.wiki_api import fetch_all_query

unique_query = {'title': 'Special:CargoExport',
'tables': 'items,',
'fields': 'items.name, items.base_item, items.class_id',
'where': 'items.rarity = "Unique"',
'order by': '`cargo__items`.`name`,`cargo__items`.`base_item`',
'limit': '5000',
'format': 'json'}

wiki_unique_fetch = fetch_all_query(unique_query)

# 02.14.21
# Bated Breath Chain Belt


print(f"{len(wiki_unique_fetch)} Uniques Fetched from Wiki")

def results_to_jsonl(results, file_name):

    with open(f"{file_name}.jsonl", "w") as f:
        for result in results:
            f.write(json.dumps(result) + "\n")


def get_results_from_unique(name, type):    
    query = OfficialApiQuery(stat_filters=[StatFilters([StatFilter(id="pseudo.pseudo_number_of_implicit_mods", min=1, max=1)])],corrupted=True, sale_type="priced", name=name, type=type).to_json()

    fetch_ids, unsplit_queries = recurse_fetch_query_with_query_divider(
        query, [generate_by_ilvl, generate_by_price]
    )
    
    return fetch_results(fetch_ids)


def estimate_price_in_chaos(price):
    if price.currency =="alch":
        return price.amount * .2
    elif price.currency =="chaos":
        return price.amount * 1
    elif price.currency =="exalted":
        return price.amount * 100
    elif price.currency =="mirror":
        return price.amount * 100 * 420
    else:
        # print(price)
        return None



item_classes =  dict(
    BOW = "weapon.bow",
    CLAW = "weapon.claw",
    BASE_DAGGER = "weapon.basedagger",
    RUNE_DAGGER = "weapon.runedagger",
    ONE_HANDED_AXE = "weapon.oneaxe",
    ONE_HANDED_MACE = "weapon.onemace",
    ONE_HANDED_SWORD = "weapon.onesword",
    SCEPTRE = "weapon.sceptre",
    BASE_STAFF = "weapon.basestaff",
    WARSTAFF = "weapon.warstaff",
    TWO_HANDED_AXE = "weapon.twoaxe",
    TWO_HANDED_MACE = "weapon.twomace",
    TWO_HANDED_SWORD = "weapon.twosword",
    WAND = "weapon.wand",
    BODY_ARMOUR = "armour.chest",
    BOOTS = "armour.boots",
    GLOVES = "armour.gloves",
    HELMET = "armour.helmet",
    SHIELD = "armour.shield",
    QUIVER = "armour.quiver",
    AMULET = "accessory.amulet",
    BELT = "accessory.belt",
    RING = "accessory.ring",
    BASE_JEWEL = "jewel.base",
    ABYSS_JEWEL = "jewel.abyss",
    CLUSTER_JEWEL = "jewel.cluster")

wiki_item_class_to_api_item_class = {'LifeFlask' : None,
 'One Hand Sword': "ONE_HANDED_SWORD",
 'Wand': "WAND",
 'AtlasRegionUpgradeItem': None,
 'Rune Dagger' : "RUNE_DAGGER",
 'Thrusting One Hand Sword' :"ONE_HANDED_SWORD",
 'Map' : None,
 'Ring' : "RING",
 'Body Armour' : "BODY_ARMOUR",
 'One Hand Axe' : "ONE_HANDED_AXE",
 'Claw' : "CLAW",
 'Staff' : "BASE_STAFF",
 'FishingRod' : None,
 'Belt' : "BELT",
 'Shield' : "SHIELD",
 'HybridFlask' : None,
 'One Hand Mace' : "ONE_HANDED_MACE",
 'Warstaff' : "WARSTAFF",
 'HeistContract' : None,
 'Sceptre' : "SCEPTRE",
 'Jewel' : "BASE_JEWEL",
 'UtilityFlask' : None,
 'Bow' : "BOW",
 'Dagger' : "BASE_DAGGER",
 'Helmet' : "HELMET",
 'Amulet' : "AMULET",
 'Two Hand Axe' : "TWO_HANDED_AXE",
 'UtilityFlaskCritical' : None,
 'Quiver' : "QUIVER",
 'Two Hand Mace' : "TWO_HANDED_MACE",
 'Two Hand Sword' : "TWO_HANDED_SWORD",
 'Boots' : "BOOTS",
 'UniqueFragment' : None,
 'ManaFlask': None,
 'Gloves' : "GLOVES"}


def fetch_all_corrupt_uniques():
    g = open("unique_counts.txt", "w")

    for values in wiki_unique_fetch:
        name_ = values["name"]
        type_ = values['base item']

        stripped_name = f"""./data/unique_corrupts/{name_.replace(" ", "_").lower()}"""

        try:
            if os.path.exists(f"{stripped_name}.jsonl"):
                query = OfficialApiQuery(stat_filters=[StatFilters([StatFilter(id="pseudo.pseudo_number_of_implicit_mods", min=1, max=1)])],corrupted=True, sale_type="priced", name=name_, type=type_).to_json()
                fetch_ids, total, query = search_query(query)
        
                with open(f"{stripped_name}.jsonl", "r") as f:
                    g.writelines([f"{name_} {type_} {total} {len(f.readlines())}"])

                print(f"skipping {name_}")
            else:
                print(name_, type_)
                results = get_results_from_unique(name_, type_)
                results_to_jsonl(results, stripped_name)
                # parse_results_to_csv(stripped_name)
        except Exception as e:
            traceback.print_exc()
            print(name_, type_, e)


@lru_cache(maxsize=None)
def get_corrupt_for_item_class(category):
    non_corrupt = find_affixes(OfficialApiQuery(stat_filters=[StatFilters([StatFilter(id="pseudo.pseudo_number_of_implicit_mods", min=1, max=1)])],category=category, corrupted=False, sale_type="priced", synthesised=False), affix_type="implicit"
    )
    corrupt = find_affixes(OfficialApiQuery(stat_filters=[StatFilters([StatFilter(id="pseudo.pseudo_number_of_implicit_mods", min=1, max=1)])],category=category,corrupted=True, sale_type="priced", synthesised=False), affix_type="implicit"
    )
    return corrupt.difference(non_corrupt)



for values in wiki_unique_fetch:
    results_df = pd.DataFrame()
    name_ = values["name"]
    type_ = values['base item']

    item_class = wiki_item_class_to_api_item_class[values["class id"]]
    
    if item_class is not None:
        print(item_class)
        get_corrupt_for_item_class(item_classes[item_class])
    continue
    corrupt_mods = get_corrupt_for_item_class(values["class id"])

    stripped_name = f"""./data/unique_corrupts/{name_.replace(" ", "_").lower()}_{type_.replace(" ", "_").lower()}"""
    query = OfficialApiQuery(stat_filters=[StatFilters([StatFilter(id="pseudo.pseudo_number_of_implicit_mods", min=1, max=1)])],corrupted=True, sale_type="priced", name=name_, type=type_).to_json()

    for mod in []:
        fetch_ids, total, query = search_query(query)
        results = fetch_results(fetch_ids)
        
        results_entry = {"mod_str": str(mod), "mod_json": json.dumps(mod.to_json())}
        
        for idx, result in enumerate(results):
            parsed_result = OfficialApiResult(result)
            results_entry[f"price_{idx:02}"] = estimate_price_in_chaos(parsed_result.price)
            
        results_df = results_df.append(results_entry, ignore_index=True)
    results_df.to_csv(f"{stripped_name}.csv")

