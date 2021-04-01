from PoEQuery.official_api_async import (
    characters,
    fetch,
    fetch_batched,
    items,
    passive_tree,
    search,
)
import asyncio
from tqdm import tqdm
import pytest

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


async def _test_search():
    print("search")
    return await search(
        {
            "query": {
                "status": {"option": "online"},
                "stats": [{"type": "and", "filters": []}],
            },
            "sort": {"price": "asc"},
        },
    )


async def _test_fetch():
    print("fetch")
    return await fetch(item_ids[:10])


def test_endpoints():
    async def test_fetch_batched():
        print("fetch_batched")
        return await fetch_batched(item_ids)

    asyncio.run(_test_search())
    asyncio.run(_test_fetch())
    asyncio.run(test_fetch_batched())

    asyncio.run(characters("havoc616"))
    passive_tree("havoc616", "Havoc_TwitchPrime")
    asyncio.run(items("havoc616", "Havoc_TwitchPrime"))


def test_async_gather():
    N = 10

    async def main():
        things = [_test_fetch() for _ in range(N)] + [_test_search() for _ in range(N)]
        return await asyncio.gather(*things)

    asyncio.run(main())


def test_multiple_fetch_batched():

    N = 100
    _tqdm = tqdm(total=N)

    async def sleep_fetch(item_ids, sleep_time, tqdm: tqdm = None):
        await asyncio.sleep(sleep_time)
        results = await fetch_batched(item_ids)
        if tqdm is not None:
            tqdm.update(len(results))

    coroutines = [
        sleep_fetch(
            ["229ec3ed6037b122ef54d922fdc9c0ae8eaab590da5dc29fec9139803b2da442"],
            0.1 * idx,
            _tqdm,
        )
        for idx in range(N)
    ]

    async def _boilerplate():
        return await asyncio.gather(*coroutines)

    asyncio.run(_boilerplate())


if __name__ == "__main__":
    pytest.main()
