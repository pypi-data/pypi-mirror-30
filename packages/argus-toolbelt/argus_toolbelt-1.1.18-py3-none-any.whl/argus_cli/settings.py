"""Load default YAML settings file, then look for user defined settings and create a ChainMap."""
import logging.config
from os import environ
from os.path import join, dirname, abspath, expanduser, exists
from yaml import load


# Default plugin location
DEFAULT_PLUGIN_DIRECTORY = abspath(join(dirname(abspath(__file__)), "..", "argus_plugins"))

# Default locations for settings.ini files
SETTINGS_ENV_VAR = "ARGUS_CLI_SETTINGS"

# Expected user location if none is provided
DEFAULT_SETTINGS_LOCATION = join(abspath(dirname(__file__)), "resources", "config.yaml")
USER_SETTINGS_LOCATION = environ.get(SETTINGS_ENV_VAR, join(expanduser("~"), ".argus_cli.yaml"))


def merge(source: dict, destination: dict) -> dict:
    """Deep merges two dictionaries and replaces values from destination with the ones from source."""
    for key, value in source.items():
        if isinstance(value, dict):
            node = destination.setdefault(key, {})
            merge(value, node)
        else:
            destination[key] = value

    return destination


logging.info("Getting settings from %s..." % USER_SETTINGS_LOCATION)

# Load default settings and allow user settings to take precedence
settings = merge(
    load(open(USER_SETTINGS_LOCATION)) if exists(USER_SETTINGS_LOCATION) else {},
    load(open(DEFAULT_SETTINGS_LOCATION))
)

if "plugins" not in settings["cli"].keys() or not settings["cli"]["plugins"]:
    logging.info("No plugin directory specified. Defaulting to %s" % DEFAULT_PLUGIN_DIRECTORY)
    settings["cli"]["plugins"] = []
else:
    # Remove plugin directories that don't exist and warn about them

    for directory in settings["cli"]["plugins"]:
        if not exists(directory):
            logging.warning("Plugin directory %s does not exist. Ignoring")

    settings["cli"]["plugins"] = [
        directory
        for directory in settings["cli"]["plugins"]
        if exists(directory)
    ]

settings["cli"]["plugins"] += [DEFAULT_PLUGIN_DIRECTORY]
