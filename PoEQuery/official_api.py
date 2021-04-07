import logging
from PoEQuery.official_api_query import OfficialApiQuery
from typing import Callable, List, Optional
from PoEQuery.official_api_async import search
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
        total = response_json["total"]
    except KeyError:
        if use_cached:
            return await search_query_async(query, False)
        else:
            logging.error(f"Key Error on {query}")
            raise

    return fetch_ids, total, query


async def recurse_fetch_query_with_query_divider(
    query: OfficialApiQuery,
    query_dividers: List[Callable[[OfficialApiQuery], List[OfficialApiQuery]]],
    fetch_queries_tqdm: Optional[tqdm] = None,
):

    fetch_ids, total, query = await search_query_async(query)

    if fetch_queries_tqdm is None:
        fetch_queries_tqdm = tqdm(total=total, desc="recurse fetch count")

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
                        ) = await recurse_fetch_query_with_query_divider(
                            finer_query, query_dividers, fetch_queries_tqdm
                        )
                        fetch_ids = new_fetch_ids + fetch_ids
                        unsplit_queries += new_unsplit_queries
                break
        else:
            unsplit_queries += [query]

        return fetch_ids, unsplit_queries
    else:
        fetch_queries_tqdm.update(len(fetch_ids))
        return fetch_ids, unsplit_queries


def search_and_fetch_batched(queries: List[OfficialApiQuery]):
    async def _boilerplate():
        return await asyncio.gather(
            *[search_and_fetch_async(query) for query in queries]
        )

    return asyncio.run(_boilerplate())


async def search_and_fetch_async(query: OfficialApiQuery):
    fetch_ids, total, query = await search_query_async(query)
    return await fetch_batched(fetch_ids)
