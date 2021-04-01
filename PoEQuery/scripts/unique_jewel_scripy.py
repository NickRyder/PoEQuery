import json
import requests
from official_api import fetch_results, fetch_query
import pandas as pd


unique_jewel_json = """https://pathofexile.gamepedia.com/index.php?title=Special:CargoExport&tables=items%2C&&fields=items.base_item%2C+items.name%2C&where=items.class+%3D+%22Jewel%22+AND+items.base_item+%21%3D+%22%22&order+by=%60cargo__items%60.%60base_item%60%2C%60cargo__items%60.%60name%60&limit=500&format=json"""

unique_jewel_json = requests.get(unique_jewel_json).json()

print(unique_jewel_json)


def create_item_query(name, base_item):
    return {
        "query": {
            "status": {"option": "online"},
            "name": name,
            "type": base_item,
            "stats": [{"type": "and", "filters": [{"id": "implicit.stat_2227180465"}]}],
            "filters": {
                "trade_filters": {"filters": {"sale_type": {"option": "priced"}}}
            },
        },
        "sort": {"price": "asc"},
    }


def _convert_price_to_chaos(price_json):
    if price_json["currency"] == "chaos":
        return price_json["amount"]
    elif price_json["currency"] == "exa":
        return price_json["amount"] * 130
    else:
        raise ValueError(f"unknown currency: {price_json['currency']}")


data = []
for jewel in unique_jewel_json:
    try:
        query = create_item_query(name=jewel["name"], base_item=jewel["base item"])
        fetch_ids, total, query = fetch_query(query)
        results = fetch_results(fetch_ids[:10])
        prices = [jewel["name"], jewel["base item"]]
        for result in results:
            try:
                prices.append(_convert_price_to_chaos(result["listing"]["price"]))
            except ValueError as e:
                print(e)
        data.append(prices)
        print(prices)
    except Exception as e:
        print(e)

unique_jewel_dataframe = pd.DataFrame(
    data,
    columns=[
        "name",
        "base item",
        "price 0",
        "price 1",
        "price 2",
        "price 3",
        "price 4",
        "price 5",
        "price 6",
        "price 7",
        "price 8",
        "price 9",
    ],
)

breakpoint()
