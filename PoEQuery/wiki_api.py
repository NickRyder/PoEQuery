from urllib.parse import ParseResult, urlencode
from typing import Dict
import requests


poe_wiki = ParseResult(
    scheme="https",
    netloc="pathofexile.gamepedia.com",
    path="/index.php",
    params="",
    query="",
    fragment="",
)


def build_poe_url_from_query(query: Dict[str, str]) -> str:
    query_string = urlencode(query)
    parsed_result_dict = poe_wiki._asdict().copy()
    parsed_result_dict.update({"query": query_string})
    return ParseResult(**parsed_result_dict).geturl()


def fetch_all_query(query: Dict[str, str]) -> dict:
    fetch_url = build_poe_url_from_query(query)
    fetch_json = requests.get(fetch_url).json()
    assert len(fetch_json) <= int(query["limit"]), "response got limited by query"
    return fetch_json


if __name__ == "__main__":
    example_query = {
        "title": "Special:CargoExport",
        "tables": "items,",
        "fields": "items.name, items.base_item",
        "where": 'items.rarity = "Unique"',
        "order by": "`cargo__items`.`name`,`cargo__items`.`base_item`",
        "limit": "5000",
        "format": "json",
    }

    unique_json = fetch_all_query(example_query)
    print(unique_json)
