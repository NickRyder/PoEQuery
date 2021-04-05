from os.path import dirname, join
import os
import yaml
import logging
import tqdm


class TqdmLoggingHandler(logging.StreamHandler):
    """
    https://stackoverflow.com/questions/38543506/change-logging-print-function-to-tqdm-write-so-logging-doesnt-interfere-wit
    """

    def __init__(self, level=logging.NOTSET):
        super().__init__(level)

    def emit(self, record):
        try:
            msg = self.format(record)
            tqdm.tqdm.write(msg)
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)


handler = TqdmLoggingHandler()
handler.setFormatter(logging.Formatter(logging.BASIC_FORMAT))

logging.getLogger().setLevel(logging.INFO)
logging.getLogger().addHandler(handler)

__diskcache_path__ = join(dirname(dirname(__file__)), ".diskcache/")
__settings_path__ = join(dirname(dirname(__file__)), "settings.yaml")
__example_settings_path__ = join(dirname(dirname(__file__)), "example_settings.yaml")


if not os.path.exists(__example_settings_path__):
    raise FileExistsError("example_settings.yaml does not exist")

if not os.path.exists(__settings_path__):
    raise FileExistsError(
        "settings.yaml does not exist, please copy from example_settings.yaml and fill in necessary information"
    )

with open(__settings_path__, "r") as f:
    settings = yaml.load(f, Loader=yaml.SafeLoader)

with open(__example_settings_path__, "r") as f:
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
    raise KeyError("please copy template from example_settings.yaml")

if not all([setting is not None for setting in settings.values()]):
    raise ValueError("please fill out all fields in settings.yaml")
