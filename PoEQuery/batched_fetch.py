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

import asyncio
from functools import lru_cache
import logging
from asyncio.futures import Future
from collections import deque
from typing import Dict, List

import time

from tqdm import tqdm  # type: ignore

import requests

from PoEQuery import __diskcache_path__, poesessid, user_agent
from PoEQuery.x_rate_limiter import TqdmLock, rate_limited

from PoEQuery.cache import cache_results

USER_AGENT_HEADER = {"user-agent": user_agent}

API_FETCH = "https://www.pathofexile.com/api/trade/fetch"


class ItemFuture(Future):
    item_id: str

    def __init__(self, item_id):
        self.item_id = item_id
        super().__init__()


# TODO: wrap these in a class?
to_fetch_queue: deque = deque()
to_fetch_id_to_future: Dict[str, ItemFuture] = dict()
desc_to_tqdm: Dict[str, tqdm] = dict()


@lru_cache(maxsize=1)
def fetch_queue_lock_lazy() -> TqdmLock:
    return TqdmLock(tqdm(total=0, desc="trade-fetch-request-limit"))


async def fetch_batched(item_ids: List[str], use_cached=True) -> List[dict]:
    return await asyncio.gather(
        *[queue_single_fetch(item_id, use_cached=use_cached) for item_id in item_ids]
    )


@cache_results("fetch_results", key=lambda item_id: item_id)
async def queue_single_fetch(
    item_id: str,
) -> List[dict]:
    if item_id not in to_fetch_id_to_future:
        item_future: ItemFuture = ItemFuture(item_id)
        to_fetch_queue.append(item_future)
        to_fetch_id_to_future[item_id] = item_future
    else:
        logging.info(f"Item already in queue to be fetched: {item_id}")
        item_future = to_fetch_id_to_future[item_id]

    async with fetch_queue_lock_lazy():
        while not item_future.done():
            await _fetch_batched()

    returned_item = await item_future
    if returned_item is None:
        logging.warning(f"Received null result from fetch: {item_future.item_id}")
    else:
        assert returned_item["id"] == item_future.item_id
    return returned_item


# don't use tqdm here, since we have an outer TqdmLock
@rate_limited("trade-fetch-request-limit", use_tqdm=False)
def _fetch_batched() -> requests.Response:
    assert len(to_fetch_queue) > 0, "queue should be populated"
    item_futures = []
    for _ in range(10):
        try:
            item_future = to_fetch_queue.popleft()
            item_futures.append(item_future)
            del to_fetch_id_to_future[item_future.item_id]
        except IndexError:
            pass
    item_ids = [item_future.item_id for item_future in item_futures]
    response = requests.get(
        f"{API_FETCH}/{','.join(item_ids)}",
        headers=USER_AGENT_HEADER,
        cookies=dict(POESESSID=poesessid),
    )

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logging.warning(e)

    for item_result, item_future in zip(response.json()["result"], item_futures):
        item_future.set_result(item_result)
    return response


if __name__ == "__main__":
    item_ids = [
        "388785b8862730a8f112bfa62e6e207d44d39c7585de5cc7f81f18c21d5498e9",
        "2d0d4561e3074cfe7e1b7a836108248bab54902b1c8f3fc04e407d8e4b679703",
        "269a8332f4af43ee2c244486d9e5f84d7b0e0319a758ca86e5f8cca5250fbc7c",
        "859de7bbf3724b20b5ed1a07d15c1ef29bdad613b0d4904e5857d199e898bcab",
        "d3be0b726851c592597a0d188d75e258e41a54796c77fa9cb02d70b69cabdd30",
        "43e3ebf23e01d98d3ffc1622a470359f6300ff32c78d9174475e213768a8cbc3",
        "9db224474ff9183e70c1ddefa4e8c0bd6a0fa6e4cf053bb83f9017d1642367ed",
        "26ecb874399777d4a28e314b0773f87205997ea60bf0c49cf73b1e65b0661226",
        "8293b6469e1f2f983def6835f179264d45752bd538113ce3612a3f6e90c732a1",
        "ac26f737f496ea4140ebefbb727bd3466530afa704b65085a07f4fa5d78c28a1",
    ]

    for _ in range(10):
        asyncio.run(fetch_batched(item_ids * 2))
        time.sleep(1)
