from enum import unique
import json
from PoEQuery.official_api_result import Mod, OfficialApiResult
from PoEQuery.official_api import fetch_results, search_query
from PoEQuery.official_api_query import StatFilters, OfficialApiQuery
from PoEQuery.affix_finder import find_affixes
from tqdm import tqdm

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

def sanitize(string):
    return string.lower().replace(" ", "_").replace("'", "")


from pandas import DataFrame

results_df = DataFrame()

# remaining_use_mod = Mod({'name': '', 'tier': '', 'magnitudes': [{'hash': 'explicit.stat_1479533453', 'min': 15, 'max': 15}]})

watchstones = [
 "Platinum Glennach Cairns Watchstone", 
 "Platinum Haewark Hamlet Watchstone", 
 "Platinum Lex Ejoris Watchstone", 
 "Platinum Lex Proxima Watchstone", 
 "Platinum Lira Arthain Watchstone", 
 "Platinum New Vastir Watchstone", 
 "Platinum Tirn's End Watchstone", 
 "Platinum Valdo's Rest Watchstone",
 "Chromium Glennach Cairns Watchstone", 
 "Chromium Haewark Hamlet Watchstone", 
 "Chromium Lex Ejoris Watchstone", 
 "Chromium Lex Proxima Watchstone", 
 "Chromium Lira Arthain Watchstone", 
 "Chromium New Vastir Watchstone", 
 "Chromium Tirn's End Watchstone", 
 "Chromium Valdo's Rest Watchstone",
 "Titanium Glennach Cairns Watchstone", 
 "Titanium Haewark Hamlet Watchstone", 
 "Titanium Lex Ejoris Watchstone", 
 "Titanium Lex Proxima Watchstone", 
 "Titanium Lira Arthain Watchstone", 
 "Titanium New Vastir Watchstone", 
 "Titanium Tirn's End Watchstone", 
 "Titanium Valdo's Rest Watchstone"]

for type in watchstones:
    print(type)
    mods = find_affixes(OfficialApiQuery(type=type, identified=True, rarity="nonunique"), affix_type="explicit")

    for mod in tqdm(mods):
        results_entry = {"mod_str": str(mod), "mod_json": json.dumps(mod.to_json())}
        mod_stat_filters = StatFilters(filters=mod.to_query_stat_filters())
        fetch_ids, total, query = search_query(OfficialApiQuery(type=type, identified=True, rarity="nonunique", mirrored=False, enchanted=False, corrupted=False, indexed="2week", stat_filters=[mod_stat_filters]).to_json())
        print(total)
        results = fetch_results(fetch_ids)

        for idx, result in enumerate(results):
            parsed_result = OfficialApiResult(result)
            results_entry[f"price_{idx}"] = estimate_price_in_chaos(parsed_result.price)
        
        results_df = results_df.append(results_entry, ignore_index=True)
    results_df.to_csv(f"data/watchstones/{sanitize(type)}.csv")

