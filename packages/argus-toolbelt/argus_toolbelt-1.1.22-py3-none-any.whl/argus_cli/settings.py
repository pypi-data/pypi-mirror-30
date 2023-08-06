"""Load default YAML settings file, then look for user defined settings and create a ChainMap."""
from os import environ
from os.path import join, dirname, abspath, expanduser, exists
from yaml import load

from argus_cli.helpers import log as log_module

# Default plugin location
DEFAULT_PLUGIN_DIRECTORY = abspath(join(dirname(abspath(__file__)), "..", "argus_plugins"))

# Default locations for settings.ini files
SETTINGS_ENV_VAR = "ARGUS_CLI_SETTINGS"

# Expected user location if none is provided
DEFAULT_SETTINGS_LOCATION = join(abspath(dirname(__file__)), "resources", "config.yaml")
USER_SETTINGS_LOCATION = environ.get(SETTINGS_ENV_VAR, join(expanduser("~"), ".argus_cli.yaml"))

settings = None


def merge(source: dict, destination: dict) -> dict:
    """Deep merges two dictionaries and replaces values from destination with the ones from source."""
    for key, value in source.items():
        if isinstance(value, dict):
            node = destination.setdefault(key, {})
            merge(value, node)
        else:
            destination[key] = value

    return destination


def _get_plugins(settings: dict) -> dict:
    if "plugins" not in settings["cli"].keys() or not settings["cli"]["plugins"]:
        log_module.log.info("No plugin directory specified. Defaulting to %s" % DEFAULT_PLUGIN_DIRECTORY)
        settings["cli"]["plugins"] = []
    else:
        # Remove plugin directories that don't exist and warn about them

        for directory in settings["cli"]["plugins"]:
            if not exists(directory):
                log_module.log.warning("Plugin directory %s does not exist. Ignoring")

        settings["cli"]["plugins"] = [
            directory
            for directory in settings["cli"]["plugins"]
            if exists(directory)
        ]

    settings["cli"]["plugins"] += [DEFAULT_PLUGIN_DIRECTORY]

    return settings


def _get_debug_mode(settings: dict) -> dict:
    """Sets up debug mode if there is a --debug argument on the commandline"""
    from argus_cli import arguments

    if arguments.debug_mode():
        settings["global"] = {"debug": True}

        for logger in settings["logging"]["handlers"].values():
            logger["level"] = "DEBUG"

        log_module.log.info("Debug mode activated!")
    return settings


def load_settings():
    """Loads settings from a settings-file.

    :param debug_mode: Weather or not to explicity enable debug mode
    """
    # Load default settings and allow user settings to take precedence
    global settings
    settings = merge(
        load(open(USER_SETTINGS_LOCATION)) if exists(USER_SETTINGS_LOCATION) else {},
        load(open(DEFAULT_SETTINGS_LOCATION))
    )

    # Get logging settings
    settings = _get_debug_mode(settings)
    # Then configure the logger with these settings
    log_module.setup_logger(settings["logging"])

    # and proceed to load plugins
    settings = _get_plugins(settings)

    log_module.log.debug("Loaded settings:\n\t%s" % settings)


load_settings()
