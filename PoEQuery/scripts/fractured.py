import asyncio
import json
from PoEQuery.official_api_result import OfficialApiResult
from PoEQuery.official_api import search_and_fetch_async
from PoEQuery.official_api_query import StatFilters, OfficialApiQuery
from PoEQuery.affix_finder import find_affixes
from pandas import DataFrame


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


item_classes = dict(
    # BOW = "weapon.bow",
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


for item_class_key, item_class_value in item_classes.items():
    print(item_class_key)
    queries = []
    results_df = DataFrame()

    async def search_and_fetch_and_price(mod):
        results_entry = {"mod_str": str(mod), "mod_json": json.dumps(mod.to_json())}
        mod_stat_filters = StatFilters(filters=mod.to_query_stat_filters())
        query = OfficialApiQuery(
            category=item_class_value,
            corrupted=False,
            indexed="1week",
            mirrored=False,
            rarity="nonunique",
            stat_filters=[mod_stat_filters],
        ).to_json()

        results = await search_and_fetch_async(query)
        print(results_entry["mod_str"])
        for idx, result in enumerate(results):
            parsed_result = OfficialApiResult(result)
            results_entry[f"price_{idx:02}"] = estimate_price_in_chaos(
                parsed_result.price
            )

        global results_df
        results_df = results_df.append(results_entry, ignore_index=True)
        return results_entry

    mods = find_affixes(
        OfficialApiQuery(
            category=item_class_value,
            corrupted=False,
            fractured=True,
            quality_max=0,
            rarity="nonunique",
        ),
        affix_type="fractured",
    )

    async def main():
        await asyncio.gather(*[search_and_fetch_and_price(mod) for mod in mods])
        results_df.to_csv(f"data/frac_prices/{item_class_key}.csv")

    asyncio.run(main())
