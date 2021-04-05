import json
import traceback
from collections import defaultdict

import os
import pandas as pd

from PoEQuery.official_api import (
    search_query,
    fetch_results,
    recurse_fetch_query_with_query_divider,
)
from PoEQuery.query_generator import generate_by_ilvl, generate_by_price
from PoEQuery.wiki_api import fetch_all_query


def create_item_query(name=None, type=None, corrupted=True):
    """
    Creates an item query with the following stipulations:
    - priced
    - corrupted
    - 1 implicit
    """
    item_query = {
        "query": {
            "filters": {
                "trade_filters": {"filters": {"sale_type": {"option": "priced"}}}
            },
            "stats": [],
            "status": {"option": "any"},
        }
    }

    if "name" is not None:
        item_query["query"]["name"] = name
    if "type" is not None:
        item_query["query"]["type"] = type

    return item_query


def fetch_single_unique(name, type):
    query = create_item_query(name=name, type=type)
    fetch_ids, total, query = search_query(query)
    first_fetch_id = [fetch_ids[0]]
    results = fetch_results(first_fetch_id)
    return results[0]


def results_jsonl(results, file_name):

    with open(f"{file_name}.jsonl", "w") as f:
        for result in results:
            f.write(json.dumps(result) + "\n")


def get_results_from_unique(name_, type_):
    # result = fetch_single_unique(name=name_, type=type_)
    query = create_item_query(name=name_, type=type_)

    fetch_ids, unsplit_queries = recurse_fetch_query_with_query_divider(
        query, [generate_by_ilvl, generate_by_price]
    )

    return fetch_results(fetch_ids)


def fetch_all_corrupt_uniques():

    stripped_name = f"""./data/skin_of_the_lords"""

    try:
        query = create_item_query(
            name="Skin of the Lords", type="Simple Robe", corrupted=False
        )

        fetch_ids, unsplit_queries = recurse_fetch_query_with_query_divider(
            query, [generate_by_ilvl, generate_by_price]
        )

        results = fetch_results(fetch_ids)

        results_jsonl(results, stripped_name)
        # parse_results_to_csv(stripped_name)
    except Exception as e:
        traceback.print_exc()
        print(e)


fetch_all_corrupt_uniques()
