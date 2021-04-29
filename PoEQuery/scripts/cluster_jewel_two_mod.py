import asyncio
from PoEQuery.query_generator import bisect_count_two_mod
from PoEQuery.official_api import (
    fetch_query_with_query_dividers,
)
from PoEQuery.official_api_query import OfficialApiQuery, StatFilter, StatFilters
from PoEQuery.affix_finder import find_affixes


option_idx_dicts = [
    {
        "id": 1,
        "text": "Axe Attacks deal 12% increased Damage with Hits and Ailments\nSword Attacks deal 12% increased Damage with Hits and Ailments",
    },
    {
        "id": 2,
        "text": "Staff Attacks deal 12% increased Damage with Hits and Ailments\nMace or Sceptre Attacks deal 12% increased Damage with Hits and Ailments",
    },
    {
        "id": 3,
        "text": "Claw Attacks deal 12% increased Damage with Hits and Ailments\nDagger Attacks deal 12% increased Damage with Hits and Ailments",
    },
    {
        "id": 4,
        "text": "12% increased Damage with Bows\n12% increased Damage Over Time with Bow Skills",
    },
    {"id": 5, "text": "Wand Attacks deal 12% increased Damage with Hits and Ailments"},
    {"id": 6, "text": "12% increased Damage with Two Handed Weapons"},
    {"id": 7, "text": "12% increased Attack Damage while Dual Wielding"},
    {"id": 8, "text": "12% increased Attack Damage while holding a Shield"},
    {"id": 9, "text": "10% increased Attack Damage"},
    {"id": 10, "text": "10% increased Spell Damage"},
    {"id": 11, "text": "10% increased Elemental Damage"},
    {"id": 12, "text": "12% increased Physical Damage"},
    {"id": 13, "text": "12% increased Fire Damage"},
    {"id": 14, "text": "12% increased Lightning Damage"},
    {"id": 15, "text": "12% increased Cold Damage"},
    {"id": 16, "text": "12% increased Chaos Damage"},
    {"id": 17, "text": "Minions deal 10% increased Damage"},
    {"id": 18, "text": "+5% to Fire Damage over Time Multiplier"},
    {"id": 19, "text": "+5% to Chaos Damage over Time Multiplier"},
    {"id": 20, "text": "+5% to Physical Damage over Time Multiplier"},
    {"id": 21, "text": "+5% to Cold Damage over Time Multiplier"},
    {"id": 22, "text": "+4% to Damage over Time Multiplier"},
    {"id": 23, "text": "10% increased Effect of Non-Damaging Ailments"},
    {"id": 24, "text": "6% increased effect of Non-Curse Auras from your Skills"},
    {"id": 25, "text": "5% increased Effect of your Curses"},
    {"id": 26, "text": "10% increased Damage while affected by a Herald"},
    {
        "id": 27,
        "text": "Minions deal 10% increased Damage while you are affected by a Herald",
    },
    {"id": 28, "text": "Exerted Attacks deal 20% increased Damage"},
    {"id": 29, "text": "15% increased Critical Strike Chance"},
    {"id": 30, "text": "Minions have 12% increased maximum Life"},
    {"id": 31, "text": "10% increased Area Damage"},
    {"id": 32, "text": "10% increased Projectile Damage"},
    {"id": 33, "text": "12% increased Trap Damage\n12% increased Mine Damage"},
    {"id": 34, "text": "12% increased Totem Damage"},
    {"id": 35, "text": "12% increased Damage with Brand Skills"},
    {"id": 36, "text": "Channelling Skills deal 12% increased Damage"},
    {"id": 37, "text": "6% increased Flask Effect Duration"},
    {
        "id": 38,
        "text": "10% increased Life Recovery from Flasks\n10% increased Mana Recovery from Flasks",
    },
    {"id": 39, "text": "4% increased maximum Life"},
    {"id": 40, "text": "6% increased maximum Energy Shield"},
    {"id": 41, "text": "6% increased maximum Mana"},
    {"id": 42, "text": "15% increased Armour"},
    {"id": 43, "text": "15% increased Evasion Rating"},
    {"id": 44, "text": "1% Chance to Block Attack Damage"},
    {"id": 45, "text": "1% Chance to Block Spell Damage"},
    {"id": 46, "text": "+15% to Fire Resistance"},
    {"id": 47, "text": "+15% to Cold Resistance"},
    {"id": 48, "text": "+15% to Lightning Resistance"},
    {"id": 49, "text": "+12% to Chaos Resistance"},
    {"id": 50, "text": "1% chance to Dodge Attack Hits"},
]


mods = find_affixes(
    OfficialApiQuery(
        stat_filters=[
            StatFilters(
                filters=[
                    StatFilter("enchant.stat_3948993189", option=18),
                    StatFilter("enchant.stat_3086156145"),
                ]
            )
        ],
        mirrored=False,
        corrupted=False,
        rarity="nonunique",
    ),
    affix_type="explicit",
)

query = OfficialApiQuery(
    stat_filters=[
        StatFilters(
            filters=[
                StatFilter("enchant.stat_3948993189", option=18),
                StatFilter("enchant.stat_3086156145"),
            ]
        ),
        StatFilters(
            filters=[
                stat_filter
                for mod in mods
                for stat_filter in mod.to_query_stat_filters()
            ],
            type="count",
            min="2",
        ),
    ],
    mirrored=False,
    corrupted=False,
    rarity="nonunique",
)

asyncio.run(fetch_query_with_query_dividers(query, [bisect_count_two_mod]))
