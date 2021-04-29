from PoEQuery.cache import cache_results
from collections import defaultdict
from requests_html import HTMLSession
from functools import lru_cache
from urllib.parse import ParseResult
import pandas as pd
from io import BytesIO, StringIO
import zipfile


CURRENT_LEAGUES = [
    "Harvest",
    "HC Harvest",
    "Delirium",
    "HC Delirium",
    "Metamorph",
    "HC Metamorph",
    "Blight",
    "HC Blight",
    "Legion",
    "HC Legion",
    "Synthesis",
    "HC Synthesis",
    "Betrayal",
    "HC Betrayal",
    "Delve",
    "HC Delve",
    "Incursion Flashback",
    "Incursion HC Flashback",
    "Incursion",
    "HC Incursion",
    "Flashback",
    "HC Flashback",
    "Bestiary",
    "HC Bestiary",
    "Abyss",
    "HC Abyss",
    "Harbinger",
    "HC Harbinger",
    "Legacy",
    "HC Legacy",
    "Breach",
    "HC Breach",
    "Essence",
    "HC Essence",
]


@lru_cache()
def scrape_data_links():
    with HTMLSession() as session:
        r = session.get("https://poe.ninja/data")
        # ninja uses js
        r.html.render()

        league_to_link = {}
        for challenge_league in r.html.find("div.challenge-leagues"):
            for link_element in challenge_league.find("a"):
                league_to_link[link_element.text] = link_element.attrs["href"]
        return league_to_link


@cache_results("ninja_data", key=lambda league_name: league_name)
def get_past_league_data(league_name):
    data_links = scrape_data_links()
    try:
        ninja_url = ParseResult(
            scheme="https",
            netloc="poe.ninja",
            path=data_links[league_name],
            params="",
            query="",
            fragment="",
        )

        with HTMLSession() as session:
            response = session.get(ninja_url.geturl())
            zip = zipfile.ZipFile(BytesIO(response.content))
            zipped_contents = {}
            for info in zip.infolist():
                zipped_contents[info.filename.split(".")[-2]] = pd.read_csv(
                    StringIO(zip.read(info.filename).decode()), sep=";"
                )
            return zipped_contents

    except KeyError:
        raise KeyError(
            f"{league_name} not a valid league name, try: {data_links.keys()}"
        )


if __name__ == "__main__":
    print(get_past_league_data("Harvest"))
