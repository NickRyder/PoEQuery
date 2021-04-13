import diskcache  # type: ignore
from PoEQuery.official_api_query import OfficialApiQuery, StatFilter, StatFilters
import pickle as pkl
import pytest  # type: ignore

query1 = OfficialApiQuery(
    stat_filters=[
        StatFilters(
            filters=[
                StatFilter(
                    id="fractured.stat_1671376347",
                    min=18.0,
                    max=29.0,
                    disabled=False,
                ),
                StatFilter(
                    id="fractured.stat_1290399200",
                    min=21.0,
                    max=50.0,
                    disabled=False,
                ),
                StatFilter(
                    id="fractured.stat_1037193709",
                    min=10.5,
                    max=52.5,
                    disabled=False,
                ),
                StatFilter(
                    id="fractured.stat_821021828", min=4.0, max=5.0, disabled=False
                ),
                StatFilter(
                    id="fractured.stat_2843100721", min=1.0, max=1.0, disabled=False
                ),
                StatFilter(
                    id="fractured.stat_4220027924",
                    min=6.0,
                    max=35.0,
                    disabled=False,
                ),
                StatFilter(
                    id="fractured.stat_2517001139",
                    min=11.0,
                    max=35.0,
                    disabled=False,
                ),
                StatFilter(
                    id="fractured.stat_2923486259",
                    min=5.0,
                    max=10.0,
                    disabled=False,
                ),
                StatFilter(
                    id="fractured.stat_210067635",
                    min=17.0,
                    max=25.0,
                    disabled=False,
                ),
                StatFilter(
                    id="fractured.stat_829382474", min=1.0, max=1.0, disabled=False
                ),
                StatFilter(
                    id="fractured.stat_789117908",
                    min=40.0,
                    max=49.0,
                    disabled=False,
                ),
                StatFilter(
                    id="fractured.stat_3261801346",
                    min=8.0,
                    max=32.0,
                    disabled=False,
                ),
                StatFilter(
                    id="fractured.stat_691932474",
                    min=21.0,
                    max=325.0,
                    disabled=False,
                ),
                StatFilter(
                    id="fractured.stat_1509134228",
                    min=20.0,
                    max=64.0,
                    disabled=False,
                ),
                StatFilter(
                    id="fractured.stat_3695891184",
                    min=11.0,
                    max=14.0,
                    disabled=False,
                ),
                StatFilter(
                    id="fractured.stat_3556824919",
                    min=15.0,
                    max=29.0,
                    disabled=False,
                ),
                StatFilter(
                    id="fractured.stat_709508406", min=2.0, max=48.0, disabled=False
                ),
                StatFilter(
                    id="fractured.stat_3639275092",
                    min=-18.0,
                    max=-18.0,
                    disabled=False,
                ),
                StatFilter(
                    id="fractured.stat_3336890334",
                    min=36.0,
                    max=85.0,
                    disabled=False,
                ),
                StatFilter(
                    id="fractured.stat_1940865751",
                    min=6.0,
                    max=27.0,
                    disabled=False,
                ),
                StatFilter(
                    id="fractured.stat_1050105434",
                    min=40.0,
                    max=109.0,
                    disabled=False,
                ),
                StatFilter(
                    id="fractured.stat_328541901", min=8.0, max=37.0, disabled=False
                ),
                StatFilter(
                    id="fractured.stat_795138349",
                    min=20.0,
                    max=30.0,
                    disabled=False,
                ),
                StatFilter(
                    id="fractured.stat_3372524247",
                    min=12.0,
                    max=29.0,
                    disabled=False,
                ),
                StatFilter(
                    id="fractured.stat_2375316951",
                    min=10.0,
                    max=29.0,
                    disabled=False,
                ),
                StatFilter(
                    id="fractured.stat_387439868",
                    min=11.0,
                    max=36.0,
                    disabled=False,
                ),
            ],
            type="not",
        ),
        StatFilters(),
    ],
    name=None,
    type=None,
    corrupted=False,
    mirrored=None,
    synthesised=None,
    alternate_art=False,
    talisman_tier_max=None,
    quality_max=0,
    rarity="nonunique",
    category="weapon.claw",
    indexed=None,
    sale_type=None,
    identified=None,
    enchanted=None,
    fractured=True,
    crafted=None,
    sockets_b=None,
    sockets_g=None,
    sockets_r=None,
    sockets_w=None,
    links_b=None,
    links_g=None,
    links_r=None,
    links_w=None,
)

