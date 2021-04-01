from os.path import dirname, join
import os
import yaml

__settings_path__ = join(dirname(dirname(__file__)), "settings.yaml")
__example_settings_path__ = join(dirname(dirname(__file__)), "example_settings.yaml")

if not os.exists(__settings_path__):
    raise FileExistsError(
        "settings.yaml does not exist, please copy from example_settings.yaml and fill in necessary information"
    )

if not os.exists(__example_settings_path__):
    raise FileExistsError("example_settings.yaml does not exist")

with open(join(dirname(dirname(__file__)), "settings.yaml"), "r") as f:
    settings = yaml.load(f, Loader=yaml.SafeLoader)
    example_settings = yaml.load(f, Loader=yaml.SafeLoader)
    assert (
        settings.keys() == example_settings.keys()
    ), "please copy example_settings.yaml to settings.yaml"

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
