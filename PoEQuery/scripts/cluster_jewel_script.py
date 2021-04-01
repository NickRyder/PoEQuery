import json
import requests
from official_api import fetch_results, fetch_query
import pandas as pd


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


def create_item_query(option_idx, ilvl, passive_count):
    return {
        "query": {
            "status": {"option": "any"},
            "stats": [
                {
                    "type": "and",
                    "filters": [
                        {
                            "id": "enchant.stat_3948993189",
                            "value": {"option": option_idx},
                            "disabled": False,
                        },
                        {
                            "id": "enchant.stat_3086156145",
                            "value": {"min": passive_count, "max": passive_count},
                            "disabled": False,
                        },
                    ],
                }
            ],
            "filters": {
                "misc_filters": {
                    "filters": {"ilvl": {"min": ilvl}, "corrupted": {"option": "false"}}
                },
                "trade_filters": {"filters": {"indexed": {"option": "3days"}}},
            },
        },
        "sort": {"price": "asc"},
    }


def _convert_price_to_chaos(price_json):
    if price_json["currency"] == "chaos":
        return price_json["amount"]
    elif price_json["currency"] == "exa":
        return price_json["amount"] * 165
    elif price_json["currency"] == "exalted":
        return price_json["amount"] * 165
    else:
        raise ValueError(f"unknown currency: {price_json['currency']}")


data = []
for option_idx in range(1, 51, 1):
    for ilvl_cutoff in range(68, 87):
        for passive_count in range(2, 13, 1):
            try:
                query = create_item_query(
                    option_idx=option_idx, ilvl=ilvl_cutoff, passive_count=passive_count
                )
                fetch_ids, total, query = fetch_query(query)
                results = fetch_results(fetch_ids[:10])
                for option_idx_dict in option_idx_dicts:
                    if option_idx_dict["id"] == option_idx:
                        option_text = option_idx_dict["text"]
                header = [option_text, ilvl_cutoff, passive_count]
                prices = []
                for result in results:
                    try:
                        prices.append(
                            _convert_price_to_chaos(result["listing"]["price"])
                        )
                    except ValueError as e:
                        print(e)
                if prices:
                    data.append(header + prices)
                    print(header + prices)
            except Exception as e:
                print(e)

dataframe = pd.DataFrame(
    data,
    columns=[
        "option_idx",
        "base ilvl_cutoff",
        "passive_count",
        "price 0",
        "price 1",
        "price 2",
        "price 3",
        "price 4",
        "price 5",
        "price 6",
        "price 7",
        "price 8",
        "price 9",
    ],
)
dataframe.to_csv("cluster_jewel_prices_extended.csv")
breakpoint()
