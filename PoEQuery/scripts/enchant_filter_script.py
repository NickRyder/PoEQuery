import requests
import re
import pandas as pd

enchant_json_url = """https://pathofexile.gamepedia.com/index.php?title=Special:CargoExport&tables=spawn_weights%2C+mods%2C&join+on=mods._pageID%3Dspawn_weights._pageID&fields=mods.name%2C+mods.stat_text%2C&where=mods.generation_type+%3D+10+AND+spawn_weights.tag+%3D+%22helmet%22+AND+spawn_weights.weight+%3E+0&order+by=%60cargo__mods%60.%60name%60%2C%60cargo__mods%60.%60stat_text%60&limit=10000&format=json"""

enchant_jsons = requests.get(enchant_json_url).json()

enchant_poe_ninja_url = """https://poe.ninja/api/data/itemoverview?league=Delirium&type=HelmetEnchant&language=en"""

enchant_poe_ninja_json = requests.get(enchant_poe_ninja_url).json()["lines"]


def fix_json(enchant_jsons):
    for enchant_json in enchant_jsons:
        enchant_json["id"] = enchant_json["name"]
        del enchant_json["name"]
        # .replace("_", "")
        # enchant_json["id"] = re.sub(
        #     "([a-z])([A-Z0-9])", "\g<1> \g<2>", enchant_json["id"]
        # )

        # lacerate fix
        # changes
        ## (1-2) to (3-4)
        # into
        ## 1 to 4
        enchant_json["stat text"] = re.sub(
            r"\((\d*)-(\d*)\) to \((\d*)-(\d*)\)",
            "\g<1> to \g<4>",
            enchant_json["stat text"],
        )

        enchant_json["stat text"] = re.sub(
            r"\[\[([A-Za-z ]*)\|([A-Za-z ]*)\]\]", "\g<2>", enchant_json["stat text"],
        )
        enchant_json["stat text"] = (
            enchant_json["stat text"].replace("[[", "").replace("]]", "")
        )


fix_json(enchant_jsons) 

data = []

for poe_ninja_enchant in enchant_poe_ninja_json:
    if "Allocates" not in poe_ninja_enchant["name"]:
        for enchant_json in enchant_jsons:
            if enchant_json["stat text"].strip() == poe_ninja_enchant["name"].strip():

                try:
                    data.append(
                        [
                            poe_ninja_enchant["name"],
                            enchant_json["id"],
                            poe_ninja_enchant["chaosValue"],
                        ]
                    )
                except KeyError as e:
                    print(f"""{poe_ninja_enchant["name"]} has no chaos value""")
                break
        else:
            raise ValueError(f"no found match for {poe_ninja_enchant['name']}")

dataframe = pd.DataFrame(data, columns=["name", "id", "chaosValue"])
dataframe.to_csv("enchants.csv")

enchant_count = len(data)
top_ten_percentile = enchant_count // 10

top_ten_percentile_ids = dataframe["id"].iloc[:top_ten_percentile].values


def _copy_to_clipboard(text):
    import pyperclip

    pyperclip.copy(text)


concatenated_into_list = (
    "[" + ",".join([f'"\\"{id}\\""' for id in top_ten_percentile_ids]) + "]"
)
_copy_to_clipboard(concatenated_into_list)
breakpoint()
