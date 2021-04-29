import asyncio
from PoEQuery.official_api_query import StatFilters, OfficialApiQuery
from PoEQuery.affix_finder import find_affixes
from tqdm import tqdm
from PoEQuery.query_generator import bisect_count_one_mod

from PoEQuery.official_api import (
    fetch_query_with_query_dividers,
)

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
    "Titanium Valdo's Rest Watchstone",
]

t = tqdm(watchstones)
for type in t:
    t.set_description(desc=f"watchstone - {type}")

    mods = find_affixes(
        OfficialApiQuery(type=type, identified=True, rarity="nonunique"),
        affix_type="explicit",
    )
    all_query = OfficialApiQuery(
        type=type,
        # identified=True,
        rarity="nonunique",
        # mirrored=False,
        # enchanted=False,
        # corrupted=False,
        indexed="2weeks",
        stat_filters=[
            StatFilters(
                [
                    stat_filter
                    for mod in mods
                    for stat_filter in mod.to_query_stat_filters()
                ],
                type="count",
                min=1,
            )
        ],
    )

    # results = search_and_fetch_batched(queries)
    asyncio.run(fetch_query_with_query_dividers(all_query, [bisect_count_one_mod]))
