from collections import defaultdict
from requests_html import HTMLSession
from functools import lru_cache
from urllib.parse import ParseResult
import pandas as pd
from io import BytesIO, StringIO
import zipfile


@lru_cache()
def scrape_data_links():
    with HTMLSession() as session:
        r = session.get("https://poe.ninja/data")
        # ninja uses js
        r.html.render()

        league_to_link = defaultdict(lambda: defaultdict())
        for challenge_league in r.html.find("div.challenge-leagues"):
            for link_element in challenge_league.find("a"):
                league_to_link[link_element.text] = link_element.attrs["href"]
        return league_to_link


@lru_cache()
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
                zipped_contents[info.filename] = pd.read_csv(
                    StringIO(zip.read(info.filename).decode()), sep=";"
                )
            return zipped_contents

    except KeyError:
        raise KeyError(
            f"{league_name} not a valid league name, try: {data_links.keys()}"
        )


if __name__ == "__main__":
    print(get_past_league_data("Harvest"))
