from asyncio.futures import Future
from collections import defaultdict, deque
import logging
from typing import Callable
import requests
import asyncio
from asyncio import Lock
import time

from requests.api import request

from PoEQuery import x_rate_limiter
from PoEQuery import poesessid, user_agent

USER_AGENT_HEADER = {"user-agent": user_agent}

API_FETCH = "https://www.pathofexile.com/api/trade/fetch"

# global objects which keep track of the wait time needed for the x_rate_policy
# the lock should be used for accessing, waiting, and modifying the wait time
# asyncio gets mad if you create a lock in a different loop, so i need to enumerate
# the locks by loop.
# **IMPORTANT** THIS WILL NOT WORK FOR ANY TYPE OF CONCURRENCY BEYOND ASYNCIO
locks_by_policy = defaultdict(lambda: defaultdict(Lock))
wait_times_by_policy = defaultdict(int)


def rate_limited(x_rate_policy):
    def rate_limited_decorator(
        function: Callable[..., requests.Response]
    ) -> Callable[..., requests.Response]:
        async def rate_limited_function(*args, **kwargs):
            request_lock = locks_by_policy[asyncio.get_running_loop()][x_rate_policy]
            async with request_lock:
                request_wait_time = wait_times_by_policy[x_rate_policy]
                if request_wait_time is not None:
                    wait_time = max(0, request_wait_time - time.monotonic())
                    await asyncio.sleep(wait_time)

                response = function(*args, **kwargs)
                try:
                    response.raise_for_status()
                except requests.exceptions.HTTPError as e:
                    logging.warn(e)

                wait_time = x_rate_limiter.time_to_wait_on_new_response(
                    response, x_rate_policy
                )
                wait_times_by_policy[x_rate_policy] = time.monotonic() + wait_time
                return response

        return rate_limited_function

    return rate_limited_decorator


API_TRADE = "https://www.pathofexile.com/api/trade/search"


@rate_limited("trade-search-request-limit")
def search(league_id: str, query: dict = None) -> requests.Response:
    query = {} if query is None else query
    return requests.post(
        f"{API_TRADE}/{league_id}",
        headers=USER_AGENT_HEADER,
        json=query,
        cookies=dict(POESESSID=poesessid),
    )


@rate_limited("trade-fetch-request-limit")
def fetch(url):
    return requests.get(
        url, headers=USER_AGENT_HEADER, cookies=dict(POESESSID=poesessid)
    )


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

to_fetch_queue = deque()
fetch_queue_lock = defaultdict(Lock)


def _get_search_link_from_item_ids(item_ids):
    item_ids_str = ",".join(item_ids)
    return f"{API_FETCH}/{item_ids_str}"


async def fetch_batched(item_ids):
    item_futures = []
    for item_id in item_ids:
        item_future = Future()
        item_future.__setattr__("item_id", item_id)
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
            logging.warn(f"received null result from fetch: {item_future.item_id}")
        else:
            assert returned_item["id"] == item_future.item_id
        returned_results.append(returned_item)
    return returned_results


@rate_limited("trade-fetch-request-limit")
def _fetch_batched():
    assert len(to_fetch_queue) > 0, "queue should be populated"
    item_futures = []
    for _ in range(10):
        try:
            item_futures.append(to_fetch_queue.popleft())
        except IndexError:
            pass

    url = _get_search_link_from_item_ids(
        [item_future.item_id for item_future in item_futures]
    )
    print(len(item_futures))
    result = requests.get(
        url, headers=USER_AGENT_HEADER, cookies=dict(POESESSID=poesessid)
    )
    for item_result, item_future in zip(result.json()["result"], item_futures):
        item_future.set_result(item_result)
    return result


@rate_limited("backend-item-request-limit")
def stash_tab(url, params):
    return requests.get(
        url=url,
        params=params,
        headers=USER_AGENT_HEADER,
        cookies=dict(POESESSID=poesessid),
    )


