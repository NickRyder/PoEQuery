from functools import lru_cache
from PoEQuery.cache import cache_results
import requests


@cache_results("ninja_overview", key=lambda league, type: (league, type))
def item_overview(league: str, type: str):
    url = "https://poe.ninja/api/data/ItemOverview"

    response = requests.get(url, params={"league": league, "type": type})

    response.raise_for_status()

    return response.json()["lines"]


def item_history(league: str, type: str, itemId: int):
    url = "https://poe.ninja/api/data/ItemHistory"

    response = requests.get(
        url, params={"league": league, "type": type, "itemId": itemId}
    )

    return response.json()


@lru_cache(maxsize=1)
def currency_overview(league: str, type: str = "Currency"):
    url = "https://poe.ninja/api/data/CurrencyOverview"

    response = requests.get(url, params={"league": league, "type": type})
    currency_dict = {v.pop("currencyTypeName"): v for v in response.json()["lines"]}
    currency_details_dict = {
        v.pop("name"): v for v in response.json()["currencyDetails"]
    }
    return {
        name: {**currency_dict[name], **currency_details_dict[name]}
        for name in currency_dict.keys()
    }


if __name__ == "__main__":
    currency = currency_overview("Ultimatum")
    print(currency)
