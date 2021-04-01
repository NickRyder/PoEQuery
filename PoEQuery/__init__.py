from os.path import dirname, join
import os
import yaml

__settings_path__ = join(dirname(dirname(__file__)), "settings.yaml")

if not os.exists(__settings_path__):
    raise FileExistsError(
        "settings.yaml does not exist, please copy from example_settings.yaml and fill in necessary information"
    )

with open(join(dirname(dirname(__file__)), "settings.yaml"), "r") as f:
    settings = yaml.load(f, Loader=yaml.FullLoader)

try:
    account_name = settings["account_name"]
    realm = settings["realm"]
    league_id = settings["league_id"]
    poesessid = settings["poesessid"]
    user_agent = settings["user_agent"]
except KeyError:
    raise KeyError(
        "please fill out all keys in settings.yaml, following template from examples.yaml"
    )