query2 = OfficialApiQuery(
    stat_filters=[
        StatFilters(),
        StatFilters(
            filters=[
                StatFilter(
                    id="fractured.stat_3336890334",
                    min=36.0,
                    max=85.0,
                    disabled=False,
                ),
                StatFilter(
                    id="fractured.stat_1671376347",
                    min=18.0,
                    max=29.0,
                    disabled=False,
                ),
                StatFilter(
                    id="fractured.stat_3639275092",
                    min=-18.0,
                    max=-18.0,
                    disabled=False,
                ),
                StatFilter(
                    id="fractured.stat_328541901", min=8.0, max=37.0, disabled=False
                ),
                StatFilter(
                    id="fractured.stat_2375316951",
                    min=10.0,
                    max=29.0,
                    disabled=False,
                ),
                StatFilter(
                    id="fractured.stat_1037193709",
                    min=10.5,
                    max=52.5,
                    disabled=False,
                ),
                StatFilter(
                    id="fractured.stat_1290399200",
                    min=21.0,
                    max=50.0,
                    disabled=False,
                ),
                StatFilter(
                    id="fractured.stat_387439868",
                    min=11.0,
                    max=36.0,
                    disabled=False,
                ),
                StatFilter(
                    id="fractured.stat_3261801346",
                    min=8.0,
                    max=32.0,
                    disabled=False,
                ),
                StatFilter(
                    id="fractured.stat_3695891184",
                    min=11.0,
                    max=14.0,
                    disabled=False,
                ),
                StatFilter(
                    id="fractured.stat_4220027924",
                    min=6.0,
                    max=35.0,
                    disabled=False,
                ),
                StatFilter(
                    id="fractured.stat_795138349",
                    min=20.0,
                    max=30.0,
                    disabled=False,
                ),
                StatFilter(
                    id="fractured.stat_1050105434",
                    min=40.0,
                    max=109.0,
                    disabled=False,
                ),
                StatFilter(
                    id="fractured.stat_1509134228",
                    min=20.0,
                    max=64.0,
                    disabled=False,
                ),
                StatFilter(
                    id="fractured.stat_821021828", min=4.0, max=5.0, disabled=False
                ),
                StatFilter(
                    id="fractured.stat_829382474", min=1.0, max=1.0, disabled=False
                ),
                StatFilter(
                    id="fractured.stat_3556824919",
                    min=15.0,
                    max=29.0,
                    disabled=False,
                ),
                StatFilter(
                    id="fractured.stat_709508406", min=2.0, max=48.0, disabled=False
                ),
                StatFilter(
                    id="fractured.stat_210067635",
                    min=17.0,
                    max=25.0,
                    disabled=False,
                ),
                StatFilter(
                    id="fractured.stat_2517001139",
                    min=11.0,
                    max=35.0,
                    disabled=False,
                ),
                StatFilter(
                    id="fractured.stat_789117908",
                    min=40.0,
                    max=49.0,
                    disabled=False,
                ),
                StatFilter(
                    id="fractured.stat_2843100721", min=1.0, max=1.0, disabled=False
                ),
                StatFilter(
                    id="fractured.stat_2923486259",
                    min=5.0,
                    max=10.0,
                    disabled=False,
                ),
                StatFilter(
                    id="fractured.stat_3372524247",
                    min=12.0,
                    max=29.0,
                    disabled=False,
                ),
                StatFilter(
                    id="fractured.stat_1940865751",
                    min=6.0,
                    max=27.0,
                    disabled=False,
                ),
                StatFilter(
                    id="fractured.stat_691932474",
                    min=21.0,
                    max=325.0,
                    disabled=False,
                ),
            ],
            type="not",
        ),
    ],
    name=None,
    type=None,
    corrupted=False,
    mirrored=None,
    synthesised=None,
    alternate_art=False,
    talisman_tier_max=None,
    quality_max=0,
    rarity="nonunique",
    category="weapon.claw",
    indexed=None,
    sale_type=None,
    identified=None,
    enchanted=None,
    fractured=True,
    crafted=None,
    sockets_b=None,
    sockets_g=None,
    sockets_r=None,
    sockets_w=None,
    links_b=None,
    links_g=None,
    links_r=None,
    links_w=None,
)


def test_match():
    assert query1.json() == query2.json()
    assert pkl.dumps(query1.json()) == pkl.dumps(query2.json())
    cache = diskcache.Cache("..tmp")
    cache.clear()
    cache.set(query1.json(), "test")
    assert query2.json() in cache


def test_default():

    search_json = {
        "query": {
            "status": {"option": "any"},
            "stats": [{"type": "and", "filters": []}],
            "filters": {
                "misc_filters": {"filters": {"alternate_art": {"option": "false"}}}
            },
        },
        "sort": {"price": "asc"},
    }
    assert OfficialApiQuery().json() == search_json


if __name__ == "__main__":
    pytest.main(["-vxs"])
