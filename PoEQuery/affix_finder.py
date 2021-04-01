from typing import List, Set
from PoEQuery.official_api import search_query, fetch_results
from PoEQuery.official_api_query import OfficialApiQuery, StatFilter, StatFilters
from PoEQuery.official_api_result import Mod, OfficialApiResult

import logging

from itertools import combinations

added_filters = {
    "implicit": StatFilters(
        filters={StatFilter(id="pseudo.pseudo_number_of_implicit_mods", min=1)}
    ),
    "explicit": StatFilters(
        filters={StatFilter(id="pseudo.pseudo_number_of_affix_mods", min=1)}
    ),
    "fractured": StatFilters(),
}


def simplify_stat_filter(
    stat_filters: Set[StatFilter], threshold: float = 1.0
) -> Set[StatFilter]:
    """
    takes in a list of stat_filters and attempts to simplify them by merging contiguous stat filters
    """
    while True:
        for stat_filter_1, stat_filter_2 in combinations(stat_filters, 2):
            if stat_filter_1.id == stat_filter_2.id:
                # Two types of collisions:
                # xxxxxx
                #     000000
                #
                # xxxxxxxxxx
                #   000000
                # min <= max + threshold
                assert (
                    stat_filter_1.min is not None
                    and stat_filter_1.max is not None
                    and stat_filter_2.max is not None
                    and stat_filter_2.min is not None
                ), "stat filters must have both min and max"

                overlap_check_1 = stat_filter_1.min <= stat_filter_2.max + threshold
                overlap_check_2 = stat_filter_2.min <= stat_filter_1.max + threshold

                if overlap_check_1 or overlap_check_2:
                    # replace set of stat filters with all others + combined
                    other_stat_filters = {
                        stat_filter
                        for stat_filter in stat_filters
                        if stat_filter != stat_filter_1 and stat_filter != stat_filter_2
                    }
                    combined_stat_filter = StatFilter(
                        id=stat_filter_1.id,
                        min=min(stat_filter_1.min, stat_filter_2.min),
                        max=max(stat_filter_1.max, stat_filter_2.max),
                    )
                    other_stat_filters.add(combined_stat_filter)
                    stat_filters = other_stat_filters
                    break

        else:
            return stat_filters


def find_affixes(
    official_query: OfficialApiQuery,
    affix_type: str = "explicit",
    exclude_affixes: List[Mod] = [],
    use_added_filter_for_speed: bool = True,
) -> Set[Mod]:
    stat_filter = StatFilters(filters=set(), type="not")

    if use_added_filter_for_speed:
        official_query.stat_filters.append(added_filters[affix_type])
    official_query.stat_filters.append(stat_filter)

    found_mods: Set[Mod] = set()

    fetch_ids, total, query = search_query(official_query.to_json())
    results = fetch_results(fetch_ids)

    if not results and use_added_filter_for_speed:
        logging.warn(
            "For unique items you might need to set use_added_filter_for_speed=False"
        )

    added_mod = True
    while results and added_mod:
        added_mod = False
        new_found_mods = set()
        for result in results:
            parsed_result = OfficialApiResult(result)
            print(parsed_result)
            for mod in parsed_result.__getattribute__(f"{affix_type}s"):
                if mod not in exclude_affixes:
                    new_found_mods.add(mod)
        if found_mods & new_found_mods:
            logging.warning(
                f"found a mod that should be excluded: {found_mods & new_found_mods} (for jewelry, try setting quality_max=0)"
            )
        added_mod = len(new_found_mods.difference(found_mods)) > 0
        found_mods = found_mods | new_found_mods
        stat_filter.filters = simplify_stat_filter(
            {
                stat_filter
                for mod in found_mods
                for stat_filter in mod.to_query_stat_filters()
            }
        )
        print(f"found {len(new_found_mods)} new mods, blocking {len(found_mods)} mods")
        fetch_ids, total, query = search_query(official_query.to_json())
        results = fetch_results(fetch_ids)

    return found_mods
