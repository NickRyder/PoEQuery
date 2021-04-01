import json
import traceback
from collections import defaultdict
from functools import partial

import pandas as pd
import requests

from official_api import (fetch_query, fetch_results,
                         recurse_fetch_query_with_query_divider)
from query_generator import (generate_by_ilvl, generate_by_price,
                             generate_by_roll_ranges)

wiki_fetch_url = "https://pathofexile.gamepedia.com/index.php?title=Special:CargoExport&tables=items%2C&&fields=items.name%2C+items.base_item&where=items.rarity+%3D+%22Unique%22+and+items.class+%3D+%22Helmets%22&order+by=%60cargo__items%60.%60name%60%2C%60cargo__items%60.%60base_item%60&limit=5000&format=json"

wiki_fetch = requests.get(wiki_fetch_url).json()

print(wiki_fetch)


def create_item_query(name = None, type = None, price_low = 0, price_high = 9999):
    item_query = {
        "query": {
            "status": {"option": "any"},
            "stats": [{"type": "and", "filters": []}],
            "filters": {
                "trade_filters": {
                    "filters": {
                        "sale_type": {"option": "priced"},
                        "indexed": {"option": "2weeks"},
                        "price": {"max": price_high, "min": price_low},
                    }
                },
                "misc_filters": {
                    "filters": {
                        "enchanted": {"option": "true"},
                        "corrupted": {"option": "false"},
                    }
                },
            },
        },
        "sort": {"price": "asc"},
    }

    if "name" is not None:
        item_query["query"]["name"] = name
    if "type" is not None:
        item_query["query"]["type"] = type
    
    return item_query


def _convert_price_to_chaos(price_json):
    if price_json["currency"] == "chaos":
        return price_json["amount"]
    elif price_json["currency"] == "exa":
        return price_json["amount"] * 145
    else:
        raise ValueError(f"unknown currency: {price_json['currency']}")


# collected_helm_data = []
# for helm in wiki_fetch:
#     print(helm)
#     query = create_item_query(
#         name=helm["name"], type=helm["base item"], price_low=150, price_high=150 * 50
#     )

#     fetch_ids, unsplit_queries = recurse_fetch_query_with_query_divider(
#         query, generate_by_ilvl
#     )
#     assert not unsplit_queries
#     results = fetch_results(fetch_ids)


def fetch_single_unique(name, type):
    query = create_item_query(name=name, type=type, price_low=0, price_high=150 * 150)
    fetch_ids, total, query = fetch_query(query)
    first_fetch_id = [fetch_ids[0]]
    results = fetch_results(first_fetch_id)
    return results[0]


def results_to_csv(results, file_name):

    with open(f"{file_name}.jsonl", "w") as f:
        for result in results:
            f.write(json.dumps(result) + "\n")


def parse_results_to_csv(file_name):
    enchant_to_prices = defaultdict(list)

    with open(f"{file_name}.jsonl") as f:
        for l in f:
            json_data = json.loads(l)
            try:
                price = _convert_price_to_chaos(json_data["listing"]["price"])
                enchant = json_data["item"]["enchantMods"]
                assert len(enchant) == 1
                enchant = enchant[0]
                enchant_to_prices[enchant].append(price)
            except ValueError:
                pass

    data = []
    for k, v in enchant_to_prices.items():
        data.append([k] + v)

    column_count = max([len(v) for v in data])
    df = pd.DataFrame(
        data, columns=["enchant"] + [f"price{idx}" for idx in range(column_count - 1)]
    )

    df.to_csv(f"{file_name}.csv")

def get_results_from_unique(name_, type_):
    result = fetch_single_unique(name=name_, type=type_)


    query = create_item_query(name=name_, type=type_, price_low=0, price_high=150 * 50)

    fetch_ids, unsplit_queries = recurse_fetch_query_with_query_divider(
        query, [partial(generate_by_roll_ranges, result=result), generate_by_ilvl, generate_by_price]
    )
    
    return fetch_results(fetch_ids)


def combine_all_data():
    all_jsons = []
    for values in wiki_fetch:
        name_ = values["name"]
        type_ = values['base item']

        stripped_name = f"""helm_enchants/{name_.replace(" ", "").lower()}"""

        try:
            with open(f"{stripped_name}.jsonl") as f:
                for l in f:
                    all_jsons.append(json.loads(l))
        except Exception as e:
            print(name_, type_)
            print(0)


    enchant_to_prices = defaultdict(list)
    for json_data in all_jsons:
        try:
            price = _convert_price_to_chaos(json_data["listing"]["price"])
            if price > 0:
                enchant = json_data["item"]["enchantMods"]
                # assert len(enchant) == 1, json_data
                enchant = enchant[0]
                enchant_to_prices[(json_data["item"]["name"] + " " + json_data["item"]["typeLine"], enchant)].append(price)
        except Exception:
            pass

    data = []
    for k, v in enchant_to_prices.items():
        data.append([k[0], k[1]] + v)

    column_count = max([len(v) for v in data])
    df = pd.DataFrame(
        data, columns=["helmet", "enchant"] + [f"price{idx}" for idx in range(column_count - 2)]
    )

    df.to_csv(f"helm_enchants.csv")

def fetch_all_helms():
    for values in wiki_fetch:
        name_ = values["name"]
        type_ = values['base item']

        stripped_name = f"""helm_enchants/{name_.replace(" ", "").lower()}"""

        print(name_, type_)
        try:
            results = get_results_from_unique(name_, type_)
            results_to_csv(results, stripped_name)
            parse_results_to_csv(stripped_name)
        except Exception as e:
            traceback.print_exc()
            print(name_, type_, e)


def fetch_trinkets():

    query = {
        "query": {
            "status": {"option": "any"},
            "stats": [{"type": "and", "filters": []}],
            "type" : "Foliate Brooch"
            },
        "sort": {"price": "asc"},
    }

    print(query)
    fetch_ids, unsplit_queries = recurse_fetch_query_with_query_divider(
        query, [generate_by_ilvl, generate_by_price]
    )
    
    return fetch_results(fetch_ids)


combine_all_data()