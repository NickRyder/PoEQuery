# [WIP] PoEQuery

A package to simplify querying the official trade website and parsing its results.

Currently `x_rate_limiter.py` and `official_api_async.py` are somewhat stable, expect the rest to move rapidly.

# X Rate Limiting
Provides a decorator to automatically respect rate limits, spits out an asyncio coroutine, so you can do other work while waiting on rate limits.

Example usage
```
from PoEQuery.x_rate_limiter import rate_limited


@rate_limited("trade-search-request-limit")
def search(query: dict = None) -> requests.Response:
    query = {} if query is None else query
    return requests.post(
        f"{API_SEARCH}/{league_id}",
        headers=USER_AGENT_HEADER,
        json=query,
        cookies=dict(POESESSID=poesessid),
    )
```
