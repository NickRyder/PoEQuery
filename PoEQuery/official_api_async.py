from PoEQuery.official_api_query import OfficialApiQuery
from PoEQuery.batched_fetch import fetch_batched
from typing import List

import requests

from PoEQuery import league_id, poesessid, realm, user_agent
from PoEQuery.x_rate_limiter import rate_limited

from PoEQuery.cache import cache_results

USER_AGENT_HEADER = {"user-agent": user_agent}

API_FETCH = "https://www.pathofexile.com/api/trade/fetch"

API_SEARCH = "https://www.pathofexile.com/api/trade/search"

API_STASH = "https://www.pathofexile.com/character-window/get-stash-items"

API_CHARACTER = "https://www.pathofexile.com/character-window/get-characters"

API_PASSIVE = "https://www.pathofexile.com/character-window/get-passive-skills"

API_ITEM = "https://www.pathofexile.com/character-window/get-items"


@cache_results("search_results", key=lambda query: query.json())
@rate_limited("trade-search-request-limit")
def search(query: OfficialApiQuery = None) -> requests.Response:
    query_json = {} if query is None else query.json()
    return requests.post(
        f"{API_SEARCH}/{league_id}",
        headers=USER_AGENT_HEADER,
        json=query_json,
        cookies=dict(POESESSID=poesessid),
    )


# See PoEQuery.batched_fetch for a batched, cached variant
async def fetch(item_ids: List[str]) -> List[dict]:
    return await fetch_batched(item_ids)


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