if __name__ == "__main__":

    item_ids = [
        "229ec3ed6037b122ef54d922fdc9c0ae8eaab590da5dc29fec9139803b2da442",
        "9801a885b860bc01c5481185a73de06b4faecbd1966b69c3695b858128df4ae2",
        "9821eb040c5d6ad5a1849dc47f63d0ef4d6acbce191390142d4fce6ce677d85f",
        "3c09140f706df93ce4114cb9d1177be459567d5d85b1ae508053271aeef9d114",
        "d66d2843e490b7b51699487d74f984015a833df8bbb0b25d062ede926b439d2b",
        "2cb36a3f83d1049e843a495ba5b9ee62cb037fe7bb578815cb6b8e8d2248ff5e",
        "9253d0a427243d42e0b7d9de7f470cafc913372ef3c685bb0812500eccd7461b",
        "e3b33f355aff873996df52d388754a08f81a7e3cf94ebded5b84baef63cd696f",
        "229ec3ed6037b122ef54d922fdc9c0ae8eaab590da5dc29fec9139803b2da442",
        "9801a885b860bc01c5481185a73de06b4faecbd1966b69c3695b858128df4ae2",
        "9821eb040c5d6ad5a1849dc47f63d0ef4d6acbce191390142d4fce6ce677d85f",
        "3c09140f706df93ce4114cb9d1177be459567d5d85b1ae508053271aeef9d114",
        "d66d2843e490b7b51699487d74f984015a833df8bbb0b25d062ede926b439d2b",
        "2cb36a3f83d1049e843a495ba5b9ee62cb037fe7bb578815cb6b8e8d2248ff5e",
        "9253d0a427243d42e0b7d9de7f470cafc913372ef3c685bb0812500eccd7461b",
        "e3b33f355aff873996df52d388754a08f81a7e3cf94ebded5b84baef63cd696f",
    ]

    async def test_search():
        print("search")
        return await search(
            "https://www.pathofexile.com/api/trade/search/Ritual",
            {
                "query": {
                    "status": {"option": "online"},
                    "stats": [{"type": "and", "filters": []}],
                },
                "sort": {"price": "asc"},
            },
        )

    async def test_fetch():
        print("fetch")
        return await fetch(
            "https://www.pathofexile.com/api/trade/fetch/229ec3ed6037b122ef54d922fdc9c0ae8eaab590da5dc29fec9139803b2da442,9801a885b860bc01c5481185a73de06b4faecbd1966b69c3695b858128df4ae2,9821eb040c5d6ad5a1849dc47f63d0ef4d6acbce191390142d4fce6ce677d85f,3c09140f706df93ce4114cb9d1177be459567d5d85b1ae508053271aeef9d114,d66d2843e490b7b51699487d74f984015a833df8bbb0b25d062ede926b439d2b,2cb36a3f83d1049e843a495ba5b9ee62cb037fe7bb578815cb6b8e8d2248ff5e,9253d0a427243d42e0b7d9de7f470cafc913372ef3c685bb0812500eccd7461b,e3b33f355aff873996df52d388754a08f81a7e3cf94ebded5b84baef63cd696f,02716bfc05aa59b3ef43be557ebce8c15756b46aecece49b58fd8b493429c9d3,3a9e791544f36169a27f24d2be35b5fff74a6b18a2804bd0bd43993b22a57cbd?query=Ab3LSL"
        )

    async def test_fetch_batched():
        print("fetch_batched")
        return await fetch_batched(item_ids)

    asyncio.run(test_search())
    asyncio.run(test_fetch())
    asyncio.run(test_fetch_batched())

    N = 500

    async def main():
        things = [test_fetch() for _ in range(N)] + [test_search() for _ in range(N)]
        return await asyncio.gather(*things)

    async def sleep_fetch(item_ids, sleep_time):
        await asyncio.sleep(sleep_time)
        return await fetch_batched(item_ids)

    async def test_multiple_fetch_batched():
        things = [
            sleep_fetch(
                ["229ec3ed6037b122ef54d922fdc9c0ae8eaab590da5dc29fec9139803b2da442"],
                0.1 * idx,
            )
            for idx in range(N)
        ]
        await asyncio.gather(*things)

    asyncio.run(test_multiple_fetch_batched())
