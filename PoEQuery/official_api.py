from typing import Optional
from PoEQuery.official_api_async import search, fetch, fetch_batched
from PoEQuery import league_id

import asyncio
from tqdm import tqdm


API_FETCH = "https://www.pathofexile.com/api/trade/fetch"
STASH_URL = "https://www.pathofexile.com/character-window/get-stash-items"


async def search_query_async(query):

    response = await search(query)

    response_json = response.json()
    try:
        query = response_json["query"]
    except KeyError:
        pass
    fetch_ids = response_json["result"]
    total = response_json["total"]

    return fetch_ids, total, query


def search_query(query):
    return asyncio.run(search_query_async(query))


def recurse_fetch_query_with_query_divider(query, query_dividers):
    global fetch_queries_tqdm

    fetch_queries_tqdm = None

    return _recurse_fetch_query_with_query_divider(query, query_dividers)


def _recurse_fetch_query_with_query_divider(query, query_dividers):
    global fetch_queries_tqdm

    fetch_ids, total, query = search_query(query)

    if fetch_queries_tqdm is None:
        fetch_queries_tqdm = tqdm(total=total)

    unsplit_queries = []

    if total > 100:
        for query_divider in query_dividers:
            finer_queries = query_divider(query)
            if finer_queries:
                for finer_query in finer_queries:

                    if len(fetch_ids) == total:
                        # no need to recurse further, already found all
                        break
                    else:
                        (
                            new_fetch_ids,
                            new_unsplit_queries,
                        ) = _recurse_fetch_query_with_query_divider(
                            finer_query, query_dividers
                        )
                        fetch_ids = new_fetch_ids | fetch_ids
                        unsplit_queries += new_unsplit_queries
                break
        else:
            unsplit_queries += [query]

        return fetch_ids, unsplit_queries
    else:
        fetch_queries_tqdm.update(len(fetch_ids))
        return fetch_ids, unsplit_queries


def fetch_results(fetch_ids):
    return asyncio.run(_fetch_results(fetch_ids))


async def _fetch_results(fetch_ids, fetch_results_tqdm: Optional[tqdm] = None):
    fetch_ids = list(fetch_ids)
    if fetch_ids:
        if fetch_results_tqdm is None:
            fetch_results_tqdm = tqdm(total=len(fetch_ids))

        batch = fetch_ids[-10:]
        del fetch_ids[-10:]
        result = await fetch(batch)
        result_json = result.json()

        fetch_results_tqdm.update(len(batch))

        try:
            return result_json["result"] + await _fetch_results(
                fetch_ids, fetch_results_tqdm
            )
        except KeyError:
            print(result_json)
            raise KeyError("result not key in response json")
    else:
        fetch_results_tqdm = None
        return []


async def search_and_fetch_async(query: dict):
    fetch_ids, total, query = await search_query_async(query)
    return await fetch_batched(fetch_ids)


if __name__ == "__main__":
    print(
        search_query(
            {
                "query": {
                    "status": {"option": "online"},
                    "stats": [{"type": "and", "filters": []}],
                },
                "sort": {"price": "asc"},
            }
        )
    )
