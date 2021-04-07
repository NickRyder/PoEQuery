import asyncio
import pandas as pd  # type:ignore

from PoEQuery import account_name, league_id, realm
from PoEQuery.official_api_async import stash_tab
from PoEQuery.stash_tab_result import StashTabResult

STASH_URL = "https://www.pathofexile.com/character-window/get-stash-items"


def get_tab_overview():
    params = {
        "accountName": account_name,
        "realm": realm,
        "league": league_id,
        "tabIndex": 0,
        "tabs": 1,
    }
    response = asyncio.run(stash_tab(params=params))
    return response.json()


def get_tab_index(tab_index):
    params = {
        "accountName": account_name,
        "realm": realm,
        "league": league_id,
        "tabIndex": tab_index,
    }
    response = asyncio.run(stash_tab(params=params))
    return response.json()


df = pd.DataFrame()
stash_tab_results = StashTabResult(get_tab_overview())
print(stash_tab_results.tabs)
for tab in stash_tab_results.tabs:
    if tab.name in ["LOW LEVEL BREACH"]:
        df = pd.DataFrame()
        tab_results = StashTabResult(get_tab_index(tab_index=tab.index))
        for item in tab_results.items:
            df = df.append(
                {"type": item.type, "count": item.stack_size}, ignore_index=True
            )
        print(tab.name, df)
