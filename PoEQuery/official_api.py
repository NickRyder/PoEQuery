import logging
from PoEQuery.official_api_query import OfficialApiQuery
from typing import Callable, List, Optional, Tuple
from PoEQuery.official_api_async import fetch, search
from PoEQuery.batched_fetch import fetch_batched

import asyncio
from tqdm import tqdm  # type: ignore


async def search_query_async(query: OfficialApiQuery, use_cached=True):
    """
    We do a single retry if use_cached=True

    This prevents us from recalling data from error results

    TODO: need more robust validation before caching
    """
    response = await search(query, use_cached=use_cached)
    response_json = response.json()
    try:
        query = response_json["query"]
    except KeyError:
        pass

    try:
        fetch_ids = response_json["result"]
        logging.info(f"Complexity {response_json['complexity']}")
        total = response_json["total"]
    except KeyError:
        if use_cached:
            return await search_query_async(query, False)
        else:
            logging.error(f"Key Error on {query}")
            raise

    return fetch_ids, total, query


async def fetch_query_with_query_dividers(
    query: OfficialApiQuery,
    query_dividers: List[Callable[[OfficialApiQuery], List[OfficialApiQuery]]],
):
    (
        fetch_ids,
        fetch_promises,
    ) = await _recurse_fetch_query_with_query_dividers(query, query_dividers)

    fetched_results = []
    for fetch_promise in fetch_promises:
        fetched_results += await fetch_promise

    return fetched_results


async def _recurse_fetch_query_with_query_dividers(
    query: OfficialApiQuery,
    query_dividers: List[Callable[[OfficialApiQuery], List[OfficialApiQuery]]],
    fetch_queries_tqdm: Optional[tqdm] = None,
) -> Tuple[List[str], List[OfficialApiQuery], List[asyncio.Task]]:

    fetch_ids, total, query = await search_query_async(query)

    # launches a side task to go fetch the ids
    fetch_promises: List[asyncio.Task] = [asyncio.create_task(fetch_batched(fetch_ids))]

    if total > 100:
        seen_fetch_ids = set(fetch_ids)
        for query_divider in query_dividers:
            finer_queries = query_divider(query)
            if finer_queries:
                for finer_query in finer_queries:
                    if len(seen_fetch_ids) == total:
                        # no need to recurse further, already found all
                        break
                    else:
                        (
                            new_fetch_ids,
                            new_fetch_promise,
                        ) = await _recurse_fetch_query_with_query_dividers(
                            finer_query, query_dividers, fetch_queries_tqdm
                        )
                        seen_fetch_ids |= set(new_fetch_ids)
                        fetch_promises += new_fetch_promise
                break
        else:
            logging.warn(f"Unsplit query: {query}")

        return list(seen_fetch_ids), fetch_promises
    else:
        return fetch_ids, fetch_promises


def search_and_fetch_batched(queries: List[OfficialApiQuery]):
    async def _boilerplate():
        return await asyncio.gather(
            *[search_and_fetch_async(query) for query in queries]
        )

    return asyncio.run(_boilerplate())


async def search_and_fetch_async(query: OfficialApiQuery):
    fetch_ids, total, query = await search_query_async(query)
    return await fetch_batched(fetch_ids)
