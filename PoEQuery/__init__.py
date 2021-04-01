from os.path import dirname, join
import yaml


with open(join(dirname(dirname(__file__)), "settings.yaml"), "r") as f:
    settings = yaml.load(f, Loader=yaml.FullLoader)

account_name = settings["account_name"]
realm = settings["realm"]
league_id = settings["league_id"]
poesessid = settings["poesessid"]
user_agent = settings["user_agent"]
