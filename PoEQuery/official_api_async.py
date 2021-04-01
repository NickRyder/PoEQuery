import asyncio
import logging
from asyncio import Lock
from asyncio.events import AbstractEventLoop
from asyncio.futures import Future
from collections import defaultdict, deque
from typing import Dict, List

import requests

from PoEQuery import league_id, poesessid, realm, user_agent
from PoEQuery.x_rate_limiter import rate_limited

USER_AGENT_HEADER = {"user-agent": user_agent}

API_FETCH = "https://www.pathofexile.com/api/trade/fetch"

API_SEARCH = "https://www.pathofexile.com/api/trade/search"

API_STASH = "https://www.pathofexile.com/character-window/get-stash-items"

API_CHARACTER = "https://www.pathofexile.com/character-window/get-characters"

API_PASSIVE = "https://www.pathofexile.com/character-window/get-passive-skills"

API_ITEM = "https://www.pathofexile.com/character-window/get-items"


@rate_limited("trade-search-request-limit")
def search(query: dict = None) -> requests.Response:
    query = {} if query is None else query
    return requests.post(
        f"{API_SEARCH}/{league_id}",
        headers=USER_AGENT_HEADER,
        json=query,
        cookies=dict(POESESSID=poesessid),
    )


@rate_limited("trade-fetch-request-limit")
def fetch(item_ids: List[str]) -> requests.Response:
    return requests.get(
        f"{API_FETCH}/{','.join(item_ids)}",
        headers=USER_AGENT_HEADER,
        cookies=dict(POESESSID=poesessid),
    )


@rate_limited("backend-item-request-limit")
def stash_tab(params: dict) -> requests.Response:
    return requests.get(
        url=API_STASH,
        params=params,
        headers=USER_AGENT_HEADER,
        cookies=dict(POESESSID=poesessid),
    )


@rate_limited("backend-character-request-limit")
def characters(account_name: str, realm: str = realm) -> requests.Response:
    params = {"accountName": account_name, "realm": realm}
    return requests.get(API_CHARACTER, params=params, headers=USER_AGENT_HEADER)


def passive_tree(
    account_name: str, character_name: str, realm: str = realm
) -> requests.Response:
    params = {
        "accountName": account_name,
        "realm": realm,
        "character": character_name,
    }
    return requests.get(
        API_PASSIVE,
        params=params,
        headers=USER_AGENT_HEADER,
        cookies=dict(POESESSID=poesessid),
    )


@rate_limited("backend-item-request-limit")
def items(
    account_name: str, character_name: str, realm: str = realm
) -> requests.Response:
    params = {"accountName": account_name, "character": character_name, "realm": realm}
    return requests.get(API_ITEM, params=params, headers=USER_AGENT_HEADER)


###
# Batched Fetching
###

"""
To maximize our fetches per second, we want to batch as many fetches as we can.
To accomplish this we create a global queue of fetches `to_fetch_queue`
Everytime we submit a list of item_ids, it gets added to the global queue as asyncio.Futures

While not all our futures are done, we send `_fetch_batched` which is wrapped with a rate limit respecter
once done awaiting the rate limit, the inner function is executed, which pops of 10 items from the queue
it then sets the results of the Futures it pops off with the results from the request.get

In fetch_batched, after creating the futures, and awaiting `_fetch_batched`, we
await the results of the futures, and then return them.
"""

to_fetch_queue: deque = deque()
fetch_queue_lock: Dict[AbstractEventLoop, Lock] = defaultdict(Lock)


class ItemFuture(Future):
    item_id: str

    def __init__(self, item_id):
        self.item_id = item_id
        super().__init__()


async def fetch_batched(item_ids: List[str]) -> List[dict]:
    item_futures: List[ItemFuture] = []
    for item_id in item_ids:
        item_future: ItemFuture = ItemFuture(item_id)
        item_futures.append(item_future)
        to_fetch_queue.append(item_future)

    async with fetch_queue_lock[asyncio.get_running_loop()]:
        all_done = all([item_future.done() for item_future in item_futures])
        while not all_done:
            await _fetch_batched()
            all_done = all([item_future.done() for item_future in item_futures])

    returned_results = []
    for item_future in item_futures:
        returned_item = await item_future
        if returned_item is None:
            logging.warning(f"received null result from fetch: {item_future.item_id}")
        else:
            assert returned_item["id"] == item_future.item_id
        returned_results.append(returned_item)
    return returned_results


@rate_limited("trade-fetch-request-limit")
def _fetch_batched() -> requests.Response:
    assert len(to_fetch_queue) > 0, "queue should be populated"
    item_futures = []
    for _ in range(10):
        try:
            item_futures.append(to_fetch_queue.popleft())
        except IndexError:
            pass

    item_ids = [item_future.item_id for item_future in item_futures]
    result = requests.get(
        f"{API_FETCH}/{','.join(item_ids)}",
        headers=USER_AGENT_HEADER,
        cookies=dict(POESESSID=poesessid),
    )
    for item_result, item_future in zip(result.json()["result"], item_futures):
        item_future.set_result(item_result)
    return result
