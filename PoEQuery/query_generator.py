import logging
from typing import List
from PoEQuery.official_api_query import OfficialApiQuery
from string import ascii_lowercase
from copy import deepcopy


def get_subdict_from_key_list(dict, key_list):
    sub_dict = dict
    for key in key_list:
        if key not in sub_dict:
            sub_dict[key] = {}
        sub_dict = sub_dict[key]
    return sub_dict


def get_stat_subdict(dict, stat_id):
    if "stats" not in dict["query"]:
        dict["query"]["stats"] = []

    for stat_dict in dict["query"]["stats"]:
        if stat_dict["type"] == "and" and len(stat_dict["filters"]) == 1:
            filter = stat_dict["filters"][0]
            if filter["id"] == stat_id and not filter["disabled"]:
                return filter["value"]

    # didnt exist
    dict["query"]["stats"].append(
        {
            "type": "and",
            "filters": [
                {
                    "id": stat_id,
                    "value": {},
                    "disabled": False,
                }
            ],
        }
    )

    return dict["query"]["stats"][-1]["filters"][0]["value"]


def round(value, precision):
    return int(value * (10 ** precision)) / 10 ** precision


def generate_by_stat_range(
    query, stat_id, default_min_value, default_max_value, rounding_precision=2
):
    """
    Specificy a range in the query using a list of keys
    Then generate two finer queries by splitting this range
    Return nothing if range < .01

    query - query dict
    key_list - list of keys to get to range
    default_min_value - default min if the entry doesnt exist
    default_max_value - default max if the entry doesnt exist
    """
    query_copy = deepcopy(query)
    sub_dict = get_stat_subdict(query_copy, stat_id)
    return generate_by_range_from_subdict(
        query_copy,
        sub_dict,
        default_min_value,
        default_max_value,
        rounding_precision=rounding_precision,
    )


def generate_by_range(
    query, key_list, default_min_value, default_max_value, rounding_precision=2
):
    """
    Specificy a range in the query using a list of keys
    Then generate two finer queries by splitting this range
    Return nothing if range < .01

    query - query dict
    key_list - list of keys to get to range
    default_min_value - default min if the entry doe    snt exist
    default_max_value - default max if the entry doesnt exist
    """
    query_copy = deepcopy(query)
    sub_dict = get_subdict_from_key_list(query_copy, key_list)
    return generate_by_range_from_subdict(
        query_copy,
        sub_dict,
        default_min_value,
        default_max_value,
        rounding_precision=rounding_precision,
    )


def generate_by_range_from_subdict(
    query, sub_dict, default_min_value, default_max_value, rounding_precision=2
):
    min_value = sub_dict["min"] if "min" in sub_dict else default_min_value
    max_value = sub_dict["max"] if "max" in sub_dict else default_max_value
    if max_value - min_value >= 10 ** (-rounding_precision):
        sub_dict["min"] = min_value
        sub_dict["max"] = round((min_value + max_value) / 2, rounding_precision)
        new_query_low = deepcopy(query)

        sub_dict["min"] = round(
            (min_value + max_value) / 2, rounding_precision
        ) + 10 ** (-rounding_precision)
        sub_dict["max"] = max_value
        new_query_high = deepcopy(query)
        return [new_query_low, new_query_high]
    else:
        return []


def generate_by_roll_ranges(query, result):
    hash_to_range = {}

    mods = result["item"]["extended"]["mods"]
    for mod_type, mods_of_type in mods.items():
        for mod in mods_of_type:
            for magnitude in mod["magnitudes"]:
                if magnitude["hash"] not in hash_to_range:
                    hash_to_range[magnitude["hash"]] = [0, 0]
                    hash_to_range[magnitude["hash"]][0] += magnitude["min"]
                    hash_to_range[magnitude["hash"]][1] += magnitude["max"]

    query_copy = deepcopy(query)
    for mod_hash, range_ in hash_to_range.items():
        min_, max_ = range_
        min_, max_ = min(min_, max_), max(min_, max_)
        sub_dict = get_stat_subdict(query_copy, mod_hash)
        current_min = sub_dict.get("min", min_)
        current_max = sub_dict.get("min", max_)

        # we try to split, and if we cant, we move onto the next hash
        possible_splits = generate_by_stat_range(
            query, mod_hash, current_min, current_max
        )
        if possible_splits:
            return possible_splits

    return []


def bisect_count_one_mod(query: OfficialApiQuery) -> List[OfficialApiQuery]:
    """
    Query must have one stat_filter which is a count

    """
    assert (
        len(query.stat_filters) == 1
    ), "bisect_count_one_mod expects only one stat filter"
    assert (
        query.stat_filters[0].type == "count"
    ), "bisect_count_one_mod expects a count filter"

    count_stat_filters = query.stat_filters[0]
    if len(count_stat_filters.filters) > 1:

        n_filters = len(count_stat_filters.filters)
        logging.info(f"Bisecting {n_filters} mods")
        left_filters = count_stat_filters.filters[: n_filters // 2]
        right_filters = count_stat_filters.filters[n_filters // 2 :]

        left_query_copy, right_query_copy = deepcopy(query), deepcopy(query)
        left_query_copy.stat_filters[0].filters = left_filters
        right_query_copy.stat_filters[0].filters = right_filters

        return [left_query_copy, right_query_copy]
    else:
        return []


from functools import partial

generate_by_price = partial(
    generate_by_range,
    key_list=["query", "filters", "trade_filters", "filters", "price"],
    default_min_value=0,
    default_max_value=150 * 150,
    rounding_precision=0,
)
generate_by_ilvl = partial(
    generate_by_range,
    key_list=["query", "filters", "misc_filters", "filters", "ilvl"],
    default_min_value=0,
    default_max_value=100,
    rounding_precision=0,
)
