import requests


def stats_from_web():
    _STATS_URL = "https://www.pathofexile.com/api/trade/data/stats"
    return requests.get(
        _STATS_URL,
        headers={
            "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0"
        },
    ).json()


def items_from_web():
    _STATS_URL = "https://www.pathofexile.com/api/trade/data/items"
    return requests.get(
        _STATS_URL,
        headers={
            "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0"
        },
    ).json()


stats = {
    mod_dict["id"]: mod_dict["text"]
    for stat_dict in stats_from_web()["result"]
    for mod_dict in stat_dict["entries"]
}
items = items_from_web()["result"]


uniques = sorted(
    [
        x["name"]
        for y in items
        for x in y["entries"]
        if x.get("flags", {}).get("unique", False)
    ]
)

stats["explicit.stat_2120904498"] = "# to Level of all Raise Skeleton Gems"
stats["implicit.stat_125218179"] = "# to maximum number of Spectres"
stats["crafted.stat_125218179"] = "# to maximum number of Spectres"
stats["implicit.stat_2428829184"] = "# to maximum number of Skeletons"

stats[
    "explicit.stat_3102860761"
] = "#% increased Movement Speed for # seconds on Throwing a Trap"
stats[
    "explicit.stat_723388324"
] = "#% chance to Trigger Socketed Spells when\nyou Spend at least # Mana to Use a Skill"
