import json
from PoEQuery.official_api_result import Mod, OfficialApiResult
from PoEQuery.official_api import fetch_results, search_query
from PoEQuery.official_api_query import StatFilters, OfficialApiQuery
from PoEQuery.affix_finder import find_affixes
from tqdm import tqdm


def estimate_price_in_chaos(price):
    if price.currency == "alch":
        return price.amount * 0.2
    elif price.currency == "chaos":
        return price.amount * 1
    elif price.currency == "exalted":
        return price.amount * 100
    elif price.currency == "mirror":
        return price.amount * 100 * 420
    else:
        # print(price)
        return None


from pandas import DataFrame

results_df = DataFrame()

life_mod = Mod(
    {
        "name": "",
        "tier": "",
        "magnitudes": [{"hash": "explicit.stat_983749596", "min": 4, "max": 6}],
    }
)
mana_mod = Mod(
    {
        "name": "",
        "tier": "",
        "magnitudes": [{"hash": "explicit.stat_2748665614", "min": 4, "max": 6}],
    }
)
es_mod = Mod(
    {
        "name": "",
        "tier": "",
        "magnitudes": [{"hash": "explicit.stat_2482852589", "min": 4, "max": 6}],
    }
)

mods = find_affixes(
    OfficialApiQuery(name="Watcher's Eye", type="Prismatic Jewel", identified=True),
    affix_type="explicit",
    exclude_affixes=[life_mod, mana_mod, es_mod],
    use_added_filter_for_speed=False,
)

for mod in tqdm(mods):
    results_entry = {"mod_str": str(mod), "mod_json": json.dumps(mod.json())}
    mod_stat_filters = StatFilters(filters=mod.to_query_stat_filters())
    fetch_ids, total, query = search_query(
        OfficialApiQuery(
            name="Watcher's Eye",
            type="Prismatic Jewel",
            identified=True,
            corrupted=False,
            indexed="2week",
            stat_filters=[mod_stat_filters],
        ).json()
    )
    print(total)
    results = fetch_results(fetch_ids)

    for idx, result in enumerate(results):
        parsed_result = OfficialApiResult(result)
        results_entry[f"price_{idx}"] = estimate_price_in_chaos(parsed_result.price)

    results_df = results_df.append(results_entry, ignore_index=True)
results_df.to_csv(f"data/watchers_eyes.csv")
