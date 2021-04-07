from dataclasses import dataclass
from typing import Tuple
from PoEQuery.official_api_result import OfficialApiItem


@dataclass(unsafe_hash=True)
class Tab:
    name: str
    index: int

    def __init__(self, json):
        self.name, self.index = json["n"], json["i"]
        # self.id = json["id"]


@dataclass(unsafe_hash=True)
class StashTabResult:
    num_tabs: int
    items: Tuple[OfficialApiItem]
    tabs: Tuple[Tab]

    def __init__(self, json):
        self.num_tabs = json["numTabs"]
        self.tabs = tuple([Tab(tab) for tab in json.get("tabs", [])])
        self.items = tuple([OfficialApiItem(item) for item in json["items"]])
