from PoEQuery.official_api_query import OfficialApiQuery
from PoEQuery.official_api_async import (
    characters,
    items,
    passive_tree,
    search,
)
from PoEQuery.batched_fetch import fetch_batched

import asyncio
import pytest  # type: ignore

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


query = OfficialApiQuery()


def test_endpoints():
    asyncio.run(search(query))
    asyncio.run(fetch_batched(item_ids))

    asyncio.run(characters("Havoc6"))
    passive_tree("Havoc6", "Havoc_TwitchPrime")
    asyncio.run(items("Havoc6", "Havoc_TwitchPrime"))


@pytest.mark.parametrize("use_cached", [True, False])
def test_async_gather(use_cached):
    N = 10

    async def main():
        things = [fetch_batched(item_ids, use_cached=use_cached) for _ in range(N)] + [
            search(query, use_cached=use_cached) for _ in range(N)
        ]
        return await asyncio.gather(*things)

    asyncio.run(main())


def test_multiple_fetch_batched():
    async def sleep_fetch(item_ids, sleep_time):
        await asyncio.sleep(sleep_time)
        results = await fetch_batched(item_ids, use_cached=False)

    coroutines = [
        sleep_fetch(
            [item_id],
            0.1 * idx,
        )
        for idx, item_id in enumerate(item_ids * 1)
    ]

    async def _boilerplate():
        return await asyncio.gather(*coroutines)

    asyncio.run(_boilerplate())


if __name__ == "__main__":
    pytest.main(["-vxs"])
